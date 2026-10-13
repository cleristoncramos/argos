"""Configuração comum dos testes: isola o ambiente do terminal."""

import pytest

ENV_VARS = (
    "ARGOS_DEMO_MODE",
    "ARGOS_DEMO_DIR",
    "ARGOS_LLM_MODE",
    "ARGOS_LLM_RECORD",
    "OPENAI_API_KEY",
)


@pytest.fixture(autouse=True)
def _clean_argos_environment(monkeypatch):
    """Nenhum teste depende de variáveis deixadas no terminal, nem chama a API por engano."""
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)