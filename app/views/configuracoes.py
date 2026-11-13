"""
Configurações (etapa 4 da DL2, 13/11/2026).

B1: referência de comparação padrão (a sugestão automática continua sendo o padrão).
B2: catálogo de ativos. Fixo e somente leitura na versão pública; editável só numa
instalação local com ARGOS_CATALOGO_EDITAVEL=on (DL2-E). A lógica fica em
core/local_catalog.py e app/ui/catalog_state.py.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import streamlit as st

from app.ui.catalog_state import (
    active_catalog,
    group_label,
    local_catalog,
    preferred_reference,
    set_preferred_reference,
)
from app.ui.sidebar import fetch_recent
from core.assets import ASSET_GROUPS, CATALOG_SIZE, CATEGORY_METADATA
from core.benchmark import BENCHMARKS, reference_name
from core.local_catalog import ENV_VAR, CatalogError
from core.ticker_input import validate_ticker

st.set_page_config(page_title="Argos", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    '<header class="pg-head">'
    '<div class="pg-kicker">Preferências da plataforma</div>'
    '<h1 class="pg-title">Configurações</h1>'
    '<p class="pg-sub">Referência de comparação padrão e catálogo de ativos.</p>'
    "</header>",
    unsafe_allow_html=True,
)

catalog = active_catalog()
local = local_catalog()
FLASH_KEY = "config_catalogo_mensagem"

# ==========================================================
# B1: referência de comparação padrão
# ==========================================================
st.markdown("### Referência de comparação padrão")
st.markdown(
    "Na Análise Individual, a trajetória do ativo pode ser vista ao lado de uma referência "
    "de mercado, as duas começando em 100. Por padrão, o Argos **sugere a referência pela "
    "classe do ativo** (por exemplo, Ibovespa para ações brasileiras). Aqui você pode fixar "
    "outra referência para todas as análises. Ela é só um ponto de comparação, não uma meta."
)

AUTOMATIC = "__automatica__"
TYPED = "__digitada__"
current = preferred_reference()
fixed = list(BENCHMARKS)
others = sorted(
    (a["ticker"] for a in catalog if a["ticker"] not in BENCHMARKS),
    key=lambda t: reference_name(t, catalog).lower(),
)
options = [AUTOMATIC, *fixed, *others, TYPED]
if current and current not in options:
    options.insert(-1, current)


def option_label(value: str) -> str:
    if value == AUTOMATIC:
        return "Automática, pela classe do ativo (recomendado)"
    if value == TYPED:
        return "Digitar outro ticker…"
    return f"{reference_name(value, catalog)} ({value})"


choice = st.selectbox(
    "Referência padrão",
    options,
    index=options.index(current) if current in options else 0,
    format_func=option_label,
    key="config_referencia",
)
typed = ""
if choice == TYPED:
    typed = st.text_input("Ticker da referência (código do Yahoo Finance)", placeholder="Ex.: ^STOXX50E, EWW")

if st.button("Salvar referência", type="primary"):
    if choice == AUTOMATIC:
        set_preferred_reference(None)
        st.success("Referência padrão: automática, pela classe do ativo.")
    elif choice == TYPED:
        with st.spinner("Verificando ticker..."):
            result = validate_ticker(typed, fetch_recent)
        if result.ok:
            set_preferred_reference(result.ticker)
            st.success(f"Referência padrão: {result.ticker}.")
        else:
            st.error(result.message)
    else:
        set_preferred_reference(choice)
        st.success(f"Referência padrão: {option_label(choice)}.")

saved = preferred_reference()
st.caption(
    ("Em uso: " + (option_label(saved) if saved else "automática, pela classe do ativo") + ". ")
    + ("Fica salva nesta instalação." if local else "Vale até você fechar o navegador.")
    + " Quando o ativo analisado é a própria referência, o Argos volta à sugestão automática."
)

st.divider()

# ==========================================================
# B2: catálogo de ativos
# ==========================================================
st.markdown("### Catálogo de ativos")

groups = [g["key"] for g in ASSET_GROUPS] + ([g["key"] for g in local.groups()] if local else [])
summary = pd.DataFrame(
    [
        {
            "Grupo": group_label(key),
            "Ativos": sum(1 for a in catalog if a["group"] == key),
            "Seus ativos": sum(1 for a in catalog if a["group"] == key and a.get("local")),
        }
        for key in groups
    ]
)
if not local:
    summary = summary.drop(columns="Seus ativos")

if not local:
    st.info(
        f"Nesta versão, o catálogo é **fixo e somente leitura**: são {CATALOG_SIZE} ativos em "
        f"{len(ASSET_GROUPS)} grupos. A edição do catálogo só existe numa instalação local do "
        "Argos. Ativos fora do catálogo podem ser analisados pela opção \"Digitar ticker\" da "
        "barra lateral.",
        icon="🔒",
    )
    st.dataframe(summary, hide_index=True, use_container_width=True)
    st.caption(
        f"Para editar numa instalação local, inicie o Argos com a variável de ambiente "
        f"{ENV_VAR}=on. As alterações ficam num arquivo SQLite da própria instalação."
    )
    st.stop()

st.markdown(
    f"O catálogo base, com {CATALOG_SIZE} ativos, não muda. Por cima dele, esta instalação "
    "guarda os grupos e ativos que você acrescentar. Eles aparecem na escolha de ativos da "
    "barra lateral e da Comparação de Ativos, com ⭐ nos grupos novos. O Panorama do Catálogo "
    "continua mostrando só o catálogo base."
)
st.dataframe(summary, hide_index=True, use_container_width=True)

# Mensagem da última alteração, mostrada depois de recarregar a página com o catálogo novo.
if FLASH_KEY in st.session_state:
    st.success(st.session_state.pop(FLASH_KEY))

col_asset, col_group = st.columns(2, gap="large")

with col_asset:
    st.markdown("#### Acrescentar ativo")
    with st.form("form_ativo_local", clear_on_submit=True):
        ticker = st.text_input("Ticker (código do Yahoo Finance)", placeholder="Ex.: AMD, EMBR3.SA")
        name = st.text_input("Nome (opcional)", placeholder="Ex.: Embraer")
        group = st.selectbox("Grupo", groups, format_func=group_label)
        if st.form_submit_button("Acrescentar", type="primary", use_container_width=True):
            try:
                with st.spinner("Verificando ticker na fonte..."):
                    added = local.add_asset(ticker, name, group, fetch_recent)
            except CatalogError as error:
                st.error(str(error))
            else:
                st.session_state[FLASH_KEY] = f"{added} acrescentado a {group_label(group)}."
                st.rerun()

with col_group:
    st.markdown("#### Criar grupo")
    with st.form("form_grupo_local", clear_on_submit=True):
        label = st.text_input("Nome do grupo", max_chars=40, placeholder="Ex.: Tecnologia")
        asset_class = st.selectbox("Classe dos ativos", list(CATEGORY_METADATA))
        if st.form_submit_button("Criar grupo", use_container_width=True):
            try:
                local.add_group(label, asset_class)
            except CatalogError as error:
                st.error(str(error))
            else:
                st.session_state[FLASH_KEY] = f"Grupo \"{label.strip()}\" criado."
                st.rerun()

mine = local.assets()
if mine:
    st.markdown("#### Seus ativos")
    for item in mine:
        col_info, col_remove = st.columns([4, 1], vertical_alignment="center")
        col_info.markdown(f"**{item['name']}** ({item['ticker']}) · {group_label(item['group'])}")
        if col_remove.button("Remover", key=f"remover_{item['ticker']}", use_container_width=True):
            local.remove_asset(item["ticker"])
            st.rerun()

empty_groups = [g for g in local.groups() if not any(a["group"] == g["key"] for a in mine)]
if empty_groups:
    st.markdown("#### Grupos vazios")
    for g in empty_groups:
        col_info, col_remove = st.columns([4, 1], vertical_alignment="center")
        col_info.markdown(f"{g['label']} · {g['class']}")
        if col_remove.button("Remover grupo", key=f"remover_grupo_{g['key']}", use_container_width=True):
            local.remove_group(g["key"])
            st.rerun()
