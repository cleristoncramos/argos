"""
Validador da camada de linguagem v1.0-experimental.

Todas as verificações precisam passar; se uma falhar, a resposta não é exibida.
Além das verificações herdadas da v0.6 (estrutura, ativo, período, métricas,
números rastreáveis, linguagem), verifica a AUTORIZAÇÃO: estimativa e conclusão
só podem aparecer quando a política de liberação as autorizou, e cada camada
só pode usar os próprios números. Módulo puro (sem rede).

Reaproveita as funções de texto de `core.llm_validation` (v0.6), sem alterá-las.
"""

from __future__ import annotations

import json
import re
from typing import Iterable, Optional

from core import llm_exp_context as ec
from core import llm_exp_policy as policy
from core import llm_exp_prompts as ep
from core.llm_context import LIMITATION_KEYWORDS
from core.llm_validation import (
    HARD_TERMS,
    SOFT_JUDGMENT,
    SOFT_PREDICTION,
    SOFT_RECOMMENDATION,
    Check,
    ValidationResult,
    _is_traceable,
    _negated,
    _numbers_in,
    _sentences,
    _soft_hits,
    fold,
)

CHECK_NAMES = (
    "json_valido",
    "campos_obrigatorios",
    "ativo_consistente",
    "periodo_frequencia",
    "metricas_por_camada",
    "valores_rastreaveis",
    "estimativa_autorizada",
    "conclusao_autorizada",
    "sem_futuro_fora_da_estimativa",
    "sem_recomendacao_propria",
    "sem_termos_proibidos",
    "sem_promessa_nem_persuasao",
    "limitacoes",
    "ressalva_media_historica",
    "limite_da_evidencia",
    "pedido_tratado",
    "politica_de_liberacao",
)

MAX_TEXT = 900
MAX_RESUMO = 700
MAX_METRICS = 6
MAX_LIST_ITEMS = 4

# Persuasão e urgência: proibidas em qualquer forma, mesmo negadas.
PERSUASION_TERMS = (
    r"\baproveite\b", r"\bnao perca\b", r"\bimperdive(l|is)\b", r"\bultima chance\b", r"\bcorra\b",
    r"\burgente\b", r"\bagora mesmo\b", r"\bso hoje\b",
)
# Promessa e falsa certeza: aceitas só em frase negada ("não há garantia de resultado").
PROMISE_TERMS = (
    r"\bgarant\w*", r"\blucro (certo|garantido|assegurado)\b", r"\bsem risco\b",
    r"\bretorno (certo|garantido|assegurado)\b", r"\bcom certeza\b", r"\bcertamente\b", r"\binfalive\w*",
    r"\bseguramente\b",
)
# Correção 4 (DL1-B): nenhuma frase atribui aprovação, recomendação, validação ou garantia
# a indicador, estratégia, regra, sinal ou modelo (aceito só em frase negada).
ATTRIBUTION_TERMS = (
    r"\b(indicador(es)?|rsi|macd|estrategias?|regras?|sinal|sinais|modelos?)\b[^.;:]{0,60}?"
    r"\b(aprovad\w*|recomendad\w*|recomenda\w*|validad[oa]s?|comprovad\w*|garant\w*|confiave\w*|eficaz\w*|"
    r"infalive\w*|segur[oa]s?)",
)

# Correção 1 (DL1-B): frase com média, comparação entre períodos ou frequência histórica
# exige, no mesmo parágrafo, limitação da amostra e não garantia de repetição. A checagem é
# por classe de expressão; médias móveis e médias exponenciais (EMA), que são indicadores, não
# disparam a regra (DL1-O). Continuam sujeitas às checagens de futuro e de atribuição.
HISTORICAL_AVERAGE_TRIGGERS = (
    r"\bmedias?\b(?!\s+(mov|exponenc))", r"\bmediana\b", r"\b(superior|inferior)(es)? (a|ao|aos|as|a de|a do|ao de|ao do)\b",
    r"\b(acima|abaixo) da media\b", r"\banos positivos\b", r"\bproporcao de (anos|meses|periodos)\b",
    r"\bfrequencia historica\b", r"\bem \d+ de \d+ (anos|meses)\b", r"\bem comparacao (com|a)\b",
)
SAMPLE_CAVEATS = (
    r"\bamostra (e |foi |era |ainda e )?(limitada|pequena|curta|reduzida)\b", r"\bpoucos anos\b",
    r"\bpoucas observacoes\b", r"\bnumero (pequeno|limitado|reduzido) de (anos|observacoes|meses)\b",
    r"\bperiodo curto\b",
)
# DL1-M: parágrafo que cite média ou mediana de período exige também o número de anos da
# amostra e a dispersão entre anos (classes de expressão, com variantes).
PERIOD_AVERAGE_TRIGGERS = (r"\bmedias?\b(?!\s+(mov|exponenc))", r"\bmediana\b")
YEARS_STATEMENTS = (
    r"\b\d+ anos\b", r"\b(19|20)\d\d (a|e|ate) (19|20)\d\d\b", r"\bamostra de \d+ (anos|meses)\b",
)
DISPERSION_STATEMENTS = (
    r"\bdesvio(-padrao| padrao)?\b", r"\bdispersao\b", r"\bvari(ou|aram|acao) (muito |bastante )?(de|entre)\b",
    r"[-+]?\d+(,\d+)?% a [-+]?\d+(,\d+)?%", r"\bamplitude\b", r"\boscil\w+ (de|entre)\b",
)
REPETITION_CAVEATS = (
    r"\bnao (indica|garante|significa|assegura|permite (concluir|afirmar)) que\b.{0,80}"
    r"(repet|se mant|continu|volt|ocorr)",
    r"\b(pode|podera) nao se repetir\b", r"\bnao se repete(m)? necessariamente\b",
    r"\bsem garantia de (que )?.{0,40}repet", r"\bnao ha garantia de repeticao\b",
)

_INSUFFICIENT = re.compile(r"insuficient|nao (sao|ha|foi possivel|e possivel)\b.{0,40}suficiente")


def _texts(items: Iterable) -> str:
    return "\n".join(str(x) for x in items)


def _metric_texts(block: dict) -> list:
    return [m.get("leitura", "") for m in block.get("metricas_relevantes", [])]


def _strip(folded: str, phrases: Iterable[str]) -> str:
    """Retira as frases fixas copiadas literalmente (elas já são verificadas à parte)."""
    for phrase in sorted({fold(p) for p in phrases if p}, key=len, reverse=True):
        folded = folded.replace(phrase, " ")
    return folded


def _is_metric_list(value) -> bool:
    if not isinstance(value, list) or len(value) > MAX_METRICS:
        return False
    for item in value:
        if not isinstance(item, dict) or set(item) != {"id", "valor", "unidade", "leitura"}:
            return False
        if isinstance(item["valor"], bool) or not isinstance(item["valor"], (int, float)):
            return False
        if not all(isinstance(item[k], str) for k in ("id", "unidade", "leitura")):
            return False
    return True


def _text_list_ok(value) -> bool:
    return (isinstance(value, list) and 1 <= len(value) <= MAX_LIST_ITEMS
            and all(isinstance(x, str) and x.strip() and len(x) <= MAX_TEXT for x in value))


def _structure_problem(data: dict) -> Optional[str]:
    missing = [f for f in ep.OUTPUT_SCHEMA["required"] if f not in data]
    if missing:
        return f"campos ausentes: {', '.join(missing)}"
    if not isinstance(data["resumo"], str) or not data["resumo"].strip() or len(data["resumo"]) > MAX_RESUMO:
        return "'resumo' deve ser texto não vazio e curto"
    if data["tratamento_do_pedido"] not in ep.TREATMENTS:
        return "'tratamento_do_pedido' fora da lista"
    filters = data["filtros_aplicados"]
    if not isinstance(filters, dict) or set(filters) != {"ativos", "periodo_inicio", "periodo_fim", "frequencia"}:
        return "'filtros_aplicados' incompleto"
    if not isinstance(filters["ativos"], list) or not all(isinstance(a, str) for a in filters["ativos"]):
        return "'filtros_aplicados.ativos' deve ser lista de textos"
    hist, est, concl = data["observacao_historica"], data["estimativa"], data["conclusao_experimental"]
    if not isinstance(hist, dict) or set(hist) != {"rotulo", "texto", "metricas_relevantes", "limite_da_evidencia"}:
        return "'observacao_historica' incompleta"
    if not isinstance(est, dict) or set(est) != {"rotulo", "situacao", "texto", "metricas_relevantes", "incerteza"}:
        return "'estimativa' incompleta"
    if not isinstance(concl, dict) or set(concl) != {"rotulo", "situacao", "texto"}:
        return "'conclusao_experimental' incompleta"
    for name in ep.BLOCK_LABELS:
        if data[name]["rotulo"] != ep.BLOCK_LABELS[name]:
            return f"'{name}.rotulo' diferente do cabeçalho fixo do bloco"
    for name, value in (("observacao_historica.texto", hist["texto"]),
                        ("observacao_historica.limite_da_evidencia", hist["limite_da_evidencia"]),
                        ("estimativa.texto", est["texto"]), ("conclusao_experimental.texto", concl["texto"])):
        if not isinstance(value, str) or not value.strip() or len(value) > MAX_TEXT:
            return f"'{name}' deve ser texto não vazio e curto"
    if not isinstance(est["incerteza"], str) or len(est["incerteza"]) > MAX_TEXT:
        return "'estimativa.incerteza' deve ser texto curto"
    if est["situacao"] not in ep.ESTIMATE_STATES or concl["situacao"] not in ep.CONCLUSION_STATES:
        return "situação da estimativa ou da conclusão fora da lista"
    if not _is_metric_list(hist["metricas_relevantes"]) or not _is_metric_list(est["metricas_relevantes"]):
        return "métricas inválidas"
    for name in ("limitacoes", "o_que_nao_pode_ser_concluido"):
        if not _text_list_ok(data[name]):
            return f"'{name}' deve ser lista de 1 a {MAX_LIST_ITEMS} textos não vazios"
    if data["nota_educativa"] != ep.EDUCATIONAL_NOTE:
        return "'nota_educativa' diferente do texto fixo"
    return None


def _metric_problems(cited: list, reference: list, layer: str) -> tuple[list, int]:
    by_id = {m["id"]: m for m in reference}
    problems, correct = [], 0
    for item in cited:
        ref = by_id.get(item["id"])
        if ref is None:
            problems.append(f"{layer}: id fora da camada: {item['id']}")
            continue
        tolerance = 0.5 * 10 ** (-min(ref.get("decimals", 2), 2)) + 1e-9
        if abs(float(item["valor"]) - ref["value"]) > tolerance or fold(item["unidade"]) != fold(ref["unit"]):
            problems.append(f"{layer}: valor ou unidade diferente em {item['id']} "
                            f"(esperado {ref['value']} '{ref['unit']}', recebido {item['valor']} '{item['unidade']}')")
            continue
        correct += 1
    return problems, correct


def _untraceable(text: str, allowed: list, remove: list) -> list:
    return [readings[0][0] for readings in _numbers_in(text, remove)
            if not any(_is_traceable(v, d, allowed) for v, d in readings)]


def attribution_hits(folded: str) -> list:
    """
    (termo, frase) em que indicador, estratégia, regra, sinal ou modelo recebe aprovação,
    recomendação, validação ou garantia. A frase só passa se houver negação antes do termo
    ou entre o termo e o atributo ("o sinal do indicador não garante reversão").
    """
    hits = []
    for sentence in _sentences(folded):
        for pattern in ATTRIBUTION_TERMS:
            for match in re.finditer(pattern, sentence):
                between = sentence[match.start():match.start(match.lastindex)]
                if not _negated(sentence[: match.start()]) and not _negated(between):
                    hits.append((match.group(0), sentence.strip()))
    return hits


def _paragraphs(data: dict) -> list:
    """Unidades de texto em que a ressalva da correção 1 precisa aparecer junto da afirmação."""
    hist, est = data["observacao_historica"], data["estimativa"]
    units = [data["resumo"],
             _texts([hist["texto"], *_metric_texts(hist), hist["limite_da_evidencia"]]),
             _texts([est["texto"], *_metric_texts(est), est["incerteza"]])]
    return units + list(data["limitacoes"]) + list(data["o_que_nao_pode_ser_concluido"])


def missing_average_caveat(data: dict, fixed: Iterable[str]) -> list:
    """Parágrafos com média, comparação ou frequência histórica sem as duas ressalvas."""
    problems = []
    for unit in _paragraphs(data):
        folded = fold(unit)
        if not any(re.search(p, _strip(folded, fixed)) for p in HISTORICAL_AVERAGE_TRIGGERS):
            continue
        stripped = _strip(folded, fixed)
        period = any(re.search(p, stripped) for p in PERIOD_AVERAGE_TRIGGERS)
        elements = [("amostra limitada", any(re.search(p, folded) for p in SAMPLE_CAVEATS)),
                    ("não repetição", any(re.search(p, folded) for p in REPETITION_CAVEATS))]
        if period:
            elements += [("número de anos", any(re.search(p, folded) for p in YEARS_STATEMENTS)),
                         ("dispersão entre anos", any(re.search(p, folded) for p in DISPERSION_STATEMENTS))]
        missing = [name for name, ok in elements if not ok]
        if missing:
            problems.append(f"falta {', '.join(missing)} em «{unit[:120]}»")
    return problems


def validate_experimental(
    raw,
    context: dict,
    known_tickers: Iterable[str] = (),
    model_registry: Optional[dict] = None,
    engine_registry: Optional[dict] = None,
) -> ValidationResult:
    """Valida a resposta (texto JSON ou dict) contra o contexto v1.0-experimental enviado."""
    result = ValidationResult()

    def add(name: str, ok: bool, detail: str = "") -> None:
        result.checks.append(Check(name, bool(ok), "" if ok else detail))

    # 1. JSON -----------------------------------------------------------------
    data = raw if isinstance(raw, dict) else None
    if data is None:
        try:
            data = json.loads(raw)
        except (TypeError, ValueError):
            data = None
    if not isinstance(data, dict):
        add("json_valido", False, "resposta não é um objeto JSON")
        for name in CHECK_NAMES[1:]:
            add(name, False, "não avaliado: JSON inválido")
        return result
    add("json_valido", True)

    # 2. Estrutura ---------------------------------------------------------------
    problem = _structure_problem(data)
    add("campos_obrigatorios", problem is None, problem or "")
    if problem is not None:
        for name in CHECK_NAMES[2:]:
            add(name, False, "não avaliado: estrutura inválida")
        return result

    hist, est, concl = data["observacao_historica"], data["estimativa"], data["conclusao_experimental"]
    ctx_hist, ctx_est, ctx_dec = context["historical"], context["estimate"], context["decision"]
    request = context.get("user_request")
    refusal = bool(request) and request["type"] in (ec.REQUEST_RECOMMENDATION, ec.REQUEST_GUARANTEE)
    decision_text = ctx_dec.get("texto_conclusao", "")
    fixed = list(ep.FIXED_TEXTS) + list(context["required_limits"]) + ([decision_text] if decision_text else [])

    hist_text = _texts([hist["texto"], *_metric_texts(hist), hist["limite_da_evidencia"]])
    est_text = _texts([est["texto"], *_metric_texts(est), est["incerteza"]])
    general_text = _texts([data["resumo"], *data["limitacoes"], *data["o_que_nao_pode_ser_concluido"]])
    all_text = _texts([general_text, hist_text, est_text, concl["texto"]])

    # 3. Ativo ----------------------------------------------------------------------
    asset = context["asset"].upper()
    stated = [a.strip().upper() for a in data["filtros_aplicados"]["ativos"]]
    others = [t for t in known_tickers
              if t.upper() != asset and (len(t) >= 3 or not t.isalpha())
              and re.search(rf"(?<![A-Za-z0-9]){re.escape(t)}(?![A-Za-z0-9])", all_text)]
    add("ativo_consistente", stated == [asset] and not others,
        f"ativos informados {stated} != contexto ['{asset}']" if stated != [asset]
        else f"cita ativo fora do contexto: {others[0] if others else ''}")

    # 4. Período ---------------------------------------------------------------------
    f, cf = data["filtros_aplicados"], context["filters"]
    add("periodo_frequencia",
        f["periodo_inicio"] == cf["period_start"] and f["periodo_fim"] == cf["period_end"]
        and fold(f["frequencia"]) == fold(cf["frequency"]),
        "período ou frequência diferentes do contexto")

    # 5. Métricas, cada uma na sua camada ---------------------------------------------
    problems, correct_h = _metric_problems(hist["metricas_relevantes"], ctx_hist["metrics"], "histórica")
    est_problems, correct_e = _metric_problems(est["metricas_relevantes"], ctx_est.get("metrics", []), "estimativa")
    problems += est_problems
    result.metrics_cited = len(hist["metricas_relevantes"]) + len(est["metricas_relevantes"])
    result.metrics_correct = correct_h + correct_e
    if context["status"] == "dados_insuficientes":
        if hist["metricas_relevantes"]:
            problems.append("com dados insuficientes não deve citar métricas")
        if not _INSUFFICIENT.search(fold(data["resumo"])):
            problems.append("o resumo não informa que os dados são insuficientes")
    elif refusal and hist["metricas_relevantes"]:
        problems.append("recusa não pode citar métricas")
    elif not refusal and ctx_hist["metrics"] and not hist["metricas_relevantes"]:
        problems.append("nenhuma métrica histórica citada")
    add("metricas_por_camada", not problems, "; ".join(problems))

    # 6. Números rastreáveis, por camada ---------------------------------------------
    remove = [context["asset"], context.get("asset_name", ""), ctx_dec.get("regra_id", "")]
    allowed_h = ec.historical_allowed_numbers(context)
    allowed_e = ec.estimate_allowed_numbers(context)
    bad = (_untraceable(hist_text, allowed_h, remove)
           + _untraceable(est_text, allowed_e if ctx_est.get("disponivel") else [], remove)
           + _untraceable(general_text, allowed_h + allowed_e, remove))
    if refusal:
        bad += _untraceable(general_text + "\n" + hist_text, [], remove)
    add("valores_rastreaveis", not bad, f"número fora da camada ou do contexto: {bad[0]:g}" if bad else "")

    # 7. Estimativa autorizada ---------------------------------------------------------
    abstained = (est["situacao"] == "abstencao" and fold(est["texto"]) == fold(ep.ESTIMATE_ABSTENTION)
                 and not est["metricas_relevantes"] and not est["incerteza"].strip())
    if est["situacao"] == "abstencao":
        est_ok, detail = abstained, "abstenção sem o texto fixo, com métricas ou com incerteza"
    elif not ctx_est.get("disponivel"):
        est_ok, detail = False, f"estimativa apresentada sem autorização ({ctx_est.get('motivo')})"
    else:
        ids = {m["id"] for m in est["metricas_relevantes"]}
        est_ok = (ctx_est["ponto_id"] in ids and bool(ids & set(ctx_est["incerteza_ids"]))
                  and bool(est["incerteza"].strip()))
        detail = "estimativa sem o ponto, sem medida de incerteza ou sem descrição da incerteza"
    add("estimativa_autorizada", est_ok, detail)

    # 8. Conclusão autorizada ------------------------------------------------------------
    if concl["situacao"] == "nao_disponivel":
        concl_ok = fold(concl["texto"]) == fold(ep.CONCLUSION_UNAVAILABLE)
        detail = "conclusão indisponível sem o texto fixo"
    elif not ctx_dec.get("disponivel"):
        concl_ok, detail = False, f"conclusão sem motor autorizado ({ctx_dec.get('motivo')})"
    else:
        concl_ok = concl["texto"] == decision_text
        detail = "a conclusão não é cópia literal do texto emitido pelo motor"
    add("conclusao_autorizada", concl_ok, detail)

    # 9-12. Linguagem ------------------------------------------------------------------
    outside = _strip(fold(_texts([general_text, hist_text, concl["texto"]]
                                 + ([] if est["situacao"] == "apresentada" else [est_text]))), fixed)
    future = _soft_hits(outside, SOFT_PREDICTION)
    add("sem_futuro_fora_da_estimativa", not future,
        f"futuro fora da estimativa: '{future[0][0]}' em «{future[0][1][:140]}»" if future else "")
    everything = _strip(fold(all_text), fixed)
    rec = _soft_hits(everything, SOFT_RECOMMENDATION) + attribution_hits(everything)
    add("sem_recomendacao_propria", not rec,
        f"recomendação ou atribuição: '{rec[0][0]}' em «{rec[0][1][:140]}»" if rec else "")
    hard = [m.group(0) for p in HARD_TERMS for m in re.finditer(p, everything)]
    hard += [h[0] for h in _soft_hits(everything, SOFT_JUDGMENT)]
    add("sem_termos_proibidos", not hard, f"termo proibido: '{hard[0]}'" if hard else "")
    persuasion = [m.group(0) for p in PERSUASION_TERMS for m in re.finditer(p, everything)]
    promise = [h[0] for h in _soft_hits(everything, PROMISE_TERMS)]
    add("sem_promessa_nem_persuasao", not (persuasion or promise),
        f"persuasão ou promessa: '{(persuasion + promise)[0]}'" if (persuasion or promise) else "")

    # 13. Limitações sinalizadas -----------------------------------------------------------
    lim_text = fold(" ".join(data["limitacoes"]))
    missing = [flag for flag in ctx_hist["limitation_flags"]
               if not any(k in lim_text for k in LIMITATION_KEYWORDS[flag])]
    add("limitacoes", refusal or not missing, f"limitação obrigatória ausente: {missing[0]}" if missing else "")

    # 13a. Ressalva sobre média histórica (correção 1) ------------------------------------
    caveats = missing_average_caveat(data, fixed)
    add("ressalva_media_historica", not caveats, caveats[0] if caveats else "")

    # 14. Limite por gráfico ou da síntese -----------------------------------------------
    items = {fold(x).strip() for x in data["o_que_nao_pode_ser_concluido"]}
    required = [ep.REFUSAL_LIMIT] if refusal else context["required_limits"]
    absent = [lim for lim in required if fold(lim).strip() not in items]
    add("limite_da_evidencia", not absent, f"limite obrigatório ausente: «{absent[0]}»" if absent else "")

    # 15. Pedido ------------------------------------------------------------------------
    treatment = data["tratamento_do_pedido"]
    if not request:
        ok, detail = treatment == "sem_pedido", "tratamento de pedido sem pedido"
    elif refusal:
        phrase = ep.REFUSAL_RECOMMENDATION if request["type"] == ec.REQUEST_RECOMMENDATION else ep.REFUSAL_GUARANTEE
        expected = "recusa_recomendacao" if request["type"] == ec.REQUEST_RECOMMENDATION else "recusa_garantia"
        ok = (treatment == expected and data["resumo"].strip() == phrase
              and fold(hist["texto"]) == fold(ep.NOT_APPLICABLE)
              and fold(hist["limite_da_evidencia"]) == fold(ep.REFUSAL_LIMIT)
              and est["situacao"] == "abstencao" and concl["situacao"] == "nao_disponivel")
        detail = "pedido de recomendação ou garantia não foi recusado com os textos fixos"
    elif ctx_est.get("disponivel"):
        ok = treatment == "previsao_explicada" and est["situacao"] == "apresentada"
        detail = "pedido de previsão com estimativa autorizada não foi explicado"
    else:
        ok = treatment == "previsao_abstencao" and fold(data["resumo"]).startswith(fold(ep.ESTIMATE_ABSTENTION))
        detail = "pedido de previsão sem modelo autorizado não começou pela abstenção"
    add("pedido_tratado", ok, detail)

    # 16. Política de liberação (integridade do contexto) ---------------------------------
    release = context["release"]
    est_auth = policy.estimate_authorization(ctx_est.get("model_id"), context["asset"], release["ambiente"],
                                             model_registry)[0]
    dec_auth = policy.decision_authorization(ctx_dec.get("engine_id"), release["ambiente"], engine_registry)[0]
    integrity = (context.get("protocol_family") == ec.PROTOCOL_FAMILY
                 and release["recomendacao_habilitada"] is False
                 and (not ctx_est.get("disponivel") or est_auth)
                 and (not ctx_dec.get("disponivel") or dec_auth))
    add("politica_de_liberacao", integrity, "contexto com estimativa, conclusão ou recomendação fora da política")
    return result
