"""
Verificações de comparabilidade entre ativos: períodos históricos
divergentes e diferenças de natureza (moeda, taxa x preço, calendário).
Sem dependência de UI.
"""

from dataclasses import dataclass
from datetime import date
from typing import Iterable

import pandas as pd

from core.currency import currency_info, is_crypto

START_TOLERANCE_DAYS = 10
END_TOLERANCE_DAYS = 7

# Grupos com exposição sobreposta (correlação alta por construção)
OVERLAP_GROUPS = [
    {"SPY", "VOO", "VTI", "^GSPC"},
    {"BABA", "9988.HK"},
    {"DIA", "^DJI"},
    {"IWM", "^RUT"},
]


@dataclass(frozen=True)
class AssetSpan:
    ticker: str
    start: date
    end: date
    observations: int


@dataclass(frozen=True)
class PeriodCheck:
    spans: tuple
    common_start: date | None
    common_end: date | None
    start_spread_days: int
    end_spread_days: int
    divergent: bool
    has_common_period: bool
    shortest_history: str | None
    longest_history: str | None


def build_spans(daily_dates: dict[str, Iterable]) -> list[AssetSpan]:
    """Primeira e última data diária de cada ativo (ativos sem datas são ignorados)."""
    spans = []
    for ticker, dates in daily_dates.items():
        series = pd.to_datetime(pd.Series(list(dates)), errors="coerce").dropna()
        if series.empty:
            continue
        spans.append(
            AssetSpan(ticker, series.min().date(), series.max().date(), int(len(series)))
        )
    return spans


def check_period_divergence(
    spans: list[AssetSpan],
    start_tolerance_days: int = START_TOLERANCE_DAYS,
    end_tolerance_days: int = END_TOLERANCE_DAYS,
) -> PeriodCheck:
    if not spans:
        return PeriodCheck((), None, None, 0, 0, False, False, None, None)

    common_start = max(s.start for s in spans)
    common_end = min(s.end for s in spans)
    start_spread = (common_start - min(s.start for s in spans)).days
    end_spread = (max(s.end for s in spans) - common_end).days

    shortest = max(spans, key=lambda s: s.start).ticker
    longest = min(spans, key=lambda s: s.start).ticker

    return PeriodCheck(
        spans=tuple(spans),
        common_start=common_start,
        common_end=common_end,
        start_spread_days=start_spread,
        end_spread_days=end_spread,
        divergent=(start_spread > start_tolerance_days or end_spread > end_tolerance_days),
        has_common_period=common_start < common_end,
        shortest_history=shortest,
        longest_history=longest,
    )


def _fmt(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else "—"


def comparison_notes(
    period_check: PeriodCheck,
    tickers: list[str],
    frequency: str,
    aligned_to_common: bool = False,
) -> list[tuple[str, str]]:
    """Lista de (nível, texto), com nível em {"error", "warning", "info"}."""
    notes: list[tuple[str, str]] = []

    if period_check.spans and not period_check.has_common_period:
        notes.append((
            "error",
            "Os ativos selecionados não possuem nenhum período em comum no intervalo "
            "consultado; a comparação direta não é possível.",
        ))
    elif period_check.divergent:
        common = f"{_fmt(period_check.common_start)} a {_fmt(period_check.common_end)}"
        if aligned_to_common:
            notes.append((
                "info",
                f"Os ativos foram alinhados ao período comum ({common}). Seus históricos "
                "originais eram diferentes; os resultados valem apenas para esse intervalo.",
            ))
        else:
            notes.append((
                "warning",
                f"Os ativos possuem períodos históricos diferentes: {period_check.shortest_history} "
                f"começa em {_fmt(period_check.common_start)}, enquanto "
                f"{period_check.longest_history} tem dados desde "
                f"{_fmt(min(s.start for s in period_check.spans))}. Retorno total, volatilidade "
                "e drawdown de cada ativo são medidos sobre o período dele, o que dificulta a "
                f"comparação direta. Para comparar no mesmo intervalo ({common}), ative a opção "
                "\"Comparar apenas o período comum\" na barra lateral.",
            ))

    infos = {t: currency_info(t) for t in tickers}
    kinds = {i.kind for i in infos.values()}

    if "rate" in kinds and len(kinds) > 1:
        notes.append((
            "warning",
            "A seleção mistura taxas de juros (yields) com preços de ativos. Variação de uma "
            "taxa mede a mudança do nível da taxa, e não o retorno de um título; as métricas "
            "não são diretamente equivalentes.",
        ))

    currencies = {i.code for i in infos.values() if i.kind == "price"}
    if len(currencies) > 1:
        notes.append((
            "info",
            "Os ativos são cotados em moedas diferentes (" + ", ".join(sorted(currencies)) + "). "
            "Retornos percentuais e a Base 100 não incorporam variação cambial.",
        ))

    crypto = [t for t in tickers if is_crypto(t)]
    if frequency == "Diário" and crypto and len(crypto) < len(tickers):
        notes.append((
            "info",
            "Criptomoedas negociam todos os dias e demais ativos seguem calendários de bolsa; "
            "em frequência diária, as correlações usam apenas as datas coincidentes.",
        ))

    for group in OVERLAP_GROUPS:
        present = [t for t in tickers if t in group]
        if len(present) >= 2:
            notes.append((
                "info",
                "Ativos com exposição sobreposta na seleção (" + ", ".join(present) + "): "
                "correlação próxima de 1 é esperada por construção e não indica diversificação.",
            ))

    return notes