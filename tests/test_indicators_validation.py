import numpy as np
import pandas as pd
import pytest

from core.indicators import (
    _check_window,
    add_bollinger_bands,
    add_exponential_moving_averages,
    add_macd,
    add_moving_averages,
    add_rsi,
    mask_warmup,
)


@pytest.fixture
def prices() -> pd.DataFrame:
    rng = np.random.default_rng(1)
    return pd.DataFrame({"Value": 100 + np.cumsum(rng.normal(0, 1, 60))})


@pytest.mark.parametrize("bad", [1, 0, -3, 2.5, True, "10"])
def test_check_window_rejects_invalid(bad):
    with pytest.raises(ValueError):
        _check_window(bad)


def test_check_window_accepts_valid():
    _check_window(2)
    _check_window(14)


def test_rsi_invalid_method(prices):
    with pytest.raises(ValueError):
        add_rsi(prices, method="outro")


def test_rsi_invalid_flat_series(prices):
    with pytest.raises(ValueError):
        add_rsi(prices, flat_series="outro")


def test_bollinger_invalid_ddof(prices):
    with pytest.raises(ValueError):
        add_bollinger_bands(prices, ddof=2)


def test_bollinger_ddof_zero_is_narrower(prices):
    d1 = add_bollinger_bands(prices, ddof=1)
    d0 = add_bollinger_bands(prices, ddof=0)
    w1 = (d1["BB_Upper"] - d1["BB_Lower"]).dropna()
    w0 = (d0["BB_Upper"] - d0["BB_Lower"]).dropna()
    assert (w0 < w1).all()


def test_invalid_windows_in_other_indicators(prices):
    with pytest.raises(ValueError):
        add_moving_averages(prices, short_window=1, long_window=5)
    with pytest.raises(ValueError):
        add_exponential_moving_averages(prices, short_window=3, long_window=1)
    with pytest.raises(ValueError):
        add_macd(prices, short_span=12, long_span=26, signal_span=1)


def test_mask_warmup_masks_and_noop(prices):
    masked = mask_warmup(prices, ["Value"], 5)
    assert masked["Value"].iloc[:5].isna().all()
    assert masked["Value"].iloc[5:].notna().all()
    assert mask_warmup(prices, ["Value"], 0)["Value"].notna().all()
    assert prices["Value"].notna().all()  # original intacto