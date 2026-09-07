import pandas as pd
import pytest
import plotly.graph_objects as go

from core.visualizations import (
    create_candlestick_chart,
    create_cumulative_return_chart,
    create_drawdown_chart,
    create_macd_chart,
    create_price_indicator_chart,
    create_returns_histogram,
    create_rsi_chart,
    create_volume_chart,
    format_context,
)


def create_visualization_dataframe():
    return pd.DataFrame(
        {
            "Date": pd.date_range(
                start="2024-01-01",
                periods=30,
                freq="D",
            ),
            "Open": [100 + index for index in range(30)],
            "High": [102 + index for index in range(30)],
            "Low": [98 + index for index in range(30)],
            "Close": [101 + index for index in range(30)],
            "Volume": [1000 + (index * 10) for index in range(30)],
            "Value": [101 + index for index in range(30)],
            "SMA_3": [None, None] + [
                102 + index
                for index in range(28)
            ],
            "SMA_5": [None] * 4 + [
                103 + index
                for index in range(26)
            ],
            "EMA_3": [101 + index for index in range(30)],
            "EMA_5": [101 + index for index in range(30)],
            "BB_Lower": [98 + index for index in range(30)],
            "BB_Middle": [101 + index for index in range(30)],
            "BB_Upper": [104 + index for index in range(30)],
            "RSI_14": [50 + ((index % 5) - 2) for index in range(30)],
            "MACD": [index * 0.1 for index in range(30)],
            "MACD_Signal": [index * 0.08 for index in range(30)],
            "MACD_Histogram": [index * 0.02 for index in range(30)],
            "Simple_Return": [None] + [0.01] * 29,
            "Drawdown": [0.0, -0.02, -0.01] + [0.0] * 27,
        }
    )


def test_format_context():
    result = format_context(
        "BTC-USD",
        "2024-01-01",
        "2024-12-31",
        "Diário",
    )

    assert "BTC-USD" in result
    assert "01/01/2024" in result
    assert "31/12/2024" in result
    assert "Diário" in result


def test_create_price_indicator_chart():
    df = create_visualization_dataframe()

    figure = create_price_indicator_chart(
        df=df,
        symbol="BTC-USD",
        context="Contexto de teste",
        show_sma_short=True,
        sma_short_col="SMA_3",
        show_sma_long=True,
        sma_long_col="SMA_5",
        show_ema_short=True,
        ema_short_col="EMA_3",
        show_ema_long=True,
        ema_long_col="EMA_5",
        show_bollinger=True,
    )

    assert isinstance(figure, go.Figure)
    assert len(figure.data) >= 6


def test_create_candlestick_chart():
    df = create_visualization_dataframe()

    figure = create_candlestick_chart(
        df=df,
        symbol="BTC-USD",
        context="Contexto de teste",
    )

    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 1
    assert figure.data[0].type == "candlestick"


def test_create_volume_chart():
    df = create_visualization_dataframe()

    figure = create_volume_chart(
        df=df,
        symbol="BTC-USD",
        context="Contexto de teste",
    )

    assert isinstance(figure, go.Figure)
    assert figure.data[0].type == "bar"


def test_create_rsi_chart():
    df = create_visualization_dataframe()

    figure = create_rsi_chart(
        df=df,
        symbol="BTC-USD",
        context="Contexto de teste",
        rsi_col="RSI_14",
    )

    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 1


def test_create_macd_chart():
    df = create_visualization_dataframe()

    figure = create_macd_chart(
        df=df,
        symbol="BTC-USD",
        context="Contexto de teste",
    )

    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 3


def test_create_cumulative_return_chart():
    df = create_visualization_dataframe()

    figure = create_cumulative_return_chart(
        df=df,
        symbol="BTC-USD",
        context="Contexto de teste",
    )

    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 1


def test_create_drawdown_chart():
    df = create_visualization_dataframe()

    figure = create_drawdown_chart(
        df=df,
        symbol="BTC-USD",
        context="Contexto de teste",
    )

    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 1


def test_create_returns_histogram():
    df = create_visualization_dataframe()

    figure = create_returns_histogram(
        df=df,
        symbol="BTC-USD",
        context="Contexto de teste",
    )

    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 1


def test_chart_requires_expected_columns():
    df = pd.DataFrame(
        {
            "Date": pd.date_range(
                start="2024-01-01",
                periods=3,
                freq="D",
            )
        }
    )

    with pytest.raises(
        ValueError,
        match="Colunas obrigatórias ausentes",
    ):
        create_price_indicator_chart(
            df=df,
            symbol="BTC-USD",
            context="Contexto de teste",
        )