"""Exibição das notas de comparabilidade."""

import streamlit as st


def render_comparison_notes(notes: list[tuple[str, str]]) -> None:
    for level, text in notes:
        {"error": st.error, "warning": st.warning}.get(level, st.info)(text)