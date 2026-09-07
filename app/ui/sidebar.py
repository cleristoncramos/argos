from typing import Any

import streamlit as st


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
    Renderiza os controles compartilhados para análise de um ativo.

    A função pressupõe que initialize_asset_state() foi chamada antes.
    """
    with st.sidebar:
        st.header(title)

        symbol = st.text_input(
            "Símbolo do Ativo",
            key="asset_symbol",
        )

        start_date = st.date_input(
            "Data Inicial",
            key="asset_start_date",
        )

        end_date = st.date_input(
            "Data Final",
            key="asset_end_date",
        )

        frequency = st.selectbox(
            "Frequência",
            FREQUENCY_OPTIONS,
            key="asset_frequency",
        )

        submitted = st.button(
            button_label,
            key=button_key,
        )

    return {
        "symbol": symbol.strip().upper(),
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
        "submitted": submitted,
    }


def render_comparison_controls() -> dict[str, Any]:
    """
    Renderiza os controles exclusivos da página de comparação.
    """
    with st.sidebar:
        st.header("⚖️ Parâmetros da Comparação")

        symbols_text = st.text_input(
            "Símbolos dos ativos",
            key="comparison_symbols_text",
            help=(
                "Informe de 2 a 5 símbolos separados por vírgula. "
                "Exemplo: BTC-USD,AAPL,SPY"
            ),
        )

        start_date = st.date_input(
            "Data inicial",
            key="comparison_start_date",
        )

        end_date = st.date_input(
            "Data final",
            key="comparison_end_date",
        )

        frequency = st.selectbox(
            "Frequência",
            FREQUENCY_OPTIONS,
            key="comparison_frequency",
        )

        risk_free_rate_pct = st.number_input(
            "Taxa livre de risco anual (%)",
            min_value=0.0,
            step=0.25,
            key="comparison_risk_free_rate_pct",
        )

        submitted = st.button(
            "⚖️ Comparar ativos",
            key="comparison_run_button",
        )

    return {
        "symbols_text": symbols_text,
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
        "risk_free_rate_pct": risk_free_rate_pct,
        "submitted": submitted,
    }