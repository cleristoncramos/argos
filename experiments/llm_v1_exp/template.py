"""
Template determinístico da fase 1: a terceira fonte da avaliação cega (DL1-E, DL1-N).

SITUAÇÃO: NÃO CONGELADO. O conjunto de casos será refeito (DL1-O) e o template precisa ser
reverificado sobre os contextos corrigidos antes de ganhar hash próprio.

Compõe, por regras fixas e sem modelo de linguagem, uma resposta no esquema v1.0-experimental
para cada caso do conjunto congelado. Garantias por construção, sem depender do validador:
- todo número vem de uma métrica do contexto, escrito no padrão brasileiro;
- a ressalva da média histórica (amostra limitada, número de anos, dispersão entre anos e não
  garantia de repetição) entra por estrutura fixa no MESMO parágrafo da afirmação;
- só cita recursos do próprio contexto (a síntese não fala de RSI nem de MACD);
- estimativa em abstenção e conclusão indisponível, com os textos fixos aprovados.

Uso, a partir da raiz:  python -m experiments.llm_v1_exp.template [--gravar]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from core import llm_exp_prompts as ep
from core.llm_render import format_value
from experiments.llm_v1_exp import conjunto

ARQUIVO = Path(__file__).resolve().parent / "respostas_template.json"
VERSAO = "template-v1"
LIMITACAO_PADRAO = "Os dados são históricos e não indicam o futuro."
LIMITE_HISTORICO = "O recorte é um trecho do passado e não permite concluir o que acontecerá depois."
RESSALVA_FINAL = "A amostra é limitada, e isso não indica que o próximo período repetirá o resultado."
LIMITACAO_FLAGS = {
    "poucas_observacoes": "Há poucas observações no período.",
    "poucos_anos": "Há poucos anos de dados na amostra.",
    "mes_em_andamento": "O mês em andamento foi excluído.",
    "preco_nao_positivo": "Há preço menor ou igual a zero na série.",
}
# Recursos que cada tipo de contexto pode nomear (o template não cita recurso fora do contexto).
RECURSOS_PERMITIDOS = {
    "preco_medias": ("média móvel",), "rsi_macd": ("RSI", "MACD"), "volatilidade": ("volatilidade",),
    "drawdown": ("queda",), "sazonalidade": (),
}


def _m(contexto: dict) -> dict:
    return {m["id"]: m for m in contexto["historical"]["metrics"]}


def _v(metrica: dict) -> str:
    return format_value(metrica["value"], metrica["unit"])


def _data(iso: str) -> str:
    ano, mes, dia = iso.split("-")
    return f"{dia}/{mes}/{ano}"


def _item(metrica: dict, leitura: str) -> dict:
    return {"id": metrica["id"], "valor": metrica["value"], "unidade": metrica["unit"], "leitura": leitura}


def paragrafo_media(afirmacao: str, anos: dict, dispersao: str) -> str:
    """Estrutura fixa da correção 1 (DL1-M): os quatro elementos no mesmo parágrafo da afirmação."""
    return (f"{afirmacao} São {_v(anos)} de amostra, {dispersao}. {RESSALVA_FINAL}")


def _sintese(ctx: dict) -> tuple[str, str, list]:
    m = _m(ctx)
    var, dd, vol = m["variacao_no_recorte"], m["drawdown_maximo"], m["volatilidade_anualizada"]
    texto = (f"No recorte selecionado, de {_data(ctx['filters']['period_start'])} a {_data(ctx['filters']['period_end'])}, "
             f"a variação foi de {_v(var)}, a queda máxima foi de {_v(dd)} e a volatilidade anualizada foi de {_v(vol)}.")
    resumo = f"No recorte selecionado, {ctx['asset']} teve variação de {_v(var)} e queda máxima de {_v(dd)}."
    itens = [_item(var, "Mudança do preço do início ao fim do recorte."),
             _item(dd, "Maior perda em relação a um pico anterior dentro do recorte."),
             _item(vol, "Intensidade das oscilações diárias, em base anual.")]
    return resumo, texto, itens


def _grafico(ctx: dict) -> tuple[str, str, list]:
    m, chart = _m(ctx), ctx["charts"][0]
    if chart == "preco_medias":
        var, m50, m200 = m["variacao_no_recorte"], m["fechamento_vs_mm50"], m["fechamento_vs_mm200"]
        texto = (f"No recorte, a variação foi de {_v(var)}. No último pregão, a diferença entre o fechamento e a média "
                 f"móvel curta foi de {_v(m50)}, e em relação à média móvel longa, de {_v(m200)}.")
        resumo = f"No recorte selecionado, {ctx['asset']} teve variação de {_v(var)}."
        itens = [_item(var, "Mudança do preço do início ao fim do recorte."),
                 _item(m50, "Distância do fechamento final à média móvel curta."),
                 _item(m200, "Distância do fechamento final à média móvel longa.")]
    elif chart == "rsi_macd":
        rsi, macd = m["rsi_14"], m["macd_histograma_sobre_fechamento"]
        texto = (f"No último pregão do recorte, o RSI foi de {_v(rsi)}, e o histograma do MACD "
                 f"correspondeu a {_v(macd)} do fechamento.")
        resumo = f"No último pregão do recorte, {ctx['asset']} teve RSI de {_v(rsi)}."
        itens = [_item(rsi, "Medida das altas e baixas recentes, numa escala que vai de zero a cem."),
                 _item(macd, "Diferença entre duas médias móveis exponenciais, em relação ao fechamento.")]
    elif chart == "volatilidade":
        vol, vol20 = m["volatilidade_anualizada"], m["volatilidade_20_pregoes"]
        texto = (f"A volatilidade anualizada no recorte foi de {_v(vol)}, e a do fim do recorte, "
                 f"também anualizada, foi de {_v(vol20)}.")
        resumo = f"No recorte selecionado, {ctx['asset']} teve volatilidade anualizada de {_v(vol)}."
        itens = [_item(vol, "Intensidade das oscilações diárias no recorte, em base anual."),
                 _item(vol20, "Intensidade das oscilações no fim do recorte, em base anual.")]
    else:
        dd, fundo = m["drawdown_maximo"], m["dias_ate_o_fundo"]
        texto = f"A queda máxima no recorte foi de {_v(dd)}, e a maior queda levou {_v(fundo)} do pico ao fundo."
        itens = [_item(dd, "Maior perda em relação a um pico anterior dentro do recorte."),
                 _item(fundo, "Tempo do pico ao ponto mais baixo da maior queda.")]
        if "dias_do_fundo_a_recuperacao" in m:
            rec = m["dias_do_fundo_a_recuperacao"]
            texto += f" Do fundo à recuperação, foram {_v(rec)}."
            itens.append(_item(rec, "Tempo do ponto mais baixo até voltar ao pico anterior."))
        else:
            texto += f" Essa queda não foi recuperada até {_data(ctx['filters']['period_end'])}."
        resumo = f"No recorte selecionado, {ctx['asset']} teve queda máxima de {_v(dd)}."
    return resumo, texto, itens


def _media(ctx: dict) -> tuple[str, str, list]:
    m = _m(ctx)
    anos = m["anos_na_amostra"]
    if "media_do_mes" in m:
        media, mediana, minimo, maximo, desvio = (m[k] for k in ("media_do_mes", "mediana_do_mes", "minimo_do_mes",
                                                                 "maximo_do_mes", "desvio_entre_anos"))
        mes = media["label"].rsplit(" ", 1)[-1]
        texto = paragrafo_media(
            f"No recorte selecionado, o retorno de {mes} teve média de {_v(media)} e mediana de {_v(mediana)}.", anos,
            f"e o resultado variou de {_v(minimo)} a {_v(maximo)} entre os anos, com desvio-padrão de {_v(desvio)}")
        resumo = f"Os números descrevem o retorno de {mes} de {ctx['asset']} na amostra disponível."
        itens = [_item(media, f"Média do retorno de {mes} nos anos da amostra."),
                 _item(mediana, f"Valor do meio do retorno de {mes} nos anos da amostra."),
                 _item(desvio, "Quanto o resultado variou de um ano para outro."), _item(anos, "Tamanho da amostra.")]
    elif "proporcao_meses_positivos" in m:
        pm, pa, desvio = m["proporcao_meses_positivos"], m["proporcao_anos_positivos"], m["desvio_retorno_anual"]
        texto = paragrafo_media(
            f"No recorte selecionado, a proporção de meses positivos foi de {_v(pm)}, e a de anos positivos, de {_v(pa)}.",
            anos, f"e o retorno anual variou entre os anos, com desvio-padrão de {_v(desvio)}")
        resumo = f"Os números descrevem os meses e os anos de {ctx['asset']} com retorno acima de zero."
        itens = [_item(pm, "Parte dos meses da amostra com retorno positivo."),
                 _item(pa, "Parte dos anos da amostra com retorno positivo."),
                 _item(desvio, "Quanto o retorno anual variou de um ano para outro."), _item(anos, "Tamanho da amostra.")]
    else:
        ultimo, anteriores, desvio = m["media_mensal_2021"], m["media_mensal_2016_2020"], m["desvio_retorno_anual_2016_2020"]
        texto = paragrafo_media(
            f"No recorte selecionado, a média do retorno mensal em 2021, de janeiro a novembro, foi de {_v(ultimo)}, "
            f"e a de 2016 a 2020 foi de {_v(anteriores)}.", anos,
            f"e o retorno anual de 2016 a 2020 variou entre os anos, com desvio-padrão de {_v(desvio)}")
        resumo = f"Os números descrevem o retorno mensal de {ctx['asset']} em dois períodos."
        itens = [_item(ultimo, "Média do retorno mensal de janeiro a novembro de 2021."),
                 _item(anteriores, "Média do retorno mensal de 2016 a 2020."),
                 _item(desvio, "Quanto o retorno anual variou de 2016 a 2020."), _item(anos, "Anos considerados.")]
    return resumo, texto, itens


def _textos(resposta: dict) -> list:
    """Unidades de parágrafo, as mesmas do validador: o resumo, o bloco histórico inteiro e cada item de lista."""
    hist = resposta["observacao_historica"]
    bloco = " ".join([hist["texto"], *[i["leitura"] for i in hist["metricas_relevantes"]], hist["limite_da_evidencia"]])
    # Os limites obrigatórios são frases fixas aprovadas, copiadas literalmente; ficam fora, como no validador.
    return [resposta["resumo"], bloco, *resposta["limitacoes"]]


def defeitos_de_composicao(resposta: dict, caso: dict) -> list:
    """
    Checagem do PRÓPRIO template, independente do validador (DL1-N): reprova a resposta se
    (1) um parágrafo citar média ou mediana sem a estrutura fixa da ressalva (número de anos de
    amostra, dispersão e a frase final), mesmo que o validador aceite outra redação;
    (2) o texto citar recurso fora do contexto; (3) a queda não recuperada sugerir prazo.
    """
    import re
    defeitos = []
    for texto in _textos(resposta):
        baixo = texto.lower()
        if re.search(r"\bmédias?\b(?!\s+móve)|\bmediana\b", baixo) and not texto.startswith("Os números"):
            if not (RESSALVA_FINAL in texto and re.search(r"São \d+ anos de amostra, ", texto)
                    and ("variou" in texto and "desvio-padrão" in texto)):
                defeitos.append(f"média sem a ressalva estrutural: «{texto[:80]}»")
    permitidos = set()
    for chart in caso["contexto"]["charts"] if caso["bloco"] == "grafico" else ():
        permitidos |= set(RECURSOS_PERMITIDOS[chart])
    corpo = " ".join(_textos(resposta))
    for recurso in ("RSI", "MACD", "média móvel"):
        if recurso in corpo and recurso not in permitidos:
            defeitos.append(f"recurso fora do contexto: {recurso}")
    if re.search(r"\bainda\b", corpo.lower()):
        defeitos.append("formulação que sugere prazo ('ainda')")
    return defeitos


def responder(caso: dict) -> dict:
    ctx = caso["contexto"]
    compor = {"sintese": _sintese, "grafico": _grafico, "media": _media}[caso["bloco"]]
    resumo, texto, itens = compor(ctx)
    limitacoes = [LIMITACAO_FLAGS[f] for f in ctx["historical"]["limitation_flags"]] or [LIMITACAO_PADRAO]
    return {
        "resumo": resumo,
        "tratamento_do_pedido": "sem_pedido",
        "filtros_aplicados": {"ativos": [ctx["asset"]], "periodo_inicio": ctx["filters"]["period_start"],
                              "periodo_fim": ctx["filters"]["period_end"], "frequencia": ctx["filters"]["frequency"]},
        "observacao_historica": {"rotulo": ep.BLOCK_LABELS["observacao_historica"], "texto": texto,
                                 "metricas_relevantes": itens[:6], "limite_da_evidencia": LIMITE_HISTORICO},
        "estimativa": {"rotulo": ep.BLOCK_LABELS["estimativa"], "situacao": "abstencao", "texto": ep.ESTIMATE_ABSTENTION,
                       "metricas_relevantes": [], "incerteza": ""},
        "conclusao_experimental": {"rotulo": ep.BLOCK_LABELS["conclusao_experimental"], "situacao": "nao_disponivel",
                                   "texto": ep.CONCLUSION_UNAVAILABLE},
        "limitacoes": limitacoes[:4],
        "o_que_nao_pode_ser_concluido": list(ctx["required_limits"]),
        "nota_educativa": ep.EDUCATIONAL_NOTE,
    }


def montar(casos: list) -> dict:
    return {"versao": VERSAO, "conjunto_sha256": conjunto.HASH_CONGELADO,
            "codigo_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "respostas": {c["id"]: responder(c) for c in casos}}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Gera ou confere as respostas do template da fase 1.")
    parser.add_argument("--gravar", action="store_true")
    args = parser.parse_args(argv)
    casos = json.loads(conjunto.ARQUIVO.read_text(encoding="utf-8"))["casos"]
    conteudo = conjunto.serializar(montar(casos))
    if args.gravar:
        ARQUIVO.write_bytes(conteudo)
    igual = ARQUIVO.exists() and ARQUIVO.read_bytes() == conteudo
    print(f"sha256 {hashlib.sha256(conteudo).hexdigest()} | arquivo {'igual' if igual else 'DIFERENTE'}")
    return 0 if igual else 1


if __name__ == "__main__":
    sys.exit(main())
