import pandas as pd
import pytest

from core.indicators import (
    add_moving_averages,
    add_exponential_moving_averages,
    add_rsi,
    add_macd,
    add_bollinger_bands,
)


def create_indicator_dataframe():
    """
    Cria uma série conhecida para validar os indicadores.
    """
    return pd.DataFrame(
        {
            "Date": pd.date_range(
                start="2024-01-01",
                periods=10,
                freq="D",
            ),
            "Value": [
                10.0,
                11.0,
                12.0,
                13.0,
                14.0,
                15.0,
                16.0,
                17.0,
                18.0,
                19.0,
            ],
        }
    )


def test_add_moving_averages_creates_columns():
    df = create_indicator_dataframe()

    result = add_moving_averages(
        df,
        value_col="Value",
        short_window=3,
        long_window=5,
    )

    assert "SMA_3" in result.columns
    assert "SMA_5" in result.columns


def test_add_moving_averages_calculates_known_values():
    df = create_indicator_dataframe()

    result = add_moving_averages(
        df,
        value_col="Value",
        short_window=3,
        long_window=5,
    )

    assert pd.isna(result.loc[0, "SMA_3"])
    assert pd.isna(result.loc[1, "SMA_3"])

    # Média de 10, 11 e 12
    assert result.loc[2, "SMA_3"] == pytest.approx(11.0)

    # Média de 10, 11, 12, 13 e 14
    assert result.loc[4, "SMA_5"] == pytest.approx(12.0)


def test_add_exponential_moving_averages_creates_columns():
    df = create_indicator_dataframe()

    result = add_exponential_moving_averages(
        df,
        value_col="Value",
        short_window=3,
        long_window=5,
    )

    assert "EMA_3" in result.columns
    assert "EMA_5" in result.columns

    # A EMA começa pelo primeiro valor da série
    assert result.loc[0, "EMA_3"] == pytest.approx(10.0)
    assert result.loc[0, "EMA_5"] == pytest.approx(10.0)


def test_rsi_stays_between_zero_and_one_hundred():
    df = create_indicator_dataframe()

    result = add_rsi(
        df,
        value_col="Value",
        window=3,
    )

    rsi = result["RSI_3"].dropna()

    assert not rsi.empty
    assert rsi.between(0, 100).all()


def test_rsi_is_one_hundred_for_only_gains():
    df = create_indicator_dataframe()

    result = add_rsi(
        df,
        value_col="Value",
        window=3,
    )

    rsi = result["RSI_3"].dropna()

    assert (rsi == 100.0).all()


def test_macd_calculates_histogram_correctly():
    df = create_indicator_dataframe()

    result = add_macd(
        df,
        value_col="Value",
        short_span=3,
        long_span=5,
        signal_span=2,
    )

    expected_histogram = (
        result["MACD"] - result["MACD_Signal"]
    )

    pd.testing.assert_series_equal(
        result["MACD_Histogram"],
        expected_histogram,
        check_names=False,
    )


def test_bollinger_bands_respect_order():
    df = create_indicator_dataframe()

    result = add_bollinger_bands(
        df,
        value_col="Value",
        window=3,
        num_std=2.0,
    )

    valid_rows = result.dropna(
        subset=[
            "BB_Lower",
            "BB_Middle",
            "BB_Upper",
        ]
    )

    assert not valid_rows.empty

    assert (
        valid_rows["BB_Upper"] >= valid_rows["BB_Middle"]
    ).all()

    assert (
        valid_rows["BB_Middle"] >= valid_rows["BB_Lower"]
    ).all()