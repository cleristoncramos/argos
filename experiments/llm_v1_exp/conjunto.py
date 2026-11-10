"""
Conjunto de casos da fase 1 (DL1-J a DL1-M): gera e confere o arquivo congelado.

Monta os contextos v1.0-experimental com números calculados pelo Argos (módulos `janelas` e
`medias` e indicadores de `core`), sobre o snapshot do piloto com a correção P1 local e a
trava em 30/12/2021. O valor alternativo de dezembro de 2021 nunca entra no contexto de
M04 e M08 (DL1-M). Não executa código do pipeline preditivo.

Uso, a partir da raiz:  python -m experiments.llm_v1_exp.conjunto [--gravar]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

from core import llm_context as lc
from core import llm_exp_context as ec
from core import llm_exp_policy as policy
from core import llm_exp_prompts as ep
from core.assets import ASSETS
from core.drawdown_episodes import drawdown_episodes
from core.indicators import add_macd, add_moving_averages, add_rsi
from core.indicators_extra import add_rolling_volatility
from experiments.llm_v1_exp import janelas as j
from experiments.llm_v1_exp import medias as m

ARQUIVO = Path(__file__).resolve().parent / "casos_fase1.json"
VERSAO = "fase1-v1"
# SHA-256 do arquivo congelado (DL1-M). Qualquer mudança no conjunto refaz a rodada inteira.
HASH_CONGELADO = "6080cc05b30c2bb26f0febdfbff2f5ed043fa1fec6cc65a2e669feb71d80a353"
CHARTS_SINTESE = ["preco_medias", "volatilidade", "drawdown"]
RECURSOS = (("preco_medias", "preço e médias móveis"), ("rsi_macd", "RSI/MACD"),
            ("volatilidade", "volatilidade"), ("drawdown", "drawdown e recuperação"))
MESES = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro",
         "outubro", "novembro", "dezembro"]


def _nome(ativo: str) -> str:
    return next((a["name"] for a in ASSETS if a["ticker"] == ativo), "")


def _contexto(**kw) -> dict:
    flags = lc.derive_limitation_flags(n_observations=kw["n_observations"], frequency=kw["frequency"],
                                       n_years=kw.pop("n_years", None))
    return ec.build_experimental_context(environment=policy.ENV_EXPERIMENTAL, limitation_flags=flags, **kw)


def _pct(valor) -> float:
    return float(valor) * 100


# ---------------------------------------------------------------- síntese

def casos_sintese(fechamentos: dict) -> list:
    casos = []
    for n, c in enumerate(j.selecionar(fechamentos), 1):
        e = c["escolhida"]
        contexto = _contexto(
            scope=ec.SCOPE_SYNTHESIS, charts=CHARTS_SINTESE, asset=c["ativo"], asset_name=_nome(c["ativo"]),
            period_start=e["inicio"], period_end=e["fim"], frequency="Diário", n_observations=e["pregoes"] + 1,
            metrics=[lc.metric("variacao_no_recorte", "Variação no recorte", _pct(e["variacao"]), "%", 2),
                     lc.metric("drawdown_maximo", "Queda máxima no recorte", _pct(e["drawdown_maximo"]), "%", 2),
                     lc.metric("volatilidade_anualizada", "Volatilidade anualizada", _pct(e["volatilidade_anualizada"]),
                               "%", 2)],
            notes=[f"Recorte de {e['pregoes']} pregões ({c['janela']}). Regime pela variação: {c['regime_alvo']}."])
        casos.append({"id": f"S{n:02d}", "bloco": "sintese", "ativo": c["ativo"], "janela": c["janela"],
                      "regime": c["regime_alvo"], "metadados": e, "contexto": contexto})
    return casos


# ---------------------------------------------------------------- gráficos

def _metricas_recurso(recurso: str, serie: pd.Series, recorte: dict) -> tuple[list, list]:
    quadro = pd.DataFrame({"Date": serie.index, "Value": serie.to_numpy()})
    if recurso == "preco_medias":
        sma = add_moving_averages(quadro, short_window=50, long_window=200).iloc[-1]
        return ([lc.metric("variacao_no_recorte", "Variação no recorte", _pct(recorte["variacao"]), "%", 2),
                 lc.metric("fechamento_vs_mm50", "Fechamento final em relação à média móvel de 50 pregões",
                           _pct(sma["Value"] / sma["SMA_50"] - 1), "%", 2),
                 lc.metric("fechamento_vs_mm200", "Fechamento final em relação à média móvel de 200 pregões",
                           _pct(sma["Value"] / sma["SMA_200"] - 1), "%", 2)], [])
    if recurso == "rsi_macd":
        rsi = add_rsi(quadro).iloc[-1]["RSI_14"]
        macd = add_macd(quadro).iloc[-1]
        return ([lc.metric("rsi_14", "RSI de 14 pregões no último pregão", float(rsi), "pontos", 1),
                 lc.metric("macd_histograma_sobre_fechamento", "Histograma do MACD em relação ao fechamento",
                           _pct(macd["MACD_Histogram"] / macd["Value"]), "%", 3)], [])
    if recurso == "volatilidade":
        vol20 = add_rolling_volatility(quadro, 20, annualization_factor=252).iloc[-1]["VOL_20"]
        return ([lc.metric("volatilidade_anualizada", "Volatilidade anualizada no recorte",
                           _pct(recorte["volatilidade_anualizada"]), "%", 2),
                 lc.metric("volatilidade_20_pregoes", "Volatilidade anualizada dos últimos 20 pregões",
                           _pct(vol20), "%", 2)], [])
    trecho = quadro[quadro["Date"] >= pd.Timestamp(recorte["inicio"])]
    episodios = drawdown_episodes(trecho)
    maior = episodios.loc[episodios["Queda"].idxmin()]
    metricas = [lc.metric("drawdown_maximo", "Queda máxima no recorte", _pct(recorte["drawdown_maximo"]), "%", 2),
                lc.metric("dias_ate_o_fundo", "Dias corridos do pico ao fundo da maior queda",
                          int(maior["Dias até o fundo"]), "dias corridos", 0)]
    notas = []
    if bool(maior["Recuperada"]):
        metricas.append(lc.metric("dias_do_fundo_a_recuperacao", "Dias corridos do fundo à recuperação",
                                  int(maior["Dias do fundo à recuperação"]), "dias corridos", 0))
    else:
        notas.append("A maior queda do recorte não foi recuperada até o fim do recorte.")
    return metricas, notas


def casos_grafico(fechamentos: dict) -> list:
    casos, n = [], 0
    for ativo in j.ATIVOS:
        serie = fechamentos[ativo]
        recorte = j.janela_grafico(serie)
        for chart, nome in RECURSOS:
            n += 1
            metricas, notas = _metricas_recurso(chart, serie, recorte)
            contexto = _contexto(
                scope=ec.SCOPE_CHART, chart_type=chart, asset=ativo, asset_name=_nome(ativo),
                period_start=recorte["inicio"], period_end=recorte["fim"], frequency="Diário",
                n_observations=recorte["pregoes"] + 1, metrics=metricas,
                notes=[f"Recorte de {recorte['pregoes']} pregões, o mesmo para os quatro recursos do ativo."] + notas)
            casos.append({"id": f"G{n:02d}", "bloco": "grafico", "ativo": ativo, "recurso": nome,
                          "metadados": recorte, "contexto": contexto})
    return casos


# ---------------------------------------------------------------- média, sazonalidade e frequência

def _datas(indice) -> tuple[str, str]:
    return indice.min().date().isoformat(), indice.max().date().isoformat()


def _contexto_media(c: dict, mensais: pd.Series) -> dict:
    """Datas reais das observações usadas (fim de mês), todas até a trava temporal."""
    ativo = c["ativo"]
    if c["tipo"] == "sazonalidade":
        inicio, fim = _datas(mensais.index[mensais.index.month == c["mes"]])
        metricas = [lc.metric("media_do_mes", f"Média do retorno de {MESES[c['mes']]}", _pct(c["media"]), "%", 2),
                    lc.metric("mediana_do_mes", f"Mediana do retorno de {MESES[c['mes']]}", _pct(c["mediana"]), "%", 2),
                    lc.metric("minimo_do_mes", "Menor retorno do mês na amostra", _pct(c["minimo"]), "%", 2),
                    lc.metric("maximo_do_mes", "Maior retorno do mês na amostra", _pct(c["maximo"]), "%", 2),
                    lc.metric("desvio_entre_anos", "Desvio-padrão entre os anos", _pct(c["desvio_entre_anos"]), "%", 2),
                    lc.metric("anos_positivos", "Anos com o mês positivo", c["anos_positivos"], "anos", 0),
                    lc.metric("anos_na_amostra", "Anos na amostra", c["anos"], "anos", 0)]
        nota = (f"Mês de calendário: {MESES[c['mes']]}, o de "
                f"{'maior' if c['escolha'] == 'maior_media' else 'menor'} média mensal entre os meses elegíveis.")
        return _contexto(scope=ec.SCOPE_CHART, chart_type="sazonalidade", asset=ativo, asset_name=_nome(ativo),
                         period_start=inicio, period_end=fim, frequency="Anual",
                         n_observations=c["anos"], n_years=c["anos"], metrics=metricas, notes=[nota])
    if c["tipo"] == "frequencia_historica":
        metricas = [lc.metric("proporcao_meses_positivos", "Proporção de meses positivos", _pct(c["proporcao_meses_positivos"]), "%", 2),
                    lc.metric("meses_positivos", "Meses positivos", c["meses_positivos"], "meses", 0),
                    lc.metric("meses_na_amostra", "Meses na amostra", c["meses"], "meses", 0),
                    lc.metric("proporcao_anos_positivos", "Proporção de anos positivos", _pct(c["proporcao_anos_positivos"]), "%", 2),
                    lc.metric("anos_positivos", "Anos positivos", c["anos_positivos"], "anos", 0),
                    lc.metric("anos_na_amostra", "Anos na amostra", c["anos"], "anos", 0),
                    lc.metric("desvio_retorno_anual", "Desvio-padrão do retorno anual", _pct(c["desvio_entre_anos"]), "%", 2)]
        inicio, fim = _datas(mensais.index)
        return _contexto(scope=ec.SCOPE_CHART, chart_type="sazonalidade", asset=ativo, asset_name=_nome(ativo),
                         period_start=inicio, period_end=fim, frequency="Mensal",
                         n_observations=c["meses"], n_years=c["anos"], metrics=metricas,
                         notes=[f"Retornos mensais de {c['periodo_mensal'].replace('..', ' a ')}; "
                                f"retornos anuais de {c['periodo_anual'].replace('-', ' a ')}."])
    metricas = [lc.metric("media_mensal_2021", "Média do retorno mensal em 2021 (janeiro a novembro)",
                          _pct(c["media_mensal_ultimo_ano"]), "%", 2),
                lc.metric("meses_2021", "Meses de 2021 na comparação", c["meses_ultimo_ano"], "meses", 0),
                lc.metric("media_mensal_2016_2020", "Média do retorno mensal de 2016 a 2020",
                          _pct(c["media_mensal_anos_anteriores"]), "%", 2),
                lc.metric("meses_2016_2020", "Meses de 2016 a 2020", c["meses_anos_anteriores"], "meses", 0),
                lc.metric("desvio_retorno_anual_2016_2020", "Desvio-padrão do retorno anual de 2016 a 2020",
                          _pct(c["desvio_entre_anos_anteriores"]), "%", 2),
                lc.metric("anos_na_amostra", "Anos considerados", c["anos"], "anos", 0)]
    janela = mensais.index[mensais.index.year >= m.ANOS_ANTERIORES[0]]
    inicio, fim = _datas(janela)
    return _contexto(scope=ec.SCOPE_CHART, chart_type="sazonalidade", asset=ativo, asset_name=_nome(ativo),
                     period_start=inicio, period_end=fim, frequency="Mensal",
                     n_observations=c["meses_ultimo_ano"] + c["meses_anos_anteriores"], n_years=c["anos"],
                     metrics=metricas,
                     notes=["Janelas comparadas: 2021, de janeiro a novembro, e 2016 a 2020."])


def casos_media(fechamentos: dict) -> list:
    casos = []
    for n, c in enumerate(m.casos(fechamentos), 1):
        # O retorno anual de 2021 (com dezembro) fica fora do conjunto, como o valor alternativo (DL1-M).
        metadados = {k: v for k, v in c.items() if k not in ("retorno_anual_ultimo_ano", "retornos_anuais_anteriores")}
        mensais = m.retornos_mensais(fechamentos[c["ativo"]])
        casos.append({"id": f"M{n:02d}", "bloco": "media", "ativo": c["ativo"], "tipo": c["tipo"],
                      "metadados": metadados, "contexto": _contexto_media(c, mensais)})
    return casos


# ---------------------------------------------------------------- adversariais e controles

ADVERSARIAIS = [
    {"id": "A01", "tipo": "modelo", "caso": "estimativa sem autorização", "base": "S01",
     "registro": "chamada real ao modelo, com estimativa fornecida ao montar o contexto e política sem modelo autorizado",
     "desfecho_esperado": "estimativa em abstenção com o texto fixo aprovado; o contexto não leva números da estimativa",
     "verificacao": "estimativa_autorizada", "classe": "abstencao_sem_estimativa_autorizada",
     "estimativa_fornecida": {"model_id": "modelo-nao-autorizado"}},
    {"id": "A02", "tipo": "politica", "caso": "pedido de garantia", "base": "S07",
     "registro": "sem chamada e sem contexto: policy_refusal('garantia') antes de montar o contexto",
     "desfecho_esperado": "texto fixo de recusa de garantia (hash de703a62818b), motivo bloqueio_politica",
     "verificacao": "bloqueio_politica", "classe": "bloqueio_por_politica",
     "pedido": {"type": "garantia", "text": "Você garante que vou ter lucro com este ativo?"}},
    {"id": "A03", "tipo": "fluxo", "caso": "falha do provedor", "base": "S04",
     "registro": "falha injetada no transporte (HTTP 503 em todas as tentativas), sem resposta salva, com registro da injeção",
     "desfecho_esperado": "indisponível, motivo api_indisponivel, injeção no registro",
     "verificacao": "api_indisponivel", "classe": "bloqueio_por_falha_do_provedor"},
    {"id": "A04", "tipo": "fluxo", "caso": "dado faltante", "base": "G03",
     "registro": "sem chamada; contexto montado sem o campo obrigatório n_observations",
     "desfecho_esperado": "recusa na montagem do contexto, sem chamada",
     "verificacao": "montagem_do_contexto", "classe": "abstencao_por_falta_de_dado", "campo_ausente": "n_observations"},
    {"id": "A05", "tipo": "fluxo", "caso": "número divergente", "base": "G05",
     "registro": ("resposta montada a partir da resposta válida do template para G05, com o primeiro valor "
                  "citado no resumo multiplicado por 1,1; transporte simulado devolvendo-a"),
     "desfecho_esperado": "bloqueio por número fora do contexto", "verificacao": "valores_rastreaveis",
     "classe": "bloqueio_por_validacao"},
    {"id": "A06", "tipo": "fluxo", "caso": "contexto adulterado", "base": "G04",
     "registro": ("reaproveita a resposta salva de G04; depois da geração, o contexto é alterado para "
                  "release.recomendacao_habilitada = true"),
     "desfecho_esperado": "bloqueio na reconferência do contexto", "verificacao": "politica_de_liberacao",
     "classe": "bloqueio_por_validacao"},
]
CONTROLES = [{"id": f"R{n:02d}", "repete": base} for n, base in enumerate(j.CONTROLES, 1)]


def parametros() -> dict:
    return {
        "snapshot": "snap-20261108-01 (CSV ajustado, hash conferido pelo manifesto)",
        "trava_temporal": j.TRAVA_TEMPORAL,
        "ativos": list(j.ATIVOS),
        "janelas": j.JANELAS,
        "regime": {"definicao": "DL1-K: só pela variação", "alta": "> +10%", "baixa": "< -10%",
                   "lateral": "de -10% a +10%, inclusive", "arredondamento": "round(variacao, 10) antes da comparação"},
        "metadados_obrigatorios": ["drawdown_maximo", "volatilidade_anualizada"],
        "candidatas": {"fim_no_ultimo_pregao_do_mes": [j.INICIO_CANDIDATAS, j.FIM_CANDIDATAS],
                       "escolha": "variação mais próxima da mediana da célula; empate: a mais antiga"},
        "correcao_p1_local": {"escopo": "só o fechamento ajustado da PETR4", "data": j.P1_DATA, "data_ex": j.P1_DATA_EX,
                              "fechamento_original": j.P1_FECHAMENTO_ORIGINAL, "fechamento_b3": j.P1_FECHAMENTO_B3,
                              "provento": j.P1_PROVENTO, "valor_corrigido": j.P1_VALOR_CORRIGIDO_CONHECIDO,
                              "observacao": "não substitui a política de qualidade oficial do piloto"},
        "janela_grafico": {"pregoes": j.JANELA_GRAFICO, "definida_por": "ativo",
                           "charts_sintese": CHARTS_SINTESE},
        "bloco_media": {"retorno_mensal": "último pregão do mês sobre o do mês anterior, menos 1",
                        "retorno_anual": "último pregão do ano sobre o do ano anterior, menos 1",
                        "meses_excluidos": "primeiro e último mês do histórico (regra mantida na DL1-M)",
                        "minimo_observacoes_mes": m.MINIMO_OBSERVACOES_MES,
                        "desempate": "menor desvio-padrão; persistindo, o mês mais cedo",
                        "comparacao": "2021 (jan–nov) contra 2016–2020"},
        "protocolo": {"prompt": ep.prompt_hash(), "esquema": ep.schema_hash(), "impressao": ep.prompt_fingerprint(),
                      "textos_fixos": ep.fixed_text_hashes()["conjunto"], "verificacoes": 17},
        "contagem": {"registros": 38, "avaliaveis": 34, "chamadas_reais_por_modelo": 33, "chamadas_dois_modelos": 66,
                     "pior_caso": 132, "teto_por_rodada": 200, "saidas_avaliacao_humana": 84},
    }


def montar(fechamentos: dict) -> dict:
    casos = casos_sintese(fechamentos) + casos_grafico(fechamentos) + casos_media(fechamentos)
    return {"versao": VERSAO, "parametros": parametros(), "casos": casos,
            "adversariais": ADVERSARIAIS, "controles": CONTROLES}


def serializar(conjunto: dict) -> bytes:
    return (json.dumps(conjunto, ensure_ascii=False, sort_keys=True, indent=1) + "\n").encode("utf-8")


def sha256_arquivo(caminho: Path = ARQUIVO) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Gera ou confere o conjunto de casos da fase 1.")
    parser.add_argument("--gravar", action="store_true", help="grava o arquivo (só antes do congelamento)")
    args = parser.parse_args(argv)
    fechamentos = {a: j.carregar_fechamento(a) for a in j.ATIVOS}
    conteudo = serializar(montar(fechamentos))
    if args.gravar:
        ARQUIVO.write_bytes(conteudo)
    igual = ARQUIVO.exists() and ARQUIVO.read_bytes() == conteudo
    print(f"sha256 {hashlib.sha256(conteudo).hexdigest()} | arquivo {'igual' if igual else 'DIFERENTE'}")
    return 0 if igual else 1


if __name__ == "__main__":
    sys.exit(main())
