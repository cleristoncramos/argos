from typing import Any

import streamlit as st

from app.ui.state import persist_asset_widget_state, sync_asset_widget_state


FREQUENCY_OPTIONS = [
    "Diário",
    "Semanal",
    "Mensal",
]


def render_asset_controls(
    title: str = "⚙️ Configurações",
    button_label: str = "🔄 Carregar Dados",
    button_key: str = "asset_load_button",
) -> dict[str, Any]:
    """
    Renderiza a sidebar compartilhada de análise individual.

    Os widgets usam chaves temporárias widget_asset_*.
    Os valores persistentes usam chaves asset_*.
    """
    sync_asset_widget_state()

    with st.sidebar:
        st.header(title)

        symbol = st.text_input(
            "Símbolo do Ativo",
            key="widget_asset_symbol",
            help="Exemplos: BTC-USD, AAPL, USD=BRL, GOLD",
            on_change=persist_asset_widget_state,
        )

        start_date = st.date_input(
            "Data Inicial",
            key="widget_asset_start_date",
            on_change=persist_asset_widget_state,
        )

        end_date = st.date_input(
            "Data Final",
            key="widget_asset_end_date",
            on_change=persist_asset_widget_state,
        )

        frequency = st.selectbox(
            "Frequência",
            options=FREQUENCY_OPTIONS,
            key="widget_asset_frequency",
            on_change=persist_asset_widget_state,
        )

        invalid_period = start_date >= end_date

        if invalid_period:
            st.error(
                "A data inicial deve ser anterior à data final."
            )

        submitted = st.button(
            button_label,
            key=button_key,
            type="primary",
            disabled=invalid_period,
        )

    return {
        "symbol": symbol.strip().upper(),
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
        "submitted": submitted,
    }