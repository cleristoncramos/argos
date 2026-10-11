"""Retornos simples não devem preencher lacunas (independe da versão do pandas)."""

import numpy as np
import pandas as pd

from core.analyzer import calculate_percentage_change, calculate_returns
from core.comparison import calculate_returns_table
from core.indicators_extra import add_rolling_volatility
from core.returns_utils import simple_returns


def test_simple_returns_known_values():
    result = simple_returns(pd.Series([100.0, 110.0, 121.0]))

    assert np.isnan(result.iloc[0])
    assert result.iloc[1] == 0.1 or abs(result.iloc[1] - 0.10) < 1e-12
    assert abs(result.iloc[2] - 0.10) < 1e-12


def test_simple_returns_gap_is_not_filled():
    # Com o preenchimento antigo (pad): [NaN, 0.0, 0.21]. Esperado: tudo NaN.
    result = simple_returns(pd.Series([100.0, np.nan, 121.0]))

    assert result.isna().all()


def test_simple_returns_resumes_after_gap():
    result = simple_returns(pd.Series([100.0, np.nan, 121.0, 133.1]))

    assert np.isnan(result.iloc[1])
    assert np.isnan(result.iloc[2])
    assert abs(result.iloc[3] - 0.10) < 1e-12


def test_simple_returns_dataframe_columns_are_independent():
    frame = pd.DataFrame({"A": [100.0, 110.0, 121.0], "B": [50.0, np.nan, 55.0]})

    result = simple_returns(frame)

    assert abs(result["A"].iloc[1] - 0.10) < 1e-12
    assert abs(result["A"].iloc[2] - 0.10) < 1e-12
    assert result["B"].isna().all()


def test_simple_returns_keeps_index_and_does_not_mutate_input():
    index = pd.date_range("2024-01-31", periods=3, freq="ME")
    series = pd.Series([10, 11, 12], index=index)
    before = series.copy()

    result = simple_returns(series)

    assert result.index.equals(index)
    pd.testing.assert_series_equal(series, before)
    assert abs(result.iloc[1] - 0.10) < 1e-12


def test_returns_table_does_not_turn_gap_into_zero_return():
    prices = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]),
            "A": [100.0, 110.0, 121.0, 133.1],
            "B": [50.0, np.nan, 55.0, 60.5],
        }
    )

    result = calculate_returns_table(prices)

    assert abs(result["A"].iloc[3] - 0.10) < 1e-12
    assert np.isnan(result["B"].iloc[1])
    assert np.isnan(result["B"].iloc[2])  # sem retorno 0,0 nem retorno acumulado
    assert abs(result["B"].iloc[3] - 0.10) < 1e-12


def test_analyzer_returns_keep_gap_empty():
    df = pd.DataFrame({"Value": [100.0, np.nan, 121.0, 133.1]})

    simple = calculate_returns(df, value_col="Value")["Simple_Return"]
    pct = calculate_percentage_change(df, value_col="Value")["Pct_Change"]

    assert simple.iloc[1:3].isna().all()
    assert pct.iloc[1:3].isna().all()
    assert abs(simple.iloc[3] - 0.10) < 1e-12
    assert abs(pct.iloc[3] - 10.0) < 1e-9


def test_rolling_volatility_does_not_use_filled_returns():
    close = [100.0, 101.0, np.nan, 103.0, 104.0, 105.0]
    df = pd.DataFrame({"Close": close})

    result = add_rolling_volatility(df, window=2, value_col="Close")

    # Janela de 2 retornos que inclui a lacuna não pode ter valor.
    assert result["VOL_2"].iloc[2:4].isna().all()