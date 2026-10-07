import pytest

from core.currency import currency_info, is_crypto


@pytest.mark.parametrize(
    "ticker, code, prefix",
    [
        ("PETR4.SA", "BRL", "R$ "),
        ("AAPL", "USD", "US$ "),
        ("NESN.SW", "CHF", "CHF "),
        ("MC.PA", "EUR", "€ "),
        ("SIE.DE", "EUR", "€ "),
        ("NOVO-B.CO", "DKK", "DKK "),
        ("005930.KS", "KRW", "₩ "),
        ("0700.HK", "HKD", "HK$ "),
        ("7203.T", "JPY", "¥ "),
        ("BTC-USD", "USD", "US$ "),
        ("GC=F", "USD", "US$ "),
        ("^BVSP", "PTS", "Pts "),
        ("000001.SS", "PTS", "Pts "),
        ("USDBRL=X", "FX", ""),
        ("^TNX", "PCT", ""),
        (" petr4.sa ", "BRL", "R$ "),
    ],
)
def test_currency_info(ticker, code, prefix):
    info = currency_info(ticker)
    assert info.code == code
    assert info.prefix == prefix


def test_kinds():
    assert currency_info("^TNX").kind == "rate"
    assert currency_info("^GSPC").kind == "points"
    assert currency_info("EURUSD=X").kind == "fx"
    assert currency_info("AAPL").kind == "price"


def test_is_crypto():
    assert is_crypto("BTC-USD")
    assert not is_crypto("BRK-B")
    assert not is_crypto(None)