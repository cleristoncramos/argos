import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

st.set_page_config(
    page_title="Argos DataLab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# Injeção de CSS Customizado (Dashboard Premium)
# ==========================================================
st.markdown(
    """
    <style>
    /* ==========================================================
       BARRA DE BOTÕES-ABA DOS MÓDULOS (Segmented Control)
       ========================================================== */
    div[data-testid="stHorizontalBlock"].argos-module-tabs {
        gap: 0 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        overflow: hidden !important; 
        background-color: #f8fafc !important;
        margin-bottom: 16px !important;
        width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"].argos-module-tabs > div {
        min-width: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stHorizontalBlock"].argos-module-tabs button {
        width: 100% !important;
        min-height: 48px !important;
        border-radius: 0 !important;
        border: none !important;
        border-right: 1px solid #cbd5e1 !important;
        background-color: transparent !important;
        color: #475569 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        transition: background-color 0.2s, color 0.2s;
    }
    div[data-testid="stHorizontalBlock"].argos-module-tabs > div:last-child button {
        border-right: none !important;
    }
    div[data-testid="stHorizontalBlock"].argos-module-tabs button[kind="primary"] {
        background-color: #ef4444 !important;
        color: #ffffff !important;
    }
    div[data-testid="stHorizontalBlock"].argos-module-tabs button[kind="secondary"]:hover {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
    }

    /* ==========================================================
       Refinamento geral de Grids e Cards
       ========================================================== */
    .argos-static-card {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 22px 24px;
        height: 100%;
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    .argos-static-card h3 {
        margin-top: 0;
        margin-bottom: 0.75rem;
    }
    .argos-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 12px;
    }
    .argos-grid-item {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s ease;
    }
    .argos-grid-item:hover {
        border-color: #cbd5e1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transform: translateY(-1px);
    }
    .argos-grid-title {
        font-weight: 600;
        color: #1e293b;
        font-size: 0.95rem;
    }
    .argos-grid-badge {
        background-color: #f1f5f9;
        color: #475569;
        font-size: 0.8rem;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# Cabeçalho Principal
# ==========================================================
st.markdown(
    """
    <h1 style="font-weight: 800; padding-bottom: 0.2rem; margin-top: -1rem;">
        📊 Sobre o Projeto 
        <span style="color: #ef4444; font-weight: 850; letter-spacing: -1px;">
            Argos DataLab
        </span>
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    "<p style='font-size:1.2rem; opacity: 0.8; margin-bottom:1.5rem;'>"
    "Plataforma inteligente de análise exploratória, modelagem de risco e "
    "comparação de ativos para o mercado financeiro.</p>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="display:flex; align-items:center; gap:14px; background: linear-gradient(90deg, #fef2f2 0%, #ffffff 100%);
                border: 1px solid #fecaca; border-left: 4px solid #ef4444; border-radius: 10px; padding: 16px 20px;">
        <span style="font-size:1.6rem;">💡</span>
        <span style="color:#334155; font-size:0.98rem;">
            <b>Bem-vindo ao Argos!</b> Utilize o menu lateral esquerdo para navegar entre as seções da plataforma.
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# Seção: Propósito & Visão Geral (Grid de Cards)
# ==========================================================
st.header("🎯 Propósito da Plataforma")
st.markdown(
    "O **Argos DataLab** foi desenvolvido para democratizar o acesso a ferramentas "
    "analíticas avançadas, permitindo que pesquisadores, estudantes e entusiastas do mercado "
    "examinem o comportamento histórico de ações, criptomoedas, FIIs, REITs e commodities com "
    "rigor estatístico e visualizações profissionais."
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        """
        <div style="border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; padding: 22px; height: 100%;">
            <h4 style="margin-top: 0;">🔍 Exploração Robusta</h4>
            <p style="opacity: 0.8; font-size: 0.9rem; margin-bottom: 0;">
                Navegação hierárquica por classes de ativos em português, com dados obtidos 
                em tempo real e tratados contra instabilidades de API.
            </p>
        </div>
        """, unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        """
        <div style="border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; padding: 22px; height: 100%;">
            <h4 style="margin-top: 0;">⚖️ Análise Comparativa</h4>
            <p style="opacity: 0.8; font-size: 0.9rem; margin-bottom: 0;">
                Cruzamento de múltiplos ativos (2 a 5) normalizados em Base 100, acompanhados 
                de matrizes de correlação e heatmaps dinâmicos.
            </p>
        </div>
        """, unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        """
        <div style="border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; padding: 22px; height: 100%;">
            <h4 style="margin-top: 0;">📉 Métricas de Risco</h4>
            <p style="opacity: 0.8; font-size: 0.9rem; margin-bottom: 0;">
                Cálculo de volatilidade anualizada, índice de Sharpe ajustado, análise de 
                drawdown máximo e distribuição detalhada de retornos.
            </p>
        </div>
        """, unsafe_allow_html=True,
    )

st.markdown("<br><br>", unsafe_allow_html=True)


# ==========================================================
# Seção: Catálogo de Ativos (Limpa, Linear e com Borda)
# ==========================================================
with st.container(border=True):
    st.header("📚 Catálogo de Ativos")
    st.markdown(
        "<p style='opacity: 0.8; font-size: 0.95rem; margin-bottom: 1.5rem;'>"
        "A aplicação mantém uma infraestrutura metodológica centralizada para garantir uma organização "
        "padronizada dos instrumentos financeiros disponíveis para análise.</p>",
        unsafe_allow_html=True
    )

    st.markdown("#### 📦 Composição do Catálogo")
    st.markdown(
        "O catálogo possui **120 ativos** criteriosamente mapeados e integrados ao ecossistema Yahoo Finance. "
        "Eles abrangem desde mercados tradicionais até instrumentos alternativos, "
        "garantindo cobertura global para modelagem de risco e retorno."
    )
    
    st.markdown(
        """
        <ul style="opacity:0.9; line-height:1.8; margin-top: 10px; margin-bottom: 2rem;">
            <li><b>Rigor Técnico:</b> Os registros garantem identificadores únicos para consulta precisa.</li>
            <li><b>Camada Editorial:</b> A aplicação enriquece os ativos padronizando nomes, ícones, classes e subclasses, independentemente do formato entregue pela API de mercado.</li>
            <li><b>Segurança:</b> O mapeamento evita duplicação de definições e padroniza as exibições na interface.</li>
        </ul>
        """, unsafe_allow_html=True
    )
    
    st.markdown("#### 📂 Visão Geral dos 13 Grupos Disponíveis")
    grid_grupos = """
    <div class="argos-grid">
        <div class="argos-grid-item"><span class="argos-grid-title">₿ Criptomoedas</span><span class="argos-grid-badge">10 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">🇧🇷 Ações Brasil</span><span class="argos-grid-badge">12 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">🇺🇸 Ações EUA</span><span class="argos-grid-badge">15 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">🇪🇺 Ações Europa</span><span class="argos-grid-badge">8 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">🌏 Ações Ásia</span><span class="argos-grid-badge">8 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">📈 ETFs de Ações</span><span class="argos-grid-badge">10 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">💵 ETFs de Renda Fixa</span><span class="argos-grid-badge">6 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">🏢 REITs / Mercado Imobiliário</span><span class="argos-grid-badge">5 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">🏠 FIIs Brasil</span><span class="argos-grid-badge">5 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">📊 Índices de Mercado</span><span class="argos-grid-badge">12 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">💱 Forex</span><span class="argos-grid-badge">8 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">🛢️ Commodities</span><span class="argos-grid-badge">14 ativos</span></div>
        <div class="argos-grid-item"><span class="argos-grid-title">💵 Taxas de Juros / Treasuries</span><span class="argos-grid-badge">7 ativos</span></div>
    </div>
    """
    st.markdown(grid_grupos, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)


# ==========================================================
# Seção: Módulos do Sistema (Englobada em Borda Discreta)
# ==========================================================
with st.container(border=True):
    # Âncora para injeção do CSS dos botões-aba
    st.markdown("<div id='anchor-modules'></div>", unsafe_allow_html=True)
    
    st.header("🛠️ Módulos e Funcionalidades do Sistema")
    st.markdown("<p style='opacity: 0.8; font-size: 0.95rem; margin-bottom: 1rem;'>Selecione um módulo abaixo para detalhar suas capacidades operacionais:</p>", unsafe_allow_html=True)

    MODULES = [
        {
            "key": "individual",
            "label": "📈 Análise Individual",
            "title": "Visão Geral e Sazonalidade do Ativo",
            "bullets": """
            - **Seleção Hierárquica:** Escolha de ativos divididos em classes e subclasses organizadas.
            - **Período Inteligente:** Atalhos rápidos de 1, 3, 5, 10 anos ou definição de datas personalizadas.
            - **Gráfico de Volatilidade por Mês:** Acompanhamento do desvio padrão anualizado mês a mês.
            - **Mapa de Calor Sazonal:** Visualização do comportamento estatístico e sazonais de retornos.
            - **Exportação:** Download completo dos dados tratados e limpos em formato CSV.
            """,
        },
        {
            "key": "comparacao",
            "label": "⚖️ Comparação de Ativos",
            "title": "Comparação Multi-Ativo Avançada",
            "bullets": """
            - **Seleção Flexível:** Filtros combinados por classe e subclasse para até 5 ativos simultâneos.
            - **Evolução Base 100:** Gráfico unificado com normalização de ponto de partida e tooltips monetários.
            - **Matriz de Correlação:** Heatmap triangular exclusivo que evita redundâncias e facilita a leitura de pares.
            - **Resumo Consolidado:** Tabela comparativa interativa destacando melhor retorno, menor drawdown e Sharpe.
            """,
        },
        {
            "key": "indicadores",
            "label": "📉 Indicadores Técnicos",
            "title": "Análise Técnica Aplicada",
            "bullets": """
            - **Gráficos de Preço e Candles:** Visualização de barras ou linhas de fechamento (com regra de segurança mensal).
            - **Indicadores de Tendência e Momentum:** Médias Móveis (SMA/EMA), Bandas de Bollinger, RSI e MACD.
            - **Controle de Volume:** Acompanhamento integrado da liquidez negociada do ativo.
            """,
        },
        {
            "key": "risco",
            "label": "⚠️ Risco & Retorno",
            "title": "Gestão e Métricas de Risco",
            "bullets": """
            - **Cards Executivos:** 8 indicadores-chave consolidados (Retorno Total, Médio, Win Rate, Volatilidade e Sharpe).
            - **Drawdown Máximo:** Identificação precisa do impacto e da data da pior queda do período.
            - **Taxa Livre de Risco:** Parâmetro anual configurável pelo usuário para cálculo refinado do Índice de Sharpe.
            - **Distribuição de Retornos:** Gráficos de frequência divididos em faixas percentuais padronizadas.
            """,
        },
    ]

    MODULE_SELECTION_KEY = "sobre_projeto_modulo_selecionado"

    if MODULE_SELECTION_KEY not in st.session_state:
        st.session_state[MODULE_SELECTION_KEY] = MODULES[0]["key"]


    def _select_module(module_key: str) -> None:
        st.session_state[MODULE_SELECTION_KEY] = module_key


    tab_columns = st.columns(len(MODULES))

    for column, module in zip(tab_columns, MODULES):
        is_selected = st.session_state[MODULE_SELECTION_KEY] == module["key"]
        with column:
            st.button(
                module["label"],
                key=f"module_tab_btn_{module['key']}",
                type="primary" if is_selected else "secondary",
                on_click=_select_module,
                args=(module["key"],),
                use_container_width=True
            )

    st.markdown(
        """
        <script>
        setTimeout(function() {
            var anchor = window.parent.document.getElementById('anchor-modules');
            if(anchor) {
                var verticalBlock = anchor.closest('div[data-testid="stVerticalBlock"]');
                var hBlocks = verticalBlock.querySelectorAll('div[data-testid="stHorizontalBlock"]');
                if(hBlocks.length > 0) {
                    hBlocks[0].classList.add('argos-module-tabs');
                }
            }
        }, 50);
        </script>
        """,
        unsafe_allow_html=True,
    )

    selected_module = next(
        (m for m in MODULES if m["key"] == st.session_state[MODULE_SELECTION_KEY]),
        MODULES[0],
    )

    st.markdown(
        f"""
        <h3 style="margin-top:0.5rem; color: #1e293b;">{selected_module['title']}</h3>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(selected_module["bullets"])

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# Seção: Contexto Acadêmico & Avisos
# ==========================================================
col_acad, col_aviso = st.columns(2, gap="large")

with col_acad:
    st.markdown(
        """
        <div class="argos-static-card">
            <h3>🎓 Contexto Acadêmico</h3>
            <ul style="padding-left: 1.1rem; margin-bottom: 0; opacity: 0.9; font-size: 0.95rem; line-height: 1.7;">
                <li><b>Programa:</b> Iniciação em Desenvolvimento Tecnológico e Inovação (<b>PIBITI UFPI 2026–2027</b>).</li>
                <li><b>Plano de Trabalho:</b> <i>Análise de Dados para Apoio à Tomada de Decisão em Investimentos no Mercado Financeiro</i>.</li>
                <li><b>Pesquisador (Discente):</b> Clériston de Castro Ramos.</li>
                <li><b>Orientador:</b> Prof. Dr. Arlino Henrique Magalhães de Araújo.</li>
                <li><b>Instituição:</b> Universidade Federal do Piauí (UFPI) — Curso de Tecnologia em Gestão de Dados.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_aviso:
    st.markdown(
        """
        <div class="argos-static-card" style="border-left: 4px solid #f59e0b;">
            <h3>⚠️ Aviso Legal e Metodológico</h3>
            <p style="opacity: 0.9; font-size: 0.95rem; line-height: 1.7; margin-bottom: 0;">
                Esta aplicação possui estrita finalidade educacional, de pesquisa e de desenvolvimento
                tecnológico. Os dados históricos são obtidos via API do Yahoo Finance e processados
                computacionalmente. <b>Resultados passados não garantem rentabilidade ou desempenho
                futuro</b>, e nenhuma das análises expostas configura recomendação, indicação ou
                aconselhamento formal de investimento.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.caption("Argos DataLab · Desenvolvido com Python, Streamlit e Plotly.")