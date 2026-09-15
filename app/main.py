import os
import streamlit as st
import streamlit.components.v1 as components

# ==========================================================
# 0. Bloqueio do tradutor via injeção JS no documento pai
# ==========================================================
def bloquear_tradutor_nativo():
    """
    Injeta as tags anti-tradução via JavaScript, atuando diretamente
    no documento do navegador (não no arquivo estático do pacote).
    Funciona em qualquer ambiente de deploy, inclusive com FS somente-leitura.
    """
    components.html(
        """
        <script>
        (function() {
            try {
                var doc = window.parent.document;

                // 1. Ajusta o idioma e o atributo translate na tag <html>
                doc.documentElement.setAttribute('lang', 'pt-BR');
                doc.documentElement.setAttribute('translate', 'no');

                // 2. Injeta a meta tag oficial do Google, se ainda não existir
                if (!doc.querySelector('meta[name="google"]')) {
                    var meta = doc.createElement('meta');
                    meta.name = 'google';
                    meta.content = 'notranslate';
                    doc.head.appendChild(meta);
                }

                // 3. Marca o body como notranslate também (reforço)
                doc.body.classList.add('notranslate');
            } catch (e) {
                // Ignora silenciosamente caso algo bloqueie o acesso ao parent
            }
        })();
        </script>
        """,
        height=0,
        width=0,
    )

# Executa a função imediatamente ao carregar o main.py
bloquear_tradutor_nativo()


# ==========================================================
# 1. Configuração da Página
# ==========================================================
st.set_page_config(
    page_title="Argos DataLab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# 2. Definição Explícita das Páginas
# ==========================================================
home_page = st.Page("views/home.py", title="Início", icon="🏠", default=True)
sobre_page = st.Page("views/sobre_projeto.py", title="Sobre o Projeto", icon="📊")
analise_page = st.Page("views/analise_individual.py", title="Análise Individual", icon="📈")
comparacao_page = st.Page("views/comparacao_ativos.py", title="Comparação de Ativos", icon="⚖️")
indicadores_page = st.Page("views/indicadores_tecnicos.py", title="Indicadores Técnicos", icon="📉")
risco_page = st.Page("views/risco_retorno.py", title="Risco e Retorno", icon="⚠️")


# ==========================================================
# 3. Configuração do Menu de Navegação Nativo
# ==========================================================
pg = st.navigation({
    "Menu Principal": [
        home_page,  
        sobre_page,
        analise_page,
        comparacao_page,
        indicadores_page,
        risco_page,
    ]
})


# ==========================================================
# 4. Injeção Dinâmica de CSS e do Ícone "Home" (Casinha)
# ==========================================================
if pg != home_page:
    st.markdown("""
        <style>
        /* Oculta rigorosamente a primeira opção ("Início") do menu nativo */
        [data-testid="stSidebarNav"] ul li:first-of-type {
            display: none !important;
        }
        
        /* Empurra o menu "Menu Principal" para baixo, abrindo espaço
           para a casinha ficar posicionada acima dele */
        [data-testid="stSidebarNav"] {
            margin-top: 60px !important;
        }
        
        /* POSITION FIXED: posiciona a casinha ABAIXO do botão nativo
           de recolher/expandir o sidebar, alinhada à esquerda, e
           acima do "Menu Principal" */
        .fixed-home-btn {
            position: fixed !important;
            top: 55px !important;
            left: 25px !important;
            font-size: 1.5rem !important;
            text-decoration: none !important;
            z-index: 999999 !important;
            opacity: 0.5;
            transition: opacity 0.2s ease, transform 0.2s ease !important;
        }
        
        .fixed-home-btn:hover {
            opacity: 1;
            transform: scale(1.1) !important;
        }
        </style>
        
        <!-- Link HTML puro da Casinha -->
        <a href="/" target="_self" class="fixed-home-btn" title="Ir para a Home">🏠</a>
    """, unsafe_allow_html=True)


# ==========================================================
# 5. Executa a Página Selecionada
# ==========================================================
pg.run()