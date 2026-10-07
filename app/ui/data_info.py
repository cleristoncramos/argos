"""Bloco de informações sobre a fonte e a disponibilidade dos dados."""

from datetime import datetime

import streamlit as st

from core.data_availability import (
    DataAvailability,
    availability_messages,
    availability_summary,
)

from core.catalog_notice import (
    CATALOG_DISCLAIMER_TEXT,
    CATALOG_SELECTION_TEXT,
    CATALOG_SHORT_NOTE,
)

DATA_SOURCE = "Yahoo Finance (via biblioteca yfinance)"


def render_availability_messages(availability: DataAvailability) -> None:
    for level, text in availability_messages(availability):
        {"error": st.error, "warning": st.warning}.get(level, st.info)(text)


def render_data_availability(
    availability: DataAvailability,
    fetched_at: datetime | None = None,
    source: str = DATA_SOURCE,
) -> None:
    summary = availability_summary(availability)

    with st.container(border=True):
        left, middle, right = st.columns(3)
        left.markdown(f"**Período solicitado**  \n{summary['requested']}")
        middle.markdown(f"**Período disponível**  \n{summary['available']}")
        right.markdown(f"**Observações**  \n{summary['observations']}")

        consulted = fetched_at.strftime("%d/%m/%Y às %H:%M") if fetched_at else "—"
        st.caption(
            f"Fonte: {source} · Consulta realizada em {consulted} · "
            "A fonte não informa quando atualizou os dados; a última observação "
            "disponível é a data final do período disponível."
        )

    render_availability_messages(availability)


def render_catalog_notice() -> None:
    """Expander com o critério de seleção dos ativos do catálogo."""
    with st.expander(f"🗂️ Sobre o catálogo de ativos. {CATALOG_SHORT_NOTE}", expanded=False):
        st.markdown(CATALOG_SELECTION_TEXT)
        st.markdown(CATALOG_DISCLAIMER_TEXT)