from __future__ import annotations

from collections.abc import Sequence

import streamlit as st

from core.assets import (
    ASSETS,
    get_assets,
)


ASSET_CLASS_STATE_KEY = "selected_asset_class"
ASSET_SUBCATEGORY_STATE_KEY = "selected_asset_subcategory"
ASSET_MARKET_STATE_KEY = "selected_asset_market"
ASSET_TICKER_STATE_KEY = "selected_asset_ticker"


# Mapeamento para nomes mais amigáveis e com ícones no seletor de classes
CLASS_MAPPING = {
    "Criptomoeda": "₿ Criptomoedas",
    "Ação": "🏢 Ações",
    "ETF": "📈 ETFs",
    "REIT": "🏙️ REITs/Imobiliário",
    "FII": "🏠 FIIs",
    "Índice": "📊 Índices de Mercado",
    "Forex": "💱 Forex (Moedas)",
    "Commodity": "🛢️ Commodities",
    "Renda Fixa": "💵 Renda Fixa / Treasuries"
}


def _class_label(asset_class: str) -> str:
    if asset_class == "Todas as Classes":
        return "Todas as Classes"
        
    matching_assets = get_assets(
        asset_class=asset_class,
    )

    count = len(matching_assets)
    # Busca o nome traduzido ou mantém o original se não achar
    name = CLASS_MAPPING.get(asset_class, asset_class)

    return f"{name} ({count})"


def _asset_label(asset: dict[str, str]) -> str:
    icon = asset.get('icon', '')
    icon_str = f"{icon} " if icon else ""
    return (
        f"{icon_str}{asset['ticker']} "
        f"— {asset['name']}"
    )


def _ticker_to_label(ticker: str) -> str:
    """Busca o asset completo pelo ticker e o formata para a label."""
    asset = next((a for a in ASSETS if a["ticker"] == ticker), None)
    if asset:
        return _asset_label(asset)
    return ticker


def inject_compact_css():
    """Injeta CSS para deixar as listas de seleção (dropdowns) mais compactas e profissionais."""
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


def render_asset_selector(
    *,
    key_prefix: str = "asset_selector",
    label_prefix: str = "Selecionar ativo",
    default_ticker: str | None = None,
    include_market: bool = True,
) -> str | None:
    """
    Renderiza o seletor hierárquico único (para as páginas individuais):
    Classe → Subclasse → Mercado → Ativo.
    Retorna o ticker selecionado ou None.
    """
    inject_compact_css()
    
    classes = sorted(
        {
            asset["class"]
            for asset in ASSETS
        }
    )

    if not classes:
        st.error(
            "O catálogo de ativos está vazio."
        )
        return None

    class_key = f"{key_prefix}_class"
    subcategory_key = f"{key_prefix}_subcategory"
    market_key = f"{key_prefix}_market"
    ticker_key = f"{key_prefix}_ticker"

    selected_class = st.selectbox(
        f"{label_prefix} — classe",
        options=classes,
        format_func=_class_label,
        key=class_key,
        width="stretch",
    )

    class_assets = get_assets(
        asset_class=selected_class,
    )

    subcategories = sorted(
        {
            asset["subcategory"]
            for asset in class_assets
        }
    )

    selected_subcategory = st.selectbox(
        f"{label_prefix} — subclasse",
        options=subcategories,
        key=subcategory_key,
        width="stretch",
    )

    subcategory_assets = get_assets(
        asset_class=selected_class,
        subcategory=selected_subcategory,
    )

    if include_market:
        markets = sorted(
            {
                asset["market"]
                for asset in subcategory_assets
            }
        )

        selected_market = st.selectbox(
            f"{label_prefix} — mercado",
            options=markets,
            key=market_key,
            width="stretch",
        )

        selected_assets = get_assets(
            asset_class=selected_class,
            subcategory=selected_subcategory,
            market=selected_market,
        )
    else:
        selected_market = None
        selected_assets = subcategory_assets

    if not selected_assets:
        st.warning(
            "Não há ativos disponíveis para os filtros selecionados."
        )
        return None

    default_index = 0

    if default_ticker:
        matching_indexes = [
            index
            for index, asset in enumerate(selected_assets)
            if asset["ticker"] == default_ticker
        ]

        if matching_indexes:
            default_index = matching_indexes[0]

    selected_asset = st.selectbox(
        f"{label_prefix} — ativo",
        options=selected_assets,
        index=default_index,
        format_func=_asset_label,
        key=ticker_key,
        width="stretch",
    )

    st.caption(
        f"**{selected_asset['ticker']}** · "
        f"{selected_asset['description']}"
    )

    return selected_asset["ticker"]


def render_multi_asset_selector(
    *,
    key_prefix: str = "multi_asset_selector",
    label: str = "Ativos para comparar",
    default_tickers: list[str] | None = None,
    max_selections: int = 5,
) -> list[str]:
    """
    Renderiza um seletor multiselect com filtros hierárquicos Opcionais
    (Classe -> Subclasse) para estreitar as opções na página de Comparação,
    preservando os ativos já selecionados (evita a quebra no Streamlit).
    """
    inject_compact_css()
    
    st.markdown("<p style='font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: 600; color: #475569;'>Filtros de Busca (Opcional)</p>", unsafe_allow_html=True)
    
    classes = sorted({asset["class"] for asset in ASSETS})
    class_options = ["Todas as Classes"] + classes
    
    selected_class = st.selectbox(
        "Filtrar por Classe",
        options=class_options,
        format_func=_class_label,
        key=f"{key_prefix}_class_filter"
    )
    
    if selected_class == "Todas as Classes":
        filtered_assets = ASSETS
    else:
        filtered_assets = get_assets(asset_class=selected_class)
        
        subcategories = sorted({asset["subcategory"] for asset in filtered_assets})
        if len(subcategories) > 1:
            subcat_options = ["Todas as Subclasses"] + subcategories
            selected_subcat = st.selectbox(
                "Filtrar por Subclasse",
                options=subcat_options,
                key=f"{key_prefix}_subcat_filter"
            )
            if selected_subcat != "Todas as Subclasses":
                filtered_assets = get_assets(asset_class=selected_class, subcategory=selected_subcat)
    
    # Recupera seleções ativas para garantir que não sumam do multiselect ao mudar o filtro
    current_selection_tickers = st.session_state.get(f"{key_prefix}_tickers", default_tickers or [])
    
    # Construir as opções finais (apenas Tickers string) para evitar bug de objeto do Streamlit
    options_dict = {a["ticker"]: a for a in filtered_assets}
    
    # Se um ativo estiver selecionado mas não pertencer ao filtro atual, forçamos a inclusão dele 
    # nas opções do multiselect para que o Streamlit não dê erro nem limpe a seleção.
    for ticker in current_selection_tickers:
        if ticker not in options_dict:
            asset_obj = next((a for a in ASSETS if a["ticker"] == ticker), None)
            if asset_obj:
                options_dict[ticker] = asset_obj
                
    final_options = list(options_dict.values())
    final_options.sort(key=lambda x: x["ticker"])
    final_tickers = [a["ticker"] for a in final_options]
    
    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    
    selected_tickers = st.multiselect(
        label,
        options=final_tickers,
        default=current_selection_tickers,
        format_func=_ticker_to_label,
        max_selections=max_selections,
        key=f"{key_prefix}_tickers",
        help="Utilize os filtros acima para facilitar a localização. Você pode comparar ativos de classes diferentes."
    )
    
    if selected_tickers:
        st.caption(f"**Selecionados ({len(selected_tickers)}/{max_selections}):** " + ", ".join(selected_tickers))
        
    return selected_tickers