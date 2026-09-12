from datetime import datetime

import streamlit as st

from core.assets import ASSETS
from core.config import config


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
    "treasury": "💵 Taxas de Juros / Treasuries",
}


# ==========================================================
# CSS global do sidebar
# ==========================================================
def inject_compact_sidebar_css() -> None:
    """Aplica compactação global aos widgets do sidebar."""
    st.markdown(
        """
        <style>
        /* Selectbox fechado */
        section[data-testid="stSidebar"] [data-baseweb="select"] > div {
            min-height: 34px !important;
            height: 34px !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        /* Popover aberto: o menu pode ser filho do body, portanto não é
           limitado por section[data-testid='stSidebar']. */
        div[data-baseweb="popover"] {
            padding: 0 !important;
            margin: 0 !important;
        }

        div[data-baseweb="popover"] [role="listbox"] {
            padding: 0 !important;
            margin: 0 !important;
            border-spacing: 0 !important;
        }

        div[data-baseweb="popover"] [role="option"] {
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            min-height: 24px !important;
            height: 24px !important;
            max-height: 24px !important;
            padding: 2px 8px !important;
            margin: 0 !important;
            line-height: 1 !important;
            font-size: 0.80rem !important;
        }

        div[data-baseweb="popover"] [role="option"] > *,
        div[data-baseweb="popover"] [role="option"] p,
        div[data-baseweb="popover"] [role="option"] span,
        div[data-baseweb="popover"] [role="option"] div {
            box-sizing: border-box !important;
            min-height: 0 !important;
            height: auto !important;
            max-height: none !important;
            padding: 0 !important;
            margin: 0 !important;
            line-height: 1 !important;
            font-size: 0.80rem !important;
        }

        /* BaseWeb frequentemente adiciona esta camada interna. */
        div[data-baseweb="popover"] [data-baseweb="menu"] {
            padding: 0 !important;
            margin: 0 !important;
        }

        div[data-baseweb="popover"] [data-baseweb="menu"] li,
        div[data-baseweb="popover"] [data-baseweb="menu"] [role="option"] {
            min-height: 24px !important;
            height: 24px !important;
            padding-top: 2px !important;
            padding-bottom: 2px !important;
        }

        /* Labels compactos no sidebar. */
        section[data-testid="stSidebar"] label {
            margin-bottom: 1px !important;
        }

        /* Espaçamento geral entre os widgets. */
        section[data-testid="stSidebar"]
        div[data-testid="stVerticalBlock"] {
            gap: 0.25rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# Controles
# ==========================================================
def render_asset_controls(
    title: str,
    button_label: str,
    button_key: str,
) -> dict:
    """Renderiza os controles compactos da barra lateral."""
    inject_compact_sidebar_css()

    with st.sidebar:
        st.header(title)

        groups = []
        for asset in ASSETS:
            group = asset.get(
                "group",
                asset.get("class", "Outros"),
            )
            if group not in groups:
                groups.append(group)

        if not groups:
            st.error("Nenhuma classe de ativo foi encontrada.")
            return {
                "symbol": None,
                "period": None,
                "start_date": None,
                "end_date": None,
                "frequency": None,
                "submitted": False,
            }

        current_symbol = st.session_state.get(
            "asset_symbol",
            "BTC-USD",
        )

        current_group = groups[0]
        for asset in ASSETS:
            if asset.get("ticker") == current_symbol:
                current_group = asset.get(
                    "group",
                    asset.get("class", "Outros"),
                )
                break

        selected_group = st.selectbox(
            "Classe do Ativo",
            options=groups,
            index=(
                groups.index(current_group)
                if current_group in groups
                else 0
            ),
            format_func=lambda value: GROUP_MAPPING.get(
                str(value).lower(),
                str(value).replace("_", " ").title(),
            ),
            key=f"{button_key}_group_select",
            width="stretch",
        )

        filtered_assets = [
            asset
            for asset in ASSETS
            if asset.get(
                "group",
                asset.get("class", "Outros"),
            ) == selected_group
        ]

        asset_index = 0
        for index, asset in enumerate(filtered_assets):
            if asset.get("ticker") == current_symbol:
                asset_index = index
                break

        selected_asset = st.selectbox(
            "Símbolo do Ativo",
            options=filtered_assets,
            format_func=lambda asset: (
                f"{asset['ticker']} — {asset['name']}"
            ),
            index=asset_index,
            key=f"{button_key}_asset_select",
            width="stretch",
        )

        symbol = (
            selected_asset["ticker"]
            if selected_asset
            else current_symbol
        )

        st.divider()

        period_options = [
            "1 ano",
            "3 anos",
            "5 anos",
            "10 anos",
            "Personalizado",
        ]

        current_period = st.session_state.get(
            "asset_period",
            "5 anos",
        )

        selected_period = st.selectbox(
            "Período",
            options=period_options,
            index=(
                period_options.index(current_period)
                if current_period in period_options
                else 2
            ),
            key=f"{button_key}_period_select",
            width="stretch",
        )

        today = datetime.now().date()

        if selected_period == "Personalizado":
            start_date = st.date_input(
                "Data inicial",
                value=st.session_state.get(
                    "asset_start_date",
                    today.replace(year=today.year - 5),
                ),
                key=f"{button_key}_start_date",
            )

            end_date = st.date_input(
                "Data final",
                value=st.session_state.get(
                    "asset_end_date",
                    today,
                ),
                key=f"{button_key}_end_date",
            )
        else:
            end_date = today
            years_to_subtract = int(selected_period.split()[0])
            target_year = today.year - years_to_subtract
            target_month = today.month + 1

            if target_month > 12:
                target_month = 1
                target_year += 1

            start_date = datetime(
                target_year,
                target_month,
                1,
            ).date()

        frequency_options = getattr(
            config,
            "FREQUENCIES",
            ["Diário", "Semanal", "Mensal"],
        )

        current_frequency = st.session_state.get(
            "asset_frequency",
            "Mensal",
        )

        frequency = st.selectbox(
            "Frequência",
            options=frequency_options,
            index=(
                frequency_options.index(current_frequency)
                if current_frequency in frequency_options
                else 0
            ),
            key=f"{button_key}_frequency_select",
            width="stretch",
        )

        submitted = st.button(
            button_label,
            key=button_key,
            type="primary",
            width="stretch",
        )

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
