"""Maiores quedas e recuperação no gráfico de drawdown (app/ui/drawdown_highlight.py)."""

import pandas as pd
import plotly.graph_objects as go

from app.ui.drawdown_highlight import (
    DRAWDOWN_CSS,
    DRAWDOWN_NOTES,
    HIGHLIGHT_HELP,
    NO_DRAWDOWN,
    PILLS_KEY,
    add_episode_highlight,
    build_facts_html,
    drawdown_prompt,
    format_duration,
    short_duration,
    span_facts,
    span_label,
)
from core.disclaimers import contains_forbidden_phrase
from core.drawdown_episodes import episode_spans, largest_drawdowns

NB = " "


def _spans():
    df = pd.DataFrame({
        "Date": pd.date_range("2020-01-31", periods=9, freq="ME"),
        "Value": [100, 120, 90, 60, 110, 125, 130, 80, 100],
    })
    return episode_spans(largest_drawdowns(df))


def test_duracoes():
    assert format_duration(None) == "—" and format_duration(float("nan")) == "—"
    assert format_duration(1) == "1 dia" and format_duration(30) == "30 dias"
    assert format_duration(61) == f"61 dias (≈{NB}2{NB}meses)"
    assert format_duration(800) == f"800 dias (≈{NB}2,2{NB}anos)"
    assert short_duration(1) == "1 dia" and short_duration(12) == "12 dias"
    assert short_duration(122) == f"≈{NB}4{NB}meses" and short_duration(800) == f"≈{NB}2,2{NB}anos"


def test_botoes_trazem_queda_datas_e_duracao_total():
    first, second = _spans()
    assert span_label(first) == f"1ª · -50,00% · 02/2020 → 06/2020 · ≈{NB}4{NB}meses"
    assert span_label(second) == f"2ª · -38,46% · 07/2020 → sem recuperação · ≈{NB}2{NB}meses até agora"
    assert drawdown_prompt("Mensal", 3) == "As 3 maiores quedas do período, nos fechamentos mensais"
    assert drawdown_prompt("Outra", 1) == "A maior queda do período, nos fechamentos do período"


def test_ficha_com_as_informacoes_da_antiga_tabela():
    first, second = _spans()
    facts = dict(span_facts(first))
    assert facts == {
        "Queda (pico ao fundo)": "-50,00%",
        "Pico": "29/02/2020",
        "Fundo": "30/04/2020",
        "Recuperação do pico": "30/06/2020",
        "Do pico ao fundo": f"61 dias (≈{NB}2{NB}meses)",
        "Do fundo à recuperação": f"61 dias (≈{NB}2{NB}meses)",
        "Duração total": f"122 dias (≈{NB}4{NB}meses)",
    }
    open_facts = dict(span_facts(second))
    assert open_facts["Recuperação do pico"] == "sem recuperação"
    assert open_facts["Do fundo à recuperação"] == "—"
    assert open_facts["Duração total"].endswith(", até 30/09/2020")
    html = build_facts_html(first)
    assert "1ª maior queda" in html and html.count("<span>") == 7 and "dd-fact-main" in html


def test_destaque_no_grafico_com_tooltips():
    first, second = _spans()
    fig = go.Figure()
    add_episode_highlight(fig, first)
    shape = fig.layout.shapes[0]
    assert shape.type == "rect" and shape.layer == "below" and shape.opacity == 0.07
    assert pd.Timestamp(shape.x0) == first["start"] and pd.Timestamp(shape.x1) == first["end"]
    markers = fig.data[0]
    assert list(markers.y) == [0.0, -50.0, 0.0] and markers.showlegend is False
    assert markers.customdata[0].startswith("<b>Pico em 29/02/2020</b> · 1ª maior queda")
    assert "Do pico ao fundo: 61 dias" in markers.customdata[1] and "Duração total: 122 dias" in markers.customdata[2]

    fig_open = go.Figure()
    add_episode_highlight(fig_open, second)            # sem recuperação: só pico e fundo
    assert len(fig_open.data[0].x) == 2 and "Do fundo à recuperação: —" in fig_open.data[0].customdata[0]


def test_textos_e_estilo():
    assert f".st-key-{PILLS_KEY}" in DRAWDOWN_CSS and "border-radius: 0" in DRAWDOWN_CSS
    assert "dias corridos" in DRAWDOWN_NOTES and "sem estimar" in DRAWDOWN_NOTES
    for text in (DRAWDOWN_NOTES, HIGHLIGHT_HELP, NO_DRAWDOWN, *[span_label(s) for s in _spans()]):
        assert contains_forbidden_phrase(text) is None
