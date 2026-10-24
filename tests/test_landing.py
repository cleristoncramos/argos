from app.ui.landing import (
    ACADEMIC_INFO,
    TECHNOLOGIES,
    TOUR_VIDEO,
    build_academic_header_html,
    build_details_html,
    build_mosaic_html,
    build_people_html,
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
    for key in ("institution", "center", "course"):
        assert ACADEMIC_INFO[key] in html


def test_people_details_and_technologies():
    people = build_people_html()
    assert ACADEMIC_INFO["author"] in people and ACADEMIC_INFO["advisor"] in people
    assert ">CR<" in people and ">AA<" in people  # iniciais do primeiro e do último nome
    details = build_details_html()
    assert ACADEMIC_INFO["work_plan"] in details and "PIBITI" in details
    techs = build_technologies_html()
    assert techs.count('class="acad-tech"') == len(TECHNOLOGIES)


def test_tour_video_is_packaged():
    assert TOUR_VIDEO.exists() and TOUR_VIDEO.stat().st_size < 15 * 1_048_576
