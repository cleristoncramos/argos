"""Tabela "Maiores quedas e recuperação" (app/ui/drawdown_table.py)."""

import pandas as pd

from app.ui.drawdown_table import (
    DRAWDOWN_TABLE_NOTES,
    FORMATTERS,
    HEADER_LABELS,
    NOT_RECOVERED,
    build_drawdown_display,
    drawdown_intro,
    format_duration,
)
from core.disclaimers import contains_forbidden_phrase
from core.drawdown_episodes import largest_drawdowns


def test_format_duration():
    assert format_duration(None) == "—" and format_duration(float("nan")) == "—"
    assert format_duration(1) == "1 dia" and format_duration(30) == "30 dias"
    assert format_duration(61) == "61 dias (≈ 2 meses)"
    assert format_duration(800) == "800 dias (≈ 2,2 anos)"


def test_display_recovered_and_open():
    df = pd.DataFrame({
        "Date": pd.date_range("2020-01-31", periods=9, freq="ME"),
        "Value": [100, 120, 90, 60, 110, 125, 130, 80, 100],
    })
    display = build_drawdown_display(largest_drawdowns(df))
    assert list(display.columns) == list(HEADER_LABELS)

    first = display.iloc[0]
    assert first["Pico"] == "29/02/2020" and first["Fundo"] == "30/04/2020"
    assert first["Recuperação"] == "30/06/2020"
    assert first["Até o fundo"] == "61 dias (≈ 2 meses)" and first["Total"] == "122 dias (≈ 4 meses)"

    second = display.iloc[1]
    assert second["Recuperação"] == NOT_RECOVERED
    assert second["Fundo à recuperação"] == "—"
    assert second["Total"].endswith(", até a última observação")


def test_cells_and_texts():
    assert FORMATTERS["Queda"](-0.25)[0] == "-25,00%"
    assert "italic" in FORMATTERS["Recuperação"](NOT_RECOVERED)[1]
    assert "italic" not in FORMATTERS["Recuperação"]("30/06/2020")[1]
    assert FORMATTERS["Total"]("61 dias")[0] == "61 dias"

    intro = drawdown_intro("Mensal", 3)
    assert "As 3 maiores quedas" in intro and "fechamentos mensais" in intro
    assert "fechamentos do período" in drawdown_intro("Outra", 2)
    assert "dias corridos" in DRAWDOWN_TABLE_NOTES and "sem estimar" in DRAWDOWN_TABLE_NOTES
    for text in (intro, DRAWDOWN_TABLE_NOTES):
        assert contains_forbidden_phrase(text) is None
