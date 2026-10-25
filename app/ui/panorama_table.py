"""
Textos e tabela da página "Panorama do Catálogo" (A3).

Prepara a tabela de core/panorama.py para o componente padrão de
app/ui/tables.py. A tabela começa ordenada por nome e não destaca nenhum
ativo; as cores indicam apenas o sinal da variação.
"""

import pandas as pd

from core.formatters import format_return_pct
from core.panorama import STATUS_NO_DATA, STATUS_RATE

PANORAMA_NOTICE = (
    "**A ordem da tabela não é uma recomendação.** O panorama descreve como os "
    "preços se comportaram no período escolhido. Variação passada não indica "
    "variação futura, e cada linha mostra o retorno ao lado da volatilidade e da "
    "queda máxima, porque altas maiores costumam vir acompanhadas de oscilações e "
    "quedas maiores."
)

PANORAMA_NOTES = (
    "**Como ler:** *variação no período* compara o último fechamento com o primeiro "
    "do período; *variação em 12 meses* usa os últimos 12 meses; *volatilidade "
    "anualizada* mede a intensidade das oscilações diárias (√252); *queda máxima* é a "
    "maior queda de um pico até um fundo no período. **\\*** O histórico do ativo "
    "começa depois do início pedido; as métricas valem para o trecho disponível. "
    "\"—\" indica dado indisponível, nunca zero. Considera apenas o preço de "
    "fechamento, sem dividendos."
)

RATE_NOTE = (
    "Taxas de juros (yields) aparecem sem variação, volatilidade e queda: a variação "
    "percentual do nível da taxa não equivale ao retorno de um título."
)

SORT_OPTIONS = {
    "Nome": "Nome",
    "Variação no período": "Variação no período",
    "Variação em 12 meses": "Variação em 12 meses",
    "Volatilidade anualizada": "Volatilidade anualizada",
    "Queda máxima": "Queda máxima",
    "Início do histórico": "Início",
}

HEADER_LABELS = {
    "Ativo": "Ativo",
    "Variação no período": "Variação no período",
    "Variação em 12 meses": "Variação em 12 meses",
    "Volatilidade anualizada": "Volatilidade anualizada",
    "Queda máxima": "Queda máxima",
    "Histórico": "Dados desde",
    "Alertas": "Alertas de dados",
}

_CENTER = "text-align:center;white-space:nowrap;font-variant-numeric:tabular-nums;"


def asset_label(name: str, ticker: str) -> str:
    """Nome e ticker, sem repetir o ticker quando ele já está no nome (ex.: BIL)."""
    if f"({ticker.split('.')[0].lstrip('^')})" in name:
        return name
    return f"{name} ({ticker})"


def build_panorama_display(table: pd.DataFrame) -> pd.DataFrame:
    """Colunas prontas para exibição, na ordem de `HEADER_LABELS`."""
    def history(row) -> object:
        if row["Status"] == STATUS_NO_DATA:
            return None
        text = row["Início"].strftime("%d/%m/%Y")
        return f"{text}*" if row["Começa depois"] else text

    def alerts(row) -> object:
        return None if row["Status"] == STATUS_NO_DATA else int(row["Alertas"])

    return pd.DataFrame({
        "Ativo": [asset_label(n, t) for n, t in zip(table["Nome"], table["Ticker"])],
        "Variação no período": table["Variação no período"],
        "Variação em 12 meses": table["Variação em 12 meses"],
        "Volatilidade anualizada": table["Volatilidade anualizada"],
        "Queda máxima": table["Queda máxima"],
        "Histórico": table.apply(history, axis=1),
        "Alertas": table.apply(alerts, axis=1),
    })


def _is_empty(value) -> bool:
    return value is None or (isinstance(value, float) and pd.isna(value))


def signed_cell(value) -> tuple[str, str]:
    """Variação com sinal; a cor indica só o sinal."""
    if _is_empty(value):
        return "—", _CENTER
    text = format_return_pct(value)
    if value > 0:
        return f"+{text}", _CENTER + "color:#166534;"
    if value < 0:
        return text, _CENTER + "color:#991b1b;"
    return text, _CENTER


def plain_pct_cell(value) -> tuple[str, str]:
    return ("—" if _is_empty(value) else format_return_pct(value)), _CENTER


def text_cell(value) -> tuple[str, str]:
    return ("—" if _is_empty(value) else str(value)), _CENTER


FORMATTERS = {
    "Ativo": lambda v: (str(v), "text-align:left;font-weight:600;"),
    "Variação no período": signed_cell,
    "Variação em 12 meses": signed_cell,
    "Volatilidade anualizada": plain_pct_cell,
    "Queda máxima": plain_pct_cell,
    "Histórico": text_cell,
    "Alertas": text_cell,
}


def unavailable_assets(table: pd.DataFrame) -> list[str]:
    """Tickers sem dados na consulta (falhas parciais)."""
    return list(table.loc[table["Status"] == STATUS_NO_DATA, "Ticker"])


def has_rates(table: pd.DataFrame) -> bool:
    return bool((table["Status"] == STATUS_RATE).any())
