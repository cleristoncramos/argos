"""Frequências semestral e anual: agregação, fim do período e anualização."""

import numpy as np
import pandas as pd
import pytest

from core.comparison import build_price_table, calculate_returns_table
from core.config import ANNUALIZATION_FACTORS, LONG_FREQUENCIES, config
from core.data_processor import aggregate_by_frequency, period_end, select_primary_variable
from core.risk_metrics import build_risk_summary, calculate_volatility


def daily(start="2023-01-02", end="2024-10-15"):
    dates = pd.bdate_range(start, end)
    values = np.arange(1, len(dates) + 1, dtype=float)
    return pd.DataFrame(
        {
            "Date": dates,
            "Open": values,
            "High": values + 0.5,
            "Low": values - 0.5,
            "Close": values,
            "Volume": 10,
        }
    )


def test_new_frequencies_are_offered_with_their_factors():
    assert config.FREQUENCIES[-2:] == ("Semestral", "Anual")
    assert ANNUALIZATION_FACTORS["Semestral"] == 2
    assert ANNUALIZATION_FACTORS["Anual"] == 1
    assert LONG_FREQUENCIES == ("Semestral", "Anual")


@pytest.mark.parametrize(
    "day, semester_end, year_end",
    [
        ("2024-01-01", "2024-06-30", "2024-12-31"),
        ("2024-06-30", "2024-06-30", "2024-12-31"),
        ("2024-07-01", "2024-12-31", "2024-12-31"),
        ("2024-12-31", "2024-12-31", "2024-12-31"),
    ],
)
def test_period_end_splits_semesters_in_june_and_december(day, semester_end, year_end):
    dates = pd.Series(pd.to_datetime([day]))
    assert period_end(dates, "Semestral").iloc[0] == pd.Timestamp(semester_end)
    assert period_end(dates, "Anual").iloc[0] == pd.Timestamp(year_end)


def test_period_end_rejects_unknown_frequency():
    with pytest.raises(ValueError):
        period_end(pd.Series(pd.to_datetime(["2024-01-01"])), "Trimestral")


def test_semester_aggregation_follows_ohlcv_rules():
    df = daily()
    result = aggregate_by_frequency(df, "Semestral")

    assert list(result["PeriodEnd"]) == list(
        pd.to_datetime(["2023-06-30", "2023-12-31", "2024-06-30", "2024-12-31"])
    )
    first = df[df["Date"] <= "2023-06-30"]
    row = result.iloc[0]
    assert row["Open"] == first["Open"].iloc[0]
    assert row["Close"] == first["Close"].iloc[-1]
    assert row["High"] == first["High"].max()
    assert row["Low"] == first["Low"].min()
    assert row["Volume"] == first["Volume"].sum()
    # Date é o último pregão do semestre, não o fim do calendário
    assert row["Date"] == pd.Timestamp("2023-06-30")
    assert result.iloc[1]["Date"] == pd.Timestamp("2023-12-29")


def test_last_period_in_progress_closes_on_last_available_day():
    result = aggregate_by_frequency(daily(end="2024-10-15"), "Anual")

    assert len(result) == 2
    assert result.iloc[-1]["Date"] == pd.Timestamp("2024-10-15")
    assert result.iloc[-1]["PeriodEnd"] == pd.Timestamp("2024-12-31")


def test_annual_risk_metrics_use_factor_one():
    df = select_primary_variable(
        aggregate_by_frequency(daily("2015-01-02", "2024-12-31"), "Anual"), "Close"
    )
    returns = df["Value"].pct_change().dropna()

    summary = build_risk_summary(df, annualization_factor=ANNUALIZATION_FACTORS["Anual"])

    assert len(df) == 10
    assert summary["Volatilidade"] == pytest.approx(calculate_volatility(returns, 1))
    assert summary["Volatilidade"] == pytest.approx(returns.std(ddof=1))


def test_long_frequencies_align_assets_by_period_end():
    # Um ativo negocia nos fins de semana e o outro não: o último pregão difere,
    # mas o fim do semestre é o mesmo, e a tabela fica alinhada.
    crypto = daily("2023-01-01", "2023-12-31")
    crypto["Date"] = pd.date_range("2023-01-01", periods=len(crypto), freq="D")
    stock = daily("2023-01-02", "2023-12-31")

    frames = {
        name: select_primary_variable(aggregate_by_frequency(df, "Semestral"), "Close")
        for name, df in {"BTC": crypto, "AAPL": stock}.items()
    }
    table = build_price_table(frames, value_col="Value", align_col="PeriodEnd")

    assert len(table) == 2
    assert table[["BTC", "AAPL"]].notna().all().all()
    assert calculate_returns_table(table)[["BTC", "AAPL"]].iloc[1].notna().all()


# ---------- último período em andamento ----------

def _availability(end, frequency):
    from datetime import date

    from core.data_availability import assess_availability

    dates = pd.bdate_range("2015-01-02", end)
    return assess_availability(
        dates, date(2015, 1, 1), pd.Timestamp(end).date(), 20, frequency=frequency
    )


def test_partial_year_is_flagged_with_its_end():
    from datetime import date

    from core.data_availability import availability_messages

    a = _availability("2024-10-15", "Anual")
    assert a.partial_period_end == date(2024, 12, 31)
    texts = [text for level, text in availability_messages(a) if level == "info"]
    assert any("último ano ainda está em andamento" in t and "31/12/2024" in t for t in texts)


def test_partial_semester_message_names_the_semester():
    from core.data_availability import availability_messages

    a = _availability("2024-03-28", "Semestral")
    assert any("último semestre" in text for _, text in availability_messages(a))


def test_complete_period_and_short_frequencies_are_not_flagged():
    assert _availability("2024-12-31", "Anual").partial_period_end is None
    assert _availability("2024-10-15", "Mensal").partial_period_end is None
    assert _availability("2024-10-15", None).partial_period_end is None
