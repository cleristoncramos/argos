import numpy as np
import pandas as pd
import pytest

from core.analyzer import (
    analyze_seasonality,
    calculate_percentage_change,
    calculate_statistics,
    create_monthly_return_matrix,
    create_year_month_matrix,
)
from core.risk_metrics import calculate_drawdown, get_max_drawdown_date


# ---------- data do pior drawdown ----------

def test_max_drawdown_date_is_the_trough():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "Value": [100.0, 120.0, 90.0],
        }
    )

    drawdown = calculate_drawdown(df)

    assert get_max_drawdown_date(drawdown) == pd.Timestamp("2024-01-03")


def test_max_drawdown_date_ties_return_first_date():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "Drawdown": [0.0, -0.1, -0.1],
        }
    )

    assert get_max_drawdown_date(df) == pd.Timestamp("2024-01-02")


def test_max_drawdown_date_without_values_returns_none():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-01"]),
            "Drawdown": [np.nan],
        }
    )

    assert get_max_drawdown_date(df) is None
    assert get_max_drawdown_date(pd.DataFrame({"Date": [], "Drawdown": []})) is None


def test_max_drawdown_date_requires_columns():
    with pytest.raises(ValueError):
        get_max_drawdown_date(pd.DataFrame({"Date": [1]}))

    with pytest.raises(ValueError):
        get_max_drawdown_date(pd.DataFrame({"Drawdown": [-0.1]}))


# ---------- estatísticas ----------

def test_statistics_total_return_is_nan_when_first_value_is_zero():
    stats = calculate_statistics(pd.DataFrame({"Value": [0.0, 5.0]}))

    assert np.isnan(stats["total_return"])


def test_statistics_total_return_for_empty_series_is_zero():
    stats = calculate_statistics(pd.DataFrame({"Value": []}))

    assert stats["total_return"] == 0
    assert stats["first_value"] is None


def test_statistics_total_return_in_percent():
    stats = calculate_statistics(pd.DataFrame({"Value": [100.0, 150.0]}))

    assert stats["total_return"] == pytest.approx(50.0)


# ---------- sazonalidade ----------

def make_monthly(values):
    dates = pd.date_range("2023-01-31", periods=len(values), freq="ME")
    df = pd.DataFrame({"Date": dates, "Value": values})
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    return calculate_percentage_change(df)


def test_seasonality_positive_pct_ignores_missing_first_change():
    df = make_monthly([100.0, 110.0, 99.0, 120.0])

    result = analyze_seasonality(df)

    # janeiro só tem a primeira linha (sem variação): não conta como 0%
    assert np.isnan(result.loc[1, "positive_pct"])
    assert result.loc[2, "positive_pct"] == pytest.approx(100.0)
    assert result.loc[3, "positive_pct"] == pytest.approx(0.0)
    assert result.loc[4, "positive_pct"] == pytest.approx(100.0)


def test_seasonality_requires_columns():
    with pytest.raises(ValueError):
        analyze_seasonality(pd.DataFrame({"Value": [1.0, 2.0]}))


# ---------- matriz de retorno mensal ----------

def test_monthly_return_matrix_matches_between_daily_and_monthly_data():
    days = pd.bdate_range("2024-01-01", "2024-04-30")
    daily = pd.DataFrame(
        {"Date": days, "Value": np.arange(1, len(days) + 1, dtype=float)}
    )
    monthly = daily.groupby(daily["Date"].dt.to_period("M")).last().reset_index(drop=True)

    from_daily = create_monthly_return_matrix(daily)
    from_monthly = create_monthly_return_matrix(monthly)

    pd.testing.assert_frame_equal(from_daily, from_monthly)
    assert list(from_daily.columns) == ["Jan", "Fev", "Mar", "Abr"]
    assert np.isnan(from_daily.loc[2024, "Jan"])


def test_monthly_return_matrix_value_is_percent_of_month_end_change():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-31", "2024-02-29", "2024-03-29"]),
            "Value": [100.0, 110.0, 99.0],
        }
    )

    matrix = create_monthly_return_matrix(df)

    assert matrix.loc[2024, "Fev"] == pytest.approx(10.0)
    assert matrix.loc[2024, "Mar"] == pytest.approx(-10.0)


def test_monthly_return_matrix_leaves_gaps_empty():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-31", "2024-03-29", "2024-04-30"]),
            "Value": [100.0, 120.0, 132.0],
        }
    )

    matrix = create_monthly_return_matrix(df)

    # fevereiro ausente: março e abril não têm mês anterior válido... março
    # compara com fevereiro (ausente) e fica vazio; abril compara com março
    assert np.isnan(matrix.loc[2024, "Mar"])
    assert matrix.loc[2024, "Abr"] == pytest.approx(10.0)


def test_monthly_return_matrix_edge_cases():
    assert create_monthly_return_matrix(
        pd.DataFrame({"Date": [], "Value": []})
    ).empty

    with pytest.raises(ValueError):
        create_monthly_return_matrix(pd.DataFrame({"Date": [1]}))


def test_year_month_matrix_still_averages_values():
    df = pd.DataFrame(
        {
            "Year": [2024, 2024, 2024],
            "Month": [1, 1, 2],
            "Pct_Change": [2.0, 4.0, 5.0],
        }
    )

    matrix = create_year_month_matrix(df)

    assert matrix.loc[2024, "Jan"] == pytest.approx(3.0)
    assert matrix.loc[2024, "Fev"] == pytest.approx(5.0)