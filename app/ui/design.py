"""
Linguagem visual comum a todas as páginas do Argos DataLab.

Regras: tema escuro azul-marinho com profundidade (gradientes, brilho e
sombras suaves), nenhum canto arredondado e elementos delimitados por linhas
finas quase pretas, discretas sobre o fundo escuro. O tema base está em
.streamlit/config.toml; este CSS cobre o que o tema não alcança, inclusive o
HTML próprio das páginas.
"""

import streamlit as st

BG = "#0B1220"
SURFACE = "#111A2E"
SURFACE_2 = "#16213A"
LINE = "#04070D"                       # bordas de elementos e seções
LINE_SOFT = "rgba(148,163,184,0.14)"   # divisões internas (linhas de tabela)
ACCENT = "#E5484D"                     # vermelho do Argos
INK = "#E6EAF2"
MUTED = "#94A3B8"

# Superfície padrão de cartões e painéis.
CARD_BG = "linear-gradient(160deg, #15203A 0%, #0F182B 100%)"
CARD_SHADOW = "0 14px 34px rgba(0,0,0,.38), inset 0 1px 0 rgba(255,255,255,.04)"

GLOBAL_CSS = f"""
<style>
*, *::before, *::after {{ border-radius: 0 !important; }}

.stApp {{
    background:
        radial-gradient(1000px 480px at 85% -10%, rgba(229, 72, 77, .10), transparent 60%),
        radial-gradient(900px 520px at -10% 10%, rgba(56, 189, 248, .07), transparent 60%),
        {BG} !important;
}}
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0F182B 0%, #0A1120 100%) !important;
    border-right: 1px solid {LINE};
}}

/* Painéis delimitados por linhas finas, com profundidade */
[data-testid="stPlotlyChart"] {{
    border: 1px solid {LINE}; padding: 8px;
    background: {CARD_BG}; box-shadow: {CARD_SHADOW};
}}
[data-testid="stExpander"] details {{ border: 1px solid {LINE} !important; background: rgba(17, 26, 46, .6); }}
[data-testid="stAlertContainer"] {{ border: 1px solid {LINE} !important; }}
[data-testid="stVerticalBlockBorderWrapper"] {{ border-color: {LINE} !important; }}
[data-baseweb="tab-list"] {{ border-bottom: 1px solid {LINE}; }}
[data-testid="stMain"] hr {{ border-color: rgba(148,163,184,.18) !important; opacity: 1; }}

/* Botão principal com brilho */
[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(135deg, #EF4444, #C81E2A) !important; border: 1px solid {LINE} !important;
    box-shadow: 0 8px 22px rgba(229, 72, 77, .28) !important;
}}
[data-testid="stBaseButton-primary"]:hover {{ box-shadow: 0 10px 28px rgba(229, 72, 77, .42) !important; }}
</style>
"""


def apply_global_style() -> None:
    """Aplica o CSS comum; chamado uma vez por execução em app/main.py."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
