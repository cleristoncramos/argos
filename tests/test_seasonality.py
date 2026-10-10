import numpy as np
import pandas as pd
import pytest

from core.analyzer import create_monthly_return_matrix
from core.seasonality import (
    SEASONALITY_METHOD_TEXT,
    SEASONALITY_WINDOW_NOTE,
    exclude_month_in_progress,
    filter_monthly_matrix,
    monthly_closes,
    seasonal_summary,
    window_returns,
    window_summary,
)

FAR_FUTURE = pd.Timestamp("2030-01-01")


def month_end_frame(start, values):
    """Um fechamento por mês, no último dia do mês, a partir de `start`."""
    dates = pd.date_range(start, periods=len(values), freq="ME")
    return pd.DataFrame({"Date": dates, "Value": values})


# Ago/2021 a Mar/2022. Retornos mensais: Set 0%, Out +10%, Nov -10%,
# Dez +20%, Jan +10%, Fev -10%, Mar +10%.
YEAR_ONE = [100.0, 100.0, 110.0, 99.0, 118.8, 130.68, 117.612, 129.3732]


def hand_matrix():
    return pd.DataFrame(
        {"Jan": [10.0, -5.0, 0.0, 5.0], "Fev": [2.0, np.nan, 4.0, 6.0]},
        index=pd.Index([2021, 2022, 2023, 2024], name="Year"),
    )


# 1. Regressão: todos os anos == média geral atual
def test_all_years_equals_current_general_average():
    df = month_end_frame("2021-08-31", YEAR_ONE)
    matrix = create_monthly_return_matrix(df, "Value")
    summary = seasonal_summary(matrix)
    pd.testing.assert_series_equal(
        summary["Média do recorte"], matrix.mean(axis=0),
        check_names=False,
    )
    pd.testing.assert_series_equal(
        summary["Média geral"], summary["Média do recorte"],
        check_names=False,
    )
    assert (summary["Diferença (p.p.)"].dropna() == 0).all()


# 2. Subconjunto: média manual
def test_subset_mean_is_manual_average():
    summary = seasonal_summary(hand_matrix(), years=[2022, 2024])
    assert summary.loc["Jan", "Média do recorte"] == pytest.approx(0.0)
    assert summary.loc["Fev", "Média do recorte"] == pytest.approx(6.0)
    assert summary.loc["Jan", "Média geral"] == pytest.approx(2.5)
    assert summary.loc["Fev", "Média geral"] == pytest.approx(4.0)
    assert summary.loc["Jan", "Diferença (p.p.)"] == pytest.approx(-2.5)
    assert summary.loc["Fev", "Diferença (p.p.)"] == pytest.approx(2.0)


# 3. N = células não vazias
def test_n_counts_non_empty_cells():
    summary = seasonal_summary(hand_matrix(), years=[2022, 2024])
    assert summary["N geral"].tolist() == [4, 3]
    assert summary["N do recorte"].tolist() == [2, 1]


# 4. Janela de um mês == célula da matriz
def test_one_month_window_equals_matrix_cell():
    df = month_end_frame("2021-08-31", YEAR_ONE)
    matrix = create_monthly_return_matrix(df, "Value")
    result = window_returns(df, "Set", "Out", as_of=FAR_FUTURE)
    assert result["Ano"].tolist() == [2021]
    assert result["Retorno (%)"].iloc[0] == pytest.approx(10.0)
    assert result["Retorno (%)"].iloc[0] == pytest.approx(matrix.loc[2021, "Out"])


# 5. Janela de três meses é composta, não somada
def test_three_month_window_is_compounded():
    df = month_end_frame("2021-08-31", YEAR_ONE)
    matrix = create_monthly_return_matrix(df, "Value")
    result = window_returns(df, 9, 12, as_of=FAR_FUTURE)
    composed = (
        (1 + matrix.loc[2021, "Out"] / 100)
        * (1 + matrix.loc[2021, "Nov"] / 100)
        * (1 + matrix.loc[2021, "Dez"] / 100)
        - 1
    ) * 100
    assert result["Retorno (%)"].iloc[0] == pytest.approx(18.8)
    assert result["Retorno (%)"].iloc[0] == pytest.approx(composed)
    # a soma simples daria 20: a janela não pode ser somada
    assert result["Retorno (%)"].iloc[0] != pytest.approx(20.0)


# 6. Virada de ano: rótulo é o ano da entrada
def test_window_crossing_year_boundary():
    df = month_end_frame("2021-08-31", YEAR_ONE)
    result = window_returns(df, "Nov", "Fev", as_of=FAR_FUTURE)
    assert result["Ano"].tolist() == [2021]
    assert result["Fechamento de entrada"].iloc[0] == pytest.approx(99.0)
    assert result["Fechamento de saída"].iloc[0] == pytest.approx(117.612)
    assert result["Retorno (%)"].iloc[0] == pytest.approx(18.8)


# 7. Ano com fechamento ausente sai do N
def test_year_with_missing_close_is_excluded():
    one = month_end_frame("2021-08-31", YEAR_ONE)
    one = one[one["Date"] != pd.Timestamp("2021-12-31")]  # sem dezembro/2021
    two = month_end_frame("2022-08-31", [200.0, 200.0, 220.0, 220.0, 240.0])
    df = pd.concat([one, two], ignore_index=True)

    result = window_returns(df, "Set", "Dez", as_of=FAR_FUTURE)
    assert result["Ano"].tolist() == [2022]
    assert result["Retorno (%)"].iloc[0] == pytest.approx(20.0)
    assert window_summary(result)["N"] == 1

    only_2021 = window_returns(df, "Set", "Dez", years=[2021], as_of=FAR_FUTURE)
    assert only_2021.empty
    assert window_summary(only_2021)["N"] == 0


# 8. Mês em andamento não entra
def test_month_in_progress_is_excluded():
    df = month_end_frame("2021-08-31", YEAR_ONE)  # termina em mar/2022
    as_of = pd.Timestamp("2022-03-20")

    closes = monthly_closes(df, as_of=as_of)
    assert pd.isna(closes.loc[pd.Period("2022-03", "M")])
    assert closes.loc[pd.Period("2022-02", "M")] == pytest.approx(117.612)

    assert window_returns(df, "Fev", "Mar", as_of=as_of).empty
    assert len(window_returns(df, "Fev", "Mar", as_of=FAR_FUTURE)) == 1

    matrix = create_monthly_return_matrix(df, "Value")
    masked = exclude_month_in_progress(matrix, as_of=as_of)
    assert pd.isna(masked.loc[2022, "Mar"])
    assert not pd.isna(matrix.loc[2022, "Mar"])          # original intacto
    assert seasonal_summary(matrix)["N geral"]["Mar"] == 1
    assert seasonal_summary(masked)["N geral"]["Mar"] == 0


def test_exclude_month_in_progress_when_not_in_matrix_is_noop():
    matrix = hand_matrix()
    result = exclude_month_in_progress(matrix, as_of=pd.Timestamp("2030-05-10"))
    pd.testing.assert_frame_equal(result, matrix)


def test_as_of_defaults_to_today():
    today = pd.Timestamp.today()
    df = pd.DataFrame({"Date": [today], "Value": [10.0]})
    assert monthly_closes(df).isna().all()


# 9. Mediana e % de anos positivos
def test_median_and_positive_share_even_and_odd_n_with_zero():
    summary = seasonal_summary(hand_matrix())
    # Jan: -5, 0, 5, 10 -> N par, mediana (0+5)/2; zero não é positivo
    assert summary.loc["Jan", "Mediana geral"] == pytest.approx(2.5)
    assert summary.loc["Jan", "Anos positivos geral (%)"] == pytest.approx(50.0)
    # Fev: 2, 4, 6 -> N ímpar, mediana 4; 3 de 3 positivos
    assert summary.loc["Fev", "Mediana geral"] == pytest.approx(4.0)
    assert summary.loc["Fev", "Anos positivos geral (%)"] == pytest.approx(100.0)

    cut = seasonal_summary(hand_matrix(), years=[2022, 2024])
    assert cut.loc["Jan", "Mediana do recorte"] == pytest.approx(0.0)
    assert cut.loc["Jan", "Anos positivos recorte (%)"] == pytest.approx(50.0)
    assert cut.loc["Fev", "Anos positivos recorte (%)"] == pytest.approx(100.0)


def test_window_summary_values():
    window = pd.DataFrame({"Ano": [2020, 2021, 2022, 2023],
                           "Retorno (%)": [10.0, -4.0, 0.0, 6.0]})
    result = window_summary(window)
    assert result["N"] == 4
    assert result["Média"] == pytest.approx(3.0)
    assert result["Mediana"] == pytest.approx(3.0)
    assert result["Anos positivos (%)"] == pytest.approx(50.0)


def test_no_positive_data_gives_nan_share():
    matrix = pd.DataFrame({"Jan": [np.nan, np.nan]}, index=[2021, 2022])
    summary = seasonal_summary(matrix)
    assert summary.loc["Jan", "N geral"] == 0
    assert pd.isna(summary.loc["Jan", "Anos positivos geral (%)"])


# 10. Linguagem neutra e texto obrigatório
def test_texts_are_descriptive_and_contain_mandatory_sentences():
    assert "evidência histórica descritiva" in SEASONALITY_METHOD_TEXT
    assert "não como padrão determinístico" in SEASONALITY_METHOD_TEXT
    assert "Um ano específico pode divergir significativamente" in SEASONALITY_METHOD_TEXT
    forbidden = [
        "melhor mês", "pior mês", "recomend", "garant", "oportunidade",
        "compre", "venda", "vai subir", "vai cair", "prever", "previs",
        "lucro certo",
    ]
    for text in (SEASONALITY_METHOD_TEXT, SEASONALITY_WINDOW_NOTE):
        lowered = text.lower()
        for word in forbidden:
            assert word not in lowered


# Filtros e validações
def test_filter_monthly_matrix_by_years_and_months():
    matrix = hand_matrix()
    assert filter_monthly_matrix(matrix).shape == (4, 2)
    assert filter_monthly_matrix(matrix, years=[2022, 2099]).index.tolist() == [2022]
    assert filter_monthly_matrix(matrix, months=["Fev"]).columns.tolist() == ["Fev"]
    assert filter_monthly_matrix(matrix, months=["Mar"]).shape == (4, 0)
    with pytest.raises(ValueError, match="Mês desconhecido"):
        filter_monthly_matrix(matrix, months=["Foo"])


def test_seasonal_summary_empty_matrix():
    assert seasonal_summary(pd.DataFrame()).empty


def test_window_validations():
    df = month_end_frame("2021-08-31", YEAR_ONE)
    with pytest.raises(ValueError, match="diferentes"):
        window_returns(df, "Set", 9, as_of=FAR_FUTURE)
    with pytest.raises(ValueError, match="Mês desconhecido"):
        window_returns(df, 13, 2, as_of=FAR_FUTURE)
    with pytest.raises(ValueError, match="Mês desconhecido"):
        window_returns(df, "Foo", "Out", as_of=FAR_FUTURE)
    with pytest.raises(ValueError, match="não existe"):
        monthly_closes(pd.DataFrame({"Date": [], "X": []}))


def test_monthly_closes_empty_and_window_on_empty():
    empty = pd.DataFrame({"Date": [], "Value": []})
    assert monthly_closes(empty).empty
    assert window_returns(empty, "Set", "Out", as_of=FAR_FUTURE).empty


def test_window_skips_non_positive_entry_close_and_year_filter():
    df = month_end_frame("2021-08-31", [0.0, 10.0, 11.0])
    # entrada com fechamento zero: o ano não entra
    assert window_returns(df, "Ago", "Set", as_of=FAR_FUTURE).empty
    ok = window_returns(df, "Set", "Out", as_of=FAR_FUTURE)
    assert ok["Retorno (%)"].iloc[0] == pytest.approx(10.0)
    assert window_returns(df, "Set", "Out", years=[2030], as_of=FAR_FUTURE).empty


def test_window_year_without_exit_month_in_range():
    df = month_end_frame("2021-08-31", [100.0, 110.0])  # só ago e set
    assert window_returns(df, "Set", "Out", as_of=FAR_FUTURE).empty