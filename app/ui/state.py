from datetime import date

import streamlit as st

from core.periods import DEFAULT_PERIOD, period_start_date


def get_default_start_date() -> date:
    """
    Data inicial padrão, derivada do período padrão (core/periods.py).

    Usa a mesma regra da barra lateral, para que o estado inicial e o
    seletor de período nunca divirjam.
    """
    return period_start_date(DEFAULT_PERIOD, date.today())


ASSET_DEFAULTS = {
    "asset_symbol": "BTC-USD",
    "asset_period": DEFAULT_PERIOD,
    "asset_start_date": get_default_start_date(),
    "asset_end_date": date.today(),
    "asset_frequency": "Mensal",
    "asset_loaded": False,
    "asset_query": None,
}


COMPARISON_DEFAULTS = {
    "comparison_symbols_text": "BTC-USD,AAPL,SPY",
    "comparison_period": DEFAULT_PERIOD,
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
    # Datas recalculadas a cada chamada (o app pode ficar aberto por dias),
    # sem alterar o dicionário de padrões do módulo.
    initialize_state(
        {
            **ASSET_DEFAULTS,
            "asset_start_date": get_default_start_date(),
            "asset_end_date": date.today(),
        }
    )


def initialize_comparison_state() -> None:
    """Inicializa o estado persistente da comparação de ativos."""
    initialize_state(
        {
            **COMPARISON_DEFAULTS,
            "comparison_start_date": get_default_start_date(),
            "comparison_end_date": date.today(),
        }
    )
