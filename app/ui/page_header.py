"""
Cabeçalho padrão das páginas de análise.

Mesmo desenho em todas as páginas, sem ícones: linha do módulo, título e
subtítulo. O título e a numeração vêm da ordem oficial (app/ui/pages.py),
para combinar com o menu e com os "Primeiros passos" da página inicial.
O estilo (classes pg-*) está em app/ui/design.py.
"""

from html import escape

import streamlit as st

from app.ui.pages import MENU_PAGES

# Páginas de análise numeradas; "Sobre o Projeto" (a última) é institucional.
ANALYSIS_PAGES = MENU_PAGES[:-1]


def build_page_header_html(path: str, subtitle: str) -> str:
    """HTML do cabeçalho da página `path` (caminho como em app/ui/pages.py)."""
    paths = [spec.path for spec in ANALYSIS_PAGES]
    if path not in paths:
        raise ValueError(f"Página sem cabeçalho de análise: {path}")
    index = paths.index(path)
    spec = ANALYSIS_PAGES[index]
    kicker = f"Módulo {index + 1:02d} de {len(ANALYSIS_PAGES):02d} · Análise histórica"
    return (
        '<header class="pg-head">'
        f'<div class="pg-kicker">{escape(kicker)}</div>'
        f'<h1 class="pg-title">{escape(spec.title)}</h1>'
        f'<p class="pg-sub">{escape(subtitle)}</p>'
        "</header>"
    )


def render_page_header(path: str, subtitle: str) -> None:
    st.markdown(build_page_header_html(path, subtitle), unsafe_allow_html=True)
