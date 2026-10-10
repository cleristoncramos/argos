"""
Sazonalidade por anos, meses e janela de retorno (Plano 2, Bloco 2).

Funções puras, sem Streamlit. Unidade: PERCENTUAL (mesma do `analyzer`):
5.0 significa 5%. Os nomes de mês seguem `core.analyzer.ORDERED_MONTHS`.

Regras de método:
- O fechamento de um mês é o último valor observado naquele mês.
- A janela de retorno vai do fechamento do mês de entrada ao fechamento do
  mês de saída: P(saída) / P(entrada) - 1. Janelas longas são compostas, não
  somadas. "Setembro -> outubro" é, portanto, o retorno de outubro.
- Dados ausentes não são interpolados: o ano sai da média e do N.
- O mês em andamento (o mês de `as_of`) nunca entra como mês completo.
"""

from typing import Iterable, Optional, Union

import numpy as np
import pandas as pd

from core.analyzer import ORDERED_MONTHS

MonthRef = Union[int, str]

# Texto metodológico obrigatório (Plano 2, Bloco 2). Linguagem descritiva:
# sem recomendação, sem previsão.
SEASONALITY_METHOD_TEXT = (
    "A média histórica representa o comportamento agregado dos anos disponíveis. "
    "Um ano específico pode divergir significativamente dessa média. "
    "A sazonalidade deve ser interpretada como evidência histórica descritiva, "
    "não como padrão determinístico."
)

SEASONALITY_WINDOW_NOTE = (
    "A janela vai do fechamento do mês de entrada ao fechamento do mês de saída. "
    "Por exemplo, de setembro a outubro corresponde ao retorno de outubro. "
    "Janelas com mais de um mês são compostas, não somadas. "
    "Anos sem os dois fechamentos ficam de fora, e o mês em andamento não é "
    "tratado como mês completo."
)


def _to_month_number(month: MonthRef) -> int:
    """Converte 1..12 ou o nome abreviado ("Set") em número do mês."""
    if isinstance(month, str):
        if month not in ORDERED_MONTHS:
            raise ValueError(f"Mês desconhecido: {month!r}.")
        return ORDERED_MONTHS.index(month) + 1
    if isinstance(month, (int, np.integer)) and 1 <= int(month) <= 12:
        return int(month)
    raise ValueError(f"Mês desconhecido: {month!r}.")


def _as_of_period(as_of: Optional[pd.Timestamp]) -> pd.Period:
    reference = pd.Timestamp.today() if as_of is None else pd.Timestamp(as_of)
    return reference.to_period("M")


def monthly_closes(
    df: pd.DataFrame,
    value_col: str = "Value",
    date_col: str = "Date",
    as_of: Optional[pd.Timestamp] = None,
) -> pd.Series:
    """
    Último valor de cada mês, indexado por período mensal contínuo.

    Meses sem dados ficam NaN (sem preenchimento). O mês em andamento
    (o de `as_of`; por padrão, o de hoje) também fica NaN.
    """
    for column in (date_col, value_col):
        if column not in df.columns:
            raise ValueError(f"A coluna '{column}' não existe no DataFrame.")

    data = df[[date_col, value_col]].copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")
    data = data.dropna().sort_values(date_col)

    if data.empty:
        return pd.Series(dtype=float)

    closes = data.groupby(data[date_col].dt.to_period("M"))[value_col].last()
    closes = closes.reindex(
        pd.period_range(closes.index.min(), closes.index.max(), freq="M")
    )

    in_progress = _as_of_period(as_of)
    if in_progress in closes.index:
        closes.loc[in_progress] = np.nan

    return closes


def exclude_month_in_progress(
    matrix: pd.DataFrame,
    as_of: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """Cópia da matriz ano x mês com a célula do mês em andamento vazia."""
    result = matrix.copy()
    period = _as_of_period(as_of)
    month_name = ORDERED_MONTHS[period.month - 1]

    if period.year in result.index and month_name in result.columns:
        result.loc[period.year, month_name] = np.nan

    return result


def filter_monthly_matrix(
    matrix: pd.DataFrame,
    years: Optional[Iterable[int]] = None,
    months: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Submatriz com os anos e meses escolhidos. `None` significa todos.
    Anos ou meses que não existem na matriz são ignorados.
    """
    result = matrix

    if years is not None:
        wanted_years = set(int(year) for year in years)
        result = result.loc[[y for y in result.index if int(y) in wanted_years]]

    if months is not None:
        wanted = set(months)
        for name in wanted:
            _to_month_number(name)  # valida o nome
        result = result[[m for m in result.columns if m in wanted]]

    return result


def _positive_share(values: pd.DataFrame) -> pd.Series:
    """% de anos com retorno estritamente positivo, sobre os anos com dado."""
    counts = values.notna().sum(axis=0)
    positives = (values > 0).sum(axis=0)
    share = positives / counts.replace(0, np.nan) * 100
    return share


def seasonal_summary(
    matrix: pd.DataFrame,
    years: Optional[Iterable[int]] = None,
) -> pd.DataFrame:
    """
    Resumo por mês do calendário: todos os anos (geral) x anos do recorte.

    Colunas (percentuais, exceto N): Média geral, Mediana geral,
    Anos positivos geral (%), N geral, Média do recorte, Mediana do recorte,
    Anos positivos recorte (%), N do recorte, Diferença (p.p.).
    A diferença é Média do recorte - Média geral, em pontos percentuais.
    Com `years=None`, o recorte coincide com o conjunto geral.
    """
    if matrix.empty:
        return pd.DataFrame()

    subset = filter_monthly_matrix(matrix, years=years)

    summary = pd.DataFrame(
        {
            "Média geral": matrix.mean(axis=0),
            "Mediana geral": matrix.median(axis=0),
            "Anos positivos geral (%)": _positive_share(matrix),
            "N geral": matrix.notna().sum(axis=0),
            "Média do recorte": subset.mean(axis=0),
            "Mediana do recorte": subset.median(axis=0),
            "Anos positivos recorte (%)": _positive_share(subset),
            "N do recorte": subset.notna().sum(axis=0),
        }
    )
    summary["Diferença (p.p.)"] = (
        summary["Média do recorte"] - summary["Média geral"]
    )
    summary.index.name = "Mês"

    return summary


def window_returns(
    df: pd.DataFrame,
    entry_month: MonthRef,
    exit_month: MonthRef,
    years: Optional[Iterable[int]] = None,
    value_col: str = "Value",
    date_col: str = "Date",
    as_of: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """
    Retorno da janela fechamento(entrada) -> fechamento(saída), por ano.

    O rótulo "Ano" é o ano da entrada. Se o mês de saída vem antes do mês de
    entrada no calendário (ex.: novembro -> fevereiro), a saída pertence ao
    ano seguinte. Anos com qualquer fechamento ausente (ou do mês em
    andamento) ficam de fora. Retorno em percentual.
    """
    m_in = _to_month_number(entry_month)
    m_out = _to_month_number(exit_month)

    if m_in == m_out:
        raise ValueError("Os meses de entrada e de saída devem ser diferentes.")

    closes = monthly_closes(df, value_col, date_col, as_of)
    columns = ["Ano", "Fechamento de entrada", "Fechamento de saída", "Retorno (%)"]

    if closes.empty:
        return pd.DataFrame(columns=columns)

    wanted = None if years is None else set(int(y) for y in years)
    wrap = m_out < m_in
    rows = []

    for year in sorted(set(closes.index.year)):
        if wanted is not None and year not in wanted:
            continue

        entry = pd.Period(year=year, month=m_in, freq="M")
        exit_ = pd.Period(year=year + (1 if wrap else 0), month=m_out, freq="M")

        if entry not in closes.index or exit_ not in closes.index:
            continue

        p_in, p_out = closes.loc[entry], closes.loc[exit_]

        if pd.isna(p_in) or pd.isna(p_out) or p_in <= 0:
            continue

        rows.append(
            {
                "Ano": year,
                "Fechamento de entrada": p_in,
                "Fechamento de saída": p_out,
                "Retorno (%)": (p_out / p_in - 1) * 100,
            }
        )

    return pd.DataFrame(rows, columns=columns)


def window_summary(window: pd.DataFrame) -> dict:
    """Média, mediana, % de anos positivos e N dos retornos da janela."""
    values = window["Retorno (%)"].dropna() if not window.empty else pd.Series(dtype=float)

    if values.empty:
        return {"N": 0, "Média": np.nan, "Mediana": np.nan, "Anos positivos (%)": np.nan}

    return {
        "N": int(len(values)),
        "Média": float(values.mean()),
        "Mediana": float(values.median()),
        "Anos positivos (%)": float((values > 0).sum() / len(values) * 100),
    }