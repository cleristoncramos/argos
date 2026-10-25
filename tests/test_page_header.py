"""Cabeçalho padrão das páginas e títulos sem ícones."""

import re
from pathlib import Path

import pytest

from app.ui.page_header import ANALYSIS_PAGES, build_page_header_html
from app.ui.pages import MENU_PAGES

APP = Path(__file__).resolve().parents[1] / "app"
# Título que começa com ícone: st.title/header/subheader("…"), markdown "## …" ou title="…"
ICON_HEADING = re.compile(r'(st\.(?:title|header|subheader)\(f?"|"#{1,5} |\btitle=")[^\w\s"{]')


def test_header_uses_menu_title_and_numbering():
    html = build_page_header_html("views/comparacao_ativos.py", "Subtítulo <x>")
    assert '<h1 class="pg-title">Comparação de Ativos</h1>' in html
    assert "Módulo 02 de 06" in html
    assert "Subtítulo &lt;x&gt;" in html


def test_about_page_is_not_numbered_as_analysis():
    assert MENU_PAGES[-1].title == "Sobre o Projeto"
    assert MENU_PAGES[-1] not in ANALYSIS_PAGES
    with pytest.raises(ValueError):
        build_page_header_html(MENU_PAGES[-1].path, "x")


def test_every_analysis_page_uses_the_standard_header():
    for spec in ANALYSIS_PAGES:
        source = (APP / spec.path).read_text(encoding="utf-8")
        assert f'render_page_header(\n    "{spec.path}",' in source, spec.path
        assert "st.title(" not in source, spec.path


def test_headings_have_no_icons():
    offenders = []
    for path in sorted((APP / "views").glob("*.py")) + sorted((APP / "ui").glob("*.py")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "page_title" in line or line.lstrip().startswith("#"):
                continue
            if ICON_HEADING.search(line):
                offenders.append(f"{path.relative_to(APP).as_posix()}:{number}: {line.strip()}")
    assert offenders == [], "\n".join(offenders)
