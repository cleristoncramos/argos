"""Prompts versionados e esquema de saída."""

import json

from core import llm_context as lc
from core import llm_prompts as lp


def _ctx(**over):
    base = dict(
        analysis_type="comparacao",
        assets=["AAPL", "^GSPC"],
        period_start="2020-01-01",
        period_end="2024-12-31",
        frequency="Mensal",
        n_observations=60,
        metrics=[lc.metric("correlacao", "Correlação", 0.91, "")],
    )
    base.update(over)
    return lc.build_context(**base)


def test_every_analysis_type_has_instruction():
    for kind in lc.ANALYSIS_TYPES:
        assert kind in lp._USER_INSTRUCTIONS


def test_system_prompt_mentions_core_rules():
    text = lp.SYSTEM_PROMPT.lower()
    for word in ("histórico", "recomendação", "previsão", "compre", "vai subir"):
        assert word in text


def test_response_format_is_strict_schema():
    fmt = lp.response_format()
    assert fmt["type"] == "json_schema"
    assert fmt["json_schema"]["strict"] is True
    schema = fmt["json_schema"]["schema"]
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == set(schema["properties"])


def test_user_prompt_contains_context_and_request():
    ctx = _ctx(user_request=("previsao", "Vai subir?"))
    prompt = lp.user_prompt(ctx)
    assert json.dumps("AAPL") in prompt
    assert "Pedido do usuário (tipo previsao): Vai subir?" in prompt
    assert "Pedido do usuário" not in lp.user_prompt(_ctx())


def test_build_messages_roles():
    messages = lp.build_messages(_ctx())
    assert [m["role"] for m in messages] == ["system", "user"]


def test_fingerprint_is_stable_and_short():
    assert lp.prompt_fingerprint() == lp.prompt_fingerprint()
    assert len(lp.prompt_fingerprint()) == 12


def test_fixed_texts_present():
    assert "não fornece recomendação" in lp.REFUSAL_TEXT
    assert "previsão" in lp.REFUSAL_FORECAST_TEXT
    assert lp.VALIDATION_FAILURE_TEXT
