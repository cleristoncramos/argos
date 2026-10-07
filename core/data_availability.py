"""
Avaliação da disponibilidade real de dados: período solicitado x período
disponível, quantidade de observações e avisos. Sem dependência de UI.
"""

from dataclasses import dataclass
from datetime import date

import pandas as pd

MIN_OBSERVATIONS = 2            # abaixo disso não há como calcular retorno
RECOMMENDED_OBSERVATIONS = 12   # abaixo disso as estatísticas são pouco estáveis
START_TOLERANCE_DAYS = 10       # fins de semana/feriados no início do período
END_TOLERANCE_DAYS = 7          # fins de semana/feriados no fim do período


@dataclass(frozen=True)
class DataAvailability:
    requested_start: date
    requested_end: date
    available_start: date | None
    available_end: date | None
    daily_observations: int
    period_observations: int
    start_gap_days: int
    end_gap_days: int
    shorter_history: bool
    stale_end: bool
    insufficient: bool
    limited: bool


def assess_availability(
    dates,
    requested_start: date,
    requested_end: date,
    period_observations: int,
    *,
    start_tolerance_days: int = START_TOLERANCE_DAYS,
    end_tolerance_days: int = END_TOLERANCE_DAYS,
    min_observations: int = MIN_OBSERVATIONS,
    recommended_observations: int = RECOMMENDED_OBSERVATIONS,
) -> DataAvailability:
    """
    `dates`: datas das observações diárias baixadas (antes de agregar).
    `period_observations`: quantidade de períodos após agregar pela frequência.
    """
    series = pd.to_datetime(pd.Series(list(dates)), errors="coerce").dropna()

    if series.empty:
        return DataAvailability(
            requested_start, requested_end, None, None,
            0, period_observations, 0, 0,
            shorter_history=False, stale_end=False,
            insufficient=True, limited=True,
        )

    first = series.min().date()
    last = series.max().date()
    start_gap = max((first - requested_start).days, 0)
    end_gap = max((requested_end - last).days, 0)

    return DataAvailability(
        requested_start=requested_start,
        requested_end=requested_end,
        available_start=first,
        available_end=last,
        daily_observations=int(len(series)),
        period_observations=int(period_observations),
        start_gap_days=start_gap,
        end_gap_days=end_gap,
        shorter_history=start_gap > start_tolerance_days,
        stale_end=end_gap > end_tolerance_days,
        insufficient=period_observations < min_observations,
        limited=period_observations < recommended_observations,
    )


def _fmt(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else "—"


def availability_messages(a: DataAvailability) -> list[tuple[str, str]]:
    """Lista de (nível, texto), com nível em {"error", "warning", "info"}."""
    messages: list[tuple[str, str]] = []

    if a.insufficient:
        messages.append((
            "error",
            f"Dados insuficientes: {a.period_observations} período(s) disponível(is) "
            f"para o intervalo solicitado; são necessários ao menos {MIN_OBSERVATIONS} "
            "para calcular retornos. Tente um período mais longo ou outra frequência.",
        ))
        return messages

    if a.shorter_history:
        messages.append((
            "warning",
            f"Histórico menor que o solicitado: o período pedido começa em "
            f"{_fmt(a.requested_start)}, mas o primeiro dado disponível é de "
            f"{_fmt(a.available_start)} ({a.start_gap_days} dias depois). Isso é comum "
            "em ativos recentes (como criptomoedas e IPOs) ou quando a fonte não tem "
            "histórico completo. As métricas valem para o período efetivamente disponível.",
        ))

    if a.stale_end:
        messages.append((
            "warning",
            f"Os dados terminam em {_fmt(a.available_end)}, {a.end_gap_days} dias antes "
            f"da data final solicitada ({_fmt(a.requested_end)}). Pode indicar ativo sem "
            "negociação recente, descontinuado ou indisponibilidade temporária da fonte.",
        ))

    if a.limited:
        messages.append((
            "info",
            f"Poucas observações ({a.period_observations} períodos): estatísticas "
            "calculadas sobre amostras curtas são pouco estáveis.",
        ))

    return messages


def availability_summary(a: DataAvailability) -> dict[str, str]:
    """Textos prontos para exibição."""
    return {
        "requested": f"{_fmt(a.requested_start)} a {_fmt(a.requested_end)}",
        "available": f"{_fmt(a.available_start)} a {_fmt(a.available_end)}",
        "observations": (
            f"{a.daily_observations} diárias · {a.period_observations} no período agregado"
        ),
    }