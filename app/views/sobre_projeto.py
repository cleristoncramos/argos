import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from app.ui.about import (
    ABOUT_CSS,
    build_context_html,
    build_data_html,
    build_disclaimer_html,
    build_hero_html,
    build_methodology_html,
    build_modules_html,
    build_quality_html,
    build_research_html,
    build_team_html,
    group_counts,
)
from app.ui.landing import catalog_stats
from core.assets import ASSET_GROUPS, ASSETS

st.set_page_config(
    page_title="Argos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# Sobre o Projeto: conteúdo em app/ui/about.py
# ==========================================================
stats = catalog_stats(ASSETS)

st.markdown(ABOUT_CSS, unsafe_allow_html=True)
st.markdown(build_hero_html(stats), unsafe_allow_html=True)
st.markdown(build_context_html(), unsafe_allow_html=True)
st.markdown(build_research_html(), unsafe_allow_html=True)
st.markdown(build_modules_html(), unsafe_allow_html=True)
st.markdown(build_methodology_html(), unsafe_allow_html=True)
st.markdown(build_data_html(stats, group_counts(ASSETS, ASSET_GROUPS)), unsafe_allow_html=True)
st.markdown(build_quality_html(), unsafe_allow_html=True)
st.markdown(build_team_html(), unsafe_allow_html=True)
st.markdown(build_disclaimer_html(), unsafe_allow_html=True)

st.caption(
    "Argos · Plataforma de Análise Histórica de Ativos Financeiros · "
    "Desenvolvido com Python, Streamlit e Plotly."
)
