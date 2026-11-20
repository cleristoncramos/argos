"""
Tabela "Maiores quedas e recuperação" da página Risco e Retorno (A7).

Prepara os episódios de core/drawdown_episodes.py para o componente padrão
de app/ui/tables.py e reúne os textos explicativos.
"""

import pandas as pd

from core.formatters import format_return_pct

NOT_RECOVERED = "não recuperado até a última observação disponível"

# Espaço que não quebra: mantém "(≈ 5 meses)" na mesma linha da célula.
NBSP = "\u00a0"

HEADER_LABELS = {
    "Nº": "Nº",
    "Queda": "Queda (pico ao fundo)",
    "Pico": "Início da queda (pico)",
    "Fundo": "Fundo",
    "Recuperação": "Recuperação do pico",
    "Até o fundo": "Do pico ao fundo",
    "Fundo à recuperação": "Do fundo à recuperação",
    "Total": "Duração total",
}

DRAWDOWN_TABLE_NOTES = (
    "**Como ler:** o *início da queda* é o pico anterior; o *fundo* é o menor "
    "valor antes de o preço voltar ao pico; a *recuperação* é a primeira data em "
    "que o preço igualou ou superou o pico. Durações em **dias corridos** entre "
    "essas datas. Quando o preço não voltou ao pico, a duração conta até a última "
    "observação, sem estimar quando a recuperação ocorreria. Considera apenas o "
    "preço de fechamento, sem dividendos."
)

_CENTER = "text-align:center;white-space:nowrap;font-variant-numeric:tabular-nums;"
_WRAP = "text-align:center;font-variant-numeric:tabular-nums;"
_MUTED = _WRAP + "color:#991b1b;font-style:italic;"

FREQUENCY_NOUNS = {
    "Diário": "diários",
    "Semanal": "semanais",
    "Mensal": "mensais",
    "Semestral": "semestrais",
    "Anual": "anuais",
}


def drawdown_intro(frequency: str, top: int) -> str:
    """Texto que explica a base da tabela (a frequência escolhida)."""
    noun = FREQUENCY_NOUNS.get(frequency, "do período")
    return (
        f"As {top} maiores quedas do período, medidas nos **fechamentos {noun}** "
        "(a frequência escolhida na barra lateral), e quanto tempo o preço levou "
        "para voltar ao pico anterior. Com frequências mais longas, as datas e as "
        "durações ficam aproximadas à resolução da frequência."
    )


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


def build_drawdown_display(episodes: pd.DataFrame) -> pd.DataFrame:
    """Colunas prontas para exibição, na ordem de `HEADER_LABELS`."""
    def recovery(row) -> str:
        if row["Recuperada"]:
            return row["Recuperação"].strftime("%d/%m/%Y")
        return NOT_RECOVERED

    def total(row) -> str:
        text = format_duration(row["Dias em queda"])
        return text if row["Recuperada"] else f"{text}, até a última observação"

    return pd.DataFrame({
        "Nº": [f"{i}ª" for i in range(1, len(episodes) + 1)],
        "Queda": episodes["Queda"],
        "Pico": episodes["Pico"].dt.strftime("%d/%m/%Y"),
        "Fundo": episodes["Fundo"].dt.strftime("%d/%m/%Y"),
        "Recuperação": episodes.apply(recovery, axis=1),
        "Até o fundo": episodes["Dias até o fundo"].map(format_duration),
        "Fundo à recuperação": episodes["Dias do fundo à recuperação"].map(format_duration),
        "Total": episodes.apply(total, axis=1),
    })


def drop_cell(value) -> tuple[str, str]:
    return format_return_pct(value), _CENTER + "color:#991b1b;font-weight:600;"


def recovery_cell(value) -> tuple[str, str]:
    return str(value), (_MUTED if value == NOT_RECOVERED else _CENTER)


def text_cell(value) -> tuple[str, str]:
    return str(value), _WRAP


def number_cell(value) -> tuple[str, str]:
    return str(value), _CENTER + "font-weight:700;color:#475569;"


FORMATTERS = {
    "Nº": number_cell,
    "Queda": drop_cell,
    "Pico": text_cell,
    "Fundo": text_cell,
    "Recuperação": recovery_cell,
    "Até o fundo": text_cell,
    "Fundo à recuperação": text_cell,
    "Total": text_cell,
}


# -------------------------------------------------------
# Destaque de uma queda no gráfico de drawdown (pedido do orientador)
# -------------------------------------------------------
HIGHLIGHT_COLOR = "#991b1b"
HIGHLIGHT_PROMPT = "Ver no gráfico uma das maiores quedas"
HIGHLIGHT_HELP = (
    "Clique em uma queda para sombrear no gráfico o período do pico à recuperação. "
    "Clique de novo para ocultar."
)


def span_label(span: dict) -> str:
    """Rótulo curto do botão: "1ª · −76,63% · 08/11/2021 → 04/03/2024"."""
    end = span["end"].strftime("%d/%m/%Y") if span["recovered"] else "sem recuperação"
    return f"{span['position']}ª · {format_return_pct(span['drop'])} · {span['start']:%d/%m/%Y} → {end}"


def span_caption(span: dict) -> str:
    """Frase sob o gráfico que descreve o período destacado."""
    text = (
        f"Em destaque, a {span['position']}ª maior queda: do pico em {span['start']:%d/%m/%Y} "
        f"ao fundo em {span['trough']:%d/%m/%Y} ({format_return_pct(span['drop'])})"
    )
    if span["recovered"]:
        return text + f", com recuperação em {span['end']:%d/%m/%Y}; {format_duration(span['days'])} no total."
    return text + f"; sem recuperação até a última observação, {span['end']:%d/%m/%Y}."


def add_episode_highlight(fig, span: dict) -> None:
    """Fundo discreto do pico à recuperação (ou à última observação) no gráfico."""
    fig.add_vrect(
        x0=span["start"],
        x1=span["end"],
        fillcolor=HIGHLIGHT_COLOR,
        opacity=0.08,
        line_width=0,
        layer="below",
        annotation_text=f"{span['position']}ª queda · {format_return_pct(span['drop'])}",
        annotation_position="top left",
        annotation_font=dict(size=11, color=HIGHLIGHT_COLOR),
    )
