import os
import sys
from datetime import date, datetime

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../..",
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT,
    )

import streamlit as st

from app.ui.data_cache import download_active_data
from app.ui.data_info import DATA_SOURCE, render_catalog_notice
from app.ui.disclaimers import render_footer_disclaimer
from app.ui.page_header import render_page_header
from app.ui.panorama_table import (
    FORMATTERS,
    HEADER_LABELS,
    PANORAMA_NOTES,
    PANORAMA_NOTICE,
    RATE_NOTE,
    SORT_OPTIONS,
    build_panorama_display,
    has_rates,
    unavailable_assets,
)
from app.ui.sidebar import GROUP_MAPPING
from app.ui.tables import render_table
from core.assets import ASSET_GROUPS, ASSETS
from core.data_processor import prepare_dataframe
from core.demo_mode import catalog_assets
from core.panorama import build_panorama, panorama_period, sort_panorama
from core.periods import period_start_date

# Limite de ativos por consulta: o maior grupo do catálogo tem 22.
MAX_ASSETS_PER_QUERY = 25
PANORAMA_PERIODS = ["1 ano", "3 anos", "5 anos"]


st.set_page_config(
    page_title="Argos",
    page_icon="📈",
    layout="wide",
)

render_page_header(
    "views/panorama_catalogo.py",
    "Visão descritiva de todos os ativos de um grupo no mesmo período: variação, "
    "volatilidade e queda máxima lado a lado.",
)

st.info(PANORAMA_NOTICE, icon="ℹ️")


# ==========================================================
# Controles
# ==========================================================
catalog = catalog_assets(ASSETS)
groups = [g["key"] for g in ASSET_GROUPS if any(a["group"] == g["key"] for a in catalog)]

with st.sidebar:
    st.header("Parâmetros do Panorama")
    group = st.selectbox(
        "Grupo de ativos",
        groups,
        format_func=lambda key: GROUP_MAPPING.get(key, key),
        key="panorama_group",
    )
    period = st.selectbox("Período", PANORAMA_PERIODS, index=2, key="panorama_period")
    load = st.button("Gerar panorama", type="primary", use_container_width=True)
    st.caption(
        "Os dados de cada ativo do grupo são consultados um a um e guardados por "
        "1 hora; a primeira consulta de um grupo pode levar alguns segundos."
    )


# ==========================================================
# Consulta (só ao clicar, um grupo por vez)
# ==========================================================
if load:
    today = date.today()
    start = period_start_date(period, today)
    assets = [a for a in catalog if a["group"] == group][:MAX_ASSETS_PER_QUERY]
    data = {}
    progress = st.progress(0.0, text="Consultando os ativos do grupo...")
    for position, asset in enumerate(assets, 1):
        try:
            raw = download_active_data(
                symbol=asset["ticker"],
                start_date=start.strftime("%Y-%m-%d"),
                end_date=today.strftime("%Y-%m-%d"),
                interval="1d",
            )
            data[asset["ticker"]] = prepare_dataframe(raw) if raw is not None and not raw.empty else None
        except Exception:
            data[asset["ticker"]] = None
        progress.progress(position / len(assets), text=f"Consultando {asset['ticker']} ({position}/{len(assets)})")
    progress.empty()

    st.session_state["panorama_table"] = build_panorama(data, assets, start)
    st.session_state["panorama_query"] = {"group": group, "period": period, "start": start}
    st.session_state["panorama_fetched_at"] = datetime.now()

query = st.session_state.get("panorama_query")
table = st.session_state.get("panorama_table")

if query is None or table is None:
    st.info(
        "Escolha um grupo e o período na barra lateral e clique em **Gerar panorama**. "
        "O panorama é montado um grupo por vez."
    )
    st.stop()


# ==========================================================
# Tabela
# ==========================================================
group_label = GROUP_MAPPING.get(query["group"], query["group"])
st.markdown(f"### {group_label} · {query['period']}")

span = panorama_period(table)
fetched_at = st.session_state.get("panorama_fetched_at")
consulted = fetched_at.strftime("%d/%m/%Y às %H:%M") if fetched_at else "—"
if span:
    st.caption(
        f"Período pedido a partir de {query['start']:%d/%m/%Y}; dados de "
        f"{span[0]:%d/%m/%Y} a {span[1]:%d/%m/%Y}, fechamentos diários. "
        f"Fonte: {DATA_SOURCE} · Consulta em {consulted}."
    )

col_sort, col_order = st.columns([2, 1])
with col_sort:
    sort_label = st.selectbox("Ordenar por", list(SORT_OPTIONS), index=0, key="panorama_sort")
with col_order:
    descending = st.radio(
        "Ordem", ["Crescente", "Decrescente"], horizontal=True, key="panorama_order",
    ) == "Decrescente"

ordered = sort_panorama(table, SORT_OPTIONS[sort_label], descending=descending)
render_table(
    build_panorama_display(ordered),
    list(HEADER_LABELS),
    FORMATTERS,
    header_labels=HEADER_LABELS,
    max_height=None,
    min_width=820,
    wrap_header=True,
)
st.caption(PANORAMA_NOTES)

if has_rates(table):
    st.caption(f"ℹ️ {RATE_NOTE}")

missing = unavailable_assets(table)
if missing:
    st.warning(
        "Sem dados nesta consulta: " + ", ".join(missing) + ". As métricas desses "
        "ativos ficam vazias (não são tratadas como zero). Tente novamente em instantes.",
    )

alerted = table[(table["Alertas"].fillna(0) > 0)]
if not alerted.empty:
    st.caption(
        "Ativos com alertas de qualidade dos dados ("
        + ", ".join(alerted["Ticker"])
        + "): veja os detalhes na Análise Individual do ativo antes de interpretar."
    )

render_catalog_notice()
render_footer_disclaimer()
