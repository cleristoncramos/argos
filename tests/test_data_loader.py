from unittest.mock import Mock, patch

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
    history_return: pd.DataFrame | None = None,
    history_side_effect: list | Exception | None = None,
) -> Mock:
    """Cria um ticker simulado com comportamento configurável."""
    ticker = Mock()

    if history_side_effect is not None:
        ticker.history.side_effect = history_side_effect
    else:
        ticker.history.return_value = (
            history_return if history_return is not None else pd.DataFrame()
        )

    return ticker


def test_download_normalizes_arguments_before_cached_call(monkeypatch):
    """Garante que a função pública de download ajusta a data final e normaliza os dados."""
    cached_download = Mock(return_value="resultado-simulado")

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

    # A data_end deve ter somado 1 dia automaticamente (2024-02-01)
    cached_download.assert_called_once_with(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-02-01",
        interval="1d",
    )


def test_download_returns_none_for_empty_symbol(monkeypatch):
    """Testa se rejeita símbolos vazios imediatamente."""
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
    """Testa o caminho feliz onde o download histórico ocorre com sucesso."""
    ticker = build_ticker(history_return=valid_history_dataframe)
    ticker_factory = Mock(return_value=ticker)

    monkeypatch.setattr(data_loader.yf, "Ticker", ticker_factory)

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
    assert expected_columns.issubset(result.columns)

    ticker_factory.assert_called_once_with("AAPL")
    ticker.history.assert_called_once_with(
        start="2024-01-01",
        end="2024-01-31",
        interval="1d",
        auto_adjust=False,
    )


@patch("core.data_loader.time.sleep")
def test_cached_download_retries_and_returns_none_when_history_raises_exception(
    mock_sleep,
    monkeypatch,
    uncached_download,
):
    """Testa o retry da API se houver falha de rede/exceção. Deve retornar None após exceder tentativas."""
    ticker = build_ticker(
        history_side_effect=RuntimeError("Falha de rede simulada")
    )
    monkeypatch.setattr(data_loader.yf, "Ticker", Mock(return_value=ticker))

    # Passamos max_retries=2 explícito para testar o limite
    result = uncached_download(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-31",
        max_retries=2
    )

    assert result is None
    assert ticker.history.call_count == 2
    mock_sleep.assert_called_once()  # Dorme apenas 1 vez (entre as 2 tentativas)


@patch("core.data_loader.time.sleep")
def test_cached_download_recovers_after_exception(
    mock_sleep,
    monkeypatch,
    uncached_download,
    valid_history_dataframe
):
    """Garante que a função consegue se recuperar e entregar o DataFrame se falhar na primeira vez."""
    # Retorna Erro na 1ª chamada, DataFrame válido na 2ª chamada
    ticker = build_ticker(
        history_side_effect=[RuntimeError("Erro intermitente"), valid_history_dataframe]
    )
    monkeypatch.setattr(data_loader.yf, "Ticker", Mock(return_value=ticker))

    result = uncached_download(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-31",
        max_retries=3
    )

    assert result is not None
    assert len(result) == 3
    assert ticker.history.call_count == 2


@patch("core.data_loader.time.sleep")
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
                pd.to_datetime(["2024-01-01"]),
                name="Date",
            ),
        ),
    ],
)
def test_cached_download_returns_none_for_empty_or_incomplete_history(
    mock_sleep,
    monkeypatch,
    uncached_download,
    history,
):
    """Testa se rejeita DataFrames vazios ou faltando colunas e gasta as tentativas."""
    ticker = build_ticker(history_return=history)
    monkeypatch.setattr(data_loader.yf, "Ticker", Mock(return_value=ticker))

    result = uncached_download(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-31",
        max_retries=2
    )

    assert result is None
    assert ticker.history.call_count == 2


@patch("core.data_loader.time.sleep")
def test_cached_download_returns_none_without_date_or_datetime_column(
    mock_sleep,
    monkeypatch,
    uncached_download,
):
    """Garante rejeição quando não há coluna de índice temporal detectável."""
    history = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [101.0],
            "Low": [99.0],
            "Close": [100.5],
            "Volume": [1000],
        }
    )
    ticker = build_ticker(history_return=history)
    monkeypatch.setattr(data_loader.yf, "Ticker", Mock(return_value=ticker))

    result = uncached_download(
        symbol="AAPL",
        start_date="2024-01-01",
        end_date="2024-01-31",
        max_retries=1
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

    result = validate_data(df)

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
def test_validate_data_handles_none_or_empty_dataframe(df):
    result = validate_data(df)

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

    result = validate_data(df)

    assert result["total_rows"] == 2
    assert result["duplicate_dates"] == 0
    assert result["negative_close"] == 0
    assert result["has_data"] is True