"""Pacote de contexto da explicação assistida."""

import pytest

from core import llm_context as lc


def _ctx(**over):
    base = dict(
        analysis_type="risco_retorno",
        assets=["AAPL"],
        period_start="2020-01-01",
        period_end="2024-12-31",
        frequency="Diário",
        n_observations=1250,
        metrics=[lc.metric("retorno_total", "Retorno total", 12.3456, "%")],
    )
    base.update(over)
    return lc.build_context(**base)


def test_metric_rounds_and_validates():
    m = lc.metric("vol", "Volatilidade", 18.4567, "%", decimals=1)
    assert m["value"] == 18.5
    assert m["decimals"] == 1
    with pytest.raises(ValueError):
        lc.metric(" ", "x", 1, "%")
    with pytest.raises(ValueError):
        lc.metric("a", "x", "abc", "%")
    with pytest.raises(ValueError):
        lc.metric("a", "x", float("nan"), "%")
    with pytest.raises(ValueError):
        lc.metric("a", "x", 1, "%", decimals=-1)


def test_flags():
    assert lc.derive_limitation_flags(n_observations=10, frequency="Diário") == ["poucas_observacoes"]
    assert lc.derive_limitation_flags(n_observations=1000, frequency="Diário") == []
    assert lc.derive_limitation_flags(
        n_observations=1000, frequency="Mensal", n_years=3, incomplete_month=True, nonpositive_price=True
    ) == ["poucos_anos", "mes_em_andamento", "preco_nao_positivo"]
    assert lc.derive_limitation_flags(n_observations=5, frequency="Outra") == []


def test_build_context_ok():
    ctx = _ctx(
        user_request=("recomendacao", " Devo comprar? "),
        limitation_flags=["poucos_anos", "poucos_anos"],
        notes=["nota"],
        extra_numbers=[3],
        asset_names={"AAPL": "Apple"},
    )
    assert ctx["context_version"] == lc.CONTEXT_VERSION
    assert ctx["filters"] == {
        "period_start": "2020-01-01",
        "period_end": "2024-12-31",
        "frequency": "Diário",
    }
    assert ctx["user_request"] == {"type": "recomendacao", "text": "Devo comprar?"}
    assert ctx["limitation_flags"] == ["poucos_anos"]
    assert ctx["extra_numbers"] == [3.0]
    assert _ctx()["user_request"] is None


@pytest.mark.parametrize(
    "over",
    [
        {"analysis_type": "x"},
        {"status": "x"},
        {"frequency": "Trimestral"},
        {"assets": []},
        {"assets": [""]},
        {"assets": ["AAPL", "aapl"]},
        {"period_start": "01/01/2020"},
        {"period_start": "2025-01-01"},
        {"n_observations": -1},
        {"n_observations": 1.5},
        {"metrics": [lc.metric("a", "A", 1, "%"), lc.metric("a", "B", 2, "%")]},
        {"status": "dados_insuficientes"},
        {"limitation_flags": ["inexistente"]},
        {"user_request": ("outro", "texto")},
    ],
)
def test_build_context_rejects(over):
    with pytest.raises(ValueError):
        _ctx(**over)


def test_insufficient_without_metrics_is_ok():
    ctx = _ctx(status="dados_insuficientes", metrics=[])
    assert ctx["status"] == "dados_insuficientes"


def test_allowed_numbers():
    nums = lc.allowed_numbers(_ctx(extra_numbers=[7]))
    assert 12.35 in nums
    assert 1250.0 in nums
    assert 7.0 in nums
    assert 100.0 in nums
    assert 2022.0 in nums


def test_allowed_numbers_include_period_span_and_scale():
    nums = lc.allowed_numbers(_ctx())
    assert 5.0 in nums and 0.0 in nums and 1.0 in nums
