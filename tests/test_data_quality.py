"""Alertas de qualidade e de comportamento atípico dos dados (core/data_quality.py)."""

from datetime import date

import numpy as np
import pandas as pd

from core.data_quality import (
    JUMP_THRESHOLDS,
    assess_data_quality,
    find_jumps,
    longest_flat_run,
    quality_summary,
    series_kind,
    volume_is_relevant,
)
from core.disclaimers import contains_forbidden_phrase


def make_series(prices, start="2020-01-01", freq="B", volume=1000):
    rng = np.random.default_rng(0)
    dates = pd.date_range(start, periods=len(prices), freq=freq)
    vol = volume if np.ndim(volume) else np.full(len(prices), volume)
    return pd.DataFrame({"Date": dates, "Close": prices, "Volume": vol}), rng


def noisy(n, base=100.0, scale=0.01, seed=1):
    """Passeio aleatório suave, sem dias atípicos nem preços repetidos."""
    rng = np.random.default_rng(seed)
    return list(base * np.cumprod(1 + rng.normal(0, scale, n)))


def codes(alerts):
    return [a.code for a in alerts]


def test_series_kind_and_volume_relevance():
    assert series_kind("^TNX") == "rate"
    assert series_kind("^vix") == "volatility_index"
    assert series_kind("BTC-USD") == "crypto"
    assert series_kind("USDBRL=X") == "forex"
    assert series_kind("GC=F") == "commodity"
    assert series_kind("^BVSP") == "index" and series_kind("000001.SS") == "index"
    assert series_kind("PETR4.SA") == "stock" and series_kind(None) == "stock"
    assert volume_is_relevant("PETR4.SA") and volume_is_relevant("GC=F")
    assert not volume_is_relevant("^BVSP") and not volume_is_relevant("EURUSD=X")
    assert set(JUMP_THRESHOLDS) == {"crypto", "commodity", "index", "volatility_index", "forex", "stock"}


def test_clean_series_has_no_alerts():
    df, _ = make_series(noisy(1000))
    assert assess_data_quality(df, "ABC", requested_start=date(2020, 1, 1)) == []
    assert quality_summary([]) == "Nenhum alerta nas verificações automáticas"


def test_empty_or_tiny_inputs():
    assert assess_data_quality(None, "X") == []
    assert assess_data_quality(pd.DataFrame(), "X") == []
    assert assess_data_quality(pd.DataFrame({"Date": ["2020-01-01"]}), "X") == []
    one, _ = make_series([10.0])
    assert assess_data_quality(one, "X") == []
    two, _ = make_series([10.0, 11.0])
    assert find_jumps(two.iloc[:2], "X").empty


def test_temporary_discontinuity_counts_once():
    prices = noisy(300)
    level = prices[150]
    prices[151:154] = [level / 100, level / 100 * 1.001, level / 100 * 0.999]
    prices[154] = level * 1.002
    df, _ = make_series(prices)

    jumps = find_jumps(df, "XPML11.SA")
    assert len(jumps) == 1 and bool(jumps["Reversal"].iloc[0])

    alerts = assess_data_quality(df, "XPML11.SA", requested_start=date(2020, 1, 1))
    assert codes(alerts) == ["temporary_discontinuity"]
    assert alerts[0].level == "warning"
    assert "desdobramento" in alerts[0].text and "-99,00%" in alerts[0].text
    assert alerts[0].text.endswith("que incluem esse período.")


def test_several_discontinuities_are_listed_with_plural():
    prices = noisy(500)
    for position in (60, 140, 220, 300, 380):
        level = prices[position]
        prices[position + 1] = level * 4
        prices[position + 2] = level * 1.001
    df, _ = make_series(prices)

    alerts = assess_data_quality(df, "DHN-USD", requested_start=date(2020, 1, 1))
    assert codes(alerts) == ["temporary_discontinuity"]
    assert "e mais 2" in alerts[0].text
    assert alerts[0].text.endswith("que incluem esses períodos.")


def test_partial_retrace_is_an_atypical_jump_not_a_discontinuity():
    prices = noisy(300)
    prices[150:] = [p * 1.30 for p in prices[150:]]
    prices[151] = prices[151] * 0.88  # devolve só parte da alta
    df, _ = make_series(prices)

    alerts = assess_data_quality(df, "005930.KS", requested_start=date(2020, 1, 1))
    assert codes(alerts) == ["atypical_jump"]
    assert alerts[0].level == "info" and "acima de 25%" in alerts[0].text


def test_many_jumps_are_summarized_and_rates_are_skipped():
    prices = noisy(400, scale=0.005)
    for position in (50, 100, 150, 200, 250):
        prices[position:] = [p * 1.6 for p in prices[position:]]
    df, _ = make_series(prices)

    alerts = assess_data_quality(df, "SOL-USD", requested_start=date(2020, 1, 1))
    assert codes(alerts) == ["atypical_jump"]
    assert "5 dia(s)" in alerts[0].text and "e mais 2" in alerts[0].text

    assert find_jumps(df, "^IRX").empty


def test_jump_must_also_be_atypical_for_the_asset():
    # Série muito volátil: um dia de +30% não foge do comportamento típico.
    rng = np.random.default_rng(3)
    prices = list(100 * np.cumprod(1 + rng.choice([-0.2, 0.2], 300)))
    df, _ = make_series(prices)
    assert find_jumps(df, "XYZ").empty


def test_constant_series_and_non_positive_prices():
    df, _ = make_series([10.0] * 20 + [15.0])
    jumps = find_jumps(df, "XYZ")
    assert len(jumps) == 1  # desvio típico zero: qualquer salto acima do limiar conta

    with_zero, _ = make_series([0.0, 1.0, 1.1, 1.2])
    assert find_jumps(with_zero, "XYZ").empty


def test_flat_prices_depend_on_series_kind():
    prices = noisy(200)
    prices[100:106] = [prices[100]] * 6
    df, _ = make_series(prices, freq="D")

    crypto = assess_data_quality(df, "DHN-USD", requested_start=date(2020, 1, 1))
    assert codes(crypto) == ["flat_prices"] and "6 observações" in crypto[0].text
    assert assess_data_quality(df, "ABC", requested_start=date(2020, 1, 1)) == []

    run, start, end = longest_flat_run(df)
    assert run == 6 and start == df["Date"].iloc[100] and end == df["Date"].iloc[105]
    assert longest_flat_run(df.iloc[0:0]) == (0, None, None)


def test_missing_volume_only_where_relevant():
    volume = np.where(np.arange(1000) % 3 == 0, 0, 500)
    df, _ = make_series(noisy(1000), volume=volume)

    futures = assess_data_quality(df, "PL=F", requested_start=date(2020, 1, 1))
    assert codes(futures) == ["missing_volume"] and "33%" in futures[0].text
    assert assess_data_quality(df, "^BVSP", requested_start=date(2020, 1, 1)) == []
    assert assess_data_quality(df.drop(columns="Volume"), "PL=F", requested_start=date(2020, 1, 1)) == []


def test_long_gap():
    df, _ = make_series(noisy(1000))
    df.loc[500:, "Date"] = df.loc[500:, "Date"] + pd.Timedelta(days=30)

    alerts = assess_data_quality(df, "ABC", requested_start=date(2020, 1, 1))
    assert codes(alerts) == ["long_gap"]
    assert "31 dias corridos" in alerts[0].text


def test_short_history_only_when_source_starts_late():
    df, _ = make_series(noisy(300), start="2025-01-01")

    late = assess_data_quality(df, "HYPE-USD", requested_start=date(2020, 1, 1))
    assert codes(late) == ["short_history"] and "desde 01/01/2025" in late[0].text
    assert assess_data_quality(df, "HYPE-USD", requested_start=date(2025, 1, 1)) == []
    assert codes(assess_data_quality(df, "HYPE-USD")) == ["short_history"]


def test_summary_and_neutral_wording():
    prices = noisy(300)
    level = prices[150]
    prices[151:153] = [level * 3, level * 3]
    prices[153] = level
    prices[200:212] = [prices[200]] * 12
    df, _ = make_series(prices, start="2025-01-01", volume=0)

    alerts = assess_data_quality(df, "AAA.SA", requested_start=date(2020, 1, 1))
    assert codes(alerts) == ["temporary_discontinuity", "flat_prices", "missing_volume", "short_history"]
    summary = quality_summary(alerts)
    assert summary.startswith("4 alerta(s): mudança de patamar")
    for alert in alerts:
        assert contains_forbidden_phrase(alert.text) is None
        assert "fraude" not in alert.text and "manipula" not in alert.text
