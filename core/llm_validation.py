"""
Validador da resposta da explicação assistida (etapas 7A e 7B).

Roda todas as verificações e devolve o resultado de cada uma. Se qualquer
uma falhar, a resposta NÃO é exibida. Módulo puro (sem rede).
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Iterable, Optional

from core.llm_context import LIMITATION_KEYWORDS, allowed_numbers
from core.llm_prompts import REFUSAL_FORECAST_TEXT, REFUSAL_TEXT

CHECK_NAMES = (
    "json_valido",
    "campos_obrigatorios",
    "ativo_consistente",
    "periodo_frequencia",
    "metricas_no_contexto",
    "valores_rastreaveis",
    "sem_recomendacao",
    "sem_previsao",
    "sem_termos_proibidos",
    "limitacoes",
    "recusa_correta",
)

_INSUFFICIENT = re.compile(r"insuficient|nao (sao|ha|foi possivel|e possivel)\b.{0,40}suficiente")

MAX_TEXT = 900
MAX_RESUMO = 700
MAX_LIST_ITEMS = 6
MAX_METRICS = 12

TEXT_FIELDS = ("resumo", "o_que_o_grafico_mostra", "nota_educativa")
REQUIRED_FIELDS = (
    "resumo",
    "recusa_recomendacao",
    "filtros_aplicados",
    "o_que_o_grafico_mostra",
    "metricas_relevantes",
    "limitacoes",
    "o_que_nao_pode_ser_concluido",
    "nota_educativa",
)

# Termos proibidos em qualquer contexto, mesmo negados (o prompt os proíbe).
HARD_TERMS = (
    r"\bcompre\b",
    r"\bcomprem\b",
    r"\binvista\b",
    r"\binvistam\b",
    r"\baposte\b",
    r"\bapostem\b",
    r"\bbarat[oa]s?\b",
    r"\bcar[oa]s?\b",
    r"\bmelhor investimento\b",
    r"\bpior investimento\b",
    r"\bvai (subir|cair)\b",
    r"\bvao (subir|cair)\b",
    r"\bdeve investir\b",
    r"\bdeveria investir\b",
    r"\bvale a pena\b",
    r"\bseria (bom|ideal|melhor|recomendavel|aconselhavel)\b",
    r"\bbom momento\b",
    r"\bboa hora\b",
    r"\bhora de (comprar|vender|investir|entrar|sair)\b",
    r"\boportunidade de (compra|investimento)\b",
    r"\bpreco justo\b",
    r"\b(sub|sobre)valorizad[oa]s?\b",
)

# Recomendação: aceita apenas dentro de frase negada ("não é recomendação...").
SOFT_RECOMMENDATION = (
    r"\brecomend\w*",
    r"\baconselh\w*",
    r"\b(comprar|vender|investir|aplicar|resgatar)\b",
    r"\bvendas?\b",
    r"\baloc\w+",
)

# Previsão: aceita apenas dentro de frase negada ("não permite prever...").
SOFT_PREDICTION = (
    r"\b(vai|vao|ira|irao|devera|deverao|deve|devem)\s+(se\s+)?"
    r"(subir|cair|valorizar|desvalorizar|render|aumentar|diminuir|recuperar|"
    r"manter|continuar|repetir|ocorrer|acontecer)\b",
    r"\btende(m)? a\b",
    r"\bproxim[oa]s?\s+(dia|dias|semana|semanas|mes|meses|ano|anos|periodo|periodos)\b",
    r"\bgarant\w*",
    r"\bcom certeza\b",
    r"\bcertamente\b",
    r"\bprevis\w*",
    r"\bprojec\w*",
    r"\bespera-?se\b",
    r"\be esperado\b",
)

NEGATIONS = ("nao", "nem", "sem", "nunca", "nenhum", "nenhuma", "jamais", "tampouco")


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class ValidationResult:
    checks: list = field(default_factory=list)
    metrics_cited: int = 0
    metrics_correct: int = 0

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)

    @property
    def failed(self) -> list:
        return [c.name for c in self.checks if not c.ok]

    def passed(self, name: str) -> bool:
        return next(c.ok for c in self.checks if c.name == name)

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "checks": {c.name: c.ok for c in self.checks},
            "details": {c.name: c.detail for c in self.checks if c.detail},
            "metrics_cited": self.metrics_cited,
            "metrics_correct": self.metrics_correct,
        }


def fold(text: str) -> str:
    """Minúsculas e sem acentos, para comparar termos."""
    decomposed = unicodedata.normalize("NFD", str(text).lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def _sentences(folded: str) -> list:
    return [s for s in re.split(r"[.!?;:\n]+", folded) if s.strip()]


def _hard_hits(folded: str) -> list:
    return [m.group(0) for p in HARD_TERMS for m in re.finditer(p, folded)]


def _soft_hits(folded: str, patterns: Iterable[str]) -> list:
    """(termo, frase) das ocorrências sem negação anterior ao termo na frase."""
    hits = []
    for sentence in _sentences(folded):
        for pattern in patterns:
            for match in re.finditer(pattern, sentence):
                before = sentence[: match.start()]
                if not any(re.search(rf"\b{n}\b", before) for n in NEGATIONS):
                    hits.append((match.group(0), sentence.strip()))
    return hits


_NUMBER = re.compile(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}(?!\d)|\d{1,2}/\d{4}")
_THOUSANDS = re.compile(r"[1-9]\d{0,2}(?:\.\d{3})+(?:,\d+)?")


def _decimals_of(raw: str) -> int:
    return len(raw.split(".")[1]) if "." in raw else 0


def _numbers_in(text: str, remove: Iterable[str]) -> list:
    """
    Números do texto, sem tickers nem datas. Cada item é a lista de leituras
    possíveis [(valor, casas decimais), ...]: "1.825" tanto pode ser 1825
    (milhar brasileiro) quanto 1,825 (ponto decimal); "0.056" só pode ser decimal.
    """
    cleaned = _DATE.sub(" ", text)
    for token in sorted({t for t in remove if t}, key=len, reverse=True):
        cleaned = re.sub(re.escape(token), " ", cleaned, flags=re.IGNORECASE)
    found = []
    for match in _NUMBER.finditer(cleaned):
        raw = match.group(0)
        end = match.end()
        if end < len(cleaned) and cleaned[end] in "ºª":
            continue
        readings = []
        if _THOUSANDS.fullmatch(raw):
            thousands = raw.replace(".", "").replace(",", ".")
            readings.append((float(thousands), _decimals_of(thousands)))
        plain = raw.replace(",", ".")
        if plain.count(".") <= 1:
            readings.append((float(plain), _decimals_of(plain)))
        found.append(readings)
    return found


def _is_traceable(value: float, decimals: int, allowed: Iterable[float]) -> bool:
    tolerance = 0.5 * 10 ** (-decimals) + 1e-9
    return any(abs(abs(value) - abs(a)) <= tolerance for a in allowed)


def _collect_text(data: dict) -> str:
    parts = [str(data.get(f, "")) for f in TEXT_FIELDS]
    parts += [str(m.get("leitura", "")) for m in data.get("metricas_relevantes", [])]
    parts += [str(x) for x in data.get("limitacoes", [])]
    parts += [str(x) for x in data.get("o_que_nao_pode_ser_concluido", [])]
    return "\n".join(parts)


def _is_text_list(value) -> bool:
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def _structure_problem(data: dict) -> Optional[str]:
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        return f"campos ausentes: {', '.join(missing)}"
    for name in TEXT_FIELDS:
        if not isinstance(data[name], str) or not data[name].strip():
            return f"'{name}' deve ser texto não vazio"
    if len(data["resumo"]) > MAX_RESUMO or any(
        len(data[n]) > MAX_TEXT for n in TEXT_FIELDS
    ):
        return "texto longo demais"
    if not isinstance(data["recusa_recomendacao"], bool):
        return "'recusa_recomendacao' deve ser booleano"
    filters = data["filtros_aplicados"]
    if not isinstance(filters, dict) or not all(
        k in filters for k in ("ativos", "periodo_inicio", "periodo_fim", "frequencia")
    ):
        return "'filtros_aplicados' incompleto"
    if not _is_text_list(filters["ativos"]):
        return "'filtros_aplicados.ativos' deve ser lista de textos"
    metrics = data["metricas_relevantes"]
    if not isinstance(metrics, list) or len(metrics) > MAX_METRICS:
        return "'metricas_relevantes' inválido"
    for item in metrics:
        if not isinstance(item, dict) or not all(
            k in item for k in ("id", "valor", "unidade", "leitura")
        ):
            return "item de 'metricas_relevantes' incompleto"
        if isinstance(item["valor"], bool) or not isinstance(item["valor"], (int, float)):
            return "'valor' da métrica deve ser número"
        if not isinstance(item["id"], str) or not isinstance(item["leitura"], str):
            return "'id' e 'leitura' devem ser texto"
    for name in ("limitacoes", "o_que_nao_pode_ser_concluido"):
        value = data[name]
        if not _is_text_list(value) or not value or len(value) > MAX_LIST_ITEMS:
            return f"'{name}' deve ser lista de 1 a {MAX_LIST_ITEMS} textos"
        if any(not x.strip() or len(x) > MAX_TEXT for x in value):
            return f"'{name}' tem item vazio ou longo demais"
    return None


def validate_response(
    raw,
    context: dict,
    known_tickers: Iterable[str] = (),
) -> ValidationResult:
    """
    Valida a resposta (texto JSON ou dict) contra o contexto enviado.
    `known_tickers`: catálogo inteiro, para detectar ativos de fora do contexto.
    """
    result = ValidationResult()

    def add(name: str, ok: bool, detail: str = "") -> None:
        result.checks.append(Check(name, bool(ok), detail))

    # 1. JSON válido ----------------------------------------------------
    data = None
    if isinstance(raw, dict):
        data = raw
    else:
        try:
            data = json.loads(raw)
        except (TypeError, ValueError):
            data = None
    json_ok = isinstance(data, dict)
    add("json_valido", json_ok, "" if json_ok else "resposta não é um objeto JSON")
    if not json_ok:
        for name in CHECK_NAMES[1:]:
            add(name, False, "não avaliado: JSON inválido")
        return result

    # 2. Campos obrigatórios -------------------------------------------
    problem = _structure_problem(data)
    add("campos_obrigatorios", problem is None, problem or "")
    if problem is not None:
        for name in CHECK_NAMES[2:]:
            add(name, False, "não avaliado: estrutura inválida")
        return result

    filters = data["filtros_aplicados"]
    ctx_filters = context["filters"]
    assets = [a.upper() for a in context["assets"]]

    # 3. Ativo(s) ---------------------------------------------------------
    stated = sorted(a.strip().upper() for a in filters["ativos"])
    text = _collect_text(data)
    folded = fold(text)
    # Case-sensitive e ignorando códigos curtos ("A", "T"), que casariam com
    # palavras comuns do texto em português.
    others = [
        t
        for t in known_tickers
        if t.upper() not in assets
        and (len(t) >= 3 or not t.isalpha())
        and re.search(rf"(?<![A-Za-z0-9]){re.escape(t)}(?![A-Za-z0-9])", text)
    ]
    asset_ok = stated == sorted(assets) and not others
    detail = ""
    if stated != sorted(assets):
        detail = f"ativos informados {stated} != contexto {sorted(assets)}"
    elif others:
        detail = f"cita ativo fora do contexto: {others[0]}"
    add("ativo_consistente", asset_ok, detail)

    # 4. Período e frequência ---------------------------------------------
    period_ok = (
        filters["periodo_inicio"] == ctx_filters["period_start"]
        and filters["periodo_fim"] == ctx_filters["period_end"]
        and fold(filters["frequencia"]) == fold(ctx_filters["frequency"])
    )
    add("periodo_frequencia", period_ok, "" if period_ok else "período ou frequência diferentes do contexto")

    # 5. Métricas existem no contexto e com o mesmo valor ----------------------
    by_id = {m["id"]: m for m in context["metrics"]}
    cited = data["metricas_relevantes"]
    result.metrics_cited = len(cited)
    problems = []
    for item in cited:
        ref = by_id.get(item["id"])
        if ref is None:
            problems.append(f"id inexistente: {item['id']}")
            continue
        tolerance = 0.5 * 10 ** (-min(ref.get("decimals", 2), 2)) + 1e-9
        if abs(float(item["valor"]) - ref["value"]) > tolerance or fold(item["unidade"]) != fold(ref["unit"]):
            problems.append(f"valor ou unidade diferente: {item['id']}")
            continue
        result.metrics_correct += 1
    if context["status"] == "dados_insuficientes":
        if cited:
            problems.append("com dados insuficientes não deve citar métricas")
        if not _INSUFFICIENT.search(fold(data["resumo"])):
            problems.append("o resumo não informa que os dados são insuficientes")
    elif context["metrics"] and not cited and not context.get("user_request"):
        problems.append("nenhuma métrica citada")
    add("metricas_no_contexto", not problems, "; ".join(problems))

    # 6. Números rastreáveis -----------------------------------------------
    remove = list(context["assets"]) + [str(n) for n in context["asset_names"].values()]
    allowed = allowed_numbers(context)
    untraceable = [
        readings[0][0]
        for readings in _numbers_in(text, remove)
        if not any(_is_traceable(v, d, allowed) for v, d in readings)
    ]
    add(
        "valores_rastreaveis",
        not untraceable,
        "" if not untraceable else f"número fora do contexto: {untraceable[0]:g}",
    )

    # 7-9. Linguagem ------------------------------------------------------------
    rec = _soft_hits(folded, SOFT_RECOMMENDATION)
    add("sem_recomendacao", not rec, "" if not rec else f"recomendação: '{rec[0][0]}' em «{rec[0][1][:140]}»")
    pred = _soft_hits(folded, SOFT_PREDICTION)
    add("sem_previsao", not pred, "" if not pred else f"previsão: '{pred[0][0]}' em «{pred[0][1][:140]}»")
    hard = _hard_hits(folded)
    add("sem_termos_proibidos", not hard, "" if not hard else f"termo proibido: '{hard[0]}'")

    # 10. Limitações ----------------------------------------------------------------
    lim_text = fold(" ".join(data["limitacoes"]))
    missing_flags = [
        flag
        for flag in context["limitation_flags"]
        if not any(k in lim_text for k in LIMITATION_KEYWORDS[flag])
    ]
    add(
        "limitacoes",
        not missing_flags,
        "" if not missing_flags else f"limitação obrigatória ausente: {missing_flags[0]}",
    )

    # 11. Recusa --------------------------------------------------------------------
    request = context.get("user_request")
    if request:
        expected = REFUSAL_TEXT if request["type"] == "recomendacao" else REFUSAL_FORECAST_TEXT
        refused = data["recusa_recomendacao"] is True and fold(data["resumo"]).startswith(fold(expected))
        add("recusa_correta", refused, "" if refused else "pedido não foi recusado com a frase fixa")
    else:
        spurious = data["recusa_recomendacao"] is True
        add("recusa_correta", not spurious, "recusa sem pedido de recomendação" if spurious else "")

    return result
