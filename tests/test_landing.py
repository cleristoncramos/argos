import re

from app.ui.design import GLOBAL_CSS
from app.ui.landing import (
    ACADEMIC_INFO,
    ACADEMIC_MODAL_CSS,
    DATA_SOURCES,
    FEATURES_VIDEO,
    MOSAIC_TEMPLATE,
    TECHNOLOGIES,
    build_academic_header_html,
    build_data_sources_html,
    build_identification_html,
    build_mosaic_html,
    build_technologies_html,
    catalog_stats,
    institutional_logo_uri,
)
from core.assets import ASSETS


def _logo(ticker, group):
    return f"https://logos.example/{ticker}.png" if group == "crypto" else None


def test_mosaic_has_every_asset_twice_and_escapes_text():
    assets = [
        {"ticker": "BTC-USD", "name": "Bitcoin", "class": "Criptomoeda", "group": "crypto",
         "icon": "₿", "category_color": "#F59E0B"},
        {"ticker": "X<1>", "name": "<script>alert(1)</script>", "class": "Ação", "group": "us_stocks",
         "icon": "📈", "category_color": "#2563EB"},
    ]
    html = build_mosaic_html(assets, _logo, rows=1)
    # Cada faixa é duplicada para o laço contínuo da animação.
    assert html.count(">BTC-USD<") == 2
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
    assert "https://logos.example/BTC-USD.png" in html
    assert "onerror=" in html  # monograma assume se o logo remoto falhar


def test_mosaic_spreads_the_full_catalog_across_lanes():
    html = build_mosaic_html(ASSETS, lambda t, g: None, rows=3)
    assert html.count('class="lane"') == 3
    assert html.count('class="tile"') == 2 * len(ASSETS)


def test_catalog_stats():
    stats = catalog_stats(ASSETS)
    assert stats["assets"] == len(ASSETS)
    assert stats["classes"] >= 5
    assert stats["groups"] >= stats["classes"]


def test_institutional_logos_are_packaged():
    for name in ("UFPI", "CEAD"):
        uri = institutional_logo_uri(name)
        assert uri and uri.startswith("data:image/")
    assert institutional_logo_uri("NAO_EXISTE") is None


def test_academic_header_lists_institution_center_and_course():
    html = build_academic_header_html({"UFPI": "data:image/svg+xml;base64,AA", "CEAD": None})
    assert html.count("<img") == 1
    for key in ("institution", "center", "course", "system"):
        assert ACADEMIC_INFO[key] in html


def test_identification_has_author_advisor_and_program():
    html = build_identification_html()
    for key in ("author", "advisor", "work_plan", "program", "course", "center"):
        assert ACADEMIC_INFO[key] in html


def test_modal_is_sober_without_mythology():
    """Opção A do nome (24/10/2026): sem 'DataLab' e sem a analogia mitológica."""
    html = "".join((
        build_academic_header_html({}),
        build_identification_html(),
        build_technologies_html(),
        build_data_sources_html(catalog_stats(ASSETS)),
    ))
    assert ACADEMIC_INFO["system"] == "Argos"
    assert "Plataforma de Análise Histórica de Ativos Financeiros" in html
    for term in ("DataLab", "Velocino", "Argonauta", "mitologia", "Jasão"):
        assert term not in html


def test_technologies_and_data_sources_tables():
    assert build_technologies_html().count("<tr>") == len(TECHNOLOGIES) + 1
    html = build_data_sources_html(catalog_stats(ASSETS))
    assert html.count("<tr>") == len(DATA_SOURCES) + 1
    assert "Yahoo Finance" in html and str(len(ASSETS)) in html


def test_no_rounded_corners_in_own_styles():
    for css in (GLOBAL_CSS, ACADEMIC_MODAL_CSS, MOSAIC_TEMPLATE):
        radii = re.findall(r"border-radius\s*:\s*([^;}\s]+)", css)
        assert all(value in ("0", "0!important") for value in radii), radii


def test_features_video_is_packaged():
    assert FEATURES_VIDEO.exists() and FEATURES_VIDEO.stat().st_size < 15 * 1_048_576


def test_mosaic_shows_logo_ticker_and_name_without_group_badge():
    asset = {"ticker": "PETR4.SA", "name": "Petrobras PN", "class": "Ação", "group": "br_stocks",
             "icon": "📈", "category_color": "#2563EB"}
    html = build_mosaic_html([asset], lambda t, g: "https://logos.example/p.png", rows=1)
    assert ">PETR4.SA<" in html and ">Petrobras PN<" in html
    assert 'class="cls"' not in html and ">Ação<" not in html
