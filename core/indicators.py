import numpy as np
import pandas as pd


def add_moving_averages(
    df: pd.DataFrame,
    value_col: str = "Value",
    short_window: int = 3,
    long_window: int = 5,
) -> pd.DataFrame:
    """
    Adiciona médias móveis simples de curto e longo prazo.
    """
    result = df.copy()

    result[f"SMA_{short_window}"] = (
        result[value_col]
        .rolling(
            window=short_window,
            min_periods=short_window,
        )
        .mean()
    )

    result[f"SMA_{long_window}"] = (
        result[value_col]
        .rolling(
            window=long_window,
            min_periods=long_window,
        )
        .mean()
    )

    return result


def add_exponential_moving_averages(
    df: pd.DataFrame,
    value_col: str = "Value",
    short_window: int = 3,
    long_window: int = 5,
) -> pd.DataFrame:
    """
    Adiciona médias móveis exponenciais de curto e longo prazo.
    """
    result = df.copy()

    result[f"EMA_{short_window}"] = (
        result[value_col]
        .ewm(
            span=short_window,
            adjust=False,
        )
        .mean()
    )

    result[f"EMA_{long_window}"] = (
        result[value_col]
        .ewm(
            span=long_window,
            adjust=False,
        )
        .mean()
    )

    return result


def add_rsi(
    df: pd.DataFrame,
    value_col: str = "Value",
    window: int = 14,
) -> pd.DataFrame:
    """
    Calcula o Relative Strength Index (RSI).
    """
    result = df.copy()

    delta = result[value_col].diff()

    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.rolling(
        window=window,
        min_periods=window,
    ).mean()

    avg_loss = losses.rolling(
        window=window,
        min_periods=window,
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    rsi = rsi.where(avg_loss != 0, 100.0)
    rsi = rsi.where(avg_gain != 0, 0.0)

    result[f"RSI_{window}"] = rsi

    return result


def add_macd(
    df: pd.DataFrame,
    value_col: str = "Value",
    short_span: int = 12,
    long_span: int = 26,
    signal_span: int = 9,
) -> pd.DataFrame:
    """
    Calcula MACD, linha de sinal e histograma.
    """
    result = df.copy()

    ema_short = result[value_col].ewm(
        span=short_span,
        adjust=False,
    ).mean()

    ema_long = result[value_col].ewm(
        span=long_span,
        adjust=False,
    ).mean()

    result["MACD"] = ema_short - ema_long

    result["MACD_Signal"] = result["MACD"].ewm(
        span=signal_span,
        adjust=False,
    ).mean()

    result["MACD_Histogram"] = (
        result["MACD"] - result["MACD_Signal"]
    )

    return result


def add_bollinger_bands(
    df: pd.DataFrame,
    value_col: str = "Value",
    window: int = 20,
    num_std: float = 2.0,
) -> pd.DataFrame:
    """
    Calcula as bandas de Bollinger.
    """
    result = df.copy()

    middle = result[value_col].rolling(
        window=window,
        min_periods=window,
    ).mean()

    standard_deviation = result[value_col].rolling(
        window=window,
        min_periods=window,
    ).std()

    result["BB_Middle"] = middle
    result["BB_Upper"] = middle + (
        num_std * standard_deviation
    )
    result["BB_Lower"] = middle - (
        num_std * standard_deviation
    )

    return result