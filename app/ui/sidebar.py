from datetime import date

import streamlit as st


DEFAULT_SYMBOL = "BTC-USD"
DEFAULT_START_DATE = date(2020, 1, 1)
DEFAULT_END_DATE = date.today()
DEFAULT_FREQUENCY = "Mensal"

FREQUENCY_OPTIONS = [
    "Diário",
    "Semanal",
    "Mensal",
]


def render_asset_sidebar(title="⚙️ Configurações"):
    """
    Renderiza controles compartilhados de análise individual.

    Retorna os parâmetros escolhidos pelo usuário.
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

        load_data = st.button(
            "🔄 Carregar Dados",
            key="asset_load_button",
        )

    return {
        "symbol": symbol.strip().upper(),
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
        "load_data": load_data,
    }

def render_comparison_sidebar():
    """
    Renderiza os controles exclusivos da comparação de ativos.
    """
    with st.sidebar:
        st.header("⚖️ Parâmetros da Comparação")

        symbols_text = st.text_input(
            "Símbolos dos ativos",
            key="comparison_symbols_text",
            help=(
                "Informe entre 2 e 5 símbolos separados por vírgula. "
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

        risk_free_rate = st.number_input(
            "Taxa livre de risco anual (%)",
            min_value=0.0,
            value=0.0,
            step=0.25,
            key="comparison_risk_free_rate_pct",
        )

        compare_assets = st.button(
            "⚖️ Comparar ativos",
            key="comparison_run_button",
        )

    return {
        "symbols_text": symbols_text,
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
        "risk_free_rate_pct": risk_free_rate,
        "compare_assets": compare_assets,
    }