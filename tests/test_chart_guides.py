import ast
import re
import unicodedata
from pathlib import Path

import pytest

from core.chart_guides import (
    CHART_GUIDES,
    GUIDE_FIELDS,
    GUIDE_LABELS,
    chart_guide,
    guide_text,
)

ROOT = Path(__file__).resolve().parent.parent
VIEWS = sorted((ROOT / "app" / "views").glob("*.py"))
UI_FILES = sorted((ROOT / "app" / "ui").glob("*.py"))

# Textos novos: sem recomendação, previsão afirmativa ou ranking.
FORBIDDEN_GUIDE = [
    r"\bmelhor\b", r"\bpior\b", r"\bvai subir\b", r"\bvai cair\b", r"\bvai ocorrer\b",
    r"\bcompre\b", r"\binvista\b", r"\brecomendamos\b", r"\bgarantid[oa]\b",
    r"\boportunidade\b", r"\bquanto investir\b",
]

# Frases afirmativas proibidas em qualquer texto de app/ui/ (item 5.7).
FORBIDDEN_UI = [
    r"\bvai subir\b", r"\bvai cair\b", r"\bcompre\b", r"\binvista\b",
    r"\brecomendamos\b", r"\blucro garantido\b", r"\bretorno garantido\b",
    r"\bmelhor momento para\b", r"\bnão perca\b",
]

GLOSSARY_TERMS = [
    "retorno", "volatilidade", "sharpe", "drawdown", "correlacao",
    "sazonalidade", "rsi", "macd", "medias moveis", "base 100",
]


def plain(text):
    text = unicodedata.normalize("NFKD", text.lower().replace("_", " "))
    return "".join(c for c in text if not unicodedata.combining(c))


def string_constants(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        n.value for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    ]


def count_calls(path, attribute=None, name=None):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    total = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if attribute and isinstance(func, ast.Attribute) and func.attr == attribute:
            total += 1
        if name and isinstance(func, ast.Name) and func.id == name:
            total += 1
    return total


def guide_ids_used(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "render_chart_guide"
        and node.args
        and isinstance(node.args[0], ast.Constant)
    ]


# 5.2 estrutura: quatro partes, curtas e não vazias
def test_every_guide_has_four_short_parts():
    assert len(CHART_GUIDES) >= 22
    for chart_id, guide in CHART_GUIDES.items():
        assert set(guide) == set(GUIDE_FIELDS), chart_id
        for field in GUIDE_FIELDS:
            text = guide[field]
            assert 15 <= len(text) <= 260, (chart_id, field, len(text))
            assert text.endswith("."), (chart_id, field)


def test_labels_cover_all_fields():
    assert set(GUIDE_LABELS) == set(GUIDE_FIELDS)


def test_guide_lookup_and_text():
    assert chart_guide("drawdown")["mede"].startswith("A queda")
    text = guide_text("drawdown")
    for label in GUIDE_LABELS.values():
        assert label + ":" in text
    with pytest.raises(KeyError, match="sem roteiro"):
        chart_guide("grafico_inexistente")


# 5.7 neutralidade nos roteiros
def test_guides_use_neutral_language():
    for chart_id, guide in CHART_GUIDES.items():
        for text in guide.values():
            lowered = text.lower()
            for pattern in FORBIDDEN_GUIDE:
                assert not re.search(pattern, lowered), (chart_id, pattern, text)


def test_every_guide_states_a_limit_on_conclusions():
    for chart_id, guide in CHART_GUIDES.items():
        assert plain(guide["nao_permite"]).split()[0] in {
            "concluir", "dizer", "estimar", "tratar", "explicar", "ordenar",
            "indicar", "identificar", "prever", "calcular",
        }, chart_id


# 5.5 "nenhum gráfico sem texto": cada plotly_chart tem um roteiro na página
@pytest.mark.parametrize("page", VIEWS, ids=lambda p: p.name)
def test_every_chart_on_a_page_has_a_guide(page):
    charts = count_calls(page, attribute="plotly_chart")
    guides = guide_ids_used(page)
    assert len(guides) >= charts, (page.name, charts, len(guides))
    for chart_id in guides:
        assert chart_id in CHART_GUIDES, (page.name, chart_id)


def test_pages_were_found():
    assert len(VIEWS) >= 5
    assert any(count_calls(p, attribute="plotly_chart") for p in VIEWS)


# 5.4 os 10 termos da lista no glossário
def test_glossary_covers_the_ten_required_terms():
    import core.glossary as glossary

    data = [v for v in vars(glossary).values() if isinstance(v, (dict, list, tuple))]
    blob = plain(repr(data))
    missing = [term for term in GLOSSARY_TERMS if term not in blob]
    assert not missing, f"Termos ausentes em core/glossary.py: {missing}"


# 5.7 linguagem neutra em todos os textos de app/ui/
@pytest.mark.parametrize("path", UI_FILES, ids=lambda p: p.name)
def test_ui_texts_have_no_prescriptive_phrases(path):
    for text in string_constants(path):
        lowered = text.lower()
        for pattern in FORBIDDEN_UI:
            assert not re.search(pattern, lowered), (path.name, pattern, text)


def test_chart_guide_component_exists_and_uses_core():
    source = (ROOT / "app" / "ui" / "chart_guide.py").read_text(encoding="utf-8")
    assert "def render_chart_guide" in source
    assert "Como ler este gráfico" in source