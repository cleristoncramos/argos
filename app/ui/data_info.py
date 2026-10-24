"""Bloco de informações sobre a fonte e a disponibilidade dos dados."""

from datetime import datetime
from html import escape
from typing import Iterable, Mapping, Optional

import streamlit as st

from app.ui.asset_cards import render_asset_hero_logo

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
    show_messages: bool = True,
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

    if show_messages:
        render_availability_messages(availability)


def build_processing_details_html(details: Iterable[tuple[str, str]]) -> str:
    """
    Grade compacta de rótulo e valor para os detalhes do processamento.
    Valores longos (mais de 60 caracteres) ocupam a linha inteira.
    """
    cells = []
    for label, value in details:
        wide = " pd-wide" if len(str(value)) > 60 else ""
        cells.append(
            f'<div class="pd-cell{wide}"><span>{escape(str(label))}</span>'
            f"<b>{escape(str(value))}</b></div>"
        )
    return f'<div class="pd-grid">{"".join(cells)}</div>'


def render_analysis_summary(
    asset: Optional[Mapping[str, str]],
    availability: Optional[DataAvailability],
    fetched_at: datetime | None,
    details: Iterable[tuple[str, str]],
    details_label: str = "Detalhes do processamento",
) -> None:
    """
    Topo das páginas de análise: cartão do ativo ao lado do resumo de
    disponibilidade (alturas parecidas) e, abaixo, em largura total, os
    avisos e um expansor compacto com os detalhes do processamento.
    """
    col_logo, col_info = st.columns([1, 3], vertical_alignment="center")
    with col_logo:
        if asset:
            render_asset_hero_logo(asset)
    with col_info:
        if availability is not None:
            render_data_availability(availability, fetched_at, show_messages=False)

    if availability is not None:
        render_availability_messages(availability)

    with st.expander(details_label, expanded=False):
        st.markdown(build_processing_details_html(details), unsafe_allow_html=True)


def render_catalog_notice() -> None:
    """Expander com o critério de seleção dos ativos do catálogo."""
    with st.expander(f"🗂️ Sobre o catálogo de ativos. {CATALOG_SHORT_NOTE}", expanded=False):
        st.markdown(CATALOG_SELECTION_TEXT)
        st.markdown(CATALOG_DISCLAIMER_TEXT)