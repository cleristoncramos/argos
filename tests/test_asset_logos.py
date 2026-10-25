from core.asset_logos import (
    CRYPTO_LOGO_BASE_URL,
    SPECIAL_LOGO_MAP,
    STOCK_LOGO_BASE_URL,
    _crypto_symbol_from_ticker,
    get_asset_logo_url,
)


def test_crypto_symbol_from_ticker():
    assert _crypto_symbol_from_ticker("BTC-USD") == "btc"
    assert _crypto_symbol_from_ticker("ETH-USD") == "eth"


def test_crypto_logo_url():
    logo_url = get_asset_logo_url(
        "BTC-USD",
        "crypto",
    )

    assert logo_url == (
        CRYPTO_LOGO_BASE_URL.format(
            symbol="btc",
        )
    )


def test_crypto_logo_url_is_case_insensitive():
    logo_url = get_asset_logo_url(
        "eth-usd",
        "crypto",
    )

    assert logo_url == (
        CRYPTO_LOGO_BASE_URL.format(
            symbol="eth",
        )
    )


def test_stock_logo_url():
    logo_url = get_asset_logo_url(
        "AAPL",
        "us_stocks",
    )

    assert logo_url == (
        STOCK_LOGO_BASE_URL.format(
            ticker="AAPL",
        )
    )


def test_stock_logo_url_is_case_insensitive():
    logo_url = get_asset_logo_url(
        "aapl",
        "us_stocks",
    )

    assert logo_url == (
        STOCK_LOGO_BASE_URL.format(
            ticker="AAPL",
        )
    )


def test_brazilian_stock_logo_url():
    logo_url = get_asset_logo_url(
        "PETR4.SA",
        "br_stocks",
    )

    assert logo_url == (
        STOCK_LOGO_BASE_URL.format(
            ticker="PETR4.SA",
        )
    )


def test_etf_logo_url():
    logo_url = get_asset_logo_url(
        "SPY",
        "equity_etfs",
    )

    assert logo_url == (
        STOCK_LOGO_BASE_URL.format(
            ticker="SPY",
        )
    )


def test_reit_logo_url():
    logo_url = get_asset_logo_url(
        "VNQ",
        "reits",
    )

    assert logo_url == (
        STOCK_LOGO_BASE_URL.format(
            ticker="VNQ",
        )
    )


def test_fii_without_logo_at_source_returns_none():
    logo_url = get_asset_logo_url(
        "MXRF11.SA",
        "brazil_fiis",
    )

    assert logo_url is None


def test_special_logo_map():
    logo_url = get_asset_logo_url(
        "EMBJ3.SA",
        "br_stocks",
    )

    assert logo_url == SPECIAL_LOGO_MAP["EMBJ3.SA"]


def test_crypto_symbol_override_and_b3_etfs_in_other_groups():
    assert _crypto_symbol_from_ticker("UNI7083-USD") == "uni"
    assert get_asset_logo_url("UNI7083-USD", "crypto") == CRYPTO_LOGO_BASE_URL.format(symbol="uni")
    # ETF da B3 classificado em outro grupo usa a fonte de ações.
    assert get_asset_logo_url("XYZW11.SA", "crypto") == STOCK_LOGO_BASE_URL.format(ticker="XYZW11.SA")


def test_indexes_without_special_mapping_return_none():
    logo_url = get_asset_logo_url(
        "^BVSP",
        "indexes",
    )

    assert logo_url is None


def test_forex_returns_none():
    logo_url = get_asset_logo_url(
        "USDBRL=X",
        "forex",
    )

    assert logo_url is None


def test_commodities_returns_none():
    logo_url = get_asset_logo_url(
        "GC=F",
        "commodities",
    )

    assert logo_url is None


def test_treasury_returns_none():
    logo_url = get_asset_logo_url(
        "^TNX",
        "treasury",
    )

    assert logo_url is None


def test_empty_group_returns_none():
    logo_url = get_asset_logo_url(
        "AAPL",
        "",
    )

    assert logo_url is None


def test_logo_url_is_cached():
    first_result = get_asset_logo_url(
        "AAPL",
        "us_stocks",
    )

    second_result = get_asset_logo_url(
        "AAPL",
        "us_stocks",
    )

    assert first_result == second_result
    assert get_asset_logo_url.cache_info().hits >= 1

def test_unavailable_source_logos_fall_back_to_icon():
    from core.asset_logos import UNAVAILABLE_LOGOS, get_asset_logo_url

    get_asset_logo_url.cache_clear()
    assert {"V", "QQQ", "KNRI11.SA", "GOLD11.SA", "HASH11.SA"} <= UNAVAILABLE_LOGOS
    for ticker in UNAVAILABLE_LOGOS:
        assert get_asset_logo_url(ticker, "us_stocks") is None
        assert get_asset_logo_url(ticker.lower(), "equity_etfs") is None
