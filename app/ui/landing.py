"""
Blocos HTML da página inicial e do modal de informações acadêmicas.

As funções aqui só montam texto HTML (sem chamar o Streamlit), para que
possam ser testadas isoladamente. Todo texto vindo do catálogo de ativos é
escapado antes de entrar no HTML. Visual: cantos retos e linhas pretas finas
(ver app/ui/design.py).
"""

from __future__ import annotations

import base64
from html import escape
from pathlib import Path
from typing import Callable, Iterable, Mapping, Optional

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
INSTITUTIONAL_DIR = ASSETS_DIR / "institucional"
FEATURES_VIDEO = ASSETS_DIR / "video" / "argos_recursos.mp4"

ACADEMIC_INFO = {
    "system": "Argos DataLab",
    "system_summary": "Plataforma web para análise exploratória de ativos financeiros, "
                      "comparação de desempenho, indicadores técnicos e métricas de risco",
    "institution": "Universidade Federal do Piauí (UFPI)",
    "center": "Centro de Educação Aberta e a Distância (CEAD)",
    "course": "Curso Superior de Tecnologia em Gestão de Dados",
    "program": "Programa Institucional de Bolsas de Iniciação em Desenvolvimento "
               "Tecnológico e Inovação (PIBITI UFPI 2026–2027)",
    "work_plan": "Análise de Dados para Apoio à Tomada de Decisão em Investimentos "
                 "no Mercado Financeiro",
    "author": "Clériston de Castro Ramos",
    "author_role": "Pesquisador discente, bolsista PIBITI",
    "advisor": "Prof. Dr. Arlino Henrique Magalhães de Araújo",
    "advisor_role": "Orientador, docente da UFPI",
    "year": "2026–2027",
    "nature": "Pesquisa, ensino e desenvolvimento tecnológico; sem recomendação de investimento",
    "repository": "github.com/cleristoncramos/argos",
    "address": "argos-datalab.streamlit.app",
}

# (camada, tecnologia, papel no projeto)
TECHNOLOGIES = [
    ("Linguagem", "Python 3", "Toda a lógica de dados, cálculos e interface"),
    ("Dados", "pandas", "Limpeza, agregação por frequência e séries de retorno"),
    ("Dados", "NumPy", "Volatilidade, Sharpe, drawdown e estatísticas"),
    ("Interface", "Streamlit", "Aplicação web multipágina, navegação e cache"),
    ("Interface", "Plotly", "Gráficos interativos (linhas, candles, mapas de calor)"),
    ("Coleta", "yfinance", "Acesso às séries históricas do Yahoo Finance"),
    ("Qualidade", "pytest e pytest-cov", "Testes automatizados com cobertura medida"),
    ("Publicação", "GitHub e GitHub Actions", "Versionamento e rotina que mantém o app ativo"),
    ("Publicação", "Streamlit Community Cloud", "Hospedagem pública do sistema"),
    ("IA (opcional)", "API de modelo de linguagem", "Explicação assistida dos gráficos, desligada por padrão"),
]

# (fonte, conteúdo, uso no sistema)
DATA_SOURCES = [
    ("Yahoo Finance (via yfinance)",
     "Séries diárias de abertura, máxima, mínima, fechamento e volume. Consulta sob demanda, "
     "com cache de 1 hora.",
     "Base de todas as análises. Retornos calculados sobre o fechamento, sem dividendos."),
    ("Catálogo interno do Argos",
     "Ativos organizados por classe, mercado e subcategoria, com nome e descrição.",
     "Seleção guiada dos ativos e organização da interface."),
    ("Pacote de demonstração",
     "Arquivos CSV congelados, com manifesto, data da coleta e hash SHA-256 de cada arquivo.",
     "Apresentações e avaliação com usuários sem depender da internet."),
    ("CoinCap e Financial Modeling Prep",
     "Logotipos públicos de criptomoedas, ações, ETFs, REITs e FIIs.",
     "Identificação visual dos ativos; desligados no modo de demonstração."),
]

# (mito, leitura no Argos DataLab)
NAME_STORY = [
    ("O construtor",
     "Argos construiu o navio Argo com a orientação de Atena, deusa da sabedoria e da "
     "estratégia, e deu a ele o seu nome.",
     "A plataforma é a embarcação: uma infraestrutura construída com método para atravessar "
     "o mar de dados do mercado financeiro."),
    ("A proa que falava",
     "Na proa do Argo havia uma peça de carvalho sagrado capaz de falar e orientar a "
     "tripulação.",
     "Gráficos, indicadores e textos educativos traduzem os números em leitura compreensível."),
    ("Os Argonautas",
     "Jasão reuniu heróis com habilidades distintas: a força de Héracles, a música de Orfeu, "
     "a visão aguçada de Linceu.",
     "Cada classe de ativo tem seu comportamento: criptomoedas velozes e voláteis, ações e "
     "FIIs como base, commodities como recursos essenciais. Quem usa o sistema é o argonauta."),
    ("As rochas e as tempestades",
     "No caminho, as Simplégades se chocavam para esmagar os navios.",
     "Crises, quedas e volatilidade: o Argos mede esses perigos com drawdown, volatilidade e "
     "Índice de Sharpe."),
    ("O Velocino de Ouro",
     "O tesouro que motivava a jornada, guardado por um dragão que nunca dormia.",
     "O objetivo é a decisão mais bem informada: entender risco e retorno com dados "
     "históricos. O dragão que não dorme é o mercado, que não para; o sistema não promete o "
     "tesouro, ajuda a ler o mapa."),
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


# ==========================================================
# Mosaico de ativos
# ==========================================================
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
    color = escape(asset.get("category_color", "#5f5f5f"))
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
*{box-sizing:border-box;border-radius:0}
html,body{margin:0;background:transparent;font-family:"Source Sans 3","Source Sans Pro",-apple-system,"Segoe UI",sans-serif;overflow:hidden}
.mosaic{display:flex;flex-direction:column;gap:12px;padding:2px 0;
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent);
          mask-image:linear-gradient(90deg,transparent,#000 7%,#000 93%,transparent)}
.lane{overflow:hidden}
.track{display:flex;gap:12px;width:max-content;animation:slide var(--d) linear infinite;animation-direction:var(--dir)}
.mosaic:hover .track{animation-play-state:paused}
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.tile{position:relative;display:flex;align-items:center;gap:12px;min-width:240px;padding:10px 14px 10px 10px;
  background:#fff;border:1px solid #1f1f1f;transition:transform .2s ease,background .2s ease}
.tile::before{content:"";position:absolute;left:-1px;top:-1px;bottom:-1px;width:3px;background:var(--c)}
.tile:hover{transform:translateY(-2px);background:#f5f5f3}
.logo{position:relative;flex:none;width:42px;height:42px;background:#fff;border:1px solid #d4d4d4;display:grid;place-items:center;overflow:hidden}
.logo img{width:80%;height:80%;object-fit:contain;position:relative;z-index:1}
.logo b{position:absolute;inset:0;display:none;place-items:center;font-size:.7rem;color:#fff;background:var(--c)}
.logo.fallback b{display:grid}
.logo.emoji{font-size:1.35rem;background:#f5f5f3}
.txt{display:flex;flex-direction:column;min-width:0}
.tk{color:#111;font-weight:700;font-size:.88rem;letter-spacing:.02em;font-family:"JetBrains Mono",ui-monospace,Consolas,monospace}
.nm{color:#5f5f5f;font-size:.76rem;white-space:nowrap;max-width:132px;overflow:hidden;text-overflow:ellipsis}
.cls{margin-left:auto;padding:2px 7px;font-size:.6rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
  color:#111;border:1px solid #1f1f1f;white-space:nowrap}
@media (prefers-reduced-motion:reduce){.track{animation:none}}
</style></head><body><div class="mosaic">{{LANES}}</div></body></html>"""


# ==========================================================
# Modal de informações acadêmicas
# ==========================================================
def _table(rows: Iterable[tuple[str, ...]], header: Optional[tuple[str, ...]] = None,
           css_class: str = "ac-table") -> str:
    head = ""
    if header:
        head = "<thead><tr>" + "".join(f"<th>{escape(h)}</th>" for h in header) + "</tr></thead>"
    body = "".join(
        "<tr>" + "".join(
            f"<{'th' if i == 0 and not header else 'td'}>{escape(cell)}</{'th' if i == 0 and not header else 'td'}>"
            for i, cell in enumerate(row)
        ) + "</tr>"
        for row in rows
    )
    return f'<table class="{css_class}">{head}<tbody>{body}</tbody></table>'


def build_academic_header_html(logos: Mapping[str, Optional[str]]) -> str:
    """Cabeçalho do modal: logotipos (UFPI e CEAD), instituição, centro e curso."""
    plates = "".join(
        f'<img src="{uri}" alt="Logotipo {escape(name)}">' for name, uri in logos.items() if uri
    )
    info = ACADEMIC_INFO
    return f"""
<div class="ac-head">
  <div class="ac-logos">{plates}</div>
  <div class="ac-ids">
    <div class="ac-inst">{escape(info["institution"])}</div>
    <div class="ac-center">{escape(info["center"])}</div>
    <div class="ac-course">{escape(info["course"])}</div>
  </div>
</div>
<div class="ac-title">
  <div class="ac-kicker">Trabalho acadêmico · {escape(info["year"])}</div>
  <div class="ac-name">{escape(info["system"])}</div>
  <div class="ac-summary">{escape(info["system_summary"])}.</div>
</div>"""


def build_identification_html() -> str:
    """Ficha de identificação do trabalho."""
    info = ACADEMIC_INFO
    rows = (
        ("Sistema", info["system"]),
        ("Plano de trabalho", info["work_plan"]),
        ("Programa", info["program"]),
        ("Instituição", info["institution"]),
        ("Centro", info["center"]),
        ("Curso", info["course"]),
        ("Autor", f'{info["author"]} ({info["author_role"]})'),
        ("Orientador", f'{info["advisor"]} ({info["advisor_role"]})'),
        ("Vigência", info["year"]),
        ("Natureza", info["nature"]),
        ("Endereço", info["address"]),
        ("Repositório", info["repository"]),
    )
    return _table(rows)


def build_name_story_html() -> str:
    """Seção 'Por que Argos DataLab': o mito do navio Argo lido no sistema."""
    intro = (
        '<p class="ac-lead">Na mitologia grega, <b>Argos</b> foi o construtor do <b>Argo</b>, o '
        "navio que levou Jasão e os Argonautas por mares desconhecidos em busca do Velocino de "
        "Ouro. O nome une essa jornada guiada por sabedoria e técnica a um <b>DataLab</b>: um "
        "laboratório onde os dados de mercado são explorados com método, de forma reproduzível "
        "e transparente.</p>"
    )
    table = _table(
        ((title, myth, reading) for title, myth, reading in NAME_STORY),
        header=("Elemento", "No mito", "No Argos DataLab"),
        css_class="ac-table ac-story",
    )
    return intro + table


def build_technologies_html() -> str:
    """Tabela com as tecnologias utilizadas, por camada."""
    return _table(TECHNOLOGIES, header=("Camada", "Tecnologia", "Papel no projeto"),
                  css_class="ac-table ac-grid")


def build_data_sources_html(stats: Mapping[str, int]) -> str:
    """Tabela das bases de dados e da cobertura do catálogo."""
    coverage = (
        f'<div class="ac-stats"><div><b>{stats["assets"]}</b><span>ativos</span></div>'
        f'<div><b>{stats["classes"]}</b><span>classes</span></div>'
        f'<div><b>{stats["groups"]}</b><span>mercados</span></div>'
        "<div><b>OHLCV</b><span>diário</span></div></div>"
    )
    table = _table(DATA_SOURCES, header=("Fonte", "Conteúdo", "Uso no sistema"),
                   css_class="ac-table ac-grid")
    note = (
        '<p class="ac-note">Dados de mercado podem ter atrasos, ajustes históricos e falhas '
        "temporárias da fonte. Resultados passados não garantem resultados futuros.</p>"
    )
    return coverage + table + note


ACADEMIC_MODAL_CSS = """
<style>
div[role="dialog"] { border: 1px solid #1f1f1f !important; box-shadow: 0 30px 80px rgba(0,0,0,.35) !important; }
.ac-head { display: flex; align-items: stretch; border: 1px solid #1f1f1f; }
.ac-logos { display: flex; align-items: center; gap: 18px; padding: 14px 20px; background: #fff; border-right: 1px solid #1f1f1f; }
.ac-logos img { height: 58px; width: auto; display: block; }
.ac-logos img + img { padding-left: 18px; border-left: 1px solid #d4d4d4; }
.ac-ids { flex: 1; padding: 14px 20px; background: #111; color: #fff; display: flex; flex-direction: column; justify-content: center; }
.ac-inst { font-size: 1.15rem; font-weight: 700; letter-spacing: -.01em; }
.ac-center { margin-top: 3px; color: #ff8a8a; font-weight: 600; font-size: .9rem; }
.ac-course { color: #d4d4d4; font-size: .86rem; }
.ac-title { padding: 18px 0 6px; border-bottom: 1px solid #1f1f1f; margin-bottom: 4px; }
.ac-kicker { color: #c8102e; font-size: .7rem; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; }
.ac-name { font-size: 1.9rem; font-weight: 800; letter-spacing: -.03em; color: #111; line-height: 1.15; }
.ac-summary { color: #5f5f5f; font-size: .95rem; margin-bottom: 10px; }
.ac-table { width: 100%; border-collapse: collapse; border: 1px solid #1f1f1f; font-size: .88rem; margin: 6px 0 10px; }
.ac-table th, .ac-table td { padding: 9px 12px; text-align: left; vertical-align: top; border: 0; border-bottom: 1px solid #d4d4d4; color: #111; }
.ac-table tr:last-child th, .ac-table tr:last-child td { border-bottom: 0; }
.ac-table tbody th { width: 170px; background: #f5f5f3; font-weight: 700; border-right: 1px solid #1f1f1f; }
.ac-table thead th { background: #111; color: #fff; font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; font-weight: 700; }
.ac-grid td:first-child, .ac-story td:first-child { font-weight: 700; white-space: nowrap; background: #f5f5f3; border-right: 1px solid #d4d4d4; }
.ac-story td:nth-child(2) { color: #5f5f5f; width: 36%; }
.ac-lead { font-size: .95rem; line-height: 1.65; color: #111; margin: 8px 0 12px; padding-left: 12px; border-left: 3px solid #c8102e; }
.ac-stats { display: grid; grid-template-columns: repeat(4, 1fr); border: 1px solid #1f1f1f; margin: 8px 0 10px; }
.ac-stats div { padding: 10px 14px; border-right: 1px solid #1f1f1f; }
.ac-stats div:last-child { border-right: 0; }
.ac-stats b { display: block; font-size: 1.35rem; color: #111; }
.ac-stats span { font-size: .68rem; text-transform: uppercase; letter-spacing: .12em; color: #5f5f5f; font-weight: 700; }
.ac-note { font-size: .8rem; color: #5f5f5f; margin: 4px 0 0; }
@media (max-width: 760px) {
  .ac-head { flex-direction: column; }
  .ac-logos { border-right: 0; border-bottom: 1px solid #1f1f1f; }
  .ac-logos img { height: 44px; }
  .ac-table tbody th { width: 110px; }
  .ac-stats { grid-template-columns: repeat(2, 1fr); }
}
</style>
"""
