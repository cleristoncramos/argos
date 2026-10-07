import pandas as pd

from app.ui.metric_card import build_metric_card_html
from app.ui.tables import build_table_html, date_cell, number_cell, percent_cell
from app.ui.colors import NEGATIVE_FG, POSITIVE_FG, tone_icon, tone_of


def test_tone_of():
    assert tone_of(0.1) == "positive"
    assert tone_of(-0.1) == "negative"
    assert tone_of(0) == "neutral"
    assert tone_of(float("nan")) == "neutral"
    assert tone_of(None) == "neutral"
    assert tone_icon(1) == "▲" and tone_icon(-1) == "▼" and tone_icon(0) == "−"


def test_cells():
    assert number_cell(1234.5)[0] == "1.234,50"
    assert number_cell(None)[0] == "—"
    assert date_cell("2026-10-06")[0] == "06/10/2026"
    assert percent_cell(fraction=True)(0.1234)[0] == "12,34%"
    assert percent_cell(fraction=False)(12.0)[0] == "12,00%"
    assert POSITIVE_FG in percent_cell(colored=True)(0.1)[1]
    assert NEGATIVE_FG in percent_cell(colored=True)(-0.1)[1]
    assert percent_cell()(float("nan"))[0] == "—"


def test_table_escapes_html_and_uses_formatters():
    df = pd.DataFrame({"Nome": ["<b>x</b>"], "Valor": [10.0]})
    html = build_table_html(df, ["Nome", "Valor"], {"Valor": number_cell}, max_height=300)
    assert "&lt;b&gt;x&lt;/b&gt;" in html
    assert "<b>x</b>" not in html
    assert "10,00" in html
    assert "max-height:300px" in html


def test_metric_card_tooltip_badge_and_escape():
    html = build_metric_card_html(
        "Retorno <x>", "<span>1</span>", metric_key="sharpe",
        badge=("▲ 10%", "positive"), subtitle="sub",
    )
    assert "Retorno &lt;x&gt;" in html
    assert "Unidade" in html          # tooltip educativo
    assert POSITIVE_FG in html        # cor do badge
    assert "sub" in html


def test_metric_card_free_tooltip_escaped():
    html = build_metric_card_html("T", "1", tooltip='diz "oi"')
    assert "&quot;oi&quot;" in html


def test_percent_cell_has_no_thousands_separator():
    # Mesmo comportamento de core.formatters.format_return_pct
    assert percent_cell()(12.345)[0] == "1234,50%"