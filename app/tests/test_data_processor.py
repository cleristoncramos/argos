import pandas as pd

from core.data_processor import (
    prepare_dataframe,
    aggregate_by_frequency,
    select_primary_variable,
)


def create_sample_dataframe():
    """
    Cria dados sintéticos pequenos e previsíveis.
    Esses dados não dependem de internet.
    """
    return pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2020-01-30",
                    "2020-01-31",
                    "2020-02-03",
                    "2020-02-28",
                    "2020-03-02",
                    "2020-03-31",
                ]
            ),
            "Open": [9000, 9100, 9200, 9300, 9400, 9500],
            "High": [9150, 9250, 9350, 9450, 9550, 9650],
            "Low": [8900, 9000, 9100, 9200, 9300, 9400],
            "Close": [9100, 9200, 9300, 9400, 9500, 9600],
            "Volume": [100, 110, 120, 130, 140, 150],
        }
    )


def test_prepare_dataframe_creates_derived_columns():
    df = create_sample_dataframe()

    result = prepare_dataframe(df)

    expected_columns = {
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Year",
        "Month",
        "YearMonth",
    }

    assert expected_columns.issubset(result.columns)
    assert result["Date"].is_monotonic_increasing
    assert result["Year"].tolist() == [2020, 2020, 2020, 2020, 2020, 2020]
    assert result["Month"].tolist() == [1, 1, 2, 2, 3, 3]
    assert result["YearMonth"].tolist() == [
        "2020-01",
        "2020-01",
        "2020-02",
        "2020-02",
        "2020-03",
        "2020-03",
    ]


def test_daily_aggregation_keeps_all_rows():
    df = prepare_dataframe(create_sample_dataframe())

    result = aggregate_by_frequency(df, "Diário")

    assert len(result) == len(df)
    assert "YearMonth" in result.columns


def test_monthly_aggregation_keeps_last_close():
    """
    Confirma o comportamento definido no projeto:
    cada mês usa o último fechamento disponível.
    """
    df = prepare_dataframe(create_sample_dataframe())

    result = aggregate_by_frequency(df, "Mensal")

    assert len(result) == 3
    assert "YearMonth" in result.columns
    assert result["Close"].tolist() == [9200, 9400, 9600]
    assert result["Month"].tolist() == [1, 2, 3]
    assert result["Year"].tolist() == [2020, 2020, 2020]


def test_weekly_aggregation_returns_expected_columns():
    df = prepare_dataframe(create_sample_dataframe())

    result = aggregate_by_frequency(df, "Semanal")

    expected_columns = {
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Year",
        "Month",
        "YearMonth",
    }

    assert not result.empty
    assert expected_columns.issubset(result.columns)


def test_select_primary_variable_creates_value_column():
    df = prepare_dataframe(create_sample_dataframe())

    result = select_primary_variable(df, "Close")

    expected_columns = {
        "Date",
        "Value",
        "Year",
        "Month",
        "YearMonth",
    }

    assert expected_columns.issubset(result.columns)
    assert result["Value"].tolist() == [9100, 9200, 9300, 9400, 9500, 9600]


def test_select_primary_variable_raises_error_for_missing_column():
    df = prepare_dataframe(create_sample_dataframe())

    try:
        select_primary_variable(df, "ColunaInexistente")
        assert False, "A função deveria gerar erro para uma coluna inexistente."
    except ValueError as error:
        assert "Colunas obrigatórias ausentes" in str(error)