from numbers import Integral

import numpy as np
import pandas as pd


# ==========================================================
# Validação e utilitários
# ==========================================================
def _check_window(window, name: str = "janela") -> None:
    """Garante que a janela/período seja um inteiro >= 2."""
    if isinstance(window, bool) or not isinstance(window, Integral) or window < 2:
        raise ValueError(
            f"A {name} deve ser um inteiro >= 2 (recebido: {window!r})."
        )


def mask_warmup(
    df: pd.DataFrame,
    columns: list[str],
    periods: int,
) -> pd.DataFrame:
    """
    Marca como NaN os primeiros `periods` valores de colunas recursivas
    (EMA/MACD), cujo início depende do ponto de partida da série.

    Não é usada nos gráficos; serve para a camada de features e para
    exportações destinadas a modelos.
    """
    result = df.copy()
    if periods > 0 and columns:
        result.loc[result.index[:periods], columns] = np.nan
    return result


# ==========================================================
# Médias móveis
# ==========================================================
def add_moving_averages(
    df: pd.DataFrame,
    value_col: str = "Value",
    short_window: int = 3,
    long_window: int = 5,
) -> pd.DataFrame:
    """
    Adiciona médias móveis simples de curto e longo prazo.
    Usa apenas dados até o instante t (janela retrospectiva).
    """
    _check_window(short_window, "janela curta")
    _check_window(long_window, "janela longa")

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

    Observação: os primeiros valores dependem do ponto inicial da série
    (período de aquecimento). Use `mask_warmup` para features/modelos.
    """
    _check_window(short_window, "janela curta")
    _check_window(long_window, "janela longa")

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


# ==========================================================
# RSI
# ==========================================================
def add_rsi(
    df: pd.DataFrame,
    value_col: str = "Value",
    window: int = 14,
    method: str = "wilder",
    flat_series: str = "nan",
) -> pd.DataFrame:
    """
    Calcula o Relative Strength Index (RSI).

    Parâmetros
    ----------
    method:
        "wilder" (padrão): suavização de Wilder (alpha = 1/window),
        a mesma usada pela maioria das plataformas.
        "cutler": média simples de ganhos e perdas (variante anterior).
    flat_series:
        "nan" (padrão): série sem variação resulta em RSI indefinido (NaN).
        "legacy": série sem variação resulta em RSI = 0 (comportamento antigo).

    Observação: a média de Wilder é inicializada com o primeiro ganho/perda
    (e não com a média simples das N primeiras variações). Os primeiros
    valores podem diferir levemente de outras plataformas e convergem
    ao longo da série.
    """
    _check_window(window, "janela do RSI")

    if method not in {"cutler", "wilder"}:
        raise ValueError("method deve ser 'cutler' ou 'wilder'.")
    if flat_series not in {"legacy", "nan"}:
        raise ValueError("flat_series deve ser 'legacy' ou 'nan'.")

    result = df.copy()

    delta = result[value_col].diff()

    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    if method == "cutler":
        avg_gain = gains.rolling(
            window=window,
            min_periods=window,
        ).mean()

        avg_loss = losses.rolling(
            window=window,
            min_periods=window,
        ).mean()
    else:
        avg_gain = gains.ewm(
            alpha=1 / window,
            adjust=False,
            min_periods=window,
        ).mean()

        avg_loss = losses.ewm(
            alpha=1 / window,
            adjust=False,
            min_periods=window,
        ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    rsi = rsi.where(avg_loss != 0, 100.0)
    rsi = rsi.where(avg_gain != 0, 0.0)

    if flat_series == "nan":
        both_zero = (avg_gain == 0) & (avg_loss == 0)
        rsi = rsi.mask(both_zero, np.nan)

    result[f"RSI_{window}"] = rsi

    return result


# ==========================================================
# MACD
# ==========================================================
def add_macd(
    df: pd.DataFrame,
    value_col: str = "Value",
    short_span: int = 12,
    long_span: int = 26,
    signal_span: int = 9,
) -> pd.DataFrame:
    """
    Calcula MACD, linha de sinal e histograma.

    Observação: baseado em EMAs; os primeiros valores dependem do ponto
    inicial da série. Use `mask_warmup` para features/modelos.
    """
    _check_window(short_span, "EMA curta")
    _check_window(long_span, "EMA longa")
    _check_window(signal_span, "linha de sinal")

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


# ==========================================================
# Bandas de Bollinger
# ==========================================================
def add_bollinger_bands(
    df: pd.DataFrame,
    value_col: str = "Value",
    window: int = 20,
    num_std: float = 2.0,
    ddof: int = 1,
) -> pd.DataFrame:
    """
    Calcula as bandas de Bollinger.

    Parâmetros
    ----------
    ddof:
        1 (padrão): desvio-padrão amostral.
        0: desvio-padrão populacional (definição clássica de Bollinger).
    """
    _check_window(window, "janela das Bandas de Bollinger")

    if ddof not in (0, 1):
        raise ValueError("ddof deve ser 0 ou 1.")

    result = df.copy()

    middle = result[value_col].rolling(
        window=window,
        min_periods=window,
    ).mean()

    standard_deviation = result[value_col].rolling(
        window=window,
        min_periods=window,
    ).std(ddof=ddof)

    result["BB_Middle"] = middle
    result["BB_Upper"] = middle + (
        num_std * standard_deviation
    )
    result["BB_Lower"] = middle - (
        num_std * standard_deviation
    )

    return result