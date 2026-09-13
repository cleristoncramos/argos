from datetime import date, datetime

import streamlit as st

def get_default_start_date() -> date:
    """Calcula a data inicial padrão (5 anos atrás, arredondado para o mês seguinte)."""
    today = datetime.now().date()
    target_year = today.year - 5
    target_month = today.month + 1
    if target_month > 12:
        target_month = 1
        target_year += 1
    return date(target_year, target_month, 1)


ASSET_DEFAULTS = {
    "asset_symbol": "BTC-USD",
    "asset_period": "5 anos",
    "asset_start_date": get_default_start_date(),
    "asset_end_date": date.today(),
    "asset_frequency": "Mensal",
    "asset_loaded": False,
    "asset_query": None,
}


COMPARISON_DEFAULTS = {
    "comparison_symbols_text": "BTC-USD,AAPL,SPY",
    "comparison_period": "5 anos",
    "comparison_start_date": get_default_start_date(),
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
    # Atualiza a data caso o app fique aberto por dias
    ASSET_DEFAULTS["asset_start_date"] = get_default_start_date()
    ASSET_DEFAULTS["asset_end_date"] = date.today()
    initialize_state(ASSET_DEFAULTS)


def initialize_comparison_state() -> None:
    """Inicializa o estado persistente da comparação de ativos."""
    # Atualiza a data caso o app fique aberto por dias
    COMPARISON_DEFAULTS["comparison_start_date"] = get_default_start_date()
    COMPARISON_DEFAULTS["comparison_end_date"] = date.today()
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
        "widget_asset_symbol": st.session_state.get("asset_symbol", "BTC-USD"),
        "widget_asset_start_date": st.session_state.get("asset_start_date", get_default_start_date()),
        "widget_asset_end_date": st.session_state.get("asset_end_date", date.today()),
        "widget_asset_frequency": st.session_state.get("asset_frequency", "Mensal"),
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
    if "widget_asset_symbol" in st.session_state:
        st.session_state["asset_symbol"] = (
            st.session_state["widget_asset_symbol"]
            .strip()
            .upper()
        )
    if "widget_asset_start_date" in st.session_state:
        st.session_state["asset_start_date"] = (
            st.session_state["widget_asset_start_date"]
        )
    if "widget_asset_end_date" in st.session_state:
        st.session_state["asset_end_date"] = (
            st.session_state["widget_asset_end_date"]
        )
    if "widget_asset_frequency" in st.session_state:
        st.session_state["asset_frequency"] = (
            st.session_state["widget_asset_frequency"]
        )