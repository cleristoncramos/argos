"""Componentes de UI para explicar cada indicador técnico."""

import streamlit as st

from core.indicator_docs import INDICATOR_DOCS, get_indicator_doc


def render_indicator_note(key: str) -> None:
    """Legenda curta (o que mede + limitação) logo abaixo de um gráfico."""
    doc = get_indicator_doc(key)
    if doc is None:
        return
    st.caption(f"**{doc.name}** ({doc.category}): {doc.measures} {doc.limitations}")


def render_indicator_glossary(keys: list[str] | None = None) -> None:
    """Expander com ficha completa dos indicadores (fórmula, parâmetros, limitações)."""
    keys = keys or list(INDICATOR_DOCS)
    with st.expander("📘 O que significa cada indicador?", expanded=False):
        st.markdown(
            "Indicadores técnicos são transformações matemáticas de preço e volume. "
            "Aqui eles **descrevem o comportamento histórico**; não indicam compra ou venda."
        )
        for key in keys:
            doc = get_indicator_doc(key)
            if doc is None:
                continue
            st.markdown(f"#### {doc.name} · _{doc.category}_")
            st.markdown(f"**O que mede:** {doc.measures}")
            st.markdown(f"**Cálculo:** `{doc.formula}`")
            if doc.parameters:
                params = " · ".join(f"{k}: {v}" for k, v in doc.parameters.items())
                st.markdown(f"**Parâmetros:** {params}")
            st.markdown(f"**Limitações:** {doc.limitations}")