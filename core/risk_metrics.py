import numpy as np
import pandas as pd


def calculate_drawdown(
    df: pd.DataFrame,
    value_col: str = "Value",
) -> pd.DataFrame:
    """
    Calcula o pico acumulado e o drawdown de uma série de preços.

    Running_Peak:
        Maior valor observado até cada data.

    Drawdown:
        Queda percentual do valor atual em relação ao maior pico
        observado anteriormente ou na própria data.

    Exemplo:
        Preços: 100, 120, 90
        Pico:   100, 120, 120
        DD:     0%,  0%, -25%
    """
    if value_col not in df.columns:
        raise ValueError(
            f"A coluna '{value_col}' não existe no DataFrame."
        )

    if df.empty:
        result = df.copy()
        result["Running_Peak"] = pd.Series(dtype="float64")
        result["Drawdown"] = pd.Series(dtype="float64")
        return result

    result = df.copy()

    # Garante que preços inválidos não gerem divisão por zero
    values = pd.to_numeric(
        result[value_col],
        errors="coerce",
    )

    if values.isna().any():
        raise ValueError(
            f"A coluna '{value_col}' possui valores não numéricos ou ausentes."
        )

    if (values <= 0).any():
        raise ValueError(
            f"A coluna '{value_col}' deve conter valores maiores que zero."
        )

    # Maior preço alcançado até cada observação
    result["Running_Peak"] = values.cummax()

    # Queda percentual em relação ao maior pico anterior
    result["Drawdown"] = (
        values / result["Running_Peak"] - 1
    )

    return result


def get_max_drawdown(
    df: pd.DataFrame,
    drawdown_col: str = "Drawdown",
) -> float | None:
    """
    Retorna o maior drawdown da série.

    O resultado é negativo ou zero:
    - 0.0: não houve queda em relação a pico anterior;
    - -0.25: queda máxima de 25%.
    """
    if drawdown_col not in df.columns:
        raise ValueError(
            f"A coluna '{drawdown_col}' não existe no DataFrame."
        )

    if df.empty or df[drawdown_col].dropna().empty:
        return None

    return float(df[drawdown_col].min())