"""Referência de comparação sugerida (core/benchmark.py)."""

import pandas as pd
import pytest

from core.assets import ASSETS, get_asset
from core.benchmark import (
    BENCHMARKS,
    align_with_benchmark,
    benchmark_notes,
    describe_comparison,
    suggest_benchmark,
)
from core.disclaimers import contains_forbidden_phrase


@pytest.mark.parametrize("ticker, expected", [
    ("PETR4.SA", "^BVSP"),
    ("BOVA11.SA", "^BVSP"),
    ("IVVB11.SA", "^GSPC"),
    ("AAPL", "^GSPC"),
    ("SPY", "^GSPC"),
    ("O", "^GSPC"),
    ("ETH-USD", "BTC-USD"),
    ("HASH11.SA", "BTC-USD"),
    ("GOLD11.SA", "GC=F"),
    ("MXRF11.SA", None),
    ("SAP", None),
    ("VT", None),
    ("TLT", None),
    ("USDBRL=X", None),
    ("CL=F", None),
    ("^TNX", None),
])
def test_catalog_suggestions(ticker, expected):
    suggestion = suggest_benchmark(ticker, get_asset(ticker))
    assert suggestion.ticker == expected
    assert suggestion.reason


def test_special_cases_and_typed_tickers():
    assert suggest_benchmark("^BVSP", get_asset("^BVSP")).ticker is None
    assert "próprio ativo" in suggest_benchmark("btc-usd", get_asset("BTC-USD")).reason
    assert "IFIX" in suggest_benchmark("KNRI11.SA", get_asset("KNRI11.SA")).reason
    assert suggest_benchmark("DHN-USD").ticker == "BTC-USD"
    assert suggest_benchmark("ABCD3.SA").ticker is None
    # Toda sugestão do catálogo aponta para uma referência disponível.
    for asset in ASSETS:
        ref = suggest_benchmark(asset["ticker"], asset).ticker
        assert ref is None or ref in BENCHMARKS


def frame(dates, values, period_end=None):
    df = pd.DataFrame({"Date": pd.to_datetime(dates), "Value": values})
    if period_end is not None:
        df["PeriodEnd"] = pd.to_datetime(period_end)
    return df


def test_align_daily_uses_common_dates():
    asset = frame(["2026-01-02", "2026-01-03", "2026-01-05", "2026-01-06"], [10, 11, 12, 15])
    ref = frame(["2026-01-02", "2026-01-05", "2026-01-06", "2026-01-07"], [200, 210, 220, 230])
    aligned = align_with_benchmark(asset, ref, "Diário")
    assert list(aligned["Date"].dt.day) == [2, 5, 6]
    assert aligned["Ativo"].tolist() == pytest.approx([100, 120, 150])
    assert aligned["Referência"].tolist() == pytest.approx([100, 105, 110])


def test_align_aggregated_uses_period_end():
    asset = frame(["2026-01-30", "2026-02-27"], [10, 12], period_end=["2026-01-31", "2026-02-28"])
    ref = frame(["2026-01-29", "2026-02-26"], [100, 90], period_end=["2026-01-31", "2026-02-28"])
    aligned = align_with_benchmark(asset, ref, "Mensal")
    # Alinha pelo fim do mês, mas mostra o último pregão do ativo.
    assert aligned["Date"].tolist() == [pd.Timestamp("2026-01-30"), pd.Timestamp("2026-02-27")]
    assert aligned["Referência"].iloc[-1] == pytest.approx(90)


def test_align_without_overlap_or_data():
    asset = frame(["2026-01-02", "2026-01-05"], [10, 11])
    other = frame(["2025-01-02", "2025-01-03"], [10, 11])
    assert align_with_benchmark(asset, other, "Diário").empty
    assert align_with_benchmark(asset, pd.DataFrame(), "Diário").empty
    assert align_with_benchmark(None, asset, "Diário").empty


def test_notes():
    assert any("pontos" in n for n in benchmark_notes("PETR4.SA", "^BVSP", "Mensal"))
    assert not any("câmbio" in n for n in benchmark_notes("PETR4.SA", "^BVSP", "Mensal"))
    assert not any("câmbio" in n for n in benchmark_notes("AAPL", "^GSPC", "Mensal"))
    assert any("câmbio" in n for n in benchmark_notes("IVVB11.SA", "^GSPC", "Mensal"))
    assert any("câmbio" in n for n in benchmark_notes("HASH11.SA", "BTC-USD", "Mensal"))
    assert any("câmbio" in n for n in benchmark_notes("GOLD11.SA", "GC=F", "Mensal"))
    assert not any("câmbio" in n for n in benchmark_notes("ETH-USD", "BTC-USD", "Mensal"))
    assert any("todos os dias" in n for n in benchmark_notes("HASH11.SA", "BTC-USD", "Diário"))
    assert not any("todos os dias" in n for n in benchmark_notes("ETH-USD", "BTC-USD", "Diário"))
    assert any("poucos pontos" in n for n in benchmark_notes("AAPL", "^GSPC", "Anual"))
    for text in benchmark_notes("IVVB11.SA", "^GSPC", "Anual") + benchmark_notes("HASH11.SA", "BTC-USD", "Diário"):
        assert contains_forbidden_phrase(text) is None


def test_describe_comparison():
    aligned = pd.DataFrame({
        "Date": pd.to_datetime(["2021-11-01", "2026-10-23"]),
        "Ativo": [100.0, 209.57],
        "Referência": [100.0, 95.5],
    })
    text = describe_comparison(aligned, "PETR4.SA", "Ibovespa")
    assert text == (
        "Entre 01/11/2021 e 23/10/2026 (datas comuns aos dois), **PETR4.SA** variou "
        "**+109,57%** e **Ibovespa**, **-4,50%**."
    )
    assert "superou" not in text and "melhor" not in text
