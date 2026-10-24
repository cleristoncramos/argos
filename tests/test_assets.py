import pytest

from core.assets import (
    ASSETS,
    ASSET_BY_TICKER,
    get_asset,
    get_assets,
    get_hierarchy,
    get_tickers,
    validate_catalog,
)


def test_catalog_has_120_assets():
    assert len(ASSETS) == 120


def test_catalog_has_unique_tickers():
    tickers = [
        asset["ticker"]
        for asset in ASSETS
    ]

    assert len(tickers) == len(set(tickers))


def test_catalog_validation_passes():
    validate_catalog()


def test_asset_has_required_metadata():
    required_fields = {
        "ticker",
        "name",
        "class",
        "subcategory",
        "market",
        "description",
        "group",
        "icon",
        "category_color",
        "data_type",
    }

    for asset in ASSETS:
        assert required_fields.issubset(asset.keys())


def test_get_asset_returns_expected_asset():
    asset = get_asset("NVDA")

    assert asset is not None
    assert asset["ticker"] == "NVDA"
    assert asset["name"] == "Nvidia"
    assert asset["class"] == "Ação"
    assert asset["subcategory"] == "Semicondutores"
    assert asset["data_type"] == "stock"


def test_get_asset_returns_none_for_unknown_ticker():
    assert get_asset("TICKER-INEXISTENTE") is None


def test_get_asset_returns_copy():
    asset = get_asset("BTC-USD")

    assert asset is not None

    asset["name"] = "Nome alterado"

    assert ASSET_BY_TICKER["BTC-USD"]["name"] == "Bitcoin"


def test_get_assets_filters_by_class():
    crypto_assets = get_assets(
        asset_class="Criptomoeda",
    )

    assert len(crypto_assets) == 10
    assert all(
        asset["class"] == "Criptomoeda"
        for asset in crypto_assets
    )


def test_get_assets_filters_by_subcategory():
    technology_assets = get_assets(
        asset_class="Ação",
        subcategory="Tecnologia",
        market="EUA",
    )

    tickers = {
        asset["ticker"]
        for asset in technology_assets
    }

    assert {"AAPL", "MSFT", "GOOGL", "META"}.issubset(
        tickers
    )


def test_get_assets_filters_by_data_type():
    crypto_assets = get_assets(
        data_type="crypto",
    )

    assert len(crypto_assets) == 10
    assert all(
        asset["data_type"] == "crypto"
        for asset in crypto_assets
    )


def test_get_assets_filters_by_group():
    commodity_assets = get_assets(
        group="commodities",
    )

    assert len(commodity_assets) == 14
    assert all(
        asset["group"] == "commodities"
        for asset in commodity_assets
    )


def test_get_assets_with_no_match_returns_empty_list():
    result = get_assets(
        asset_class="Ação",
        market="Mercado inexistente",
    )

    assert result == []


def test_get_tickers_from_default_catalog():
    tickers = get_tickers()

    assert len(tickers) == 120
    assert "BTC-USD" in tickers
    assert "PETR4.SA" in tickers
    assert "^TNX" in tickers


def test_get_tickers_from_custom_assets():
    selected_assets = [
        {
            "ticker": "AAPL",
        },
        {
            "ticker": "NVDA",
        },
    ]

    assert get_tickers(selected_assets) == [
        "AAPL",
        "NVDA",
    ]


def test_get_hierarchy_contains_expected_levels():
    hierarchy = get_hierarchy()

    assert "Ação" in hierarchy
    assert "Tecnologia" in hierarchy["Ação"]
    assert "EUA" in hierarchy["Ação"]["Tecnologia"]


def test_get_hierarchy_contains_nvda():
    hierarchy = get_hierarchy()

    semiconductor_us_assets = hierarchy[
        "Ação"
    ][
        "Semicondutores"
    ][
        "EUA"
    ]

    tickers = {
        asset["ticker"]
        for asset in semiconductor_us_assets
    }

    assert "NVDA" in tickers


def test_get_hierarchy_returns_copies():
    hierarchy = get_hierarchy()

    hierarchy["Criptomoeda"][
        "Cripto principal"
    ][
        "Global"
    ][0]["name"] = "Nome alterado"

    assert get_asset("BTC-USD")["name"] == "Bitcoin"

# ---------- filtros encadeados da Comparação (grupo, subclasse, mercado) ----------

def test_filter_assets_ignores_empty_filters():
    from core.assets import ASSETS, filter_assets

    assert len(filter_assets(ASSETS, group=None, market=None)) == len(ASSETS)
    tickers = [a["ticker"] for a in filter_assets(ASSETS, group="commodities", subcategory="Metal precioso")]
    assert tickers == ["GC=F", "SI=F", "PL=F"]


def test_facet_values_depend_on_the_other_filters():
    from core.assets import ASSETS, facet_values

    markets = facet_values(ASSETS, "market", group="commodities")
    assert markets == ["EUA/CBOT", "EUA/COMEX", "EUA/ICE", "EUA/NYMEX", "Global/ICE"]
    # Com o mercado escolhido, só sobram subclasses existentes nesse mercado
    assert facet_values(ASSETS, "subcategory", group="commodities", market="EUA/COMEX") == [
        "Metal industrial",
        "Metal precioso",
    ]
    # O filtro do próprio campo é ignorado (a lista não encolhe para um item)
    assert facet_values(ASSETS, "market", group="commodities", market="EUA/COMEX") == markets


def test_every_facet_combination_has_assets():
    from core.assets import ASSETS, ASSET_GROUPS, facet_values, filter_assets

    for group in (g["key"] for g in ASSET_GROUPS):
        for subclass in facet_values(ASSETS, "subcategory", group=group):
            for market in facet_values(ASSETS, "market", group=group, subcategory=subclass):
                assert filter_assets(ASSETS, group=group, subcategory=subclass, market=market)


def test_single_market_groups_hide_the_market_filter():
    from core.assets import ASSETS, facet_values

    # Grupos com um só mercado não exibem o filtro (a página só mostra com 2+ opções)
    for group in ("crypto", "br_stocks", "us_stocks", "fixed_income_etfs", "reits", "brazil_fiis", "forex", "treasury"):
        assert len(facet_values(ASSETS, "market", group=group)) == 1
    for group in ("europe_stocks", "asia_stocks", "equity_etfs", "indexes", "commodities"):
        assert len(facet_values(ASSETS, "market", group=group)) > 1
