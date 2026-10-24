"""
Linguagem visual comum a todas as páginas do Argos DataLab.

Regras: nenhum canto arredondado e seções delimitadas por linhas pretas finas
e discretas. O tema base (claro, raio zero, cor das bordas) está em
.streamlit/config.toml; este CSS cobre o que o tema não alcança, inclusive o
HTML próprio das páginas.
"""

import streamlit as st

LINE = "#1F1F1F"          # bordas de elementos e seções
LINE_SOFT = "#D4D4D4"     # divisões internas (linhas de tabela)
ACCENT = "#C8102E"        # vermelho do Argos
INK = "#111111"
MUTED = "#5F5F5F"
PAPER = "#FFFFFF"
PAPER_ALT = "#F5F5F3"

GLOBAL_CSS = f"""
<style>
*, *::before, *::after {{ border-radius: 0 !important; }}

/* Seções e elementos delimitados por linhas finas */
[data-testid="stPlotlyChart"] {{ border: 1px solid {LINE}; background: {PAPER}; padding: 6px; }}
[data-testid="stExpander"] details {{ border: 1px solid {LINE} !important; }}
[data-testid="stAlertContainer"] {{ border: 1px solid {LINE} !important; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-color: {LINE} !important; }}
[data-baseweb="tab-list"] {{ border-bottom: 1px solid {LINE}; }}
[data-testid="stMain"] hr {{ border-color: {LINE} !important; opacity: 1; }}
[data-testid="stSidebar"] {{ border-right: 1px solid {LINE}; }}

/* Botões retos, sem sombra */
.stButton button, .stDownloadButton button, [data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-primary"] {{ box-shadow: none !important; }}
</style>
"""


def apply_global_style() -> None:
    """Aplica o CSS comum; chamado uma vez por execução em app/main.py."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
