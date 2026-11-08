"""
Referências e modelo candidato (protocolo, seção 7).

- retorno zero: ŷ = 0;
- média histórica: média dos alvos com label_end_date ≤ decision_date;
- Ridge: variáveis padronizadas só no treino; alpha da grade fixa escolhido
  pelo menor erro quadrático médio nas validações internas (empate: maior alpha).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from experiments.preditivo.amostras import nomes_variaveis
from experiments.preditivo.config import ALPHAS, VALIDACOES_INTERNAS
from experiments.preditivo.divisoes import divisoes_internas


def prever_zero(n: int) -> np.ndarray:
    return np.zeros(n)


def prever_media_historica(amostras: pd.DataFrame, datas_decisao: pd.Series) -> np.ndarray:
    """Para cada data de decisão, a média dos alvos já realizados nela (NaN se nenhum)."""
    realizadas = amostras.dropna(subset=["label_end_date", "y"]).sort_values("label_end_date")
    fins = realizadas["label_end_date"].to_numpy()
    acumulado = np.concatenate([[0.0], np.cumsum(realizadas["y"].to_numpy(dtype=float))])
    quantos = np.searchsorted(fins, pd.to_datetime(datas_decisao).to_numpy(), side="right")
    with np.errstate(invalid="ignore", divide="ignore"):
        media = acumulado[quantos] / quantos
    return np.where(quantos > 0, media, np.nan)


def _pipeline(alpha: float):
    return make_pipeline(StandardScaler(), Ridge(alpha=alpha))


def _ajustar(amostras: pd.DataFrame, indices: np.ndarray, alpha: float):
    nomes = nomes_variaveis(amostras)
    dados = amostras.iloc[indices]
    modelo = _pipeline(alpha)
    modelo.fit(dados[nomes].to_numpy(dtype=float), dados["y"].to_numpy(dtype=float))
    return modelo


@dataclass
class RidgeAjustada:
    alpha: float
    modelo: object
    erros_internos: dict = field(default_factory=dict)   # alpha -> EQM médio das validações internas
    anos_internos: tuple = ()
    n_treino: int = 0

    def prever(self, amostras: pd.DataFrame, indices: np.ndarray) -> np.ndarray:
        nomes = nomes_variaveis(amostras)
        return self.modelo.predict(amostras.iloc[indices][nomes].to_numpy(dtype=float))


def escolher_alpha(erros: dict) -> float:
    """Menor erro quadrático médio; empate (até a precisão de ponto flutuante): o maior alpha."""
    melhor = min(erros.values())
    empatados = [a for a, e in erros.items() if np.isclose(e, melhor, rtol=0.0, atol=1e-15)]
    return max(empatados)


def ajustar_ridge(
    amostras: pd.DataFrame,
    calendario: pd.Series,
    treino: np.ndarray,
    primeira_externa: pd.Timestamp,
    alphas=ALPHAS,
    validacoes=VALIDACOES_INTERNAS,
) -> RidgeAjustada:
    internas = divisoes_internas(amostras, calendario, treino, primeira_externa, validacoes)
    erros = {}
    for alpha in alphas:
        por_ano = []
        for divisao in internas:
            if len(divisao.treino) == 0 or len(divisao.avaliacao) == 0:
                raise ValueError(f"Validação interna de {divisao.ano} sem treino ou sem avaliação.")
            modelo = _ajustar(amostras, divisao.treino, alpha)
            nomes = nomes_variaveis(amostras)
            avaliar = amostras.iloc[divisao.avaliacao]
            previsto = modelo.predict(avaliar[nomes].to_numpy(dtype=float))
            por_ano.append(float(np.mean((avaliar["y"].to_numpy(dtype=float) - previsto) ** 2)))
        erros[float(alpha)] = float(np.mean(por_ano))
    alpha = escolher_alpha(erros)
    return RidgeAjustada(
        alpha=alpha,
        modelo=_ajustar(amostras, treino, alpha),
        erros_internos=erros,
        anos_internos=tuple(d.ano for d in internas),
        n_treino=len(treino),
    )
