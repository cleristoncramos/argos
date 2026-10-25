"""Maiores altas e quedas do período (core/extreme_moves.py)."""

import pandas as pd
import pytest

from core.extreme_moves import (
    COLUMNS,
    direction_counts,
    extreme_moves,
    last_period_is_partial,
    period_changes,
    period_label,
)


def series(values, dates):
    return pd.DataFrame({"Date": pd.to_datetime(dates), "Value": values})


def test_period_labels():
    d = pd.Timestamp("2026-10-23")
    assert period_label(d, "Diário") == "23/10/2026"
    assert period_label(d, "Semanal") == "semana até 23/10/2026"
    assert period_label(d, "Mensal") == "out/2026"
    assert period_label(pd.Timestamp("2026-03-31"), "Semestral") == "1º sem. 2026"
    assert period_label(d, "Semestral") == "2º sem. 2026"
    assert period_label(d, "Anual") == "2026"


def test_partial_last_period():
    # Mês que termina num sábado: último pregão 30/10 ainda é mês completo.
    assert not last_period_is_partial("2026-10-30", "Mensal")
    assert last_period_is_partial("2026-10-23", "Mensal")
    assert last_period_is_partial("2026-10-23", "Anual")
    assert not last_period_is_partial("2026-10-23", "Diário")
    # Com a última observação diária informada, ela é a referência.
    assert not last_period_is_partial("2026-09-30", "Mensal", last_observation="2026-09-30")
    # Semana com dados só até quarta-feira está em andamento; até sexta, completa.
    assert last_period_is_partial("2026-09-30", "Semanal")
    assert not last_period_is_partial("2026-10-02", "Semanal")


def test_changes_extremes_and_counts():
    df = series(
        [100, 110, 99, 99, 120, 90, 95],
        ["2026-03-31", "2026-04-30", "2026-05-29", "2026-06-30", "2026-07-31", "2026-08-31", "2026-10-23"],
    )
    changes = period_changes(df, "Mensal")
    assert list(changes.columns) == COLUMNS
    assert list(changes["Período"]) == ["abr/2026", "mai/2026", "jun/2026", "jul/2026", "ago/2026", "out/2026"]
    assert changes.loc[0, "Data inicial"] == pd.Timestamp("2026-03-31")
    assert changes.loc[0, "Variação"] == pytest.approx(0.10)
    assert list(changes["Parcial"]) == [False] * 5 + [True]

    highs, lows = extreme_moves(changes, top=2)
    assert list(highs["Período"]) == ["jul/2026", "abr/2026"]
    assert highs.loc[0, "Variação"] == pytest.approx(120 / 99 - 1)
    assert list(lows["Período"]) == ["ago/2026", "mai/2026"]
    assert (lows["Variação"] < 0).all()

    assert direction_counts(changes) == {"total": 6, "up": 3, "down": 2, "flat": 1}


def test_only_rises_and_invalid_inputs():
    changes = period_changes(series([1, 2, 3], ["2026-01-02", "2026-01-05", "2026-01-06"]), "Diário")
    highs, lows = extreme_moves(changes)
    assert len(highs) == 2 and lows.empty
    assert not changes["Parcial"].any()

    empty = period_changes(None, "Mensal")
    assert empty.empty and list(empty.columns) == COLUMNS
    assert extreme_moves(empty)[0].empty
    assert direction_counts(empty) == {"total": 0, "up": 0, "down": 0, "flat": 0}
    assert period_changes(series([10], ["2026-01-02"]), "Diário").empty
    assert period_changes(pd.DataFrame({"Date": ["2026-01-02"]}), "Diário").empty
    cleaned = period_changes(series([10, -1, 20], ["2026-01-02", "2026-01-05", "2026-01-06"]), "Diário")
    assert len(cleaned) == 1 and cleaned.loc[0, "Variação"] == pytest.approx(1.0)
