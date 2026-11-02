"""Diagnóstico de séries que impedem o cálculo (core/analysis_feasibility.py)."""

import numpy as np
import pandas as pd

from core.analysis_feasibility import (
    diagnose_series,
    infeasibility_markdown,
    infeasibility_summary,
    unknown_infeasibility,
)
from core.data_processor import prepare_dataframe
from core.disclaimers import contains_forbidden_phrase

DATES = pd.date_range("2026-01-05", periods=6, freq="D")


def test_valid_series_has_no_diagnosis():
    assert diagnose_series(DATES, [10, 11, 12, 11, 13, 14]) is None


def test_empty_or_all_missing_series():
    assert diagnose_series([], []).reason == "empty"
    assert diagnose_series(DATES[:2], [np.nan, None]).reason == "empty"


def test_non_positive_prices_list_dates_and_lowest_value():
    diagnosis = diagnose_series(DATES, [20, 5, 0, -37.63, 3, 4])
    assert diagnosis.reason == "non_positive"
    assert "2 observação(ões) com preço ≤ 0: 07/01/2026, 08/01/2026." in diagnosis.details[0]
    assert diagnosis.details[1] == "Menor valor: -37,63 em 08/01/2026."


def test_missing_close_points_to_the_session_in_progress():
    diagnosis = diagnose_series(DATES, [10, 11, 12, 11, 13, np.nan])
    assert diagnosis.reason == "missing"
    assert diagnosis.details == ("1 data(s) sem fechamento: 10/01/2026.",)
    assert "pregão do dia ainda não terminou" in diagnosis.explanation


def test_short_series_and_long_date_lists():
    assert diagnose_series(DATES[:2], [10, 11]).reason == "short"
    many = pd.date_range("2026-01-01", periods=8, freq="D")
    diagnosis = diagnose_series(many, [0] * 8)
    assert diagnosis.details[0].endswith("e mais 3.")


def test_messages_are_complete_and_neutral():
    diagnosis = diagnose_series(DATES, [10, 11, 12, 11, 13, np.nan])
    text = infeasibility_markdown(diagnosis, "^N225", "as métricas de risco e retorno")
    assert text.startswith("**Não foi possível calcular as métricas de risco e retorno para ^N225:")
    assert "**O que foi encontrado nos dados**" in text and "**O que você pode fazer**" in text
    assert infeasibility_summary(diagnosis, "^N225").startswith("^N225: a série tem datas sem preço")

    generic = unknown_infeasibility(ValueError("falha"))
    assert generic.reason == "unknown" and generic.details == ("Detalhe técnico: falha",)
    bare = infeasibility_markdown(generic.__class__("unknown", "Título", "Texto."), "X", "algo")
    assert "O que foi encontrado" not in bare and infeasibility_summary(
        generic.__class__("unknown", "Título", "Texto."), "X") == "X: título"

    for reason_values in ([], [0, 1, 2], [1, np.nan, 2], [1, 2]):
        found = diagnose_series(DATES[: len(reason_values)], reason_values)
        assert not contains_forbidden_phrase(infeasibility_markdown(found, "X", "o cálculo"))


def test_prepare_dataframe_drops_dates_without_close():
    # Pregão em andamento: a fonte já traz a abertura, mas ainda não o fechamento.
    raw = pd.DataFrame({
        "Date": pd.date_range("2026-10-29", periods=3, freq="D"),
        "Open": [100.0, 101.0, 102.0],
        "Close": [100.5, 101.5, np.nan],
        "Volume": [10, 10, 0],
    })
    prepared = prepare_dataframe(raw)
    assert len(prepared) == 2
    assert prepared["Close"].notna().all()
