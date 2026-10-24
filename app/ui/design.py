"""
Linguagem visual comum a todas as páginas do Argos.

Regras: tema claro com profundidade (fundo levemente quente, painéis brancos
com sombra suave e detalhes em vermelho), nenhum canto arredondado e
elementos delimitados por linhas finas escuras. O tema base está em
.streamlit/config.toml; este CSS cobre o que o tema não alcança, inclusive o
HTML próprio das páginas.
"""

import streamlit as st

LINE = "#2A2A2A"          # bordas de elementos e seções
LINE_SOFT = "#E4E1DA"     # divisões internas (linhas de tabela)
ACCENT = "#C8102E"        # vermelho do Argos
INK = "#111111"
MUTED = "#5F5F5F"
PAPER = "#FFFFFF"
PAPER_ALT = "#F6F4EF"
SHADOW = "0 8px 22px rgba(17, 17, 17, .07)"

GLOBAL_CSS = f"""
<style>
*, *::before, *::after {{ border-radius: 0 !important; }}

.stApp {{
    background:
        radial-gradient(900px 380px at 88% -6%, rgba(200, 16, 46, .07), transparent 60%),
        radial-gradient(800px 420px at -8% 12%, rgba(29, 78, 216, .05), transparent 60%),
        #F7F6F2 !important;
}}
[data-testid="stSidebar"] {{ border-right: 1px solid {LINE}; background: linear-gradient(180deg, #F1EFEA 0%, #ECE9E2 100%) !important; }}

/* Painéis brancos delimitados por linhas finas, com sombra suave */
[data-testid="stPlotlyChart"] {{ border: 1px solid {LINE}; background: {PAPER}; padding: 6px; box-shadow: {SHADOW}; }}
[data-testid="stExpander"] details {{ border: 1px solid {LINE} !important; background: {PAPER}; }}
[data-testid="stAlertContainer"] {{ border: 1px solid {LINE} !important; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-color: {LINE} !important; }}
[data-baseweb="tab-list"] {{ border-bottom: 1px solid {LINE}; }}
[data-testid="stMain"] hr {{ border-color: {LINE_SOFT} !important; opacity: 1; }}

/* Botão principal com leve relevo */
[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(180deg, #D7193A 0%, #B50E29 100%) !important; border: 1px solid #7A0A1C !important;
    box-shadow: 0 6px 16px rgba(200, 16, 46, .25) !important;
}}
/* Texto sempre branco no botão vermelho, inclusive desabilitado (antes de escolher o ativo) */
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primary"] p {{ color: #FFFFFF !important; }}
[data-testid="stBaseButton-primary"]:disabled {{
    background: linear-gradient(180deg, #E58A99 0%, #D9707F 100%) !important; border-color: #B8798A !important;
    box-shadow: none !important; cursor: not-allowed;
}}
[data-testid="stBaseButton-secondary"] {{ background: {PAPER} !important; box-shadow: 0 2px 6px rgba(17, 17, 17, .06) !important; }}
</style>
"""


def apply_global_style() -> None:
    """Aplica o CSS comum; chamado uma vez por execução em app/main.py."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
