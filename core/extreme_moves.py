"""
Maiores altas e quedas do período (A8).

Funções puras, sem Streamlit. Lista as maiores variações positivas e
negativas entre fechamentos consecutivos da série na frequência escolhida,
com o período e as datas de cada uma, e conta quantas variações foram
positivas, negativas ou nulas.

Descreve apenas os extremos observados: não calcula quanto esses períodos
contribuíram para o resultado total (detalhes em
docs/metodologia_de_calculo.md, seção 2.4).
"""

import pandas as pd

from core.data_processor import period_end

DEFAULT_TOP = 5

# Diferença máxima, em dias corridos, entre o fim do calendário do período e
# a última observação para o período ainda ser considerado completo. A semana
# termina no domingo: sexta-feira (2 dias) ou quinta com feriado (3 dias). Nos
# demais períodos, fins de semana somados a feriados chegam a 4 dias.
PARTIAL_TOLERANCE_DAYS = {"Semanal": 3}
DEFAULT_PARTIAL_TOLERANCE_DAYS = 4

MONTH_ABBREVIATIONS = (
    "jan", "fev", "mar", "abr", "mai", "jun",
    "jul", "ago", "set", "out", "nov", "dez",
)

COLUMNS = [
    "Período", "Data inicial", "Valor inicial", "Data final", "Valor final",
    "Variação", "Parcial",
]


def period_label(date, frequency: str) -> str:
    """Rótulo legível do período que termina no fechamento `date`."""
    date = pd.Timestamp(date)
    if frequency == "Semanal":
        return f"semana até {date:%d/%m/%Y}"
    if frequency == "Mensal":
        return f"{MONTH_ABBREVIATIONS[date.month - 1]}/{date.year}"
    if frequency == "Semestral":
        return f"{1 if date.month <= 6 else 2}º sem. {date.year}"
    if frequency == "Anual":
        return str(date.year)
    return f"{date:%d/%m/%Y}"


def last_period_is_partial(last_date, frequency: str, last_observation=None) -> bool:
    """
    Indica se o último período ainda não terminou nos dados: o fim do
    calendário do período fica mais dias depois da última observação do que a
    tolerância da frequência. Na frequência diária, nunca.
    """
    if frequency == "Diário":
        return False
    reference = pd.Timestamp(last_observation if last_observation is not None else last_date)
    end = period_end(pd.Series([pd.Timestamp(last_date)]), frequency).iloc[0]
    tolerance = PARTIAL_TOLERANCE_DAYS.get(frequency, DEFAULT_PARTIAL_TOLERANCE_DAYS)
    return (end - reference.normalize()).days > tolerance


def period_changes(
    df: pd.DataFrame,
    frequency: str,
    value_col: str = "Value",
    date_col: str = "Date",
    last_observation=None,
) -> pd.DataFrame:
    """
    Variação entre fechamentos consecutivos, uma linha por período, com as
    colunas de `COLUMNS`. `last_observation`: data da última observação
    diária, usada para marcar o último período como parcial.
    """
    if df is None or df.empty or value_col not in df.columns or date_col not in df.columns:
        return pd.DataFrame(columns=COLUMNS)

    data = pd.DataFrame({
        "Date": pd.to_datetime(df[date_col], errors="coerce"),
        "Value": pd.to_numeric(df[value_col], errors="coerce"),
    }).dropna()
    data = data[data["Value"] > 0].sort_values("Date").reset_index(drop=True)
    if len(data) < 2:
        return pd.DataFrame(columns=COLUMNS)

    previous = data.iloc[:-1].reset_index(drop=True)
    current = data.iloc[1:].reset_index(drop=True)
    result = pd.DataFrame({
        "Período": [period_label(d, frequency) for d in current["Date"]],
        "Data inicial": previous["Date"],
        "Valor inicial": previous["Value"],
        "Data final": current["Date"],
        "Valor final": current["Value"],
        "Variação": current["Value"] / previous["Value"] - 1,
        "Parcial": False,
    })
    result.loc[result.index[-1], "Parcial"] = last_period_is_partial(
        current["Date"].iloc[-1], frequency, last_observation
    )
    return result


def extreme_moves(changes: pd.DataFrame, top: int = DEFAULT_TOP) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(maiores altas, maiores quedas): só variações positivas e só negativas."""
    if changes.empty:
        return changes, changes
    highs = changes[changes["Variação"] > 0].sort_values("Variação", ascending=False, kind="stable")
    lows = changes[changes["Variação"] < 0].sort_values("Variação", kind="stable")
    return highs.head(top).reset_index(drop=True), lows.head(top).reset_index(drop=True)


def direction_counts(changes: pd.DataFrame) -> dict[str, int]:
    """Quantidade de variações positivas, negativas e nulas."""
    values = changes["Variação"] if not changes.empty else pd.Series(dtype=float)
    return {
        "total": int(len(values)),
        "up": int((values > 0).sum()),
        "down": int((values < 0).sum()),
        "flat": int((values == 0).sum()),
    }
