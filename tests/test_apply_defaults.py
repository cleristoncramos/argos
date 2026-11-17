"""Padrões de Configurações aplicados em todas as análises da sessão (16/11/2026)."""

from streamlit.testing.v1 import AppTest

from core.periods import period_start_date


def _run(script):
    at = AppTest.from_function(script)
    at.run()
    assert not at.exception
    return at.session_state


def test_padroes_valem_tambem_para_analises_ja_carregadas():
    def script():
        import streamlit as st
        from app.ui.state import apply_defaults
        from core.settings_info import AnalysisDefaults

        state = st.session_state
        state["asset_period"], state["asset_frequency"] = "5 anos", "Mensal"
        state["asset_loaded"] = state["risk_return_loaded"] = state["comparison_loaded"] = True
        state["indicators_loaded"] = False
        state["asset_load_button_period_select"] = "5 anos"
        state["risk_return_load_button_frequency_select"] = "Mensal"
        state["comparison_period_widget"] = "5 anos"
        state["risk_return_risk_free_rate_pct_widget"] = 0.0
        apply_defaults(AnalysisDefaults("1 ano", "Semanal", 12.0))

    state = _run(script)
    for prefix in ("asset", "comparison"):
        assert state[f"{prefix}_period"] == "1 ano" and state[f"{prefix}_frequency"] == "Semanal"
        assert state[f"{prefix}_start_date"] == period_start_date("1 ano", state[f"{prefix}_end_date"])
    assert state["comparison_risk_free_rate_pct"] == 12.0 and state["risk_return_risk_free_rate_pct"] == 12.0
    for key in ("asset_load_button_period_select", "risk_return_load_button_frequency_select",
                "comparison_period_widget", "risk_return_risk_free_rate_pct_widget"):
        assert key not in state
    # Só as páginas com análise carregada são refeitas; a análise antiga continua à vista até lá.
    assert state["asset_reload_buttons"] == {"asset_load_button", "risk_return_load_button"}
    assert state["comparison_autoload"] is True and state["asset_loaded"] is True


def test_cada_pagina_refaz_a_analise_uma_vez():
    def script():
        import streamlit as st
        from app.ui.state import RELOAD_KEY, consume_reload

        st.session_state[RELOAD_KEY] = {"asset_load_button", "simulation_load_button"}
        st.session_state["first"] = consume_reload("asset_load_button")
        st.session_state["again"] = consume_reload("asset_load_button")
        st.session_state["other"] = consume_reload("indicators_load_button")

    state = _run(script)
    assert state["first"] is True and state["again"] is False and state["other"] is False
    assert state["asset_reload_buttons"] == {"simulation_load_button"}


def test_sem_analise_carregada_nada_e_refeito():
    def script():
        import streamlit as st
        from app.ui.state import apply_defaults, consume_reload
        from core.settings_info import ARGOS_DEFAULTS

        apply_defaults(ARGOS_DEFAULTS)
        st.session_state["reload"] = consume_reload("asset_load_button")

    state = _run(script)
    assert state["asset_reload_buttons"] == set() and state["comparison_autoload"] is False
    assert state["reload"] is False and state["asset_period"] == "5 anos"
