"""
Monitor do uso de memória (RAM) do aplicativo, exibido no fim da barra lateral.

Lê o consumo do próprio processo com psutil e se atualiza sozinho a cada
REFRESH_SECONDS segundos, sem recarregar a página. Serve para acompanhar o
limite de RAM do Streamlit Community Cloud.
"""

from __future__ import annotations

import os

import psutil
import streamlit as st

MEMORY_LIMIT_MB = 1024  # limite de RAM do Streamlit Community Cloud (1 GB)
MEMORY_WARNING_MB = 850  # a partir daqui, o painel exibe um alerta
REFRESH_SECONDS = 10


def get_memory_usage() -> float:
    """Uso de RAM do processo atual, em megabytes (MB)."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def memory_share(usage_mb: float, limit_mb: float = MEMORY_LIMIT_MB) -> float:
    """Fração do limite em uso, entre 0 e 1 (para a barra de progresso)."""
    return min(max(usage_mb / limit_mb, 0.0), 1.0)


def is_near_limit(usage_mb: float, warning_mb: float = MEMORY_WARNING_MB) -> bool:
    return usage_mb > warning_mb


@st.fragment(run_every=REFRESH_SECONDS)
def _memory_panel() -> None:
    usage = get_memory_usage()
    st.metric(label="Uso de RAM atual", value=f"{usage:.2f} MB")
    st.progress(
        memory_share(usage),
        text=f"{memory_share(usage):.0%} do limite de {MEMORY_LIMIT_MB} MB",
    )
    if is_near_limit(usage):
        st.warning("O aplicativo está próximo do limite de RAM.")


# Desenhado antes da página, o bloco é levado ao fim da barra lateral pela ordem do flexbox.
_STYLE = """<style>
[data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] > :has(> .st-key-memory_monitor) { order: 999; }
.st-key-memory_monitor { margin-top: 12px; padding-top: 14px; border-top: 1px solid #d8d4cc; }
</style>"""


def render_memory_monitor() -> None:
    """Desenha o monitor no fim da barra lateral, em todas as páginas."""
    with st.sidebar:
        st.markdown(_STYLE, unsafe_allow_html=True)
        with st.container(key="memory_monitor"):
            _memory_panel()
