"""
Maiores quedas e recuperação no gráfico de drawdown da página Risco e Retorno (A7).

A tabela das três maiores quedas foi substituída (19/11/2026) por botões abaixo
do gráfico: ao escolher uma queda, o período do pico à recuperação ganha um fundo
discreto no gráfico, marcadores com tooltip no pico, no fundo e na recuperação, e
uma ficha com as datas e as durações. Os episódios vêm de core/drawdown_episodes.py.
"""

from html import escape

import plotly.graph_objects as go
import pandas as pd

from core.formatters import format_return_pct

# Espaço que não quebra: mantém "(≈ 5 meses)" junto.
NBSP = " "
HIGHLIGHT_COLOR = "#991b1b"
PILLS_KEY = "dd_pills"   # o Streamlit dá ao contêiner a classe .st-key-dd_pills

FREQUENCY_NOUNS = {
    "Diário": "diários",
    "Semanal": "semanais",
    "Mensal": "mensais",
    "Semestral": "semestrais",
    "Anual": "anuais",
}

HIGHLIGHT_HELP = (
    "Escolha uma queda para sombrear no gráfico o período do pico à recuperação e ver as "
    "datas e durações. Passe o mouse nos marcadores do gráfico para ver os detalhes. "
    "Clique de novo para ocultar."
)

DRAWDOWN_NOTES = (
    "**Como ler:** o *pico* é o maior valor antes da queda; o *fundo* é o menor valor antes "
    "de o preço voltar ao pico; a *recuperação* é a primeira data em que o preço igualou ou "
    "superou o pico. Durações em **dias corridos** entre essas datas. Quando o preço não "
    "voltou ao pico, a duração conta até a última observação, sem estimar quando a "
    "recuperação ocorreria. Considera apenas o preço de fechamento, sem dividendos."
)

NO_DRAWDOWN = "Não houve queda em relação a um pico anterior no período analisado."


def drawdown_prompt(frequency: str, top: int) -> str:
    """Rótulo dos botões: quantas quedas e em que base foram medidas."""
    noun = FREQUENCY_NOUNS.get(frequency, "do período")
    head = "A maior queda" if top == 1 else f"As {top} maiores quedas"
    return f"{head} do período, nos fechamentos {noun}"


def format_duration(days) -> str:
    """Dias corridos com uma aproximação em meses ou anos ("61 dias (≈ 2 meses)")."""
    if days is None or pd.isna(days):
        return "—"
    days = int(days)
    if days < 45:
        return f"{days} dia{'s' if days != 1 else ''}"
    if days < 730:
        months = round(days / 30.44)
        return f"{days} dias (≈{NBSP}{months}{NBSP}meses)"
    years = f"{days / 365.25:.1f}".replace(".", ",")
    return f"{days} dias (≈{NBSP}{years}{NBSP}anos)"


def short_duration(days: int) -> str:
    """Duração curta para o botão: "12 dias", "≈ 8 meses", "≈ 2,2 anos"."""
    if days < 45:
        return f"{days} dia{'s' if days != 1 else ''}"
    if days < 730:
        return f"≈{NBSP}{round(days / 30.44)}{NBSP}meses"
    return f"≈{NBSP}{days / 365.25:.1f}{NBSP}anos".replace(".", ",")


def span_label(span: dict) -> str:
    """Texto do botão: "1ª  −64,27%  ·  12/2021 → 02/2024  ·  ≈ 2,2 anos"."""
    end = f"{span['end']:%m/%Y}" if span["recovered"] else "sem recuperação"
    duration = short_duration(span["days"])
    if not span["recovered"]:
        duration += " até agora"
    return (
        f"{span['position']}ª · {format_return_pct(span['drop'])} · "
        f"{span['start']:%m/%Y} → {end} · {duration}"
    )


def span_facts(span: dict) -> list[tuple[str, str]]:
    """Datas e durações da queda escolhida, na ordem da ficha."""
    if span["recovered"]:
        recovery = f"{span['end']:%d/%m/%Y}"
        to_recovery = format_duration(span["days_to_recovery"])
        total = format_duration(span["days"])
    else:
        recovery = "sem recuperação"
        to_recovery = "—"
        total = f"{format_duration(span['days'])}, até {span['end']:%d/%m/%Y}"
    return [
        ("Queda (pico ao fundo)", format_return_pct(span["drop"])),
        ("Pico", f"{span['start']:%d/%m/%Y}"),
        ("Fundo", f"{span['trough']:%d/%m/%Y}"),
        ("Recuperação do pico", recovery),
        ("Do pico ao fundo", format_duration(span["days_to_trough"])),
        ("Do fundo à recuperação", to_recovery),
        ("Duração total", total),
    ]


def build_facts_html(span: dict) -> str:
    """Ficha compacta da queda escolhida, logo abaixo dos botões."""
    cells = "".join(
        f'<div class="dd-fact{" dd-fact-main" if i == 0 else ""}"><span>{escape(label)}</span>'
        f"<b>{escape(value)}</b></div>"
        for i, (label, value) in enumerate(span_facts(span))
    )
    return (
        f'<div class="dd-facts"><div class="dd-facts-title">{span["position"]}ª maior queda</div>'
        f'<div class="dd-facts-grid">{cells}</div></div>'
    )


def _hover(title: str, span: dict) -> str:
    facts = dict(span_facts(span))
    return (
        f"<b>{title}</b> · {span['position']}ª maior queda<br>"
        f"Queda: {facts['Queda (pico ao fundo)']}<br>"
        f"Do pico ao fundo: {facts['Do pico ao fundo']}<br>"
        f"Do fundo à recuperação: {facts['Do fundo à recuperação']}<br>"
        f"Duração total: {facts['Duração total']}"
    )


def add_episode_highlight(fig: go.Figure, span: dict) -> None:
    """
    Fundo discreto do pico à recuperação (ou à última observação) e marcadores
    no pico, no fundo e na recuperação, com as durações no tooltip.
    """
    fig.add_vrect(
        x0=span["start"],
        x1=span["end"],
        fillcolor=HIGHLIGHT_COLOR,
        opacity=0.07,
        line_width=0,
        layer="below",
    )
    points = [
        (span["start"], 0.0, f"Pico em {span['start']:%d/%m/%Y}"),
        (span["trough"], span["drop"] * 100, f"Fundo em {span['trough']:%d/%m/%Y}"),
    ]
    if span["recovered"]:
        points.append((span["end"], 0.0, f"Recuperação em {span['end']:%d/%m/%Y}"))
    fig.add_trace(go.Scatter(
        x=[p[0] for p in points],
        y=[p[1] for p in points],
        mode="markers",
        marker=dict(size=9, color="#fff", line=dict(color=HIGHLIGHT_COLOR, width=2)),
        customdata=[_hover(p[2], span) for p in points],
        hovertemplate="%{customdata}<extra></extra>",
        hoverlabel=dict(bgcolor="#fff", bordercolor=HIGHLIGHT_COLOR, font=dict(color="#111"), align="left"),
        showlegend=False,
        name="Queda em destaque",
    ))


DRAWDOWN_CSS = f"""
<style>
.st-key-{PILLS_KEY} [data-testid="stWidgetLabel"] p {{ font-size: .78rem; font-weight: 700; letter-spacing: .08em;
    text-transform: uppercase; color: #475569; }}
.st-key-{PILLS_KEY} [data-testid="stButtonGroup"] button[aria-checked] {{ border-radius: 0 !important; border: 1px solid #d6d3cc !important;
    background: #fff !important; padding: 6px 12px !important; font-variant-numeric: tabular-nums;
    box-shadow: none !important; }}
.st-key-{PILLS_KEY} [data-testid="stButtonGroup"] button[aria-checked]:hover {{ border-color: {HIGHLIGHT_COLOR} !important; }}
.st-key-{PILLS_KEY} [data-testid="stButtonGroup"] button[aria-checked="true"] {{ background: #fdf2f2 !important;
    border-color: {HIGHLIGHT_COLOR} !important; box-shadow: inset 3px 0 0 {HIGHLIGHT_COLOR} !important;
    color: {HIGHLIGHT_COLOR} !important; }}
.dd-facts {{ border: 1px solid #e4e1da; background: #fff; margin: 4px 0 10px; }}
.dd-facts-title {{ padding: 8px 14px; border-bottom: 1px solid #e4e1da; color: {HIGHLIGHT_COLOR}; font-size: .72rem;
    font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }}
.dd-facts-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); }}
.dd-fact:last-child {{ grid-column: span 2; }}
@media (max-width: 760px) {{ .dd-facts-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
.dd-fact {{ padding: 10px 14px; border-right: 1px solid #f1efe9; border-bottom: 1px solid #f1efe9; }}
.dd-fact span {{ display: block; color: #64748b; font-size: .72rem; font-weight: 600; }}
.dd-fact b {{ display: block; color: #111; font-size: .92rem; font-variant-numeric: tabular-nums; margin-top: 2px; }}
.dd-fact-main b {{ color: {HIGHLIGHT_COLOR}; font-size: 1.1rem; }}
</style>
"""
