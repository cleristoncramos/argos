"""
Teste de fumaça: a página inicial e o estado inicial de cada página abrem sem
exceção (Streamlit AppTest, sem rede: as páginas de análise só consultam dados
depois do clique do usuário).

Motivo: em 25/10/2026, a inclusão da sétima página quebrou a grade de
"Primeiros passos" da página inicial (IndexError), e o erro só apareceu na
conferência da versão publicada.
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app.ui.pages import MENU_PAGES

APP = Path(__file__).resolve().parents[1] / "app"


def test_home_opens_with_one_card_per_page():
    at = AppTest.from_file(str(APP / "main.py"), default_timeout=60)
    at.run()
    assert not at.exception, [e.message for e in at.exception]
    assert len(at.get("page_link")) == len(MENU_PAGES)


@pytest.mark.parametrize("spec", MENU_PAGES, ids=lambda spec: spec.title)
def test_every_page_opens_in_its_initial_state(spec):
    at = AppTest.from_file(str(APP / spec.path), default_timeout=60)
    at.run()
    assert not at.exception, [e.message for e in at.exception]
