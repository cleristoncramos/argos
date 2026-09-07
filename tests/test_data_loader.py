from unittest.mock import Mock

import pandas as pd
import pytest

from core import data_loader
from core.data_loader import (
    _download_active_data_cached,
    download_active_data,
    validate_data,
)


@pytest.fixture
def uncached_download():
    """
    Retorna a implementação original da função cacheada, sem o wrapper
    do Streamlit. Assim, cada teste executa a lógica real sem reutilizar
    entradas de cache.
    """
    return _download_active_data_cached.__wrapped__


@pytest.fixture
def valid_history_dataframe() -> pd.DataFrame:
    """Retorna um histórico válido com datas fora de ordem e timezone."""
    index = pd.DatetimeIndex(
        pd.to_datetime(
            [
                "2024-01-03 00:00:00+00:00",
                "2024-01-01 00:00:00+00:00",
                "2024-01-02 00:00:00+00:00",
            ]
        ),
        name="Date",
    )

    return pd.DataFrame(
        {
            "Open": [103.0, 100.0, 101.0],
            "High": [104.0, 101.0, 102.0],
            "Low": [102.0, 99.0, 100.0],
            "Close": [103.5, 100.5, 101.5],
            "Volume": [300, 100, 200],
        },
        index=index,
    )


def build_ticker(
    info: dict | None = None,
    history: pd.DataFrame | None = None,
    info_error: Exception | None = None,
    history_error: Exception | None = None,
) -> Mock:
    """Cria um ticker simulado com comportamento configurável."""
    ticker = Mock()

    if info_error is not None:
        type(ticker).info = property(
            lambda _instance: (_ for _ in ()).throw(info_error)
        )
    else:
        type(ticker).info = property(
            lambda _instance: info or {}
        )

    if history_error is not None:
        ticker.history.side_effect = history_error
    else:
        ticker.history.return_value = (
            history
            if history is not None
            else pd.DataFrame()
        )

    return ticker


def test_download_normalizes_arguments_before_cached_call(
    monkeypatch,
):
    cached_download = Mock(
        return_value="resultado-simulado",
    )

    monkeypatch.setattr(
        data_loader,
        "_download_active_data_cached",
        cached_download,
    )

    result = download_active_data(
        symbol=" aapl ",
        start_date=" 2024-01-01 ",
        end_date=" 2024-01-31 ",
        interval=" 1D ",
    )

    assert result == "resultado-simulado"

    cached_download.assert_called_once_with(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-31",
        interval="1d",
    )


def test_download_returns_none_for_empty_symbol(
    monkeypatch,
):
    cached_download = Mock()

    monkeypatch.setattr(
        data_loader,
        "_download_active_data_cached",
        cached_download,
    )

    result = download_active_data(
        symbol="   ",
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    assert result is None
    cached_download.assert_not_called()


def test_cached_download_returns_valid_dataframe(
    monkeypatch,
    uncached_download,
    valid_history_dataframe,
):
    ticker = build_ticker(
        info={"symbol": "AAPL"},
        history=valid_history_dataframe,
    )

    ticker_factory = Mock(
        return_value=ticker,
    )

    monkeypatch.setattr(
        data_loader.yf,
        "Ticker",
        ticker_factory,
    )

    result = uncached_download(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-31",
        interval="1d",
    )

    assert result is not None
    assert not result.empty
    assert list(result["Date"]) == sorted(result["Date"].tolist())
    assert result["Date"].dt.tz is None

    expected_columns = {
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    }

    assert expected_columns.issubset(
        result.columns
    )

    ticker_factory.assert_called_once_with(
        "AAPL"
    )

    ticker.history.assert_called_once_with(
        start="2024-01-01",
        end="2024-01-31",
        interval="1d",
        auto_adjust=False,
    )


def test_cached_download_returns_none_when_ticker_has_no_identity(
    monkeypatch,
    uncached_download,
    valid_history_dataframe,
):
    ticker = build_ticker(
        info={},
        history=valid_history_dataframe,
    )

    monkeypatch.setattr(
        data_loader.yf,
        "Ticker",
        Mock(return_value=ticker),
    )

    result = uncached_download(
        symbol="INVALID",
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    assert result is None
    ticker.history.assert_not_called()


def test_cached_download_returns_none_when_info_access_fails(
    monkeypatch,
    uncached_download,
    valid_history_dataframe,
):
    ticker = build_ticker(
        history=valid_history_dataframe,
        info_error=RuntimeError(
            "Falha ao obter informações",
        ),
    )

    monkeypatch.setattr(
        data_loader.yf,
        "Ticker",
        Mock(return_value=ticker),
    )

    result = uncached_download(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    assert result is None
    ticker.history.assert_not_called()


@pytest.mark.parametrize(
    "history",
    [
        pd.DataFrame(),
        pd.DataFrame(
            {
                "Open": [100.0],
                "High": [101.0],
                "Low": [99.0],
                "Close": [100.5],
            },
            index=pd.DatetimeIndex(
                pd.to_datetime(
                    [
                        "2024-01-01",
                    ]
                ),
                name="Date",
            ),
        ),
    ],
)
def test_cached_download_returns_none_for_empty_or_incomplete_history(
    monkeypatch,
    uncached_download,
    history,
):
    ticker = build_ticker(
        info={"symbol": "AAPL"},
        history=history,
    )

    monkeypatch.setattr(
        data_loader.yf,
        "Ticker",
        Mock(return_value=ticker),
    )

    result = uncached_download(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    assert result is None


def test_cached_download_returns_none_without_date_or_datetime_column(
    monkeypatch,
    uncached_download,
):
    history = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [101.0],
            "Low": [99.0],
            "Close": [100.5],
            "Volume": [1000],
        }
    )

    ticker = build_ticker(
        info={"symbol": "AAPL"},
        history=history,
    )

    monkeypatch.setattr(
        data_loader.yf,
        "Ticker",
        Mock(return_value=ticker),
    )

    result = uncached_download(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    assert result is None


def test_cached_download_returns_none_when_history_raises_exception(
    monkeypatch,
    uncached_download,
):
    ticker = build_ticker(
        info={"symbol": "AAPL"},
        history_error=RuntimeError(
            "Falha de rede simulada",
        ),
    )

    monkeypatch.setattr(
        data_loader.yf,
        "Ticker",
        Mock(return_value=ticker),
    )

    result = uncached_download(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-31",
    )

    assert result is None


def test_validate_data_returns_expected_indicators():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-02",
                ]
            ),
            "Close": [
                100.0,
                -10.0,
                None,
            ],
            "Volume": [
                100,
                None,
                300,
            ],
        }
    )

    result = validate_data(
        df
    )

    assert result == {
        "total_rows": 3,
        "missing_values": {
            "Date": 0,
            "Close": 1,
            "Volume": 1,
        },
        "duplicate_dates": 1,
        "negative_close": 1,
        "has_data": True,
    }


@pytest.mark.parametrize(
    "df",
    [
        None,
        pd.DataFrame(),
    ],
)
def test_validate_data_handles_none_or_empty_dataframe(
    df,
):
    result = validate_data(
        df
    )

    assert result == {
        "total_rows": 0,
        "missing_values": {},
        "duplicate_dates": 0,
        "negative_close": 0,
        "has_data": False,
    }


def test_validate_data_handles_missing_date_and_close_columns():
    df = pd.DataFrame(
        {
            "Value": [
                100.0,
                110.0,
            ]
        }
    )

    result = validate_data(
        df
    )

    assert result["total_rows"] == 2
    assert result["duplicate_dates"] == 0
    assert result["negative_close"] == 0
    assert result["has_data"] is True