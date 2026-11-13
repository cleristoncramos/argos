"""Provedor xAI (grok-4.3) da camada v1.0-experimental: etapa 6 da DL2, sem chamadas reais."""

import io
import json
import urllib.error
from datetime import datetime, timezone

import pytest

from core import llm_exp_prompts as ep
from core import llm_provider as lp
from core.llm_client import ApiError, CallFailed
from core.llm_exp_service import APPROVED_HASHES, current_hashes

FAKE_KEY = "chave-de-teste-nao-real"


def _response(text='{"ok": true}', model="grok-4.3", tokens=(2500, 600)):
    return {
        "id": "resp_1", "object": "response", "model": model, "status": "completed",
        "output": [
            {"type": "reasoning", "summary": []},
            {"type": "message", "content": [{"type": "output_text", "text": text}]},
        ],
        "usage": {"input_tokens": tokens[0], "output_tokens": tokens[1]},
    }


def _messages():
    return [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]


def test_troca_de_provedor_nao_muda_o_protocolo():
    # A impressão digital aprovada cobre prompt, instruções e esquema, não o modelo.
    hashes = current_hashes()
    assert {k: hashes[k] for k in ("prompt", "esquema", "impressao")} == {
        k: APPROVED_HASHES[k] for k in ("prompt", "esquema", "impressao")}
    assert lp.XAI.model not in json.dumps([ep.SYSTEM_PROMPT, ep.OUTPUT_SCHEMA])


def test_configuracao_registrada():
    assert (lp.XAI.name, lp.XAI.model, lp.XAI.key_env) == ("xAI", "grok-4.3", "XAI_API_KEY")
    assert lp.XAI.api_url == "https://api.x.ai/v1/responses"
    assert (lp.XAI.price_in, lp.XAI.price_out) == (1.25, 2.50)
    assert lp.XAI.temperature == 0.0 and lp.XAI.seed is None and lp.RUNS_WITHOUT_SEED == 2
    assert lp.BUDGET_CAP_USD == 16.0 and lp.MAX_CALLS == 200 and len(lp.PROVIDER_RESTRICTIONS) == 4
    assert "reprodutibilidade" in lp.PROVIDER_RESTRICTIONS[3]
    reserva = lp.XAI_FALLBACK
    assert reserva.model == "grok-4.20-0309-non-reasoning" and (reserva.price_in, reserva.price_out) == (1.25, 2.50)
    assert reserva.reasoning_effort is None and reserva.temperature == 0.0
    assert "reasoning" not in lp.build_payload(reserva, _messages(), ep.response_format())
    assert lp.LEDGER_FILE.parent.name == "logs"           # pasta ignorada pelo git


def test_chave_so_da_variavel_de_ambiente(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    assert lp.api_key() is None
    monkeypatch.setenv("XAI_API_KEY", "  ")
    assert lp.api_key() is None
    monkeypatch.setenv("XAI_API_KEY", f" {FAKE_KEY} ")
    assert lp.api_key() == FAKE_KEY


def test_custo_da_rodada_estimada():
    one = lp.estimate_cost(lp.XAI, 2500, 600)
    assert one == pytest.approx(0.004625)
    assert 33 * one == pytest.approx(0.152625)                      # 33 chamadas: US$ 0,15
    assert 66 * one == pytest.approx(0.30525)                       # 33 casos x 2 execuções: US$ 0,31
    assert 66 * lp.estimate_cost(lp.XAI, 2500, lp.XAI.max_output_tokens) < lp.BUDGET_CAP_USD
    assert lp.estimate_cost(lp.XAI, 200_000, 1000) == pytest.approx(0.505)   # contexto longo


def test_corpo_da_responses_api():
    payload = lp.build_payload(lp.XAI, _messages(), ep.response_format())
    assert payload["model"] == "grok-4.3" and payload["input"] == _messages()
    fmt = payload["text"]["format"]
    assert fmt["type"] == "json_schema" and fmt["strict"] is True and fmt["schema"] == ep.OUTPUT_SCHEMA
    assert payload["temperature"] == 0.0 and "seed" not in payload
    assert payload["reasoning"] == {"effort": "low"} and payload["store"] is False
    assert payload["max_output_tokens"] == 1400

    other = lp.Provider(**{**lp.XAI.__dict__, "temperature": None, "seed": 7, "reasoning_effort": None})
    payload = lp.build_payload(other, _messages(), ep.response_format())
    assert "temperature" not in payload and payload["seed"] == 7 and "reasoning" not in payload


def test_leitura_da_resposta():
    parsed = lp.parse_response(_response(model="grok-4.3-0101"))
    assert parsed == {"raw": '{"ok": true}', "finish_reason": "completed", "input_tokens": 2500,
                      "output_tokens": 600, "model_version": "grok-4.3-0101"}
    assert lp.parse_response({"output_text": "x"})["raw"] == "x"
    assert lp.parse_response({})["model_version"] == "" and lp.parse_response({})["input_tokens"] == 0


def test_registro_sem_chave_nem_texto(tmp_path):
    ledger = lp.BudgetLedger(tmp_path / "custos" / "rodada.jsonl")
    assert ledger.entries() == [] and ledger.spent() == 0
    fixed = lambda: datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
    result = lp.call_provider(lp.XAI, _messages(), ep.response_format(), FAKE_KEY, ledger, "C01", 2500,
                              transport=lambda *a: _response(text="segredo do texto"))
    entry = ledger.entries()[0]
    assert result["raw"] == "segredo do texto" and result["attempts"] == 1
    assert entry["modelo_pedido"] == "grok-4.3" and entry["modelo_devolvido"] == "grok-4.3"
    assert entry["custo_usd"] == pytest.approx(0.004625) and entry["caso"] == "C01"
    content = (tmp_path / "custos" / "rodada.jsonl").read_text(encoding="utf-8")
    assert FAKE_KEY not in content and "segredo do texto" not in content
    assert ledger.record(lp.XAI, {"input_tokens": 1, "output_tokens": 1}, "C02", now=fixed)["horario"] \
        == "2026-11-13T12:00:00+00:00"


def test_teto_de_custo(tmp_path):
    ledger = lp.BudgetLedger(tmp_path / "r.jsonl", cap_usd=0.01)
    lp.call_provider(lp.XAI, _messages(), ep.response_format(), FAKE_KEY, ledger, "C01", 2500,
                     transport=lambda *a: _response(tokens=(2500, 3000)))
    calls = []
    with pytest.raises(lp.BudgetExceeded, match="Teto de US\\$ 0.01"):
        lp.call_provider(lp.XAI, _messages(), ep.response_format(), FAKE_KEY, ledger, "C02", 2500,
                         transport=lambda *a: calls.append(1))
    assert calls == []                                       # nada chega à API


def test_teto_de_chamadas(tmp_path):
    ledger = lp.BudgetLedger(tmp_path / "r.jsonl", max_calls=2)
    for case in ("C01", "C02"):
        lp.call_provider(lp.XAI, _messages(), ep.response_format(), FAKE_KEY, ledger, case, 100,
                         transport=lambda *a: _response())
    with pytest.raises(lp.BudgetExceeded, match="Teto de 2 chamadas"):
        lp.call_provider(lp.XAI, _messages(), ep.response_format(), FAKE_KEY, ledger, "C03", 100,
                         transport=lambda *a: pytest.fail("não deveria chamar"))


def test_sem_chave_nao_chama(tmp_path):
    with pytest.raises(CallFailed, match="sem chave"):
        lp.call_provider(lp.XAI, _messages(), ep.response_format(), "", lp.BudgetLedger(tmp_path / "r.jsonl"),
                         "C01", 100, transport=lambda *a: pytest.fail("não deveria chamar"))


def test_retentativas(tmp_path):
    ledger = lp.BudgetLedger(tmp_path / "r.jsonl")
    script = [ApiError(503, "ocupado"), TimeoutError(), _response()]

    def flaky(*args):
        step = script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step

    sleeps = []
    result = lp.call_provider(lp.XAI, _messages(), ep.response_format(), FAKE_KEY, ledger, "C01", 100,
                              transport=flaky, sleep=sleeps.append)
    assert result["attempts"] == 3 and sleeps == [1, 2]

    def bad_request(*args):
        raise ApiError(400, "pedido inválido")

    with pytest.raises(CallFailed, match="HTTP 400") as info:
        lp.call_provider(lp.XAI, _messages(), ep.response_format(), FAKE_KEY, ledger, "C02", 100,
                         transport=bad_request, sleep=sleeps.append)
    assert info.value.attempts == 1

    def offline(*args):
        raise OSError("sem rede")

    with pytest.raises(CallFailed, match="rede: OSError") as info:
        lp.call_provider(lp.XAI, _messages(), ep.response_format(), FAKE_KEY, ledger, "C03", 100,
                         transport=offline, sleep=lambda s: None)
    assert info.value.attempts == 3


def test_transporte_http(monkeypatch):
    seen = {}

    class FakeResponse(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fake_urlopen(request, timeout):
        seen["url"], seen["auth"], seen["timeout"] = request.full_url, request.headers["Authorization"], timeout
        return FakeResponse(json.dumps(_response()).encode())

    monkeypatch.setattr(lp.urllib.request, "urlopen", fake_urlopen)
    assert lp.http_transport(lp.XAI, {"x": 1}, FAKE_KEY)["model"] == "grok-4.3"
    assert seen == {"url": lp.XAI.api_url, "auth": f"Bearer {FAKE_KEY}", "timeout": 20}

    def http_error(body):
        def raise_(request, timeout):
            raise urllib.error.HTTPError(lp.XAI.api_url, 401, "x", {}, io.BytesIO(body))
        return raise_

    monkeypatch.setattr(lp.urllib.request, "urlopen", http_error('{"error": {"message": "chave inválida"}}'.encode()))
    with pytest.raises(ApiError, match="chave inválida"):
        lp.http_transport(lp.XAI, {}, FAKE_KEY)
    monkeypatch.setattr(lp.urllib.request, "urlopen", http_error(b"texto solto"))
    with pytest.raises(ApiError, match="texto solto"):
        lp.http_transport(lp.XAI, {}, FAKE_KEY)
