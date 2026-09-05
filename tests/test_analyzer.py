import numpy as np
import pandas as pd
import pytest

from core.analyzer import (
    calculate_percentage_change,
    calculate_statistics,
    calculate_returns,
    calculate_cumulative_return,
)


def create_sample_dataframe():
    """
    Cria dados simples, conhecidos e independentes de internet.

    Série de preços:
    100 -> 110 -> 121

    Retornos esperados:
    NaN -> 10% -> 10%

    Retorno acumulado esperado:
    21%
    """
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                ]
            ),
            "Value": [100.0, 110.0, 121.0],
            "Year": [2024, 2024, 2024],
            "Month": [1, 1, 1],
            "YearMonth": [
                "2024-01",
                "2024-01",
                "2024-01",
            ],
        }
    )


def test_calculate_percentage_change():
    df = create_sample_dataframe()

    result = calculate_percentage_change(df, "Value")

    assert pd.isna(result.loc[0, "Pct_Change"])
    assert result.loc[1, "Pct_Change"] == pytest.approx(10.0)
    assert result.loc[2, "Pct_Change"] == pytest.approx(10.0)


def test_calculate_statistics():
    df = create_sample_dataframe()

    stats = calculate_statistics(df, "Value")

    assert stats["count"] == 3
    assert stats["first_value"] == 100.0
    assert stats["last_value"] == 121.0
    assert stats["min"] == 100.0
    assert stats["max"] == 121.0
    assert stats["mean"] == pytest.approx(110.3333333333)
    assert stats["total_return"] == pytest.approx(21.0)


def test_calculate_returns():
    df = create_sample_dataframe()

    result = calculate_returns(df, "Value")

    assert "Simple_Return" in result.columns
    assert "Log_Return" in result.columns

    assert pd.isna(result.loc[0, "Simple_Return"])
    assert result.loc[1, "Simple_Return"] == pytest.approx(0.10)
    assert result.loc[2, "Simple_Return"] == pytest.approx(0.10)

    expected_log_return = np.log(1.10)

    assert result.loc[1, "Log_Return"] == pytest.approx(
        expected_log_return
    )
    assert result.loc[2, "Log_Return"] == pytest.approx(
        expected_log_return
    )


def test_calculate_cumulative_return():
    df = create_sample_dataframe()

    df_returns = calculate_returns(df, "Value")

    result = calculate_cumulative_return(
        df_returns,
        "Simple_Return"
    )

    assert "Cumulative_Return" in result.columns
    assert result.loc[0, "Cumulative_Return"] == pytest.approx(0.0)
    assert result.loc[1, "Cumulative_Return"] == pytest.approx(0.10)
    assert result.loc[2, "Cumulative_Return"] == pytest.approx(0.21)


def test_cumulative_return_respects_compounding():
    """
    Confirma que dois retornos consecutivos de 10% produzem
    retorno acumulado de 21%, e não 20%.
    """
    df = pd.DataFrame(
        {
            "Value": [100.0, 110.0, 121.0],
            "Simple_Return": [np.nan, 0.10, 0.10],
        }
    )

    result = calculate_cumulative_return(
        df,
        "Simple_Return"
    )

    assert result.loc[2, "Cumulative_Return"] == pytest.approx(0.21)