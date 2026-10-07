import pandas as pd
import pytest

from core.comparison import (
    build_base_100_table,
    build_price_table,
    calculate_correlation_matrix,
    calculate_returns_table,
    create_comparison_summary,
    format_return_pct,
    normalize_to_base_100,
    parse_symbols,
)


def create_asset_data():
    """
    Cria duas séries pequenas com datas parcialmente diferentes.

    BTC possui três datas consecutivas.
    AAPL começa no segundo dia, simulando calendários diferentes.
    """
    btc = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                ]
            ),
            "Value": [
                100.0,
                110.0,
                121.0,
            ],
            "Simple_Return": [
                None,
                0.10,
                0.10,
            ],
        }
    )

    aapl = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                ]
            ),
            "Value": [
                50.0,
                55.0,
                60.0,
            ],
            "Simple_Return": [
                None,
                0.10,
                0.0909090909,
            ],
        }
    )

    return {
        "BTC-USD": btc,
        "AAPL": aapl,
    }


def test_parse_symbols_normalizes_and_removes_duplicates():
    result = parse_symbols(
        " btc-usd, AAPL, btc-usd "
    )

    assert result == [
        "BTC-USD",
        "AAPL",
    ]


def test_parse_symbols_requires_at_least_two_assets():
    with pytest.raises(
        ValueError,
        match="pelo menos 2 ativos",
    ):
        parse_symbols("BTC-USD")


def test_parse_symbols_limits_to_five_assets():
    with pytest.raises(
        ValueError,
        match="no máximo 5 ativos",
    ):
        parse_symbols(
            "BTC-USD,AAPL,SPY,MSFT,USD=BRL,GC=F"
        )


def test_normalize_to_base_100():
    df = pd.DataFrame(
        {
            "Value": [
                50.0,
                55.0,
                60.0,
            ]
        }
    )

    result = normalize_to_base_100(df)

    assert result["Base_100"].tolist() == pytest.approx(
        [100.0, 110.0, 120.0]
    )


def test_build_price_table_uses_outer_join():
    asset_data = create_asset_data()

    result = build_price_table(asset_data)

    assert list(result.columns) == [
        "Date",
        "BTC-USD",
        "AAPL",
    ]

    assert len(result) == 4

    first_day = result[
        result["Date"] == pd.Timestamp("2024-01-01")
    ].iloc[0]

    assert first_day["BTC-USD"] == pytest.approx(100.0)
    assert pd.isna(first_day["AAPL"])


def test_build_base_100_table():
    asset_data = create_asset_data()

    result = build_base_100_table(asset_data)

    assert list(result.columns) == [
        "Date",
        "BTC-USD",
        "AAPL",
    ]

    assert result.loc[0, "BTC-USD"] == pytest.approx(100.0)

    aapl_first_value = result["AAPL"].dropna().iloc[0]

    assert aapl_first_value == pytest.approx(100.0)


def test_calculate_returns_table():
    price_table = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                ]
            ),
            "BTC-USD": [
                100.0,
                110.0,
                121.0,
            ],
            "AAPL": [
                50.0,
                55.0,
                60.0,
            ],
        }
    )

    result = calculate_returns_table(price_table)

    assert pd.isna(result.loc[0, "BTC-USD"])
    assert result.loc[1, "BTC-USD"] == pytest.approx(0.10)
    assert result.loc[2, "BTC-USD"] == pytest.approx(0.10)

    assert result.loc[1, "AAPL"] == pytest.approx(0.10)
    assert result.loc[2, "AAPL"] == pytest.approx(
        0.0909090909
    )


def test_correlation_matrix_is_symmetric():
    asset_data = create_asset_data()

    price_table = build_price_table(asset_data)
    returns_table = calculate_returns_table(price_table)
    correlation = calculate_correlation_matrix(returns_table)

    assert list(correlation.index) == [
        "BTC-USD",
        "AAPL",
    ]

    assert list(correlation.columns) == [
        "BTC-USD",
        "AAPL",
    ]

    pd.testing.assert_frame_equal(
        correlation,
        correlation.T,
    )


def test_create_comparison_summary():
    asset_data = create_asset_data()

    result = create_comparison_summary(asset_data)

    assert len(result) == 2
    assert set(result["Ativo"]) == {
        "BTC-USD",
        "AAPL",
    }

    btc_row = result[
        result["Ativo"] == "BTC-USD"
    ].iloc[0]

    assert btc_row["Retorno total"] == pytest.approx(0.21)
    assert btc_row["Observações"] == 3

def test_format_return_pct_formats_decimal_values():
    assert format_return_pct(0.20) == "20,00%"
    assert format_return_pct(-0.15) == "-15,00%"
    assert format_return_pct(0.0) == "0,00%"


def test_format_return_pct_handles_none():
    assert format_return_pct(None) == "—"


def test_returns_table_does_not_fill_calendar_gaps():
    import numpy as np
    import pandas as pd
    from core.comparison import calculate_returns_table

    table = pd.DataFrame({
        "Date": pd.date_range("2024-01-01", periods=4, freq="D"),
        "A": [100.0, 110.0, 121.0, 133.1],
        "B": [50.0, np.nan, 55.0, 60.5],
    })

    result = calculate_returns_table(table)

    assert result["A"].iloc[1] == pytest.approx(0.10)
    assert pd.isna(result["B"].iloc[1])   # sem valor no dia: sem retorno
    assert pd.isna(result["B"].iloc[2])   # anterior ausente: sem retorno
    assert result["B"].iloc[3] == pytest.approx(0.10)


def test_tables_align_by_period_end_instead_of_last_trading_day():
    import pandas as pd
    from core.comparison import build_price_table

    a = pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-30"]),
        "PeriodEnd": pd.to_datetime(["2024-01-31"]),
        "Value": [10.0],
    })
    b = pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-31"]),
        "PeriodEnd": pd.to_datetime(["2024-01-31"]),
        "Value": [20.0],
    })

    by_date = build_price_table({"A": a, "B": b})
    by_period = build_price_table({"A": a, "B": b}, align_col="PeriodEnd")

    assert len(by_date) == 2
    assert len(by_period) == 1
    assert by_period.iloc[0]["A"] == 10.0 and by_period.iloc[0]["B"] == 20.0