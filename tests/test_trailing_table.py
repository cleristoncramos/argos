"""Tabela "Variação por prazo" (app/ui/trailing_table.py)."""

import pandas as pd

from app.ui.trailing_table import (
    FORMATTERS,
    HEADER_LABELS,
    NOT_APPLICABLE,
    RATE_NOTE,
    TRAILING_NOTES,
    build_trailing_display,
    change_cell,
    rate_cell,
    trailing_intro,
)
from core.disclaimers import contains_forbidden_phrase
from core.trailing_returns import trailing_returns


def sample_display():
    dates = pd.bdate_range("2021-11-01", "2026-10-23")
    df = pd.DataFrame({"Date": dates, "Close": [100.0 + i * 0.1 for i in range(len(dates))]})
    return build_trailing_display(trailing_returns(df)).set_index("Janela")


def test_display_rows():
    display = sample_display()
    assert list(display.reset_index().columns) == list(HEADER_LABELS)

    assert display.loc["5 anos", "Início"] == "01/11/2021*"           # início ajustado
    assert display.loc["1 ano", "Início"] == "23/10/2025"
    assert display.loc["6 meses", "Taxa"] == NOT_APPLICABLE           # prazo menor que 1 ano
    assert display.loc["1 ano", "Taxa"] > 0
    assert pd.isna(display.loc["10 anos", "Início"])                  # sem histórico
    assert pd.isna(display.loc["10 anos", "Variação"]) and pd.isna(display.loc["10 anos", "Taxa"])
    assert pd.isna(display.loc["10 anos", "Fim"]) and pd.isna(display.loc["10 anos", "Valor final"])


def test_cells():
    assert change_cell(0.1234)[0] == "+12,34%" and "#166534" in change_cell(0.1234)[1]
    assert change_cell(-0.05)[0] == "-5,00%" and "#991b1b" in change_cell(-0.05)[1]
    assert change_cell(0.0) == ("0,00%", change_cell(0.0)[1]) and "color" not in change_cell(0.0)[1]
    assert change_cell(None)[0] == "—" and change_cell(float("nan"))[0] == "—"
    assert rate_cell(NOT_APPLICABLE)[0] == NOT_APPLICABLE and "italic" in rate_cell(NOT_APPLICABLE)[1]
    assert rate_cell(0.08)[0] == "+8,00%"

    assert FORMATTERS["Janela"]("1 ano")[0] == "1 ano"
    assert FORMATTERS["Início"](None)[0] == "—" and FORMATTERS["Início"]("01/11/2021*")[0] == "01/11/2021*"
    assert FORMATTERS["Valor final"](1234.5)[0] == "1.234,50" and FORMATTERS["Valor inicial"](None)[0] == "—"


def test_texts():
    intro = trailing_intro(pd.Timestamp("2021-11-01"), pd.Timestamp("2026-10-23"))
    assert "Base: o período carregado na barra lateral" in intro
    assert "de 01/11/2021 a 23/10/2026" in intro and "o preço variou" in intro
    assert "o nível da taxa" in trailing_intro(pd.Timestamp("2021-11-01"), pd.Timestamp("2026-10-23"), rate=True)

    assert "Variação acumulada" in TRAILING_NOTES and "Taxa equivalente ao ano" in TRAILING_NOTES
    assert "fechamentos diários" in TRAILING_NOTES and "Retorno Total" in TRAILING_NOTES
    for text in (TRAILING_NOTES, RATE_NOTE, intro):
        assert contains_forbidden_phrase(text) is None
