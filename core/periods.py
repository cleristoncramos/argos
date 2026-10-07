"""Cálculo de períodos de análise (atalhos de 1, 3, 5, 10 anos)."""

from datetime import date

CUSTOM_PERIOD = "Personalizado"
PERIOD_OPTIONS = ["1 ano", "3 anos", "5 anos", "10 anos", CUSTOM_PERIOD]
DEFAULT_PERIOD = "5 anos"


def period_start_date(period_label: str, today: date) -> date:
    """
    Data inicial de um atalho de período: primeiro dia do mês seguinte,
    N anos atrás (mesma regra usada até agora nas páginas).

    Levanta ValueError para "Personalizado" ou rótulos inválidos.
    """
    if period_label == CUSTOM_PERIOD:
        raise ValueError("O período personalizado não tem data inicial calculável.")

    try:
        years = int(period_label.split()[0])
    except (ValueError, IndexError, AttributeError):
        raise ValueError(f"Rótulo de período inválido: {period_label!r}.")

    year = today.year - years
    month = today.month + 1
    if month > 12:
        month = 1
        year += 1
    return date(year, month, 1)