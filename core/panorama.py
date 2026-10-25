"""
Panorama descritivo de um grupo do catálogo (A3).

Funções puras, sem Streamlit. Para cada ativo, resume a série DIÁRIA do
período escolhido: variação no período e em 12 meses, volatilidade
anualizada, queda máxima, histórico disponível e quantidade de alertas de
qualidade dos dados. Retorno e risco ficam sempre lado a lado.

Regras (detalhes em docs/metodologia_de_calculo.md, seção 5.2):
- Ativo sem dados ou com falha na consulta fica com as métricas vazias,
  nunca com zero.
- Taxas de juros (yields) não têm variação, volatilidade nem queda
  calculadas: a variação percentual do nível da taxa não é retorno.
- A ordenação inicial é por nome; ordenar por uma métrica deixa os vazios
  sempre no fim. Nenhum ativo é destacado como "melhor".
"""

from datetime import date
from typing import Iterable, Mapping, Optional

import numpy as np
import pandas as pd

from core.config import ANNUALIZATION_FACTORS
from core.currency import currency_info
from core.data_quality import assess_data_quality
from core.trailing_returns import TrailingWindow, trailing_returns

# Tolerância para considerar que o histórico começa no início pedido.
START_TOLERANCE_DAYS = 10

METRIC_COLUMNS = [
    "Variação no período", "Variação em 12 meses", "Volatilidade anualizada", "Queda máxima",
]

COLUMNS = [
    "Ticker", "Nome", "Status", "Início", "Fim", "Começa depois", *METRIC_COLUMNS, "Alertas",
]

STATUS_OK = "ok"
STATUS_NO_DATA = "sem dados"
STATUS_RATE = "taxa"

_TWELVE_MONTHS = (TrailingWindow("12 meses", years=1),)


def _empty_row(asset: Mapping[str, str], status: str) -> dict:
    row = {column: None for column in COLUMNS}
    row.update({"Ticker": asset["ticker"], "Nome": asset["name"], "Status": status, "Começa depois": False})
    return row


def asset_overview(
    df: Optional[pd.DataFrame],
    asset: Mapping[str, str],
    requested_start: Optional[date] = None,
) -> dict:
    """Uma linha do panorama para o ativo, com as colunas de `COLUMNS`."""
    if df is None or df.empty or "Close" not in df.columns or "Date" not in df.columns:
        return _empty_row(asset, STATUS_NO_DATA)

    data = pd.DataFrame({
        "Date": pd.to_datetime(df["Date"], errors="coerce"),
        "Close": pd.to_numeric(df["Close"], errors="coerce"),
    }).dropna()
    data = data[data["Close"] > 0].sort_values("Date").reset_index(drop=True)
    if len(data) < 2:
        return _empty_row(asset, STATUS_NO_DATA)

    first, last = data["Date"].iloc[0], data["Date"].iloc[-1]
    starts_late = (
        requested_start is not None
        and (first.date() - requested_start).days > START_TOLERANCE_DAYS
    )
    alerts = assess_data_quality(df, asset["ticker"], requested_start)

    if currency_info(asset["ticker"]).kind == "rate":
        row = _empty_row(asset, STATUS_RATE)
    else:
        closes = data["Close"]
        returns = closes.pct_change().dropna()
        drawdown = closes / closes.cummax() - 1
        twelve = trailing_returns(data, value_col="Close", windows=_TWELVE_MONTHS)
        row = _empty_row(asset, STATUS_OK)
        row.update({
            "Variação no período": float(closes.iloc[-1] / closes.iloc[0] - 1),
            "Variação em 12 meses": (
                float(twelve["Variação"].iloc[0]) if bool(twelve["Disponível"].iloc[0]) else None
            ),
            "Volatilidade anualizada": (
                float(returns.std() * np.sqrt(ANNUALIZATION_FACTORS["Diário"])) if len(returns) >= 2 else None
            ),
            "Queda máxima": float(drawdown.min()),
        })

    row.update({"Início": first, "Fim": last, "Começa depois": starts_late, "Alertas": len(alerts)})
    return row


def build_panorama(
    data_by_ticker: Mapping[str, Optional[pd.DataFrame]],
    assets: Iterable[Mapping[str, str]],
    requested_start: Optional[date] = None,
) -> pd.DataFrame:
    """Tabela do panorama, uma linha por ativo, ordenada por nome."""
    rows = [
        asset_overview(data_by_ticker.get(asset["ticker"]), asset, requested_start)
        for asset in assets
    ]
    table = pd.DataFrame(rows, columns=COLUMNS)
    return sort_panorama(table, "Nome")


def sort_panorama(table: pd.DataFrame, column: str, descending: bool = False) -> pd.DataFrame:
    """Ordena por uma coluna; valores vazios ficam sempre no fim."""
    if table.empty:
        return table
    key = (lambda s: s.str.casefold()) if column == "Nome" else None
    return table.sort_values(
        column, ascending=not descending, na_position="last", kind="stable", key=key,
    ).reset_index(drop=True)


def panorama_period(table: pd.DataFrame) -> Optional[tuple[pd.Timestamp, pd.Timestamp]]:
    """Menor início e maior fim entre os ativos com dados."""
    with_data = table[table["Status"] != STATUS_NO_DATA]
    if with_data.empty:
        return None
    return with_data["Início"].min(), with_data["Fim"].max()
