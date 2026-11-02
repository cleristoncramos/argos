"""
Diagnóstico de séries que impedem um cálculo.

Quando retorno, drawdown, Base 100 ou métricas de risco não podem ser
calculados, estas funções examinam a série de preços para explicar o motivo
real, com as datas e os valores envolvidos, em vez de uma mensagem genérica.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np
import pandas as pd

# Com menos de três preços há no máximo um retorno: não há variação a medir.
MIN_OBSERVATIONS = 3
MAX_LISTED_DATES = 5


@dataclass(frozen=True)
class Infeasibility:
    """Motivo pelo qual a série não permite o cálculo."""

    reason: str  # "empty", "short", "non_positive", "missing" ou "unknown"
    title: str
    explanation: str
    details: tuple[str, ...] = field(default_factory=tuple)
    suggestions: tuple[str, ...] = field(default_factory=tuple)


def _format_dates(dates: pd.Series) -> str:
    listed = [pd.Timestamp(d).strftime("%d/%m/%Y") for d in dates[:MAX_LISTED_DATES]]
    extra = len(dates) - len(listed)
    text = ", ".join(listed)
    return text + (f" e mais {extra}" if extra > 0 else "")


def _format_number(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def diagnose_series(
    dates: Iterable,
    values: Iterable,
    min_observations: int = MIN_OBSERVATIONS,
) -> Infeasibility | None:
    """
    Explica por que a série não permite calcular retornos e risco.

    Retorna None quando a série está apta: valores numéricos, todos
    maiores que zero e em quantidade suficiente.
    """
    frame = pd.DataFrame({
        "Date": pd.to_datetime(pd.Series(list(dates)), errors="coerce"),
        "Value": pd.to_numeric(pd.Series(list(values), dtype="object"), errors="coerce"),
    })
    frame["Value"] = frame["Value"].astype(float)
    finite = np.isfinite(frame["Value"])
    valid = frame[finite]

    if frame.empty or valid.empty:
        return Infeasibility(
            reason="empty",
            title="Não há preços válidos no período",
            explanation=(
                "A fonte não retornou nenhum preço de fechamento utilizável para o período "
                "escolhido, então não há série sobre a qual calcular as métricas."
            ),
            suggestions=(
                "Amplie o período ou escolha outra data de início.",
                "Confira o código do ativo (ações brasileiras terminam em .SA).",
            ),
        )

    non_positive = valid[valid["Value"] <= 0]
    if not non_positive.empty:
        lowest = non_positive.loc[non_positive["Value"].idxmin()]
        return Infeasibility(
            reason="non_positive",
            title="A série tem preços iguais ou abaixo de zero",
            explanation=(
                "Retorno percentual, drawdown e Base 100 dividem cada preço pelo anterior "
                "(ou pelo pico). Com preço zero ou negativo, essa divisão perde o sentido "
                "financeiro: não há como medir uma variação percentual a partir de um valor "
                "nulo ou negativo. Isso acontece em contratos futuros em situações extremas, "
                "como o petróleo WTI em abril de 2020."
            ),
            details=(
                f"{len(non_positive)} observação(ões) com preço ≤ 0: {_format_dates(non_positive['Date'])}.",
                f"Menor valor: {_format_number(lowest['Value'])} em "
                f"{pd.Timestamp(lowest['Date']).strftime('%d/%m/%Y')}.",
            ),
            suggestions=(
                "Escolha um período que não inclua essas datas.",
                "Compare com um ETF ou um índice do mesmo mercado, que não costumam ter preços negativos.",
            ),
        )

    missing = frame[~finite]
    if not missing.empty:
        return Infeasibility(
            reason="missing",
            title="A série tem datas sem preço de fechamento",
            explanation=(
                "Cada retorno compara um preço com o anterior; uma data sem fechamento "
                "interrompe a sequência e impede o cálculo. Isso costuma ocorrer quando o "
                "pregão do dia ainda não terminou (a fonte já informa a abertura, mas não o "
                "fechamento) ou quando a fonte não registrou o fechamento daquela data."
            ),
            details=(
                f"{len(missing)} data(s) sem fechamento: {_format_dates(missing['Date'].dropna())}.",
            ),
            suggestions=(
                "Tente novamente depois do fechamento do mercado.",
                "Encerre o período um dia antes da data indicada.",
            ),
        )

    if len(valid) < min_observations:
        return Infeasibility(
            reason="short",
            title="O período tem poucas observações",
            explanation=(
                f"São necessárias pelo menos {min_observations} observações para medir "
                "variações, volatilidade e quedas; com menos que isso, os números não teriam "
                "significado estatístico."
            ),
            details=(f"Observações disponíveis na frequência escolhida: {len(valid)}.",),
            suggestions=(
                "Amplie o período.",
                "Use uma frequência mais curta (por exemplo, diária em vez de mensal).",
            ),
        )

    return None


def unknown_infeasibility(error: Exception | str) -> Infeasibility:
    """Motivo genérico, quando a série parece válida mas o cálculo falhou."""
    return Infeasibility(
        reason="unknown",
        title="Os dados não passaram nas verificações do cálculo",
        explanation=(
            "A série tem preços válidos, mas alguma verificação de consistência do cálculo "
            "não foi atendida. Nenhum resultado foi exibido para não mostrar números incorretos."
        ),
        details=(f"Detalhe técnico: {error}",),
        suggestions=("Tente outro período ou outra frequência.",),
    )


def infeasibility_markdown(diagnosis: Infeasibility, symbol: str, what: str) -> str:
    """Mensagem completa em Markdown: o que falhou, por quê, os dados e o que fazer."""
    lines = [
        f"**Não foi possível calcular {what} para {symbol}: {diagnosis.title.lower()}.**",
        "",
        diagnosis.explanation,
    ]
    if diagnosis.details:
        lines += ["", "**O que foi encontrado nos dados**"]
        lines += [f"- {item}" for item in diagnosis.details]
    if diagnosis.suggestions:
        lines += ["", "**O que você pode fazer**"]
        lines += [f"- {item}" for item in diagnosis.suggestions]
    return "\n".join(lines)


def infeasibility_summary(diagnosis: Infeasibility, symbol: str) -> str:
    """Uma linha por ativo, para listas de ativos excluídos de uma comparação."""
    detail = f" ({diagnosis.details[0]})" if diagnosis.details else ""
    return f"{symbol}: {diagnosis.title.lower()}{detail}"
