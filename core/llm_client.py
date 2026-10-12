"""
Cliente da API de chat para a explicação assistida (etapa 7B).

Regras fixas aprovadas: modelo principal gpt-5-mini, prompt v0.6 congelado,
saída em JSON Schema estrito, teto de 1.400 tokens, timeout de 20 s por
tentativa e no máximo 2 retentativas. Sem bibliotecas externas. A chave da API
vem de fora (variável de ambiente ou segredo do app) e nunca é gravada.

Toda chamada de rede passa por `transport`, para que os testes usem um cliente
simulado.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Callable, Optional

from core import llm_prompts

API_URL = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-5-mini"
MAX_OUTPUT_TOKENS = 1400
TIMEOUT_S = 20
MAX_RETRIES = 2
REASONING_EFFORT = "minimal"
RETRY_STATUS = (429, 500, 502, 503, 504)


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.message = message


class CallFailed(Exception):
    """A chamada não produziu resposta, mesmo com as retentativas permitidas."""

    def __init__(self, message: str, attempts: int, latency_s: float):
        super().__init__(message)
        self.attempts = attempts
        self.latency_s = latency_s


def api_key_from_env() -> Optional[str]:
    """Chave da variável OPENAI_API_KEY, ou None se ausente ou vazia."""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    return key or None


def http_transport(payload: dict, api_key: str, timeout: float = TIMEOUT_S) -> dict:
    """Chamada real à API de chat."""
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


def build_payload(context: dict) -> dict:
    """Corpo da requisição: só o prompt congelado e o contexto estruturado."""
    return {
        "model": MODEL,
        "messages": llm_prompts.build_messages(context),
        "response_format": llm_prompts.response_format(),
        "max_completion_tokens": MAX_OUTPUT_TOKENS,
        "reasoning_effort": REASONING_EFFORT,
    }


def call_model(
    context: dict,
    api_key: str,
    transport: Callable = http_transport,
    sleep: Callable = time.sleep,
    clock: Callable = time.monotonic,
) -> dict:
    """
    Uma chamada com até MAX_RETRIES retentativas (429, 5xx, timeout e falha de rede).
    Erros do tipo 4xx (exceto 429) não são repetidos. Devolve
    {"raw", "finish_reason", "input_tokens", "output_tokens", "latency_s", "attempts"}
    ou levanta CallFailed.
    """
    payload = build_payload(context)
    started = clock()
    attempts = 0
    last = "erro desconhecido"
    while attempts <= MAX_RETRIES:
        attempts += 1
        try:
            data = transport(payload, api_key, TIMEOUT_S)
        except ApiError as exc:
            last = f"HTTP {exc.status}"
            if exc.status in RETRY_STATUS and attempts <= MAX_RETRIES:
                sleep(2 ** (attempts - 1))
                continue
            break
        except (TimeoutError, OSError) as exc:  # inclui URLError e timeout de socket
            last = f"rede: {type(exc).__name__}"
            if attempts <= MAX_RETRIES:
                sleep(2 ** (attempts - 1))
                continue
            break
        choice = (data.get("choices") or [{}])[0]
        usage = data.get("usage") or {}
        return {
            "raw": (choice.get("message") or {}).get("content") or "",
            "finish_reason": choice.get("finish_reason"),
            "input_tokens": int(usage.get("prompt_tokens", 0)),
            "output_tokens": int(usage.get("completion_tokens", 0)),
            "latency_s": round(clock() - started, 3),
            "attempts": attempts,
        }
    raise CallFailed(last, attempts, round(clock() - started, 3))
