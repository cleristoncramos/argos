"""
Componente de UI para exibir cards com logo/ícone, ticker e nome
dos ativos atualmente selecionados -- inspirado em layouts de
rankings de ativos com ícone + nome + valor lado a lado.
"""

from html import escape

import streamlit as st

from core.asset_logos import get_asset_logo_url


def _logo_html(asset: dict, size: int, fallback_font: str) -> str:
    """Logo do ativo (ou emoji de reserva, se não houver logo ou ele falhar)."""
    ticker = asset.get("ticker", "")
    group = asset.get("group", asset.get("class", ""))
    logo_url = get_asset_logo_url(ticker, group)
    fallback_icon = asset.get("icon", "📊")

    if not logo_url:
        return f"<span style='font-size:{fallback_font};'>{fallback_icon}</span>"
    return (
        f"<img src='{escape(logo_url)}' "
        f"style='width:{size}px;height:{size}px;flex:none;object-fit:contain;"
        "background:#fff;border:1px solid #E2E8F0;' "
        "onerror=\"this.style.display='none'; "
        "this.nextElementSibling.style.display='inline';\"/>"
        f"<span style='font-size:{fallback_font}; display:none;'>{fallback_icon}</span>"
    )


def build_asset_card_html(asset: dict, *, hero: bool = False) -> str:
    """
    HTML do cartão de um ativo. `hero=True` é a versão grande das páginas de
    ativo único, que ocupa toda a altura da coluna (para acompanhar o
    resumo ao lado); a versão compacta é a da fileira da Comparação.
    """
    ticker = escape(str(asset.get("ticker", "")))
    name = escape(str(asset.get("name", asset.get("ticker", ""))))

    if hero:
        logo = _logo_html(asset, 64, "2.6rem")
        box = "gap:16px; padding:16px 20px; height:100%; min-height:120px;"
        ticker_style = "font-weight:800; font-size:1.3rem;"
        name_style = "font-size:0.95rem;"
    else:
        logo = _logo_html(asset, 52, "2.2rem")
        box = "gap:16px; padding:18px 20px; height:100%; min-height:104px;"
        ticker_style = "font-weight:750; font-size:1.1rem;"
        name_style = "font-size:0.86rem;"

    return f"""
    <div class="asset-card" style="display:flex; align-items:center; {box} background:#FFFFFF;
                border:1px solid #2A2A2A; box-shadow:0 8px 22px rgba(17,17,17,.07); box-sizing:border-box;">
        {logo}
        <div style="display:flex; flex-direction:column; line-height:1.3; overflow:hidden;">
            <span style="{ticker_style} color:#0f172a;
                         white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                {ticker}
            </span>
            <span style="{name_style} color:#64748b;
                         white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                {name}
            </span>
        </div>
    </div>
    """


def render_selected_asset_cards(assets: list[dict]) -> None:
    """
    Renderiza uma fileira de cards, um por ativo selecionado, cada um
    com logo (ou emoji de fallback), ticker e nome.

    `assets` deve ser uma lista de dicionários no mesmo formato usado
    em ASSETS (precisa ao menos de "ticker"; "name", "group"/"class"
    e "icon" são usados quando disponíveis).
    """
    if not assets:
        return

    for column, asset in zip(st.columns(len(assets)), assets):
        with column:
            st.markdown(build_asset_card_html(asset), unsafe_allow_html=True)


def render_asset_hero_logo(asset: dict) -> None:
    """
    Renderiza APENAS o bloco visual (logo grande + ticker + nome) de um
    único ativo, em destaque, sem envolver em st.columns -- para que o
    chamador possa posicioná-lo lado a lado com outro conteúdo (ex: o
    resumo de disponibilidade) dentro da mesma fileira.
    """
    if not asset:
        return
    st.markdown(build_asset_card_html(asset, hero=True), unsafe_allow_html=True)
