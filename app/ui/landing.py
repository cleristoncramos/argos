"""
Blocos HTML da página inicial e da página de informações acadêmicas.

As funções aqui só montam texto HTML (sem chamar o Streamlit), para que
possam ser testadas isoladamente. Todo texto vindo do catálogo de ativos é
escapado antes de entrar no HTML.
"""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path
from typing import Callable, Iterable, Mapping, Optional

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
INSTITUTIONAL_DIR = ASSETS_DIR / "institucional"
TOUR_VIDEO = ASSETS_DIR / "video" / "argos_tour.mp4"

ACADEMIC_INFO = {
    "institution": "Universidade Federal do Piauí (UFPI)",
    "center": "Centro de Educação Aberta e a Distância (CEAD)",
    "course": "Curso Superior de Tecnologia em Gestão de Dados",
    "program": "Programa Institucional de Bolsas de Iniciação em Desenvolvimento "
               "Tecnológico e Inovação (PIBITI UFPI 2026–2027)",
    "work_plan": "Análise de Dados para Apoio à Tomada de Decisão em Investimentos "
                 "no Mercado Financeiro",
    "author": "Clériston de Castro Ramos",
    "author_role": "Pesquisador discente (bolsista PIBITI)",
    "advisor": "Prof. Dr. Arlino Henrique Magalhães de Araújo",
    "advisor_role": "Orientador",
    "year": "2026–2027",
}

# (nome, papel no projeto)
TECHNOLOGIES = [
    ("Python", "Linguagem principal"),
    ("Streamlit", "Interface web e navegação"),
    ("pandas", "Tratamento de séries históricas"),
    ("NumPy", "Cálculos estatísticos"),
    ("Plotly", "Gráficos interativos"),
    ("yfinance", "Dados do Yahoo Finance"),
    ("pytest", "Testes automatizados"),
    ("GitHub Actions", "Rotina que mantém o app ativo"),
    ("Streamlit Community Cloud", "Publicação do app"),
]

_LOGO_TYPES = ((".svg", "image/svg+xml"), (".png", "image/png"))


def institutional_logo_uri(name: str, directory: Path = INSTITUTIONAL_DIR) -> Optional[str]:
    """Logotipo institucional (<name>.svg ou .png) como data URI; None se não existir."""
    for extension, mime in _LOGO_TYPES:
        path = directory / f"{name}{extension}"
        if path.exists():
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{encoded}"
    return None


def catalog_stats(assets: Iterable[Mapping[str, str]]) -> dict:
    """Quantidade de ativos, classes e mercados do catálogo."""
    records = list(assets)
    return {
        "assets": len(records),
        "classes": len({a["class"] for a in records}),
        "groups": len({a["group"] for a in records}),
    }


def _interleave_by_class(assets: list[Mapping[str, str]]) -> list[Mapping[str, str]]:
    """Alterna as classes para que cada faixa do mosaico misture tipos de ativo."""
    buckets: dict[str, list] = {}
    for asset in assets:
        buckets.setdefault(asset["class"], []).append(asset)
    queues = list(buckets.values())
    mixed = []
    while any(queues):
        for queue in queues:
            if queue:
                mixed.append(queue.pop(0))
    return mixed


def _monogram(ticker: str) -> str:
    core = ticker.lstrip("^").split(".")[0].split("-")[0].split("=")[0]
    return (core or ticker)[:4]


def _mosaic_tile(asset: Mapping[str, str], logo_url: Optional[str]) -> str:
    ticker = escape(asset["ticker"])
    name = escape(asset["name"])
    asset_class = escape(asset["class"])
    color = escape(asset.get("category_color", "#64748b"))
    fallback = escape(asset.get("icon") or _monogram(asset["ticker"]))
    monogram = escape(_monogram(asset["ticker"]))
    if logo_url:
        # Se o logo remoto falhar, o monograma assume o lugar.
        badge = (
            f'<span class="logo"><img src="{escape(logo_url)}" alt="" loading="lazy" '
            f"onerror=\"this.parentNode.classList.add('fallback');this.remove()\">"
            f'<b>{monogram}</b></span>'
        )
    else:
        badge = f'<span class="logo emoji">{fallback}</span>'
    return (
        f'<div class="tile" style="--c:{color}">{badge}'
        f'<span class="txt"><span class="tk">{ticker}</span>'
        f'<span class="nm">{name}</span></span>'
        f'<span class="cls">{asset_class}</span></div>'
    )


def build_mosaic_html(
    assets: Iterable[Mapping[str, str]],
    logo_for: Callable[[str, str], Optional[str]],
    rows: int = 3,
) -> str:
    """Documento HTML do mosaico animado (faixas que deslizam em sentidos alternados)."""
    mixed = _interleave_by_class(list(assets))
    lanes = [mixed[i::rows] for i in range(rows)]
    durations = (140, 170, 155, 185)
    lanes_html = []
    for index, lane in enumerate(lanes):
        tiles = "".join(_mosaic_tile(a, logo_for(a["ticker"], a["group"])) for a in lane)
        direction = "reverse" if index % 2 else "normal"
        duration = durations[index % len(durations)]
        # O conteúdo é duplicado para o deslocamento de -50% fechar o ciclo sem salto.
        lanes_html.append(
            f'<div class="lane" style="--d:{duration}s;--dir:{direction}">'
            f'<div class="track">{tiles}{tiles}</div></div>'
        )
    return MOSAIC_TEMPLATE.replace("{{LANES}}", "".join(lanes_html))


MOSAIC_TEMPLATE = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}
html,body{margin:0;background:transparent;font-family:Inter,-apple-system,"Segoe UI",sans-serif;overflow:hidden}
.mosaic{position:relative;display:flex;flex-direction:column;gap:14px;padding:6px 0;
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 9%,#000 91%,transparent);
          mask-image:linear-gradient(90deg,transparent,#000 9%,#000 91%,transparent)}
.lane{overflow:hidden}
.track{display:flex;gap:14px;width:max-content;animation:slide var(--d) linear infinite;animation-direction:var(--dir)}
.mosaic:hover .track{animation-play-state:paused}
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.tile{display:flex;align-items:center;gap:12px;min-width:236px;padding:11px 16px 11px 11px;border-radius:14px;
  background:linear-gradient(145deg,rgba(30,41,59,.78),rgba(15,23,42,.9));
  border:1px solid rgba(148,163,184,.16);box-shadow:0 8px 24px rgba(0,0,0,.25);
  transition:transform .25s ease,border-color .25s ease,box-shadow .25s ease}
.tile:hover{transform:translateY(-3px) scale(1.03);border-color:var(--c);box-shadow:0 12px 30px rgba(0,0,0,.4),0 0 0 1px var(--c)}
.logo{position:relative;flex:none;width:44px;height:44px;border-radius:12px;background:#fff;display:grid;place-items:center;overflow:hidden;
  box-shadow:0 0 0 2px var(--c)}
.logo img{width:78%;height:78%;object-fit:contain;position:relative;z-index:1}
.logo b{position:absolute;inset:0;display:none;place-items:center;font-size:.72rem;letter-spacing:.02em;color:#fff;background:var(--c)}
.logo.fallback b{display:grid}
.logo.emoji{background:rgba(255,255,255,.06);font-size:1.45rem}
.txt{display:flex;flex-direction:column;min-width:0}
.tk{color:#f8fafc;font-weight:800;font-size:.9rem;letter-spacing:.02em;font-family:"JetBrains Mono",ui-monospace,monospace}
.nm{color:#94a3b8;font-size:.74rem;white-space:nowrap;max-width:132px;overflow:hidden;text-overflow:ellipsis}
.cls{margin-left:auto;padding:3px 8px;border-radius:999px;font-size:.62rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--c);background:rgba(255,255,255,.04);border:1px solid rgba(148,163,184,.18);white-space:nowrap}
@media (prefers-reduced-motion:reduce){.track{animation:none}}
</style></head><body><div class="mosaic">{{LANES}}</div></body></html>"""


def build_academic_header_html(logos: Mapping[str, Optional[str]]) -> str:
    """Cabeçalho com os logotipos (UFPI e CEAD), instituição, centro e curso."""
    plates = "".join(
        f'<img src="{uri}" alt="Logotipo {escape(name)}">'
        for name, uri in logos.items()
        if uri
    )
    info = ACADEMIC_INFO
    return f"""
<div class="acad-hero">
  <div class="acad-logos">{plates}</div>
  <div class="acad-ids">
    <div class="acad-inst">{escape(info["institution"])}</div>
    <div class="acad-center">{escape(info["center"])}</div>
    <div class="acad-course">{escape(info["course"])}</div>
  </div>
</div>"""


def build_people_html() -> str:
    """Cartões de autor e orientador."""
    info = ACADEMIC_INFO
    people = (
        ("Autor", info["author"], info["author_role"]),
        ("Orientador", info["advisor"], "Docente da UFPI"),
    )
    cards = []
    for label, name, role in people:
        words = [w for w in name.replace("Prof. Dr. ", "").split() if w[0].isupper()]
        initials = words[0][0] + words[-1][0]
        cards.append(
            f'<div class="acad-person"><div class="acad-avatar">{escape(initials)}</div>'
            f'<div><div class="acad-label">{escape(label)}</div>'
            f'<div class="acad-name">{escape(name)}</div>'
            f'<div class="acad-role">{escape(role)}</div></div></div>'
        )
    return f'<div class="acad-people">{"".join(cards)}</div>'


def build_details_html() -> str:
    """Tabela de identificação do trabalho."""
    info = ACADEMIC_INFO
    rows = (
        ("Programa", info["program"]),
        ("Plano de trabalho", info["work_plan"]),
        ("Instituição", info["institution"]),
        ("Centro", info["center"]),
        ("Curso", info["course"]),
        ("Vigência", info["year"]),
    )
    body = "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(value)}</td></tr>" for label, value in rows
    )
    return f'<table class="acad-table">{body}</table>'


def build_technologies_html() -> str:
    """Grade com as tecnologias utilizadas e o papel de cada uma."""
    chips = "".join(
        f'<div class="acad-tech"><span>{escape(name)}</span><small>{escape(role)}</small></div>'
        for name, role in TECHNOLOGIES
    )
    return f'<div class="acad-techs">{chips}</div>'
