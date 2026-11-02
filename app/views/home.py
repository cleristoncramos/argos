import os
import sys

import streamlit as st
import streamlit.components.v1 as components

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.ui.academic_dialog import show_academic_dialog  # noqa: E402
from app.ui.landing import FEATURES_VIDEO, build_mosaic_html, catalog_stats  # noqa: E402
from app.ui.pages import ANALYSIS_PAGES, START_PAGE  # noqa: E402
from core.asset_logos import get_asset_logo_url  # noqa: E402
from core.assets import ASSETS  # noqa: E402


# ==========================================================
# ESTILO DA PÁGINA INICIAL (tema claro com profundidade, cantos retos)
# ==========================================================
st.markdown(
    """
<style>
[data-testid="stSidebar"], [data-testid="collapsedControl"], header, footer { display: none !important; }
#MainMenu { visibility: hidden !important; }
.stApp {
    background:
        radial-gradient(1000px 420px at 85% -8%, rgba(200, 16, 46, .09), transparent 60%),
        radial-gradient(900px 480px at -10% 14%, rgba(29, 78, 216, .06), transparent 60%),
        #F7F6F2 !important;
}
.stApp::before {
    content: ""; position: fixed; inset: 0; pointer-events: none;
    background-image: linear-gradient(rgba(17, 17, 17, .025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(17, 17, 17, .025) 1px, transparent 1px);
    background-size: 56px 56px;
    -webkit-mask-image: radial-gradient(ellipse at 50% 0%, #000 0%, transparent 70%);
            mask-image: radial-gradient(ellipse at 50% 0%, #000 0%, transparent 70%);
}
/* Largura total, como nas demais páginas (sem limite lateral) */
.block-container { max-width: none !important; padding-top: 1.2rem !important; padding-bottom: 1rem !important; }

@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: .25; } }

/* ---------- barra superior ---------- */
.st-key-topbar { padding: 10px 0 14px; border-bottom: 1px solid #e4e1da; animation: rise .5s ease both; }
.st-key-topbar_right { gap: 10px !important; }
.st-key-topbar [data-testid="stMarkdownContainer"] { margin-bottom: 0 !important; }
.brand { display: flex; align-items: center; gap: 10px; color: #111; font-weight: 800; letter-spacing: .16em;
    font-size: .8rem; text-transform: uppercase; }
.brand-mark { width: 26px; height: 26px; display: grid; place-items: center;
    background: linear-gradient(135deg, #E11D48, #B50E29); box-shadow: 0 4px 12px rgba(200, 16, 46, .3); color: #fff;
    font-size: .8rem; font-weight: 800; letter-spacing: 0; }
.top-meta { display: flex; border: 1px solid #e4e1da; font-size: .68rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: #3a3a3a; background: #fff; box-shadow: 0 4px 14px rgba(17, 17, 17, .05); }
.top-meta span { padding: 6px 12px; border-right: 1px solid #e4e1da; }
.top-meta span:last-child { border-right: 0; }
.live { display: inline-block; width: 7px; height: 7px; background: #16a34a; margin-right: 7px; animation: blink 1.6s infinite; }

/* ---------- hero ---------- */
.eyebrow { margin-top: 28px; color: #c8102e; font-size: .74rem; font-weight: 700; letter-spacing: .22em;
    text-transform: uppercase; animation: rise .6s .05s ease both; }
.hero-title { margin: 12px 0 0; font-size: clamp(3rem, 6vw, 5.2rem); line-height: .95; font-weight: 800;
    letter-spacing: -.045em; color: #111; animation: rise .6s .12s ease both; }
.hero-title span { background: linear-gradient(100deg, #B50E29 0%, #E11D48 55%, #F97316 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero-tagline { margin-top: 18px; padding-left: 14px; border-left: 3px solid #c8102e; font-size: clamp(1.2rem, 2vw, 1.5rem);
    line-height: 1.3; font-weight: 650; color: #111; animation: rise .6s .2s ease both; }
.hero-sub { margin-top: 14px; font-size: 1rem; line-height: 1.7; color: #4a4a4a; text-align: justify; hyphens: auto;
    animation: rise .6s .28s ease both; }
.hero-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 26px 0 20px;
    animation: rise .6s .36s ease both; }
.hero-stats div { position: relative; padding: 16px 10px 14px; text-align: center; background: #fff;
    border: 1px solid #e4e1da; box-shadow: 0 8px 22px rgba(17, 17, 17, .06);
    transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease; }
.hero-stats div::before { content: ""; position: absolute; top: -1px; left: 50%; width: 32px; height: 3px;
    transform: translateX(-50%); background: linear-gradient(90deg, #B50E29, #F97316); transition: width .25s ease; }
.hero-stats div:hover { transform: translateY(-3px); border-color: #2a2a2a; box-shadow: 0 14px 30px rgba(17, 17, 17, .11); }
.hero-stats div:hover::before { width: 100%; }
.hero-stats b { display: block; font-size: 1.75rem; font-weight: 800; line-height: 1.1; letter-spacing: -.03em;
    background: linear-gradient(135deg, #111 0%, #3a3a3a 55%, #B50E29 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero-stats small { display: block; margin-top: 6px; color: #6b6b6b; font-size: .64rem; text-transform: uppercase;
    letter-spacing: .16em; font-weight: 700; }
.hero-note { margin-top: 8px; color: #5f5f5f; font-size: .76rem; }

/* ---------- botões ---------- */
/* Get Started: gradiente que se desloca devagar */
@keyframes flow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
.st-key-cta_start button { min-height: 52px; font-weight: 700 !important; letter-spacing: .04em; color: #fff !important;
    background: linear-gradient(110deg, #9F0C24 0%, #C8102E 25%, #E11D48 50%, #F0563A 70%, #C8102E 100%) !important;
    background-size: 260% 100% !important; animation: flow 9s ease-in-out infinite;
    border: 1px solid #7A0A1C !important; box-shadow: 0 10px 24px rgba(200, 16, 46, .28) !important;
    transition: transform .15s ease, box-shadow .15s ease !important; }
.st-key-cta_start button:hover { transform: translateY(-2px); box-shadow: 0 14px 30px rgba(200, 16, 46, .36) !important; }
.st-key-cta_start p { color: inherit !important; font-weight: 700 !important; }

/* Informações acadêmicas: botão pequeno ao lado dos selos */
.st-key-cta_academic button { min-height: 0 !important; height: auto; padding: 6px 12px !important; background: #fff !important;
    border: 1px solid #e4e1da !important; box-shadow: 0 4px 14px rgba(17, 17, 17, .05) !important; color: #3a3a3a !important;
    transition: background .15s ease, color .15s ease !important; }
.st-key-cta_academic button p { font-size: .68rem !important; font-weight: 700 !important; letter-spacing: .12em;
    text-transform: uppercase; color: inherit !important; }
.st-key-cta_academic button:hover { background: #111 !important; color: #fff !important; border-color: #111 !important; }

/* ---------- vídeo ---------- */
.st-key-hero_video { width: 90% !important; margin: 36px auto 0; border: 1px solid #d8d4cc; background: #fff; gap: 0 !important; animation: rise .8s .2s ease both;
    box-shadow: 0 30px 60px rgba(17, 17, 17, .16), 0 0 0 6px rgba(255, 255, 255, .6);
    transform: perspective(1600px) rotateY(-3deg) rotateX(1.5deg); transition: transform .6s ease; }
.st-key-hero_video:hover { transform: none; }
.st-key-hero_video video { display: block; width: 100%; }
.st-key-hero_video [data-testid="stElementContainer"],
.st-key-hero_video [data-testid="stMarkdownContainer"] { margin: 0 !important; }
.video-bar { display: flex; align-items: center; padding: 8px 12px;
    border-bottom: 2px solid #c8102e; background: linear-gradient(180deg, #2b2b31, #1b1b1f); color: #fff; font-size: .7rem; font-weight: 700;
    letter-spacing: .14em; text-transform: uppercase; }
.video-caption { width: 90%; margin: 14px auto 0; color: #5f5f5f; font-size: .78rem; text-align: center; }
.video-missing { aspect-ratio: 16/9; display: grid; place-items: center; color: #5f5f5f; }

/* ---------- seções ---------- */
.section { margin: 72px 0 22px; padding-top: 28px; border-top: 1px solid #2a2a2a; }
.section-kicker { display: flex; align-items: center; gap: 10px; color: #c8102e; font-size: .72rem; font-weight: 700;
    letter-spacing: .2em; text-transform: uppercase; }
.section-kicker::before { content: ""; width: 22px; height: 2px; background: linear-gradient(90deg, #B50E29, #F97316); }
.section-title { margin-top: 10px; color: #111; font-size: clamp(1.5rem, 2.6vw, 2rem); font-weight: 800; letter-spacing: -.03em; line-height: 1.15; }
.section-sub { margin-top: 8px; max-width: 760px; color: #5f5f5f; font-size: .95rem; line-height: 1.6; }

/* ---------- tutorial ---------- */
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.step { position: relative; overflow: hidden; min-height: 210px; padding: 26px 26px 28px;
    background: linear-gradient(155deg, #1d1d22 0%, #141417 100%); border: 1px solid #111;
    box-shadow: 0 14px 30px rgba(17, 17, 17, .16); transition: transform .25s ease, box-shadow .25s ease; }
.step::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #B50E29, #E11D48 55%, #F97316); }
.step::after { content: attr(data-n); position: absolute; right: 14px; bottom: -22px; font-family: "JetBrains Mono", ui-monospace, Consolas, monospace;
    font-size: 6.5rem; font-weight: 800; line-height: 1; letter-spacing: -.06em; color: rgba(255, 255, 255, .05); pointer-events: none; }
.step:hover { transform: translateY(-4px); box-shadow: 0 20px 40px rgba(17, 17, 17, .24); }
.step-n { display: inline-block; padding: 3px 8px; font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: .72rem;
    font-weight: 700; color: #fff; letter-spacing: .1em; background: linear-gradient(135deg, #E11D48, #B50E29);
    box-shadow: 0 4px 12px rgba(225, 29, 72, .35); }
.step h4 { margin: 16px 0 8px; color: #fff !important; font-size: 1.18rem; font-weight: 750; padding: 0 !important; }
.step p { position: relative; margin: 0; color: #c9c9cf !important; font-size: .92rem; line-height: 1.65; }
.step kbd { padding: 1px 6px; border: 1px solid #3a3a42; background: #26262c; color: #fff; font-size: .78rem; font-family: inherit; }

/* ---------- primeiros passos: seis etapas lado a lado ---------- */
.st-key-first_steps { position: relative; padding-top: 30px; }
.st-key-first_steps::before { content: ""; position: absolute; top: 9px; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #c8102e 0%, #e11d48 45%, #f97316 100%); opacity: .55; }
.st-key-first_steps [data-testid="stHorizontalBlock"] { align-items: stretch; }
.st-key-first_steps [data-testid="stColumn"] { display: flex; flex-direction: column; align-self: stretch; }
.st-key-first_steps [data-testid="stColumn"] > [data-testid="stVerticalBlock"],
.st-key-first_steps [data-testid="stColumn"] [data-testid="stLayoutWrapper"] { flex: 1 1 auto; }
[class*="st-key-fs_"] { position: relative; flex: 1 1 auto; padding: 18px 18px 14px; background: #fff; border: 1px solid #e4e1da;
    box-shadow: 0 8px 22px rgba(17, 17, 17, .05); gap: 0 !important;
    transition: transform .25s ease, box-shadow .25s ease, background .25s ease; }
[class*="st-key-fs_"]::before { content: ""; position: absolute; top: -27px; left: 18px; width: 12px; height: 12px;
    border-radius: 50% !important; background: #fff; border: 2px solid #c8102e; box-shadow: 0 0 0 4px #f6f4ef;
    transition: background .25s ease; }
[class*="st-key-fs_"]:hover { transform: translateY(-4px); border-color: #d8d4cc;
    box-shadow: inset 0 3px 0 #c8102e, 0 16px 32px rgba(17, 17, 17, .1); }
[class*="st-key-fs_"]:hover::before { background: #c8102e; }
[class*="st-key-fs_"] > div:last-child { margin-top: auto; width: 100%; }
.fs-top { display: flex; justify-content: space-between; align-items: flex-start; }
.fs-n { font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: 1.9rem; font-weight: 800; line-height: 1;
    letter-spacing: -.04em; background: linear-gradient(135deg, #B50E29 0%, #E11D48 55%, #F97316 100%);
    -webkit-background-clip: text; background-clip: text; color: transparent; }
.fs-icon { font-size: 1.25rem; }
.fs-title { margin-top: 14px; color: #111; font-weight: 750; font-size: .98rem; line-height: 1.25; }
.fs-desc { margin: 8px 0 12px; color: #4a4a4a; font-size: .83rem; line-height: 1.55; }
[class*="st-key-fs_"] [data-testid="stPageLink"] { width: 100%; padding-top: 10px; border-top: 1px solid #e4e1da; }
[class*="st-key-fs_"] [data-testid="stPageLink"] a { padding: 0 !important; background: transparent !important; }
[class*="st-key-fs_"] [data-testid="stPageLink"] p { color: #c8102e !important; font-weight: 700 !important; font-size: .82rem !important; }

/* ---------- rodapé ---------- */
.home-footer { margin-top: 88px; padding: 18px 0 6px; border-top: 1px solid #2a2a2a; display: flex;
    justify-content: space-between; gap: 18px; flex-wrap: wrap; color: #5f5f5f; font-size: .76rem; }
.home-footer b { color: #111; letter-spacing: .1em; }

@media (max-width: 1200px) {
    .st-key-first_steps [data-testid="stHorizontalBlock"] { flex-wrap: wrap; row-gap: 40px; }
    .st-key-first_steps [data-testid="stColumn"] { flex: 1 1 calc(33.333% - 1rem) !important; min-width: 200px; }
}
@media (max-width: 900px) {
    .steps { grid-template-columns: 1fr; }
    .hero-stats { grid-template-columns: repeat(2, 1fr); }
    .st-key-hero_video, .video-caption { width: 100% !important; }
    .top-meta span:not(:first-child) { display: none; }
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
with st.container(key="topbar", horizontal=True, horizontal_alignment="distribute", vertical_alignment="center"):
    st.markdown('<div class="brand"><span class="brand-mark">A</span>Argos</div>', unsafe_allow_html=True, width="content")
    with st.container(key="topbar_right", horizontal=True, vertical_alignment="center", width="content"):
        st.markdown(
            '<div class="top-meta"><span><i class="live"></i>Online</span><span>PIBITI</span><span>UFPI · CEAD</span></div>',
            unsafe_allow_html=True,
            width="content",
        )
        with st.container(key="cta_academic", width="content"):
            if st.button("Informações acadêmicas"):
                show_academic_dialog()

# ==========================================================
# HERO: TEXTO, BOTÕES E VÍDEO
# ==========================================================
col_text, col_video = st.columns([1, 1.15], gap="large", vertical_alignment="center")

with col_text:
    st.markdown(
        f"""
<div class="eyebrow">Pesquisa e educação financeira · PIBITI UFPI</div>
<div class="hero-title">Argos</div>
<div class="hero-tagline">Plataforma de Análise Histórica de Ativos Financeiros</div>
<div class="hero-sub">
  Consulte o histórico de {stats["assets"]} ativos do catálogo, entre ações brasileiras e
  americanas, ETFs, FIIs, criptomoedas, moedas, commodities, índices e renda fixa, com
  dados do Yahoo Finance. Analise um ativo por vez, compare vários na mesma base,
  acompanhe indicadores técnicos, meça risco e retorno, observe a sazonalidade,
  simule aportes periódicos e veja o catálogo inteiro em um panorama. Cada gráfico
  traz um roteiro de leitura em linguagem simples, e alertas de qualidade indicam
  trechos dos dados que merecem atenção.
</div>
<div class="hero-stats">
  <div><b>{stats["assets"]}</b><small>ativos</small></div>
  <div><b>{stats["classes"]}</b><small>classes</small></div>
  <div><b>{stats["groups"]}</b><small>grupos</small></div>
  <div><b>6</b><small>módulos</small></div>
</div>
""",
        unsafe_allow_html=True,
    )
    with st.container(key="cta_start"):
        if st.button("Get Started  →", use_container_width=True):
            st.switch_page(START_PAGE.path)
    st.markdown(
        '<div class="hero-note">Finalidade educacional e de pesquisa. '
        "Não constitui recomendação de investimento.</div>",
        unsafe_allow_html=True,
    )

with col_video:
    with st.container(key="hero_video"):
        st.markdown(
            '<div class="video-bar"><span>▶ Tour pelos recursos</span></div>',
            unsafe_allow_html=True,
        )
        if FEATURES_VIDEO.exists():
            st.video(str(FEATURES_VIDEO), autoplay=True, muted=True, loop=True)
        else:
            st.markdown('<div class="video-missing">Vídeo indisponível</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="video-caption">Análise individual, comparação, indicadores técnicos, '
        "risco e retorno, sazonalidade e simulação de aportes.</div>",
        unsafe_allow_html=True,
    )

# ==========================================================
# MOSAICO DE ATIVOS
# ==========================================================
st.markdown(
    f"""
<div class="section">
  <div class="section-kicker">01 · Catálogo</div>
  <div class="section-title">Um mosaico do mercado, em um só lugar</div>
  <div class="section-sub">{stats["assets"]} ativos organizados em {stats["groups"]} grupos: do Bitcoin à
  Petrobras, do ouro ao S&amp;P 500. Passe o mouse para pausar.</div>
</div>
""",
    unsafe_allow_html=True,
)
components.html(build_mosaic_html(ASSETS, get_asset_logo_url), height=284, scrolling=False)

# ==========================================================
# TUTORIAL BREVE
# ==========================================================
st.markdown(
    """
<div class="section">
  <div class="section-kicker">02 · Tutorial rápido</div>
  <div class="section-title">Sua primeira análise em 3 passos</div>
  <div class="section-sub">Leva menos de um minuto. Todas as páginas de análise seguem o mesmo fluxo.</div>
</div>
<div class="steps">
  <div class="step" data-n="01"><div class="step-n">PASSO 01</div><h4>Escolha o ativo</h4>
    <p>Na barra lateral, escolha o grupo e o ativo ou digite o ticker direto, como <kbd>PETR4.SA</kbd> ou <kbd>BTC-USD</kbd>.</p></div>
  <div class="step" data-n="02"><div class="step-n">PASSO 02</div><h4>Defina o período</h4>
    <p>Use os atalhos de 1, 3, 5 ou 10 anos ou escolha as datas. Ajuste a frequência: diária, semanal, mensal, semestral ou anual.</p></div>
  <div class="step" data-n="03"><div class="step-n">PASSO 03</div><h4>Carregue e explore</h4>
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
  <div class="section-kicker">03 · Primeiros passos</div>
  <div class="section-title">Por onde começar</div>
  <div class="section-sub">Cada módulo responde a uma pergunta diferente sobre os dados históricos.</div>
</div>
""",
    unsafe_allow_html=True,
)

# Módulos de análise, na mesma ordem do menu principal (app/ui/pages.py);
# a página Sobre o Projeto fica só no menu.
# Todos lado a lado, como etapas de uma linha do tempo.
with st.container(key="first_steps"):
    columns = st.columns(len(ANALYSIS_PAGES), gap="small")
    for index, (column, spec) in enumerate(zip(columns, ANALYSIS_PAGES)):
        with column, st.container(key=f"fs_{index}"):
            st.markdown(
                f'<div class="fs-top"><span class="fs-n">{index + 1:02d}</span>'
                f'<span class="fs-icon">{spec.icon}</span></div>'
                f'<div class="fs-title">{spec.title}</div><div class="fs-desc">{spec.description}</div>',
                unsafe_allow_html=True,
            )
            st.page_link(spec.path, label="Abrir módulo →")

# ==========================================================
# RODAPÉ
# ==========================================================
st.markdown(
    """
<div class="home-footer">
  <div><b>ARGOS</b> · PIBITI UFPI 2026–2027 · CEAD · Tecnologia em Gestão de Dados</div>
  <div>Dados históricos via Yahoo Finance · Uso educacional, sem recomendação de investimento</div>
</div>
""",
    unsafe_allow_html=True,
)
