"""Mosaico de ativos da página inicial: logomarcas dos 148 ativos, filtros e clique."""

from collections import Counter

import pytest

from core.asset_logos import STOCK_LOGO_BASE_URL
from core.assets import ASSETS
from core.mosaic import (
    CATEGORIES,
    EMBLEMS,
    FLAG_URL,
    INDEX_FLAGS,
    ISSUER_LOGOS,
    TARGET_FREQUENCY,
    TARGET_PERIOD,
    interleave_by_class,
    logo_spec,
    monogram,
    mosaic_data,
)


def _asset(ticker, group="us_stocks", cls="Ação"):
    return {"ticker": ticker, "name": ticker, "group": group, "class": cls, "category_color": "#2563EB"}


def test_todos_os_ativos_tem_logomarca():
    data = mosaic_data(ASSETS, demo=False)
    assert len(data["tiles"]) == len(ASSETS) == 148
    assert {t["t"] for t in data["tiles"]} == {a["ticker"] for a in ASSETS}
    kinds = Counter(t["logo"]["kind"] for t in data["tiles"])
    # Logo de marca (do ativo ou da gestora), bandeira ou emblema: nenhum emoji.
    assert kinds == {"img": 109, "flags": 24, "mark": 15}
    marks = {t["t"] for t in data["tiles"] if t["logo"]["kind"] == "mark"}
    assert marks == set(EMBLEMS)
    for tile in data["tiles"]:
        if tile["logo"]["kind"] != "mark":
            assert tile["logo"]["fallback"], tile["t"]       # monograma se a imagem falhar


def test_mapas_so_tem_ativos_do_catalogo():
    tickers = {a["ticker"] for a in ASSETS}
    assert set(ISSUER_LOGOS) <= tickers and set(INDEX_FLAGS) <= tickers and set(EMBLEMS) <= tickers


def test_logo_da_gestora_e_bandeiras():
    bova = logo_spec(_asset("BOVA11.SA", "equity_etfs", "ETF"), demo=False)
    assert bova["src"] == STOCK_LOGO_BASE_URL.format(ticker="SHV") and "iShares" in bova["note"]
    visa = logo_spec(_asset("V"), demo=False)
    assert visa["bg"] == "#1A1F71" and visa["note"] == ""    # logo branco da própria Visa, fundo escuro
    ibov = logo_spec(_asset("^BVSP", "indexes", "Índice"), demo=False)
    assert ibov == {"kind": "flags", "src": [FLAG_URL.format(code="br")], "tag": "IBOV", "fallback": "BVSP"}
    pair = logo_spec(_asset("EURUSD=X", "forex", "Forex"), demo=False)
    assert pair["src"] == [FLAG_URL.format(code="eu"), FLAG_URL.format(code="us")] and pair["tag"] == "EUR/USD"
    # Par com moeda sem bandeira mapeada: emblema com o monograma.
    odd = logo_spec(_asset("XAUXAG=X", "forex", "Forex"), demo=False)
    assert odd == {"kind": "mark", "text": "XAUX", "bg": "#2563EB"}
    gold = logo_spec(_asset("GC=F", "commodities", "Commodity"), demo=False)
    assert gold == {"kind": "mark", "text": "Au", "bg": "#B8901F"}
    btc = logo_spec(_asset("BTC-USD", "crypto", "Criptomoeda"), demo=False)
    assert btc["kind"] == "img" and "coincap" in btc["src"]
    unknown = logo_spec(_asset("^XYZ", "indexes", "Índice"), demo=False)
    assert unknown["kind"] == "mark" and unknown["text"] == "XYZ"


def test_modo_demo_sem_imagens_remotas(monkeypatch):
    data = mosaic_data(ASSETS, demo=True)
    assert {t["logo"]["kind"] for t in data["tiles"]} == {"mark"}
    assert logo_spec(_asset("GC=F", "commodities", "Commodity"), demo=True)["text"] == "Au"
    monkeypatch.setenv("ARGOS_DEMO_MODE", "true")
    assert logo_spec(_asset("AAPL"))["kind"] == "mark"


def test_monograma():
    assert monogram("^GSPC") == "GSPC" and monogram("petr4.sa") == "PETR"
    assert monogram("BTC-USD") == "BTC" and monogram("USDBRL=X") == "USDB" and monogram("^") == "^"


def test_faixas_categorias_e_destino():
    data = mosaic_data(ASSETS, lanes=4, demo=False)
    lanes = Counter(t["lane"] for t in data["tiles"])
    assert set(lanes) == {0, 1, 2, 3} and max(lanes.values()) - min(lanes.values()) <= 1
    cats = {c["key"]: c["count"] for c in data["categories"]}
    assert cats["todos"] == 148 and sum(v for k, v in cats.items() if k != "todos") == 148
    assert [c["key"] for c in data["categories"][1:]] == [key for key, _, _ in CATEGORIES]
    assert data["period"] == TARGET_PERIOD == "5 anos" and data["frequency"] == TARGET_FREQUENCY == "Mensal"
    # Grupo fora das categorias (catálogo local): categoria "outros", não some do mosaico.
    extra = mosaic_data([_asset("AMD", "local_tec")], demo=False)
    assert extra["tiles"][0]["cat"] == "outros" and extra["categories"] == [
        {"key": "todos", "label": "Todos", "count": 1}]


def test_intercala_as_classes():
    assets = [_asset("A1"), _asset("A2"), _asset("C1", "crypto", "Criptomoeda")]
    assert [a["ticker"] for a in interleave_by_class(assets)] == ["A1", "C1", "A2"]


def test_clique_prepara_a_analise_individual():
    from streamlit.testing.v1 import AppTest

    def script():
        import streamlit as st
        from app.ui.state import AUTOLOAD_KEY, queue_individual_analysis

        st.session_state["asset_load_button_asset_select"] = "antigo"
        queue_individual_analysis({"ticker": "VALE3.SA", "group": "br_stocks"}, "5 anos", "Mensal")
        st.write(st.session_state[AUTOLOAD_KEY])

    at = AppTest.from_function(script)
    at.run()
    assert not at.exception
    state = at.session_state
    assert state["asset_symbol"] == "VALE3.SA" and state["asset_group"] == "br_stocks"
    assert state["asset_period"] == "5 anos" and state["asset_frequency"] == "Mensal"
    from core.periods import period_start_date
    assert state["asset_start_date"] == period_start_date("5 anos", state["asset_end_date"])
    assert state["asset_loaded"] is False and "asset_load_button_asset_select" not in state
    assert state["asset_autoload"] is True


@pytest.mark.parametrize("ticker", ["BOVA11.SA", "KNRI11.SA", "GOLD11.SA", "AXIA3.SA"])
def test_fundos_sem_logo_proprio_mostram_quem_e_a_gestora(ticker):
    asset = next(a for a in ASSETS if a["ticker"] == ticker)
    spec = logo_spec(asset, demo=False)
    assert spec["kind"] == "img" and spec["note"].startswith("Logomarca da gestora ou emissora")
