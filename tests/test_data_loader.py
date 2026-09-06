import pandas as pd

from core.data_loader import download_active_data, validate_data


def test_download_btc_data():
    """
    Verifica se a aplicação consegue baixar dados históricos
    do Bitcoin e se as colunas essenciais existem.
    """
    df = download_active_data(
        symbol="BTC-USD",
        start_date="2020-01-01",
        end_date="2020-12-31",
        interval="1d"
    )

    assert df is not None, "O download retornou None."
    assert not df.empty, "O DataFrame retornado está vazio."

    expected_columns = {"Date", "Open", "High", "Low", "Close", "Volume"}
    actual_columns = set(df.columns)

    missing_columns = expected_columns - actual_columns

    assert not missing_columns, (
        f"Colunas ausentes no download: {missing_columns}. "
        f"Colunas recebidas: {list(df.columns)}"
    )

    assert pd.api.types.is_datetime64_any_dtype(df["Date"]), (
        "A coluna Date deveria estar no tipo datetime."
    )


def test_validate_downloaded_data():
    """
    Verifica se a função de validação retorna os indicadores esperados.
    """
    df = download_active_data(
        symbol="BTC-USD",
        start_date="2020-01-01",
        end_date="2020-01-31",
        interval="1d"
    )

    assert df is not None
    assert not df.empty

    validation = validate_data(df)

    expected_keys = {
        "total_rows",
        "missing_values",
        "duplicate_dates",
        "negative_close",
        "has_data"
    }

    assert expected_keys.issubset(validation.keys())
    assert validation["has_data"] is True
    assert validation["total_rows"] > 0
    assert validation["duplicate_dates"] == 0
    assert validation["negative_close"] == 0


def test_invalid_symbol_returns_none():
    """
    Verifica se um símbolo inexistente é tratado sem encerrar a aplicação.
    """
    df = download_active_data(
        symbol="SIMBOLO-INEXISTENTE-XYZ",
        start_date="2020-01-01",
        end_date="2020-01-31",
        interval="1d"
    )

    assert df is None or df.empty