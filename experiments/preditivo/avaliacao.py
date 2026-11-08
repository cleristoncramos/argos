"""
Avaliação por ano com reestimação no início de cada ano (protocolo, 6.1 e 6.3).

Cada ano tem um ajuste próprio da Ridge, com o treino disponível na primeira
data avaliada (expurgo pelas datas). As previsões guardam o modelo vigente.
"""

from __future__ import annotations

import pandas as pd

from experiments.preditivo.divisoes import dividir_ano
from experiments.preditivo.modelos import ajustar_ridge, prever_media_historica, prever_zero


def prever_anos(
    amostras: pd.DataFrame,
    calendario: pd.Series,
    anos,
    embargo_por_ano: dict,
    ativo: str,
    limite_avaliacao=None,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Devolve as previsões (uma linha por data avaliada) e o resumo de cada ajuste.
    Linhas sem alvo realizado continuam na saída: a estratégia usa a previsão;
    as métricas e o teste filtram pela lista de datas elegíveis.
    """
    linhas, ajustes = [], []
    for ano in anos:
        divisao = dividir_ano(amostras, calendario, ano, embargo_por_ano[ano], limite_avaliacao)
        if len(divisao.avaliacao) == 0:
            continue
        ridge = ajustar_ridge(amostras, calendario, divisao.treino, divisao.primeira_data)
        avaliar = amostras.iloc[divisao.avaliacao]
        modelo_id = f"ridge-{ativo}-{ano}-alpha{ridge.alpha:g}"
        bloco = avaliar[["decision_date", "entry_date", "label_end_date", "y"]].copy()
        bloco["yhat"] = ridge.prever(amostras, divisao.avaliacao)
        alvo_treino = amostras.iloc[divisao.treino]["y"]
        bloco["yhat_zero"] = prever_zero(len(bloco))
        bloco["yhat_media"] = prever_media_historica(amostras, bloco["decision_date"])
        bloco["modelo_id"] = modelo_id
        bloco["ano_ajuste"] = ano
        linhas.append(bloco)
        ajustes.append({
            "ano": ano,
            "modelo_id": modelo_id,
            "data_ajuste": divisao.primeira_data.date().isoformat(),
            "alpha": ridge.alpha,
            "erros_internos": ridge.erros_internos,
            "anos_internos": list(ridge.anos_internos),
            "n_treino": ridge.n_treino,
            "n_avaliacao": len(divisao.avaliacao),
            "embargo": embargo_por_ano[ano],
            # Alpha alto encolhe os coeficientes; com intercepto, as previsões se aproximam
            # de uma constante ligada à média do alvo no treino, não necessariamente de zero.
            "fit_intercept": bool(ridge.modelo[-1].fit_intercept),
            "media_alvo_treino": float(alvo_treino.mean()),
            "previsoes_media": float(bloco["yhat"].mean()),
            "previsoes_desvio": float(bloco["yhat"].std(ddof=1)) if len(bloco) > 1 else 0.0,
            "alpha_no_limite_da_grade": ridge.alpha in (min(ridge.erros_internos), max(ridge.erros_internos)),
        })
    previsoes = pd.concat(linhas, ignore_index=True) if linhas else pd.DataFrame()
    return previsoes, ajustes
