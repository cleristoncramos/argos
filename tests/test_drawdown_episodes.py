"""Episódios de queda e tempo de recuperação (core/drawdown_episodes.py)."""

import pandas as pd
import pytest

from core.drawdown_episodes import COLUMNS, drawdown_episodes, largest_drawdowns


def series(values, start="2020-01-31", freq="ME"):
    return pd.DataFrame({
        "Date": pd.date_range(start, periods=len(values), freq=freq),
        "Value": values,
    })


def test_recovered_and_open_episodes():
    #        0    1    2   3    4    5    6    7   8
    values = [100, 120, 90, 60, 110, 125, 130, 80, 100]
    episodes = drawdown_episodes(series(values))
    assert list(episodes.columns) == COLUMNS
    assert len(episodes) == 2

    first = episodes.iloc[0]
    assert first["Pico"] == pd.Timestamp("2020-02-29") and first["Valor no pico"] == 120
    assert first["Fundo"] == pd.Timestamp("2020-04-30") and first["Valor no fundo"] == 60
    assert first["Queda"] == pytest.approx(-0.5)
    assert first["Recuperada"] and first["Recuperação"] == pd.Timestamp("2020-06-30")
    assert first["Dias até o fundo"] == 61
    assert first["Dias do fundo à recuperação"] == 61
    assert first["Dias em queda"] == 122 and first["Períodos em queda"] == 4

    second = episodes.iloc[1]
    assert second["Pico"] == pd.Timestamp("2020-07-31") and second["Queda"] == pytest.approx(80 / 130 - 1)
    assert not second["Recuperada"] and pd.isna(second["Recuperação"])
    assert pd.isna(second["Dias do fundo à recuperação"])
    assert second["Dias em queda"] == (pd.Timestamp("2020-09-30") - pd.Timestamp("2020-07-31")).days
    assert second["Períodos em queda"] == 2


def test_recovery_on_equal_value_and_largest_order():
    values = [100, 80, 100, 95, 100, 70, 101]
    episodes = drawdown_episodes(series(values))
    assert len(episodes) == 3
    assert list(episodes["Recuperada"]) == [True, True, True]

    top = largest_drawdowns(series(values), top=2)
    assert list(top["Queda"].round(2)) == [-0.30, -0.20]
    assert top.loc[0, "Pico"] == pd.Timestamp("2020-05-31")  # pico do 100 que antecede o 70


def test_rising_series_and_invalid_inputs():
    assert drawdown_episodes(series([1, 2, 3, 4])).empty
    assert largest_drawdowns(series([1, 2, 3, 4])).empty
    for bad in (None, pd.DataFrame(), series([10]), pd.DataFrame({"Date": ["2020-01-01"]})):
        assert drawdown_episodes(bad).empty
    cleaned = drawdown_episodes(pd.DataFrame({
        "Date": ["2020-01-01", "2020-02-01", None, "2020-03-01", "2020-04-01"],
        "Value": [100, -5, 50, 80, 120],
    }))
    assert len(cleaned) == 1 and cleaned.loc[0, "Valor no fundo"] == 80
