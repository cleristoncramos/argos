"""Ordem das páginas: menu principal, "Primeiros passos" e Get Started alinhados."""

from pathlib import Path

from app.ui.pages import HOME_PAGE, MENU_PAGES, START_PAGE

APP = Path(__file__).resolve().parents[1] / "app"


def test_menu_order_puts_analyses_first_and_about_last():
    assert [p.title for p in MENU_PAGES] == [
        "Análise Individual",
        "Comparação de Ativos",
        "Indicadores Técnicos",
        "Risco e Retorno",
        "Simulação de Aportes",
        "Panorama do Catálogo",
        "Sobre o Projeto",
    ]


def test_get_started_opens_the_first_menu_page():
    assert START_PAGE is MENU_PAGES[0]
    assert START_PAGE.path == "views/analise_individual.py"


def test_every_page_file_exists_and_has_a_description():
    for spec in (HOME_PAGE, *MENU_PAGES):
        assert (APP / spec.path).exists(), spec.path
    assert all(spec.description for spec in MENU_PAGES)
    assert len({spec.path for spec in MENU_PAGES}) == len(MENU_PAGES)


def test_menu_and_home_are_built_from_the_same_list():
    main = (APP / "main.py").read_text(encoding="utf-8")
    home = (APP / "views" / "home.py").read_text(encoding="utf-8")
    assert "for spec in MENU_PAGES" in main and '"Menu Principal": [home_page, *menu_pages]' in main
    assert "ANALYSIS_PAGES[index]" in home and "st.switch_page(START_PAGE.path)" in home
    # Nenhuma das duas telas mantém uma lista própria de páginas
    for title in ("Sobre o Projeto", "Simulação de Aportes"):
        assert f'title="{title}"' not in main
        assert f'"{title}"' not in home
