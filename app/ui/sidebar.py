from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

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
# CSS global do sidebar (Compactação + Correção de Overflow)
# ==========================================================
def inject_compact_sidebar_css() -> None:
    """Aplica compactação global aos widgets do sidebar."""
    st.markdown(
        """
        <style>
        /* 1. Selectbox Fechado: Mantém a caixa principal compacta */
        section[data-testid="stSidebar"] [data-baseweb="select"] > div {
            min-height: 34px !important;
            height: 34px !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        /* 2. Textos do Dropdown Aberto: Compactados para 24px */
        div[role="option"][data-rac] {
            height: 24px !important;
            min-height: 24px !important;
            max-height: 24px !important;
            padding: 2px 8px !important;
            margin: 0px !important;
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            line-height: 1.2 !important;
        }

        div[role="option"][data-rac] div[data-item-hl] {
            height: auto !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            line-height: 1.2 !important;
            font-size: 0.80rem !important;
        }

        /* 3. A MÁGICA: Força o Popover a ser menor para acionar o scroll */
        div[data-baseweb="popover"] div[role="listbox"] {
            max-height: 240px !important;
            overflow-y: auto !important;
        }

        /* 4. Labels e Espaçamento: Mais discretos */
        section[data-testid="stSidebar"] label {
            margin-bottom: 1px !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
            gap: 0.25rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# Script de compactação da lista virtualizada (React Aria)
# ==========================================================
def inject_compact_dropdown_script() -> None:
    """
    Corrige apenas o posicionamento (top/height) de cada opção já montada,
    SEM alterar a altura do container de rolagem interno ("sizer").

    IMPORTANTE: versões anteriores deste script sobrescreviam a altura do
    sizer para (totalCount * ROW_HEIGHT). Isso quebrava a rolagem: o
    virtualizador (react-window/BaseWeb) calcula internamente, em JS,
    quando montar cada item com base na altura ORIGINAL das linhas
    (maior que os 24px usados na compactação). Ao forçar uma área de
    rolagem física menor que a esperada pelo virtualizador, a última
    opção (ex: "Taxas de Juros / Treasuries", item 13 de 13) nunca
    chegava a ser montada -- não importa o quanto o usuário rolasse.

    Por isso NÃO tocamos mais na altura do sizer: deixamos o
    virtualizador gerenciar sua própria área de rolagem (pode sobrar um
    espaço em branco no fim da lista -- efeito colateral cosmético menor,
    aceitável em troca de a rolagem voltar a funcionar de verdade).
    """
    components.html(
        """
        <script>
        (function () {
            const parentWindow = window.parent;
            const doc = parentWindow.document;

            if (parentWindow.__compactListboxObserver) {
                parentWindow.__compactListboxObserver.disconnect();
            }

            const ROW_HEIGHT = 24;

            function compactarListbox(listbox) {
                const scrollBody = listbox.querySelector(":scope > div");
                if (!scrollBody) {
                    return;
                }

                const wrappers = scrollBody.querySelectorAll(
                    ':scope > div[style*="position: absolute"]'
                );

                if (wrappers.length === 0) {
                    return;
                }

                let totalCount = null;

                wrappers.forEach((wrapper) => {
                    const opt = wrapper.querySelector('[role="option"]');
                    if (!opt) return;

                    const posText = opt.getAttribute("aria-posinset");
                    if (posText) {
                        const pos = parseInt(posText, 10);
                        if (!isNaN(pos)) {
                            wrapper.style.setProperty(
                                "top",
                                ((pos - 1) * ROW_HEIGHT) + "px",
                                "important"
                            );
                        }
                    }

                    wrapper.style.setProperty(
                        "height",
                        ROW_HEIGHT + "px",
                        "important"
                    );

                    const setsize = opt.getAttribute("aria-setsize");
                    if (setsize) {
                        totalCount = parseInt(setsize, 10);
                    }
                });

                // Diagnóstico: avisa no console se ainda faltar montar
                // alguma linha (não deve mais acontecer após esta correção,
                // já que paramos de estrangular a área de rolagem real).
                if (totalCount && wrappers.length < totalCount) {
                    console.warn(
                        "[compactarListbox] Só " + wrappers.length +
                        " de " + totalCount + " opções foram montadas no DOM."
                    );
                }

                // NÃO sobrescrevemos mais scrollBody.style.height aqui.
            }

            const observer = new MutationObserver(() => {
                doc.querySelectorAll('div[role="listbox"]').forEach(
                    compactarListbox
                );
            });

            parentWindow.__compactListboxObserver = observer;
            observer.observe(doc.body, { childList: true, subtree: true });
        })();
        </script>
        """,
        height=0,
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
    inject_compact_dropdown_script()

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
            "Símbolo/Nome do Ativo",
            options=filtered_assets,
            format_func=lambda asset: (
                f"{asset['ticker']} — {asset.get('description', asset.get('descricao', asset.get('name')))}"
                if asset.get("group", asset.get("class", "")) == "forex"
                else f"{asset['ticker']} — {asset.get('name')}"
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