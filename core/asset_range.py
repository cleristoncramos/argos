"""
Período disponível de um ativo, para limitar as datas no menu lateral (reunião de
10/11/2026, DL2-B). Funções puras, sem Streamlit; a busca de dados é injetada.

- Modo de demonstração: as datas vêm do manifesto dos dados salvos.
- Fora dele: uma busca mensal desde o início acha o primeiro e o último mês com dados, e
  duas buscas diárias, só nesses meses, acham o primeiro e o último pregão. Qualquer falha devolve None, e o menu
  segue sem limite (o aviso de histórico menor continua depois do carregamento).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable, Optional

import pandas as pd

EARLIEST = "1950-01-01"


@dataclass(frozen=True)
class AssetRange:
    first: date
    last: date


def _dates(frame: Optional[pd.DataFrame]) -> Optional[pd.Series]:
    if frame is None or frame.empty or "Date" not in frame.columns:
        return None
    datas = pd.to_datetime(frame["Date"], errors="coerce").dropna()
    return datas if not datas.empty else None


def range_from_frame(frame: Optional[pd.DataFrame]) -> Optional[AssetRange]:
    datas = _dates(frame)
    if datas is None:
        return None
    return AssetRange(datas.min().date(), datas.max().date())


def demo_range(ticker: str, manifest: dict) -> Optional[AssetRange]:
    """Datas do ativo no manifesto da demonstração; None se ele não estiver lá."""
    simbolo = str(ticker).strip().upper()
    for entrada in manifest.get("assets", []):
        if str(entrada.get("ticker", "")).upper() == simbolo:
            try:
                return AssetRange(date.fromisoformat(entrada["first_date"]), date.fromisoformat(entrada["last_date"]))
            except (KeyError, TypeError, ValueError):
                return None
    return None


def online_range(symbol: str, fetch: Callable, today: date) -> Optional[AssetRange]:
    """
    `fetch(symbol, start_date, end_date, interval)` devolve um DataFrame com coluna "Date"
    ou levanta exceção. Duas buscas pequenas: mensal (primeiro mês) e diária (primeiro dia).
    """
    fim = (today + timedelta(days=1)).isoformat()
    try:
        mensal = range_from_frame(fetch(symbol, EARLIEST, fim, "1mo"))
        if mensal is None:
            return None
        inicio_mes = mensal.first.replace(day=1)
        diario = range_from_frame(fetch(symbol, inicio_mes.isoformat(),
                                        (inicio_mes + timedelta(days=45)).isoformat(), "1d"))
        # A barra mensal é rotulada no início do mês: o último pregão sai de uma busca diária.
        ultimo_mes = range_from_frame(fetch(symbol, mensal.last.replace(day=1).isoformat(), fim, "1d"))
    except Exception:  # noqa: BLE001 - qualquer falha de rede ou de dados: sem limite
        return None
    primeiro = diario.first if diario is not None else mensal.first
    ultimo = ultimo_mes.last if ultimo_mes is not None else mensal.last
    return AssetRange(primeiro, min(ultimo, today))


def clamp_period(start: date, end: date, rng: Optional[AssetRange]) -> tuple[date, date, bool]:
    """Ajusta o início ao primeiro dado disponível; devolve (início, fim, ajustado)."""
    if rng is None or start >= rng.first:
        return start, end, False
    return rng.first, max(end, rng.first), True


def range_caption(rng: AssetRange) -> str:
    return f"📅 Dados disponíveis de {rng.first:%d/%m/%Y} a {rng.last:%d/%m/%Y}."


def adjusted_note(rng: AssetRange, requested_start: date) -> str:
    return (f"⚠️ O histórico deste ativo começa em {rng.first:%d/%m/%Y}. O período escolhido começaria em "
            f"{requested_start:%d/%m/%Y}, então a análise usa os dados a partir de {rng.first:%d/%m/%Y}.")
