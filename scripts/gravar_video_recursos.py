"""
Grava o vídeo da página inicial (app/assets/video/argos_recursos.mp4).

O vídeo é a animação de scripts/video_recursos/animacao.html: um tour curto e
ilustrativo pelos recursos do Argos (catálogo, análise individual, comparação,
indicadores, risco, sazonalidade e simulação). Os quadros vêm do screencast do
Chromium (JPEG de alta qualidade) e são codificados em MP4 (H.264) pelo ffmpeg
do imageio-ffmpeg.

Os logotipos exibidos (catálogo e comparação) são os reais do catálogo:
o script baixa cada um (CoinCap e Financial Modeling Prep), descarta os que
falham ou vêm em branco e os injeta na animação como imagens embutidas.

Pré-requisitos (além das dependências do app, em requirements.txt):

    pip install playwright imageio-ffmpeg pillow numpy
    python -m playwright install chromium

Uso:

    python scripts/gravar_video_recursos.py
    python scripts/gravar_video_recursos.py --output caminho/do/video.mp4

Para ajustar a animação, abra animacao.html no navegador: ela toca sozinha.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANIMATION = Path(__file__).resolve().parent / "video_recursos" / "animacao.html"
OUTPUT = PROJECT_ROOT / "app" / "assets" / "video" / "argos_recursos.mp4"
WIDTH, HEIGHT = 1280, 720
FPS = 30
# Ativos da cena de comparação: precisam ter logotipo válido.
COMPARED = ("BTC-USD", "AAPL", "PETR4.SA", "MSFT")


def _fetch_logo(url: str):
    """PNG 160x160 em data URI, ou None se a imagem falhar ou vier em branco."""
    from PIL import Image, ImageStat

    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(request, timeout=15).read()
        image = Image.open(io.BytesIO(data)).convert("RGBA")
    except Exception:
        return None
    canvas = Image.new("RGBA", image.size, (255, 255, 255, 255))
    canvas.alpha_composite(image)
    if sum(ImageStat.Stat(canvas.convert("L")).stddev) < 8:  # imagem lisa: sem logotipo
        return None
    canvas.thumbnail((160, 160))
    buffer = io.BytesIO()
    canvas.convert("RGB").save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def collect_logos() -> list[dict]:
    """Logotipos reais do catálogo, alternando os grupos para variar a grade."""
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from core.asset_logos import get_asset_logo_url
    from core.assets import ASSET_GROUPS, ASSETS

    by_group = {g["key"]: [a for a in ASSETS if a["group"] == g["key"]] for g in ASSET_GROUPS}
    ordered = []
    while any(by_group.values()):
        for queue in by_group.values():
            if queue:
                ordered.append(queue.pop(0))
    candidates = [(a["ticker"], get_asset_logo_url(a["ticker"], a["group"])) for a in ordered]
    candidates = [(ticker, url) for ticker, url in candidates if url]
    with ThreadPoolExecutor(12) as pool:
        sources = list(pool.map(lambda item: _fetch_logo(item[1]), candidates))
    logos, seen = [], set()
    for (ticker, _), src in zip(candidates, sources):
        # Fundos da mesma gestora (Vanguard, iShares) repetem o logotipo: mostra uma vez.
        if src and src not in seen:
            seen.add(src)
            logos.append({"ticker": ticker, "src": src})
    missing = [ticker for ticker in COMPARED if ticker not in {l["ticker"] for l in logos}]
    if missing:
        print(f"Aviso: sem logotipo para {', '.join(missing)}; a comparação usará o ticker.")
    return logos


class Screencast:
    """Captura quadros do Chromium via CDP e grava um MP4 com taxa fixa."""

    def __init__(self, context, page):
        self.frames: list[tuple[float, str]] = []
        self.cdp = context.new_cdp_session(page)
        self.cdp.on("Page.screencastFrame", self._on_frame)

    def _on_frame(self, params):
        self.frames.append((params["metadata"]["timestamp"], params["data"]))
        try:
            self.cdp.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]})
        except Exception:  # quadro que chega depois de o navegador fechar
            pass

    def start(self):
        self.cdp.send("Page.startScreencast", {
            "format": "jpeg", "quality": 92, "everyNthFrame": 1,
            "maxWidth": WIDTH * 2, "maxHeight": HEIGHT * 2,
        })

    def stop(self):
        self.cdp.send("Page.stopScreencast")

    def write_mp4(self, path: Path, start_at: float, seconds: float) -> None:
        import imageio_ffmpeg
        import numpy as np
        from PIL import Image

        frames = sorted(self.frames)
        if not frames:
            raise RuntimeError("Nenhum quadro capturado.")
        path.parent.mkdir(parents=True, exist_ok=True)
        writer = imageio_ffmpeg.write_frames(
            str(path), (WIDTH, HEIGHT), fps=FPS, codec="libx264", quality=None,
            pix_fmt_out="yuv420p", macro_block_size=8,
            output_params=["-crf", "22", "-preset", "slow", "-movflags", "+faststart", "-an"],
        )
        writer.send(None)
        index, current = 0, None
        for n in range(int(seconds * FPS)):
            t = start_at + n / FPS
            while index < len(frames) and frames[index][0] <= t:
                current = frames[index][1]
                index += 1
            if current is None:
                continue
            image = Image.open(io.BytesIO(base64.b64decode(current))).convert("RGB")
            if image.size != (WIDTH, HEIGHT):
                image = image.resize((WIDTH, HEIGHT), Image.LANCZOS)
            writer.send(np.asarray(image).tobytes())
        writer.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Grava a animação dos recursos do Argos em MP4.")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=2)
        logos = collect_logos()
        print(f"{len(logos)} logotipos reais carregados.")
        context.add_init_script(f"window.ARGOS_LOGOS = {json.dumps(logos)};")
        page = context.new_page()
        page.goto(ANIMATION.as_uri() + "?manual", wait_until="load")
        page.wait_for_timeout(800)  # fontes e emojis carregados
        cast = Screencast(context, page)
        cast.start()
        page.wait_for_timeout(500)
        start_at = page.evaluate("Date.now() / 1000")
        total = page.evaluate("window.startArgosTour(), window.ARGOS_TOTAL_SECONDS")
        page.wait_for_timeout(int(total * 1000) + 600)
        cast.stop()
        browser.close()

    cast.write_mp4(args.output, start_at, total)
    size_mb = args.output.stat().st_size / 1_048_576
    print(f"Vídeo de {total:.0f} s gravado em {args.output} ({size_mb:.1f} MB).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
