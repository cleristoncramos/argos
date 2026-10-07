import numpy as np
import pandas as pd
import pytest

from core.comparison import (
    build_base_100_table,
    build_price_table,
    calculate_correlation_matrix,
    calculate_returns_table,
    create_comparison_summary,
    normalize_to_base_100,
)


def make_asset(values, start="2024-01-31"):
    dates = pd.date_range(start, periods=len(values), freq="ME")
    return pd.DataFrame({"Date": dates, "Value": values})


# ---------- normalize_to_base_100 ----------

def test_base_100_requires_value_column():
    with pytest.raises(ValueError):
        normalize_to_base_100(pd.DataFrame({"Other": [1.0]}))


def test_base_100_requires_valid_values():
    with pytest.raises(ValueError):
        normalize_to_base_100(pd.DataFrame({"Value": [np.nan, np.nan]}))


@pytest.mark.parametrize("first", [0.0, -5.0])
def test_base_100_requires_positive_first_value(first):
    with pytest.raises(ValueError):
        normalize_to_base_100(pd.DataFrame({"Value": [first, 10.0]}))


def test_base_100_uses_first_valid_value_as_base():
    result = normalize_to_base_100(pd.DataFrame({"Value": [np.nan, 50.0, 100.0]}))

    assert result["Base_100"].iloc[1] == pytest.approx(100.0)
    assert result["Base_100"].iloc[2] == pytest.approx(200.0)


# ---------- tabelas ----------

def test_price_table_skips_empty_and_incomplete_assets():
    assets = {
        "VAZIO": pd.DataFrame(),
        "SEM_VALOR": pd.DataFrame({"Date": [pd.Timestamp("2024-01-31")]}),
        "A": make_asset([1.0, 2.0]),
    }

    table = build_price_table(assets)

    assert list(table.columns) == ["Date", "A"]
    assert len(table) == 2


def test_price_table_is_empty_when_nothing_usable():
    assert build_price_table({"VAZIO": pd.DataFrame()}).empty
    assert build_price_table({}).empty


def test_price_table_outer_join_keeps_all_dates_sorted():
    assets = {
        "A": make_asset([1.0, 2.0], start="2024-01-31"),
        "B": make_asset([5.0, 6.0], start="2024-02-29"),
    }

    table = build_price_table(assets)

    assert len(table) == 3
    assert table["Date"].is_monotonic_increasing
    assert np.isnan(table.loc[0, "B"])


def test_base_100_table_skips_empty_and_handles_no_frames():
    assert build_base_100_table({"VAZIO": pd.DataFrame()}).empty

    table = build_base_100_table(
        {"VAZIO": pd.DataFrame(), "A": make_asset([10.0, 20.0])}
    )

    assert table["A"].tolist() == pytest.approx([100.0, 200.0])


# ---------- retornos e correlação ----------

def test_returns_table_for_empty_input_is_empty():
    assert calculate_returns_table(pd.DataFrame()).empty


def test_returns_table_computes_simple_returns():
    prices = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-31", periods=3, freq="ME"),
            "A": [100.0, 110.0, 99.0],
        }
    )

    returns = calculate_returns_table(prices)

    assert returns["A"].iloc[1] == pytest.approx(0.10)
    assert returns["A"].iloc[2] == pytest.approx(-0.10)


def test_correlation_matrix_edge_cases():
    assert calculate_correlation_matrix(pd.DataFrame()).empty
    assert calculate_correlation_matrix(
        pd.DataFrame({"Date": pd.date_range("2024-01-31", periods=2, freq="ME")})
    ).empty


def test_correlation_matrix_perfect_positive_and_negative():
    returns = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-31", periods=4, freq="ME"),
            "A": [0.01, 0.02, 0.03, 0.04],
            "B": [0.02, 0.04, 0.06, 0.08],
            "C": [-0.01, -0.02, -0.03, -0.04],
        }
    )

    corr = calculate_correlation_matrix(returns)

    assert corr.loc["A", "B"] == pytest.approx(1.0)
    assert corr.loc["A", "C"] == pytest.approx(-1.0)


# ---------- resumo ----------

def test_summary_skips_unusable_assets_and_leaves_mean_empty_without_returns():
    good = make_asset([100.0, 150.0])
    good["Simple_Return"] = [np.nan, 0.5]

    no_returns = make_asset([10.0, 20.0])

    assets = {
        "VAZIO": pd.DataFrame(),
        "SEM_VALUE": pd.DataFrame({"Date": [pd.Timestamp("2024-01-31")]}),
        "SO_NAN": pd.DataFrame({"Value": [np.nan, np.nan]}),
        "BOM": good,
        "SEM_RETORNO": no_returns,
    }

    summary = create_comparison_summary(assets).set_index("Ativo")

    assert list(summary.index) == ["BOM", "SEM_RETORNO"]
    assert summary.loc["BOM", "Retorno total"] == pytest.approx(0.5)
    assert summary.loc["BOM", "Retorno médio"] == pytest.approx(0.5)
    assert pd.isna(summary.loc["SEM_RETORNO", "Retorno médio"])
    assert summary.loc["BOM", "Observações"] == 2


def test_summary_mean_is_empty_when_return_column_has_no_values():
    asset = make_asset([10.0, 20.0])
    asset["Simple_Return"] = np.nan

    summary = create_comparison_summary({"A": asset})

    assert pd.isna(summary.loc[0, "Retorno médio"])