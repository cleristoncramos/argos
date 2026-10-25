"""Conteúdo da página Sobre o Projeto (app/ui/about.py)."""

import re

from app.ui import about
from app.ui.landing import ACADEMIC_INFO, catalog_stats
from app.ui.pages import ANALYSIS_PAGES, MENU_PAGES
from core.assets import ASSET_GROUPS, ASSETS


def _page_html() -> str:
    stats = catalog_stats(ASSETS)
    return "".join((
        about.build_hero_html(stats),
        about.build_context_html(),
        about.build_research_html(),
        about.build_modules_html(),
        about.build_methodology_html(),
        about.build_data_html(stats, about.group_counts(ASSETS, ASSET_GROUPS)),
        about.build_quality_html(),
        about.build_team_html(),
        about.build_disclaimer_html(),
    ))


def test_page_no_longer_has_the_welcome_banner_or_inaccurate_claims():
    html = _page_html()
    assert "Bem-vindo" not in html
    assert "menu lateral esquerdo" not in html
    assert "tempo real" not in html.replace("Dados em tempo real: as séries são históricas", "")


def test_research_section_is_a_short_overview():
    html = about.build_research_html()
    assert about.RESEARCH_AIM in html
    assert html.count('class="ab-card"') == len(about.RESEARCH_GOALS)
    for title, _ in about.RESEARCH_GOALS:
        assert title in html
    assert "aprendizado de máquina" in html
    # Sem pergunta fechada nem situação de cada objetivo.
    assert "Pergunta de pesquisa" not in html
    assert "Situação" not in html


def test_modules_follow_the_menu_order():
    html = about.build_modules_html()
    positions = [html.index(spec.title) for spec in ANALYSIS_PAGES]
    assert positions == sorted(positions)
    assert set(about.MODULE_DETAILS) == {spec.path for spec in ANALYSIS_PAGES}
    # A própria página Sobre o Projeto não tem cartão na seção de módulos.
    assert MENU_PAGES[-1].title not in html


def test_catalog_numbers_come_from_the_catalog():
    groups = about.group_counts(ASSETS, ASSET_GROUPS)
    assert len(groups) == len(ASSET_GROUPS)
    assert sum(count for _, _, count in groups) == len(ASSETS)
    html = about.build_data_html(catalog_stats(ASSETS), groups)
    assert html.count('class="ab-group"') == len(ASSET_GROUPS)


def test_team_section_uses_the_academic_record():
    html = about.build_team_html()
    for key in ("institution", "center", "course", "author", "advisor"):
        assert ACADEMIC_INFO[key] in html


def test_about_css_has_no_rounded_corners():
    radii = re.findall(r"border-radius\s*:\s*([^;}\s]+)", about.ABOUT_CSS)
    assert all(value in ("0", "0!important") for value in radii), radii
