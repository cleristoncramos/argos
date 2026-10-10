"""Aviso permanente do modo de demonstração (versão congelada, dados salvos)."""

import streamlit as st

from core.demo_mode import banner_message, is_demo_mode, verify_package


def render_demo_banner() -> None:
    """Mostra o aviso em todas as páginas; não faz nada fora do modo demo."""
    if not is_demo_mode():
        return

    st.info(banner_message(), icon="🧊")

    problems = verify_package()
    if problems:
        st.error(
            "O pacote de dados da demonstração tem problemas: "
            + " ".join(problems)
            + " Gere-o novamente com `python scripts/gerar_dados_demo.py`."
        )