"""
Grava o vídeo de demonstração exibido na página inicial (app/assets/video/).

O vídeo é uma navegação real pelo Argos, conduzida pelo Playwright: um cursor
visível se move até os controles, os campos são digitados e as páginas são
roladas com suavidade. Os quadros vêm do screencast do Chromium (JPEG de alta
qualidade) e são codificados em MP4 (H.264) pelo ffmpeg do imageio-ffmpeg.

Pré-requisitos (fora do requirements do app):

    pip install playwright imageio-ffmpeg pillow numpy
    python -m playwright install chromium

Com o app rodando em tema escuro e com internet (dados do Yahoo Finance):

    streamlit run app/main.py --server.port 8518 --theme.base dark --client.toolbarMode minimal
    python scripts/gravar_video_tour.py --url http://localhost:8518
    python scripts/gravar_video_tour.py --dry-run   # só executa o roteiro, sem gravar

Recomenda-se um --dry-run antes: ele aquece o cache de dados do app e a
gravação final fica sem esperas longas de carregamento.
"""

from __future__ import annotations

import argparse
import base64
import io
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "app" / "assets" / "video" / "argos_tour.mp4"
WIDTH, HEIGHT = 1280, 720
FPS = 30

CURSOR_SCRIPT = """
(() => {
  if (window.__argosCursor) return;
  window.__argosCursor = true;
  const install = () => {
    const c = document.createElement('div');
    c.id = 'argos-cursor';
    c.innerHTML = '<svg width="26" height="26" viewBox="0 0 24 24"><path d="M4 2l15 9.5-6.6 1.4 3.9 7.3-2.6 1.4-3.9-7.3L4 19z" fill="#fff" stroke="#0f172a" stroke-width="1.4" stroke-linejoin="round"/></svg>';
    Object.assign(c.style, {position:'fixed', left:'0', top:'0', zIndex:2147483647, pointerEvents:'none',
      transform:'translate(-200px,-200px)', filter:'drop-shadow(0 2px 4px rgba(0,0,0,.45))'});
    document.body.appendChild(c);
    const ring = document.createElement('div');
    Object.assign(ring.style, {position:'fixed', width:'34px', height:'34px', marginLeft:'-17px', marginTop:'-17px',
      borderRadius:'50%', border:'2px solid #ef4444', zIndex:2147483646, pointerEvents:'none', opacity:'0',
      transition:'transform .45s ease, opacity .45s ease'});
    document.body.appendChild(ring);
    document.addEventListener('mousemove', e => {
      c.style.transform = `translate(${e.clientX - 4}px, ${e.clientY - 2}px)`;
    }, true);
    document.addEventListener('mousedown', e => {
      ring.style.transition = 'none';
      ring.style.left = e.clientX + 'px'; ring.style.top = e.clientY + 'px';
      ring.style.transform = 'scale(.3)'; ring.style.opacity = '1';
      requestAnimationFrame(() => requestAnimationFrame(() => {
        ring.style.transition = 'transform .45s ease, opacity .45s ease';
        ring.style.transform = 'scale(1.4)'; ring.style.opacity = '0';
      }));
    }, true);
  };
  if (document.body) install(); else document.addEventListener('DOMContentLoaded', install);
})();
"""


class Tour:
    def __init__(self, page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.mouse = (WIDTH // 2, HEIGHT // 2)

    def pause(self, seconds: float) -> None:
        self.page.wait_for_timeout(int(seconds * 1000))

    def glide(self, x: float, y: float, seconds: float = 0.7) -> None:
        """Move o cursor em curva suave (easing) até (x, y)."""
        x0, y0 = self.mouse
        steps = max(8, int(seconds * 60))
        for i in range(1, steps + 1):
            t = i / steps
            ease = t * t * (3 - 2 * t)
            self.page.mouse.move(x0 + (x - x0) * ease, y0 + (y - y0) * ease)
            self.page.wait_for_timeout(int(seconds * 1000 / steps))
        self.mouse = (x, y)

    def glide_to(self, locator, seconds: float = 0.7) -> None:
        locator.scroll_into_view_if_needed()
        box = locator.bounding_box()
        self.glide(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, seconds)

    def click(self, locator, seconds: float = 0.7) -> None:
        self.glide_to(locator, seconds)
        self.pause(0.15)
        self.page.mouse.down()
        self.page.wait_for_timeout(90)
        self.page.mouse.up()

    def choose(self, label: str, text: str, scope=None) -> None:
        """Abre o selectbox pelo rótulo, digita o filtro e confirma."""
        scope = scope or self.page
        box = scope.locator('[data-testid="stSelectbox"]').filter(has_text=label).first
        self.click(box.locator("input, [role='combobox']").first)
        self.pause(0.35)
        self.page.keyboard.type(text, delay=85)
        self.pause(0.45)
        self.page.keyboard.press("Enter")
        self.wait_idle()

    def wait_idle(self, timeout: float = 60) -> None:
        """Espera o Streamlit terminar o rerun (indicador de execução some)."""
        self.pause(0.4)
        deadline = time.time() + timeout
        while time.time() < deadline:
            running = self.page.locator('[data-testid="stStatusWidget"]').count()
            if not running:
                break
            self.pause(0.25)
        self.pause(0.3)

    def scroll(self, pixels: int, seconds: float = 1.6) -> None:
        """Rolagem suave da área principal."""
        self.glide(WIDTH * 0.62, HEIGHT * 0.55, 0.3)
        steps = max(6, int(seconds * 30))
        for _ in range(steps):
            self.page.mouse.wheel(0, pixels / steps)
            self.page.wait_for_timeout(int(seconds * 1000 / steps))

    def open_page(self, title: str) -> None:
        link = self.page.locator('[data-testid="stSidebarNav"] a').filter(has_text=title).first
        self.click(link, 0.8)
        self.wait_idle()
        self.pause(0.6)

    def press_button(self, text: str) -> None:
        button = self.page.locator('[data-testid="stSidebar"] button').filter(has_text=text).first
        self.click(button, 0.8)
        self.wait_idle(90)


def run_script(tour: Tour) -> None:
    page = tour.page
    sidebar = page.locator('[data-testid="stSidebar"]')

    # 1. Análise individual do Bitcoin
    page.goto(f"{tour.base_url}/analise_individual", wait_until="networkidle")
    tour.wait_idle()
    tour.pause(1.2)
    tour.choose("Classe do Ativo", "Cripto", sidebar)
    tour.choose("Símbolo/Nome do Ativo", "BTC", sidebar)
    tour.press_button("Carregar Dados")
    tour.pause(1.2)
    tour.scroll(650, 2.2)
    tour.pause(1.4)
    tour.scroll(700, 2.2)
    tour.pause(1.4)
    tour.scroll(800, 2.4)
    tour.pause(1.6)

    # 2. Indicadores técnicos do mesmo ativo
    tour.open_page("Indicadores Técnicos")
    tour.choose("Classe do Ativo", "Cripto", sidebar)
    tour.choose("Símbolo/Nome do Ativo", "BTC", sidebar)
    tour.press_button("Gerar análise técnica")
    tour.pause(1.0)
    tour.scroll(600, 2.0)
    tour.pause(1.4)
    tour.scroll(700, 2.2)
    tour.pause(1.4)

    # 3. Risco e retorno de uma ação brasileira
    tour.open_page("Risco e Retorno")
    tour.choose("Classe do Ativo", "Ações Brasil", sidebar)
    tour.choose("Símbolo/Nome do Ativo", "PETR4", sidebar)
    tour.press_button("Analisar risco e retorno")
    tour.pause(1.0)
    tour.scroll(600, 2.0)
    tour.pause(1.6)
    tour.scroll(650, 2.0)
    tour.pause(1.8)


class Screencast:
    """Captura quadros do Chromium via CDP e grava um MP4 com taxa fixa."""

    def __init__(self, context, page):
        self.frames: list[tuple[float, str]] = []
        self.cdp = context.new_cdp_session(page)
        self.cdp.on("Page.screencastFrame", self._on_frame)

    def _on_frame(self, params):
        self.frames.append((params["metadata"]["timestamp"], params["data"]))
        self.cdp.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]})

    def start(self):
        self.cdp.send("Page.startScreencast", {
            "format": "jpeg", "quality": 92, "everyNthFrame": 1,
            "maxWidth": WIDTH * 2, "maxHeight": HEIGHT * 2,
        })

    def stop(self):
        self.cdp.send("Page.stopScreencast")

    def write_mp4(self, path: Path, skip_start: float = 0.0) -> None:
        import imageio_ffmpeg
        import numpy as np
        from PIL import Image

        frames = sorted(self.frames)
        if not frames:
            raise RuntimeError("Nenhum quadro capturado.")
        start = frames[0][0] + skip_start
        end = frames[-1][0]
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = imageio_ffmpeg.write_frames(
            str(path), (WIDTH, HEIGHT), fps=FPS, codec="libx264", quality=None,
            pix_fmt_out="yuv420p", macro_block_size=8,
            output_params=["-crf", "24", "-preset", "slow", "-movflags", "+faststart", "-an"],
        )
        writer.send(None)
        index, current = 0, None
        t = start
        while t <= end:
            while index < len(frames) and frames[index][0] <= t:
                current = frames[index][1]
                index += 1
            if current is not None:
                image = Image.open(io.BytesIO(base64.b64decode(current))).convert("RGB")
                if image.size != (WIDTH, HEIGHT):
                    image = image.resize((WIDTH, HEIGHT), Image.LANCZOS)
                writer.send(np.asarray(image).tobytes())
            t += 1 / FPS
        writer.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Grava o tour do Argos para a página inicial.")
    parser.add_argument("--url", default="http://localhost:8518")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--dry-run", action="store_true", help="executa o roteiro sem gravar")
    parser.add_argument("--headed", action="store_true", help="mostra o navegador")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=2,
            color_scheme="dark", locale="pt-BR",
        )
        context.add_init_script(CURSOR_SCRIPT)
        page = context.new_page()
        tour = Tour(page, args.url)
        cast = None if args.dry_run else Screencast(context, page)
        if cast:
            cast.start()
        started = time.time()
        try:
            run_script(tour)
        except Exception:
            page.screenshot(path=str(PROJECT_ROOT / "tour_erro.png"))
            raise
        finally:
            if cast:
                cast.stop()
        print(f"Roteiro executado em {time.time() - started:.1f} s.")
        browser.close()

    if cast:
        cast.write_mp4(args.output, skip_start=1.8)  # descarta o carregamento inicial
        size_mb = args.output.stat().st_size / 1_048_576
        print(f"Vídeo gravado em {args.output} ({size_mb:.1f} MB).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
