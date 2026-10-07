from datetime import date

import pytest

from core.glossary import (
    GLOSSARY,
    find_forbidden_language,
    get_glossary_entry,
    glossary_terms,
)
from core.periods import CUSTOM_PERIOD, PERIOD_OPTIONS, period_start_date


def test_period_start_regular():
    assert period_start_date("5 anos", date(2026, 10, 6)) == date(2021, 11, 1)


def test_period_start_december_rolls_year():
    assert period_start_date("1 ano", date(2026, 12, 15)) == date(2026, 1, 1)


@pytest.mark.parametrize("bad", [CUSTOM_PERIOD, "abc", "", "anos 5"])
def test_period_start_invalid(bad):
    with pytest.raises(ValueError):
        period_start_date(bad, date(2026, 10, 6))


def test_period_options_include_custom():
    assert PERIOD_OPTIONS[-1] == CUSTOM_PERIOD


def test_glossary_has_all_terms_from_minutes():
    expected = {"retorno", "volatilidade", "drawdown", "sharpe", "correlacao",
                "media_movel", "rsi", "macd", "base_100", "sazonalidade"}
    assert set(glossary_terms()) == expected


def test_glossary_entries_complete():
    for entry in GLOSSARY.values():
        assert entry.definition and entry.example and entry.limitation


def test_glossary_neutral_language():
    assert find_forbidden_language() == []


def test_glossary_lookup():
    assert get_glossary_entry("sharpe").term == "Índice de Sharpe"
    assert get_glossary_entry("inexistente") is None

def test_find_forbidden_language_detects_phrase(monkeypatch):
    import core.glossary as glossary
    from core.glossary import GlossaryEntry

    bad = GlossaryEntry("x", "X", "Este é o momento de comprar.", "ex", "lim")
    monkeypatch.setitem(glossary.GLOSSARY, "x", bad)

    found = glossary.find_forbidden_language()
    assert ("Este é o momento de comprar.", "momento de comprar") in found