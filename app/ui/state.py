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
    Cria chaves de session state somente se ainda não existirem.

    Nunca sobrescreve seleções feitas pelo usuário em reruns.
    """
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def initialize_asset_state() -> None:
    """Inicializa estado compartilhado de análise de um ativo."""
    initialize_state(ASSET_DEFAULTS)


def initialize_comparison_state() -> None:
    """Inicializa estado exclusivo da comparação de ativos."""
    initialize_state(COMPARISON_DEFAULTS)