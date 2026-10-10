import numpy as np
import pandas as pd
import pytest

from core.trend import (
    RATIO_START_NOTE,
    ROLLING_NOTE,
    TREND_DISCLAIMER,
    TREND_WINDOWS,
    monthly_close_table,
    performance_ratio,
    rebase_common_start,
    rolling_label,
    rolling_return,
    rolling_return_gap,
)

FAR_FUTURE = pd.Timestamp("2030-01-01")


def month_series(values, start="2020-01"):
    index = pd.period_range(start, periods=len(values), freq="M")
    return pd.Series(values, index=index, dtype=float)


def monthly_frame(start, values):
    dates = pd.date_range(start, periods=len(values), freq="ME")
    return pd.DataFrame({"Date": dates, "Value": values})


def test_rolling_return_doubling_in_twelve_months_is_one():
    values = [100.0 * 2 ** (m / 12) for m in range(13)]
    result = rolling_return(month_series(values), 12)
    assert result.iloc[:12].isna().all()          # sem histórico: vazio, não zero
    assert result.iloc[12] == pytest.approx(1.0)


def test_rolling_return_known_values():
    result = rolling_return(month_series([100.0, 110.0, 99.0, 108.9]), 1)
    assert result.tolist()[1:] == pytest.approx([0.10, -0.10, 0.10])
    three = rolling_return(month_series([100.0, 110.0, 99.0, 150.0]), 3)
    assert three.iloc[3] == pytest.approx(0.5)


def test_window_larger_than_series_is_all_empty():
    result = rolling_return(month_series([100.0, 110.0, 121.0]), 12)
    assert result.isna().all()


def test_rolling_return_with_missing_month_is_empty_where_it_touches():
    result = rolling_return(month_series([100.0, np.nan, 121.0, 133.1]), 1)
    assert result.isna().tolist() == [True, True, True, False]
    assert result.iloc[3] == pytest.approx(0.10)


def test_rolling_return_ignores_non_positive_base():
    result = rolling_return(month_series([0.0, 10.0]), 1)
    assert pd.isna(result.iloc[1])


def test_rolling_return_works_on_dataframes():
    table = pd.DataFrame({"A": month_series([100.0, 200.0]), "B": month_series([50.0, 75.0])})
    result = rolling_return(table, 1)
    assert result.iloc[1].tolist() == pytest.approx([1.0, 0.5])


@pytest.mark.parametrize("bad", [0, -3, 1.5, "12", True])
def test_invalid_window_is_rejected(bad):
    with pytest.raises(ValueError, match="janela"):
        rolling_return(month_series([100.0, 110.0]), bad)


def test_rolling_return_gap_in_decimal():
    a = month_series([100.0 * 2 ** (m / 12) for m in range(13)])   # dobra
    b = month_series([100.0 + 50.0 * m / 12 for m in range(13)])   # +50%
    gap = rolling_return_gap(a, b, 12)
    assert gap.iloc[12] == pytest.approx(0.5)      # 50 pontos percentuais
    assert gap.iloc[:12].isna().all()


def test_performance_ratio_identical_series_is_zero_everywhere():
    a = month_series([100.0, 120.0, 90.0, 130.0])
    assert performance_ratio(a, a.copy()).tolist() == pytest.approx([0.0] * 4)


def test_performance_ratio_known_values_and_invalid_denominator():
    a = month_series([100.0, 120.0, 150.0])
    b = month_series([100.0, 100.0, 0.0])
    ratio = performance_ratio(a, b)
    assert ratio.iloc[0] == pytest.approx(0.0)
    assert ratio.iloc[1] == pytest.approx(0.2)
    assert pd.isna(ratio.iloc[2])                  # denominador não positivo


def test_performance_ratio_aligns_different_histories():
    a = month_series([100.0, 110.0, 120.0], start="2020-01")
    b = month_series([100.0, 100.0], start="2020-02")
    ratio = performance_ratio(a, b)
    assert pd.isna(ratio.iloc[0])                  # B ainda não existia
    assert ratio.iloc[1] == pytest.approx(0.10)
    assert ratio.iloc[2] == pytest.approx(0.20)


def test_rebase_common_start_uses_first_date_with_all_assets():
    table = pd.DataFrame(
        {
            "A": month_series([50.0, 60.0, 90.0, 120.0]),
            "B": month_series([np.nan, 200.0, 220.0, 400.0]),
        }
    )
    based = rebase_common_start(table)
    assert based.index[0] == pd.Period("2020-02", "M")
    assert based.iloc[0].tolist() == pytest.approx([100.0, 100.0])
    assert based["A"].iloc[-1] == pytest.approx(200.0)    # 120/60
    assert based["B"].iloc[-1] == pytest.approx(200.0)    # 400/200


def test_rebase_common_start_errors():
    disjoint = pd.DataFrame(
        {"A": month_series([1.0, np.nan]), "B": month_series([np.nan, 2.0])}
    )
    with pytest.raises(ValueError, match="em comum"):
        rebase_common_start(disjoint)
    non_positive = pd.DataFrame({"A": month_series([0.0, 1.0]), "B": month_series([1.0, 1.0])})
    with pytest.raises(ValueError, match="maiores que zero"):
        rebase_common_start(non_positive)


def test_cross_over_in_ratio_depends_on_start_date():
    # B sobe primeiro e A o ultrapassa depois: a razão (A contra B) é
    # negativa cedo e positiva no fim se o início for cedo, mas começar mais
    # tarde muda o sinal inicial. O teste fixa os valores conhecidos.
    a = month_series([100.0, 100.0, 150.0, 200.0])
    b = month_series([100.0, 150.0, 150.0, 150.0])
    early = performance_ratio(*[rebase_common_start(pd.DataFrame({"A": a, "B": b}))[c] for c in "AB"])
    late_table = pd.DataFrame({"A": a, "B": b}).iloc[1:]
    late = performance_ratio(*[rebase_common_start(late_table)[c] for c in "AB"])
    assert early.iloc[1] == pytest.approx(100.0 / 150.0 - 1)       # -1/3
    assert early.iloc[-1] == pytest.approx(200.0 / 150.0 - 1)      # +1/3
    assert late.iloc[0] == pytest.approx(0.0)                       # recomeça em 100
    assert late.iloc[-1] == pytest.approx(200.0 / 100.0 / (150.0 / 150.0) - 1)


def test_monthly_close_table_different_histories_and_gap():
    a = monthly_frame("2020-01-31", [100.0, 110.0, 121.0])
    b = monthly_frame("2020-03-31", [50.0, 55.0])
    table = monthly_close_table({"A": a, "B": b}, as_of=FAR_FUTURE)
    assert table.index[0] == pd.Period("2020-01", "M")
    assert table.index[-1] == pd.Period("2020-04", "M")
    assert pd.isna(table.loc[pd.Period("2020-01", "M"), "B"])
    assert table.loc[pd.Period("2020-03", "M"), "A"] == pytest.approx(121.0)
    assert pd.isna(table.loc[pd.Period("2020-04", "M"), "A"])


def test_monthly_close_table_disjoint_histories_keep_continuous_months():
    a = monthly_frame("2020-01-31", [1.0])
    b = monthly_frame("2020-04-30", [2.0])
    table = monthly_close_table({"A": a, "B": b}, as_of=FAR_FUTURE)
    assert len(table) == 4
    assert table.isna().sum().sum() == 6


def test_monthly_close_table_excludes_month_in_progress_and_handles_empty():
    a = monthly_frame("2020-01-31", [100.0, 110.0])
    table = monthly_close_table({"A": a}, as_of=pd.Timestamp("2020-02-10"))
    assert pd.isna(table.loc[pd.Period("2020-02", "M"), "A"])
    assert monthly_close_table({}).empty
    assert monthly_close_table({"A": pd.DataFrame({"Date": [], "Value": []})}).empty


def test_labels_and_texts_are_historical_and_neutral():
    assert rolling_label(12) == "retorno móvel de 12 meses"
    assert rolling_label(1) == "retorno móvel de 1 mês"
    assert TREND_WINDOWS == (3, 6, 12)
    assert "Tendência histórica" in TREND_DISCLAIMER
    assert "pode mudar" in TREND_DISCLAIMER
    assert "depende da data inicial" in RATIO_START_NOTE
    for text in (TREND_DISCLAIMER, RATIO_START_NOTE, ROLLING_NOTE):
        lowered = text.lower()
        for word in ("tendência futura", "previs", "prever", "vai continuar",
                     "melhor", "pior", "recomend", "compre", "venda", "garant"):
            assert word not in lowered, (word, text)