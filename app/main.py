import streamlit as st

st.set_page_config(
    page_title="Argos DataLab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 1. Definição explícita de todas as páginas e títulos do sistema por código
sobre_page = st.Page(
    "views/sobre_projeto.py",
    title="Sobre o Projeto",
    icon="📊",
    default=True,  # Torna esta a primeira página aberta ao acessar a URL
)

analise_page = st.Page(
    "views/analise_individual.py",
    title="Análise Individual",
    icon="📈",
)

comparacao_page = st.Page(
    "views/comparacao_ativos.py",
    title="Comparação de Ativos",
    icon="⚖️",
)

indicadores_page = st.Page(
    "views/indicadores_tecnicos.py",
    title="Indicadores Técnicos",
    icon="📉",
)

risco_page = st.Page(
    "views/risco_retorno.py",
    title="Risco e Retorno",
    icon="⚠️",
)

# 2. Configuração do menu de navegação lateral limpo (sem rastro de 'main')
pg = st.navigation(
    {
        "Menu Principal": [
            sobre_page,
            analise_page,
            comparacao_page,
            indicadores_page,
            risco_page,
        ]
    }
)

# 3. Executa a página selecionada
pg.run()