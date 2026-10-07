import pandas as pd
import pytest

from core.ticker_input import (
    is_valid_ticker_format,
    normalize_ticker,
    validate_ticker,
)


@pytest.mark.parametrize("ticker", ["AAPL", "PETR4.SA", "BRK-B", "BTC-USD", "^BVSP", "GC=F", "USDBRL=X"])
def test_valid_formats(ticker):
    assert is_valid_ticker_format(ticker)


@pytest.mark.parametrize("ticker", ["", "AAPL;DROP", "A/B", "ABCDEFGHIJKLMNOP", "..SA", "AAPL.", "$AAPL"])
def test_invalid_formats(ticker):
    assert not is_valid_ticker_format(ticker)


def test_normalize():
    assert normalize_ticker("  petr4 .sa ") == "PETR4.SA"
    assert normalize_ticker(None) == ""


def test_validate_ok():
    fetch = lambda t: pd.DataFrame({"Close": [1.0]})
    result = validate_ticker("aapl", fetch)
    assert result.ok and result.ticker == "AAPL"


def test_validate_empty_input():
    result = validate_ticker("   ", lambda t: None)
    assert not result.ok and "Digite" in result.message


def test_validate_bad_format_does_not_fetch():
    called = []
    result = validate_ticker("A/B", lambda t: called.append(t))
    assert not result.ok and called == []


@pytest.mark.parametrize("data", [None, pd.DataFrame()])
def test_validate_not_found(data):
    result = validate_ticker("XYZ", lambda t: data)
    assert not result.ok and "não encontrado" in result.message


def test_validate_source_failure():
    def boom(_):
        raise RuntimeError("rede")
    result = validate_ticker("AAPL", boom)
    assert not result.ok and "Tente novamente" in result.message