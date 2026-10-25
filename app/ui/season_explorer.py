"""
Textos do bloco "Explorar anos e meses" da Análise Individual.

Transformam os resumos de core/seasonality.py em frases curtas, em
linguagem simples e descritiva (sem previsão nem recomendação). Ficam
fora da página para poderem ser testados.
"""

from typing import Iterable, Mapping

import pandas as pd

from core.analyzer import ORDERED_MONTHS

FULL_MONTH_NAMES = dict(zip(ORDERED_MONTHS, [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]))

YEARS_INTRO = (
    "Escolha um ou mais anos para ver, mês a mês, se a variação do preço "
    "nesses anos ficou **acima** ou **abaixo** da média de todos os anos do "
    "histórico carregado."
)

WINDOW_INTRO = (
    "Escolha um mês de partida e um mês de chegada. Para cada ano, o sistema "
    "calcula quanto o preço variou entre o fechamento desses dois meses e "
    "mostra em quantos anos essa variação foi positiva."
)

WINDOW_NOTE = (
    "Como é calculado: a variação vai do último preço do mês de partida ao "
    "último preço do mês de chegada. De setembro a outubro, por exemplo, é a "
    "variação de outubro. Intervalos de vários meses são compostos (não "
    "somados). Anos sem os dois fechamentos ficam de fora, e o mês em "
    "andamento não conta como mês completo."
)

PP_NOTE = (
    "**p.p. (pontos percentuais)** é a diferença direta entre duas "
    "porcentagens: se a média dos anos escolhidos foi 3% e a média de todos "
    "os anos foi 1%, a diferença é de 2 p.p."
)


def month_label(month: str) -> str:
    """Nome completo com inicial maiúscula (ex.: "Mar" -> "Março")."""
    name = FULL_MONTH_NAMES.get(month, str(month))
    return name[:1].upper() + name[1:]


def fmt_pct(value, signed: bool = True) -> str:
    """Percentual no padrão brasileiro (5.0 -> "+5,00%")."""
    if value is None or pd.isna(value):
        return "—"
    text = f"{value:+.2f}" if signed else f"{value:.2f}"
    return text.replace(".", ",") + "%"


def fmt_pp(value) -> str:
    """Diferença em pontos percentuais (1.5 -> "+1,50 p.p.")."""
    if value is None or pd.isna(value):
        return "—"
    return f"{value:+.2f}".replace(".", ",") + " p.p."


def years_label(years: Iterable[int]) -> str:
    """Lista de anos em texto ("2022", "2022 e 2023", "2021, 2022 e 2023")."""
    items = [str(int(y)) for y in years]
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " e " + items[-1]


def year_comparison_highlights(summary: pd.DataFrame) -> dict:
    """
    Contagens e extremos da diferença entre os anos escolhidos e a média
    geral, só com os meses que têm dado nos anos escolhidos.
    """
    diff = summary["Diferença (p.p.)"].dropna()
    above = diff[diff > 0]
    below = diff[diff < 0]
    return {
        "months": int(len(diff)),
        "above": int(len(above)),
        "below": int(len(below)),
        "largest_above": (above.idxmax(), float(above.max())) if not above.empty else None,
        "largest_below": (below.idxmin(), float(below.min())) if not below.empty else None,
    }


def describe_year_comparison(highlights: Mapping, years: Iterable[int]) -> str:
    """Frase-resumo da comparação dos anos escolhidos com a média geral."""
    years = list(years)
    label = years_label(years)
    subject = f"Em {label}" if len(years) == 1 else f"Na média de {label}"
    months = highlights["months"]

    if months == 0:
        return f"{subject}, não há meses com dado para comparar."

    text = (
        f"{subject}, a variação ficou **acima da média histórica em "
        f"{highlights['above']} de {months} meses** e abaixo em {highlights['below']}."
    )
    parts = []
    if highlights["largest_above"]:
        month, value = highlights["largest_above"]
        parts.append(f"a maior diferença para cima foi em **{FULL_MONTH_NAMES.get(month, month)}** ({fmt_pp(value)})")
    if highlights["largest_below"]:
        month, value = highlights["largest_below"]
        parts.append(f"a maior diferença para baixo foi em **{FULL_MONTH_NAMES.get(month, month)}** ({fmt_pp(value)})")
    if parts:
        joined = " e ".join(parts)
        text += " " + joined[:1].upper() + joined[1:] + "."
    return text


def window_label(entry: str, exit_: str) -> str:
    """Descrição da janela, indicando quando a chegada é no ano seguinte."""
    following = ORDERED_MONTHS.index(exit_) < ORDERED_MONTHS.index(entry)
    suffix = " do ano seguinte" if following else ""
    return (
        f"do fechamento de {FULL_MONTH_NAMES[entry]} ao fechamento de "
        f"{FULL_MONTH_NAMES[exit_]}{suffix}"
    )


def describe_window(stats: Mapping, entry: str, exit_: str) -> str:
    """Frase-resumo da variação entre dois meses ao longo dos anos."""
    n = int(stats["N"])
    if n == 0:
        return "Nenhum ano tem os dois fechamentos disponíveis para esse intervalo."

    positives = round(stats["Anos positivos (%)"] / 100 * n)
    label = window_label(entry, exit_)
    return (
        f"{label[:1].upper() + label[1:]}, o preço **subiu em {positives} de {n} "
        f"{'ano' if n == 1 else 'anos'}**. A variação média foi de "
        f"**{fmt_pct(stats['Média'])}** e a mediana, de **{fmt_pct(stats['Mediana'])}**."
    )


# ----------------------------------------------------------
# Células das tabelas (formato de app/ui/tables.py: texto e estilo)
# ----------------------------------------------------------
_CENTER = "text-align:center;white-space:nowrap;font-variant-numeric:tabular-nums;"


def pp_cell(value) -> tuple[str, str]:
    """Diferença em p.p., verde se positiva e vermelha se negativa."""
    if value is None or pd.isna(value):
        return "—", _CENTER
    color = "#166534" if value > 0 else "#991b1b" if value < 0 else "#334155"
    return fmt_pp(value), _CENTER + f"color:{color};font-weight:600;"


def pct_cell(value) -> tuple[str, str]:
    """Percentual com sinal, centralizado, verde ou vermelho conforme o sinal."""
    if value is None or pd.isna(value):
        return "—", _CENTER
    color = "#166534" if value > 0 else "#991b1b" if value < 0 else "#334155"
    return fmt_pct(value), _CENTER + f"color:{color};font-weight:600;"


def price_cell(value) -> tuple[str, str]:
    """Preço no padrão brasileiro, centralizado."""
    if value is None or pd.isna(value):
        return "—", _CENTER
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), _CENTER


def share_cell(value) -> tuple[str, str]:
    """Proporção já em percentual (66.7 -> "67%")."""
    if value is None or pd.isna(value):
        return "—", _CENTER
    return f"{value:.0f}%", _CENTER


def center_cell(value) -> tuple[str, str]:
    return ("—" if value is None else str(value)), _CENTER
