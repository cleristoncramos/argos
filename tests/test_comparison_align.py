"""Alinhamento por coluna escolhida (Date ou PeriodEnd) em build_price_table/build_base_100_table."""

import pandas as pd

from core.comparison import build_base_100_table, build_price_table


def _asset(dates, period_ends, values):
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(dates),
            "PeriodEnd": pd.to_datetime(period_ends),
            "Value": values,
        }
    )


def _pair():
    # Último pregão do mês difere entre os ativos; o fim do período é o mesmo.
    a = _asset(["2024-01-30"], ["2024-01-31"], [10.0])
    b = _asset(["2024-01-31"], ["2024-01-31"], [20.0])
    return {"A": a, "B": b}


def test_price_table_by_date_keeps_different_trading_days():
    table = build_price_table(_pair())

    assert len(table) == 2


def test_price_table_by_period_end_merges_the_same_period():
    table = build_price_table(_pair(), align_col="PeriodEnd")

    assert len(table) == 1
    assert list(table.columns) == ["Date", "A", "B"]
    assert table.loc[0, "Date"] == pd.Timestamp("2024-01-31")
    assert table.loc[0, "A"] == 10.0 and table.loc[0, "B"] == 20.0


def test_base_100_table_by_period_end_merges_the_same_period():
    table = build_base_100_table(_pair(), align_col="PeriodEnd")

    assert len(table) == 1
    assert list(table.columns) == ["Date", "A", "B"]
    assert table.loc[0, "A"] == 100.0 and table.loc[0, "B"] == 100.0


def test_asset_without_align_column_falls_back_to_date():
    data = _pair()
    data["B"] = data["B"].drop(columns="PeriodEnd")

    price = build_price_table(data, align_col="PeriodEnd")
    base = build_base_100_table(data, align_col="PeriodEnd")

    # A usa PeriodEnd (31/01); B não tem PeriodEnd e usa Date (31/01): mesma linha.
    assert list(price.columns) == ["Date", "A", "B"]
    assert list(base.columns) == ["Date", "A", "B"]
    assert len(price) == 1 and len(base) == 1