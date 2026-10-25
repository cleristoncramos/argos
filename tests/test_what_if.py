"""Bloco "Se você tivesse investido" (app/ui/what_if.py)."""

import pandas as pd

from app.ui.what_if import (
    WHAT_IF_FOOTNOTE,
    WHAT_IF_HOW_TO_READ,
    build_what_if_html,
    format_money,
)
from core.disclaimers import contains_forbidden_phrase
from core.simulation import what_if


def make_result(values, amount=1000.0, dates=None):
    dates = dates or pd.date_range("2024-01-01", periods=len(values), freq="ME")
    return what_if(pd.DataFrame({"Date": dates, "Value": values}), amount)


def test_format_money_brazilian_pattern():
    assert format_money(2052.12, "R$ ") == "R$ 2.052,12"
    assert format_money(-35.5, "US$ ") == "-US$ 35,50"
    assert format_money(1234567.891) == "1.234.567,89"


def test_sentence_with_lookback_and_gain():
    html = build_what_if_html(
        make_result([10.0, 8.0, 20.52]), symbol="PETR4.SA", period_label="1 ano", prefix="R$ "
    )

    assert "Se você tivesse investido <b>R$ 1.000,00</b> em <b>PETR4.SA</b> há <b>1 ano</b>" in html
    assert '<span class="wi-final wi-up">R$ 2.052,00</span>*' in html
    assert "+R$ 1.052,00" in html
    assert "R$ 800,00" in html  # pior momento
    assert "prazo menor que 1 ano" in html
    assert "Não inclui dividendos" in html


def test_sentence_with_chosen_date_and_loss_escapes_symbol():
    html = build_what_if_html(make_result([10.0, 7.5]), symbol="<X>", period_label="")

    assert "em <b>&lt;X&gt;</b> em <b>31/01/2024</b>" in html
    assert "wi-final wi-down" in html
    assert "-250,00" in html


def test_annualized_rate_is_shown_over_one_year():
    dates = list(pd.to_datetime(["2020-01-01", "2022-01-02"]))
    html = build_what_if_html(make_result([10.0, 40.0], dates=dates), symbol="A", period_label="2 anos")

    assert "prazo menor que 1 ano" not in html
    assert "Equivale a, ao ano" in html


def test_texts_are_honest_and_neutral():
    assert "dividendos" in WHAT_IF_FOOTNOTE and "inflação" in WHAT_IF_FOOTNOTE
    for text in (WHAT_IF_FOOTNOTE, WHAT_IF_HOW_TO_READ):
        assert contains_forbidden_phrase(text) is None
