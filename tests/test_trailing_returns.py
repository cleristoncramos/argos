"""Variação por janelas até a última observação (core/trailing_returns.py)."""

import pandas as pd
import pytest

from core.trailing_returns import (
    COLUMNS,
    TRAILING_WINDOWS,
    TrailingWindow,
    base_description,
    calendar_years,
    trailing_returns,
    window_target,
)


def daily(start, end, value=lambda i: 100.0 + i):
    dates = pd.bdate_range(start, end)
    return pd.DataFrame({"Date": dates, "Close": [value(i) for i in range(len(dates))]})


def row(table, label):
    return table.set_index("Janela").loc[label]


def test_calendar_years():
    assert calendar_years(pd.Timestamp("2025-10-23"), pd.Timestamp("2026-10-23")) == 1
    assert calendar_years(pd.Timestamp("2023-10-20"), pd.Timestamp("2026-10-23")) == pytest.approx(3 + 3 / 365.25)
    assert calendar_years(pd.Timestamp("2021-11-01"), pd.Timestamp("2026-10-23")) == pytest.approx(4 + 356 / 365.25)
    assert calendar_years(pd.Timestamp("2024-02-29"), pd.Timestamp("2025-02-28")) == 1  # 29/02 + 1 ano = 28/02


def test_windows_and_targets():
    assert [w.label for w in TRAILING_WINDOWS] == [
        "1 mês", "3 meses", "6 meses", "No ano", "1 ano", "2 anos", "3 anos", "5 anos", "10 anos",
    ]
    assert not TrailingWindow("6 meses", months=6).is_long and TrailingWindow("1 ano", years=1).is_long
    end = pd.Timestamp("2026-10-23 16:00")
    assert window_target(end, TrailingWindow("1 mês", months=1)) == pd.Timestamp("2026-09-23")
    assert window_target(end, TrailingWindow("5 anos", years=5)) == pd.Timestamp("2021-10-23")
    assert window_target(end, TrailingWindow("No ano", year_to_date=True)) == pd.Timestamp("2025-12-31")
    assert window_target(pd.Timestamp("2024-02-29"), TrailingWindow("1 ano", years=1)) == pd.Timestamp("2023-02-28")


def test_values_dates_and_annual_rate():
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2023-10-20", "2024-10-23", "2025-10-23", "2026-09-23", "2026-10-23"]),
        "Close": [50.0, 80.0, 100.0, 110.0, 121.0],
    })
    table = trailing_returns(df)
    assert list(table.columns) == COLUMNS

    month = row(table, "1 mês")
    assert month["Disponível"] and not month["Ajustada"]
    assert month["Data inicial"] == pd.Timestamp("2026-09-23")
    assert month["Variação"] == pytest.approx(0.10) and pd.isna(month["Taxa anual"])

    one_year = row(table, "1 ano")
    assert one_year["Valor inicial"] == 100.0 and one_year["Variação"] == pytest.approx(0.21)
    assert one_year["Taxa anual"] == pytest.approx(0.21)  # exatamente 1 ano

    # A data-alvo cai entre observações: usa a última observação antes dela.
    three = row(table, "3 anos")
    assert three["Data inicial"] == pd.Timestamp("2023-10-20") and three["Valor inicial"] == 50.0
    assert three["Taxa anual"] == pytest.approx((121 / 50) ** (1 / (3 + 3 / 365.25)) - 1)

    ytd = row(table, "No ano")
    assert ytd["Data inicial"] == pd.Timestamp("2025-10-23") and pd.isna(ytd["Taxa anual"])


def test_unavailable_and_adjusted_windows():
    # Série que começa em 01/11/2021, como no atalho "5 anos" da barra lateral.
    table = trailing_returns(daily("2021-11-01", "2026-10-23"))

    five = row(table, "5 anos")
    assert five["Disponível"] and five["Ajustada"]
    assert five["Data inicial"] == pd.Timestamp("2021-11-01")
    assert five["Data-alvo"] == pd.Timestamp("2021-10-23")

    ten = row(table, "10 anos")
    assert not ten["Disponível"] and pd.isna(ten["Variação"]) and pd.isna(ten["Data inicial"])

    # Janelas curtas têm tolerância menor: 10 dias depois da data-alvo não basta.
    short = trailing_returns(daily("2026-10-05", "2026-10-23"))
    assert not row(short, "1 mês")["Disponível"]
    almost = trailing_returns(daily("2026-09-28", "2026-10-23"))
    assert row(almost, "1 mês")["Ajustada"]


def test_cleaning_timezone_and_empty_inputs():
    df = daily("2025-01-01", "2026-01-02")
    df["Date"] = df["Date"].dt.tz_localize("America/Sao_Paulo")
    df.loc[3, "Close"] = -1.0
    df.loc[4, "Close"] = None
    table = trailing_returns(df)
    assert row(table, "1 ano")["Disponível"]
    assert row(table, "1 ano")["Data final"].tzinfo is None

    for bad in (None, pd.DataFrame(), pd.DataFrame({"Date": ["2020-01-01"]}), daily("2026-01-01", "2026-01-01")):
        assert trailing_returns(bad).empty
    assert trailing_returns(daily("2025-01-01", "2026-01-01"), value_col="Value").empty


def test_base_description():
    df = daily("2025-01-06", "2025-02-07")
    assert base_description(df) == (pd.Timestamp("2025-01-06"), pd.Timestamp("2025-02-07"))
    assert base_description(None) is None
    assert base_description(pd.DataFrame({"Date": [None]})) is None
    assert base_description(pd.DataFrame({"X": [1]})) is None
