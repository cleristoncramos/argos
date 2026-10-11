"""
Análises descritivas: estatísticas, variações, sazonalidade e retornos.

Convenções de unidade (atenção ao combinar funções):
- calculate_statistics (total_return), calculate_percentage_change
  (Pct_Change), analyze_seasonality e as matrizes de sazonalidade usam
  PERCENTUAL (10.0 = 10%).
- calculate_returns, calculate_cumulative_return e core/risk_metrics usam
  DECIMAL (0.10 = 10%).
Converta antes de usar format_return_pct(), que espera decimal.
"""

from typing import Any, Dict, Iterable

import numpy as np
import pandas as pd

from core.returns_utils import simple_returns


MONTH_NAMES = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}

ORDERED_MONTHS = list(MONTH_NAMES.values())


def _require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    """Levanta ValueError se faltar alguma coluna obrigatória."""
    missing = [column for column in columns if column not in df.columns]

    if missing:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {missing}"
        )


def calculate_statistics(df: pd.DataFrame, value_col: str = "Value") -> Dict[str, Any]:
    """
    Calcula estatísticas descritivas para a variável principal.

    O retorno total é expresso em percentual. Se o primeiro valor for zero
    ou ausente, o retorno total é NaN (não há base de comparação).
    """
    first_value = df[value_col].iloc[0] if len(df) > 0 else None
    last_value = df[value_col].iloc[-1] if len(df) > 0 else None

    if len(df) == 0:
        total_return = 0
    elif pd.isna(first_value) or first_value == 0:
        total_return = np.nan
    else:
        total_return = ((last_value / first_value) - 1) * 100

    stats = {
        'mean': df[value_col].mean(),
        'median': df[value_col].median(),
        'std': df[value_col].std(),
        'min': df[value_col].min(),
        'max': df[value_col].max(),
        'count': len(df),
        'first_value': first_value,
        'last_value': last_value,
        'total_return': total_return,
    }
    return stats


def calculate_percentage_change(df: pd.DataFrame, value_col: str = "Value") -> pd.DataFrame:
    """
    Calcula a variação percentual entre períodos consecutivos.

    Fórmula:
    var_pct = ((Value_t / Value_t-1) - 1) * 100

    A coluna Pct_Change está em PERCENTUAL (não em decimal).
    """
    df_calc = df.copy()
    df_calc['Pct_Change'] = simple_returns(df_calc[value_col]) * 100
    return df_calc


def analyze_seasonality(df: pd.DataFrame, value_col: str = "Value") -> pd.DataFrame:
    """
    Analisa o comportamento por mês do ano.

    Requer as colunas Month e Pct_Change (ver calculate_percentage_change).
    Só faz sentido interpretar como "comportamento mensal" quando a série
    está em frequência mensal; em dados diários, cada linha é um dia.

    Retorna uma tabela com:
    - Média, mediana, desvio-padrão e contagem da variação percentual
    - Média, mediana, mínimo e máximo do valor
    - positive_pct: percentual de observações positivas, calculado apenas
      sobre observações com variação válida (a primeira linha da série não
      tem variação e fica de fora).
    """
    _require_columns(df, ["Month", "Pct_Change", value_col])

    df_season = df.copy()

    # Agrupar por mês
    seasonality = df_season.groupby('Month').agg({
        'Pct_Change': ['mean', 'median', 'std', 'count'],
        value_col: ['mean', 'median', 'min', 'max']
    }).round(4)

    # Percentual de observações positivas, ignorando variações ausentes
    valid = df_season.dropna(subset=['Pct_Change'])
    positive_pct = (
        (valid['Pct_Change'] > 0).groupby(valid['Month']).mean() * 100
    )

    seasonality['positive_pct'] = positive_pct

    return seasonality


def create_year_month_matrix(
    df: pd.DataFrame,
    value_col: str = "Pct_Change"
) -> pd.DataFrame:
    """
    Cria uma matriz de variação percentual por ano e mês.

    Cada célula é a MÉDIA de `value_col` no ano/mês. Em dados mensais isso
    coincide com o retorno do mês; em dados diários ou semanais é a média
    das variações do período, não o retorno do mês. Para o retorno mensal
    em qualquer frequência, use create_monthly_return_matrix().
    """

    required_columns = ["Year", "Month", value_col]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {missing_columns}"
        )

    df_matrix = df.pivot_table(
        index="Year",
        columns="Month",
        values=value_col,
        aggfunc="mean"
    )

    df_matrix = df_matrix.rename(columns=MONTH_NAMES)

    existing_months = [
        month for month in ORDERED_MONTHS
        if month in df_matrix.columns
    ]

    return df_matrix[existing_months]


def create_monthly_return_matrix(
    df: pd.DataFrame,
    value_col: str = "Value",
    date_col: str = "Date",
) -> pd.DataFrame:
    """
    Matriz de retorno MENSAL (em %) por ano e mês, a partir de qualquer
    frequência.

    O retorno de um mês é o último valor do mês dividido pelo último valor
    do mês anterior, menos 1. Assim, dados diários e mensais geram o mesmo
    resultado. Meses sem dados e o mês seguinte a eles ficam vazios (NaN),
    pois não há valor anterior para comparação. O primeiro mês da série
    também fica vazio.
    """
    _require_columns(df, [date_col, value_col])

    data = df[[date_col, value_col]].copy()
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")
    data = data.dropna().sort_values(date_col)

    if data.empty:
        return pd.DataFrame()

    month_end = data.groupby(data[date_col].dt.to_period("M"))[value_col].last()

    full_range = pd.period_range(
        month_end.index.min(),
        month_end.index.max(),
        freq="M",
    )
    month_end = month_end.reindex(full_range)

    monthly_return = (month_end / month_end.shift(1) - 1) * 100

    table = pd.DataFrame(
        {
            "Year": monthly_return.index.year,
            "Month": monthly_return.index.month,
            "Return": monthly_return.to_numpy(),
        }
    )

    matrix = table.pivot_table(
        index="Year",
        columns="Month",
        values="Return",
        aggfunc="first",
        dropna=False,
    )

    matrix = matrix.rename(columns=MONTH_NAMES)

    existing_months = [
        month for month in ORDERED_MONTHS
        if month in matrix.columns
    ]

    return matrix[existing_months]


def calculate_returns(
    df: pd.DataFrame,
    value_col: str = "Value"
) -> pd.DataFrame:
    """
    Calcula retornos simples e logarítmicos entre períodos consecutivos.

    Os retornos estão em DECIMAL (0.10 = 10%).
    """
    result = df.copy()

    result["Simple_Return"] = simple_returns(result[value_col])
    result["Log_Return"] = np.log(
        result[value_col] / result[value_col].shift(1)
    )

    return result


def calculate_cumulative_return(
    df: pd.DataFrame,
    return_col: str = "Simple_Return"
) -> pd.DataFrame:
    """
    Calcula o retorno acumulado da série de retornos simples.

    Retorno ausente conta como zero; o resultado está em DECIMAL.
    """
    result = df.copy()
    result["Cumulative_Return"] = (
        (1 + result[return_col].fillna(0)).cumprod() - 1
    )
    return result