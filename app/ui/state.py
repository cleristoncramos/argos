from datetime import date

import streamlit as st

from core.clock import today_brasilia
from core.periods import DEFAULT_PERIOD, period_start_date


def get_default_start_date() -> date:
    """
    Data inicial padrão, derivada do período padrão (core/periods.py).

    Usa a mesma regra da barra lateral, para que o estado inicial e o
    seletor de período nunca divirjam.
    """
    return period_start_date(DEFAULT_PERIOD, today_brasilia())


ASSET_DEFAULTS = {
    "asset_symbol": "BTC-USD",
    "asset_period": DEFAULT_PERIOD,
    "asset_start_date": get_default_start_date(),
    "asset_end_date": today_brasilia(),
    "asset_frequency": "Mensal",
    "asset_loaded": False,
    "asset_query": None,
}


COMPARISON_DEFAULTS = {
    "comparison_symbols_text": "BTC-USD,AAPL,SPY",
    "comparison_period": DEFAULT_PERIOD,
    "comparison_start_date": get_default_start_date(),
    "comparison_end_date": today_brasilia(),
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


def _analysis_defaults():
    """Período, frequência e taxa padrão escolhidos em Configurações."""
    from app.ui.catalog_state import analysis_defaults   # import tardio: evita ciclo de imports

    return analysis_defaults()


def initialize_asset_state() -> None:
    """Inicializa o estado persistente da análise individual."""
    # Datas recalculadas a cada chamada (o app pode ficar aberto por dias),
    # sem alterar o dicionário de padrões do módulo. Período e frequência
    # seguem os padrões de Configurações.
    defaults = _analysis_defaults()
    today = today_brasilia()
    initialize_state(
        {
            **ASSET_DEFAULTS,
            "asset_period": defaults.period,
            "asset_start_date": period_start_date(defaults.period, today),
            "asset_end_date": today,
            "asset_frequency": defaults.frequency,
        }
    )


def initialize_comparison_state() -> None:
    """Inicializa o estado persistente da comparação de ativos."""
    defaults = _analysis_defaults()
    today = today_brasilia()
    initialize_state(
        {
            **COMPARISON_DEFAULTS,
            "comparison_period": defaults.period,
            "comparison_start_date": period_start_date(defaults.period, today),
            "comparison_end_date": today,
            "comparison_frequency": defaults.frequency,
            "comparison_risk_free_rate_pct": defaults.risk_free_pct,
        }
    )


def apply_defaults_to_unloaded(defaults) -> None:
    """
    Leva novos padrões de Configurações às análises ainda não consultadas nesta
    sessão. Análises já carregadas mantêm a escolha feita na barra lateral.
    """
    today = today_brasilia()
    if not st.session_state.get("asset_loaded"):
        st.session_state["asset_period"] = defaults.period
        st.session_state["asset_start_date"] = period_start_date(defaults.period, today)
        st.session_state["asset_frequency"] = defaults.frequency
    if not st.session_state.get("comparison_loaded"):
        st.session_state["comparison_period"] = defaults.period
        st.session_state["comparison_start_date"] = period_start_date(defaults.period, today)
        st.session_state["comparison_frequency"] = defaults.frequency
        st.session_state["comparison_risk_free_rate_pct"] = defaults.risk_free_pct
    st.session_state["risk_return_risk_free_rate_pct"] = defaults.risk_free_pct
