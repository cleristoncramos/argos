"""Validação do intervalo de datas escolhido pelo usuário. Sem dependência de UI."""

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class DateRangeCheck:
    ok: bool
    message: str = ""


def _as_date(value) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def validate_date_range(start, end, today: date | None = None) -> DateRangeCheck:
    """
    Verifica se o intervalo [start, end] pode ser consultado.

    Regras: as duas datas devem existir, a data inicial deve ser anterior à
    final (são necessários ao menos dois dias para calcular retornos) e a data
    final não pode estar no futuro.
    """
    start_date = _as_date(start)
    end_date = _as_date(end)
    reference = _as_date(today) or date.today()

    if start_date is None or end_date is None:
        return DateRangeCheck(False, "Informe a data inicial e a data final.")

    if start_date >= end_date:
        return DateRangeCheck(
            False,
            "A data inicial deve ser anterior à data final.",
        )

    if end_date > reference:
        return DateRangeCheck(
            False,
            f"A data final não pode estar no futuro (hoje é {reference.strftime('%d/%m/%Y')}).",
        )

    return DateRangeCheck(True)