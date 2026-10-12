"""Contextos por tela e apresentação da explicação (7B, bloco 2). Sem Streamlit e sem rede."""

import json

import numpy as np
import pandas as pd
import pytest

from core import llm_builders as lb
from core import llm_render as lr
from core import llm_validation as lv
from core.simulation import compare_strategies, summarize_simulation
from experiments.llm_7a import runner

NAN = float("nan")


def _df(n=300, start="2024-01-01", seed=1):
    rng = np.random.default_rng(seed)
    values = 100 * np.cumprod(1 + rng.normal(0.0005, 0.01, n))
    return pd.DataFrame({"Date": pd.date_range(start, periods=n, freq="D"), "Value": values})


def _accepts(ctx):
    answer = json.dumps(runner.canned_answer(ctx), ensure_ascii=False)
    return lv.validate_response(answer, ctx, ["AAPL"]).ok


# ---------------------------------------------------------------- individual
def test_individual_context_has_three_validated_metrics():
    df = _df()
    ctx = lb.individual_context(df, "AAPL", "Diário", 252, name="Apple Inc.", notes=["Unidade: USD."])
    assert ctx["analysis_type"] == "analise_individual" and ctx["assets"] == ["AAPL"]
    assert [m["id"] for m in ctx["metrics"]] == ["retorno_total", "retorno_medio", "volatilidade"]
    assert ctx["filters"] == {"period_start": "2024-01-01", "period_end": "2024-10-26", "frequency": "Diário"}
    assert ctx["n_observations"] == 300 and ctx["asset_names"] == {"AAPL": "Apple Inc."}
    assert ctx["notes"] == ["Unidade: USD."] and ctx["limitation_flags"] == []
    assert _accepts(ctx)


def test_individual_flags_few_observations_and_no_name():
    ctx = lb.individual_context(_df(30), "AAPL", "Diário", 252)
    assert ctx["limitation_flags"] == ["poucas_observacoes"] and ctx["asset_names"] == {}


def test_individual_nonpositive_price_returns_none():
    df = _df()
    df.loc[5, "Value"] = 0.0
    assert lb.individual_context(df, "AAPL", "Diário", 252) is None


def test_individual_without_finite_metrics_returns_none():
    summary = {k: NAN for k in ("Retorno total", "Retorno médio", "Volatilidade", "Drawdown máximo", "Percentual positivo", "Sharpe")}
    assert lb.individual_context(_df(), "AAPL", "Diário", 252, summary=summary) is None


# ---------------------------------------------------------------- risco e retorno
def test_risk_context_has_six_metrics_with_rate_in_label():
    ctx = lb.risk_context(_df(), "AAPL", "Diário", 252, 10.5)
    ids = [m["id"] for m in ctx["metrics"]]
    assert ids == ["retorno_total", "retorno_medio", "volatilidade", "drawdown_maximo", "percentual_positivo", "sharpe"]
    sharpe = ctx["metrics"][-1]
    assert sharpe["label"] == "Índice de Sharpe (taxa livre de risco 10,5%)" and sharpe["decimals"] == 2
    assert ctx["extra_numbers"] == [10.5] and _accepts(ctx)


def test_risk_context_zero_rate_label_and_given_summary():
    summary = {"Retorno total": 0.5, "Retorno médio": 0.001, "Volatilidade": 0.2,
               "Drawdown máximo": -0.3, "Percentual positivo": 0.55, "Sharpe": NAN}
    ctx = lb.risk_context(_df(), "AAPL", "Diário", 252, 0, summary=summary)
    assert [m["id"] for m in ctx["metrics"]] == ["retorno_total", "retorno_medio", "volatilidade", "drawdown_maximo", "percentual_positivo"]
    assert [m["value"] for m in ctx["metrics"]][:2] == [50.0, 0.1]


def test_risk_context_none_cases():
    df = _df()
    df.loc[3, "Value"] = -1.0
    assert lb.risk_context(df, "AAPL", "Diário", 252, 0) is None
    nan_summary = {k: NAN for k in ("Retorno total", "Retorno médio", "Volatilidade", "Drawdown máximo", "Percentual positivo", "Sharpe")}
    assert lb.risk_context(_df(), "AAPL", "Diário", 252, 0, summary=nan_summary) is None


# ---------------------------------------------------------------- simulação
def _sim(amount=500.0, every=21):
    paths = compare_strategies(_df(), periodic_amount=amount, every=every)
    return paths, summarize_simulation(paths["periodic"]), summarize_simulation(paths["lump_sum"])


def test_simulation_context_matches_validated_shape():
    paths, periodic, lump = _sim()
    ctx = lb.simulation_context(paths, "AAPL", "Diário", "US$", 500.0, 21, periodic, lump, name="Apple Inc.")
    assert ctx["analysis_type"] == "simulacao"
    assert [m["id"] for m in ctx["metrics"]] == [
        "total_investido", "valor_final_periodico", "retorno_periodico", "valor_final_unico", "retorno_unico"]
    assert ctx["metrics"][0]["unit"] == "US$" and ctx["metrics"][2]["unit"] == "%"
    assert ctx["notes"] == ["Simulação hipotética com aportes de 500 a cada 21 observações; não considera custos nem impostos."]
    assert ctx["extra_numbers"] == [500.0, 21.0] and ctx["n_observations"] == len(paths["periodic"])
    assert _accepts(ctx)


def test_simulation_context_without_finite_metrics_returns_none():
    paths, periodic, lump = _sim()
    bad = {k: NAN for k in periodic}
    assert lb.simulation_context(paths, "AAPL", "Diário", "US$", 500.0, 21, bad, bad) is None


# ---------------------------------------------------------------- apresentação
def test_escape_markdown_blocks_formatting_and_math():
    assert lr.escape_markdown("a*b_c [x] `y` $5 ~z <b>") == r"a\*b\_c \[x\] \`y\` \$5 \~z \<b\>"
    assert lr.escape_markdown(12) == "12"


def test_format_value_brazilian_style():
    assert lr.format_value(43.6, "%") == "43,6%"
    assert lr.format_value(30406.0, "BRL") == "30.406 BRL"
    assert lr.format_value(0.056, "%") == "0,056%"
    assert lr.format_value(1234567.5) == "1.234.567,5"
    assert lr.format_value(0.56, "") == "0,56"


def test_explanation_view_uses_labels_and_escapes():
    ctx = lb.risk_context(_df(), "AAPL", "Diário", 252, 0)
    data = runner.canned_answer(ctx)
    data["resumo"] = "Teve *alta* no período."
    view = lr.explanation_view(data, ctx)
    assert view["resumo"] == r"Teve \*alta\* no período."
    assert view["metricas"][0][0] == "Retorno total no período"
    assert view["limitacoes"] and view["nao_concluir"] and view["nota"] and view["grafico"]
    unknown = lr.explanation_view({**data, "metricas_relevantes": [{"id": "x_y", "valor": 1.0, "unidade": "", "leitura": "ok"}]})
    assert unknown["metricas"] == [(r"x\_y", "1", "ok")]


def test_non_numeric_metric_values_are_skipped():
    summary = {"Retorno total": 0.5, "Retorno médio": 0.001, "Volatilidade": 0.2,
               "Drawdown máximo": -0.3, "Percentual positivo": 0.55, "Sharpe": None}
    ctx = lb.risk_context(_df(), "AAPL", "Diário", 252, 0, summary=summary)
    assert "sharpe" not in [m["id"] for m in ctx["metrics"]]
