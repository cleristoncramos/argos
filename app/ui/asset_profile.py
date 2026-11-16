"""
Quadro "Sobre o ativo" da Análise Individual (16/11/2026): texto descritivo do ativo,
o que observar no histórico, números do período carregado e fontes. Fica recolhido,
logo abaixo do resumo da análise, para não competir com os gráficos.

Faz parte da camada educativa: com ARGOS_EDU_LAYER=off, não aparece.
A lógica e os textos ficam em core/asset_profiles.py e data/perfis_ativos/.
"""

from __future__ import annotations

from typing import Mapping, Optional

import pandas as pd
import streamlit as st

from core.asset_profiles import (
    PROFILE_NOTE,
    PROFILES_DIR,
    REVIEWED_ON,
    AssetProfile,
    get_profile,
    load_profiles,
    period_facts,
)
from core.currency import currency_info
from core.edu_layer import edu_layer_enabled


@st.cache_data(show_spinner=False)
def _cached_profiles(version: tuple) -> dict[str, AssetProfile]:
    return load_profiles()


def _profiles() -> dict[str, AssetProfile]:
    # Como nos eventos históricos: a data e o tamanho dos arquivos entram na chave do
    # cache, para que um texto revisado apareça logo depois do deploy.
    version = tuple(
        (p.name, p.stat().st_mtime_ns, p.stat().st_size) for p in sorted(PROFILES_DIR.glob("*.json"))
    )
    return _cached_profiles(version)


def _md(text: str) -> str:
    """Escapa o cifrão: no Markdown do Streamlit, "R$ 10 ... US$ 5" viraria fórmula."""
    return text.replace("$", "\\$")


def _profile_markdown(profile: AssetProfile) -> str:
    parts = [*profile.about, "##### Origem e história", *profile.history,
             "##### O que observar no histórico", profile.watch]
    return _md("\n\n".join(parts))


def render_asset_profile(asset: Mapping[str, str], symbol: str, daily: Optional[pd.DataFrame]) -> None:
    """Quadro recolhido com o texto do ativo e as informações do período carregado."""
    if not edu_layer_enabled():
        return
    profile = get_profile(symbol, _profiles())
    name = asset.get("name") or symbol
    with st.expander(f"📖 Sobre o ativo: {name}", expanded=False):
        if profile:
            st.markdown(_profile_markdown(profile))
        else:
            st.markdown(
                "Ainda não há um texto sobre este ativo no Argos. Os textos cobrem os "
                "148 ativos do catálogo; ativos digitados ou acrescentados numa instalação "
                "local mostram só as informações do período."
            )
        facts = period_facts(daily, currency_info(symbol))
        if facts:
            st.markdown("##### Informações do período carregado")
            st.markdown(_md("\n".join(f"- {fact}" for fact in facts)))
        if profile:
            links = " · ".join(f"[{label}]({url})" for label, url in profile.sources)
            st.markdown(f"**Para saber mais:** {links}")
        st.caption(f"{PROFILE_NOTE} Texto revisado em {REVIEWED_ON}; números calculados com os dados carregados.")
