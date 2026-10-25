"""
Referência de comparação sugerida para um ativo (A2).

Funções puras, sem Streamlit. Sugerem uma referência de mercado para
contextualizar a trajetória do ativo em Base 100 e alinham as duas séries
nas datas comuns. A referência serve apenas de contexto: não é meta, não
é calculado beta, regressão nem cruzamento (decisão N07). Quando não há
referência adequada, nenhuma é sugerida (detalhes em
docs/metodologia_de_calculo.md, seção 2.5).
"""

from dataclasses import dataclass
from typing import Mapping, Optional

import pandas as pd

from core.config import LONG_FREQUENCIES
from core.currency import currency_info, is_crypto

# Referências disponíveis, todas do catálogo.
BENCHMARKS = {
    "^BVSP": "Ibovespa",
    "^GSPC": "S&P 500",
    "BTC-USD": "Bitcoin",
    "GC=F": "Ouro (contrato futuro)",
}

REASONS = {
    "^BVSP": "o Ibovespa é o principal índice de ações da B3",
    "^GSPC": "o S&P 500 reúne 500 grandes empresas dos EUA",
    "BTC-USD": "o Bitcoin é a maior criptomoeda por capitalização",
    "GC=F": "o ativo acompanha o preço do ouro",
}

# Casos específicos do catálogo, decididos pela exposição do ativo.
TICKER_RULES = {
    "IVVB11.SA": "^GSPC",
    "HASH11.SA": "BTC-USD",
    "GOLD11.SA": "GC=F",
}

NO_REFERENCE_REASONS = {
    "brazil_fiis": (
        "não há índice de fundos imobiliários (IFIX) disponível na fonte de dados, "
        "e o Ibovespa, de ações, não representaria bem esse mercado"
    ),
    "default": "não há, no catálogo, uma referência que represente bem este ativo",
}


@dataclass(frozen=True)
class BenchmarkSuggestion:
    ticker: Optional[str]
    reason: str


def suggest_benchmark(ticker: str, asset: Optional[Mapping[str, str]] = None) -> BenchmarkSuggestion:
    """
    Referência sugerida para o ativo e o motivo, em linguagem simples.
    `asset` é o registro do catálogo (None para ticker digitado).
    """
    t = str(ticker or "").strip().upper()

    if t in BENCHMARKS:
        return BenchmarkSuggestion(None, "o próprio ativo é uma das referências disponíveis")

    if t in TICKER_RULES:
        ref = TICKER_RULES[t]
        return BenchmarkSuggestion(ref, REASONS[ref])

    if asset is None:
        if is_crypto(t):
            return BenchmarkSuggestion("BTC-USD", REASONS["BTC-USD"])
        return BenchmarkSuggestion(None, NO_REFERENCE_REASONS["default"])

    group, market = asset.get("group"), asset.get("market")
    if group == "crypto":
        return BenchmarkSuggestion("BTC-USD", REASONS["BTC-USD"])
    if group == "br_stocks" or (group == "equity_etfs" and market == "Brasil/B3"):
        return BenchmarkSuggestion("^BVSP", REASONS["^BVSP"])
    if market == "EUA" and group in {"us_stocks", "equity_etfs", "reits"}:
        return BenchmarkSuggestion("^GSPC", REASONS["^GSPC"])

    reason = NO_REFERENCE_REASONS.get(group, NO_REFERENCE_REASONS["default"])
    return BenchmarkSuggestion(None, reason)


def align_with_benchmark(
    asset_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    frequency: str,
    value_col: str = "Value",
) -> pd.DataFrame:
    """
    Ativo e referência em Base 100, só nas datas comuns.

    Nas frequências agregadas, alinha pelo fim do período (`PeriodEnd`),
    porque o último pregão pode cair em dias diferentes; na diária, pela
    data. Colunas: Date (último pregão do ativo no período), Ativo e
    Referência (Base 100 na primeira data comum).
    """
    key = "PeriodEnd" if frequency != "Diário" and "PeriodEnd" in asset_df.columns \
        and "PeriodEnd" in benchmark_df.columns else "Date"

    def clean(df: pd.DataFrame, name: str) -> pd.DataFrame:
        columns = ["Key", "Date", name]
        if df is None or df.empty or key not in df.columns or value_col not in df.columns:
            return pd.DataFrame(columns=columns)
        frame = pd.DataFrame({
            "Key": pd.to_datetime(df[key], errors="coerce").dt.normalize(),
            "Date": pd.to_datetime(df["Date"] if "Date" in df.columns else df[key], errors="coerce"),
            name: pd.to_numeric(df[value_col], errors="coerce"),
        }).dropna()
        return frame[frame[name] > 0].drop_duplicates("Key", keep="last")

    # A data exibida é o último pregão do ativo em cada período, não o fim do calendário.
    asset = clean(asset_df, "Ativo")
    reference = clean(benchmark_df, "Referência").drop(columns="Date")
    merged = asset.merge(reference, on="Key", how="inner").drop(columns="Key")
    merged = merged.sort_values("Date").reset_index(drop=True)
    if len(merged) < 2:
        return pd.DataFrame(columns=["Date", "Ativo", "Referência"])

    for column in ("Ativo", "Referência"):
        merged[column] = merged[column] / merged[column].iloc[0] * 100
    return merged


def benchmark_notes(ticker: str, benchmark: str, frequency: str) -> list[str]:
    """Avisos de moeda, unidade e calendário entre o ativo e a referência."""
    notes = []
    asset_info, ref_info = currency_info(ticker), currency_info(benchmark)

    if ref_info.kind == "points":
        notes.append(
            f"{BENCHMARKS.get(benchmark, benchmark)} é um índice em pontos: a Base 100 compara "
            "apenas a variação percentual, não valores."
        )
    if asset_info.kind == "price" and ref_info.kind == "price" and asset_info.code != ref_info.code:
        notes.append(
            f"O ativo é cotado em {asset_info.label} e a referência em {ref_info.label}: "
            "a Base 100 não converte moedas, então parte da diferença pode vir do câmbio."
        )
    elif asset_info.kind == "price" and ref_info.kind == "points" and asset_info.code != _index_currency(benchmark):
        notes.append(
            f"O ativo é cotado em {asset_info.label}, e o índice acompanha empresas cotadas em "
            "outra moeda: parte da diferença pode vir do câmbio."
        )
    if frequency == "Diário" and is_crypto(ticker) != is_crypto(benchmark):
        notes.append(
            "Criptomoedas são negociadas todos os dias e as bolsas, só em dias úteis: na "
            "frequência diária, a comparação usa apenas as datas em que os dois têm cotação."
        )
    if frequency in LONG_FREQUENCIES:
        notes.append(
            "Com frequência semestral ou anual há poucos pontos de comparação; a trajetória "
            "fica resumida."
        )
    return notes


def _index_currency(benchmark: str) -> str:
    """Moeda das empresas que compõem o índice de referência."""
    return {"^BVSP": "BRL", "^GSPC": "USD"}.get(benchmark, "")


def describe_comparison(aligned: pd.DataFrame, asset_label: str, benchmark_label: str) -> str:
    """Frase descritiva das variações no período comum (sem juízo de valor)."""
    start, end = aligned["Date"].iloc[0], aligned["Date"].iloc[-1]
    asset_change = aligned["Ativo"].iloc[-1] / 100 - 1
    ref_change = aligned["Referência"].iloc[-1] / 100 - 1

    def pct(value: float) -> str:
        return f"{value * 100:+,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")

    return (
        f"Entre {start:%d/%m/%Y} e {end:%d/%m/%Y} (datas comuns aos dois), "
        f"**{asset_label}** variou **{pct(asset_change)}** e **{benchmark_label}**, "
        f"**{pct(ref_change)}**."
    )
