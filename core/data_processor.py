import pandas as pd
from typing import Optional


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara o DataFrame para análise:
    - Seleciona colunas relevantes
    - Cria colunas derivadas (Ano, Mês)
    - Ordena por data
    """
    # Copiar para não modificar o original
    df_processed = df.copy()
    
    # Selecionar colunas principais (ajustar conforme disponibilidade)
    columns_to_keep = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    available_columns = [col for col in columns_to_keep if col in df_processed.columns]
    df_processed = df_processed[available_columns]
    
    # Criar colunas derivadas
    df_processed['Year'] = df_processed['Date'].dt.year
    df_processed['Month'] = df_processed['Date'].dt.month
    df_processed['YearMonth'] = df_processed['Date'].dt.to_period('M').astype(str)
    
    # Ordenar por data
    df_processed = df_processed.sort_values('Date').reset_index(drop=True)
    
    return df_processed


def aggregate_by_frequency(
    df: pd.DataFrame,
    frequency: str = "Mensal"
) -> pd.DataFrame:
    """
    Agrega os dados pela frequência especificada.

    Frequências suportadas:
    - Diário
    - Semanal
    - Mensal
    """

    df_agg = df.copy()

    # Garantir ordenação cronológica
    df_agg = df_agg.sort_values("Date").reset_index(drop=True)

    if frequency == "Diário":
        return df_agg

    if frequency == "Semanal":
        df_agg["Period"] = df_agg["Date"].dt.to_period("W")

    elif frequency == "Mensal":
        df_agg["Period"] = df_agg["Date"].dt.to_period("M")

    else:
        raise ValueError(f"Frequência não suportada: {frequency}")

    # Agregação correta dos dados
    aggregation = {
        "Date": "last",
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }

    # Usar somente colunas que realmente existem
    aggregation = {
        column: operation
        for column, operation in aggregation.items()
        if column in df_agg.columns
    }

    df_agg = (
        df_agg
        .groupby("Period", as_index=False)
        .agg(aggregation)
    )

    # Recriar as colunas derivadas após a agregação
    df_agg["Date"] = pd.to_datetime(df_agg["Date"])
    df_agg["Year"] = df_agg["Date"].dt.year
    df_agg["Month"] = df_agg["Date"].dt.month
    df_agg["YearMonth"] = df_agg["Date"].dt.to_period("M").astype(str)

    return df_agg


def select_primary_variable(
    df: pd.DataFrame,
    primary_var: str = "Close"
) -> pd.DataFrame:
    """
    Seleciona a variável principal para análise.
    Por padrão, utiliza o preço de fechamento.
    """

    required_columns = ["Date", primary_var]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {missing_columns}"
        )

    df_selected = df[required_columns].copy()

    df_selected = df_selected.rename(
        columns={primary_var: "Value"}
    )

    # Recriar colunas derivadas caso não existam
    df_selected["Date"] = pd.to_datetime(df_selected["Date"])
    df_selected["Year"] = df_selected["Date"].dt.year
    df_selected["Month"] = df_selected["Date"].dt.month
    df_selected["YearMonth"] = (
        df_selected["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    return df_selected