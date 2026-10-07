"""
Camada de features: transforma indicadores técnicos em variáveis
numéricas para análises e modelos futuros.

- Não define alvo (retorno futuro, direção, volatilidade futura).
- Não gera sinais de compra ou venda.
- Usa apenas dados até o instante t (sem informação futura).
- Variáveis normalizadas (razões e percentuais), pois níveis de preço
  não são comparáveis entre ativos nem estacionários.
"""

import numpy as np
import pandas as pd

from core.indicators import mask_warmup

BASE_FEATURES = [
    "ret_1",
    "close_over_sma_short",
    "close_over_sma_long",
    "ema_spread",
    "rsi",
    "macd_hist_over_close",
    "bb_percent_b",
    "atr_over_close",
    "vol_rolling",
]


def build_feature_table(
    df: pd.DataFrame,
    sma_short: int = 20,
    sma_long: int = 50,
    ema_short: int = 12,
    ema_long: int = 26,
    rsi_window: int = 14,
    atr_window: int = 14,
    vol_window: int = 20,
    lags: tuple[int, ...] = (1, 2, 3),
    value_col: str = "Value",
) -> pd.DataFrame:
    """
    Recebe o DataFrame já com os indicadores (colunas SMA_*, EMA_*, RSI_*,
    MACD_Histogram, BB_*, ATR_*, VOL_*) e devolve Date + features.

    Cada feature base é seguida de versões defasadas (`_lag1`, `_lag2`...),
    em que `_lagk` é o valor k períodos antes de t.
    """
    required = [
        f"SMA_{sma_short}", f"SMA_{sma_long}",
        f"EMA_{ema_short}", f"EMA_{ema_long}",
        f"RSI_{rsi_window}", "MACD_Histogram",
        "BB_Upper", "BB_Lower",
        f"ATR_{atr_window}", f"VOL_{vol_window}",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes para montar features: {missing}")

    close = df[value_col]
    band_width = (df["BB_Upper"] - df["BB_Lower"]).replace(0, np.nan)

    features = pd.DataFrame(index=df.index)
    if "Date" in df.columns:
        features["Date"] = df["Date"]

    features["ret_1"] = close.pct_change()
    features["close_over_sma_short"] = close / df[f"SMA_{sma_short}"] - 1
    features["close_over_sma_long"] = close / df[f"SMA_{sma_long}"] - 1
    features["ema_spread"] = (df[f"EMA_{ema_short}"] - df[f"EMA_{ema_long}"]) / close
    features["rsi"] = df[f"RSI_{rsi_window}"]
    features["macd_hist_over_close"] = df["MACD_Histogram"] / close
    features["bb_percent_b"] = (close - df["BB_Lower"]) / band_width
    features["atr_over_close"] = df[f"ATR_{atr_window}"] / close
    features["vol_rolling"] = df[f"VOL_{vol_window}"]

    # Aquecimento das médias exponenciais: ~3x a janela longa
    warmup = 3 * max(ema_long, 26)
    recursive = ["ema_spread", "macd_hist_over_close"]
    features = mask_warmup(features, recursive, warmup)

    lagged = {
        f"{name}_lag{k}": features[name].shift(k)
        for name in BASE_FEATURES
        for k in lags
    }
    features = pd.concat([features, pd.DataFrame(lagged, index=features.index)], axis=1)

    return features