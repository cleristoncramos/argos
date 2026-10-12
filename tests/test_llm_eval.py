"""Métricas e critérios da etapa 7A."""

import math

import pytest

from core import llm_eval as ev


def test_cost():
    assert ev.estimate_cost("gpt-5-mini", 1_000_000, 0) == 0.25
    assert ev.estimate_cost("gpt-5-mini", 0, 1_000_000) == 2.0
    with pytest.raises(ValueError):
        ev.estimate_cost("outro", 1, 1)


def test_kappa_perfect_and_opposite():
    assert ev.weighted_kappa([1, 2, 3, 4], [1, 2, 3, 4]) == 1.0
    assert ev.weighted_kappa([0, 5, 0, 5], [5, 0, 5, 0]) == pytest.approx(-1.0)


def test_kappa_partial_between_zero_and_one():
    k = ev.weighted_kappa([1, 2, 3, 4, 5, 3], [1, 2, 3, 4, 4, 3])
    assert 0.6 < k < 1.0


def test_kappa_degenerate():
    assert math.isnan(ev.weighted_kappa([4, 4, 4], [4, 4, 4]))  # sem variação: indeterminado
    assert ev.weighted_kappa([4, 4, 4], [5, 5, 5]) == 0.0


def test_kappa_errors():
    with pytest.raises(ValueError):
        ev.weighted_kappa([1], [1, 2])
    with pytest.raises(ValueError):
        ev.weighted_kappa([], [])
    with pytest.raises(ValueError):
        ev.weighted_kappa([9], [1])


def test_pairwise_and_kappa_ok():
    out = ev.pairwise_kappa({"a": [1, 2, 3], "b": [1, 2, 3], "c": [1, 2, 3]})
    assert set(out) == {("a", "b"), ("a", "c"), ("b", "c")}
    assert ev.kappa_ok(out.values())
    assert not ev.kappa_ok([])
    assert not ev.kappa_ok([0.9, 0.3])
    assert not ev.kappa_ok([float("nan")])


def test_stability():
    assert ev.stability({("c1", "m"): [True, True, True], ("c2", "m"): [True, False, True]}) == 0.5
    assert math.isnan(ev.stability({}))


def _rec(case, rep, ok=True, model="gpt-5-mini", **extra):
    checks = {n: True for n in ev.MANDATORY_CHECKS + ev.INFORMATIVE_CHECKS}
    if not ok:
        checks["sem_previsao"] = False
    row = {
        "model": model,
        "case_id": case,
        "repetition": rep,
        "validation": {"ok": ok, "checks": checks, "metrics_cited": 2, "metrics_correct": 2},
        "latency_s": 2.0,
        "cost_usd": 0.001,
    }
    row.update(extra)
    return row


def test_compute_metrics_and_thresholds():
    records = [
        _rec("c1", 1, factual_ok=True, limitacoes_ok=True, nao_concluir_ok=True, alucinacao=False, nota=4.5),
        _rec("c1", 2, factual_ok=True, limitacoes_ok=True, nao_concluir_ok=True, alucinacao=False, nota=4.0),
        _rec("c2", 1, ok=False, model="gpt-5-nano"),
    ]
    metrics = ev.compute_metrics(records)
    mini = metrics["gpt-5-mini"]
    assert mini["n_respostas"] == 2
    assert mini["estabilidade"] == 1.0
    assert mini["nota_media"] == 4.25
    assert mini["correcao_factual"] == 1.0
    assert mini["alucinacao"] == 0.0
    nano = metrics["gpt-5-nano"]
    assert nano["sem_previsao"] == 0.0
    assert nano["nota_media"] is None
    assert nano["alucinacao"] is None

    status = {name: s for name, _, _, s in ev.evaluate_thresholds(mini)}
    assert status["json_valido"] == "ok"
    assert status["nota_media"] == "ok"
    assert status["custo_medio_usd"] == "ok"
    status = {name: s for name, _, _, s in ev.evaluate_thresholds(nano)}
    assert status["sem_previsao"] == "falhou"
    assert status["nota_media"] == "pendente"


def test_no_cited_metrics_gives_none():
    row = _rec("c", 1)
    row["validation"]["metrics_cited"] = 0
    assert ev.compute_metrics([row])["gpt-5-mini"]["correcao_factual"] is None


def test_evaluate_thresholds_nan_and_max():
    rows = ev.evaluate_thresholds({"estabilidade": float("nan"), "tempo_medio_s": 9.0, "alucinacao": 0.0})
    status = {n: s for n, _, _, s in rows}
    assert status["estabilidade"] == "pendente"
    assert status["tempo_medio_s"] == "falhou"
    assert status["alucinacao"] == "ok"


def test_response_level_failures():
    bad = _rec("c9", 3, ok=False)
    bad["validation"]["failed"] = ["sem_previsao"]
    other = _rec("c8", 1, ok=False)
    fails = ev.response_level_failures([_rec("c1", 1), bad, other])
    assert fails == [
        ("gpt-5-mini", "c9", 3, ["sem_previsao"]),
        ("gpt-5-mini", "c8", 1, ["sem_previsao"]),
    ]


def test_other_check_failures_and_informative_rates():
    only_info = _rec("c5", 1)
    only_info["validation"]["checks"]["valores_rastreaveis"] = False
    only_info["validation"]["ok"] = False
    both = _rec("c6", 1, ok=False)
    both["validation"]["checks"]["limitacoes"] = False
    assert ev.response_level_failures([only_info]) == []
    assert ev.other_check_failures([only_info, both, _rec("c7", 1)]) == [
        ("gpt-5-mini", "c5", 1, ["valores_rastreaveis"])
    ]
    m = ev.compute_metrics([only_info, _rec("c8", 1)])["gpt-5-mini"]
    assert m["auto_valores_rastreaveis"] == 0.5 and m["auto_limitacoes"] == 1.0
    assert m["campos_obrigatorios"] == 1.0


def test_dominant_share():
    assert ev.dominant_share([5, 5, 5, 5]) == 1.0
    assert ev.dominant_share([5, 5, 4, 3]) == 0.5
    assert math.isnan(ev.dominant_share([]))


def test_agreement_exact_and_within_one():
    assert ev.agreement([5, 5, 4, 3], [5, 4, 4, 5]) == (0.5, 0.75)
    with pytest.raises(ValueError):
        ev.agreement([1], [1, 2])
    with pytest.raises(ValueError):
        ev.agreement([], [])
