"""Quadro "Sobre o ativo": textos dos 148 ativos e informações do período carregado."""

import json

import pandas as pd
import pytest

from core.asset_profiles import (
    HYPOTHETICAL_AMOUNT,
    PROFILE_NOTE,
    get_profile,
    load_profiles,
    period_facts,
)
from core.assets import ASSETS
from core.currency import currency_info
from core.disclaimers import contains_forbidden_phrase

PROFILES = load_profiles()
# Termos de portais de investimento que o Argos não usa (sem indicação de compra).
OFF_LIMITS = ("recomend", "preço justo", "preço teto", "como comprar", "onde comprar", "vale a pena")


def _texts(profile):
    return [*profile.about, *profile.history, profile.watch]


def test_todos_os_ativos_do_catalogo_tem_texto():
    tickers = {a["ticker"] for a in ASSETS}
    assert set(PROFILES) == tickers and len(PROFILES) == 148


@pytest.mark.parametrize("ticker", sorted(a["ticker"] for a in ASSETS))
def test_texto_completo_neutro_e_com_fonte(ticker):
    profile = PROFILES[ticker]
    assert profile.about and profile.history and profile.watch.strip()
    for text in _texts(profile):
        assert text.strip() and contains_forbidden_phrase(text) is None, text
        assert not any(term in text.lower() for term in OFF_LIMITS), text
    assert profile.sources
    for label, url in profile.sources:
        assert label.strip() and url.startswith("https://"), (ticker, url)
    words = sum(len(t.split()) for t in _texts(profile))
    assert 50 <= words <= 260, (ticker, words)


def test_busca_ignora_caixa_e_espacos():
    assert get_profile(" petr4.sa ", PROFILES).ticker == "PETR4.SA"
    assert get_profile("NAO-EXISTE", PROFILES) is None and get_profile(None, PROFILES) is None
    assert "recomendação" in PROFILE_NOTE


def test_pasta_ausente_e_ticker_duplicado(tmp_path):
    assert load_profiles(tmp_path / "nao_existe") == {}
    entry = {"sobre": ["a"], "historia": ["b"], "observar": "c", "fontes": [["F", "https://f"]]}
    (tmp_path / "a.json").write_text(json.dumps({"X": entry}), encoding="utf-8")
    assert load_profiles(tmp_path)["X"].sources == (("F", "https://f"),)
    (tmp_path / "b.json").write_text(json.dumps({"X": entry}), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicado"):
        load_profiles(tmp_path)


def _daily(values, start="2025-01-01", freq="D"):
    dates = pd.date_range(start, periods=len(values), freq=freq)
    return pd.DataFrame({"Date": dates, "Close": values})


def test_informacoes_de_um_ano_com_preco():
    values = [100.0] * 400
    values[-366] = 100.0
    values[-200] = 80.0
    values[-100] = 150.0
    values[-1] = 120.0
    facts = period_facts(_daily(values), currency_info("PETR4.SA"))
    assert facts[0].startswith("Última cotação no período carregado: R$ 120,00, em ")
    assert "Nos últimos 12 meses: mínima de R$ 80,00" in facts[1] and "máxima de R$ 150,00" in facts[1]
    assert facts[2] == "Nos últimos 12 meses, a variação foi de +20,00%."
    assert f"R$ {HYPOTHETICAL_AMOUNT:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") in facts[3]
    assert "valeria cerca de R$ 1.200,00" in facts[3] and "sem dividendos" in facts[3]


def test_janela_curta_pontos_e_valores_pequenos():
    facts = period_facts(_daily([1000.0, 900.0, 950.0]), currency_info("^BVSP"))
    assert "950,00 pontos" in facts[0] and facts[1].startswith("Nos 2 dias carregados")
    assert facts[2] == "Nos 2 dias carregados, a variação foi de -5,00%."
    assert len(facts) == 3                                  # sem aplicação hipotética em índice
    small = period_facts(_daily([0.15, 0.1523]), currency_info("DOGE-USD"))
    assert "US$ 0,1523" in small[0]


def test_taxas_de_juros_e_casos_limite():
    up = period_facts(_daily([4.0] * 300 + [4.5] * 100), currency_info("^TNX"))
    assert "4,50% ao ano" in up[0] and up[2] == "Nos últimos 12 meses, a taxa subiu 0,50 ponto(s) percentual(is)."
    down = period_facts(_daily([5.0, 4.0]), currency_info("^IRX"))
    assert down[2] == "No 1 dia carregado, a taxa caiu 1,00 ponto(s) percentual(is)."
    flat = period_facts(_daily([3.0, 3.0]), currency_info("^FVX"))
    assert flat[2] == "No 1 dia carregado, a taxa ficou estável."

    assert period_facts(None, currency_info("AAPL")) == []
    assert period_facts(pd.DataFrame(), currency_info("AAPL")) == []
    assert period_facts(pd.DataFrame({"Close": [1.0]}), currency_info("AAPL")) == []
    assert period_facts(_daily([float("nan")]), currency_info("AAPL")) == []
    assert period_facts(_daily([float("inf"), float("nan")]), currency_info("AAPL")) == []
    single = period_facts(_daily([10.0]), currency_info("AAPL"))
    assert len(single) == 1                                 # só a última cotação
    zero = period_facts(_daily([0.0, 5.0]), currency_info("AAPL"))
    assert len(zero) == 2                                   # sem variação a partir de zero
    fx = period_facts(_daily([5.0, 5.5]), currency_info("USDBRL=X"))
    assert fx[0].startswith("Última cotação no período carregado: 5,50") and len(fx) == 3


def test_cifrao_nao_vira_formula_no_markdown():
    from app.ui.asset_profile import _md, _profile_markdown

    assert _md("de R$ 10 a US$ 5") == "de R\$ 10 a US\$ 5"
    text = _profile_markdown(PROFILES["AAPL"])
    assert "US\$ 1 trilhão" in text and "##### Origem e história" in text
