"""
Visita o app publicado no Streamlit Community Cloud com um navegador real.

O Community Cloud hiberna apps sem visitas por cerca de 12 horas. Um simples
``curl`` não conta como visita: a URL responde com um redirecionamento para a
autenticação do share.streamlit.io e o app nem chega a ser aberto. Este script
abre a página no Chromium (Playwright), espera o app carregar e, se ele já
estiver hibernando, clica no botão de acordar.

Uso (executado pelo workflow .github/workflows/keep-alive.yml):

    pip install playwright
    python -m playwright install --with-deps chromium
    python scripts/manter_app_ativo.py
    python scripts/manter_app_ativo.py --url https://argos-datalab.streamlit.app

Sai com código 1 se o app não carregar, para que a falha apareça no Actions.
"""

from __future__ import annotations

import argparse
import sys

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

APP_URL = "https://argos-datalab.streamlit.app"
WAKE_BUTTON = "Yes, get this app back up"
APP_MARKER = "Argos DataLab"
LOAD_TIMEOUT_MS = 60_000
WAKE_TIMEOUT_MS = 300_000  # um app hibernado pode levar alguns minutos para subir


def app_loaded(page, timeout_ms: int) -> bool:
    """True se o texto do app aparecer na página ou no iframe do app."""
    deadline_steps = max(1, timeout_ms // 5_000)
    for _ in range(deadline_steps):
        for frame in page.frames:
            try:
                if frame.get_by_text(APP_MARKER).first.is_visible():
                    return True
            except Exception:  # frame recarregando ou já descartado
                continue
        page.wait_for_timeout(5_000)
    return False


def visit(url: str) -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=LOAD_TIMEOUT_MS)

        wake = page.get_by_role("button", name=WAKE_BUTTON)
        try:
            wake.wait_for(state="visible", timeout=15_000)
            print("App hibernando: clicando no botão para acordar.")
            wake.click()
            timeout_ms = WAKE_TIMEOUT_MS
        except PlaywrightTimeout:
            print("App acordado: nenhuma tela de hibernação.")
            timeout_ms = LOAD_TIMEOUT_MS

        ok = app_loaded(page, timeout_ms)
        browser.close()

    if ok:
        print(f"App carregado em {url}.")
        return 0
    print(f"O app não carregou em {url} dentro do tempo limite.", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--url", default=APP_URL)
    args = parser.parse_args()
    return visit(args.url)


if __name__ == "__main__":
    sys.exit(main())
