"""
Provedor da camada de linguagem v1.0-experimental (etapa 6 da DL2, DL2-C e DL2-I).

A troca de provedor é configuração, não protocolo: o prompt, o esquema, os textos
fixos (hashes de core/llm_exp_prompts.py), o conjunto de casos e o template
congelados não mudam. Este módulo não altera core/llm_client.py, que guarda as
regras aprovadas da 7B (v0.6, gpt-5-mini).

Provedor de referência (DL2-I, 13/11/2026): xAI, modelo `grok-4.3`.
- Preço conferido na documentação da xAI em 13/11/2026: US$ 1,25 por milhão de
  tokens de entrada e US$ 2,50 por milhão de saída, abaixo de 200 mil tokens no
  pedido; a partir disso, US$ 2,50 e US$ 5,00 para todos os tokens do pedido.
- A xAI marca Chat Completions como obsoleto e recomenda a Responses API
  (`POST /v1/responses`, esquema em `text.format`, com `strict: true`).
- Temperatura aceita de 0 a 2 (amostragem limitada a 1): fica fixa em 0. Desvio
  documentado da recomendação da xAI (0,7): a reprodutibilidade vem antes da fluência.
- Seed: não documentado. Sem seed, cada caso roda duas vezes e a variação é registrada.
- Não há snapshot datado publicado para o grok-4.3: fixa-se o nome `grok-4.3`, e
  cada chamada registra o modelo que a API devolve. Mudança de versão anula a
  ratificação. Se o grok-4.3 não estiver na lista de modelos da conta, a reserva é
  `grok-4.20-0309-non-reasoning` (snapshot datado, mesmo preço), com novo registro.
- Rodada: 33 casos x 2 execuções = 66 chamadas por modelo; tetos de US$ 16 e 200 chamadas.
- A chave vem só da variável de ambiente XAI_API_KEY e nunca é gravada.

Toda chamada de rede passa por `transport`, para os testes usarem um cliente simulado.
Nenhuma chamada é feita sem um `BudgetLedger` com saldo (teto de US$ 16).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from core.llm_client import MAX_RETRIES, RETRY_STATUS, TIMEOUT_S, ApiError, CallFailed

BUDGET_CAP_USD = 16.0
MAX_CALLS = 200
# Contador da rodada de avaliação: em logs/, pasta fora do git (.gitignore).
LEDGER_FILE = Path(__file__).resolve().parent.parent / "logs" / "llm_custos_xai.jsonl"
RUNS_WITHOUT_SEED = 2


@dataclass(frozen=True)
class Provider:
    name: str
    api_url: str
    model: str
    key_env: str
    price_in: float                 # US$ por milhão de tokens, pedidos abaixo do limite
    price_out: float
    long_context_tokens: int        # a partir daqui, vale o preço de contexto longo
    long_price_in: float
    long_price_out: float
    temperature: Optional[float]
    seed: Optional[int]
    reasoning_effort: Optional[str]
    max_output_tokens: int = 1400


XAI = Provider(
    name="xAI",
    api_url="https://api.x.ai/v1/responses",
    model="grok-4.3",
    key_env="XAI_API_KEY",
    price_in=1.25,
    price_out=2.50,
    long_context_tokens=200_000,
    long_price_in=2.50,
    long_price_out=5.00,
    temperature=0.0,
    seed=None,                      # não documentado pela xAI (13/11/2026)
    reasoning_effort="low",         # padrão do grok-4.3
)

# Reserva, só se o grok-4.3 não constar da lista de modelos da conta (DL2-I). Modelo sem
# raciocínio: o campo de esforço de raciocínio não é enviado. Usá-lo exige novo registro.
XAI_FALLBACK = Provider(
    name="xAI",
    api_url="https://api.x.ai/v1/responses",
    model="grok-4.20-0309-non-reasoning",
    key_env="XAI_API_KEY",
    price_in=1.25,
    price_out=2.50,
    long_context_tokens=200_000,
    long_price_in=2.50,
    long_price_out=5.00,
    temperature=0.0,
    seed=None,
    reasoning_effort=None,
)

PROVIDER_RESTRICTIONS = (
    "Seed não documentado: cada caso roda duas vezes e a variação entre as execuções é registrada.",
    "Sem snapshot datado do grok-4.3: o nome fica fixo e cada chamada registra o modelo devolvido pela API.",
    "Chat Completions obsoleto na xAI: a chamada usa a Responses API, com o mesmo esquema em modo estrito.",
    "Desvio documentado: a xAI recomenda temperatura 0,7; o Argos usa 0, porque a reprodutibilidade "
    "dos testes vem antes da fluência do texto. Revisão só em versão futura, nunca no meio da rodada.",
)


class BudgetExceeded(Exception):
    """A chamada passaria do teto de custo ou de chamadas da rodada."""


def api_key(provider: Provider = XAI) -> Optional[str]:
    """Chave da variável de ambiente do provedor, ou None. Nunca é registrada."""
    key = os.environ.get(provider.key_env, "").strip()
    return key or None


def estimate_cost(provider: Provider, input_tokens: int, output_tokens: int) -> float:
    """Custo em US$. Pedido com contexto longo paga o preço maior em todos os tokens."""
    if input_tokens >= provider.long_context_tokens:
        price_in, price_out = provider.long_price_in, provider.long_price_out
    else:
        price_in, price_out = provider.price_in, provider.price_out
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000


def build_payload(provider: Provider, messages: list, response_format: dict) -> dict:
    """Corpo da Responses API a partir das mensagens e do esquema congelados."""
    schema = response_format["json_schema"]
    payload = {
        "model": provider.model,
        "input": messages,
        "text": {"format": {"type": "json_schema", "name": schema["name"], "schema": schema["schema"],
                            "strict": True}},
        "max_output_tokens": provider.max_output_tokens,
        "store": False,
    }
    if provider.temperature is not None:
        payload["temperature"] = provider.temperature
    if provider.seed is not None:
        payload["seed"] = provider.seed
    if provider.reasoning_effort:
        payload["reasoning"] = {"effort": provider.reasoning_effort}
    return payload


def parse_response(data: dict) -> dict:
    """Texto, motivo de término, tokens e modelo devolvido pela Responses API."""
    texts = []
    for item in data.get("output") or []:
        if item.get("type") != "message":
            continue
        for part in item.get("content") or []:
            if part.get("type") == "output_text":
                texts.append(part.get("text") or "")
    usage = data.get("usage") or {}
    return {
        "raw": "".join(texts) or (data.get("output_text") or ""),
        "finish_reason": data.get("status"),
        "input_tokens": int(usage.get("input_tokens", 0)),
        "output_tokens": int(usage.get("output_tokens", 0)),
        "model_version": data.get("model") or "",
    }


def http_transport(provider: Provider, payload: dict, key: str, timeout: float = TIMEOUT_S) -> dict:
    """Chamada real (não usada nos testes)."""
    request = urllib.request.Request(
        provider.api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
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


class BudgetLedger:
    """
    Contador de custo da rodada, num arquivo JSONL próprio (DL2-C). Cada linha guarda
    provedor, modelo pedido, modelo devolvido, tokens, custo, caso e horário; nunca o
    texto gerado, o contexto ou a chave.
    """

    def __init__(self, path: Path | str, cap_usd: float = BUDGET_CAP_USD, max_calls: int = MAX_CALLS) -> None:
        self.path = Path(path)
        self.cap_usd = cap_usd
        self.max_calls = max_calls

    def entries(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def spent(self) -> float:
        return sum(float(e.get("custo_usd", 0.0)) for e in self.entries())

    def check(self, provider: Provider, input_tokens: int) -> None:
        """Recusa a chamada se passar do teto de chamadas ou se o pior caso dela (saída máxima) passar do teto de custo."""
        if len(self.entries()) >= self.max_calls:
            raise BudgetExceeded(f"Teto de {self.max_calls} chamadas atingido.")
        worst = estimate_cost(provider, input_tokens, provider.max_output_tokens)
        if self.spent() + worst > self.cap_usd:
            raise BudgetExceeded(
                f"Teto de US$ {self.cap_usd:.2f} atingido: gasto US$ {self.spent():.4f}, "
                f"pior caso da chamada US$ {worst:.4f}."
            )

    def record(self, provider: Provider, result: dict, case_id: str, now: Callable = None) -> dict:
        now = now or (lambda: datetime.now(timezone.utc))
        entry = {
            "horario": now().isoformat(timespec="seconds"),
            "caso": case_id,
            "provedor": provider.name,
            "modelo_pedido": provider.model,
            "modelo_devolvido": result.get("model_version", ""),
            "tokens_entrada": result["input_tokens"],
            "tokens_saida": result["output_tokens"],
            "custo_usd": round(estimate_cost(provider, result["input_tokens"], result["output_tokens"]), 6),
            "temperatura": provider.temperature,
            "seed": provider.seed,
            "tentativas": result.get("attempts"),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry


def call_provider(
    provider: Provider,
    messages: list,
    response_format: dict,
    key: str,
    ledger: BudgetLedger,
    case_id: str,
    estimated_input_tokens: int,
    transport: Callable = http_transport,
    sleep: Callable = time.sleep,
    clock: Callable = time.monotonic,
) -> dict:
    """
    Uma chamada com as mesmas regras de rede da 7B (timeout de 20 s, até 2 retentativas
    em 429, 5xx e falha de rede). Confere o teto antes e registra o custo depois.
    Levanta BudgetExceeded ou CallFailed.
    """
    if not key:
        raise CallFailed("sem chave da API", 0, 0.0)
    ledger.check(provider, estimated_input_tokens)
    payload = build_payload(provider, messages, response_format)
    started = clock()
    attempts = 0
    last = "erro desconhecido"
    while attempts <= MAX_RETRIES:
        attempts += 1
        try:
            data = transport(provider, payload, key, TIMEOUT_S)
        except ApiError as exc:
            last = f"HTTP {exc.status}"
            if exc.status in RETRY_STATUS and attempts <= MAX_RETRIES:
                sleep(2 ** (attempts - 1))
                continue
            break
        except (TimeoutError, OSError) as exc:
            last = f"rede: {type(exc).__name__}"
            if attempts <= MAX_RETRIES:
                sleep(2 ** (attempts - 1))
                continue
            break
        result = {**parse_response(data), "latency_s": round(clock() - started, 3), "attempts": attempts}
        result["log"] = ledger.record(provider, result, case_id)
        return result
    raise CallFailed(last, attempts, round(clock() - started, 3))
