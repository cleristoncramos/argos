"""
Tendência histórica: retorno móvel e razão de desempenho (Plano 2, Bloco 6).

Funções puras, em DECIMAL (0.10 = 10%). Só estes dois recursos: sem regressão
de tendência e sem detecção automática de cruzamentos [D N07]. Os rótulos
dizem "tendência histórica": descrevem o passado, sem previsão.

O retorno móvel usa fechamentos mensais (último valor de cada mês); o mês em
andamento fica de fora. Antes de haver observações para a janela, o valor é
NaN, nunca zero.
"""

from typing import Dict, Optional, TypeVar, Union

import numpy as np
import pandas as pd

from core.seasonality import monthly_closes

PandasObject = TypeVar("PandasObject", pd.Series, pd.DataFrame)

TREND_WINDOWS = (3, 6, 12)

TREND_DISCLAIMER = (
    "Tendência histórica: descreve o que já ocorreu no período analisado. "
    "A tendência passada pode mudar, e os dados não permitem concluir que um "
    "ativo continuará acima ou abaixo do outro."
)

RATIO_START_NOTE = (
    "A razão de desempenho depende da data inicial: os dois ativos partem de "
    "100 na primeira data em que ambos têm dados, e um cruzamento da linha "
    "por zero pode mudar se o período mudar. O retorno móvel é menos sensível "
    "ao ponto de partida e deve ser lido junto com a razão."
)

ROLLING_NOTE = (
    "O retorno móvel mostra, para cada mês, quanto o ativo variou nos meses "
    "da janela escolhida, usando o último fechamento de cada mês. O mês em "
    "andamento não entra, e meses sem observações suficientes ficam vazios."
)


def rolling_label(window: int) -> str:
    """Rótulo com a janela sempre visível, ex.: "retorno móvel de 12 meses"."""
    unit = "mês" if window == 1 else "meses"
    return f"retorno móvel de {window} {unit}"


def _check_window(window: int) -> None:
    if isinstance(window, bool) or not isinstance(window, (int, np.integer)) or window < 1:
        raise ValueError("A janela deve ser um número inteiro de meses, maior ou igual a 1.")


def monthly_close_table(
    asset_data: Dict[str, pd.DataFrame],
    value_col: str = "Value",
    date_col: str = "Date",
    as_of: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """
    Fechamentos mensais por ativo (uma coluna por ativo), em calendário
    mensal contínuo. Meses sem dado e o mês em andamento ficam NaN.
    """
    series = {}

    for symbol, frame in asset_data.items():
        closes = monthly_closes(frame, value_col, date_col, as_of)
        if not closes.empty:
            series[symbol] = closes

    if not series:
        return pd.DataFrame()

    table = pd.DataFrame(series)
    full_range = pd.period_range(table.index.min(), table.index.max(), freq="M")

    return table.reindex(full_range)


def rolling_return(close: PandasObject, window: int) -> PandasObject:
    """Retorno móvel: P_t / P_(t-window) - 1, em decimal. NaN sem histórico."""
    _check_window(window)
    previous = close.shift(window)
    return close / previous.where(previous > 0) - 1


def rolling_return_gap(
    close_a: pd.Series,
    close_b: pd.Series,
    window: int,
) -> pd.Series:
    """
    Diferença de retorno móvel entre dois ativos (A menos B), em decimal:
    0.05 equivale a 5 pontos percentuais.
    """
    return rolling_return(close_a, window) - rolling_return(close_b, window)


def rebase_common_start(table: pd.DataFrame) -> pd.DataFrame:
    """
    Recoloca todas as colunas em base 100 na primeira data em que todas têm
    valor. Antes dessa data as linhas são descartadas.
    """
    valid = table.dropna()

    if valid.empty:
        raise ValueError("Os ativos não têm nenhuma data em comum com dados.")

    base = valid.iloc[0]

    if (base <= 0).any():
        raise ValueError("Os valores da data inicial devem ser maiores que zero.")

    return table.loc[valid.index[0]:] / base * 100


def performance_ratio(base100_a: pd.Series, base100_b: pd.Series) -> pd.Series:
    """
    Razão de desempenho I_A / I_B - 1, em decimal; 0 significa desempenho
    igual desde a data inicial. NaN onde falta valor ou I_B não é positivo.
    """
    a, b = base100_a.align(base100_b)
    return a / b.where(b > 0) - 1