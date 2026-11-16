"""
"Sobre o ativo": texto descritivo de cada ativo do catálogo (pedido de 16/11/2026,
inspirado nas seções "Sobre" de portais de investimento, sem indicação de compra).

- Os textos ficam em data/perfis_ativos/*.json, um arquivo por grupo de ativos, com:
  o que é o ativo, origem e história, o que observar no histórico e as fontes.
- As informações do período são calculadas com os dados diários já carregados na
  Análise Individual: última cotação, mínima e máxima em 12 meses, variação em 12
  meses e, para ativos com preço, uma aplicação hipotética de 1.000 há 12 meses.
  Nada é previsão; os números descrevem o passado.

Sem Streamlit.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

import pandas as pd

from core.currency import CurrencyInfo

PROFILES_DIR = Path(__file__).resolve().parent.parent / "data" / "perfis_ativos"
REVIEWED_ON = "16/11/2026"
WINDOW_DAYS = 365
MIN_WINDOW_DAYS = 330          # abaixo disso, a janela não é chamada de "12 meses"
HYPOTHETICAL_AMOUNT = 1000.0

PROFILE_NOTE = (
    "Texto descritivo, para contexto. Não é recomendação de investimento e não "
    "indica se o ativo está caro ou barato."
)


@dataclass(frozen=True)
class AssetProfile:
    ticker: str
    about: tuple[str, ...]
    history: tuple[str, ...]
    watch: str
    sources: tuple[tuple[str, str], ...]


def load_profiles(directory: Path | str = PROFILES_DIR) -> dict[str, AssetProfile]:
    """Todos os perfis da pasta; pasta ausente devolve um dicionário vazio."""
    directory = Path(directory)
    profiles: dict[str, AssetProfile] = {}
    if not directory.exists():
        return profiles
    for path in sorted(directory.glob("*.json")):
        for ticker, raw in json.loads(path.read_text(encoding="utf-8")).items():
            if ticker in profiles:
                raise ValueError(f"Perfil duplicado: {ticker} ({path.name}).")
            profiles[ticker] = AssetProfile(
                ticker=ticker,
                about=tuple(raw["sobre"]),
                history=tuple(raw["historia"]),
                watch=raw["observar"],
                sources=tuple((name, url) for name, url in raw["fontes"]),
            )
    return profiles


def get_profile(ticker: str, profiles: Mapping[str, AssetProfile]) -> Optional[AssetProfile]:
    return profiles.get(str(ticker or "").strip().upper())


# ------------------------------------------------------------------ informações do período
def _number(value: float) -> str:
    """Padrão brasileiro; mais casas decimais para valores pequenos (ex.: 0,1523)."""
    decimals = 4 if abs(value) < 1 else 2
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def _value(value: float, unit: CurrencyInfo) -> str:
    if unit.kind == "rate":
        return f"{_number(value)}% ao ano"
    if unit.kind == "points":
        return f"{_number(value)} pontos"
    return f"{unit.prefix}{_number(value)}"


def _pct(change: float) -> str:
    sign = "+" if change > 0 else ""
    return f"{sign}{change * 100:.2f}%".replace(".", ",")


def _date(ts: pd.Timestamp) -> str:
    return ts.strftime("%d/%m/%Y")


def period_facts(daily: Optional[pd.DataFrame], unit: CurrencyInfo) -> list[str]:
    """
    Frases com números do período carregado (colunas Date e Close, frequência diária).
    Devolve lista vazia sem dados válidos.
    """
    if daily is None or daily.empty or "Close" not in daily or "Date" not in daily:
        return []
    data = daily[["Date", "Close"]].copy()
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.dropna().sort_values("Date")
    data = data[data["Close"].map(lambda v: math.isfinite(float(v)))]
    if data.empty:
        return []

    last = data.iloc[-1]
    facts = [f"Última cotação no período carregado: {_value(float(last['Close']), unit)}, em {_date(last['Date'])}."]

    start = last["Date"] - pd.Timedelta(days=WINDOW_DAYS)
    window = data[data["Date"] >= start]
    span = (window["Date"].iloc[-1] - window["Date"].iloc[0]).days
    if len(window) < 2 or span < 1:
        return facts
    full_year = span >= MIN_WINDOW_DAYS
    if full_year:
        label = "Nos últimos 12 meses"
    else:
        label = f"Nos {span} dias carregados" if span > 1 else "No 1 dia carregado"

    low = window.loc[window["Close"].idxmin()]
    high = window.loc[window["Close"].idxmax()]
    facts.append(
        f"{label}: mínima de {_value(float(low['Close']), unit)} em {_date(low['Date'])} "
        f"e máxima de {_value(float(high['Close']), unit)} em {_date(high['Date'])}."
    )

    first = float(window["Close"].iloc[0])
    final = float(last["Close"])
    if unit.kind == "rate":
        diff = final - first
        facts.append(
            f"{label}, a taxa {'subiu' if diff > 0 else 'caiu' if diff < 0 else 'ficou estável'}"
            f"{'' if diff == 0 else f' {abs(diff):.2f} ponto(s) percentual(is)'.replace('.', ',')}."
        )
        return facts
    if first <= 0:
        return facts
    change = final / first - 1
    facts.append(f"{label}, a variação foi de {_pct(change)}.")
    if unit.kind == "price" and full_year:
        amount = HYPOTHETICAL_AMOUNT * (1 + change)
        facts.append(
            f"Uma aplicação hipotética de {_value(HYPOTHETICAL_AMOUNT, unit)} feita há 12 meses "
            f"valeria cerca de {_value(amount, unit)}, considerando só o preço de fechamento, "
            "sem dividendos, taxas, impostos ou câmbio."
        )
    return facts
