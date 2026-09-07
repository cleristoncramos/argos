from typing import Dict, List

import pandas as pd


def parse_symbols(
    symbols_input: str,
    min_symbols: int = 2,
    max_symbols: int = 5,
) -> List[str]:
    """
    Converte texto separado por vírgulas em símbolos únicos.
    """
    symbols = [
        symbol.strip().upper()
        for symbol in symbols_input.split(",")
        if symbol.strip()
    ]

    unique_symbols = list(dict.fromkeys(symbols))

    if len(unique_symbols) < min_symbols:
        raise ValueError(
            f"Informe pelo menos {min_symbols} ativos válidos."
        )

    if len(unique_symbols) > max_symbols:
        raise ValueError(
            f"Informe no máximo {max_symbols} ativos por comparação."
        )

    return unique_symbols


def normalize_to_base_100(
    df: pd.DataFrame,
    value_col: str = "Value",
) -> pd.DataFrame:
    """
    Normaliza uma série para base 100 no primeiro valor válido.
    """
    if value_col not in df.columns:
        raise ValueError(
            f"A coluna '{value_col}' não existe no DataFrame."
        )

    result = df.copy()
    valid_values = result[value_col].dropna()

    if valid_values.empty:
        raise ValueError(
            f"A coluna '{value_col}' não possui valores válidos."
        )

    base_value = valid_values.iloc[0]

    if base_value <= 0:
        raise ValueError(
            "O primeiro valor válido deve ser maior que zero."
        )

    result["Base_100"] = (
        result[value_col] / base_value
    ) * 100

    return result


def build_price_table(
    asset_data: Dict[str, pd.DataFrame],
    value_col: str = "Value",
) -> pd.DataFrame:
    """
    Une as séries dos ativos por data usando união externa.
    """
    frames = []

    for symbol, df in asset_data.items():
        if df.empty:
            continue

        required_columns = {"Date", value_col}

        if not required_columns.issubset(df.columns):
            continue

        frame = df[["Date", value_col]].copy()
        frame = frame.rename(columns={value_col: symbol})
        frames.append(frame)

    if not frames:
        return pd.DataFrame()

    result = frames[0]

    for frame in frames[1:]:
        result = result.merge(
            frame,
            on="Date",
            how="outer",
        )

    return result.sort_values("Date").reset_index(drop=True)


def build_base_100_table(
    asset_data: Dict[str, pd.DataFrame],
    value_col: str = "Value",
) -> pd.DataFrame:
    """
    Cria tabela de preços normalizados para base 100.
    """
    frames = []

    for symbol, df in asset_data.items():
        if df.empty:
            continue

        normalized = normalize_to_base_100(
            df,
            value_col=value_col,
        )

        frame = normalized[["Date", "Base_100"]].copy()
        frame = frame.rename(columns={"Base_100": symbol})
        frames.append(frame)

    if not frames:
        return pd.DataFrame()

    result = frames[0]

    for frame in frames[1:]:
        result = result.merge(
            frame,
            on="Date",
            how="outer",
        )

    return result.sort_values("Date").reset_index(drop=True)


def calculate_returns_table(
    price_table: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calcula retornos simples de cada ativo.
    """
    if price_table.empty:
        return pd.DataFrame()

    result = price_table.copy()

    asset_columns = [
        column
        for column in result.columns
        if column != "Date"
    ]

    result[asset_columns] = result[asset_columns].pct_change()

    return result


def calculate_correlation_matrix(
    returns_table: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calcula correlação entre os retornos dos ativos.
    """
    if returns_table.empty:
        return pd.DataFrame()

    asset_columns = [
        column
        for column in returns_table.columns
        if column != "Date"
    ]

    if not asset_columns:
        return pd.DataFrame()

    return returns_table[asset_columns].corr()


def create_comparison_summary(
    asset_data: Dict[str, pd.DataFrame],
    return_col: str = "Simple_Return",
) -> pd.DataFrame:
    """
    Cria resumo de desempenho dos ativos.
    """
    rows = []

    for symbol, df in asset_data.items():
        if df.empty or "Value" not in df.columns:
            continue

        values = df["Value"].dropna()

        if values.empty:
            continue

        total_return = (
            values.iloc[-1] / values.iloc[0] - 1
        )

        mean_return = None

        if return_col in df.columns:
            returns = df[return_col].dropna()

            if not returns.empty:
                mean_return = returns.mean()

        rows.append(
            {
                "Ativo": symbol,
                "Observações": len(values),
                "Primeiro valor": values.iloc[0],
                "Último valor": values.iloc[-1],
                "Retorno total": total_return,
                "Retorno médio": mean_return,
            }
        )

    return pd.DataFrame(rows)

def format_return_pct(value) -> str:
    """
    Converte um retorno decimal em texto percentual no padrão brasileiro.

    Exemplos:
    0.1701 -> 17,01%
    -0.25 -> -25,00%
    None ou NaN -> —
    """
    if value is None or pd.isna(value):
        return "—"

    percentage = value * 100

    return (
        f"{percentage:,.2f}%"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )