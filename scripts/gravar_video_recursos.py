"""
Grava o vídeo da página inicial (app/assets/video/argos_recursos.mp4).

O vídeo é a animação de scripts/video_recursos/animacao.html: um tour curto e
ilustrativo pelos recursos do Argos (catálogo, análise individual, comparação,
indicadores, risco, sazonalidade e simulação). Os quadros vêm do screencast do
Chromium (JPEG de alta qualidade) e são codificados em MP4 (H.264) pelo ffmpeg
do imageio-ffmpeg.

Pré-requisitos (fora do requirements do app):

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
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANIMATION = Path(__file__).resolve().parent / "video_recursos" / "animacao.html"
OUTPUT = PROJECT_ROOT / "app" / "assets" / "video" / "argos_recursos.mp4"
WIDTH, HEIGHT = 1280, 720
FPS = 30


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
