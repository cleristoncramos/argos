"""
Backtest da estratégia exposto ou caixa (protocolo, seção 8).

- decisão a cada 20 pregões, após o fechamento de t; execução no fechamento de entry_date;
- exposto se ŷ > c; senão, caixa remunerado pelo CDI realizado;
- custo por lado sobre o valor negociado; permanecer exposto não gera custo;
- todas as estratégias encerram na data de corte com custo de venda, se expostas.
O patrimônio começa em 1,0. Retornos em decimal, antes de impostos.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from experiments.preditivo.config import HORIZONTE, LIMIAR, PREGOES_ANO


@dataclass
class ResultadoEstrategia:
    nome: str
    retorno: float
    retorno_anualizado: float
    volatilidade: float
    drawdown_maximo: float      # magnitude positiva
    trocas: int
    exposicao: float            # fração dos intervalos exposta
    caminho: pd.DataFrame

    def como_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k != "caminho"}


def datas_de_decisao(previsoes: pd.DataFrame, passo: int = HORIZONTE) -> pd.DataFrame:
    """Uma decisão a cada `passo` datas avaliadas, a partir da primeira (sem sobreposição)."""
    ordenadas = previsoes.sort_values("decision_date").reset_index(drop=True)
    return ordenadas.iloc[::passo].reset_index(drop=True)


class CaixaCDI:
    """Fator do CDI realizado entre dois fechamentos: produto de (1 + taxa) em (anterior, atual]."""

    def __init__(self, cdi: pd.DataFrame):
        serie = cdi.sort_values("data")
        self.datas = pd.DatetimeIndex(pd.to_datetime(serie["data"]))
        self.log_acumulado = np.concatenate([[0.0], np.cumsum(np.log1p(serie["taxa"].to_numpy(dtype=float)))])

    def fator(self, anterior: pd.Timestamp, atual: pd.Timestamp) -> float:
        i = self.datas.searchsorted(anterior, side="right")
        j = self.datas.searchsorted(atual, side="right")
        if j <= i:
            raise ValueError(f"Sem CDI entre {anterior.date()} e {atual.date()}: conferir a série do caixa.")
        return float(np.exp(self.log_acumulado[j] - self.log_acumulado[i]))

    def cobre(self, inicio: pd.Timestamp, fim: pd.Timestamp) -> bool:
        return len(self.datas) > 0 and self.datas[0] <= inicio and self.datas[-1] >= fim


def _metricas(nome: str, datas, patrimonio, exposto, trocas) -> ResultadoEstrategia:
    patrimonio = np.asarray(patrimonio, dtype=float)
    intervalos = len(patrimonio) - 1
    retorno = float(patrimonio[-1] - 1.0)
    anualizado = float(patrimonio[-1] ** (PREGOES_ANO / intervalos) - 1.0) if intervalos > 0 else 0.0
    diarios = patrimonio[1:] / patrimonio[:-1] - 1.0
    volatilidade = float(np.std(diarios, ddof=1) * np.sqrt(PREGOES_ANO)) if len(diarios) > 1 else 0.0
    drawdown = float(np.max(1.0 - patrimonio / np.maximum.accumulate(patrimonio)))
    caminho = pd.DataFrame({"data": datas, "patrimonio": patrimonio, "exposto_no_intervalo": exposto})
    exposicao = float(np.mean(exposto[1:])) if intervalos > 0 else 0.0
    return ResultadoEstrategia(nome, retorno, anualizado, volatilidade, drawdown, trocas, exposicao, caminho)


def _simular(nome, precos, caixa, inicio, corte, alvos: dict, custo) -> ResultadoEstrategia:
    """`alvos`: data de execução → True (exposto) ou False (caixa)."""
    serie = precos[(precos["Date"] >= inicio) & (precos["Date"] <= corte)].sort_values("Date")
    datas = list(pd.to_datetime(serie["Date"]))
    preco = serie["Close"].to_numpy(dtype=float)
    if not datas or datas[0] != inicio:
        raise ValueError(f"A série de preços não tem a data inicial {inicio.date()}.")
    if not caixa.cobre(inicio, corte):
        raise ValueError("A série do CDI não cobre o período simulado.")

    exposto, patrimonio, trocas = False, 1.0, 0
    caminho, intervalos = [], []
    for k, data in enumerate(datas):
        if k > 0:
            intervalos.append(exposto)
            patrimonio *= preco[k] / preco[k - 1] if exposto else caixa.fator(datas[k - 1], data)
        else:
            intervalos.append(False)
        if data in alvos and alvos[data] != exposto:
            patrimonio *= 1.0 - custo
            exposto, trocas = alvos[data], trocas + 1
        if k == len(datas) - 1 and exposto:
            patrimonio *= 1.0 - custo
            exposto, trocas = False, trocas + 1
        caminho.append(patrimonio)
    return _metricas(nome, datas, caminho, np.array(intervalos, dtype=bool), trocas)


def backtest(precos, cdi, decisoes, custo, corte, limiar=LIMIAR) -> dict:
    """
    Estratégia, comprar e manter e caixa, no mesmo intervalo: do fechamento da
    primeira entry_date à data de corte. `decisoes` tem entry_date e yhat.
    """
    precos = precos.assign(Date=pd.to_datetime(precos["Date"]))
    caixa = CaixaCDI(cdi)
    corte = pd.Timestamp(corte)
    validas = decisoes.dropna(subset=["entry_date"])
    validas = validas[pd.to_datetime(validas["entry_date"]) <= corte]
    if validas.empty:
        raise ValueError("Nenhuma decisão com execução até a data de corte.")
    inicio = pd.Timestamp(validas["entry_date"].iloc[0])
    alvos = {pd.Timestamp(d): bool(y > limiar) for d, y in zip(validas["entry_date"], validas["yhat"])}
    return {
        "estrategia": _simular("estratégia", precos, caixa, inicio, corte, alvos, custo),
        "comprar_manter": _simular("comprar e manter", precos, caixa, inicio, corte, {inicio: True}, custo),
        "caixa": _simular("caixa", precos, caixa, inicio, corte, {}, custo),
    }
