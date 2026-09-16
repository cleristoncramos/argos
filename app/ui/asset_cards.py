"""
Componente de UI para exibir cards com logo/ícone, ticker e nome
dos ativos atualmente selecionados -- inspirado em layouts de
rankings de ativos com ícone + nome + valor lado a lado.
"""

from html import escape

import streamlit as st

from core.asset_logos import get_asset_logo_url


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

    columns = st.columns(len(assets))

    for column, asset in zip(columns, assets):
        ticker = asset.get("ticker", "")
        name = asset.get("name", ticker)
        group = asset.get("group", asset.get("class", ""))
        logo_url = get_asset_logo_url(ticker, group)
        fallback_icon = asset.get("icon", "📊")

        safe_ticker = escape(str(ticker))
        safe_name = escape(str(name))

        if logo_url:
            image_html = (
                f"<img src='{escape(logo_url)}' "
                "style='width:32px;height:32px;border-radius:50%;object-fit:contain;"
                "background:#fff;border:1px solid #E2E8F0;' "
                "onerror=\"this.style.display='none'; "
                "this.nextElementSibling.style.display='inline';\"/>"
                f"<span style='font-size:1.4rem; display:none;'>{fallback_icon}</span>"
            )
        else:
            image_html = f"<span style='font-size:1.4rem;'>{fallback_icon}</span>"

        card_html = f"""
        <div style="display:flex; align-items:center; gap:10px; background:#F8FAFC;
                    border:1px solid #E2E8F0; border-radius:12px; padding:10px 14px;
                    height:100%;">
            {image_html}
            <div style="display:flex; flex-direction:column; line-height:1.25; overflow:hidden;">
                <span style="font-weight:700; font-size:0.85rem; color:#0f172a;
                             white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    {safe_ticker}
                </span>
                <span style="font-size:0.75rem; color:#64748b;
                             white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    {safe_name}
                </span>
            </div>
        </div>
        """

        with column:
            st.markdown(card_html, unsafe_allow_html=True)


"""
Componente de UI para exibir cards com logo/ícone, ticker e nome
dos ativos atualmente selecionados -- inspirado em layouts de
rankings de ativos com ícone + nome + valor lado a lado.
"""

from html import escape

import streamlit as st

from core.asset_logos import get_asset_logo_url


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

    columns = st.columns(len(assets))

    for column, asset in zip(columns, assets):
        ticker = asset.get("ticker", "")
        name = asset.get("name", ticker)
        group = asset.get("group", asset.get("class", ""))
        logo_url = get_asset_logo_url(ticker, group)
        fallback_icon = asset.get("icon", "📊")

        safe_ticker = escape(str(ticker))
        safe_name = escape(str(name))

        if logo_url:
            image_html = (
                f"<img src='{escape(logo_url)}' "
                "style='width:32px;height:32px;border-radius:50%;object-fit:contain;"
                "background:#fff;border:1px solid #E2E8F0;' "
                "onerror=\"this.style.display='none'; "
                "this.nextElementSibling.style.display='inline';\"/>"
                f"<span style='font-size:1.4rem; display:none;'>{fallback_icon}</span>"
            )
        else:
            image_html = f"<span style='font-size:1.4rem;'>{fallback_icon}</span>"

        card_html = f"""
        <div style="display:flex; align-items:center; gap:10px; background:#F8FAFC;
                    border:1px solid #E2E8F0; border-radius:12px; padding:10px 14px;
                    height:100%;">
            {image_html}
            <div style="display:flex; flex-direction:column; line-height:1.25; overflow:hidden;">
                <span style="font-weight:700; font-size:0.85rem; color:#0f172a;
                             white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    {safe_ticker}
                </span>
                <span style="font-size:0.75rem; color:#64748b;
                             white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    {safe_name}
                </span>
            </div>
        </div>
        """

        with column:
            st.markdown(card_html, unsafe_allow_html=True)


def render_asset_hero_logo(asset: dict) -> None:
    """
    Renderiza APENAS o bloco visual (logo grande + ticker + nome) de um
    único ativo, em destaque, sem envolver em st.columns -- para que o
    chamador possa posicioná-lo lado a lado com outro conteúdo (ex: o
    expander de detalhes da análise) dentro da mesma fileira.

    Usado em páginas de ativo único (ex: Análise Individual), onde o
    logo precisa de mais destaque do que nos cards compactos usados em
    telas de comparação de múltiplos ativos.
    """
    if not asset:
        return

    ticker = asset.get("ticker", "")
    name = asset.get("name", ticker)
    group = asset.get("group", asset.get("class", ""))
    logo_url = get_asset_logo_url(ticker, group)
    fallback_icon = asset.get("icon", "📊")

    safe_ticker = escape(str(ticker))
    safe_name = escape(str(name))

    if logo_url:
        image_html = (
            f"<img src='{escape(logo_url)}' "
            "style='width:64px;height:64px;border-radius:50%;object-fit:contain;"
            "background:#fff;border:1px solid #E2E8F0;' "
            "onerror=\"this.style.display='none'; "
            "this.nextElementSibling.style.display='inline';\"/>"
            f"<span style='font-size:2.6rem; display:none;'>{fallback_icon}</span>"
        )
    else:
        image_html = f"<span style='font-size:2.6rem;'>{fallback_icon}</span>"

    card_html = f"""
    <div style="display:flex; align-items:center; gap:16px; background:#F8FAFC;
                border:1px solid #E2E8F0; border-radius:14px; padding:16px 20px;
                height:100%;">
        {image_html}
        <div style="display:flex; flex-direction:column; line-height:1.3; overflow:hidden;">
            <span style="font-weight:800; font-size:1.3rem; color:#0f172a;
                         white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                {safe_ticker}
            </span>
            <span style="font-size:0.95rem; color:#64748b;
                         white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                {safe_name}
            </span>
        </div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)