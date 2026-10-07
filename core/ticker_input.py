"""Normalização e validação de tickers digitados livremente."""

import re
from dataclasses import dataclass
from typing import Callable

# Exemplos aceitos: AAPL, PETR4.SA, BRK-B, BTC-USD, ^BVSP, GC=F, USDBRL=X
TICKER_PATTERN = re.compile(r"^\^?[A-Z0-9]{1,12}([.\-][A-Z0-9]{1,6})?(=[A-Z])?$")


@dataclass(frozen=True)
class TickerValidation:
    ok: bool
    ticker: str
    message: str


def normalize_ticker(raw) -> str:
    """Remove espaços e converte para maiúsculas."""
    if raw is None:
        return ""
    return re.sub(r"\s+", "", str(raw)).upper()


def is_valid_ticker_format(ticker: str) -> bool:
    return bool(TICKER_PATTERN.match(ticker))


def validate_ticker(raw, fetch: Callable[[str], object]) -> TickerValidation:
    """
    `fetch(ticker)` deve devolver um DataFrame com dados recentes (ou None/vazio).
    Exceções da fonte são tratadas como indisponibilidade temporária.
    """
    ticker = normalize_ticker(raw)

    if not ticker:
        return TickerValidation(False, "", "Digite um ticker.")

    if not is_valid_ticker_format(ticker):
        return TickerValidation(
            False, ticker,
            f"Formato inválido: '{ticker}'. Use letras e números, com sufixos como "
            ".SA, -USD ou =X (ex.: PETR4.SA, AAPL, BTC-USD, ^BVSP).",
        )

    try:
        data = fetch(ticker)
    except Exception:
        return TickerValidation(
            False, ticker,
            "Não foi possível consultar a fonte de dados agora. Tente novamente em instantes.",
        )

    if data is None or getattr(data, "empty", False):
        return TickerValidation(
            False, ticker,
            f"Ticker '{ticker}' não encontrado ou sem dados recentes na fonte "
            "(Yahoo Finance). Confira o código; ações brasileiras terminam em .SA.",
        )

    return TickerValidation(True, ticker, f"Ticker '{ticker}' encontrado.")