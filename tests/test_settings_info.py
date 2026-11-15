"""Padrões da análise, situação do ambiente e resumo do arquivo SQLite (Configurações)."""

import sqlite3

import pytest

from core.local_catalog import LocalCatalog
from core.settings_info import (
    ARGOS_DEFAULTS,
    DEFAULT_FREQUENCY_CHOICES,
    DEFAULT_PERIOD_CHOICES,
    FREQUENCY_SETTING,
    PERIOD_SETTING,
    RISK_FREE_SETTING,
    TABLE_DESCRIPTIONS,
    AnalysisDefaults,
    clean_frequency,
    clean_period,
    clean_risk_free,
    defaults_from_settings,
    environment_status,
    file_summary,
    format_rate,
    format_size,
    local_assets_csv,
    settings_from_defaults,
)

ENV_NAMES = ("ARGOS_CATALOGO_EDITAVEL", "ARGOS_CATALOGO_ARQUIVO", "ARGOS_DEMO_MODE", "ARGOS_EDU_LAYER",
             "ARGOS_LLM_MODE", "ARGOS_LLM_RECORD")


@pytest.fixture
def clean_env(monkeypatch):
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    return monkeypatch


def test_padroes_do_argos():
    assert ARGOS_DEFAULTS == AnalysisDefaults("5 anos", "Mensal", 0.0)
    assert "Personalizado" not in DEFAULT_PERIOD_CHOICES
    assert DEFAULT_FREQUENCY_CHOICES == ("Diário", "Semanal", "Mensal", "Semestral", "Anual")


def test_valores_invalidos_voltam_ao_padrao():
    assert clean_period("10 anos") == "10 anos"
    assert clean_period("Personalizado") == "5 anos" and clean_period(None) == "5 anos"
    assert clean_frequency("Diário") == "Diário" and clean_frequency("Horária") == "Mensal"
    assert clean_risk_free("10,5") == 10.5 and clean_risk_free(12.345) == 12.35
    assert clean_risk_free(-3) == 0.0 and clean_risk_free(250) == 100.0
    assert clean_risk_free("abc") == 0.0 and clean_risk_free(None) == 0.0
    assert clean_risk_free(float("nan")) == 0.0


def test_preferencias_ida_e_volta():
    assert defaults_from_settings({}) == ARGOS_DEFAULTS
    assert settings_from_defaults(ARGOS_DEFAULTS) == {
        PERIOD_SETTING: None, FREQUENCY_SETTING: None, RISK_FREE_SETTING: None,
    }
    mine = AnalysisDefaults("1 ano", "Diário", 10.75)
    saved = settings_from_defaults(mine)
    assert saved == {PERIOD_SETTING: "1 ano", FREQUENCY_SETTING: "Diário", RISK_FREE_SETTING: "10.75"}
    assert defaults_from_settings(saved) == mine
    broken = {PERIOD_SETTING: "2 anos", FREQUENCY_SETTING: "x", RISK_FREE_SETTING: "dez"}
    assert defaults_from_settings(broken) == ARGOS_DEFAULTS
    assert format_rate(10.5) == "10,50% ao ano"


def test_ambiente_publico(clean_env):
    rows = {r["Variável"]: r for r in environment_status({})}
    assert list(rows) == ["ARGOS_CATALOGO_EDITAVEL", "ARGOS_CATALOGO_ARQUIVO", "ARGOS_DEMO_MODE",
                          "ARGOS_EDU_LAYER", "ARGOS_LLM_MODE"]
    assert all(r["Valor lido"] == "(não definida)" for r in rows.values())
    assert rows["ARGOS_CATALOGO_EDITAVEL"]["Efeito agora"].startswith("Desligada: catálogo fixo")
    assert rows["ARGOS_CATALOGO_ARQUIVO"]["Efeito agora"].startswith("Sem efeito")
    assert rows["ARGOS_DEMO_MODE"]["Efeito agora"].startswith("Desligado")
    assert rows["ARGOS_EDU_LAYER"]["Efeito agora"] == "Textos educativos visíveis."
    assert rows["ARGOS_LLM_MODE"]["Efeito agora"] == "Explicação assistida: desligada."
    # Chaves de API nunca aparecem, nem o nome delas.
    text = str(environment_status({"OPENAI_API_KEY": "segredo", "XAI_API_KEY": "segredo"}))
    assert "segredo" not in text and "API_KEY" not in text


def test_ambiente_local_e_demo(clean_env, tmp_path):
    clean_env.setenv("ARGOS_CATALOGO_EDITAVEL", "on")
    clean_env.setenv("ARGOS_CATALOGO_ARQUIVO", str(tmp_path / "c.sqlite"))
    clean_env.setenv("ARGOS_EDU_LAYER", "off")
    env = {"ARGOS_CATALOGO_EDITAVEL": "on", "ARGOS_LLM_MODE": "live"}
    rows = {r["Variável"]: r for r in environment_status(env)}
    assert rows["ARGOS_CATALOGO_EDITAVEL"]["Valor lido"] == "on"
    assert rows["ARGOS_CATALOGO_EDITAVEL"]["Efeito agora"].startswith("Ligada")
    assert str(tmp_path / "c.sqlite") in rows["ARGOS_CATALOGO_ARQUIVO"]["Efeito agora"]
    assert rows["ARGOS_EDU_LAYER"]["Efeito agora"].startswith("Textos educativos ocultos")
    assert rows["ARGOS_LLM_MODE"]["Efeito agora"] == "Explicação assistida: chamadas à API do modelo de linguagem."

    clean_env.setenv("ARGOS_DEMO_MODE", "true")
    rows = {r["Variável"]: r for r in environment_status(env)}
    assert rows["ARGOS_CATALOGO_EDITAVEL"]["Efeito agora"] == "Desligada pelo modo de demonstração."
    assert rows["ARGOS_DEMO_MODE"]["Efeito agora"].startswith("Ligado")
    assert rows["ARGOS_LLM_MODE"]["Efeito agora"] == "Explicação assistida: respostas salvas e já validadas."


def test_ambiente_usa_os_environ_por_padrao(clean_env):
    clean_env.setenv("ARGOS_LLM_MODE", "demo")
    rows = {r["Variável"]: r for r in environment_status()}
    assert rows["ARGOS_LLM_MODE"]["Valor lido"] == "demo"


def test_resumo_do_arquivo(tmp_path):
    missing = file_summary(tmp_path / "nao_existe.sqlite", {"ativos": 0})
    assert missing["exists"] is False and missing["size"] == "" and missing["counts"] == {"ativos": 0}

    cat = LocalCatalog(tmp_path / "c.sqlite")
    cat.add_group("Tecnologia", "Ação")
    info = file_summary(tmp_path / "c.sqlite", cat.table_counts())
    assert info["exists"] and info["path"].endswith("c.sqlite")
    assert info["size"].endswith("KB") and len(info["modified"]) == 16
    assert info["counts"] == {"grupos": 1, "ativos": 0, "preferencias": 0}
    assert format_size(512) == "512 bytes" and format_size(2048) == "2,0 KB"
    assert [t[0] for t in TABLE_DESCRIPTIONS] == ["grupos", "ativos", "preferencias"]


def test_csv_dos_ativos_locais():
    records = [{"ticker": "AMD", "name": "AMD Inc.", "group": "local_tec", "class": "Ação"},
               {"ticker": "EMBR3.SA", "name": "Embraer", "group": "acoes_br", "class": "Ação"}]
    content = local_assets_csv(records, {"local_tec": "⭐ Tecnologia"}).decode("utf-8-sig").splitlines()
    assert content == ["ticker;nome;grupo;classe", "AMD;AMD Inc.;⭐ Tecnologia;Ação", "EMBR3.SA;Embraer;acoes_br;Ação"]


def test_copia_de_seguranca_e_um_banco_valido(tmp_path):
    cat = LocalCatalog(tmp_path / "c.sqlite")
    cat.add_group("Tecnologia", "Ação")
    copy = tmp_path / "copia.sqlite"
    copy.write_bytes(cat.snapshot())
    with sqlite3.connect(copy) as db:
        assert db.execute("SELECT rotulo FROM grupos").fetchall() == [("Tecnologia",)]
