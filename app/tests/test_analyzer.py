import pandas as pd
import pytest

from core.analyzer import (
    calculate_statistics,
    calculate_percentage_change,
    analyze_seasonality,
    create_year_month_matrix,
)


def create_analysis_dataframe():
    """
    Dados previsíveis para validar cálculos sem depender
    de dados externos.
    """
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2020-01-31",
                    "2020-02-29",
                    "2020-03-31",
                    "2021-01-31",
                    "2021-02-28",
                    "2021-03-31",
                ]
            ),
            "Value": [100.0, 110.0, 121.0, 100.0, 90.0, 99.0],
            "Year": [2020, 2020, 2020, 2021, 2021, 2021],
            "Month": [1, 2, 3, 1, 2, 3],
            "YearMonth": [
                "2020-01",
                "2020-02",
                "2020-03",
                "2021-01",
                "2021-02",
                "2021-03",
            ],
        }
    )


def test_calculate_percentage_change():
    df = create_analysis_dataframe()

    result = calculate_percentage_change(df, "Value")

    assert pd.isna(result.loc[0, "Pct_Change"])
    assert result.loc[1, "Pct_Change"] == pytest.approx(10.0)
    assert result.loc[2, "Pct_Change"] == pytest.approx(10.0)
    assert result.loc[3, "Pct_Change"] == pytest.approx(-17.3553719)
    assert result.loc[4, "Pct_Change"] == pytest.approx(-10.0)
    assert result.loc[5, "Pct_Change"] == pytest.approx(10.0)


def test_calculate_statistics():
    df = create_analysis_dataframe()

    stats = calculate_statistics(df, "Value")

    assert stats["count"] == 6
    assert stats["first_value"] == 100.0
    assert stats["last_value"] == 99.0
    assert stats["min"] == 90.0
    assert stats["max"] == 121.0
    assert stats["mean"] == pytest.approx(103.3333333)
    assert stats["total_return"] == pytest.approx(-1.0)


def test_analyze_seasonality():
    df = calculate_percentage_change(create_analysis_dataframe(), "Value")

    result = analyze_seasonality(df, "Value")

    assert not result.empty
    assert 1 in result.index
    assert 2 in result.index
    assert 3 in result.index


def test_create_year_month_matrix():
    df = calculate_percentage_change(create_analysis_dataframe(), "Value")

    result = create_year_month_matrix(df, "Pct_Change")

    assert list(result.index) == [2020, 2021]
    assert "Jan" in result.columns
    assert "Fev" in result.columns
    assert "Mar" in result.columns

    assert pd.isna(result.loc[2020, "Jan"])
    assert result.loc[2020, "Fev"] == pytest.approx(10.0)
    assert result.loc[2020, "Mar"] == pytest.approx(10.0)


def test_create_year_month_matrix_requires_columns():
    invalid_df = pd.DataFrame({"Value": [100, 110]})

    with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
        create_year_month_matrix(invalid_df, "Pct_Change")