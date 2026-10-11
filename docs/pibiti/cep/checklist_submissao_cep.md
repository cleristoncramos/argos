"""Interruptor da camada educativa (condição experimental da avaliação O6)."""

import contextlib
import os
import types
from pathlib import Path

import pytest

from core import edu_layer
from core.chart_guides import CHART_GUIDES
from core.glossary import GLOSSARY
from core.indicator_docs import INDICATOR_DOCS

ROOT = Path(__file__).resolve().parents[1]


@contextlib.contextmanager
def _edu(value=None):
    old = os.environ.get(edu_layer.ENV_VAR)
    if value is None:
        os.environ.pop(edu_layer.ENV_VAR, None)
    else:
        os.environ[edu_layer.ENV_VAR] = value
    try:
        yield
    finally:
        if old is None:
            os.environ.pop(edu_layer.ENV_VAR, None)
        else:
            os.environ[edu_layer.ENV_VAR] = old


class _FakeSt:
    """Registra chamadas ao Streamlit sem renderizar nada."""

    def __init__(self):
        self.calls = []

    def _record(self, name):
        def call(*args, **kwargs):
            self.calls.append(name)

        return call

    def __getattr__(self, name):
        return self._record(name)

    @contextlib.contextmanager
    def expander(self, *args, **kwargs):
        self.calls.append("expander")
        yield


def _modules():
    from app.ui import chart_guide, education, indicator_docs

    return education, indicator_docs, chart_guide


def _run_all(fake):
    education, indicator_docs, chart_guide = _modules()
    for module in (education, indicator_docs, chart_guide):
        module.st = fake
    education.render_what_it_means(next(iter(GLOSSARY)))
    education.render_glossary()
    indicator_docs.render_indicator_note(next(iter(INDICATOR_DOCS)))
    indicator_docs.render_indicator_glossary()
    chart_guide.render_chart_guide(next(iter(CHART_GUIDES)))


def test_layer_is_enabled_by_default_and_off_values():
    with _edu(None):
        assert edu_layer.edu_layer_enabled() is True
    for value in ("on", "", "true", "1", "talvez"):
        with _edu(value):
            assert edu_layer.edu_layer_enabled() is True
    for value in ("off", "OFF", " 0 ", "false", "no", "nao", "não", "desligada"):
        with _edu(value):
            assert edu_layer.edu_layer_enabled() is False


def test_components_render_when_layer_is_on():
    fake = _FakeSt()
    with _edu("on"):
        _run_all(fake)
    assert fake.calls.count("expander") == 4  # o que significa, glossário, fichas, roteiro
    assert "caption" in fake.calls  # nota curta do indicador


def test_components_hidden_when_layer_is_off():
    fake = _FakeSt()
    with _edu("off"):
        _run_all(fake)
    assert fake.calls == []


def test_unknown_keys_do_not_break_when_layer_is_on():
    education, indicator_docs, _ = _modules()
    fake = _FakeSt()
    education.st = fake
    indicator_docs.st = fake
    with _edu("on"):
        education.render_what_it_means("chave-inexistente")
        indicator_docs.render_indicator_note("chave-inexistente")
        indicator_docs.render_indicator_glossary(["chave-inexistente"])
    assert fake.calls.count("expander") == 1  # só a ficha dos indicadores, vazia


def test_mandatory_notices_do_not_depend_on_the_switch():
    for rel in (
        "core/disclaimers.py",
        "core/simulation_texts.py",
        "app/ui/disclaimers.py",
    ):
        path = ROOT / rel
        if path.exists():
            assert "edu_layer" not in path.read_text(encoding="utf-8"), rel


def test_pages_only_hide_education_through_the_components():
    """Nenhuma página consulta o interruptor diretamente: ele vive só em app/ui/."""
    for path in sorted((ROOT / "app" / "views").glob("*.py")):
        assert "edu_layer" not in path.read_text(encoding="utf-8"), path.name