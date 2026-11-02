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
    gradient_fill,
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


def test_gradient_fill_fades_from_the_line_to_the_base():
    # Acima da base (preço): transparente no zero, forte no topo.
    up = gradient_fill("#10B981", [10, 30, 50])
    assert up["type"] == "vertical" and (up["start"], up["stop"]) == (0, 50)
    assert up["colorscale"] == [[0.0, "rgba(16, 185, 129, 0)"], [1, "rgba(16, 185, 129, 0.32)"]]

    # Abaixo da base (drawdown): forte no fundo, transparente no zero.
    down = gradient_fill("#DC2626", [0, -20, -40], opacity=0.3)
    assert (down["start"], down["stop"]) == (-40, 0)
    assert down["colorscale"] == [[0, "rgba(220, 38, 38, 0.3)"], [1.0, "rgba(220, 38, 38, 0)"]]


def test_gradient_fill_handles_both_sides_and_a_custom_base():
    both = gradient_fill("#2563EB", [-30, 10])
    assert [stop for stop, _ in both["colorscale"]] == [0, 0.75, 1]
    assert both["colorscale"][1][1].endswith(", 0)")

    floor = gradient_fill("#C8102E", [800, 1100], base=750, opacity=0.22)
    assert (floor["start"], floor["stop"]) == (750, 1100)


def test_gradient_fill_without_variation_is_transparent():
    for values in ([], [0, 0], [float("nan")]):
        flat = gradient_fill("#2563EB", values)
        assert "start" not in flat
        assert all(color.endswith(", 0)") for _, color in flat["colorscale"])


def test_area_charts_use_the_gradient_fill():
    df = create_visualization_dataframe()
    for fig in (
        create_cumulative_return_chart(df, "AAPL", "contexto"),
        create_drawdown_chart(df.assign(Drawdown=-0.1), "AAPL", "contexto"),
    ):
        area = fig.data[0]
        assert area.fill == "tozeroy" and area.fillgradient.type == "vertical"
