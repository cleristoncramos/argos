from datetime import date

import pandas as pd

from core.comparison_checks import (
    build_spans,
    check_period_divergence,
    comparison_notes,
)


def _dates(start, end):
    return pd.date_range(start, end, freq="D")


def _spans(**ranges):
    return build_spans({t: _dates(a, b) for t, (a, b) in ranges.items()})


def test_build_spans_basic_and_skips_empty():
    spans = build_spans({"A": _dates("2022-01-01", "2022-01-10"), "B": []})
    assert len(spans) == 1
    assert spans[0].start == date(2022, 1, 1) and spans[0].observations == 10


def test_no_divergence_for_same_period():
    check = check_period_divergence(
        _spans(A=("2022-01-01", "2023-01-01"), B=("2022-01-03", "2023-01-01"))
    )
    assert not check.divergent and check.has_common_period


def test_divergence_detected():
    check = check_period_divergence(
        _spans(A=("2021-01-01", "2023-01-01"), B=("2022-06-01", "2023-01-01"))
    )
    assert check.divergent
    assert check.shortest_history == "B" and check.longest_history == "A"
    assert check.common_start == date(2022, 6, 1)


def test_no_common_period():
    check = check_period_divergence(
        _spans(A=("2020-01-01", "2020-12-31"), B=("2022-01-01", "2022-12-31"))
    )
    assert not check.has_common_period
    notes = comparison_notes(check, ["A", "B"], "Mensal")
    assert notes[0][0] == "error"


def test_empty_spans():
    check = check_period_divergence([])
    assert not check.divergent and not check.has_common_period
    assert comparison_notes(check, ["AAPL", "MSFT"], "Mensal") == []


def test_divergence_note_and_aligned_variant():
    check = check_period_divergence(
        _spans(A=("2021-01-01", "2023-01-01"), B=("2022-06-01", "2023-01-01"))
    )
    warning = comparison_notes(check, ["AAPL", "MSFT"], "Mensal")
    assert warning[0][0] == "warning" and "período comum" in warning[0][1]
    aligned = comparison_notes(check, ["AAPL", "MSFT"], "Mensal", aligned_to_common=True)
    assert aligned[0][0] == "info"


def test_clean_selection_has_no_notes():
    check = check_period_divergence(
        _spans(A=("2022-01-01", "2023-01-01"), B=("2022-01-01", "2023-01-01"))
    )
    assert comparison_notes(check, ["AAPL", "MSFT"], "Mensal") == []


def test_rate_mixed_with_prices():
    check = check_period_divergence([])
    notes = comparison_notes(check, ["^TNX", "AAPL"], "Mensal")
    assert any(level == "warning" and "taxas de juros" in text for level, text in notes)


def test_multiple_currencies():
    check = check_period_divergence([])
    notes = comparison_notes(check, ["PETR4.SA", "AAPL"], "Mensal")
    assert any("moedas diferentes" in text for _, text in notes)


def test_crypto_daily_calendar_note():
    check = check_period_divergence([])
    daily = comparison_notes(check, ["BTC-USD", "AAPL"], "Diário")
    monthly = comparison_notes(check, ["BTC-USD", "AAPL"], "Mensal")
    assert any("calendários" in text for _, text in daily)
    assert not any("calendários" in text for _, text in monthly)


def test_overlap_note():
    check = check_period_divergence([])
    notes = comparison_notes(check, ["SPY", "VOO"], "Mensal")
    assert any("sobreposta" in text for _, text in notes)