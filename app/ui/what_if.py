"""
Bloco "Se você tivesse investido" da Simulação de Aportes.

Frase em destaque, indicadores em fileira e a nota de rodapé que deixa
claras as premissas (só variação de preço). Os números vêm de
core.simulation.what_if; aqui está apenas a apresentação.
"""

from html import escape
from typing import Mapping

import pandas as pd

from core.formatters import format_return_pct

WHAT_IF_FOOTNOTE = (
    "* Considera apenas a variação do preço de fechamento entre a data da "
    "compra e o último dado disponível. Não inclui dividendos, juros sobre "
    "capital próprio, custos, impostos, câmbio nem inflação. Resultado "
    "passado não indica resultado futuro."
)

WHAT_IF_HOW_TO_READ = (
    "**Como ler:** escolha um valor e há quanto tempo ele teria sido aplicado. "
    "O sistema compra o ativo no primeiro pregão a partir dessa data, sem "
    "novos aportes, e calcula quanto esse valor valeria no último dado "
    "disponível. O *pior* e o *melhor momento* mostram quanto o mesmo valor "
    "chegou a valer no caminho, ou seja, as oscilações que quem tivesse "
    "investido teria atravessado."
)

WHAT_IF_CSS = """
<style>
.wi-box { margin: .4rem 0 .9rem; padding: 22px 26px; background: #FFFFFF; border: 1px solid #2A2A2A;
    border-left: 5px solid #C8102E; box-shadow: 0 8px 22px rgba(17, 17, 17, .07); }
.wi-kicker { color: #C8102E; font-size: .7rem; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; }
.wi-sentence { margin: 8px 0 0; color: #1f1f1f; font-size: 1.3rem; line-height: 1.55; }
.wi-sentence b { color: #111111; }
.wi-final { font-size: 1.9rem; font-weight: 800; letter-spacing: -.02em; white-space: nowrap; }
.wi-up { color: #15803D !important; }
.wi-down { color: #B91C1C !important; }
.wi-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 18px;
    border: 1px solid #E4E1DA; }
.wi-cell { padding: 10px 14px; border-right: 1px solid #E4E1DA; border-bottom: 1px solid #E4E1DA; }
.wi-cell span { display: block; color: #5F5F5F; font-size: .66rem; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; }
.wi-cell b { display: block; margin-top: 3px; color: #111111; font-size: 1.05rem; font-weight: 700; }
.wi-cell small { display: block; color: #5F5F5F; font-size: .76rem; }
@media (max-width: 760px) { .wi-grid { grid-template-columns: 1fr; } .wi-final { white-space: normal; } }
.wi-note { margin-top: 14px; color: #5F5F5F; font-size: .8rem; line-height: 1.5; }
</style>
"""


def format_money(value: float, prefix: str = "") -> str:
    """Valor no padrão brasileiro com o prefixo da moeda (ex.: R$ 1.234,56)."""
    text = f"{abs(float(value)):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    sign = "-" if float(value) < 0 else ""
    return f"{sign}{prefix}{text}"


def _date(value) -> str:
    return pd.Timestamp(value).strftime("%d/%m/%Y")


def _cell(label: str, value: str, note: str = "", tone: str = "") -> str:
    css = f' class="{tone}"' if tone else ""
    small = f"<small>{escape(note)}</small>" if note else ""
    return f'<div class="wi-cell"><span>{escape(label)}</span><b{css}>{escape(value)}</b>{small}</div>'


def build_what_if_html(
    result: Mapping[str, object],
    *,
    symbol: str,
    period_label: str,
    prefix: str = "",
) -> str:
    """
    HTML do bloco. `period_label` completa a frase "há ..." (ex.: "1 ano");
    vazio quando a data foi escolhida pelo usuário.
    """
    gain = float(result["Resultado"])
    tone = "wi-up" if gain > 0 else "wi-down" if gain < 0 else ""
    when = f"há <b>{escape(period_label)}</b> (em {_date(result['Data da compra'])})" if period_label \
        else f"em <b>{_date(result['Data da compra'])}</b>"
    annual = result["Retorno anualizado"]

    sentence = (
        f"Se você tivesse investido <b>{escape(format_money(result['Valor investido'], prefix))}</b> "
        f"em <b>{escape(symbol)}</b> {when}, no último dado disponível "
        f"({_date(result['Data final'])}) você teria "
        f'<span class="wi-final {tone}">{escape(format_money(result["Valor final"], prefix))}</span>*'
    )
    cells = "".join([
        _cell("Ganho ou perda", format_money(gain, "+" + prefix if gain > 0 else prefix), tone=tone),
        _cell("Variação total", format_return_pct(result["Retorno total"]), tone=tone),
        _cell(
            "Equivale a, ao ano",
            format_return_pct(annual) if annual is not None else "—",
            "" if annual is not None else "prazo menor que 1 ano",
        ),
        _cell("Pior momento", format_money(result["Menor valor"], prefix), f"em {_date(result['Data do menor valor'])}"),
        _cell("Melhor momento", format_money(result["Maior valor"], prefix), f"em {_date(result['Data do maior valor'])}"),
        _cell(
            "Preço na compra → no fim",
            f"{format_money(result['Preço na compra'])} → {format_money(result['Preço final'])}",
            "na moeda de cotação",
        ),
    ])

    return (
        '<div class="wi-box"><div class="wi-kicker">Resultado hipotético · aplicação única</div>'
        f'<p class="wi-sentence">{sentence}</p><div class="wi-grid">{cells}</div>'
        f'<div class="wi-note">{escape(WHAT_IF_FOOTNOTE)}</div></div>'
    )
