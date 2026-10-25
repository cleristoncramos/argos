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
    background-image: linear-gradient(rgba(17, 17, 17, .035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(17, 17, 17, .035) 1px, transparent 1px);
    background-size: 56px 56px;
    -webkit-mask-image: radial-gradient(ellipse at 50% 0%, #000 0%, transparent 70%);
            mask-image: radial-gradient(ellipse at 50% 0%, #000 0%, transparent 70%);
}
/* Largura total, como nas demais páginas (sem limite lateral) */
.block-container { max-width: none !important; padding-top: 1.2rem !important; padding-bottom: 1rem !important; }

@keyframes rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: .25; } }

/* ---------- barra superior ---------- */
.topbar { display: flex; justify-content: space-between; align-items: center; padding: 10px 0 14px;
    border-bottom: 1px solid #2a2a2a; animation: rise .5s ease both; }
.brand { display: flex; align-items: center; gap: 10px; color: #111; font-weight: 800; letter-spacing: .16em;
    font-size: .8rem; text-transform: uppercase; }
.brand-mark { width: 26px; height: 26px; display: grid; place-items: center;
    background: linear-gradient(135deg, #E11D48, #B50E29); box-shadow: 0 4px 12px rgba(200, 16, 46, .3); color: #fff;
    font-size: .8rem; font-weight: 800; letter-spacing: 0; }
.top-meta { display: flex; border: 1px solid #2a2a2a; font-size: .7rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: #111; background: #fff; box-shadow: 0 10px 26px rgba(17, 17, 17, .08); }
.top-meta span { padding: 6px 12px; border-right: 1px solid #2a2a2a; }
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
.hero-stats { display: grid; grid-template-columns: repeat(4, 1fr); margin: 24px 0 18px; border: 1px solid #2a2a2a;
    background: #fff; box-shadow: 0 10px 26px rgba(17, 17, 17, .08);
    animation: rise .6s .36s ease both; }
.hero-stats div { padding: 10px 14px; border-right: 1px solid #e4e1da; }
.hero-stats div:last-child { border-right: 0; }
.hero-stats b { display: block; font-size: 1.5rem; font-weight: 800; color: #111; letter-spacing: -.02em; }
.hero-stats small { color: #5f5f5f; font-size: .66rem; text-transform: uppercase; letter-spacing: .12em; font-weight: 700; }
.hero-note { margin-top: 8px; color: #5f5f5f; font-size: .76rem; }

/* ---------- botões ---------- */
.st-key-cta_start button, .st-key-cta_academic button {
    min-height: 50px; font-weight: 700 !important; letter-spacing: .03em;
    transition: background .15s ease, color .15s ease, transform .15s ease !important; }
.st-key-cta_start button { background: linear-gradient(180deg, #D7193A 0%, #B50E29 100%) !important; border: 1px solid #7A0A1C !important;
    color: #fff !important; box-shadow: 0 10px 24px rgba(200, 16, 46, .28) !important; }
.st-key-cta_start button:hover { transform: translateY(-2px); box-shadow: 0 14px 30px rgba(200, 16, 46, .36) !important; }
.st-key-cta_academic button { background: #fff !important; border: 1px solid #2a2a2a !important; color: #111 !important;
    box-shadow: 0 8px 20px rgba(17, 17, 17, .08) !important; }
.st-key-cta_academic button:hover { background: #111 !important; color: #fff !important; transform: translateY(-1px); }
.st-key-cta_start p, .st-key-cta_academic p { color: inherit !important; font-weight: 700 !important; }

/* ---------- vídeo ---------- */
.st-key-hero_video { margin-top: 36px; border: 1px solid #2a2a2a; background: #fff; gap: 0 !important; animation: rise .8s .2s ease both;
    box-shadow: 0 30px 60px rgba(17, 17, 17, .16), 0 0 0 6px rgba(255, 255, 255, .6);
    transform: perspective(1600px) rotateY(-3deg) rotateX(1.5deg); transition: transform .6s ease; }
.st-key-hero_video:hover { transform: none; }
.st-key-hero_video video { display: block; width: 100%; }
.st-key-hero_video [data-testid="stElementContainer"],
.st-key-hero_video [data-testid="stMarkdownContainer"] { margin: 0 !important; }
.video-bar { display: flex; align-items: center; padding: 8px 12px;
    border-bottom: 2px solid #c8102e; background: linear-gradient(180deg, #2b2b31, #1b1b1f); color: #fff; font-size: .7rem; font-weight: 700;
    letter-spacing: .14em; text-transform: uppercase; }
.video-caption { margin-top: 10px; color: #5f5f5f; font-size: .78rem; }
.video-missing { aspect-ratio: 16/9; display: grid; place-items: center; color: #5f5f5f; }

/* ---------- seções ---------- */
.section { margin: 64px 0 18px; padding-top: 16px; border-top: 1px solid #2a2a2a; position: relative; display: grid;
    grid-template-columns: 220px 1fr; gap: 24px; align-items: end; }
.section-kicker { color: #c8102e; font-size: .72rem; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; }
.section-title { color: #111; font-size: clamp(1.5rem, 2.8vw, 2.1rem); font-weight: 800; letter-spacing: -.03em; line-height: 1.15; }
.section-sub { margin-top: 6px; color: #5f5f5f; font-size: .95rem; line-height: 1.6; }

/* ---------- tutorial ---------- */
.steps { display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid #2a2a2a; background: #fff; box-shadow: 0 10px 26px rgba(17, 17, 17, .08); }
.step { padding: 22px 22px 24px; border-right: 1px solid #e4e1da; transition: background .2s ease; }
.step:last-child { border-right: 0; }
.step:hover { background: linear-gradient(180deg, #fff 0%, #fbeeee 100%); }
.step-n { display: inline-block; padding: 3px 8px; font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: .74rem;
    font-weight: 700; color: #fff; letter-spacing: .1em; background: linear-gradient(135deg, #E11D48, #B50E29);
    box-shadow: 0 4px 10px rgba(200, 16, 46, .25); }
.step h4 { margin: 10px 0 6px; color: #111 !important; font-size: 1.08rem; font-weight: 750; padding: 0 !important; }
.step p { margin: 0; color: #4a4a4a !important; font-size: .9rem; line-height: 1.6; }
.step kbd { padding: 0 5px; border: 1px solid #2a2a2a; background: #fff; color: #111; font-size: .78rem; font-family: inherit; }

/* ---------- primeiros passos ---------- */
[class*="st-key-fs_"] { height: 100%; padding: 20px 20px 12px; background: #fff; border: 1px solid #2a2a2a; box-shadow: 0 10px 26px rgba(17, 17, 17, .08);
    transition: transform .25s ease, box-shadow .25s ease; }
[class*="st-key-fs_"]:hover { transform: translateY(-3px);
    box-shadow: inset 0 3px 0 #c8102e, 0 16px 34px rgba(17, 17, 17, .13); }
.fs-top { display: flex; justify-content: space-between; align-items: center; }
.fs-icon { font-size: 1.4rem; }
.fs-n { font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: .72rem; color: #5f5f5f; }
.fs-title { margin-top: 10px; color: #111; font-weight: 750; font-size: 1.02rem; }
.fs-desc { margin-top: 6px; color: #4a4a4a; font-size: .87rem; line-height: 1.55; min-height: 4.1em; }
[class*="st-key-fs_"] [data-testid="stPageLink"] a { padding: 0 !important; background: transparent !important; }
[class*="st-key-fs_"] [data-testid="stPageLink"] p { color: #c8102e !important; font-weight: 700 !important; font-size: .86rem !important; }

/* ---------- rodapé ---------- */
.home-footer { margin-top: 60px; padding: 16px 0 6px; border-top: 1px solid #2a2a2a; display: flex;
    justify-content: space-between; gap: 18px; flex-wrap: wrap; color: #5f5f5f; font-size: .76rem; }
.home-footer b { color: #111; letter-spacing: .1em; }

@media (max-width: 900px) {
    .steps { grid-template-columns: 1fr; }
    .step { border-right: 0; border-bottom: 1px solid #2a2a2a; }
    .step:last-child { border-bottom: 0; }
    .section { grid-template-columns: 1fr; gap: 6px; }
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
st.markdown(
    """
<div class="topbar">
  <div class="brand"><span class="brand-mark">A</span>Argos</div>
  <div class="top-meta"><span><i class="live"></i>Online</span><span>PIBITI</span><span>UFPI · CEAD</span></div>
</div>
""",
    unsafe_allow_html=True,
)

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
    cta_start, cta_academic = st.columns(2)
    with cta_start, st.container(key="cta_start"):
        if st.button("Get Started  →", use_container_width=True):
            st.switch_page(START_PAGE.path)
    with cta_academic, st.container(key="cta_academic"):
        if st.button("Informações acadêmicas", use_container_width=True):
            show_academic_dialog()
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
  <div><div class="section-title">Um mosaico do mercado, em um só lugar</div>
  <div class="section-sub">{stats["assets"]} ativos organizados em {stats["groups"]} grupos: do Bitcoin à
  Petrobras, do ouro ao S&amp;P 500. Passe o mouse para pausar.</div></div>
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
  <div><div class="section-title">Sua primeira análise em 3 passos</div>
  <div class="section-sub">Leva menos de um minuto. Todas as páginas de análise seguem o mesmo fluxo.</div></div>
</div>
<div class="steps">
  <div class="step"><div class="step-n">PASSO 01</div><h4>Escolha o ativo</h4>
    <p>Na barra lateral, escolha o grupo e o ativo ou digite o ticker direto, como <kbd>PETR4.SA</kbd> ou <kbd>BTC-USD</kbd>.</p></div>
  <div class="step"><div class="step-n">PASSO 02</div><h4>Defina o período</h4>
    <p>Use os atalhos de 1, 3, 5 ou 10 anos ou escolha as datas. Ajuste a frequência: diária, semanal, mensal, semestral ou anual.</p></div>
  <div class="step"><div class="step-n">PASSO 03</div><h4>Carregue e explore</h4>
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
  <div><div class="section-title">Por onde começar</div>
  <div class="section-sub">Cada módulo responde a uma pergunta diferente sobre os dados históricos.</div></div>
</div>
""",
    unsafe_allow_html=True,
)

# Módulos de análise, na mesma ordem do menu principal (app/ui/pages.py);
# a página Sobre o Projeto fica só no menu.
for row_start in range(0, len(ANALYSIS_PAGES), 3):
    columns = st.columns(3, gap="small")
    for offset, column in enumerate(columns):
        index = row_start + offset
        if index >= len(ANALYSIS_PAGES):  # última fileira incompleta
            break
        spec = ANALYSIS_PAGES[index]
        with column, st.container(key=f"fs_{index}"):
            st.markdown(
                f'<div class="fs-top"><span class="fs-icon">{spec.icon}</span>'
                f'<span class="fs-n">{index + 1:02d}</span></div>'
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
