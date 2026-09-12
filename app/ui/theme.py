import streamlit as st

def apply_fintech_theme():
    st.markdown(
        """
        <style>
        /* ==========================================================
           1. CORREÇÃO DA FAIXA SUPERIOR E FUNDO GLOBAL (Dark Mode)
           ========================================================== */
        .stApp, header[data-testid="stHeader"], [data-testid="stToolbar"] {
            background-color: #090d16 !important;
        }

        .stApp {
            color: #f8fafc;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* ==========================================================
           2. SIDEBAR MODERNA (Contraste de Textos e Ícones)
           ========================================================== */
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {
            color: #94a3b8 !important;
        }

        section[data-testid="stSidebar"] a {
            color: #cbd5e1 !important;
            font-weight: 500;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] span {
            color: #e2e8f0 !important;
        }

        section[data-testid="stSidebar"] [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(2, 132, 199, 0.25) 100%) !important;
            border-left: 4px solid #38bdf8 !important;
        }
        section[data-testid="stSidebar"] [aria-selected="true"] span {
            color: #38bdf8 !important;
            font-weight: 700 !important;
        }

        /* ==========================================================
           3. CARDS COM GLASSMORPHISM E TEXTOS NÍTIDOS
           ========================================================== */
        .fintech-card {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.75) 0%, rgba(15, 23, 42, 0.85) 100%);
            border: 1px solid rgba(56, 189, 248, 0.15);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
            color: #f8fafc !important;
        }
        
        .fintech-card p, .fintech-card li {
            color: #94a3b8 !important;
        }

        /* ==========================================================
           4. TIPOGRAFIA 
           ========================================================== */
        .neon-title {
            background: linear-gradient(135deg, #f8fafc 0%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #f8fafc !important;
        }

        /* ==========================================================
           5. ABAS (TABS) REFINADAS COM ESTILO FINTECH PROFISSIONAL
           ========================================================== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: #0f172a;
            padding: 8px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #1e293b;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            color: #94a3b8;
            font-weight: 600;
            flex: 1;
            justify-content: center;
            height: 48px;
            transition: all 0.2s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #f8fafc;
            background-color: #334155;
            border-color: rgba(56, 189, 248, 0.3);
        }

        /* Aba Selecionada corrigida para um tom sofisticado e limpo */
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
            color: #38bdf8 !important;
            border: 1px solid #38bdf8 !important;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )