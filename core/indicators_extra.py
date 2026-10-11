"""ATR e volatilidade móvel -- calculados somente com dados até o instante t."""

import numpy as np
import pandas as pd

from core.returns_utils import simple_returns


def add_atr(
    df: pd.DataFrame,
    window: int = 14,
    high_col: str = "High",
    low_col: str = "Low",
    close_col: str = "Close",
) -> pd.DataFrame:
    """Adiciona a coluna ATR_{window} (suavização de Wilder, α = 1/window)."""
    if window < 2:
        raise ValueError("A janela do ATR deve ser >= 2.")

    out = df.copy()
    prev_close = out[close_col].shift(1)
    true_range = pd.concat(
        [
            out[high_col] - out[low_col],
            (out[high_col] - prev_close).abs(),
            (out[low_col] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    out[f"ATR_{window}"] = true_range.ewm(
        alpha=1 / window, adjust=False, min_periods=window
    ).mean()
    return out


def add_rolling_volatility(
    df: pd.DataFrame,
    window: int = 20,
    value_col: str = "Value",
    annualization_factor: float | None = None,
) -> pd.DataFrame:
    """Adiciona VOL_{window}: desvio-padrão móvel dos retornos simples (fração, não %)."""
    if window < 2:
        raise ValueError("A janela da volatilidade móvel deve ser >= 2.")

    out = df.copy()
    returns = simple_returns(out[value_col])
    vol = returns.rolling(window, min_periods=window).std()
    if annualization_factor:
        vol = vol * np.sqrt(annualization_factor)
    out[f"VOL_{window}"] = vol
    return out