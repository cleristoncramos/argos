import numpy as np
import pandas as pd
import pytest

from core.features import BASE_FEATURES, build_feature_table
from core.indicators import (
    add_bollinger_bands, add_exponential_moving_averages,
    add_macd, add_moving_averages, add_rsi,
)
from core.indicators_extra import add_atr, add_rolling_volatility


def _with_indicators(n=300, seed=7):
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    df = pd.DataFrame({
        "Date": pd.date_range("2022-01-01", periods=n, freq="D"),
        "High": close + rng.uniform(0.1, 1.5, n),
        "Low": close - rng.uniform(0.1, 1.5, n),
        "Close": close,
        "Value": close,
    })
    df = add_moving_averages(df, short_window=20, long_window=50)
    df = add_exponential_moving_averages(df, short_window=12, long_window=26)
    df = add_bollinger_bands(df, window=20, num_std=2.0)
    df = add_rsi(df, window=14)
    df = add_macd(df, short_span=12, long_span=26, signal_span=9)
    df = add_atr(df, window=14)
    df = add_rolling_volatility(df, window=20)
    return df


def test_feature_table_has_base_and_lagged_columns():
    out = build_feature_table(_with_indicators())
    for name in BASE_FEATURES:
        assert name in out.columns
        for k in (1, 2, 3):
            assert f"{name}_lag{k}" in out.columns


def test_lag_is_shifted_value():
    out = build_feature_table(_with_indicators())
    pd.testing.assert_series_equal(
        out["rsi_lag2"], out["rsi"].shift(2), check_names=False
    )


def test_warmup_masks_recursive_features():
    out = build_feature_table(_with_indicators())
    assert out["ema_spread"].iloc[:78].isna().all()
    assert out["ema_spread"].iloc[78:].notna().all()


def test_missing_columns_raise():
    with pytest.raises(ValueError):
        build_feature_table(pd.DataFrame({"Value": [1.0, 2.0]}))


def test_no_target_columns():
    out = build_feature_table(_with_indicators())
    assert not any("target" in c or "future" in c for c in out.columns)


def test_features_have_no_lookahead():
    full = _with_indicators()
    cut = 200
    f_full = build_feature_table(full)
    f_trunc = build_feature_table(_with_indicators().iloc[:cut].copy())
    cols = [c for c in f_full.columns if c != "Date"]
    np.testing.assert_allclose(
        f_full[cols].iloc[:cut].to_numpy(dtype=float),
        f_trunc[cols].to_numpy(dtype=float),
        rtol=1e-9, equal_nan=True,
    )