"""
Métricas de previsão e teste de Diebold-Mariano (nota metodológica, N1 a N5).

- d_t = y_t² − (y_t − ŷ_t)²; positivo favorece o candidato;
- DM = d̄ / √(V̂/T), V̂ de Newey-West (Bartlett, L defasagens, centrada, ÷T);
- p = 1 − Φ(DM), unilateral; decisão só com p < limiar (estrito, precisão completa);
- Clark-West sobre f_t = d_t + ŷ_t², só como diagnóstico.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict

import numpy as np
import pandas as pd

from experiments.preditivo.config import NW_DEFASAGENS, P_LIMIAR, T_MINIMO

OK = "ok"
NAO_CALCULAVEL = "não calculável"


@dataclass
class ResultadoTeste:
    status: str
    motivo: str = ""
    T: int = 0
    media: float | None = None
    variancia: float | None = None
    estatistica: float | None = None
    p: float | None = None
    atende: bool = False
    datas_problema: tuple = ()

    def como_dict(self) -> dict:
        dados = asdict(self)
        dados["datas_problema"] = [str(d) for d in self.datas_problema]
        return dados


def phi(x: float) -> float:
    """Distribuição normal padrão acumulada."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


# Tolerância relativa para reconhecer série constante: a amplitude (máximo − mínimo)
# precisa ser no máximo 1e-12 vezes o maior valor absoluto da série, cerca de 4.500
# vezes o épsilon da máquina. Absorve resíduos de arredondamento sem apagar variações
# pequenas, mas reais, dos diferenciais de perda. Fixada antes de qualquer resultado.
TOLERANCIA_CONSTANTE = 1e-12


def serie_constante(serie: np.ndarray, tolerancia: float = TOLERANCIA_CONSTANTE) -> bool:
    escala = float(np.max(np.abs(serie)))
    return escala == 0.0 or float(np.ptp(serie)) <= tolerancia * escala


def variancia_newey_west(d: np.ndarray, defasagens: int) -> float:
    """V̂ = γ̂0 + 2 Σ w_j γ̂j, centrada em d̄, autocovariâncias divididas por T, pesos de Bartlett."""
    T = len(d)
    centrado = d - d.mean()
    variancia = float(np.dot(centrado, centrado) / T)
    for j in range(1, min(defasagens, T - 1) + 1):
        peso = 1.0 - j / (defasagens + 1.0)
        variancia += 2.0 * peso * float(np.dot(centrado[j:], centrado[:-j]) / T)
    return variancia


def alinhar(previsoes: pd.DataFrame, datas_elegiveis) -> tuple[pd.DataFrame | None, ResultadoTeste | None]:
    """Confere que há exatamente uma previsão finita por data elegível, sem sobras."""
    elegiveis = pd.DatetimeIndex(pd.to_datetime(list(datas_elegiveis)))
    datas = pd.DatetimeIndex(pd.to_datetime(previsoes["decision_date"]))
    if datas.duplicated().any():
        return None, ResultadoTeste(NAO_CALCULAVEL, "desalinhamento: data repetida",
                                    datas_problema=tuple(datas[datas.duplicated()]))
    sobras = datas.difference(elegiveis)
    if len(sobras):
        return None, ResultadoTeste(NAO_CALCULAVEL, "desalinhamento: previsão fora da lista de datas elegíveis",
                                    datas_problema=tuple(sobras))
    ausentes = elegiveis.difference(datas)
    if len(ausentes):
        return None, ResultadoTeste(NAO_CALCULAVEL, "previsão ausente em data elegível",
                                    datas_problema=tuple(ausentes))
    ordenado = previsoes.assign(decision_date=datas).set_index("decision_date").loc[elegiveis]
    y = ordenado["y"].to_numpy(dtype=float)
    yhat = ordenado["yhat"].to_numpy(dtype=float)
    nao_finitas = ~(np.isfinite(y) & np.isfinite(yhat))
    if nao_finitas.any():
        return None, ResultadoTeste(NAO_CALCULAVEL, "entrada não finita",
                                    datas_problema=tuple(elegiveis[nao_finitas]))
    return ordenado, None


def _teste_media(serie: np.ndarray, defasagens: int, limiar: float, minimo: int | None) -> ResultadoTeste:
    T = len(serie)
    if minimo is not None and T < minimo:
        return ResultadoTeste(NAO_CALCULAVEL, "amostra inferior ao mínimo previsto", T=T)
    if T < 2:
        return ResultadoTeste(NAO_CALCULAVEL, "amostra com menos de duas datas", T=T)
    if not np.isfinite(serie).all():
        return ResultadoTeste(NAO_CALCULAVEL, "entrada não finita", T=T)
    media = float(serie.mean())
    if serie_constante(serie):
        return ResultadoTeste(NAO_CALCULAVEL, "variância de longo prazo nula", T=T, media=media, variancia=0.0)
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            variancia = variancia_newey_west(serie, defasagens)
    except FloatingPointError:
        return ResultadoTeste(NAO_CALCULAVEL, "erro numérico no cálculo da variância", T=T, media=media)
    if not math.isfinite(variancia):
        return ResultadoTeste(NAO_CALCULAVEL, "erro numérico: variância não finita", T=T, media=media)
    if variancia <= 0.0:
        return ResultadoTeste(NAO_CALCULAVEL, "variância de longo prazo nula", T=T, media=media, variancia=variancia)
    estatistica = media / math.sqrt(variancia / T)
    p = 1.0 - phi(estatistica)
    return ResultadoTeste(OK, T=T, media=media, variancia=variancia, estatistica=estatistica, p=p, atende=p < limiar)


def diebold_mariano(previsoes, datas_elegiveis, defasagens=NW_DEFASAGENS, limiar=P_LIMIAR, minimo=T_MINIMO):
    """Critério 2. `minimo=None` desliga o mínimo operacional (só nos testes da rotina matemática)."""
    alinhado, falha = alinhar(previsoes, datas_elegiveis)
    if falha:
        return falha
    y, yhat = alinhado["y"].to_numpy(dtype=float), alinhado["yhat"].to_numpy(dtype=float)
    return _teste_media(y ** 2 - (y - yhat) ** 2, defasagens, limiar, minimo)


def clark_west(previsoes, datas_elegiveis, defasagens=NW_DEFASAGENS, limiar=P_LIMIAR, minimo=T_MINIMO):
    """Diagnóstico complementar (N5): não entra na elegibilidade."""
    alinhado, falha = alinhar(previsoes, datas_elegiveis)
    if falha:
        return falha
    y, yhat = alinhado["y"].to_numpy(dtype=float), alinhado["yhat"].to_numpy(dtype=float)
    return _teste_media(y ** 2 - (y - yhat) ** 2 + yhat ** 2, defasagens, limiar, minimo)


def r2_fora_da_amostra(y: np.ndarray, yhat: np.ndarray) -> float | None:
    """1 − SSE_candidato / SSE_zero; None (não calculável) se a perda da referência for zero."""
    y, yhat = np.asarray(y, dtype=float), np.asarray(yhat, dtype=float)
    sse_zero = float(np.sum(y ** 2))
    if sse_zero == 0.0 or not np.isfinite(sse_zero):
        return None
    return 1.0 - float(np.sum((y - yhat) ** 2)) / sse_zero


def erros(y: np.ndarray, yhat: np.ndarray) -> dict:
    y, yhat = np.asarray(y, dtype=float), np.asarray(yhat, dtype=float)
    validos = np.isfinite(y) & np.isfinite(yhat)
    if not validos.any():
        return {"mae": None, "rmse": None, "n": 0}
    e = y[validos] - yhat[validos]
    return {"mae": float(np.mean(np.abs(e))), "rmse": float(np.sqrt(np.mean(e ** 2))), "n": int(validos.sum())}


def acuracia_balanceada(y: np.ndarray, yhat: np.ndarray) -> float | None:
    """Média das taxas de acerto das classes alta (y > 0) e não alta; None se faltar uma classe."""
    y, yhat = np.asarray(y, dtype=float), np.asarray(yhat, dtype=float)
    alta, prevista = y > 0, yhat > 0
    if alta.all() or not alta.any():
        return None
    return float((np.mean(prevista[alta]) + np.mean(~prevista[~alta])) / 2.0)
