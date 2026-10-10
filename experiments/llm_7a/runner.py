"""
Executor do experimento 7A: chama a API (ou um cliente simulado), valida cada
resposta e grava um registro por chamada em JSONL.

A chave da API vem SOMENTE da variável de ambiente OPENAI_API_KEY e nunca é
gravada em arquivo. Tudo que depende de rede passa por `transport`, para que
os testes usem um cliente simulado.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Iterable, Optional

from core import llm_eval, llm_prompts, llm_validation

API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODELS = ("gpt-5-mini", "gpt-5-nano")
DEFAULT_REPETITIONS = 3
TIMEOUT_S = 20
MAX_RETRIES = 2
UNSUPPORTED_MARKERS = ("unsupported", "not supported", "unrecognized", "unknown parameter")


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.message = message


def http_transport(payload: dict, api_key: str, timeout: float = TIMEOUT_S) -> dict:
    """Chamada real à API de chat (sem bibliotecas externas)."""
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            message = json.loads(body)["error"]["message"]
        except (ValueError, KeyError, TypeError):
            message = body[:300]
        raise ApiError(exc.code, message) from exc


def fake_transport(payload: dict, api_key: str, timeout: float = TIMEOUT_S) -> dict:
    """Cliente simulado (--dry-run): devolve uma resposta válida construída do contexto."""
    user = payload["messages"][-1]["content"]
    context = json.loads(user.split("Contexto JSON:\n", 1)[1].split("\n\nPedido do usuário", 1)[0])
    return {
        "choices": [{"message": {"content": json.dumps(canned_answer(context), ensure_ascii=False)}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 900, "completion_tokens": 350},
    }


def canned_answer(context: dict) -> dict:
    """Resposta determinística e válida; serve para testar o pipeline sem custo."""
    request = context.get("user_request")
    insufficient = context["status"] == "dados_insuficientes"
    if request:
        head = llm_prompts.REFUSAL_TEXT if request["type"] == "recomendacao" else llm_prompts.REFUSAL_FORECAST_TEXT
    elif insufficient:
        head = "Os dados do período escolhido são insuficientes para calcular as métricas."
    else:
        head = "Este é um resumo descritivo do comportamento histórico no período escolhido."
    metrics = [] if insufficient else [
        {"id": m["id"], "valor": m["value"], "unidade": m["unit"], "leitura": "Valor calculado pelo Argos para o período."}
        for m in context["metrics"][:6]
    ]
    limits = ["Resultados passados descrevem o histórico e não indicam o que acontecerá depois."]
    texts = {
        "poucas_observacoes": "Há poucas observações no período, o que torna a análise frágil.",
        "poucos_anos": "Há poucos anos disponíveis; a amostra é pequena.",
        "mes_em_andamento": "O mês atual está em andamento e foi excluído.",
        "preco_nao_positivo": "Houve preço menor ou igual a zero (zero ou negativo), por isso algumas métricas não foram calculadas.",
    }
    limits += [texts[f] for f in context["limitation_flags"]]
    return {
        "resumo": head,
        "recusa_recomendacao": bool(request),
        "filtros_aplicados": {
            "ativos": list(context["assets"]),
            "periodo_inicio": context["filters"]["period_start"],
            "periodo_fim": context["filters"]["period_end"],
            "frequencia": context["filters"]["frequency"],
        },
        "o_que_o_grafico_mostra": "Mostra como os valores do ativo variaram ao longo do período selecionado.",
        "metricas_relevantes": metrics,
        "limitacoes": limits[:6],
        "o_que_nao_pode_ser_concluido": ["Não é possível concluir se o ativo é adequado para uma pessoa ou o que ocorrerá depois."],
        "nota_educativa": "As métricas descrevem o passado e dependem do período escolhido.",
    }


def build_payload(model: str, context: dict, max_tokens: int, extra: Optional[dict] = None) -> dict:
    payload = {
        "model": model,
        "messages": llm_prompts.build_messages(context),
        "response_format": llm_prompts.response_format(),
        "max_completion_tokens": max_tokens,
    }
    payload.update(extra or {})
    return payload


def call_model(
    model: str,
    context: dict,
    api_key: str,
    transport: Callable = http_transport,
    max_tokens: int = 1400,
    params: Optional[dict] = None,
    sleep: Callable = time.sleep,
):
    """
    Uma chamada com tentativas e retirada automática de parâmetros que o modelo
    não aceite (ex.: reasoning_effort). Devolve (resposta, parâmetros_usados,
    parâmetros_removidos, latência_s, tentativas).
    """
    params = dict(params or {})
    removed = []
    attempts = 0
    started = time.monotonic()
    last = None
    while attempts <= MAX_RETRIES + len(params) + 1:
        attempts += 1
        payload = build_payload(model, context, max_tokens, params)
        try:
            data = transport(payload, api_key, TIMEOUT_S)
            return data, params, removed, time.monotonic() - started, attempts
        except ApiError as exc:
            last = exc
            lowered = exc.message.lower()
            if exc.status == 400 and any(k in lowered for k in UNSUPPORTED_MARKERS):
                culprit = next((p for p in params if p in lowered), None) or next(iter(params), None)
                if culprit is None:
                    break
                params.pop(culprit)
                removed.append(culprit)
                continue
            if exc.status in (429, 500, 502, 503, 504) and attempts <= MAX_RETRIES:
                sleep(2 ** attempts)
                continue
            break
        except (TimeoutError, OSError) as exc:  # inclui timeout de socket e URLError
            last = exc
            if attempts <= MAX_RETRIES:
                sleep(2 ** attempts)
                continue
            break
    raise RuntimeError(f"Falha na chamada: {last}")


def run_one(model, case, repetition, api_key, transport, max_tokens, params, known_tickers, sleep=time.sleep) -> dict:
    record = {
        "model": model,
        "case_id": case["id"],
        "repetition": repetition,
        "prompt_version": llm_prompts.PROMPT_VERSION,
        "prompt_fingerprint": llm_prompts.prompt_fingerprint(),
    }
    try:
        data, used, removed, latency, attempts = call_model(
            model, case["contexto"], api_key, transport, max_tokens, params, sleep
        )
    except RuntimeError as exc:
        record.update(error=str(exc), raw="", latency_s=0.0, cost_usd=0.0, input_tokens=0, output_tokens=0)
        result = llm_validation.validate_response("", case["contexto"], known_tickers)
        record["validation"] = {**result.as_dict(), "failed": result.failed}
        return record

    choice = (data.get("choices") or [{}])[0]
    raw = (choice.get("message") or {}).get("content") or ""
    usage = data.get("usage") or {}
    tokens_in, tokens_out = int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0))
    result = llm_validation.validate_response(raw, case["contexto"], known_tickers)
    record.update(
        raw=raw,
        finish_reason=choice.get("finish_reason"),
        input_tokens=tokens_in,
        output_tokens=tokens_out,
        latency_s=round(latency, 3),
        cost_usd=llm_eval.estimate_cost(model, tokens_in, tokens_out),
        attempts=attempts,
        params_used=used,
        params_removed=removed,
        validation={**result.as_dict(), "failed": result.failed},
    )
    return record


def load_done(path: Path) -> set:
    done = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["model"], r["case_id"], r["repetition"]))
    return done


def run_experiment(
    cases_payload: dict,
    out_path: Path,
    models: Iterable[str] = DEFAULT_MODELS,
    repetitions: int = DEFAULT_REPETITIONS,
    api_key: str = "",
    transport: Callable = http_transport,
    max_tokens: int = 1400,
    params: Optional[dict] = None,
    max_cost: float = 2.0,
    known_tickers: Iterable[str] = (),
    only_cases: Optional[Iterable[str]] = None,
    dry_run: bool = False,
    sleep: Callable = time.sleep,
    log: Callable = print,
) -> dict:
    """Roda tudo que ainda não foi gravado; interrompe se o custo passar de `max_cost`."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = load_done(out_path)
    spent = 0.0
    if out_path.exists():
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                spent += json.loads(line).get("cost_usd", 0.0)
    wanted = set(only_cases) if only_cases else None
    cases = [c for c in cases_payload["casos"] if wanted is None or c["id"] in wanted]
    ran = skipped = 0
    stopped = False
    with out_path.open("a", encoding="utf-8") as handle:
        for model in models:
            for case in cases:
                for repetition in range(1, repetitions + 1):
                    key = (model, case["id"], repetition)
                    if key in done:
                        skipped += 1
                        continue
                    if spent >= max_cost:
                        stopped = True
                        break
                    record = run_one(model, case, repetition, api_key, transport, max_tokens, params, known_tickers, sleep)
                    record["dry_run"] = dry_run
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                    handle.flush()
                    spent += record["cost_usd"]
                    ran += 1
                    log(f"{model} {case['id']} #{repetition}: {'ok' if record['validation']['ok'] else 'FALHOU ' + ','.join(record['validation']['failed'])}")
                if stopped:
                    break
            if stopped:
                break
    return {"executadas": ran, "puladas": skipped, "custo_total_usd": round(spent, 4), "interrompido_por_custo": stopped}


def get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise SystemExit("Defina OPENAI_API_KEY no terminal (a chave nunca entra no repositório).")
    return key
