"""
Bloco "Maiores altas e quedas" da Análise Individual (A8).

Prepara as tabelas de core/extreme_moves.py para o componente padrão de
app/ui/tables.py e reúne os textos. Os textos descrevem os extremos
observados; não afirmam quanto eles explicam do resultado total.
"""

import pandas as pd

from core.formatters import format_number_br, format_return_pct

FREQUENCY_NOUNS = {
    "Diário": "variações diárias",
    "Semanal": "variações semanais",
    "Mensal": "variações mensais",
    "Semestral": "variações semestrais",
    "Anual": "variações anuais",
}

HEADER_LABELS = {
    "Período": "Período",
    "Variação": "Variação",
    "Entre": "Fechamentos comparados",
}

EXTREMES_NOTES = (
    "Cada variação compara o fechamento de um período com o do período anterior, "
    "na frequência escolhida. A tabela descreve os extremos observados; ela não "
    "mede quanto esses períodos contribuíram para o resultado total. **(em "
    "andamento)** indica o último período, que ainda não terminou nos dados. "
    "Considera apenas o preço de fechamento, sem dividendos."
)

RATE_NOTE = (
    "Para taxas de juros, a variação percentual do nível da taxa não equivale ao "
    "retorno de um título; por isso as maiores altas e quedas não são exibidas."
)

_CENTER = "text-align:center;white-space:nowrap;font-variant-numeric:tabular-nums;"
# As tabelas ficam lado a lado: período e datas podem quebrar linha na célula.
_WRAP = "text-align:center;font-variant-numeric:tabular-nums;"


def extremes_intro(frequency: str, counts: dict) -> str:
    """Resumo descritivo: quantas variações foram positivas, negativas e nulas."""
    plural = FREQUENCY_NOUNS.get(frequency, "variações")
    total = counts["total"]
    up, down, flat = counts["up"], counts["down"], counts["flat"]
    share = f"{up / total * 100:.0f}%" if total else "—"
    text = (
        f"No período carregado, **{up} de {total} {plural}** foram positivas ({share}) "
        f"e {down} foram negativas"
    )
    return text + (f"; {flat} sem variação." if flat else ".")


def build_extremes_display(moves: pd.DataFrame) -> pd.DataFrame:
    """Colunas prontas para exibição, na ordem de `HEADER_LABELS`."""
    def period(row) -> str:
        return f"{row['Período']} (em andamento)" if row["Parcial"] else row["Período"]

    def between(row) -> str:
        return (
            f"{row['Data inicial']:%d/%m/%Y} ({format_number_br(row['Valor inicial'])}) → "
            f"{row['Data final']:%d/%m/%Y} ({format_number_br(row['Valor final'])})"
        )

    if moves.empty:
        return pd.DataFrame(columns=list(HEADER_LABELS))
    return pd.DataFrame({
        "Período": moves.apply(period, axis=1),
        "Variação": moves["Variação"],
        "Entre": moves.apply(between, axis=1),
    })


def change_cell(value) -> tuple[str, str]:
    text = format_return_pct(value)
    if value > 0:
        return f"+{text}", _CENTER + "color:#166534;font-weight:600;"
    return text, _CENTER + "color:#991b1b;font-weight:600;"


FORMATTERS = {
    "Período": lambda v: (str(v), "text-align:left;font-weight:600;"),
    "Variação": change_cell,
    "Entre": lambda v: (str(v), _WRAP),
}
