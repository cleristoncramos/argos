"""Cliente da API e serviço de explicação assistida (7B, bloco 1). Sem rede."""

import io
import json
import os
import urllib.error
import urllib.request

import pytest

from core import llm_client as lc_
from core import llm_context as lc
from core import llm_prompts as lp
from core import llm_service as svc
from experiments.llm_7a import runner


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


def _answer(context):
    return json.dumps(runner.canned_answer(context), ensure_ascii=False)


def _transport_ok(context, finish="stop", counter=None):
    def transport(payload, key, timeout):
        if counter is not None:
            counter.append(payload)
        return {
            "choices": [{"message": {"content": _answer(context)}, "finish_reason": finish}],
            "usage": {"prompt_tokens": 900, "completion_tokens": 350},
        }
    return transport


def _no_sleep(_):
    return None


def _failure(transport, waits=None):
    """Executa call_model esperando CallFailed e devolve a exceção."""
    try:
        lc_.call_model(_ctx(), "k", transport, waits.append if waits is not None else _no_sleep)
    except lc_.CallFailed as exc:
        return exc
    raise AssertionError("CallFailed não foi levantada")


# ---------------------------------------------------------------- cliente
def test_payload_uses_frozen_prompt_and_fixed_params():
    ctx = _ctx()
    payload = lc_.build_payload(ctx)
    assert payload["model"] == "gpt-5-mini"
    assert payload["max_completion_tokens"] == 1400
    assert payload["reasoning_effort"] == "minimal"
    assert payload["response_format"]["json_schema"]["strict"] is True
    assert payload["messages"] == lp.build_messages(ctx)
    assert "tools" not in payload and "functions" not in payload


def test_call_model_success_and_usage():
    ctx = _ctx()
    out = lc_.call_model(ctx, "k", _transport_ok(ctx), _no_sleep)
    assert out["attempts"] == 1 and out["finish_reason"] == "stop"
    assert (out["input_tokens"], out["output_tokens"]) == (900, 350)
    assert json.loads(out["raw"])["recusa_recomendacao"] is False


def test_call_model_empty_response_fields():
    out = lc_.call_model(_ctx(), "k", lambda p, k, t: {}, _no_sleep)
    assert out["raw"] == "" and out["input_tokens"] == 0 and out["finish_reason"] is None


def test_call_model_retries_then_succeeds():
    ctx = _ctx()
    waits, state = [], {"n": 0}
    good = _transport_ok(ctx)

    def flaky(payload, key, timeout):
        state["n"] += 1
        if state["n"] == 1:
            raise lc_.ApiError(429, "limite")
        if state["n"] == 2:
            raise TimeoutError("lento")
        return good(payload, key, timeout)

    out = lc_.call_model(ctx, "k", flaky, waits.append)
    assert out["attempts"] == 3 and waits == [1, 2]


def test_call_model_gives_up_after_two_retries():
    def always(payload, key, timeout):
        raise lc_.ApiError(503, "fora do ar")

    waits = []
    exc = _failure(always, waits)
    assert exc.attempts == 3 and "503" in str(exc) and waits == [1, 2]


def test_call_model_network_error_gives_up():
    def broken(payload, key, timeout):
        raise OSError("sem rede")

    exc = _failure(broken)
    assert "rede: OSError" in str(exc) and exc.attempts == 3


def test_call_model_does_not_retry_client_errors():
    calls = []

    def bad(payload, key, timeout):
        calls.append(1)
        raise lc_.ApiError(401, "chave inválida")

    exc = _failure(bad)
    assert "HTTP 401" in str(exc) and exc.attempts == 1 and len(calls) == 1


def test_call_model_uses_timeout_of_20_seconds():
    seen = []

    def transport(payload, key, timeout):
        seen.append(timeout)
        return {"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}]}

    lc_.call_model(_ctx(), "k", transport, _no_sleep)
    assert seen == [20]


def test_http_transport_ok_and_errors():
    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    real = urllib.request.urlopen
    try:
        urllib.request.urlopen = lambda req, timeout=0: Resp(json.dumps({"ok": 1}).encode())
        assert lc_.http_transport({"a": 1}, "k") == {"ok": 1}

        def boom(body):
            def raiser(req, timeout=0):
                raise urllib.error.HTTPError("u", 400, "bad", {}, io.BytesIO(body))
            return raiser

        urllib.request.urlopen = boom(json.dumps({"error": {"message": "ruim"}}).encode())
        with pytest.raises(lc_.ApiError, match="ruim"):
            lc_.http_transport({}, "k")
        urllib.request.urlopen = boom(b"texto solto")
        with pytest.raises(lc_.ApiError, match="texto solto"):
            lc_.http_transport({}, "k")
    finally:
        urllib.request.urlopen = real


def test_api_key_from_env():
    old = os.environ.pop("OPENAI_API_KEY", None)
    try:
        assert lc_.api_key_from_env() is None
        os.environ["OPENAI_API_KEY"] = "  abc "
        assert lc_.api_key_from_env() == "abc"
        os.environ["OPENAI_API_KEY"] = "   "
        assert lc_.api_key_from_env() is None
    finally:
        os.environ.pop("OPENAI_API_KEY", None)
        if old is not None:
            os.environ["OPENAI_API_KEY"] = old


# ---------------------------------------------------------------- serviço: configuração
def test_approved_prompt_matches_frozen_fingerprint():
    assert lp.PROMPT_VERSION == svc.APPROVED_PROMPT_VERSION == "v0.6"
    assert lp.prompt_fingerprint() == svc.APPROVED_FINGERPRINT == "e3b3574b7430"


def test_invalid_mode_raises():
    with pytest.raises(ValueError):
        svc.explain(_ctx(), mode="outro")


def test_mode_off_never_calls_api():
    calls, logs = [], []
    out = svc.explain(_ctx(), mode=svc.MODE_OFF, api_key="k", transport=_transport_ok(_ctx(), counter=calls), log_sink=logs.append)
    assert out.status == svc.STATUS_OFF and not out.shown and out.fallback_text == svc.FALLBACK_TEXT
    assert calls == [] and logs[0]["status"] == "desativada"


def test_free_user_input_is_refused_before_any_call():
    ctx = _ctx(user_request=("recomendacao", "Devo vender?"))
    calls = []
    out = svc.explain(ctx, mode=svc.MODE_LIVE, api_key="k", transport=_transport_ok(ctx, counter=calls))
    assert out.status == svc.STATUS_BLOCKED and out.reason == "entrada_livre_nao_permitida"
    assert out.fallback_text and calls == []


def test_invalid_context_is_blocked():
    out = svc.explain({"analysis_type": "comparacao"}, mode=svc.MODE_LIVE, api_key="k")
    assert out.reason == "contexto_invalido" and out.status == svc.STATUS_BLOCKED
    assert svc.explain("texto", mode=svc.MODE_DEMO).reason == "contexto_invalido"


def test_prompt_divergence_blocks_before_any_call():
    ctx = _ctx()
    calls = []
    original = lp.SYSTEM_PROMPT
    try:
        lp.SYSTEM_PROMPT = original + " alterado"
        out = svc.explain(ctx, mode=svc.MODE_LIVE, api_key="k", transport=_transport_ok(ctx, counter=calls))
    finally:
        lp.SYSTEM_PROMPT = original
    assert out.reason == "prompt_divergente" and calls == []


# ---------------------------------------------------------------- serviço: modo ao vivo
def test_live_success_logs_usage_and_validates():
    ctx = _ctx()
    logs, limiter = [], svc.UsageLimiter()
    out = svc.explain(
        ctx, mode=svc.MODE_LIVE, api_key="segredo-123", transport=_transport_ok(ctx),
        known_tickers=["AAPL", "^GSPC", "BTC-USD"], limiter=limiter, log_sink=logs.append, sleep=_no_sleep,
    )
    assert out.status == svc.STATUS_OK and out.shown and out.fallback_text is None
    assert out.data["recusa_recomendacao"] is False
    log = logs[0]
    assert log["model"] == "gpt-5-mini" and log["prompt_version"] == "v0.6"
    assert log["prompt_fingerprint"] == "e3b3574b7430"
    assert (log["input_tokens"], log["output_tokens"]) == (900, 350)
    assert 0 < log["cost_usd"] < 0.002 and log["status"] == "ok" and log["failed_checks"] == []
    assert limiter.calls == 1 and limiter.cost_usd == log["cost_usd"]
    dumped = json.dumps(log, ensure_ascii=False)
    assert "segredo-123" not in dumped and out.data["resumo"] not in dumped


def test_live_without_key_is_unavailable():
    out = svc.explain(_ctx(), mode=svc.MODE_LIVE, api_key=None)
    assert out.status == svc.STATUS_UNAVAILABLE and out.reason == "sem_chave" and out.fallback_text


def test_live_validation_failure_blocks_and_records_checks():
    ctx = _ctx()
    bad = runner.canned_answer(ctx)
    bad["resumo"] = "Compre este ativo agora."
    logs = []

    def transport(payload, key, timeout):
        return {"choices": [{"message": {"content": json.dumps(bad, ensure_ascii=False)}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 10}}

    out = svc.explain(ctx, mode=svc.MODE_LIVE, api_key="k", transport=transport, log_sink=logs.append)
    assert out.status == svc.STATUS_BLOCKED and out.reason == "validacao_reprovada" and not out.shown
    assert out.fallback_text == svc.FALLBACK_TEXT
    assert "sem_termos_proibidos" in logs[0]["failed_checks"]


def test_live_invalid_json_blocks():
    def transport(payload, key, timeout):
        return {"choices": [{"message": {"content": "texto qualquer"}, "finish_reason": "stop"}]}

    out = svc.explain(_ctx(), mode=svc.MODE_LIVE, api_key="k", transport=transport)
    assert out.status == svc.STATUS_BLOCKED and "json_valido" in out.log["failed_checks"]


def test_live_truncated_response_blocks_without_validating():
    ctx = _ctx()
    out = svc.explain(ctx, mode=svc.MODE_LIVE, api_key="k", transport=_transport_ok(ctx, finish="length"))
    assert out.status == svc.STATUS_BLOCKED and out.reason == "resposta_incompleta"
    assert out.log["output_tokens"] == 350


def test_live_api_down_falls_back_and_counts_call():
    limiter = svc.UsageLimiter()

    def down(payload, key, timeout):
        raise lc_.ApiError(500, "erro")

    out = svc.explain(_ctx(), mode=svc.MODE_LIVE, api_key="k", transport=down, limiter=limiter, sleep=_no_sleep)
    assert out.status == svc.STATUS_UNAVAILABLE and out.reason.startswith("api_indisponivel")
    assert out.log["attempts"] == 3 and limiter.calls == 1 and limiter.cost_usd == 0.0


def test_usage_and_cost_limits_stop_calls():
    ctx = _ctx()
    calls = []
    limiter = svc.UsageLimiter(max_calls=1)
    first = svc.explain(ctx, mode=svc.MODE_LIVE, api_key="k", transport=_transport_ok(ctx, counter=calls), limiter=limiter)
    second = svc.explain(ctx, mode=svc.MODE_LIVE, api_key="k", transport=_transport_ok(ctx, counter=calls), limiter=limiter)
    assert first.status == svc.STATUS_OK and second.reason == "limite_de_uso" and len(calls) == 1
    costly = svc.UsageLimiter(max_cost_usd=0.0001)
    svc.explain(ctx, mode=svc.MODE_LIVE, api_key="k", transport=_transport_ok(ctx), limiter=costly)
    third = svc.explain(ctx, mode=svc.MODE_LIVE, api_key="k", transport=_transport_ok(ctx, counter=calls), limiter=costly)
    assert third.reason == "limite_de_custo" and len(calls) == 1


def test_default_limiter_is_created_per_call_when_missing():
    ctx = _ctx()
    out = svc.explain(ctx, mode=svc.MODE_LIVE, api_key="k", transport=_transport_ok(ctx))
    assert out.status == svc.STATUS_OK


# ---------------------------------------------------------------- serviço: demonstração
def test_demo_uses_saved_response_without_network():
    ctx = _ctx()
    store = {svc.context_key(ctx): _answer(ctx)}
    calls = []
    out = svc.explain(ctx, mode=svc.MODE_DEMO, demo_store=store, api_key="k", transport=_transport_ok(ctx, counter=calls))
    assert out.status == svc.STATUS_DEMO and out.shown and calls == []
    assert out.log["model"] is None and out.log["cost_usd"] == 0.0


def test_demo_without_saved_response_uses_fallback():
    out = svc.explain(_ctx(), mode=svc.MODE_DEMO, demo_store={})
    assert out.status == svc.STATUS_UNAVAILABLE and out.reason == "demo_sem_resposta_salva" and out.fallback_text
    assert svc.explain(_ctx(), mode=svc.MODE_DEMO).reason == "demo_sem_resposta_salva"


def test_demo_response_is_validated_too():
    ctx = _ctx()
    bad = runner.canned_answer(ctx)
    bad["resumo"] = "Vale a pena comprar."
    store = {svc.context_key(ctx): json.dumps(bad, ensure_ascii=False)}
    out = svc.explain(ctx, mode=svc.MODE_DEMO, demo_store=store)
    assert out.status == svc.STATUS_BLOCKED and not out.shown


def test_context_key_is_stable_and_sensitive():
    assert svc.context_key(_ctx()) == svc.context_key(_ctx())
    assert svc.context_key(_ctx()) != svc.context_key(_ctx(n_observations=61))


def test_build_and_load_demo_store(tmp_path):
    ctx_a, ctx_b = _ctx(), _ctx(n_observations=61)
    cases = [{"id": "a", "contexto": ctx_a}, {"id": "b", "contexto": ctx_b}]
    fp = svc.APPROVED_FINGERPRINT
    good = dict(model="gpt-5-mini", prompt_fingerprint=fp, validation={"ok": True})
    records = [
        {**good, "case_id": "a", "raw": _answer(ctx_a)},
        {**good, "case_id": "a", "raw": "segunda resposta ignorada"},
        {**good, "case_id": "b", "raw": "x", "dry_run": True},
        {**good, "case_id": "b", "raw": "x", "model": "gpt-5-nano"},
        {**good, "case_id": "b", "raw": "x", "validation": {"ok": False}},
        {**good, "case_id": "b", "raw": "x", "prompt_fingerprint": "outro"},
        {**good, "case_id": "zzz", "raw": "x"},
    ]
    built = svc.build_demo_store(records, cases)
    assert list(built["respostas"]) == [svc.context_key(ctx_a)]
    assert built["respostas"][svc.context_key(ctx_a)] == _answer(ctx_a)
    path = tmp_path / "demo.json"
    path.write_text(json.dumps(built, ensure_ascii=False), encoding="utf-8")
    assert svc.load_demo_store(path) == built["respostas"]
    assert svc.load_demo_store(tmp_path / "nao_existe.json") == {}
    path.write_text("[]", encoding="utf-8")
    assert svc.load_demo_store(path) == {}


def test_append_log_writes_jsonl(tmp_path):
    path = tmp_path / "sub" / "uso.jsonl"
    svc.append_log(path, {"status": "ok", "n": 1})
    svc.append_log(path, {"status": "bloqueada"})
    lines = path.read_text(encoding="utf-8").splitlines()
    assert [json.loads(x)["status"] for x in lines] == ["ok", "bloqueada"]


def test_make_demo_store_cli(tmp_path):
    from experiments.llm_7b import make_demo_store

    ctx = _ctx()
    record = dict(model="gpt-5-mini", prompt_fingerprint=svc.APPROVED_FINGERPRINT,
                  validation={"ok": True}, case_id="a", raw=_answer(ctx))
    (tmp_path / "r.jsonl").write_text(json.dumps(record, ensure_ascii=False) + "\n\n", encoding="utf-8")
    (tmp_path / "c.json").write_text(json.dumps({"casos": [{"id": "a", "contexto": ctx}]}), encoding="utf-8")
    out = tmp_path / "saida" / "demo.json"
    assert make_demo_store.main(["--responses", str(tmp_path / "r.jsonl"), "--cases", str(tmp_path / "c.json"), "--out", str(out)]) == 0
    assert svc.context_key(ctx) in svc.load_demo_store(out)


def test_api_address_lives_only_in_the_client_module():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    holders = [
        p.relative_to(root).as_posix()
        for folder in ("core", "app")
        if (root / folder).exists()
        for p in (root / folder).rglob("*.py")
        if "api.openai.com" in p.read_text(encoding="utf-8")
    ]
    assert holders == ["core/llm_client.py"]


def test_record_demo_entry_creates_updates_and_is_replayed(tmp_path):
    ctx_a, ctx_b = _ctx(), _ctx(n_observations=61)
    path = tmp_path / "dados" / "demo.json"
    key = svc.record_demo_entry(path, ctx_a, runner.canned_answer(ctx_a))
    assert key == svc.context_key(ctx_a)
    svc.record_demo_entry(path, ctx_b, runner.canned_answer(ctx_b))
    saved = svc.load_demo_store(path)
    assert set(saved) == {svc.context_key(ctx_a), svc.context_key(ctx_b)}
    header = json.loads(path.read_text(encoding="utf-8"))
    assert header["prompt_fingerprint"] == svc.APPROVED_FINGERPRINT and header["modelo"] == "gpt-5-mini"
    out = svc.explain(ctx_a, mode=svc.MODE_DEMO, demo_store=saved)
    assert out.status == svc.STATUS_DEMO and out.shown


def test_record_demo_entry_recovers_from_broken_file(tmp_path):
    ctx = _ctx()
    path = tmp_path / "demo.json"
    path.write_text("{ não é json", encoding="utf-8")
    svc.record_demo_entry(path, ctx, runner.canned_answer(ctx))
    assert list(svc.load_demo_store(path)) == [svc.context_key(ctx)]
    path.write_text("[1, 2]", encoding="utf-8")
    svc.record_demo_entry(path, ctx, runner.canned_answer(ctx))
    path.write_text(json.dumps({"respostas": "x"}), encoding="utf-8")
    svc.record_demo_entry(path, ctx, runner.canned_answer(ctx))
    assert list(svc.load_demo_store(path)) == [svc.context_key(ctx)]
