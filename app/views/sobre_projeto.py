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
# Injeção de CSS Customizado (Forçando Botões Largos)
# ==========================================================
st.markdown(
    """
    <style>
    /* 1. Container das abas: garante que o bloco ocupe 100% da tela */
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 15px !important;
        width: 100% !important;
        display: flex !important;
    }
    
    /* 2. Botões individuais das abas: força a expansão igualitária */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        flex: 1 1 0px !important; 
        background-color: transparent !important;
        border: 1px solid rgba(128, 128, 128, 0.3) !important;
        border-radius: 8px !important;
        height: 55px !important;
        margin: 0 !important;
        justify-content: center !important;
        transition: border-color 0.2s ease-in-out !important;
    }

    /* 3. Oculta os sublinhados nativos do Streamlit que poluem o visual */
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* 4. Hover suave nos botões não selecionados */
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
        border-color: rgba(128, 128, 128, 0.8) !important;
    }

    /* 5. Aba Selecionada (Destaca a borda usando a cor primária do tema) */
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border: 2px solid var(--primary-color) !important; 
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# Cabeçalho Principal
# ==========================================================
st.title('📊 Sobre o Projeto "Argos DataLab"')
st.markdown(
    "<p style='font-size:1.2rem; opacity: 0.8; margin-bottom:1.5rem;'>"
    "Plataforma inteligente de análise exploratória, modelagem de risco e "
    "comparação de ativos para o mercado financeiro.</p>",
    unsafe_allow_html=True,
)

st.info(
    "💡 **Bem-vindo ao Argos!** Utilize o menu lateral esquerdo para navegar entre as "
    "seções da plataforma."
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
        """,
        unsafe_allow_html=True,
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
        """,
        unsafe_allow_html=True,
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
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================================
# Seção: Módulos do Sistema
# ==========================================================
st.header("🛠️ Módulos e Funcionalidades do Sistema")
st.markdown("<p style='opacity: 0.8; font-size: 0.95rem; margin-bottom: 1rem;'>Selecione um módulo abaixo para detalhar suas capacidades operacionais:</p>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Análise Individual", 
    "⚖️ Comparação de Ativos", 
    "📉 Indicadores Técnicos", 
    "⚠️ Risco & Retorno"
])

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Visão Geral e Sazonalidade do Ativo")
    st.markdown(
        """
        - **Seleção Hierárquica:** Escolha de ativos divididos em classes e subclasses organizadas.
        - **Período Inteligente:** Atalhos rápidos de 1, 3, 5, 10 anos ou definição de datas personalizadas.
        - **Gráfico de Volatilidade por Mês:** Acompanhamento do desvio padrão anualizado mês a mês.
        - **Mapa de Calor Sazonal:** Visualização do comportamento estatístico e sazonais de retornos.
        - **Exportação:** Download completo dos dados tratados e limpos em formato CSV.
        """
    )
    st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Comparação Multi-Ativo Avançada")
    st.markdown(
        """
        - **Seleção Flexível:** Filtros combinados por classe e subclasse para até 5 ativos simultâneos.
        - **Evolução Base 100:** Gráfico unificado com normalização de ponto de partida e tooltips monetários.
        - **Matriz de Correlação:** Heatmap triangular exclusivo que evita redundâncias e facilita a leitura de pares.
        - **Resumo Consolidado:** Tabela comparativa interativa destacando melhor retorno, menor drawdown e Sharpe.
        """
    )
    st.markdown("<br>", unsafe_allow_html=True)

with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Análise Técnica Aplicada")
    st.markdown(
        """
        - **Gráficos de Preço e Candles:** Visualização de barras ou linhas de fechamento (com regra de segurança mensal).
        - **Indicadores de Tendência e Momentum:** Médias Móveis (SMA/EMA), Bandas de Bollinger, RSI e MACD.
        - **Controle de Volume:** Acompanhamento integrado da liquidez negociada do ativo.
        """
    )
    st.markdown("<br>", unsafe_allow_html=True)

with tab4:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Gestão e Métricas de Risco")
    st.markdown(
        """
        - **Cards Executivos:** 8 indicadores-chave consolidados (Retorno Total, Médio, Win Rate, Volatilidade e Sharpe).
        - **Drawdown Máximo:** Identificação precisa do impacto e da data da pior queda do período.
        - **Taxa Livre de Risco:** Parâmetro anual configurável pelo usuário para cálculo refinado do Índice de Sharpe.
        - **Distribuição de Retornos:** Gráficos de frequência divididos em faixas percentuais padronizadas.
        """
    )
    st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================================
# Seção: Contexto Acadêmico & Avisos
# ==========================================================
col_acad, col_aviso = st.columns(2, gap="large")

with col_acad:
    st.header("🎓 Contexto Acadêmico")
    st.markdown(
        """
        * **Programa:** Iniciação em Desenvolvimento Tecnológico e Inovação (**PIBITI UFPI 2026–2027**).
        * **Plano de Trabalho:** *Análise de Dados para Apoio à Tomada de Decisão em Investimentos no Mercado Financeiro*.
        * **Pesquisador (Discente):** Clériston de Castro Ramos.
        * **Orientador:** Prof. Dr. Arlino Henrique Magalhães de Araújo.
        * **Instituição:** Universidade Federal do Piauí (UFPI) — Curso de Tecnologia em Gestão de Dados.
        """
    )

with col_aviso:
    st.header("⚠️ Aviso Legal e Metodológico")
    st.markdown(
        """
        > Esta aplicação possui estrita finalidade educacional, de pesquisa e de desenvolvimento tecnológico. 
        > Os dados históricos são obtidos via API do Yahoo Finance e processados computacionalmente. 
        > **Resultados passados não garantem rentabilidade ou desempenho futuro**, e nenhuma das análises 
        > expostas configura recomendação, indicação ou aconselhamento formal de investimento.
        """
    )

st.markdown("---")
st.caption("Argos DataLab · Desenvolvido com Python, Streamlit e Plotly.")