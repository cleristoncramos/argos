"""Bloco "Maiores altas e quedas" (app/ui/extremes_table.py)."""

import pandas as pd

from app.ui.extremes_table import (
    EXTREMES_NOTES,
    FORMATTERS,
    HEADER_LABELS,
    RATE_NOTE,
    build_extremes_display,
    extremes_intro,
)
from core.disclaimers import contains_forbidden_phrase
from core.extreme_moves import extreme_moves, period_changes


def sample():
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2026-07-31", "2026-08-31", "2026-09-30", "2026-10-23"]),
        "Value": [100.0, 120.0, 90.0, 1234.5],
    })
    return extreme_moves(period_changes(df, "Mensal"))


def test_display():
    highs, lows = sample()
    display = build_extremes_display(highs)
    assert list(display.columns) == list(HEADER_LABELS)
    assert display.loc[0, "Período"] == "out/2026 (em andamento)"
    assert display.loc[0, "Entre"] == "30/09/2026 (90,00) → 23/10/2026 (1.234,50)"
    assert display.loc[1, "Período"] == "ago/2026"
    assert build_extremes_display(lows).loc[0, "Período"] == "set/2026"
    empty = build_extremes_display(lows.iloc[0:0])
    assert empty.empty and list(empty.columns) == list(HEADER_LABELS)


def test_cells_and_texts():
    assert FORMATTERS["Variação"](0.2) == ("+20,00%", FORMATTERS["Variação"](0.2)[1])
    assert "#166534" in FORMATTERS["Variação"](0.2)[1]
    assert FORMATTERS["Variação"](-0.25)[0] == "-25,00%" and "#991b1b" in FORMATTERS["Variação"](-0.25)[1]
    assert FORMATTERS["Período"]("ago/2026")[0] == "ago/2026"
    assert FORMATTERS["Entre"]("x → y")[0] == "x → y"

    intro = extremes_intro("Mensal", {"total": 60, "up": 33, "down": 26, "flat": 1})
    assert intro == (
        "No período carregado, **33 de 60 variações mensais** foram positivas (55%) "
        "e 26 foram negativas; 1 sem variação."
    )
    assert extremes_intro("Outra", {"total": 2, "up": 1, "down": 1, "flat": 0}).endswith("negativas.")
    assert "(—)" in extremes_intro("Diário", {"total": 0, "up": 0, "down": 0, "flat": 0})

    assert "não mede quanto esses períodos contribuíram" in EXTREMES_NOTES.replace("ela não\n", "ela não ")
    for text in (intro, EXTREMES_NOTES, RATE_NOTE):
        assert contains_forbidden_phrase(text) is None
