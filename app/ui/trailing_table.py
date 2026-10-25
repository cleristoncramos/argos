"""
Tabela "Variação por prazo" da Análise Individual (A1).

Prepara a tabela de core/trailing_returns.py para o componente padrão de
app/ui/tables.py e reúne os textos que explicam a base e as colunas.
"""

import pandas as pd

from core.formatters import format_number_br, format_return_pct

NOT_APPLICABLE = "não se aplica"

TRAILING_NOTES = (
    "**Variação acumulada** é a mudança total do preço no prazo. **Taxa "
    "equivalente ao ano** é a taxa anual constante que levaria à mesma variação "
    "acumulada; só é calculada para prazos de 1 ano ou mais, com os dias "
    "efetivamente decorridos. **\\*** Início ajustado: o período carregado começa "
    "alguns dias depois da data-alvo, e a janela usa o primeiro dado disponível. "
    "A tabela usa os **fechamentos diários**; o \"Retorno Total\" acima usa os "
    "valores agregados pela frequência escolhida (o primeiro valor é o fechamento "
    "do primeiro período), por isso os dois números podem diferir. Considera apenas "
    "o preço de fechamento, sem dividendos, custos ou inflação."
)

RATE_NOTE = (
    "Para taxas de juros, a variação percentual do nível da taxa não equivale ao "
    "retorno de um título; por isso a tabela de variação por prazo não é exibida."
)

HEADER_LABELS = {
    "Janela": "Prazo",
    "Início": "Início",
    "Fim": "Fim",
    "Valor inicial": "Valor no início",
    "Valor final": "Valor no fim",
    "Variação": "Variação acumulada",
    "Taxa": "Taxa equivalente ao ano",
}

_CENTER = "text-align:center;white-space:nowrap;font-variant-numeric:tabular-nums;"
_MUTED = _CENTER + "color:#64748b;font-style:italic;"


def trailing_intro(start: pd.Timestamp, end: pd.Timestamp, rate: bool = False) -> str:
    """Texto que deixa explícita a base usada pela tabela."""
    subject = "o nível da taxa" if rate else "o preço"
    return (
        f"Quanto {subject} variou em prazos fixos até a última observação "
        f"({end:%d/%m/%Y}). **Base: o período carregado na barra lateral**, de "
        f"{start:%d/%m/%Y} a {end:%d/%m/%Y}. Prazos mais longos que esse período "
        "aparecem como \"—\"; para vê-los, amplie o período e carregue os dados de novo."
    )


def build_trailing_display(table: pd.DataFrame) -> pd.DataFrame:
    """Colunas prontas para exibição a partir de `trailing_returns`."""
    def start_label(row) -> object:
        if not row["Disponível"]:
            return None
        text = row["Data inicial"].strftime("%d/%m/%Y")
        return f"{text}*" if row["Ajustada"] else text

    def rate_value(row) -> object:
        if not row["Disponível"]:
            return None
        if pd.isna(row["Taxa anual"]):
            return NOT_APPLICABLE
        return row["Taxa anual"]

    return pd.DataFrame({
        "Janela": table["Janela"],
        "Início": table.apply(start_label, axis=1),
        "Fim": [d.strftime("%d/%m/%Y") if ok else None for d, ok in zip(table["Data final"], table["Disponível"])],
        "Valor inicial": table["Valor inicial"],
        "Valor final": [v if ok else None for v, ok in zip(table["Valor final"], table["Disponível"])],
        "Variação": table["Variação"],
        "Taxa": table.apply(rate_value, axis=1),
    })


def text_cell(value) -> tuple[str, str]:
    return ("—" if value is None or pd.isna(value) else str(value)), _CENTER


def value_cell(value) -> tuple[str, str]:
    return ("—" if value is None or pd.isna(value) else format_number_br(value)), _CENTER


def change_cell(value) -> tuple[str, str]:
    """Variação em fração, com sinal e cor; "—" quando indisponível."""
    if value is None or pd.isna(value):
        return "—", _CENTER
    text = format_return_pct(value)
    if value > 0:
        return f"+{text}", _CENTER + "color:#166534;font-weight:600;"
    if value < 0:
        return text, _CENTER + "color:#991b1b;font-weight:600;"
    return text, _CENTER


def rate_cell(value) -> tuple[str, str]:
    if isinstance(value, str):
        return value, _MUTED
    return change_cell(value)


FORMATTERS = {
    "Janela": lambda v: (str(v), "text-align:left;white-space:nowrap;font-weight:600;"),
    "Início": text_cell,
    "Fim": text_cell,
    "Valor inicial": value_cell,
    "Valor final": value_cell,
    "Variação": change_cell,
    "Taxa": rate_cell,
}
