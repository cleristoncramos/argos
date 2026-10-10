import numpy as np
import pandas as pd
import pytest

from core.analyzer import ORDERED_MONTHS
from core.comparison_texts import (
    HIGHLIGHT_LABELS,
    LEGEND_HINT,
    SEASONALITY_COMPARISON_NOTE,
)
from core.seasonality import compare_monthly_averages

FAR_FUTURE = pd.Timestamp("2030-01-01")


def monthly(start, values):
    dates = pd.date_range(start, periods=len(values), freq="ME")
    return pd.DataFrame({"Date": dates, "Value": values})


# A: dez/2020 a mar/2022 (16 meses). Retornos: Jan/21 +10%, Fev/21 -10%,
# Jan/22 +20%, Fev/22 0%.
def asset_a():
    # dez/20=100, jan/21=110, fev/21=99, mar a dez/21=99, jan/22=118.8, fev/22=118.8
    return monthly("2020-12-31", [100.0, 110.0, 99.0] + [99.0] * 10 + [118.8, 118.8])


def asset_b():
    # fev/2021 a mar/2021: só Fev (base) e Mar
    return monthly("2021-02-28", [50.0, 55.0])


def test_compare_monthly_averages_known_values_and_different_n():
    means, counts = compare_monthly_averages(
        {"A": asset_a(), "B": asset_b()}, as_of=FAR_FUTURE
    )
    assert means.index.tolist() == ORDERED_MONTHS
    assert list(means.columns) == ["A", "B"]

    # A: Jan/21 +10% e Jan/22 +20% -> média 15, N = 2
    assert means.loc["Jan", "A"] == pytest.approx(15.0)
    assert counts.loc["Jan", "A"] == 2
    # A: Fev/21 -10% e Fev/22 0% -> média -5, N = 2
    assert means.loc["Fev", "A"] == pytest.approx(-5.0)
    assert counts.loc["Fev", "A"] == 2
    # B: só Mar/21 +10% -> N = 1; nos demais meses N = 0 e média vazia
    assert means.loc["Mar", "B"] == pytest.approx(10.0)
    assert counts.loc["Mar", "B"] == 1
    assert pd.isna(means.loc["Jan", "B"])
    assert counts.loc["Jan", "B"] == 0
    assert counts.dtypes.apply(lambda d: np.issubdtype(d, np.integer)).all()


def test_compare_monthly_averages_excludes_month_in_progress():
    means, counts = compare_monthly_averages(
        {"A": asset_a()}, as_of=pd.Timestamp("2022-02-15")
    )
    # Fev/22 está em andamento: sai da média de fevereiro
    assert counts.loc["Fev", "A"] == 1
    assert means.loc["Fev", "A"] == pytest.approx(-10.0)


def test_compare_monthly_averages_empty_inputs():
    means, counts = compare_monthly_averages({}, as_of=FAR_FUTURE)
    assert means.empty and counts.empty
    empty = pd.DataFrame({"Date": [], "Value": []})
    means, counts = compare_monthly_averages({"A": empty}, as_of=FAR_FUTURE)
    assert means.empty and counts.empty


def test_comparison_texts_are_descriptive():
    assert HIGHLIGHT_LABELS["min_drawdown"] == "Menor queda máxima observada"
    assert "retorno acumulado no período analisado" in HIGHLIGHT_LABELS["max_return"]
    texts = list(HIGHLIGHT_LABELS.values()) + [LEGEND_HINT, SEASONALITY_COMPARISON_NOTE]
    forbidden = ["melhor", "pior", "recomend", "garant", "oportunidade",
                 "compre", "venda", "vai subir", "vai cair", "prever", "previs"]
    for text in texts:
        lowered = text.lower()
        for word in forbidden:
            assert word not in lowered, (word, text)