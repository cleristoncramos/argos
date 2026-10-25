"""Panorama descritivo de um grupo do catálogo (core/panorama.py)."""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from core.panorama import (
    COLUMNS,
    STATUS_NO_DATA,
    STATUS_OK,
    STATUS_RATE,
    asset_overview,
    build_panorama,
    panorama_period,
    sort_panorama,
)

A = {"ticker": "AAA.SA", "name": "Alfa"}
B = {"ticker": "BBB.SA", "name": "beta"}
C = {"ticker": "CCC.SA", "name": "Gama"}
RATE = {"ticker": "^TNX", "name": "Treasury 10 Anos"}


def daily(values, start="2024-01-01"):
    dates = pd.bdate_range(start, periods=len(values))
    return pd.DataFrame({"Date": dates, "Close": values, "Volume": 1000})


def smooth(n, growth=0.0005, seed=0):
    rng = np.random.default_rng(seed)
    return list(100 * np.cumprod(1 + growth + rng.normal(0, 0.005, n)))


def test_overview_metrics():
    values = smooth(600)
    row = asset_overview(daily(values), A, requested_start=date(2024, 1, 1))
    assert list(row) == COLUMNS
    assert row["Status"] == STATUS_OK and not row["Começa depois"]
    assert row["Variação no período"] == pytest.approx(values[-1] / values[0] - 1)
    assert row["Variação em 12 meses"] is not None
    returns = pd.Series(values).pct_change().dropna()
    assert row["Volatilidade anualizada"] == pytest.approx(returns.std() * np.sqrt(252))
    peak = pd.Series(values).cummax()
    assert row["Queda máxima"] == pytest.approx((pd.Series(values) / peak - 1).min())
    assert row["Alertas"] == 0
    assert row["Início"] == pd.Timestamp("2024-01-01")


def test_short_history_and_late_start():
    row = asset_overview(daily(smooth(60), start="2026-06-01"), A, requested_start=date(2021, 11, 1))
    assert row["Começa depois"]
    assert row["Variação em 12 meses"] is None  # menos de 1 ano de dados
    assert row["Alertas"] >= 1  # histórico curto na fonte


def test_no_data_and_rates_stay_empty_not_zero():
    for df in (None, pd.DataFrame(), daily([10.0]), pd.DataFrame({"Date": ["2024-01-01"]})):
        row = asset_overview(df, A)
        assert row["Status"] == STATUS_NO_DATA
        assert all(row[c] is None for c in ("Variação no período", "Volatilidade anualizada", "Queda máxima"))

    rate = asset_overview(daily(smooth(300)), RATE)
    assert rate["Status"] == STATUS_RATE and rate["Variação no período"] is None
    assert rate["Início"] is not None

    one_return = asset_overview(daily([10.0, 11.0]), A)
    assert one_return["Volatilidade anualizada"] is None and one_return["Variação no período"] == pytest.approx(0.1)


def test_build_sort_and_period():
    data = {"AAA.SA": daily(smooth(300, growth=0.002)), "CCC.SA": daily(smooth(300, growth=-0.001, seed=3))}
    table = build_panorama(data, [C, B, A], requested_start=date(2024, 1, 1))
    assert list(table["Nome"]) == ["Alfa", "beta", "Gama"]  # ordem inicial por nome, sem diferenciar maiúsculas
    assert table.set_index("Ticker").loc["BBB.SA", "Status"] == STATUS_NO_DATA

    by_change = sort_panorama(table, "Variação no período", descending=True)
    assert list(by_change["Ticker"]) == ["AAA.SA", "CCC.SA", "BBB.SA"]  # vazio no fim
    ascending = sort_panorama(table, "Variação no período")
    assert list(ascending["Ticker"]) == ["CCC.SA", "AAA.SA", "BBB.SA"]  # vazio no fim também

    start, end = panorama_period(table)
    assert start == pd.Timestamp("2024-01-01") and end == table["Fim"].max()
    assert panorama_period(build_panorama({}, [A])) is None
    assert sort_panorama(pd.DataFrame(columns=COLUMNS), "Nome").empty
