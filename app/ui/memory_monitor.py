"""
Monitor do uso de memória (RAM) do aplicativo, em um selo discreto no canto
inferior esquerdo da tela.

Lê o consumo do próprio processo com psutil e se atualiza sozinho a cada
REFRESH_SECONDS segundos, sem recarregar a página. Serve para acompanhar o
limite de RAM do Streamlit Community Cloud. O selo fica quase transparente e
mostra os detalhes ao passar o mouse; perto do limite, fica vermelho.
"""

from __future__ import annotations

import os

import psutil
import streamlit as st

MEMORY_LIMIT_MB = 1024  # limite de RAM do Streamlit Community Cloud (1 GB)
MEMORY_WARNING_MB = 850  # a partir daqui, o selo fica vermelho
REFRESH_SECONDS = 10


def get_memory_usage() -> float:
    """Uso de RAM do processo atual, em megabytes (MB)."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def memory_share(usage_mb: float, limit_mb: float = MEMORY_LIMIT_MB) -> float:
    """Fração do limite em uso, entre 0 e 1."""
    return min(max(usage_mb / limit_mb, 0.0), 1.0)


def is_near_limit(usage_mb: float, warning_mb: float = MEMORY_WARNING_MB) -> bool:
    return usage_mb > warning_mb


def memory_badge_html(usage_mb: float) -> str:
    """Selo com o uso atual; o percentual do limite aparece ao passar o mouse."""
    level = "high" if is_near_limit(usage_mb) else "ok"
    detail = f"{memory_share(usage_mb):.0%} de {MEMORY_LIMIT_MB} MB"
    if level == "high":
        detail += " · próximo do limite"
    return (
        f'<div class="ram-badge {level}" title="Uso de RAM do aplicativo: {usage_mb:.2f} MB ({detail})">'
        f'<i></i>RAM {usage_mb:.0f} MB<span> · {detail}</span></div>'
    )


# O selo é fixo na tela; o bloco sai do fluxo da página para não deixar espaço vazio.
_STYLE = """<style>
[data-testid="stVerticalBlock"] > :has(> .st-key-memory_monitor) { position: absolute; }
[data-testid="stSidebarUserContent"] { padding-bottom: 44px !important; }
.ram-badge { position: fixed; left: 10px; bottom: 8px; z-index: 1000000; display: flex; align-items: center; gap: 6px;
  padding: 3px 9px; font: 600 .64rem/1.4 "JetBrains Mono", ui-monospace, Consolas, monospace; letter-spacing: .04em;
  color: #6b6b6b; background: rgba(255, 255, 255, .75); border: 1px solid #e4e1da; opacity: .5;
  transition: opacity .2s ease; white-space: nowrap; }
.ram-badge:hover { opacity: 1; }
.ram-badge i { width: 6px; height: 6px; border-radius: 50% !important; background: #16a34a; }
.ram-badge span { display: none; }
.ram-badge:hover span { display: inline; }
.ram-badge.high { opacity: 1; color: #b50e29; border-color: #b50e29; }
.ram-badge.high i { background: #c8102e; }
</style>"""


@st.fragment(run_every=REFRESH_SECONDS)
def _memory_badge() -> None:
    st.markdown(_STYLE + memory_badge_html(get_memory_usage()), unsafe_allow_html=True)


def render_memory_monitor() -> None:
    """Desenha o selo de RAM, em todas as páginas."""
    with st.container(key="memory_monitor"):
        _memory_badge()
