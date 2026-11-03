"""
Data e hora de Brasília, independentemente do fuso do servidor.

O Streamlit Community Cloud roda em UTC: `datetime.now()` mostraria a hora
três horas adiantada e, depois das 21h, já a data do dia seguinte. As páginas
usam estas funções para a hora da consulta e para a data final padrão.
"""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

BRASILIA = ZoneInfo("America/Sao_Paulo")


def now_brasilia() -> datetime:
    """Data e hora atuais no horário de Brasília (com fuso)."""
    return datetime.now(BRASILIA)


def today_brasilia() -> date:
    """Data de hoje no horário de Brasília."""
    return now_brasilia().date()
