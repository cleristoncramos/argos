"""
Amostras do piloto: variáveis disponíveis em t e alvo alinhado à entrada.

Cada linha guarda decision_date (t), entry_date (t + 1) e label_end_date
(t + 1 + horizonte), calculadas pelo calendário da própria série. O alvo é
y_t = P(label_end_date) / P(entry_date) − 1 (protocolo, seção 2).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.features import build_feature_table
from core.indicators import (
    add_bollinger_bands,
    add_exponential_moving_averages,
    add_macd,
    add_moving_averages,
    add_rsi,
)
from core.indicators_extra import add_atr, add_rolling_volatility
from experiments.preditivo.config import HORIZONTE

COLUNAS_PRECO = ("Date", "Open", "High", "Low", "Close")
EXTRAS = ("ret_20", "ret_60", "dist_pico_252")


def validar_precos(precos: pd.DataFrame) -> pd.DataFrame:
    """Confere colunas, ordem e valores; devolve a série ordenada e sem datas repetidas."""
    faltando = [c for c in COLUNAS_PRECO if c not in precos.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes na série de preços: {faltando}")
    serie = precos.loc[:, list(COLUNAS_PRECO)].copy()
    serie["Date"] = pd.to_datetime(serie["Date"]).dt.tz_localize(None).dt.normalize()
    serie = serie.dropna(subset=["Close"]).sort_values("Date")
    if serie["Date"].duplicated().any():
        raise ValueError("A série de preços tem datas repetidas.")
    valores = serie[["Open", "High", "Low", "Close"]].to_numpy(dtype=float)
    if not np.isfinite(valores).all() or (valores <= 0).any():
        raise ValueError("A série de preços tem valores ausentes, não finitos ou não positivos.")
    return serie.reset_index(drop=True)


def construir_variaveis(serie: pd.DataFrame) -> pd.DataFrame:
    """Variáveis de core/features.py e os acréscimos, todas só com dados até t."""
    df = serie.rename(columns={"Close": "Value"}).copy()
    df["Close"] = df["Value"]  # o ATR usa máxima, mínima e fechamento na mesma base de ajuste
    df = add_moving_averages(df, "Value", 20, 50)
    df = add_exponential_moving_averages(df, "Value", 12, 26)
    df = add_rsi(df, "Value", 14)
    df = add_macd(df, "Value", 12, 26, 9)
    df = add_bollinger_bands(df, "Value", 20)
    df = add_atr(df, 14, close_col="Value")
    df = add_rolling_volatility(df, 20)

    variaveis = build_feature_table(df)
    preco = df["Value"]
    variaveis["ret_20"] = preco / preco.shift(20) - 1
    variaveis["ret_60"] = preco / preco.shift(60) - 1
    variaveis["dist_pico_252"] = preco / preco.rolling(252, min_periods=252).max() - 1
    return variaveis


def construir_amostras(precos: pd.DataFrame, horizonte: int = HORIZONTE) -> pd.DataFrame:
    """
    Uma linha por data com todas as variáveis disponíveis (o aquecimento sai).

    Linhas sem alvo realizado na série (fim da série) ficam com y, entry_date
    e label_end_date vazios; quem decide se uma linha entra em treino ou
    avaliação são as funções de divisao.py, pelas datas.
    """
    serie = validar_precos(precos)
    variaveis = construir_variaveis(serie)
    nomes = [c for c in variaveis.columns if c != "Date"]

    datas = serie["Date"]
    preco = serie["Close"].to_numpy(dtype=float)
    n = len(serie)
    entrada = np.arange(n) + 1
    fim = np.arange(n) + 1 + horizonte
    tem_alvo = fim < n

    amostras = pd.DataFrame({"decision_date": datas})
    amostras["entry_date"] = pd.Series(pd.NaT, index=amostras.index, dtype="datetime64[ns]")
    amostras["label_end_date"] = pd.Series(pd.NaT, index=amostras.index, dtype="datetime64[ns]")
    amostras["y"] = np.nan
    tem_entrada = entrada < n
    amostras.loc[tem_entrada, "entry_date"] = datas.to_numpy()[entrada[tem_entrada]]
    amostras.loc[tem_alvo, "label_end_date"] = datas.to_numpy()[fim[tem_alvo]]
    amostras.loc[tem_alvo, "y"] = preco[fim[tem_alvo]] / preco[entrada[tem_alvo]] - 1

    amostras = pd.concat([amostras, variaveis[nomes]], axis=1)
    completas = np.isfinite(amostras[nomes].to_numpy(dtype=float)).all(axis=1)
    return amostras.loc[completas].reset_index(drop=True)


def nomes_variaveis(amostras: pd.DataFrame) -> list[str]:
    fixas = {"decision_date", "entry_date", "label_end_date", "y"}
    return [c for c in amostras.columns if c not in fixas]


def realizadas_ate(amostras: pd.DataFrame, data) -> pd.Series:
    """Máscara das amostras com alvo realizado na data (label_end_date ≤ data)."""
    return amostras["label_end_date"].notna() & (amostras["label_end_date"] <= pd.Timestamp(data))
