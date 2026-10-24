import os
import sys

import streamlit as st
import streamlit.components.v1 as components

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.ui.landing import TOUR_VIDEO, build_mosaic_html, catalog_stats  # noqa: E402
from core.asset_logos import get_asset_logo_url  # noqa: E402
from core.assets import ASSETS  # noqa: E402

ANALYSIS_PAGE = "views/analise_individual.py"
ACADEMIC_PAGE = "views/informacoes_academicas.py"

# ==========================================================
# ESTILO DA PÁGINA INICIAL
# ==========================================================
st.markdown(
    """
<style>
[data-testid="stSidebar"], [data-testid="collapsedControl"], header, footer { display: none !important; }
#MainMenu { visibility: hidden !important; }

.stApp {
    background:
        radial-gradient(1100px 520px at 78% -8%, rgba(239, 68, 68, 0.16), transparent 60%),
        radial-gradient(900px 600px at -10% 20%, rgba(56, 189, 248, 0.10), transparent 60%),
        linear-gradient(180deg, #050b17 0%, #040915 55%, #030711 100%) !important;
    color: #e2e8f0;
}
.stApp::before {
    content: ""; position: fixed; inset: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(148, 163, 184, 0.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(148, 163, 184, 0.045) 1px, transparent 1px);
    background-size: 56px 56px;
    -webkit-mask-image: radial-gradient(ellipse at 50% 0%, #000 0%, transparent 70%);
            mask-image: radial-gradient(ellipse at 50% 0%, #000 0%, transparent 70%);
}
.block-container { max-width: 1240px !important; padding-top: 1.6rem !important; padding-bottom: 1rem !important; }
.stApp p, .stApp li { color: #cbd5e1; }

@keyframes rise { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
@keyframes pulse { 0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.55); } 50% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); } }

/* ---------- barra superior ---------- */
.topbar { display: flex; justify-content: space-between; align-items: center; padding: 6px 0 26px; animation: rise .6s ease both; }
.brand { display: flex; align-items: center; gap: 10px; color: #f8fafc; font-weight: 800; letter-spacing: .14em; font-size: .82rem; text-transform: uppercase; }
.brand-mark { width: 30px; height: 30px; border-radius: 9px; display: grid; place-items: center;
    background: linear-gradient(135deg, #ef4444, #b91c1c); box-shadow: 0 6px 18px rgba(239, 68, 68, .35); font-size: .95rem; }
.top-pill { display: flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 999px; font-size: .72rem; font-weight: 600;
    color: #cbd5e1; background: rgba(15, 23, 42, .7); border: 1px solid rgba(148, 163, 184, .18); letter-spacing: .04em; }
.live-dot { width: 7px; height: 7px; border-radius: 50%; background: #22c55e; animation: pulse 2.2s infinite; }

/* ---------- hero ---------- */
.eyebrow { display: inline-flex; align-items: center; gap: 10px; color: #fca5a5; font-size: .74rem; font-weight: 750;
    letter-spacing: .22em; text-transform: uppercase; animation: rise .7s .05s ease both; }
.eyebrow::before { content: ""; width: 34px; height: 1px; background: #ef4444; }
.hero-title { margin: 14px 0 0; font-size: clamp(3rem, 6.2vw, 5.4rem); line-height: .95; font-weight: 850; letter-spacing: -.05em;
    color: #f8fafc; animation: rise .7s .12s ease both; }
.hero-title span { background: linear-gradient(100deg, #f87171 0%, #ef4444 45%, #fb923c 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero-tagline { margin-top: 18px; font-size: clamp(1.25rem, 2.2vw, 1.6rem); line-height: 1.3; font-weight: 650; color: #e2e8f0;
    letter-spacing: -.01em; animation: rise .7s .2s ease both; }
.hero-sub { margin-top: 14px; max-width: 560px; font-size: 1rem; line-height: 1.7; color: #94a3b8; animation: rise .7s .28s ease both; }
.hero-stats { display: flex; gap: 26px; margin: 26px 0 8px; animation: rise .7s .36s ease both; }
.hero-stats b { display: block; font-size: 1.55rem; font-weight: 800; color: #f8fafc; letter-spacing: -.02em; }
.hero-stats small { color: #64748b; font-size: .72rem; text-transform: uppercase; letter-spacing: .1em; font-weight: 650; }
.hero-note { margin-top: 10px; color: #64748b; font-size: .76rem; animation: rise .7s .5s ease both; }

/* ---------- botões ---------- */
.st-key-cta_start button, .st-key-cta_academic button {
    min-height: 52px; border-radius: 12px !important; font-weight: 750 !important; font-size: .95rem !important;
    letter-spacing: .02em; transition: transform .2s ease, box-shadow .2s ease, background .2s ease !important; }
.st-key-cta_start button { background: linear-gradient(135deg, #ef4444, #dc2626) !important; border: 1px solid #f87171 !important;
    color: #fff !important; box-shadow: 0 10px 30px rgba(220, 38, 38, .35) !important; }
.st-key-cta_start button:hover { transform: translateY(-2px); box-shadow: 0 16px 38px rgba(239, 68, 68, .45) !important; }
.st-key-cta_academic button { background: rgba(15, 23, 42, .65) !important; border: 1px solid rgba(148, 163, 184, .35) !important; color: #e2e8f0 !important; }
.st-key-cta_academic button:hover { transform: translateY(-2px); border-color: #e2e8f0 !important; background: rgba(30, 41, 59, .85) !important; }
.st-key-cta_start p, .st-key-cta_academic p { color: inherit !important; font-weight: 750 !important; }
.st-key-hero_ctas { animation: rise .7s .42s ease both; }

/* ---------- vídeo ---------- */
.st-key-hero_video { position: relative; border-radius: 16px; overflow: hidden; gap: 0 !important;
    background: #0b1222; border: 1px solid rgba(148, 163, 184, .2);
    box-shadow: 0 40px 80px rgba(0, 0, 0, .55), 0 0 0 1px rgba(255, 255, 255, .03), 0 0 120px rgba(239, 68, 68, .12);
    animation: rise .9s .25s ease both; transform: perspective(1600px) rotateY(-4deg) rotateX(2deg); transition: transform .6s ease; }
.st-key-hero_video:hover { transform: none; }
.st-key-hero_video video { display: block; width: 100%; border-radius: 0 !important; }
.st-key-hero_video [data-testid="stElementContainer"] { margin: 0 !important; }
.win-bar { display: flex; align-items: center; gap: 7px; padding: 10px 14px; background: #0f172a; border-bottom: 1px solid rgba(148, 163, 184, .14); }
.win-bar i { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.win-url { margin-left: 12px; flex: 1; padding: 4px 12px; border-radius: 7px; background: rgba(148, 163, 184, .1);
    color: #94a3b8; font-size: .72rem; font-family: "JetBrains Mono", ui-monospace, monospace; }
.video-caption { margin-top: 12px; text-align: center; color: #64748b; font-size: .76rem; }
.video-missing { aspect-ratio: 16/9; display: grid; place-items: center; color: #64748b; font-size: .9rem; }

/* ---------- seções ---------- */
.section { margin: 74px 0 22px; text-align: center; }
.section-kicker { color: #f87171; font-size: .72rem; font-weight: 750; letter-spacing: .22em; text-transform: uppercase; }
.section-title { margin-top: 10px; color: #f8fafc; font-size: clamp(1.6rem, 3vw, 2.25rem); font-weight: 800; letter-spacing: -.03em; }
.section-sub { margin: 10px auto 0; max-width: 640px; color: #94a3b8; font-size: .96rem; line-height: 1.6; }

/* ---------- tutorial ---------- */
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; counter-reset: step; }
.step { position: relative; padding: 26px 24px 24px; border-radius: 16px; text-align: left;
    background: linear-gradient(160deg, rgba(30, 41, 59, .6), rgba(15, 23, 42, .75)); border: 1px solid rgba(148, 163, 184, .14);
    transition: transform .25s ease, border-color .25s ease; }
.step:hover { transform: translateY(-4px); border-color: rgba(239, 68, 68, .45); }
.step-n { width: 38px; height: 38px; border-radius: 11px; display: grid; place-items: center; font-weight: 800; color: #fff;
    background: linear-gradient(135deg, #ef4444, #b91c1c); box-shadow: 0 8px 20px rgba(239, 68, 68, .3); }
.step h4 { margin: 16px 0 6px; color: #f8fafc !important; font-size: 1.05rem; font-weight: 750; padding: 0 !important; }
.step p { margin: 0; color: #94a3b8 !important; font-size: .88rem; line-height: 1.6; }
.step kbd { padding: 1px 6px; border-radius: 5px; background: rgba(148, 163, 184, .16); color: #e2e8f0; font-size: .78rem; font-family: inherit; }

/* ---------- primeiros passos ---------- */
[class*="st-key-fs_"] { height: 100%; padding: 22px 22px 14px; border-radius: 16px;
    background: linear-gradient(160deg, rgba(30, 41, 59, .55), rgba(15, 23, 42, .72)); border: 1px solid rgba(148, 163, 184, .14);
    transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease; }
[class*="st-key-fs_"]:hover { transform: translateY(-4px); border-color: rgba(248, 113, 113, .5); box-shadow: 0 18px 40px rgba(0, 0, 0, .35); }
.fs-icon { font-size: 1.6rem; }
.fs-title { margin-top: 10px; color: #f8fafc; font-weight: 750; font-size: 1.02rem; }
.fs-desc { margin-top: 6px; color: #94a3b8; font-size: .86rem; line-height: 1.55; min-height: 4.1em; }
[class*="st-key-fs_"] [data-testid="stPageLink"] a { padding: 0 !important; background: transparent !important; }
[class*="st-key-fs_"] [data-testid="stPageLink"] p { color: #f87171 !important; font-weight: 700 !important; font-size: .88rem !important; }
[class*="st-key-fs_"] [data-testid="stPageLink"] a:hover p { color: #fecaca !important; }

/* ---------- rodapé ---------- */
.home-footer { margin-top: 70px; padding: 22px 0 8px; border-top: 1px solid rgba(148, 163, 184, .12);
    display: flex; justify-content: space-between; gap: 18px; flex-wrap: wrap; color: #64748b; font-size: .76rem; }
.home-footer b { color: #cbd5e1; letter-spacing: .1em; }

@media (max-width: 900px) {
    .steps { grid-template-columns: 1fr; }
    .st-key-hero_video { transform: none; }
    .hero-stats { gap: 18px; flex-wrap: wrap; }
}
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
</style>
""",
    unsafe_allow_html=True,
)

stats = catalog_stats(ASSETS)

# ==========================================================
# BARRA SUPERIOR
# ==========================================================
st.markdown(
    """
<div class="topbar">
  <div class="brand"><span class="brand-mark">👁</span>Argos DataLab</div>
  <div class="top-pill"><span class="live-dot"></span>PIBITI · UFPI · CEAD</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# HERO: TEXTO, BOTÕES E VÍDEO
# ==========================================================
col_text, col_video = st.columns([1, 1.18], gap="large", vertical_alignment="center")

with col_text:
    st.markdown(
        f"""
<div class="eyebrow">Laboratório de dados financeiros</div>
<div class="hero-title">Argos <span>DataLab</span></div>
<div class="hero-tagline">Os cem olhos dos dados sobre o mercado financeiro.</div>
<div class="hero-sub">
  Explore o histórico de ações, criptomoedas, FIIs, commodities e índices.
  Compare ativos, leia indicadores técnicos e meça risco e retorno, com
  explicações em linguagem simples e foco educacional.
</div>
<div class="hero-stats">
  <div><b>{stats["assets"]}</b><small>ativos</small></div>
  <div><b>{stats["classes"]}</b><small>classes</small></div>
  <div><b>{stats["groups"]}</b><small>mercados</small></div>
  <div><b>6</b><small>módulos</small></div>
</div>
""",
        unsafe_allow_html=True,
    )
    with st.container(key="hero_ctas"):
        cta_start, cta_academic = st.columns(2)
        with cta_start:
            with st.container(key="cta_start"):
                if st.button("Get Started  →", use_container_width=True):
                    st.switch_page(ANALYSIS_PAGE)
        with cta_academic:
            with st.container(key="cta_academic"):
                if st.button("🎓  Informações acadêmicas", use_container_width=True):
                    st.switch_page(ACADEMIC_PAGE)
    st.markdown(
        '<div class="hero-note">Finalidade educacional e de pesquisa. '
        "Não constitui recomendação de investimento.</div>",
        unsafe_allow_html=True,
    )

with col_video:
    with st.container(key="hero_video"):
        st.markdown(
            '<div class="win-bar"><i style="background:#ef4444"></i><i style="background:#f59e0b"></i>'
            '<i style="background:#22c55e"></i><span class="win-url">argos-datalab.streamlit.app</span></div>',
            unsafe_allow_html=True,
        )
        if TOUR_VIDEO.exists():
            st.video(str(TOUR_VIDEO), autoplay=True, muted=True, loop=True)
        else:
            st.markdown('<div class="video-missing">Vídeo de demonstração indisponível</div>',
                        unsafe_allow_html=True)
    st.markdown(
        '<div class="video-caption">▶ Navegação real pelo Argos com dados do Yahoo Finance: '
        "análise individual, indicadores técnicos e risco e retorno.</div>",
        unsafe_allow_html=True,
    )

# ==========================================================
# MOSAICO DE ATIVOS
# ==========================================================
st.markdown(
    f"""
<div class="section">
  <div class="section-kicker">Catálogo</div>
  <div class="section-title">Um mosaico do mercado, em um só lugar</div>
  <div class="section-sub">{stats["assets"]} ativos organizados em {stats["groups"]} mercados: do Bitcoin à Petrobras,
  do ouro ao S&amp;P 500. Passe o mouse para pausar.</div>
</div>
""",
    unsafe_allow_html=True,
)
components.html(build_mosaic_html(ASSETS, get_asset_logo_url), height=232, scrolling=False)

# ==========================================================
# TUTORIAL BREVE
# ==========================================================
st.markdown(
    """
<div class="section">
  <div class="section-kicker">Tutorial rápido</div>
  <div class="section-title">Sua primeira análise em 3 passos</div>
  <div class="section-sub">Leva menos de um minuto. Todas as páginas de análise seguem o mesmo fluxo.</div>
</div>
<div class="steps">
  <div class="step"><div class="step-n">1</div><h4>Escolha o ativo</h4>
    <p>Na barra lateral, filtre por classe e mercado ou digite o ticker direto, como <kbd>PETR4.SA</kbd> ou <kbd>BTC-USD</kbd>.</p></div>
  <div class="step"><div class="step-n">2</div><h4>Defina o período</h4>
    <p>Use os atalhos de 1, 3, 5 ou 10 anos ou escolha as datas. Ajuste a frequência: diária, semanal ou mensal.</p></div>
  <div class="step"><div class="step-n">3</div><h4>Carregue e explore</h4>
    <p>Clique em <kbd>Carregar dados</kbd>: gráficos interativos, métricas com explicações e exportação em CSV.</p></div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# PRIMEIROS PASSOS
# ==========================================================
st.markdown(
    """
<div class="section">
  <div class="section-kicker">Primeiros passos</div>
  <div class="section-title">Por onde começar</div>
  <div class="section-sub">Cada módulo responde a uma pergunta diferente sobre os dados históricos.</div>
</div>
""",
    unsafe_allow_html=True,
)

FIRST_STEPS = [
    ("📈", "Análise Individual", "Preço, volatilidade mensal e sazonalidade de um ativo ao longo do tempo.",
     "views/analise_individual.py"),
    ("⚖️", "Comparação de Ativos", "De 2 a 5 ativos em base 100, correlação e resumo de risco e retorno.",
     "views/comparacao_ativos.py"),
    ("📉", "Indicadores Técnicos", "Médias móveis, Bandas de Bollinger, RSI e MACD com guias de leitura.",
     "views/indicadores_tecnicos.py"),
    ("⚠️", "Risco e Retorno", "Volatilidade, Sharpe, drawdown máximo e distribuição dos retornos.",
     "views/risco_retorno.py"),
    ("🧪", "Simulação de Aportes", "E se eu tivesse investido? Simulação histórica, sem custos nem impostos.",
     "views/simulacao_aportes.py"),
    ("📊", "Sobre o Projeto", "Objetivos, metodologia de cálculo, fontes de dados e limitações.",
     "views/sobre_projeto.py"),
]

for row_start in range(0, len(FIRST_STEPS), 3):
    columns = st.columns(3, gap="medium")
    for offset, column in enumerate(columns):
        icon, title, description, page = FIRST_STEPS[row_start + offset]
        with column, st.container(key=f"fs_{row_start + offset}"):
            st.markdown(
                f'<div class="fs-icon">{icon}</div><div class="fs-title">{title}</div>'
                f'<div class="fs-desc">{description}</div>',
                unsafe_allow_html=True,
            )
            st.page_link(page, label="Abrir módulo →")

# ==========================================================
# RODAPÉ
# ==========================================================
st.markdown(
    """
<div class="home-footer">
  <div><b>ARGOS DATALAB</b> · PIBITI UFPI 2026–2027 · CEAD · Tecnologia em Gestão de Dados</div>
  <div>Dados históricos via Yahoo Finance · Uso educacional, sem recomendação de investimento</div>
</div>
""",
    unsafe_allow_html=True,
)
