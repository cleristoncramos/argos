import base64
import streamlit as st
import streamlit.components.v1 as components

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

st.set_page_config(
    page_title="Argos DataLab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================================
# CSS DO STREAMLIT (Para esconder a sidebar e estilizar botão)
# ==========================================================

st.markdown("""
<style>
/* Esconde as barras e menus nativos */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
header { display: none !important; }
footer { display: none !important; }
#MainMenu { visibility: hidden !important; }

/* Fundo da Página (Dark Mode Gradiente) */
.stApp {
    background: radial-gradient(circle at 50% -15%, rgba(35, 52, 100, 0.34) 0%, rgba(10, 20, 40, 0.72) 34%, #050b17 72%, #030711 100%) !important;
    color: #f8fafc;
}

/* Espaçamento Principal do Container do Streamlit */
.block-container {
    max-width: 1180px !important;
    padding-top: 3rem !important;
    padding-bottom: 0 !important;
    margin: 0 auto !important;
}

/* Estilização do Botão Nativo do Streamlit */
div[data-testid="stButton"] button {
    min-height: 54px !important;
    border-radius: 4px !important;
    border: 1px solid #ef4444 !important;
    background: #dc2626 !important;
    color: #ffffff !important;
    font-size: 0.95rem !important;
    font-weight: 750 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    box-shadow: 0 8px 28px rgba(220, 38, 38, 0.18) !important;
    transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease !important;
    margin-top: 20px !important;
    margin-bottom: 20px !important;
}

div[data-testid="stButton"] button:hover {
    background: #ef4444 !important;
    border-color: #f87171 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 35px rgba(239, 68, 68, 0.28) !important;
}
</style>
""", unsafe_allow_html=True)


# ==========================================================
# PREPARAÇÃO DO GRÁFICO SVG E CÓDIGO HTML DO CORPO
# ==========================================================

SVG_CHART = """<svg viewBox="0 0 1000 170" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M0 132 C55 125,70 138,120 116 S185 108,220 119 S275 91,315 99 S365 75,405 87 S460 63,505 76 S550 48,595 61 S650 78,695 54 S745 40,790 49 S835 30,875 38 S930 20,1000 27" fill="none" stroke="#ef4444" stroke-width="2.2" vector-effect="non-scaling-stroke" />
    <path d="M0 148 C70 141,105 150,155 136 S250 129,300 139 S390 117,440 125 S530 104,580 116 S670 95,730 104 S820 80,880 91 S950 70,1000 74" fill="none" stroke="#475569" stroke-width="1.4" vector-effect="non-scaling-stroke" />
    <g stroke="#94a3b8" stroke-width="1">
        <line x1="80" y1="94" x2="80" y2="138"/>
        <rect x="74" y="105" width="12" height="21" fill="#334155" />
        <line x1="155" y1="78" x2="155" y2="128"/>
        <rect x="149" y="88" width="12" height="25" fill="#475569" />
        <line x1="230" y1="102" x2="230" y2="145"/>
        <rect x="224" y="112" width="12" height="20" fill="#1e293b" />
        <line x1="310" y1="65" x2="310" y2="116"/>
        <rect x="304" y="77" width="12" height="26" fill="#334155" />
        <line x1="390" y1="78" x2="390" y2="126"/>
        <rect x="384" y="87" width="12" height="25" fill="#475569" />
        <line x1="475" y1="48" x2="475" y2="101"/>
        <rect x="469" y="59" width="12" height="28" fill="#334155" />
        <line x1="560" y1="65" x2="560" y2="111"/>
        <rect x="554" y="73" width="12" height="24" fill="#475569" />
        <line x1="650" y1="44" x2="650" y2="91"/>
        <rect x="644" y="52" width="12" height="25" fill="#334155" />
        <line x1="735" y1="53" x2="735" y2="101"/>
        <rect x="729" y="63" width="12" height="23" fill="#475569" />
        <line x1="825" y1="29" x2="825" y2="74"/>
        <rect x="819" y="37" width="12" height="23" fill="#334155" />
        <line x1="915" y1="24" x2="915" y2="65"/>
        <rect x="909" y="32" width="12" height="21" fill="#475569" />
    </g>
</svg>"""

b64_svg = base64.b64encode(SVG_CHART.encode("utf-8")).decode("utf-8")

# O código do painel isolado em um Iframe
HTML_CONTENT = f"""
<!DOCTYPE html>
<html>
<head>
<style>
body {{
    margin: 0;
    padding: 0;
    background-color: transparent;
    color: #f8fafc;
    font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
.argos-page {{ width: 100%; }}
.eyebrow {{
    display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 25px;
    color: #e2e8f0; font-size: 0.8rem; font-weight: 750; letter-spacing: 0.25em; text-transform: uppercase; text-shadow: 0 2px 4px rgba(0,0,0,0.4);
}}
.eyebrow-line {{ width: 40px; height: 1px; background: #ef4444; }}
.hero-title {{
    margin: 0; text-align: center; font-size: clamp(3.3rem, 7vw, 5.7rem);
    line-height: 0.98; font-weight: 850; letter-spacing: -0.065em; color: #f8fafc;
}}
.hero-title .accent {{ color: #ef4444; }}
.hero-subtitle {{
    max-width: 760px; margin: 22px auto 0; text-align: center;
    color: #94a3b8; font-size: 1.05rem; line-height: 1.7;
}}
.market-strip {{
    display: grid; grid-template-columns: repeat(5, 1fr); width: 100%; margin-top: 46px;
    border-top: 1px solid rgba(148, 163, 184, 0.14); border-bottom: 1px solid rgba(148, 163, 184, 0.14); background: rgba(15, 23, 42, 0.35);
}}
.market-item {{
    min-height: 76px; padding: 14px 18px; display: flex; flex-direction: column;
    justify-content: center; align-items: center; text-align: center; border-right: 1px solid rgba(148, 163, 184, 0.12);
}}
.market-item:last-child {{ border-right: none; }}
.market-icon {{ margin-bottom: 5px; font-size: 0.9rem; color: #94a3b8; }}
.market-name {{ color: #e2e8f0; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }}
.market-code {{ margin-top: 3px; color: #475569; font-size: 0.64rem; font-family: "JetBrains Mono", monospace; }}
.analysis-visual {{
    position: relative; width: 100%; height: 245px; margin-top: 32px; overflow: hidden;
    border: 1px solid rgba(148, 163, 184, 0.13);
    background: linear-gradient(rgba(255,255,255,0.018) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.018) 1px, transparent 1px), rgba(7, 14, 28, 0.72);
    background-size: 42px 42px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.02), 0 25px 60px rgba(0,0,0,0.25);
}}
.visual-header {{
    position: absolute; top: 15px; left: 20px; right: 20px; display: flex; justify-content: space-between; align-items: center; z-index: 5;
}}
.visual-label {{ color: #cbd5e1; font-size: 0.70rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }}
.visual-status {{ color: #475569; font-size: 0.63rem; font-family: "JetBrains Mono", monospace; }}
.chart-area {{ position: absolute; left: 3%; right: 3%; top: 50px; bottom: 12px; }}
.chart-svg {{ width: 100%; height: 100%; object-fit: fill; display: block; }}
.concept-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr); width: 100%; border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}}
.concept {{ padding: 19px 24px; text-align: center; border-right: 1px solid rgba(148, 163, 184, 0.12); }}
.concept:last-child {{ border-right: none; }}
.concept-title {{ color: #e2e8f0; font-size: 0.78rem; font-weight: 750; letter-spacing: 0.08em; text-transform: uppercase; }}
.concept-description {{ margin-top: 5px; color: #64748b; font-size: 0.70rem; }}
@media (max-width: 850px) {{
    .market-strip {{ grid-template-columns: repeat(2, 1fr); }}
    .market-item {{ border-bottom: 1px solid rgba(148, 163, 184, 0.12); }}
    .concept-grid {{ grid-template-columns: 1fr; }}
    .concept {{ border-right: none; border-bottom: 1px solid rgba(148, 163, 184, 0.12); }}
}}
</style>
</head>
<body>
<div class="argos-page">
    <div class="eyebrow">
        <span class="eyebrow-line"></span>
        TERMINAL QUANTITATIVO
        <span class="eyebrow-line"></span>
    </div>
    <h1 class="hero-title">Argos <span class="accent">DataLab</span></h1>
    <div class="hero-subtitle">Plataforma quantitativa para análise de ativos financeiros, comparação histórica, auditoria de desempenho e avaliação de risco em múltiplos mercados.</div>
    <div class="market-strip">
        <div class="market-item"><div class="market-icon">📈</div><div class="market-name">B3</div><div class="market-code">IBOV · AÇÕES</div></div>
        <div class="market-item"><div class="market-icon">◉</div><div class="market-name">Global</div><div class="market-code">NASDAQ · NYSE</div></div>
        <div class="market-item"><div class="market-icon">₿</div><div class="market-name">Crypto</div><div class="market-code">BTC · ETH · SOL</div></div>
        <div class="market-item"><div class="market-icon">⇄</div><div class="market-name">Forex</div><div class="market-code">FX · CURRENCIES</div></div>
        <div class="market-item"><div class="market-icon">◆</div><div class="market-name">Commodities</div><div class="market-code">GOLD · OIL · ETC</div></div>
    </div>
    <div class="analysis-visual">
        <div class="visual-header">
            <div class="visual-label">Market Intelligence</div>
            <div class="visual-status">MULTI-ASSET · HISTORICAL DATA</div>
        </div>
        <div class="chart-area">
            <img class="chart-svg" src="data:image/svg+xml;base64,{b64_svg}" alt="Gráfico">
        </div>
    </div>
    <div class="concept-grid">
        <div class="concept"><div class="concept-title">Desempenho</div><div class="concept-description">Retorno e evolução dos ativos</div></div>
        <div class="concept"><div class="concept-title">Histórico</div><div class="concept-description">Comparação e análise temporal</div></div>
        <div class="concept"><div class="concept-title">Risco</div><div class="concept-description">Volatilidade e métricas quantitativas</div></div>
    </div>
</div>
</body>
</html>
"""

# Renderiza o Corpo Principal
components.html(HTML_CONTENT, height=730, scrolling=False)


# ==========================================================
# BOTÃO STREAMLIT CENTRALIZADO (Uso de Colunas Nativas)
# ==========================================================
col1, col2, col3 = st.columns([1, 1.2, 1]) # O botão ficará na coluna do meio

with col2:
    if st.button("Acessar Terminal de Análise", use_container_width=True):
        st.switch_page("views/sobre_projeto.py")


# ==========================================================
# RODAPÉ (Isolado no seu próprio iframe seguro)
# ==========================================================
FOOTER_CONTENT = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
    margin: 0; padding: 0; background-color: transparent; font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.argos-footer {
    width: 100%; padding: 21px 0 24px; border-top: 1px solid rgba(148, 163, 184, 0.12);
    display: flex; justify-content: space-between; align-items: center; color: #475569; font-size: 0.65rem;
}
.footer-brand { color: #94a3b8; font-weight: 750; letter-spacing: 0.10em; text-transform: uppercase; }
.footer-markets { display: flex; gap: 18px; font-family: "JetBrains Mono", monospace; }
.footer-right { text-align: right; }
@media (max-width: 850px) {
    .argos-footer { flex-direction: column; gap: 12px; text-align: center; }
}
</style>
</head>
<body>
    <div class="argos-footer">
        <div class="footer-brand">
            ARGOS DATALAB <span style="color: #ef4444; margin: 0 4px;">·</span> PIBITI UFPI 2026-2027
        </div>
        <div class="footer-markets">
            <span>B3</span>
            <span>GLOBAL</span>
            <span>CRYPTO</span>
            <span>FOREX</span>
            <span>COMMODITIES</span>
        </div>
        <div class="footer-right">TERMINAL QUANTITATIVO · MULTI-ASSET</div>
    </div>
</body>
</html>
"""

components.html(FOOTER_CONTENT, height=80, scrolling=False)