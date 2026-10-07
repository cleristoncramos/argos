import io

import pandas as pd

from core.exports import UTF8_BOM, csv_filename, dataframe_to_csv_bytes


def _sample():
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(["2024-01-31", "2024-02-29"]),
            "Ativo": ["Ação", "Café"],
            "Value": [10.5, 11.25],
        }
    )


def test_csv_roundtrip_has_no_index_column():
    data = dataframe_to_csv_bytes(_sample())

    restored = pd.read_csv(io.BytesIO(data), parse_dates=["Date"])

    assert list(restored.columns) == ["Date", "Ativo", "Value"]
    assert restored["Value"].tolist() == [10.5, 11.25]
    assert restored["Date"].iloc[0] == pd.Timestamp("2024-01-31")


def test_csv_is_utf8_and_keeps_accents():
    data = dataframe_to_csv_bytes(_sample())

    assert isinstance(data, bytes)
    assert not data.startswith(UTF8_BOM)
    assert "Ação" in data.decode("utf-8")


def test_csv_default_matches_previous_page_behavior():
    df = _sample()

    assert dataframe_to_csv_bytes(df) == df.to_csv(index=False).encode("utf-8")


def test_csv_excel_brazil_options():
    data = dataframe_to_csv_bytes(_sample(), sep=";", decimal=",", bom=True)

    assert data.startswith(UTF8_BOM)
    lines = data.decode("utf-8-sig").splitlines()
    assert lines[0] == "Date;Ativo;Value"
    assert lines[1] == "2024-01-31;Ação;10,5"


def test_csv_none_and_empty_frame():
    assert dataframe_to_csv_bytes(None) == b""

    empty = pd.DataFrame(columns=["Date", "Value"])
    assert dataframe_to_csv_bytes(empty).decode("utf-8").strip() == "Date,Value"


def test_filename_for_plain_ticker():
    assert csv_filename("PETR4.SA", "dados_tratados") == "PETR4.SA_dados_tratados.csv"
    assert csv_filename("BRK-B", "risco_retorno") == "BRK-B_risco_retorno.csv"


def test_filename_cleans_index_and_forex_symbols():
    assert csv_filename("^BVSP", "indicadores") == "BVSP_indicadores.csv"
    assert csv_filename("USDBRL=X", "dados") == "USDBRL_X_dados.csv"


def test_filename_removes_accents_and_spaces():
    assert csv_filename("Comparação de ativos") == "Comparacao_de_ativos.csv"


def test_filename_without_usable_parts():
    assert csv_filename() == "dados.csv"
    assert csv_filename("", "  ", "^") == "dados.csv"


def test_filename_single_part_keeps_underscores():
    assert (
        csv_filename("comparacao_ativos_base_100")
        == "comparacao_ativos_base_100.csv"
    )