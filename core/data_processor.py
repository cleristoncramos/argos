import pandas as pd


OHLC_COLUMNS = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara os dados de mercado para análise.

    Mantém, quando disponíveis:
    - Date
    - Open
    - High
    - Low
    - Close
    - Volume

    Também cria as colunas derivadas Year, Month e YearMonth.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df_processed = df.copy()

    if "Date" not in df_processed.columns:
        raise ValueError("A coluna obrigatória 'Date' não foi encontrada.")

    df_processed["Date"] = pd.to_datetime(
        df_processed["Date"],
        errors="coerce",
    )

    df_processed = df_processed.dropna(
        subset=["Date"],
    )

    available_columns = [
        column
        for column in OHLC_COLUMNS
        if column in df_processed.columns
    ]

    df_processed = df_processed[available_columns].copy()

    df_processed = df_processed.sort_values(
        "Date",
    ).reset_index(
        drop=True,
    )

    df_processed["Year"] = df_processed["Date"].dt.year
    df_processed["Month"] = df_processed["Date"].dt.month
    df_processed["YearMonth"] = (
        df_processed["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    return df_processed


def aggregate_by_frequency(
    df: pd.DataFrame,
    frequency: str = "Mensal",
) -> pd.DataFrame:
    """
    Agrega dados OHLCV por frequência.

    Regras financeiras de agregação:
    - Open: primeiro preço do período.
    - High: maior preço do período.
    - Low: menor preço do período.
    - Close: último preço do período.
    - Volume: soma do volume do período.

    Frequências suportadas:
    - Diário
    - Semanal
    - Mensal
    """
    if df is None or df.empty:
        return pd.DataFrame()

    if "Date" not in df.columns:
        raise ValueError("A coluna obrigatória 'Date' não foi encontrada.")

    df_agg = df.copy()

    df_agg["Date"] = pd.to_datetime(
        df_agg["Date"],
        errors="coerce",
    )

    df_agg = df_agg.dropna(
        subset=["Date"],
    ).sort_values(
        "Date",
    ).reset_index(
        drop=True,
    )

    if frequency == "Diário":
        df_agg["Year"] = df_agg["Date"].dt.year
        df_agg["Month"] = df_agg["Date"].dt.month
        df_agg["YearMonth"] = (
            df_agg["Date"]
            .dt.to_period("M")
            .astype(str)
        )
        return df_agg

    if frequency == "Semanal":
        df_agg["Period"] = df_agg["Date"].dt.to_period("W")

    elif frequency == "Mensal":
        df_agg["Period"] = df_agg["Date"].dt.to_period("M")

    else:
        raise ValueError(
            f"Frequência não suportada: {frequency}"
        )

    aggregation_rules = {
        "Date": "last",
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }

    aggregation_rules = {
        column: operation
        for column, operation in aggregation_rules.items()
        if column in df_agg.columns
    }

    df_agg = (
        df_agg
        .groupby(
            "Period",
            as_index=False,
        )
        .agg(
            aggregation_rules,
        )
    )

    df_agg["Date"] = pd.to_datetime(
        df_agg["Date"],
        errors="coerce",
    )

    df_agg = df_agg.sort_values(
        "Date",
    ).reset_index(
        drop=True,
    )

    df_agg["Year"] = df_agg["Date"].dt.year
    df_agg["Month"] = df_agg["Date"].dt.month
    df_agg["YearMonth"] = (
        df_agg["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    return df_agg


def select_primary_variable(
    df: pd.DataFrame,
    primary_var: str = "Close",
) -> pd.DataFrame:
    """
    Preserva as colunas OHLC disponíveis e cria `Value` como uma cópia
    da variável principal para manter compatibilidade com análises,
    métricas e visualizações que utilizam a coluna Value.

    Por padrão:
    - Value recebe os valores de Close.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    required_columns = [
        "Date",
        primary_var,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes: {missing_columns}"
        )

    columns_to_keep = [
        column
        for column in OHLC_COLUMNS
        if column in df.columns
    ]

    df_selected = df[columns_to_keep].copy()

    df_selected["Date"] = pd.to_datetime(
        df_selected["Date"],
        errors="coerce",
    )

    df_selected = df_selected.dropna(
        subset=["Date"],
    ).sort_values(
        "Date",
    ).reset_index(
        drop=True,
    )

    df_selected["Value"] = df_selected[primary_var]

    df_selected["Year"] = df_selected["Date"].dt.year
    df_selected["Month"] = df_selected["Date"].dt.month
    df_selected["YearMonth"] = (
        df_selected["Date"]
        .dt.to_period("M")
        .astype(str)
    )

    return df_selected