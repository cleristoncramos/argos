"""
Avaliação por ano com reestimação no início de cada ano (protocolo, 6.1 e 6.3).

Cada ano tem um ajuste próprio da Ridge, com o treino disponível na primeira
data avaliada (expurgo pelas datas). As previsões guardam o modelo vigente.
"""

from __future__ import annotations

import numpy as np
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
    alphas=None,
    registros_v2: bool = False,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Devolve as previsões (uma linha por data avaliada) e o resumo de cada ajuste.
    Linhas sem alvo realizado continuam na saída: a estratégia usa a previsão;
    as métricas e o teste filtram pela lista de datas elegíveis.

    `alphas` troca a grade (v2); `registros_v2` acrescenta os registros do protocolo v2,
    seção 4. Com os valores padrão, o comportamento é exatamente o da v1.
    """
    linhas, ajustes = [], []
    for ano in anos:
        divisao = dividir_ano(amostras, calendario, ano, embargo_por_ano[ano], limite_avaliacao)
        if len(divisao.avaliacao) == 0:
            continue
        extras = {} if alphas is None else {"alphas": alphas}
        ridge = ajustar_ridge(amostras, calendario, divisao.treino, divisao.primeira_data, **extras)
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
        ajuste = {
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
        }
        if registros_v2:
            ajuste.update(registros_do_ajuste(ridge, bloco))
        ajustes.append(ajuste)
    previsoes = pd.concat(linhas, ignore_index=True) if linhas else pd.DataFrame()
    return previsoes, ajustes


def registros_do_ajuste(ridge, bloco: pd.DataFrame) -> dict:
    """
    Protocolo v2, seção 4. O afastamento compara a Ridge com a média histórica expansiva
    (referência causal, atualizada a cada data) nas mesmas datas; a média do alvo no treino
    é outra série e fica registrada à parte.
    """
    diferenca = (bloco["yhat"] - bloco["yhat_media"]).to_numpy(dtype=float)
    finitas = diferenca[np.isfinite(diferenca)]
    coeficientes = np.asarray(ridge.modelo[-1].coef_, dtype=float)
    media = bloco["yhat_media"].to_numpy(dtype=float)
    return {
        "afastamento_media_historica": {
            "media_absoluta": float(np.mean(np.abs(finitas))) if len(finitas) else None,
            "raiz_quadratica_media": float(np.sqrt(np.mean(finitas ** 2))) if len(finitas) else None,
            "datas": int(len(finitas)),
        },
        "media_historica_nas_datas": float(np.mean(media[np.isfinite(media)])) if np.isfinite(media).any() else None,
        "norma_coeficientes": float(np.linalg.norm(coeficientes)),
        "alpha_no_limite_superior": bool(ridge.alpha == max(ridge.erros_internos)),
    }
