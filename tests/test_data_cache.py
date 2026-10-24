"""Cache dos downloads na camada de interface e isolamento do core."""

import re
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

from app.ui import data_cache
from core import data_loader

ROOT = Path(__file__).resolve().parents[1]


def _history():
    return pd.DataFrame(
        {"Open": [1.0], "High": [1.0], "Low": [1.0], "Close": [1.0], "Volume": [10]},
        index=pd.DatetimeIndex(pd.to_datetime(["2024-01-02"]), name="Date"),
    )


@pytest.fixture(autouse=True)
def _fresh_cache(monkeypatch):
    monkeypatch.setattr(data_loader.time, "sleep", lambda *_: None)
    data_cache.clear_cache()
    yield
    data_cache.clear_cache()


def test_core_does_not_import_streamlit():
    offenders = [
        path.relative_to(ROOT).as_posix()
        for path in sorted((ROOT / "core").glob("*.py"))
        if re.search(r"^\s*(?:import|from)\s+streamlit\b", path.read_text(encoding="utf-8"), re.M)
    ]
    assert offenders == []


def test_successful_download_is_cached(monkeypatch):
    ticker = Mock()
    ticker.history.return_value = _history()
    factory = Mock(return_value=ticker)
    monkeypatch.setattr(data_loader.yf, "Ticker", factory)

    first = data_cache.download_active_data(" aapl ", "2024-01-01", "2024-01-31")
    second = data_cache.download_active_data("AAPL", "2024-01-01", "2024-01-31")

    assert len(first) == 1 and second.equals(first)
    factory.assert_called_once_with("AAPL")  # a segunda chamada vem do cache


def test_failure_is_not_cached(monkeypatch):
    """Falhas levantam DataUnavailable dentro da função cacheada e não ficam guardadas."""
    ticker = Mock()
    ticker.history.side_effect = [RuntimeError("falha"), RuntimeError("falha"), RuntimeError("falha"), _history()]
    monkeypatch.setattr(data_loader.yf, "Ticker", Mock(return_value=ticker))

    assert data_cache.download_active_data("NOCACHE", "2024-01-01", "2024-01-31") is None
    result = data_cache.download_active_data("NOCACHE", "2024-01-01", "2024-01-31")

    assert result is not None and len(result) == 1
    assert ticker.history.call_count == 4  # 3 tentativas da falha + nova consulta


def test_demo_mode_uses_cached_local_loader(monkeypatch):
    calls = []

    def fake_loader(symbol, start, end, interval, directory):
        calls.append((symbol, interval, directory))
        return pd.DataFrame({"Date": pd.to_datetime(["2024-01-02"]), "Close": [1.0]})

    monkeypatch.setattr(data_cache, "load_demo_frame", fake_loader)
    monkeypatch.setattr(data_loader, "is_demo_mode", lambda: True)

    first = data_cache.download_active_data("AAPL", "2024-01-01", "2024-01-31")
    second = data_cache.download_active_data("AAPL", "2024-01-01", "2024-01-31")

    assert first.equals(second)
    assert len(calls) == 1 and calls[0][:2] == ("AAPL", "1d")
