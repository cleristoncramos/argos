import pandas as pd
import pytest

from core.data_processor import (
    aggregate_by_frequency,
    prepare_dataframe,
    select_primary_variable,
)


def make_daily():
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(
                ["2024-01-03", "2024-01-02", "2024-01-31", "2024-02-01"]
            ),
            "Open": [11.0, 10.0, 15.0, 16.0],
            "High": [12.0, 13.0, 18.0, 17.0],
            "Low": [10.0, 9.0, 14.0, 15.0],
            "Close": [11.5, 12.0, 17.0, 16.5],
            "Volume": [100, 200, 300, 400],
            "Extra": ["a", "b", "c", "d"],
        }
    )


# ---------- prepare_dataframe ----------

@pytest.mark.parametrize("df", [None, pd.DataFrame()])
def test_prepare_returns_empty_for_missing_data(df):
    assert prepare_dataframe(df).empty


def test_prepare_requires_date_column():
    with pytest.raises(ValueError):
        prepare_dataframe(pd.DataFrame({"Close": [1.0]}))


def test_prepare_sorts_drops_invalid_dates_and_keeps_ohlc_only():
    df = make_daily()
    df.loc[0, "Date"] = pd.NaT

    result = prepare_dataframe(df)

    assert len(result) == 3
    assert result["Date"].is_monotonic_increasing
    assert "Extra" not in result.columns
    assert {"Year", "Month", "YearMonth"}.issubset(result.columns)
    assert result["YearMonth"].iloc[-1] == "2024-02"


# ---------- aggregate_by_frequency ----------

@pytest.mark.parametrize("df", [None, pd.DataFrame()])
def test_aggregate_returns_empty_for_missing_data(df):
    assert aggregate_by_frequency(df, "Mensal").empty


def test_aggregate_requires_date_column():
    with pytest.raises(ValueError):
        aggregate_by_frequency(pd.DataFrame({"Close": [1.0]}), "Mensal")


def test_aggregate_daily_keeps_every_row_sorted():
    result = aggregate_by_frequency(make_daily(), "Diário")

    assert len(result) == 4
    assert result["Date"].is_monotonic_increasing
    assert {"Year", "Month", "YearMonth"}.issubset(result.columns)


def test_aggregate_monthly_applies_ohlcv_rules():
    result = aggregate_by_frequency(make_daily(), "Mensal")

    january = result.iloc[0]

    assert len(result) == 2
    assert january["Open"] == 10.0       # primeiro do mês
    assert january["High"] == 18.0       # maior máxima
    assert january["Low"] == 9.0         # menor mínima
    assert january["Close"] == 17.0      # último fechamento
    assert january["Volume"] == 600      # soma
    assert january["Date"] == pd.Timestamp("2024-01-31")


def test_aggregate_weekly_groups_by_week():
    result = aggregate_by_frequency(make_daily(), "Semanal")

    # 02 e 03/jan na mesma semana; 31/jan e 01/fev na semana seguinte
    # (29/jan a 04/fev), mesmo atravessando a virada do mês
    assert len(result) == 2
    assert result.iloc[0]["Volume"] == 300
    assert result.iloc[1]["Volume"] == 700
    assert result.iloc[1]["Close"] == 16.5


def test_aggregate_rejects_unsupported_frequency():
    with pytest.raises(ValueError):
        aggregate_by_frequency(make_daily(), "Anual")


# ---------- select_primary_variable ----------

@pytest.mark.parametrize("df", [None, pd.DataFrame()])
def test_select_primary_returns_empty_for_missing_data(df):
    assert select_primary_variable(df).empty


def test_select_primary_requires_columns():
    with pytest.raises(ValueError):
        select_primary_variable(pd.DataFrame({"Date": [1]}))

    with pytest.raises(ValueError):
        select_primary_variable(pd.DataFrame({"Close": [1.0]}))


def test_select_primary_copies_close_to_value_by_default():
    result = select_primary_variable(prepare_dataframe(make_daily()))

    assert result["Value"].tolist() == result["Close"].tolist()
    assert result["Date"].is_monotonic_increasing


def test_select_primary_accepts_other_variable_and_drops_bad_dates():
    df = prepare_dataframe(make_daily())
    df.loc[0, "Date"] = pd.NaT

    result = select_primary_variable(df, primary_var="Open")

    assert len(result) == 3
    assert result["Value"].tolist() == result["Open"].tolist()