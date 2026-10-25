"""Tabela e textos da página "Panorama do Catálogo" (app/ui/panorama_table.py)."""

from pathlib import Path

import pandas as pd

from app.ui.panorama_table import (
    FORMATTERS,
    HEADER_LABELS,
    PANORAMA_NOTES,
    PANORAMA_NOTICE,
    RATE_NOTE,
    SORT_OPTIONS,
    asset_label,
    build_panorama_display,
    has_rates,
    unavailable_assets,
)
from core.disclaimers import contains_forbidden_phrase
from core.panorama import COLUMNS, STATUS_NO_DATA, STATUS_OK, STATUS_RATE

APP = Path(__file__).resolve().parents[1] / "app"


def sample_table():
    rows = [
        {"Ticker": "AAA.SA", "Nome": "Alfa", "Status": STATUS_OK, "Início": pd.Timestamp("2021-11-01"),
         "Fim": pd.Timestamp("2026-10-23"), "Começa depois": False, "Variação no período": 0.5,
         "Variação em 12 meses": -0.1, "Volatilidade anualizada": 0.3, "Queda máxima": -0.4, "Alertas": 1},
        {"Ticker": "BBB.SA", "Nome": "Beta", "Status": STATUS_NO_DATA, "Início": None, "Fim": None,
         "Começa depois": False, "Variação no período": None, "Variação em 12 meses": None,
         "Volatilidade anualizada": None, "Queda máxima": None, "Alertas": None},
        {"Ticker": "^TNX", "Nome": "Treasury", "Status": STATUS_RATE, "Início": pd.Timestamp("2023-01-02"),
         "Fim": pd.Timestamp("2026-10-23"), "Começa depois": True, "Variação no período": None,
         "Variação em 12 meses": None, "Volatilidade anualizada": None, "Queda máxima": None, "Alertas": 0},
    ]
    return pd.DataFrame(rows, columns=COLUMNS)


def test_display_rows():
    display = build_panorama_display(sample_table())
    assert list(display.columns) == list(HEADER_LABELS)
    assert display.loc[0, "Ativo"] == "Alfa (AAA.SA)" and display.loc[0, "Histórico"] == "01/11/2021"
    assert display.loc[2, "Histórico"] == "02/01/2023*"
    assert pd.isna(display.loc[1, "Histórico"]) and pd.isna(display.loc[1, "Alertas"])
    assert display.loc[0, "Alertas"] == 1


def test_asset_label_does_not_repeat_ticker():
    assert asset_label("Alfa", "AAA.SA") == "Alfa (AAA.SA)"
    assert asset_label("Treasury 1-3 Anos (VGSH)", "VGSH") == "Treasury 1-3 Anos (VGSH)"
    assert asset_label("Trend Ouro (GOLD11)", "GOLD11.SA") == "Trend Ouro (GOLD11)"
    assert asset_label("Treasury 10 Anos", "^TNX") == "Treasury 10 Anos (^TNX)"
    assert asset_label("Visa", "V") == "Visa (V)"  # ticker de uma letra contido no nome


def test_cells_never_show_zero_for_missing():
    assert FORMATTERS["Variação no período"](0.5)[0] == "+50,00%"
    assert "#166534" in FORMATTERS["Variação no período"](0.5)[1]
    assert FORMATTERS["Variação em 12 meses"](-0.1)[0] == "-10,00%"
    assert "#991b1b" in FORMATTERS["Variação em 12 meses"](-0.1)[1]
    assert FORMATTERS["Variação no período"](0.0)[0] == "0,00%"
    for column in ("Variação no período", "Volatilidade anualizada", "Queda máxima", "Histórico", "Alertas"):
        assert FORMATTERS[column](None)[0] == "—"
        assert FORMATTERS[column](float("nan"))[0] == "—"
    assert FORMATTERS["Volatilidade anualizada"](0.3)[0] == "30,00%"
    assert FORMATTERS["Ativo"]("Alfa (AAA.SA)")[0] == "Alfa (AAA.SA)"


def test_helpers_and_texts():
    table = sample_table()
    assert unavailable_assets(table) == ["BBB.SA"]
    assert has_rates(table) and not has_rates(table.iloc[:2])
    assert list(SORT_OPTIONS)[0] == "Nome"
    assert "não é uma recomendação" in PANORAMA_NOTICE
    assert "nunca zero" in PANORAMA_NOTES
    for text in (PANORAMA_NOTICE, PANORAMA_NOTES, RATE_NOTE):
        assert contains_forbidden_phrase(text) is None
        for word in ("vencedor", "oportunidade", "melhores investimentos"):
            assert word not in text.lower()


def test_page_queries_one_group_on_demand():
    source = (APP / "views" / "panorama_catalogo.py").read_text(encoding="utf-8")
    assert 'st.button("Gerar panorama"' in source and "if load:" in source
    assert 'a["group"] == group' in source and "MAX_ASSETS_PER_QUERY" in source
    assert 'list(SORT_OPTIONS), index=0' in source  # ordem inicial por nome
