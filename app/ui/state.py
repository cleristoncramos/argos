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


# Análise Individual aberta a partir do mosaico da página inicial: a barra lateral
# consome esta marca e carrega a análise como se o botão tivesse sido clicado.
AUTOLOAD_KEY = "asset_autoload"
INDIVIDUAL_BUTTON_KEY = "asset_load_button"
_SIDEBAR_WIDGETS = ("_input_mode", "_group_select", "_asset_select", "_period_select", "_frequency_select")


def queue_individual_analysis(asset: dict, period: str, frequency: str) -> None:
    """Prepara a Análise Individual de um ativo do catálogo com período e frequência dados."""
    today = today_brasilia()
    st.session_state["asset_group"] = asset["group"]
    st.session_state["asset_symbol"] = asset["ticker"]
    st.session_state["asset_period"] = period
    st.session_state["asset_start_date"] = period_start_date(period, today)
    st.session_state["asset_end_date"] = today
    st.session_state["asset_frequency"] = frequency
    st.session_state["asset_loaded"] = False
    st.session_state["asset_query"] = None
    # Seletores de uma visita anterior não podem sobrepor a escolha feita no mosaico.
    for suffix in _SIDEBAR_WIDGETS:
        st.session_state.pop(INDIVIDUAL_BUTTON_KEY + suffix, None)
    st.session_state[AUTOLOAD_KEY] = True


COMPARISON_AUTOLOAD_KEY = "comparison_autoload"
# Páginas com análise carregada a refazer com os novos padrões (botões da barra lateral).
RELOAD_KEY = "asset_reload_buttons"
# Botão de cada página com a barra lateral de um ativo e a marca de análise carregada.
ASSET_PAGES_LOADED = {
    INDIVIDUAL_BUTTON_KEY: "asset_loaded",
    "indicators_load_button": "indicators_loaded",
    "risk_return_load_button": "risk_return_loaded",
    "simulation_load_button": "simulation_loaded",
}
ASSET_BUTTON_KEYS = tuple(ASSET_PAGES_LOADED)
_PERIOD_WIDGETS = ("_period_select", "_frequency_select", "_start_date", "_end_date")
# Seletores da Comparação e campos de taxa que guardam o último valor digitado.
_RATE_AND_COMPARISON_WIDGETS = (
    "comparison_period_widget",
    "comparison_start_date_widget",
    "comparison_end_date_widget",
    "comparison_frequency_widget",
    "comparison_risk_free_rate_pct_widget",
    "risk_return_risk_free_rate_pct_widget",
)


def apply_defaults(defaults) -> None:
    """
    Aplica os padrões salvos em Configurações em todas as análises da sessão: a
    barra lateral passa a mostrar o novo período, a nova frequência e a nova taxa.
    Uma análise já carregada é refeita com os novos padrões ao voltar à página,
    sem precisar clicar no botão de novo.
    """
    state = st.session_state
    today = today_brasilia()
    start = period_start_date(defaults.period, today)
    for prefix in ("asset", "comparison"):
        state[f"{prefix}_period"] = defaults.period
        state[f"{prefix}_start_date"] = start
        state[f"{prefix}_end_date"] = today
        state[f"{prefix}_frequency"] = defaults.frequency
    state["comparison_risk_free_rate_pct"] = defaults.risk_free_pct
    state["risk_return_risk_free_rate_pct"] = defaults.risk_free_pct

    # Seletores de uma visita anterior não podem sobrepor os novos padrões.
    for key in (*(b + s for b in ASSET_BUTTON_KEYS for s in _PERIOD_WIDGETS), *_RATE_AND_COMPARISON_WIDGETS):
        state.pop(key, None)

    state[RELOAD_KEY] = {button for button, loaded in ASSET_PAGES_LOADED.items() if state.get(loaded)}
    state[COMPARISON_AUTOLOAD_KEY] = bool(state.get("comparison_loaded"))


def consume_reload(button_key: str) -> bool:
    """True uma vez para a página que deve refazer a análise com os novos padrões."""
    pending = st.session_state.get(RELOAD_KEY) or set()
    if button_key not in pending:
        return False
    st.session_state[RELOAD_KEY] = pending - {button_key}
    return True
