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

/* Cabeçalho das páginas de análise (app/ui/page_header.py) */
.pg-head {{ margin: -0.6rem 0 1.6rem; padding: 0 0 18px; border-bottom: 1px solid {LINE}; }}
.pg-kicker {{ color: {ACCENT}; font-size: .72rem; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; }}
.pg-title {{ margin: 6px 0 0 !important; padding: 0 !important; font-size: 2.4rem !important; font-weight: 800 !important;
    letter-spacing: -.03em; line-height: 1.1 !important; color: {INK}; }}
.pg-sub {{ margin: 12px 0 0; max-width: 860px; padding-left: 12px; border-left: 3px solid {ACCENT};
    color: #3f3f3f; font-size: 1.02rem; line-height: 1.6; }}

/* Cartão do ativo com a mesma altura do resumo ao lado (render_analysis_summary) */
.st-key-analysis_summary [data-testid="stHorizontalBlock"] {{ align-items: stretch !important; }}
.st-key-analysis_summary [data-testid="stColumn"]:first-child [data-testid="stVerticalBlock"],
.st-key-analysis_summary [data-testid="stColumn"]:first-child [data-testid="stElementContainer"],
.st-key-analysis_summary [data-testid="stColumn"]:first-child [data-testid="stMarkdown"],
.st-key-analysis_summary [data-testid="stColumn"]:first-child [data-testid="stMarkdown"] > div,
.st-key-analysis_summary [data-testid="stColumn"]:first-child [data-testid="stMarkdownContainer"],
.st-key-analysis_summary .asset-card {{ height: 100% !important; }}
.st-key-analysis_summary [data-testid="stColumn"]:first-child [data-testid="stMarkdown"] > div {{ display: flex; flex-direction: column; }}
.st-key-analysis_summary [data-testid="stColumn"]:first-child [data-testid="stMarkdownContainer"] {{ flex: 1; margin: 0 !important; }}

/* Detalhes do processamento (app/ui/data_info.py): grade compacta */
.pd-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); border: 1px solid {LINE_SOFT}; background: {PAPER}; }}
.pd-cell {{ padding: 8px 12px; border-right: 1px solid {LINE_SOFT}; border-bottom: 1px solid {LINE_SOFT}; }}
.pd-cell.pd-wide {{ grid-column: 1 / -1; }}
.pd-cell span {{ display: block; color: {MUTED}; font-size: .68rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }}
.pd-cell b {{ display: block; margin-top: 2px; color: {INK}; font-size: .9rem; font-weight: 600; line-height: 1.45; }}

/* Títulos de seção (st.header e ###): sóbrios, com filete superior */
[data-testid="stMain"] [data-testid="stHeading"] h2 {{
    margin-top: 1.6rem; padding-top: 1rem !important; border-top: 1px solid {LINE_SOFT};
    font-size: 1.5rem; font-weight: 750; letter-spacing: -.01em; color: {INK};
}}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] > h3 {{ font-weight: 700; letter-spacing: -.01em; color: {INK}; }}
[data-testid="stSidebar"] [data-testid="stHeading"] h2 {{
    font-size: 1.05rem; font-weight: 750; letter-spacing: .02em; text-transform: uppercase; color: {INK};
    padding-bottom: .4rem !important; border-bottom: 2px solid {ACCENT};
}}
[data-testid="stSidebar"] [data-testid="stHeading"] {{ margin-bottom: 1rem !important; }}

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
