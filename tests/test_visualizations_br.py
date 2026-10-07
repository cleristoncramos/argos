import pandas as pd
import pytest

from core.visualizations import (
    BR_SEPARATORS,
    DEFAULT_PRICE_LABEL,
    create_candlestick_chart,
    create_cumulative_return_chart,
    create_drawdown_chart,
    create_price_indicator_chart,
    create_returns_histogram,
    create_volume_chart,
)


@pytest.fixture
def sample():
    return pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-31", periods=4, freq="ME"),
            "Open": [10.0, 11.0, 12.0, 13.0],
            "High": [11.0, 12.0, 13.0, 14.0],
            "Low": [9.0, 10.0, 11.0, 12.0],
            "Close": [10.5, 11.5, 12.5, 13.5],
            "Value": [10.5, 11.5, 12.5, 13.5],
            "Volume": [100, 200, 300, 400],
            "Simple_Return": [None, 0.1, 0.05, -0.02],
            "Drawdown": [0.0, 0.0, -0.05, -0.02],
        }
    )


def test_charts_use_brazilian_separators_and_context(sample):
    figures = [
        create_price_indicator_chart(sample, "X", "ctx"),
        create_candlestick_chart(sample, "X", "ctx"),
        create_volume_chart(sample, "X", "ctx"),
        create_cumulative_return_chart(sample, "X", "ctx"),
        create_drawdown_chart(sample, "X", "ctx"),
        create_returns_histogram(sample, "X", "ctx"),
    ]

    for figure in figures:
        assert figure.layout.separators == BR_SEPARATORS
        assert [a.text for a in figure.layout.annotations] == ["ctx"]


def test_price_label_is_configurable_with_backward_compatible_default(sample):
    default_chart = create_price_indicator_chart(sample, "X", "ctx")
    custom_chart = create_price_indicator_chart(
        sample, "X", "ctx", price_label="Preço em US$"
    )
    candle = create_candlestick_chart(sample, "X", "ctx", price_label="US$")

    assert default_chart.layout.yaxis.title.text == DEFAULT_PRICE_LABEL
    assert custom_chart.layout.yaxis.title.text == "Preço em US$"
    assert candle.layout.yaxis.title.text == "US$"


def test_cumulative_return_chart_reuses_analyzer_calculation(sample):
    figure = create_cumulative_return_chart(sample, "X", "ctx")

    expected = ((1 + sample["Simple_Return"].fillna(0)).cumprod() - 1) * 100

    assert list(figure.data[0].y) == pytest.approx(list(expected))