import pandas as pd
import pytest

from core.risk_metrics import (
    calculate_drawdown,
    get_max_drawdown,
)


def create_drawdown_dataframe():
    """
    Série conhecida para validar drawdown.

    Valores:
    100 -> 120 -> 90 -> 110 -> 130

    Drawdowns esperados:
    0% -> 0% -> -25% -> -8,3333% -> 0%
    """
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-05",
                ]
            ),
            "Value": [
                100.0,
                120.0,
                90.0,
                110.0,
                130.0,
            ],
        }
    )


def test_calculate_drawdown_creates_expected_columns():
    df = create_drawdown_dataframe()

    result = calculate_drawdown(df, "Value")

    assert "Running_Peak" in result.columns
    assert "Drawdown" in result.columns


def test_calculate_drawdown_values_are_correct():
    df = create_drawdown_dataframe()

    result = calculate_drawdown(df, "Value")

    assert result.loc[0, "Running_Peak"] == pytest.approx(100.0)
    assert result.loc[1, "Running_Peak"] == pytest.approx(120.0)
    assert result.loc[2, "Running_Peak"] == pytest.approx(120.0)
    assert result.loc[3, "Running_Peak"] == pytest.approx(120.0)
    assert result.loc[4, "Running_Peak"] == pytest.approx(130.0)

    assert result.loc[0, "Drawdown"] == pytest.approx(0.0)
    assert result.loc[1, "Drawdown"] == pytest.approx(0.0)
    assert result.loc[2, "Drawdown"] == pytest.approx(-0.25)
    assert result.loc[3, "Drawdown"] == pytest.approx(-0.0833333333)
    assert result.loc[4, "Drawdown"] == pytest.approx(0.0)


def test_get_max_drawdown_returns_worst_decline():
    df = create_drawdown_dataframe()

    result = calculate_drawdown(df, "Value")

    max_drawdown = get_max_drawdown(result)

    assert max_drawdown == pytest.approx(-0.25)


def test_increasing_series_has_zero_max_drawdown():
    df = pd.DataFrame(
        {
            "Value": [
                100.0,
                110.0,
                120.0,
                130.0,
            ]
        }
    )

    result = calculate_drawdown(df, "Value")

    assert (result["Drawdown"] == 0.0).all()
    assert get_max_drawdown(result) == pytest.approx(0.0)


def test_drawdown_rejects_zero_or_negative_values():
    df_zero = pd.DataFrame(
        {
            "Value": [
                100.0,
                0.0,
                120.0,
            ]
        }
    )

    df_negative = pd.DataFrame(
        {
            "Value": [
                100.0,
                -50.0,
                120.0,
            ]
        }
    )

    with pytest.raises(
        ValueError,
        match="valores maiores que zero",
    ):
        calculate_drawdown(df_zero, "Value")

    with pytest.raises(
        ValueError,
        match="valores maiores que zero",
    ):
        calculate_drawdown(df_negative, "Value")


def test_drawdown_rejects_missing_column():
    df = pd.DataFrame(
        {
            "Preco": [
                100.0,
                120.0,
            ]
        }
    )

    with pytest.raises(
        ValueError,
        match="não existe no DataFrame",
    ):
        calculate_drawdown(df, "Value")


def test_get_max_drawdown_returns_none_for_empty_dataframe():
    df = pd.DataFrame(
        {
            "Value": pd.Series(dtype="float64"),
        }
    )

    result = calculate_drawdown(df, "Value")

    assert get_max_drawdown(result) is None