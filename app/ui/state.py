from datetime import date

import streamlit as st


ASSET_DEFAULTS = {
    "asset_symbol": "BTC-USD",
    "asset_start_date": date(2020, 1, 1),
    "asset_end_date": date.today(),
    "asset_frequency": "Mensal",
    "asset_loaded": False,
    "asset_query": None,
}


COMPARISON_DEFAULTS = {
    "comparison_symbols_text": "BTC-USD,AAPL,SPY",
    "comparison_start_date": date(2020, 1, 1),
    "comparison_end_date": date.today(),
    "comparison_frequency": "Mensal",
    "comparison_risk_free_rate_pct": 0.0,
    "comparison_loaded": False,
    "comparison_query": None,
}


def initialize_state(defaults: dict) -> None:
    """
    Inicializa somente chaves ainda inexistentes.
    Nunca sobrescreve valores escolhidos pelo usuário.
    """
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def initialize_asset_state() -> None:
    """Inicializa o estado persistente da análise individual."""
    initialize_state(ASSET_DEFAULTS)


def initialize_comparison_state() -> None:
    """Inicializa o estado persistente da comparação de ativos."""
    initialize_state(COMPARISON_DEFAULTS)


def sync_asset_widget_state() -> None:
    """
    Inicializa widgets temporários somente quando eles não existem.

    Após navegar de outra página para main, as chaves widget_asset_*
    normalmente não existem: elas são recriadas a partir do estado
    persistente asset_*.

    Durante reruns na própria página, os widgets já existem e seus
    valores não devem ser sobrescritos.
    """
    widget_defaults = {
        "widget_asset_symbol": st.session_state["asset_symbol"],
        "widget_asset_start_date": st.session_state["asset_start_date"],
        "widget_asset_end_date": st.session_state["asset_end_date"],
        "widget_asset_frequency": st.session_state["asset_frequency"],
    }

    for key, value in widget_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def persist_asset_widget_state() -> None:
    """
    Copia valores dos widgets para o estado persistente.

    Esta função é chamada por on_change, antes do rerun que redesenha
    os widgets, portanto não viola a regra do Streamlit.
    """
    st.session_state["asset_symbol"] = (
        st.session_state["widget_asset_symbol"]
        .strip()
        .upper()
    )
    st.session_state["asset_start_date"] = (
        st.session_state["widget_asset_start_date"]
    )
    st.session_state["asset_end_date"] = (
        st.session_state["widget_asset_end_date"]
    )
    st.session_state["asset_frequency"] = (
        st.session_state["widget_asset_frequency"]
    )