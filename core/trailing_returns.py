"""
Variação por janelas até a última observação (A1).

Funções puras, sem Streamlit. Para cada janela (1 mês, 3 meses, ..., 10
anos e "no ano"), compara o último valor disponível com o valor do início
da janela e informa as datas efetivamente usadas.

Regras (detalhes em docs/metodologia_de_calculo.md, seção 2.3):
- Base: a série recebida (na interface, o período carregado na barra
  lateral). Janelas mais longas que essa base ficam indisponíveis ("—").
- Data-alvo do início: último dia da série menos o prazo da janela; em
  "No ano", o último dia do ano anterior.
- Valor inicial: última observação na data-alvo ou antes dela. Se a série
  começa depois da data-alvo, mas dentro da tolerância, usa a primeira
  observação e marca a janela como ajustada.
- Variação acumulada: valor final / valor inicial - 1.
- Taxa equivalente ao ano: só em janelas de 1 ano ou mais, com o prazo
  efetivo em anos de calendário (anos completos mais a fração restante em
  dias / 365,25): (1 + variação) ^ (1 / anos) - 1. Assim, uma janela de
  exatamente 1 ano tem taxa anual igual à variação acumulada.
"""

from dataclasses import dataclass
from typing import Optional

import pandas as pd

# Tolerância para o início da série depois da data-alvo, em dias corridos.
# Para janelas de 1 ano ou mais, cobre os atalhos de período da barra
# lateral, que começam no primeiro dia do mês seguinte (core/periods.py).
SHORT_WINDOW_TOLERANCE_DAYS = 7
LONG_WINDOW_TOLERANCE_DAYS = 31


@dataclass(frozen=True)
class TrailingWindow:
    label: str
    months: int = 0
    years: int = 0
    year_to_date: bool = False

    @property
    def is_long(self) -> bool:
        """Janela de 1 ano ou mais: tem taxa equivalente ao ano."""
        return self.years >= 1


TRAILING_WINDOWS = (
    TrailingWindow("1 mês", months=1),
    TrailingWindow("3 meses", months=3),
    TrailingWindow("6 meses", months=6),
    TrailingWindow("No ano", year_to_date=True),
    TrailingWindow("1 ano", years=1),
    TrailingWindow("2 anos", years=2),
    TrailingWindow("3 anos", years=3),
    TrailingWindow("5 anos", years=5),
    TrailingWindow("10 anos", years=10),
)

COLUMNS = [
    "Janela", "Data-alvo", "Data inicial", "Data final", "Valor inicial",
    "Valor final", "Variação", "Taxa anual", "Disponível", "Ajustada",
]


def calendar_years(start: pd.Timestamp, end: pd.Timestamp) -> float:
    """Prazo em anos: anos de calendário completos mais a fração restante."""
    start, end = pd.Timestamp(start).normalize(), pd.Timestamp(end).normalize()
    full = end.year - start.year
    if start + pd.DateOffset(years=full) > end:
        full -= 1
    anchor = start + pd.DateOffset(years=full)
    return full + (end - anchor).days / 365.25


def window_target(end: pd.Timestamp, window: TrailingWindow) -> pd.Timestamp:
    """Data-alvo do início da janela."""
    end = pd.Timestamp(end).normalize()
    if window.year_to_date:
        return pd.Timestamp(year=end.year - 1, month=12, day=31)
    return end - pd.DateOffset(months=window.months, years=window.years)


def trailing_returns(
    df: pd.DataFrame,
    value_col: str = "Close",
    date_col: str = "Date",
    windows: tuple[TrailingWindow, ...] = TRAILING_WINDOWS,
) -> pd.DataFrame:
    """
    Uma linha por janela, com as colunas de `COLUMNS`. Variação e taxa em
    fração (0,10 = 10%). Janelas indisponíveis têm `Disponível=False` e
    valores vazios; a taxa anual fica vazia nas janelas menores que 1 ano.
    """
    if df is None or df.empty or value_col not in df.columns or date_col not in df.columns:
        return pd.DataFrame(columns=COLUMNS)

    data = pd.DataFrame({
        "Date": pd.to_datetime(df[date_col], errors="coerce"),
        "Value": pd.to_numeric(df[value_col], errors="coerce"),
    })
    data = data.dropna()
    data = data[data["Value"] > 0].sort_values("Date").reset_index(drop=True)
    if len(data) < 2:
        return pd.DataFrame(columns=COLUMNS)

    dates = data["Date"].dt.tz_localize(None) if data["Date"].dt.tz is not None else data["Date"]
    end_date = dates.iloc[-1]
    end_value = float(data["Value"].iloc[-1])
    first_date = dates.iloc[0]

    rows = []
    for window in windows:
        target = window_target(end_date, window)
        tolerance = LONG_WINDOW_TOLERANCE_DAYS if window.is_long else SHORT_WINDOW_TOLERANCE_DAYS
        before = dates[dates.dt.normalize() <= target]
        adjusted = False

        if not before.empty:
            position = before.index[-1]
        elif (first_date.normalize() - target).days <= tolerance:
            position, adjusted = 0, True
        else:
            position = None

        row = {
            "Janela": window.label, "Data-alvo": target, "Data inicial": None,
            "Data final": end_date, "Valor inicial": None, "Valor final": end_value,
            "Variação": None, "Taxa anual": None, "Disponível": False, "Ajustada": False,
        }
        if position is not None:
            start_date = dates.iloc[position]
            start_value = float(data["Value"].iloc[position])
            change = end_value / start_value - 1
            years = calendar_years(start_date, end_date)
            row.update({
                "Data inicial": start_date,
                "Valor inicial": start_value,
                "Variação": change,
                "Taxa anual": (1 + change) ** (1 / years) - 1 if window.is_long else None,
                "Disponível": True,
                "Ajustada": adjusted,
            })
        rows.append(row)

    return pd.DataFrame(rows, columns=COLUMNS)


def base_description(df: pd.DataFrame, date_col: str = "Date") -> Optional[tuple[pd.Timestamp, pd.Timestamp]]:
    """Primeira e última data da base usada (para o texto da interface)."""
    if df is None or df.empty or date_col not in df.columns:
        return None
    dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
    if dates.empty:
        return None
    return dates.min(), dates.max()
