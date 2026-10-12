"""
Contextos da explicação assistida (7B) montados a partir de resultados que as
telas do Argos já calcularam. Módulo puro: sem Streamlit e sem rede.

Os ids, rótulos, unidades e casas decimais seguem os casos validados na 7A
(`experiments/llm_7a/build_cases.py`). Cada função devolve o pacote de contexto
ou None quando não há métricas finitas para explicar.
"""

from __future__ import annotations

import math
from typing import Iterable, Optional

import pandas as pd

from core import llm_context as lc
from core.risk_metrics import build_risk_summary


def _iso(value) -> str:
    return pd.Timestamp(value).date().isoformat()


def _pct(value: float) -> float:
    return float(value) * 100


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _number_text(value: float) -> str:
    return f"{value:g}".replace(".", ",")


def _metrics(specs: Iterable[tuple]) -> list:
    """Cria só as métricas cujo valor é finito: (id, rótulo, valor, unidade, casas)."""
    return [lc.metric(*spec) for spec in specs if _finite(spec[2])]


def _names(symbol: str, name: Optional[str]) -> Optional[dict]:
    return {symbol.upper(): name} if name else None


def _summary(df: pd.DataFrame, annualization_factor: float, risk_free_pct: float) -> Optional[dict]:
    try:
        return build_risk_summary(df, "Value", float(annualization_factor), float(risk_free_pct) / 100)
    except ValueError:  # preço menor ou igual a zero: a tela já explica o motivo
        return None


def _risk_specs(summary: dict, risk_free_pct: float) -> list:
    return [
        ("retorno_total", "Retorno total no período", _pct(summary["Retorno total"]), "%", 2),
        ("retorno_medio", "Retorno médio por observação", _pct(summary["Retorno médio"]), "%", 3),
        ("volatilidade", "Volatilidade anualizada", _pct(summary["Volatilidade"]), "%", 1),
        ("drawdown_maximo", "Queda máxima desde um pico (drawdown)", _pct(summary["Drawdown máximo"]), "%", 1),
        ("percentual_positivo", "Percentual de observações positivas", _pct(summary["Percentual positivo"]), "%", 1),
        (
            "sharpe",
            f"Índice de Sharpe (taxa livre de risco {_number_text(risk_free_pct)}%)",
            summary["Sharpe"], "", 2,
        ),
    ]


def individual_context(
    df: pd.DataFrame,
    symbol: str,
    frequency: str,
    annualization_factor: float,
    *,
    summary: Optional[dict] = None,
    name: Optional[str] = None,
    notes: Iterable[str] = (),
) -> Optional[dict]:
    """Análise individual: retorno total, retorno médio e volatilidade."""
    summary = summary if summary is not None else _summary(df, annualization_factor, 0.0)
    if summary is None:
        return None
    metrics = _metrics(_risk_specs(summary, 0.0)[:3])
    if not metrics:
        return None
    return lc.build_context(
        analysis_type="analise_individual",
        assets=[symbol],
        period_start=_iso(df["Date"].iloc[0]),
        period_end=_iso(df["Date"].iloc[-1]),
        frequency=frequency,
        n_observations=len(df),
        metrics=metrics,
        asset_names=_names(symbol, name),
        notes=notes,
        limitation_flags=lc.derive_limitation_flags(n_observations=len(df), frequency=frequency),
    )


def risk_context(
    df: pd.DataFrame,
    symbol: str,
    frequency: str,
    annualization_factor: float,
    risk_free_pct: float,
    *,
    summary: Optional[dict] = None,
    name: Optional[str] = None,
    notes: Iterable[str] = (),
) -> Optional[dict]:
    """Risco e retorno: as seis métricas da tela (Sharpe só se for finito)."""
    summary = summary if summary is not None else _summary(df, annualization_factor, risk_free_pct)
    if summary is None:
        return None
    metrics = _metrics(_risk_specs(summary, risk_free_pct))
    if not metrics:
        return None
    return lc.build_context(
        analysis_type="risco_retorno",
        assets=[symbol],
        period_start=_iso(df["Date"].iloc[0]),
        period_end=_iso(df["Date"].iloc[-1]),
        frequency=frequency,
        n_observations=len(df),
        metrics=metrics,
        asset_names=_names(symbol, name),
        notes=notes,
        limitation_flags=lc.derive_limitation_flags(n_observations=len(df), frequency=frequency),
        extra_numbers=[float(risk_free_pct)],
    )


def simulation_context(
    paths: dict,
    symbol: str,
    frequency: str,
    unit: str,
    amount: float,
    every: int,
    periodic: dict,
    lump_sum: dict,
    *,
    name: Optional[str] = None,
) -> Optional[dict]:
    """Simulação histórica de aportes: totais, valores finais e retornos das duas estratégias."""
    dates = paths["periodic"]["Date"]
    n_obs = len(paths["periodic"])
    metrics = _metrics([
        ("total_investido", "Total investido", periodic["Total investido"], unit, 0),
        ("valor_final_periodico", "Valor final dos aportes periódicos", periodic["Valor final"], unit, 0),
        ("retorno_periodico", "Retorno dos aportes periódicos", _pct(periodic["Retorno sobre o investido"]), "%", 2),
        ("valor_final_unico", "Valor final do aporte único", lump_sum["Valor final"], unit, 0),
        ("retorno_unico", "Retorno do aporte único", _pct(lump_sum["Retorno sobre o investido"]), "%", 2),
    ])
    if not metrics:
        return None
    amount_text = f"{amount:g}"
    return lc.build_context(
        analysis_type="simulacao",
        assets=[symbol],
        period_start=_iso(dates.iloc[0]),
        period_end=_iso(dates.iloc[-1]),
        frequency=frequency,
        n_observations=n_obs,
        metrics=metrics,
        asset_names=_names(symbol, name),
        notes=[
            f"Simulação hipotética com aportes de {amount_text} a cada {int(every)} observações; "
            "não considera custos nem impostos."
        ],
        limitation_flags=lc.derive_limitation_flags(n_observations=n_obs, frequency=frequency),
        extra_numbers=[float(amount), float(every)],
    )


def _pct_or_nan(value) -> float:
    try:
        return _pct(value)
    except (TypeError, ValueError):
        return float("nan")


def _pair_correlation(matrix, a: str, b: str) -> float:
    try:
        return float(matrix.loc[a, b])
    except (KeyError, TypeError, ValueError, AttributeError):
        return float("nan")


def comparison_context(
    summary: pd.DataFrame,
    correlation_matrix,
    asset_data: dict,
    frequency: str,
    *,
    names: Optional[dict] = None,
    notes: Iterable[str] = (),
) -> Optional[dict]:
    """
    Comparação de EXATAMENTE dois ativos (o formato validado na 7A): retorno total
    de cada um e correlação. Com outra quantidade de ativos devolve None.
    """
    tickers = [str(t) for t in summary["Ativo"].tolist()]
    if len(tickers) != 2:
        return None
    a, b = tickers
    returns = dict(zip(summary["Ativo"].astype(str), summary["Retorno total"]))
    metrics = _metrics([
        ("retorno_total_a", f"Retorno total de {a}", _pct_or_nan(returns[a]), "%", 2),
        ("retorno_total_b", f"Retorno total de {b}", _pct_or_nan(returns[b]), "%", 2),
        ("correlacao", "Correlação dos retornos nos dias em comum", _pair_correlation(correlation_matrix, a, b), "", 2),
    ])
    if not metrics:
        return None
    starts = [pd.Timestamp(asset_data[t]["Date"].iloc[0]) for t in tickers]
    ends = [pd.Timestamp(asset_data[t]["Date"].iloc[-1]) for t in tickers]
    n_obs = int(summary["Observações"].min())
    return lc.build_context(
        analysis_type="comparacao",
        assets=tickers,
        period_start=_iso(min(starts)),
        period_end=_iso(max(ends)),
        frequency=frequency,
        n_observations=n_obs,
        metrics=metrics,
        asset_names={t: n for t, n in (names or {}).items() if n} or None,
        notes=notes,
        limitation_flags=lc.derive_limitation_flags(n_observations=n_obs, frequency=frequency),
    )


def window_context(
    stats: dict,
    entry: str,
    exit_: str,
    symbol: str,
    period_start,
    period_end,
    n_closes: int,
    *,
    incomplete_month: bool = False,
    name: Optional[str] = None,
) -> Optional[dict]:
    """Janela sazonal (fechamento de um mês até o fechamento de outro): média, mediana e anos positivos."""
    n_years = int(stats["N"])
    if n_years == 0:
        return None
    metrics = _metrics([
        ("media", "Média dos anos", stats["Média"], "%", 2),
        ("mediana", "Mediana dos anos", stats["Mediana"], "%", 2),
        ("anos_positivos", "Anos positivos", stats["Anos positivos (%)"], "%", 0),
    ])
    if not metrics:
        return None
    return lc.build_context(
        analysis_type="sazonalidade",
        assets=[symbol],
        period_start=_iso(period_start),
        period_end=_iso(period_end),
        frequency="Mensal",
        n_observations=int(n_closes),
        metrics=metrics,
        asset_names=_names(symbol, name),
        notes=[f"Janela: fechamento de {str(entry).lower()} até o fechamento de {str(exit_).lower()}. N = {n_years} anos."],
        limitation_flags=lc.derive_limitation_flags(
            n_observations=int(n_closes), frequency="Mensal", n_years=n_years, incomplete_month=incomplete_month,
        ),
        extra_numbers=[n_years],
    )
