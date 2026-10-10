"""Componentes educativos: 'O que significa?' e glossário."""

import streamlit as st

from core.edu_layer import edu_layer_enabled
from core.glossary import GLOSSARY, get_glossary_entry


def _render_entry(entry, heading: bool) -> None:
    if heading:
        st.markdown(f"#### {entry.term}")
    st.markdown(entry.definition)
    st.markdown(f"**Exemplo (valores hipotéticos):** {entry.example}")
    st.caption(f"Limitação: {entry.limitation}")


def render_what_it_means(key: str) -> None:
    """Expander compacto para um termo, posicionado perto da métrica/gráfico."""
    if not edu_layer_enabled():
        return
    entry = get_glossary_entry(key)
    if entry is None:
        return
    with st.expander(f"💡 O que significa: {entry.term}?", expanded=False):
        _render_entry(entry, heading=False)


def render_glossary(keys: list[str] | None = None) -> None:
    """Glossário completo (ou parcial) em um expander."""
    if not edu_layer_enabled():
        return
    with st.expander("📚 Glossário", expanded=False):
        st.markdown(
            "Conceitos usados nesta página, em linguagem simples. "
            "Os exemplos usam números hipotéticos apenas para ilustrar."
        )
        for key in keys or list(GLOSSARY):
            entry = get_glossary_entry(key)
            if entry:
                _render_entry(entry, heading=True)