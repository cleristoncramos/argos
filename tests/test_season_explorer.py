"""Textos do bloco "Explorar anos e meses" (app/ui/season_explorer.py)."""

import numpy as np
import pandas as pd

from app.ui.season_explorer import (
    PP_NOTE,
    WINDOW_INTRO,
    WINDOW_NOTE,
    YEARS_INTRO,
    center_cell,
    describe_window,
    describe_year_comparison,
    fmt_pct,
    fmt_pp,
    month_label,
    pct_cell,
    pp_cell,
    price_cell,
    share_cell,
    window_label,
    year_comparison_highlights,
    years_label,
)
from core.disclaimers import contains_forbidden_phrase


def make_summary(diffs):
    return pd.DataFrame({"Diferença (p.p.)": diffs}, index=["Jan", "Fev", "Mar", "Abr"][: len(diffs)])


def test_formatting_helpers():
    assert fmt_pct(3.456) == "+3,46%"
    assert fmt_pct(-1, signed=False) == "-1,00%"
    assert fmt_pct(np.nan) == "—"
    assert fmt_pp(1.5) == "+1,50 p.p."
    assert fmt_pp(None) == "—"
    assert month_label("Mar") == "Março"
    assert years_label([2023]) == "2023"
    assert years_label([2022, 2023]) == "2022 e 2023"
    assert years_label([2021, 2022, 2023]) == "2021, 2022 e 2023"


def test_year_comparison_highlights_and_sentence():
    highlights = year_comparison_highlights(make_summary([2.0, -1.0, np.nan, 4.5]))

    assert highlights["months"] == 3 and highlights["above"] == 2 and highlights["below"] == 1
    assert highlights["largest_above"] == ("Abr", 4.5)
    assert highlights["largest_below"] == ("Fev", -1.0)

    text = describe_year_comparison(highlights, [2024])
    assert text.startswith("Em 2024, a variação ficou **acima da média histórica em 2 de 3 meses**")
    assert "**abril** (+4,50 p.p.)" in text and "**fevereiro** (-1,00 p.p.)" in text


def test_year_comparison_with_several_years_and_without_data():
    only_up = year_comparison_highlights(make_summary([1.0]))
    assert only_up["largest_below"] is None
    text = describe_year_comparison(only_up, [2022, 2023])
    assert text.startswith("Na média de 2022 e 2023")
    assert "para baixo" not in text

    empty = year_comparison_highlights(make_summary([np.nan, np.nan]))
    assert describe_year_comparison(empty, [2020]) == "Em 2020, não há meses com dado para comparar."


def test_window_label_and_sentence():
    assert window_label("Jun", "Dez") == "do fechamento de junho ao fechamento de dezembro"
    assert window_label("Nov", "Fev").endswith("fevereiro do ano seguinte")

    stats = {"N": 4, "Média": 2.5, "Mediana": 1.0, "Anos positivos (%)": 75.0}
    text = describe_window(stats, "Jun", "Dez")
    assert text.startswith("Do fechamento de junho ao fechamento de dezembro, o preço **subiu em 3 de 4 anos**")
    assert "**+2,50%**" in text and "**+1,00%**" in text

    single = {"N": 1, "Média": -2.0, "Mediana": -2.0, "Anos positivos (%)": 0.0}
    assert "**subiu em 0 de 1 ano**" in describe_window(single, "Jan", "Mar")
    assert describe_window({"N": 0}, "Jan", "Mar").startswith("Nenhum ano")


def test_table_cells():
    assert pp_cell(2.0)[0] == "+2,00 p.p." and "#166534" in pp_cell(2.0)[1]
    assert "#991b1b" in pp_cell(-0.5)[1]
    assert "#334155" in pp_cell(0.0)[1]
    assert pp_cell(np.nan)[0] == "—"
    assert pct_cell(3.0)[0] == "+3,00%" and "#166534" in pct_cell(3.0)[1]
    assert "#991b1b" in pct_cell(-1.0)[1] and "#334155" in pct_cell(0.0)[1]
    assert pct_cell(None)[0] == "—"
    assert price_cell(1234.5)[0] == "1.234,50" and price_cell(np.nan)[0] == "—"
    assert share_cell(66.7)[0] == "67%" and share_cell(None)[0] == "—"
    assert center_cell("10 / 2")[0] == "10 / 2" and center_cell(None)[0] == "—"


def test_texts_are_neutral():
    for text in (YEARS_INTRO, WINDOW_INTRO, WINDOW_NOTE, PP_NOTE):
        assert contains_forbidden_phrase(text) is None
        assert "melhor mês" not in text.lower() and "pior mês" not in text.lower()
