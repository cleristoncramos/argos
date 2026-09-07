import numpy as np
import pandas as pd
import pytest

from core.risk_metrics import (
    annual_to_periodic_rate,
    build_risk_summary,
    calculate_drawdown,
    calculate_positive_percentage,
    calculate_sharpe_ratio,
    calculate_volatility,
    get_max_drawdown,
)


def create_drawdown_dataframe() -> pd.DataFrame:
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


def test_annual_to_periodic_rate_converts_effective_rate():
    result = annual_to_periodic_rate(
        annual_rate=0.12,
        annualization_factor=12,
    )

    expected = (1.12 ** (1 / 12)) - 1

    assert result == pytest.approx(expected)


@pytest.mark.parametrize(
    ("annual_rate", "annualization_factor", "message"),
    [
        (0.10, 0, "fator de anualização"),
        (0.10, -12, "fator de anualização"),
        (-1.0, 12, "taxa anual"),
        (-1.10, 12, "taxa anual"),
    ],
)
def test_annual_to_periodic_rate_rejects_invalid_inputs(
    annual_rate: float,
    annualization_factor: float,
    message: str,
):
    with pytest.raises(
        ValueError,
        match=message,
    ):
        annual_to_periodic_rate(
            annual_rate=annual_rate,
            annualization_factor=annualization_factor,
        )


def test_calculate_sharpe_ratio_matches_expected_formula():
    returns = pd.Series(
        [
            0.01,
            0.02,
            -0.01,
            0.03,
        ]
    )

    annualization_factor = 12.0
    annual_risk_free_rate = 0.12

    periodic_risk_free_rate = annual_to_periodic_rate(
        annual_risk_free_rate,
        annualization_factor,
    )

    excess_returns = returns - periodic_risk_free_rate

    expected = (
        excess_returns.mean()
        / excess_returns.std(ddof=1)
        * np.sqrt(annualization_factor)
    )

    result = calculate_sharpe_ratio(
        returns=returns,
        annual_risk_free_rate=annual_risk_free_rate,
        annualization_factor=annualization_factor,
    )

    assert result == pytest.approx(expected)


def test_calculate_sharpe_ratio_returns_nan_for_insufficient_data():
    result = calculate_sharpe_ratio(
        returns=pd.Series([0.02]),
    )

    assert np.isnan(result)


def test_calculate_sharpe_ratio_returns_nan_for_constant_returns():
    result = calculate_sharpe_ratio(
        returns=pd.Series(
            [
                0.01,
                0.01,
                0.01,
            ]
        ),
    )

    assert np.isnan(result)


def test_calculate_sharpe_ratio_ignores_invalid_return_values():
    returns = pd.Series(
        [
            0.01,
            "invalido",
            np.nan,
            0.03,
            -0.01,
        ]
    )

    result = calculate_sharpe_ratio(
        returns=returns,
        annual_risk_free_rate=0.0,
        annualization_factor=12.0,
    )

    expected_returns = pd.Series(
        [
            0.01,
            0.03,
            -0.01,
        ]
    )

    expected = (
        expected_returns.mean()
        / expected_returns.std(ddof=1)
        * np.sqrt(12.0)
    )

    assert result == pytest.approx(expected)


def test_calculate_volatility_annualizes_returns():
    returns = pd.Series(
        [
            0.01,
            0.03,
            -0.01,
            0.02,
        ]
    )

    result = calculate_volatility(
        returns=returns,
        annualization_factor=12.0,
    )

    expected = returns.std(ddof=1) * np.sqrt(12.0)

    assert result == pytest.approx(expected)


def test_calculate_volatility_returns_zero_for_empty_or_constant_series():
    empty_result = calculate_volatility(
        returns=pd.Series(dtype="float64"),
    )

    constant_result = calculate_volatility(
        returns=pd.Series(
            [
                0.01,
                0.01,
                0.01,
            ]
        ),
    )

    assert empty_result == pytest.approx(0.0)
    assert constant_result == pytest.approx(0.0)


def test_build_risk_summary_returns_expected_metrics():
    df = pd.DataFrame(
        {
            "Value": [
                100.0,
                110.0,
                99.0,
                121.0,
            ]
        }
    )

    result = build_risk_summary(
        df=df,
        value_col="Value",
        annualization_factor=12.0,
        annual_risk_free_rate=0.0,
    )

    expected_returns = pd.Series(
        [
            0.10,
            -0.10,
            121 / 99 - 1,
        ]
    )

    assert set(result) == {
        "Retorno total",
        "Retorno médio",
        "Volatilidade",
        "Drawdown máximo",
        "Percentual positivo",
        "Sharpe",
    }

    assert result["Retorno total"] == pytest.approx(0.21)
    assert result["Retorno médio"] == pytest.approx(
        expected_returns.mean()
    )
    assert result["Volatilidade"] == pytest.approx(
        expected_returns.std(ddof=1) * np.sqrt(12.0)
    )
    assert result["Drawdown máximo"] == pytest.approx(-0.10)
    assert result["Percentual positivo"] == pytest.approx(2 / 3)

    expected_sharpe = (
        expected_returns.mean()
        / expected_returns.std(ddof=1)
        * np.sqrt(12.0)
    )

    assert result["Sharpe"] == pytest.approx(expected_sharpe)


def test_build_risk_summary_changes_sharpe_with_risk_free_rate():
    df = pd.DataFrame(
        {
            "Value": [
                100.0,
                103.0,
                106.0,
                109.0,
                112.0,
            ]
        }
    )

    summary_zero_rate = build_risk_summary(
        df=df,
        annualization_factor=12.0,
        annual_risk_free_rate=0.0,
    )

    summary_positive_rate = build_risk_summary(
        df=df,
        annualization_factor=12.0,
        annual_risk_free_rate=0.12,
    )

    assert summary_positive_rate["Sharpe"] < summary_zero_rate["Sharpe"]


@pytest.mark.parametrize(
    ("df", "value_col", "message"),
    [
        (
            pd.DataFrame(),
            "Value",
            "não existe no DataFrame",
        ),
        (
            pd.DataFrame(
                {
                    "Price": [
                        100.0,
                        110.0,
                    ]
                }
            ),
            "Value",
            "não existe no DataFrame",
        ),
        (
            pd.DataFrame(
                {
                    "Value": [
                        np.nan,
                        None,
                    ]
                }
            ),
            "Value",
            "não contém valores válidos",
        ),
        (
            pd.DataFrame(
                {
                    "Value": [
                        100.0,
                        0.0,
                    ]
                }
            ),
            "Value",
            "valores maiores que zero",
        ),
        (
            pd.DataFrame(
                {
                    "Value": [
                        100.0,
                        -20.0,
                    ]
                }
            ),
            "Value",
            "valores maiores que zero",
        ),
    ],
)
def test_build_risk_summary_rejects_invalid_data(
    df: pd.DataFrame,
    value_col: str,
    message: str,
):
    with pytest.raises(
        ValueError,
        match=message,
    ):
        build_risk_summary(
            df=df,
            value_col=value_col,
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


def test_calculate_drawdown_returns_empty_dataframe_with_columns():
    df = pd.DataFrame(
        {
            "Value": pd.Series(dtype="float64"),
        }
    )

    result = calculate_drawdown(
        df=df,
        value_col="Value",
    )

    assert result.empty
    assert "Running_Peak" in result.columns
    assert "Drawdown" in result.columns
    assert result["Running_Peak"].dtype == "float64"
    assert result["Drawdown"].dtype == "float64"


def test_calculate_drawdown_rejects_missing_or_invalid_values():
    missing_column_df = pd.DataFrame(
        {
            "Price": [
                100.0,
                120.0,
            ]
        }
    )

    non_numeric_df = pd.DataFrame(
        {
            "Value": [
                100.0,
                "invalido",
            ]
        }
    )

    missing_value_df = pd.DataFrame(
        {
            "Value": [
                100.0,
                np.nan,
            ]
        }
    )

    with pytest.raises(
        ValueError,
        match="não existe no DataFrame",
    ):
        calculate_drawdown(
            missing_column_df,
            "Value",
        )

    with pytest.raises(
        ValueError,
        match="não numéricos ou ausentes",
    ):
        calculate_drawdown(
            non_numeric_df,
            "Value",
        )

    with pytest.raises(
        ValueError,
        match="não numéricos ou ausentes",
    ):
        calculate_drawdown(
            missing_value_df,
            "Value",
        )


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


def test_get_max_drawdown_returns_worst_decline():
    df = create_drawdown_dataframe()

    result = calculate_drawdown(df, "Value")

    max_drawdown = get_max_drawdown(result)

    assert max_drawdown == pytest.approx(-0.25)


def test_get_max_drawdown_rejects_missing_column():
    with pytest.raises(
        ValueError,
        match="não existe no DataFrame",
    ):
        get_max_drawdown(
            pd.DataFrame(
                {
                    "Value": [
                        100.0,
                    ]
                }
            )
        )


def test_get_max_drawdown_returns_none_for_empty_or_missing_values():
    empty_df = pd.DataFrame(
        {
            "Drawdown": pd.Series(dtype="float64"),
        }
    )

    nan_df = pd.DataFrame(
        {
            "Drawdown": [
                np.nan,
                np.nan,
            ]
        }
    )

    assert get_max_drawdown(empty_df) is None
    assert get_max_drawdown(nan_df) is None


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


def test_calculate_positive_percentage_returns_decimal():
    returns = pd.Series(
        [
            -0.10,
            0.05,
            0.03,
            -0.02,
            0.01,
        ]
    )

    result = calculate_positive_percentage(returns)

    assert result == pytest.approx(0.60)


def test_calculate_positive_percentage_returns_zero_for_empty_series():
    returns = pd.Series(dtype="float64")

    result = calculate_positive_percentage(returns)

    assert result == pytest.approx(0.0)