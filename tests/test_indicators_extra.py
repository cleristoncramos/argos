import numpy as np
import pandas as pd
import pytest

from core.indicator_docs import INDICATOR_DOCS, find_forbidden_language
from core.indicators import (
    add_bollinger_bands,
    add_exponential_moving_averages,
    add_macd,
    add_moving_averages,
    add_rsi,
)
from core.indicators_extra import add_atr, add_rolling_volatility


@pytest.fixture
def ohlc() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 200
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    high = close + rng.uniform(0.1, 1.5, n)
    low = close - rng.uniform(0.1, 1.5, n)
    return pd.DataFrame(
        {
            "Date": pd.date_range("2022-01-01", periods=n, freq="D"),
            "Open": close + rng.normal(0, 0.3, n),
            "High": high,
            "Low": low,
            "Close": close,
            "Volume": rng.integers(1_000, 5_000, n),
            "Value": close,
        }
    )


# --- ATR ---------------------------------------------------------------
def test_atr_manual_first_value(ohlc):
    out = add_atr(ohlc, window=14)
    assert out["ATR_14"].iloc[:13].isna().all()
    assert out["ATR_14"].iloc[13:].notna().all()
    assert (out["ATR_14"].dropna() > 0).all()


def test_atr_true_range_uses_previous_close():
    df = pd.DataFrame(
        {"High": [10.0, 12.0], "Low": [9.0, 11.5], "Close": [9.5, 11.8]}
    )
    out = add_atr(df, window=2)
    # TR_1 = max(0.5, |12-9.5|, |11.5-9.5|) = 2.5 (lacuna de alta)
    # ATR_1 = média ponderada (α=0.5) de TR_0=1.0 e TR_1=2.5 = 1.75
    assert out["ATR_2"].iloc[1] == pytest.approx(1.75)


def test_atr_invalid_window(ohlc):
    with pytest.raises(ValueError):
        add_atr(ohlc, window=1)


# --- Volatilidade móvel ---------------------------------------------------
def test_rolling_vol_matches_manual(ohlc):
    out = add_rolling_volatility(ohlc, window=20)
    expected = ohlc["Value"].pct_change().iloc[-20:].std()
    assert out["VOL_20"].iloc[-1] == pytest.approx(expected)


def test_rolling_vol_annualization(ohlc):
    plain = add_rolling_volatility(ohlc, window=20)["VOL_20"]
    annual = add_rolling_volatility(ohlc, window=20, annualization_factor=252)["VOL_20"]
    assert (annual.dropna() / plain.dropna()).round(8).eq(round(np.sqrt(252), 8)).all()


def test_rolling_vol_insufficient_data():
    df = pd.DataFrame({"Value": [1.0, 1.1, 1.2]})
    out = add_rolling_volatility(df, window=20)
    assert out["VOL_20"].isna().all()


def test_does_not_mutate_input(ohlc):
    cols_before = list(ohlc.columns)
    add_atr(ohlc)
    add_rolling_volatility(ohlc)
    assert list(ohlc.columns) == cols_before


# --- Auditoria de look-ahead (todos os indicadores) -------------------------
INDICATOR_PIPELINES = {
    "SMA": (
        lambda d: add_moving_averages(d, value_col="Value", short_window=20, long_window=50),
        ["SMA_20", "SMA_50"],
    ),
    "EMA": (
        lambda d: add_exponential_moving_averages(d, value_col="Value", short_window=12, long_window=26),
        ["EMA_12", "EMA_26"],
    ),
    "Bollinger": (
        lambda d: add_bollinger_bands(d, value_col="Value", window=20, num_std=2.0),
        ["BB_Lower", "BB_Middle", "BB_Upper"],
    ),
    "RSI": (
        lambda d: add_rsi(d, value_col="Value", window=14),
        ["RSI_14"],
    ),
    "MACD": (
        lambda d: add_macd(d, value_col="Value", short_span=12, long_span=26, signal_span=9),
        ["MACD", "MACD_Signal", "MACD_Histogram"],
    ),
    "ATR": (lambda d: add_atr(d, window=14), ["ATR_14"]),
    "VOL": (lambda d: add_rolling_volatility(d, window=20), ["VOL_20"]),
}


@pytest.mark.parametrize("name", INDICATOR_PIPELINES)
def test_no_lookahead_truncation(ohlc, name):
    """O valor em t calculado sobre a série completa deve ser idêntico ao
    calculado sobre a série cortada em t. Qualquer diferença indica uso de
    dados futuros."""
    func, columns = INDICATOR_PIPELINES[name]
    cut = 150
    full = func(ohlc)
    truncated = func(ohlc.iloc[:cut].copy())
    for column in columns:
        np.testing.assert_allclose(
            full[column].iloc[:cut].to_numpy(dtype=float),
            truncated[column].to_numpy(dtype=float),
            rtol=1e-9,
            equal_nan=True,
            err_msg=f"{name}/{column}: possível vazamento de informação futura",
        )


# --- Documentação -----------------------------------------------------------
def test_all_priority_indicators_documented():
    expected = {"sma", "ema", "bollinger", "rsi", "macd", "atr", "volatilidade_movel", "volume"}
    assert set(INDICATOR_DOCS) == expected


def test_docs_have_required_fields():
    for doc in INDICATOR_DOCS.values():
        assert doc.measures and doc.formula and doc.limitations


def test_docs_use_neutral_language():
    assert find_forbidden_language() == []


def _wilder_rsi_manual(values, window):
    """Implementação de referência, passo a passo, da RSI de Wilder."""
    deltas = [np.nan] + [values[i] - values[i - 1] for i in range(1, len(values))]
    avg_gain = avg_loss = None
    out = [np.nan] * len(values)
    for t in range(1, len(values)):
        gain = max(deltas[t], 0.0)
        loss = max(-deltas[t], 0.0)
        if avg_gain is None:
            avg_gain, avg_loss = gain, loss
        else:
            avg_gain = (avg_gain * (window - 1) + gain) / window
            avg_loss = (avg_loss * (window - 1) + loss) / window
        if t >= window:
            if avg_loss == 0:
                out[t] = 100.0
            else:
                out[t] = 100 - 100 / (1 + avg_gain / avg_loss)
    return np.array(out)


def test_rsi_wilder_matches_manual(ohlc):
    from core.indicators import add_rsi
    result = add_rsi(ohlc, value_col="Value", window=14)["RSI_14"].to_numpy()
    expected = _wilder_rsi_manual(ohlc["Value"].to_numpy(), 14)
    np.testing.assert_allclose(result, expected, rtol=1e-9, equal_nan=True)


def test_rsi_flat_series_is_nan_by_default():
    from core.indicators import add_rsi
    df = pd.DataFrame({"Value": [10.0] * 30})
    assert add_rsi(df, window=14)["RSI_14"].isna().all()


def test_rsi_flat_series_legacy_returns_zero():
    from core.indicators import add_rsi
    df = pd.DataFrame({"Value": [10.0] * 30})
    out = add_rsi(df, window=14, flat_series="legacy")["RSI_14"].dropna()
    assert (out == 0).all()


def test_rsi_cutler_still_available(ohlc):
    from core.indicators import add_rsi
    wilder = add_rsi(ohlc, window=14)["RSI_14"]
    cutler = add_rsi(ohlc, window=14, method="cutler")["RSI_14"]
    assert not np.allclose(wilder.dropna(), cutler.dropna())


def test_rsi_always_between_0_and_100(ohlc):
    from core.indicators import add_rsi
    values = add_rsi(ohlc, window=14)["RSI_14"].dropna()
    assert values.between(0, 100).all()