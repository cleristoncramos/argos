from datetime import datetime
import streamlit as st

# Importa o catálogo construído
from core.assets import ASSETS
from core.config import config


# Dicionário robusto abrangendo as 13 classes exatas do seu catálogo de ativos
GROUP_MAPPING = {
    "crypto": "₿ Criptomoedas",
    "br_stocks": "🇧🇷 Ações Brasil",
    "us_stocks": "🇺🇸 Ações EUA",
    "europe_stocks": "🇪🇺 Ações Europa",
    "asia_stocks": "🌏 Ações Ásia",
    "equity_etfs": "📈 ETFs de Ações",
    "fixed_income_etfs": "💵 ETFs de Renda Fixa",
    "reits": "🏢 REITs / Mercado Imobiliário",
    "brazil_fiis": "🏠 FIIs Brasil",
    "fiis": "🏠 FIIs Brasil",
    "indexes": "📊 Índices de Mercado",
    "indices": "📊 Índices de Mercado",
    "forex": "💱 Forex (Moedas)",
    "commodities": "🛢️ Commodities",
    "rates": "💵 Taxas de Juros / Treasuries",
    "treasury": "💵 Taxas de Juros / Treasuries"
}


def render_asset_controls(title: str, button_label: str, button_key: str) -> dict:
    """
    Renderiza os controles padrão da barra lateral com seleção hierárquica e período inteligente.
    """
    
    st.markdown(
        """
        <style>
        /* Reduz o padding e a altura mínima das opções dentro das listas de seleção */
        ul[role="listbox"] li[role="option"] {
            padding-top: 4px !important;
            padding-bottom: 4px !important;
            min-height: 32px !important;
            font-size: 0.9rem !important;
        }
        /* Ajusta o espaçamento interno do container da lista para ficar mais denso */
        ul[role="listbox"] {
            padding-top: 4px !important;
            padding-bottom: 4px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.header(title)

        # 1. Obter a lista de classes/grupos únicos preservando a ordem original
        grupos_unicos = []
        for asset in ASSETS:
            grupo = asset.get("group", asset.get("class", "Outros"))
            if grupo not in grupos_unicos:
                grupos_unicos.append(grupo)

        # 2. Identificar a qual grupo o ativo atual pertence para inicializar os seletores
        current_symbol = st.session_state.get("asset_symbol", "BTC-USD")
        current_group = grupos_unicos[0]
        for asset in ASSETS:
            if asset["ticker"] == current_symbol:
                current_group = asset.get("group", asset.get("class", "Outros"))
                break

        # 3. Selectbox Hierárquico: Classe de Ativos
        grupo_selecionado = st.selectbox(
            "Classe do Ativo",
            options=grupos_unicos,
            index=grupos_unicos.index(current_group) if current_group in grupos_unicos else 0,
            format_func=lambda g: GROUP_MAPPING.get(str(g).lower(), str(g).replace("_", " ").title()),
            key=f"{button_key}_group_select"
        )

        # 4. Filtrar a lista de ativos com base na classe selecionada
        ativos_filtrados = [
            a for a in ASSETS 
            if a.get("group", a.get("class", "Outros")) == grupo_selecionado
        ]

        asset_index = 0
        for i, a in enumerate(ativos_filtrados):
            if a["ticker"] == current_symbol:
                asset_index = i
                break

        # 5. Selectbox Hierárquico: Ativo Específico
        ativo_selecionado = st.selectbox(
            "Símbolo do Ativo",
            options=ativos_filtrados,
            format_func=lambda x: f"{x['ticker']} — {x['name']}",
            index=asset_index,
            key=f"{button_key}_asset_select"
        )

        symbol = ativo_selecionado["ticker"] if ativo_selecionado else current_symbol

        st.divider()

        # ==========================================
        # Seleção de Período Inteligente
        # ==========================================
        period_options = ["1 ano", "3 anos", "5 anos", "10 anos", "Personalizado"]
        current_period = st.session_state.get("asset_period", "5 anos")
        
        selected_period = st.selectbox(
            "Período",
            options=period_options,
            index=period_options.index(current_period) if current_period in period_options else 2,
            key=f"{button_key}_period_select"
        )
        
        today = datetime.now().date()
        
        if selected_period == "Personalizado":
            start_date = st.date_input(
                "Data inicial",
                value=st.session_state.get("asset_start_date", today.replace(year=today.year - 5)),
            )
            end_date = st.date_input(
                "Data final",
                value=st.session_state.get("asset_end_date", today),
            )
        else:
            end_date = today
            years_to_subtract = int(selected_period.split()[0])
            
            # Regra: Pula o mês atual do passado e começa no dia 1º do mês seguinte
            # Ex: Hoje = 11/09/2026. 1 ano atrás = 11/09/2025. Data inicial = 01/10/2025.
            target_year = today.year - years_to_subtract
            target_month = today.month + 1
            
            if target_month > 12:
                target_month = 1
                target_year += 1
                
            start_date = datetime(target_year, target_month, 1).date()

        freq_options = getattr(config, "FREQUENCIES", ["Diário", "Semanal", "Mensal"])
        current_freq = st.session_state.get("asset_frequency", "Mensal")

        frequency = st.selectbox(
            "Frequência",
            options=freq_options,
            index=freq_options.index(current_freq) if current_freq in freq_options else 0,
        )

        submitted = st.button(button_label, key=button_key, type="primary", use_container_width=True)

        if submitted:
            st.session_state["asset_symbol"] = symbol
            st.session_state["asset_period"] = selected_period
            st.session_state["asset_start_date"] = start_date
            st.session_state["asset_end_date"] = end_date
            st.session_state["asset_frequency"] = frequency

        return {
            "symbol": symbol,
            "period": selected_period,
            "start_date": start_date,
            "end_date": end_date,
            "frequency": frequency,
            "submitted": submitted,
        }