"""Testes das últimas linhas não cobertas de core/ (Fase 8).

Linhas fechadas por este arquivo:
- assets.py 331, 343, 351 (validate_catalog)
- data_loader.py 96, 119, 157 (MultiIndex, coluna Datetime, laço sem tentativas)
- indicator_docs.py 114 (get_indicator_doc)
- indicators_extra.py 43 (janela inválida da volatilidade móvel)
- data_availability.py 107 (aviso de dados terminando antes do pedido)
"""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from core import assets, data_loader
from core.data_availability import (
    assess_availability,
    availability_messages,
)
from core.indicator_docs import get_indicator_doc
from core.indicators_extra import add_atr, add_rolling_volatility


# ----------------------------------------------------------------------
# assets.validate_catalog
# ----------------------------------------------------------------------

def _copy_catalog():
    return [dict(asset) for asset in assets.ASSETS]


def test_validate_catalog_accepts_current_catalog():
    assets.validate_catalog()


def test_validate_catalog_rejects_wrong_size(monkeypatch):
    monkeypatch.setattr(assets, "ASSETS", _copy_catalog()[:-1])

    with pytest.raises(ValueError, match="120"):
        assets.validate_catalog()


def test_validate_catalog_rejects_duplicated_tickers(monkeypatch):
    broken = _copy_catalog()
    broken[-1]["ticker"] = broken[0]["ticker"]
    monkeypatch.setattr(assets, "ASSETS", broken)

    with pytest.raises(ValueError, match="duplicados"):
        assets.validate_catalog()


def test_validate_catalog_rejects_missing_fields(monkeypatch):
    broken = _copy_catalog()
    broken[0].pop("icon")
    monkeypatch.setattr(assets, "ASSETS", broken)

    with pytest.raises(ValueError, match="Campos ausentes"):
        assets.validate_catalog()


# ----------------------------------------------------------------------
# data_loader._download_active_data_cached
# ----------------------------------------------------------------------

OHLCV = ["Open", "High", "Low", "Close", "Volume"]


@pytest.fixture(autouse=True)
def _no_sleep_and_fresh_cache(monkeypatch):
    """Evita esperas dos retries e isola o cache entre testes."""
    monkeypatch.setattr(data_loader.time, "sleep", lambda *_: None)
    clear = getattr(data_loader._download_active_data_cached, "clear", None)
    if callable(clear):
        clear()
    yield


def _fake_ticker(frame):
    class FakeTicker:
        def __init__(self, symbol):
            self.symbol = symbol

        def history(self, **kwargs):
            return frame.copy()

    return FakeTicker


def test_download_flattens_multiindex_columns(monkeypatch):
    index = pd.DatetimeIndex(
        pd.date_range("2024-01-02", periods=3, freq="D"), name="Date"
    )
    columns = pd.MultiIndex.from_product([OHLCV, ["AAA"]])
    frame = pd.DataFrame(np.ones((3, 5)), index=index, columns=columns)
    monkeypatch.setattr(data_loader.yf, "Ticker", _fake_ticker(frame))

    result = data_loader._download_active_data_cached(
        "MULTIIDX", "2024-01-01", "2024-02-01", "1d"
    )

    assert list(result.columns) == ["Date", *OHLCV]
    assert len(result) == 3


def test_download_accepts_datetime_index_name(monkeypatch):
    index = pd.DatetimeIndex(
        pd.date_range(
            "2024-01-02 10:00", periods=3, freq="h", tz="America/Sao_Paulo"
        ),
        name="Datetime",
    )
    frame = pd.DataFrame(np.ones((3, 5)), index=index, columns=OHLCV)
    monkeypatch.setattr(data_loader.yf, "Ticker", _fake_ticker(frame))

    result = data_loader._download_active_data_cached(
        "INTRADAY", "2024-01-01", "2024-02-01", "1h"
    )

    assert "Date" in result.columns
    assert "Datetime" not in result.columns
    assert result["Date"].dt.tz is None
    assert len(result) == 3


def test_download_without_attempts_raises_data_unavailable():
    with pytest.raises(data_loader.DataUnavailable):
        data_loader._download_active_data_cached(
            "NOATTEMPTS", "2024-01-01", "2024-02-01", "1d", 0
        )


# ----------------------------------------------------------------------
# indicator_docs.get_indicator_doc
# ----------------------------------------------------------------------

def test_get_indicator_doc_returns_known_indicator():
    doc = get_indicator_doc("rsi")

    assert doc is not None
    assert doc.key == "rsi"
    assert doc.category == "Momentum"


def test_get_indicator_doc_unknown_key_returns_none():
    assert get_indicator_doc("inexistente") is None


# ----------------------------------------------------------------------
# indicators_extra: janelas inválidas
# ----------------------------------------------------------------------

def test_rolling_volatility_rejects_window_below_two():
    df = pd.DataFrame({"Value": [10.0, 11.0, 12.0]})

    with pytest.raises(ValueError, match="volatilidade"):
        add_rolling_volatility(df, window=1)


def test_atr_rejects_window_below_two():
    df = pd.DataFrame(
        {"High": [2.0, 3.0], "Low": [1.0, 2.0], "Close": [1.5, 2.5]}
    )

    with pytest.raises(ValueError, match="ATR"):
        add_atr(df, window=1)


# ----------------------------------------------------------------------
# data_availability: aviso de dados desatualizados no fim
# ----------------------------------------------------------------------

def test_availability_warns_when_data_ends_before_requested_end():
    dates = pd.date_range("2024-01-01", "2024-06-30", freq="D")
    availability = assess_availability(
        dates,
        requested_start=date(2024, 1, 1),
        requested_end=date(2024, 12, 31),
        period_observations=20,
    )

    assert availability.stale_end is True
    assert availability.shorter_history is False

    messages = availability_messages(availability)

    assert [level for level, _ in messages] == ["warning"]
    text = messages[0][1]
    assert "30/06/2024" in text
    assert "184 dias" in text
    assert "31/12/2024" in text