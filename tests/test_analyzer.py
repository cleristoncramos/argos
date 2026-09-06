import numpy as np
import pandas as pd
import pytest

from core.analyzer import (
    analyze_seasonality,
    calculate_cumulative_return,
    calculate_percentage_change,
    calculate_returns,
    calculate_statistics,
    create_year_month_matrix,
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
        "Simple_Return",
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
        "Simple_Return",
    )

    assert result.loc[2, "Cumulative_Return"] == pytest.approx(0.21)


def test_analyze_seasonality():
    """
    Verifica a agregação mensal de retorno percentual e valor.

    Mês 1:
    - Pct_Change: 10 e 20
    - Value: 100 e 120
    - Percentual positivo: 100%

    Mês 2:
    - Pct_Change: -5 e 5
    - Value: 200 e 220
    - Percentual positivo: 50%
    """
    df = pd.DataFrame(
        {
            "Month": [1, 1, 2, 2],
            "Value": [100.0, 120.0, 200.0, 220.0],
            "Pct_Change": [10.0, 20.0, -5.0, 5.0],
        }
    )

    result = analyze_seasonality(df)

    assert list(result.index) == [1, 2]

    assert ("Pct_Change", "mean") in result.columns
    assert ("Pct_Change", "median") in result.columns
    assert ("Pct_Change", "std") in result.columns
    assert ("Pct_Change", "count") in result.columns

    assert ("Value", "mean") in result.columns
    assert ("Value", "median") in result.columns
    assert ("Value", "min") in result.columns
    assert ("Value", "max") in result.columns

    assert ("positive_pct", "") in result.columns

    assert result.loc[1, ("Pct_Change", "mean")] == pytest.approx(15.0)
    assert result.loc[1, ("Pct_Change", "median")] == pytest.approx(15.0)
    assert result.loc[1, ("Pct_Change", "count")] == 2

    assert result.loc[2, ("Pct_Change", "mean")] == pytest.approx(0.0)
    assert result.loc[2, ("Pct_Change", "median")] == pytest.approx(0.0)
    assert result.loc[2, ("Pct_Change", "count")] == 2

    assert result.loc[1, ("Value", "mean")] == pytest.approx(110.0)
    assert result.loc[1, ("Value", "min")] == pytest.approx(100.0)
    assert result.loc[1, ("Value", "max")] == pytest.approx(120.0)

    assert result.loc[2, ("Value", "mean")] == pytest.approx(210.0)
    assert result.loc[2, ("Value", "min")] == pytest.approx(200.0)
    assert result.loc[2, ("Value", "max")] == pytest.approx(220.0)

    assert result.loc[1, ("positive_pct", "")] == pytest.approx(100.0)
    assert result.loc[2, ("positive_pct", "")] == pytest.approx(50.0)


def test_create_year_month_matrix():
    """
    Verifica a criação da matriz Ano x Mês usando Pct_Change.
    """
    df = pd.DataFrame(
        {
            "Year": [2023, 2023, 2024, 2024],
            "Month": [1, 2, 1, 2],
            "Pct_Change": [1.0, 2.0, 3.0, 4.0],
        }
    )

    result = create_year_month_matrix(df)

    assert list(result.index) == [2023, 2024]
    assert list(result.columns) == [1, 2]

    assert result.loc[2023, 1] == pytest.approx(1.0)
    assert result.loc[2023, 2] == pytest.approx(2.0)
    assert result.loc[2024, 1] == pytest.approx(3.0)
    assert result.loc[2024, 2] == pytest.approx(4.0)


def test_create_year_month_matrix():
    """
    Verifica a criação da matriz Ano x Mês.

    A implementação converte os meses numéricos em abreviações
    em português: 1 -> Jan e 2 -> Fev.
    """
    df = pd.DataFrame(
        {
            "Year": [2023, 2023, 2024, 2024],
            "Month": [1, 2, 1, 2],
            "Pct_Change": [1.0, 2.0, 3.0, 4.0],
        }
    )

    result = create_year_month_matrix(df)

    assert list(result.index) == [2023, 2024]
    assert list(result.columns) == ["Jan", "Fev"]

    assert result.loc[2023, "Jan"] == pytest.approx(1.0)
    assert result.loc[2023, "Fev"] == pytest.approx(2.0)
    assert result.loc[2024, "Jan"] == pytest.approx(3.0)
    assert result.loc[2024, "Fev"] == pytest.approx(4.0)

def test_create_year_month_matrix_requires_columns():
    """
    Confirma que a matriz exige a coluna Pct_Change.
    """
    df = pd.DataFrame(
        {
            "Year": [2024],
            "Month": [1],
        }
    )

    with pytest.raises(
        ValueError,
        match="Pct_Change",
    ):
        create_year_month_matrix(df)