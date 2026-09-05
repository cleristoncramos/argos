import pandas as pd
import numpy as np
from typing import Dict, Any


def calculate_statistics(df: pd.DataFrame, value_col: str = "Value") -> Dict[str, Any]:
    """
    Calcula estatísticas descritivas para a variável principal.
    """
    stats = {
        'mean': df[value_col].mean(),
        'median': df[value_col].median(),
        'std': df[value_col].std(),
        'min': df[value_col].min(),
        'max': df[value_col].max(),
        'count': len(df),
        'first_value': df[value_col].iloc[0] if len(df) > 0 else None,
        'last_value': df[value_col].iloc[-1] if len(df) > 0 else None,
        'total_return': ((df[value_col].iloc[-1] / df[value_col].iloc[0]) - 1) * 100 if len(df) > 0 else 0
    }
    return stats


def calculate_percentage_change(df: pd.DataFrame, value_col: str = "Value") -> pd.DataFrame:
    """
    Calcula a variação percentual entre períodos consecutivos.
    
    Fórmula:
    var_pct = ((Value_t / Value_t-1) - 1) * 100
    """
    df_calc = df.copy()
    df_calc['Pct_Change'] = df_calc[value_col].pct_change() * 100
    return df_calc


def analyze_seasonality(df: pd.DataFrame, value_col: str = "Value") -> pd.DataFrame:
    """
    Analisa o comportamento por mês do ano.
    
    Retorna uma tabela com:
    - Mês
    - Média da variação percentual
    - Mediana da variação percentual
    - Número de observações
    - Percentual de meses positivos
    """
    df_season = df.copy()
    
    # Agrupar por mês
    seasonality = df_season.groupby('Month').agg({
        'Pct_Change': ['mean', 'median', 'std', 'count'],
        value_col: ['mean', 'median', 'min', 'max']
    }).round(4)
    
    # Calcular percentual de meses positivos
    df_season['Is_Positive'] = df_season['Pct_Change'] > 0
    positive_pct = df_season.groupby('Month')['Is_Positive'].mean() * 100
    
    seasonality['positive_pct'] = positive_pct
    
    return seasonality


def create_year_month_matrix(
    df: pd.DataFrame,
    value_col: str = "Pct_Change"
) -> pd.DataFrame:
    """
    Cria uma matriz de variação percentual por ano e mês.
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

    month_names = {
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

    df_matrix = df_matrix.rename(columns=month_names)

    ordered_months = [
        "Jan", "Fev", "Mar", "Abr",
        "Mai", "Jun", "Jul", "Ago",
        "Set", "Out", "Nov", "Dez"
    ]

    existing_months = [
        month for month in ordered_months
        if month in df_matrix.columns
    ]

    return df_matrix[existing_months]