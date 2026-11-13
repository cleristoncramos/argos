"""Etapa 4 da DL2: catálogo editável local (B2) e referência padrão (B1)."""

import pandas as pd
import pytest

from core.assets import ASSETS
from core.benchmark import PREFERRED_REASON, reference_name, resolve_reference, suggest_benchmark
from core.local_catalog import (
    ENV_VAR,
    LOCAL_GROUP_PREFIX,
    REFERENCE_SETTING,
    CatalogError,
    LocalCatalog,
    editable_enabled,
    local_group_labels,
    merged_catalog,
)


def _ok(ticker):
    return pd.DataFrame({"Close": [1.0]})


def _missing(ticker):
    return pd.DataFrame()


@pytest.fixture
def cat(tmp_path):
    return LocalCatalog(tmp_path / "sub" / "catalogo.sqlite", base_assets=ASSETS)


def test_edicao_so_na_instalacao_local(monkeypatch):
    monkeypatch.delenv(ENV_VAR, raising=False)
    monkeypatch.delenv("ARGOS_DEMO_MODE", raising=False)
    assert editable_enabled() is False                     # versão pública: sem a variável
    monkeypatch.setenv(ENV_VAR, "on")
    assert editable_enabled() is True
    monkeypatch.setenv(ENV_VAR, "talvez")
    assert editable_enabled() is False
    monkeypatch.setenv(ENV_VAR, "sim")
    monkeypatch.setenv("ARGOS_DEMO_MODE", "on")
    assert editable_enabled() is False                     # nunca no modo de demonstração


def test_grupos(cat):
    assert cat.groups() == []
    key = cat.add_group("  Tecnologia  ", "Ação")
    assert key == LOCAL_GROUP_PREFIX + "tecnologia"
    assert cat.groups() == [{"key": key, "label": "⭐ Tecnologia", "name": "Tecnologia", "class": "Ação"}]
    assert local_group_labels(cat.groups()) == {key: "⭐ Tecnologia"}
    assert cat.group_class(key) == "Ação" and cat.group_class("br_stocks") == "Ação"
    assert cat.group_class("nao_existe") is None
    assert cat.add_group("Energia & Petróleo", "Ação") == "local_energia_petroleo"

    for label, cls, msg in [
        ("", "Ação", "nome do grupo"),
        ("Bancos", "Inexistente", "classe"),
        ("!!!", "Ação", "letras ou números"),
        ("tecnologia", "Ação", "Já existe"),
        ("Criptomoedas", "Criptomoeda", "Já existe"),          # nome de grupo base
    ]:
        with pytest.raises(CatalogError, match=msg):
            cat.add_group(label, cls)


def test_ativos_validados_antes_de_salvar(cat):
    key = cat.add_group("Tecnologia", "Ação")
    assert cat.add_asset(" amd ", " AMD ", key, _ok) == "AMD"
    assert cat.add_asset("EMBR3.SA", "", "br_stocks", _ok) == "EMBR3.SA"   # grupo base; nome = ticker
    assert cat.assets() == [
        {"ticker": "EMBR3.SA", "name": "EMBR3.SA", "group": "br_stocks"},
        {"ticker": "AMD", "name": "AMD", "group": key},
    ]

    for ticker, group, fetch, msg in [
        ("PLTR", "nao_existe", _ok, "grupo existente"),
        ("XYZ123", key, _missing, "não encontrado"),
        ("??", key, _ok, "Formato inválido"),
        ("PETR4.SA", "br_stocks", _ok, "catálogo base"),
        ("AMD", key, _ok, "já está no seu catálogo"),
    ]:
        with pytest.raises(CatalogError, match=msg):
            cat.add_asset(ticker, "", group, fetch)

    with pytest.raises(CatalogError, match="Remova os ativos"):
        cat.remove_group(key)
    cat.remove_asset("AMD")
    cat.remove_group(key)
    assert cat.groups() == [] and [a["ticker"] for a in cat.assets()] == ["EMBR3.SA"]


def test_registros_no_formato_do_catalogo(cat):
    key = cat.add_group("Tecnologia", "Ação")
    cat.add_asset("AMD", "AMD", key, _ok)
    cat.add_asset("MATIC-USD", "Polygon", "crypto", _ok)
    # Grupo apagado direto na base: o ativo órfão não entra no catálogo.
    cat._execute("INSERT INTO ativos (ticker, nome, grupo) VALUES ('ORF', 'Órfão', 'local_sumiu')")
    records = {r["ticker"]: r for r in cat.records()}
    assert set(records) == {"AMD", "MATIC-USD"}
    assert set(records["AMD"]) >= set(ASSETS[0]) and records["AMD"]["class"] == "Ação"
    assert records["MATIC-USD"]["data_type"] == "crypto" and records["MATIC-USD"]["local"] == "sim"
    merged = merged_catalog(ASSETS, cat.records())
    assert len(merged) == len(ASSETS) + 2 and merged[: len(ASSETS)] == ASSETS


def test_preferencias(cat):
    assert cat.get_setting(REFERENCE_SETTING) is None
    cat.set_setting(REFERENCE_SETTING, "^GSPC")
    cat.set_setting(REFERENCE_SETTING, "BTC-USD")
    assert cat.get_setting(REFERENCE_SETTING) == "BTC-USD"
    cat.set_setting(REFERENCE_SETTING, None)
    assert cat.get_setting(REFERENCE_SETTING) is None


def test_referencia_padrao_tem_prioridade_e_automatica_continua_padrao():
    asset = next(a for a in ASSETS if a["ticker"] == "PETR4.SA")
    assert resolve_reference("PETR4.SA", asset, None) == suggest_benchmark("PETR4.SA", asset)
    assert resolve_reference("PETR4.SA", asset, "") == suggest_benchmark("PETR4.SA", asset)
    chosen = resolve_reference("PETR4.SA", asset, " ^gspc ")
    assert chosen.ticker == "^GSPC" and chosen.reason == PREFERRED_REASON
    # O próprio ativo nunca é a referência dele: volta à sugestão automática.
    assert resolve_reference("^GSPC", None, "^GSPC") == suggest_benchmark("^GSPC", None)


def test_nome_da_referencia():
    assert reference_name("^BVSP") == "Ibovespa"
    assert reference_name("petr4.sa", ASSETS) == next(a["name"] for a in ASSETS if a["ticker"] == "PETR4.SA")
    assert reference_name("^STOXX50E", ASSETS) == "^STOXX50E"
    assert reference_name("X", [{"ticker": "X", "name": ""}]) == "X"


def test_arquivo_da_base(monkeypatch, tmp_path):
    from core.local_catalog import DB_ENV_VAR, DB_FILE, db_path
    monkeypatch.delenv(DB_ENV_VAR, raising=False)
    assert db_path() == DB_FILE and DB_FILE.parent.name == "data"     # data/ fica fora do git
    monkeypatch.setenv(DB_ENV_VAR, str(tmp_path / "x.sqlite"))
    assert db_path() == tmp_path / "x.sqlite"


def _settings_page():
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    return AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app" / "views" / "configuracoes.py"),
                             default_timeout=60)


def test_pagina_publica_mostra_catalogo_somente_leitura(monkeypatch):
    monkeypatch.delenv(ENV_VAR, raising=False)
    at = _settings_page()
    at.run()
    assert not at.exception, [e.message for e in at.exception]
    assert any("fixo e somente leitura" in i.value for i in at.info)
    assert not at.get("form")
    at.selectbox(key="config_referencia").set_value("^GSPC")
    at.button[0].click().run()
    assert at.session_state["referencia_padrao"] == "^GSPC"
    assert any("S&P 500" in s.value for s in at.success)


def test_pagina_local_cria_grupo_e_salva_referencia(monkeypatch, tmp_path):
    monkeypatch.setenv(ENV_VAR, "on")
    monkeypatch.delenv("ARGOS_DEMO_MODE", raising=False)
    monkeypatch.setenv("ARGOS_CATALOGO_ARQUIVO", str(tmp_path / "catalogo.sqlite"))
    at = _settings_page()
    at.run()
    assert not at.exception, [e.message for e in at.exception]
    assert not at.info and len(at.get("form")) == 2
    at.text_input[-1].set_value("Tecnologia")
    at.get("form")  # garante que os formulários foram desenhados
    next(b for b in at.button if b.label == "Criar grupo").click().run()
    assert not at.exception, [e.message for e in at.exception]
    assert any("Tecnologia" in s.value for s in at.success)
    assert LocalCatalog(tmp_path / "catalogo.sqlite").groups()[0]["name"] == "Tecnologia"

    at.selectbox(key="config_referencia").set_value("BTC-USD")
    next(b for b in at.button if b.label == "Salvar referência").click().run()
    assert LocalCatalog(tmp_path / "catalogo.sqlite").get_setting(REFERENCE_SETTING) == "BTC-USD"
