"""
Catálogo em uso e preferências da página Configurações (etapa 4 da DL2).

Junta o catálogo base com a camada local (core/local_catalog.py) quando a edição
está ligada, e guarda a referência padrão (B1): na sessão do navegador e, na
instalação local, também no SQLite.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

from core.assets import ASSETS
from core.demo_mode import catalog_assets
from core.local_catalog import REFERENCE_SETTING, LocalCatalog, db_path, editable_enabled, local_group_labels

REFERENCE_KEY = "referencia_padrao"


@st.cache_resource(show_spinner=False)
def _local_catalog(path: str) -> LocalCatalog:
    return LocalCatalog(path, base_assets=ASSETS)


def local_catalog() -> Optional[LocalCatalog]:
    """Camada editável, ou None quando a edição está desligada (versão pública)."""
    return _local_catalog(str(db_path())) if editable_enabled() else None


def active_catalog() -> list:
    """Catálogo exibido nos menus: o base (filtrado no modo demo) mais os ativos locais."""
    catalog = catalog_assets(ASSETS)
    local = local_catalog()
    return catalog + local.records() if local else catalog


def find_asset(ticker: str) -> Optional[dict]:
    t = str(ticker or "").upper()
    return next((a for a in active_catalog() if str(a.get("ticker", "")).upper() == t), None)


def group_label(key) -> str:
    """Rótulo de um grupo, base ou local."""
    from app.ui.sidebar import GROUP_MAPPING   # import tardio: a barra lateral usa este módulo

    text = str(key)
    if text.lower() in GROUP_MAPPING:
        return GROUP_MAPPING[text.lower()]
    local = local_catalog()
    labels = local_group_labels(local.groups()) if local else {}
    return labels.get(text, text.replace("_", " ").title())


def preferred_reference() -> Optional[str]:
    """Referência padrão escolhida em Configurações (None = automática)."""
    if REFERENCE_KEY not in st.session_state:
        local = local_catalog()
        st.session_state[REFERENCE_KEY] = local.get_setting(REFERENCE_SETTING) if local else None
    return st.session_state[REFERENCE_KEY]


def set_preferred_reference(ticker: Optional[str]) -> None:
    st.session_state[REFERENCE_KEY] = ticker
    local = local_catalog()
    if local:
        local.set_setting(REFERENCE_SETTING, ticker)
