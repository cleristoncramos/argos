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
- Ajuste operacional (DL2-I, 13/11/2026): tempo limite de 120 s por tentativa, só neste provedor
  (o grok-4.3 com raciocínio passa de 20 s; a 7B mantém 20 s), com as mesmas 3 tentativas. O
  contador reserva o custo de pior caso ANTES de cada tentativa; a resposta troca a reserva pelo
  valor real, e a tentativa sem resposta fica com a reserva até a conferência no console.
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

from core.llm_client import MAX_RETRIES, RETRY_STATUS, ApiError, CallFailed

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
    timeout_s: float = 20.0          # por tentativa; o padrão é o da 7B
    # Saída usada na reserva de pior caso. Na xAI, os tokens de raciocínio contam como saída e
    # passam de `max_output_tokens` (aquecimento: 1.457 a 1.534 com limite de 1.400).
    reserve_output_tokens: int = 1400


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
    timeout_s=120.0,                # DL2-I: o raciocínio passa de 20 s
    reserve_output_tokens=3000,     # cerca do dobro da saída medida no aquecimento
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
    timeout_s=120.0,
    reserve_output_tokens=3000,
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
    details = usage.get("output_tokens_details") or {}
    return {
        "raw": "".join(texts) or (data.get("output_text") or ""),
        "finish_reason": data.get("status"),
        "input_tokens": int(usage.get("input_tokens", 0)),
        "output_tokens": int(usage.get("output_tokens", 0)),
        "reasoning_tokens": int(details.get("reasoning_tokens", 0)),
        "reasoning_effort": (data.get("reasoning") or {}).get("effort") or "",
        "model_version": data.get("model") or "",
    }


def http_transport(provider: Provider, payload: dict, key: str, timeout: Optional[float] = None) -> dict:
    """Chamada real (não usada nos testes)."""
    request = urllib.request.Request(
        provider.api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=provider.timeout_s if timeout is None else timeout) as response:
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
    Contador de custo da fase, num arquivo JSONL próprio (DL2-C e regra da fase 1): uma linha por
    TENTATIVA. Antes de cada tentativa, `reserve` grava o custo de pior caso; com resposta, `settle`
    troca a reserva pelo valor real; sem resposta, `fail` mantém a reserva até a conferência no
    console. O total é a soma de todas as linhas, inclusive reservas, e é sobre ele que valem os
    tetos de US$ 16 e 200 tentativas. Nunca guarda o texto gerado, o contexto ou a chave.
    """

    RESERVED, ANSWERED, NO_ANSWER = "reservada", "resposta", "sem_resposta"

    def __init__(self, path: Path | str, cap_usd: float = BUDGET_CAP_USD, max_calls: int = MAX_CALLS) -> None:
        self.path = Path(path)
        self.cap_usd = cap_usd
        self.max_calls = max_calls

    def entries(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _write(self, entries: list[dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        text = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries)
        self.path.write_text(text, encoding="utf-8")

    def spent(self) -> float:
        """Soma de tudo o que está no contador: valores reais e reservas."""
        return sum(float(e.get("custo_usd", 0.0)) for e in self.entries())

    def worst_case(self, provider: Provider, input_tokens: int) -> float:
        return estimate_cost(provider, input_tokens, max(provider.max_output_tokens, provider.reserve_output_tokens))

    def check(self, provider: Provider, input_tokens: int) -> None:
        """Recusa a tentativa se passar do teto de tentativas ou se a reserva dela passar do teto de custo."""
        if len(self.entries()) >= self.max_calls:
            raise BudgetExceeded(f"Teto de {self.max_calls} chamadas atingido.")
        worst = self.worst_case(provider, input_tokens)
        if self.spent() + worst > self.cap_usd:
            raise BudgetExceeded(
                f"Teto de US$ {self.cap_usd:.2f} atingido: gasto US$ {self.spent():.4f}, "
                f"pior caso da chamada US$ {worst:.4f}."
            )

    def reserve(self, provider: Provider, case_id: str, attempt: int, input_tokens: int,
                now: Callable = None) -> int:
        """Grava a reserva de pior caso antes da tentativa; devolve o número da linha."""
        now = now or (lambda: datetime.now(timezone.utc))
        worst = round(self.worst_case(provider, input_tokens), 6)
        entries = self.entries()
        entries.append({
            "horario": now().isoformat(timespec="seconds"),
            "caso": case_id,
            "tentativa": attempt,
            "situacao": self.RESERVED,
            "provedor": provider.name,
            "modelo_pedido": provider.model,
            "modelo_devolvido": "",
            "tokens_entrada": input_tokens,
            "tokens_saida": 0,
            "tokens_raciocinio": 0,
            "esforco_devolvido": "",
            "custo_reservado_usd": worst,
            "custo_usd": worst,
            "temperatura": provider.temperature,
            "seed": provider.seed,
            "tempo_limite_s": provider.timeout_s,
            "motivo": "",
        })
        self._write(entries)
        return len(entries) - 1

    def settle(self, index: int, provider: Provider, result: dict) -> dict:
        """Troca a reserva pelo valor real da resposta."""
        entries = self.entries()
        entry = entries[index]
        entry.update(
            situacao=self.ANSWERED,
            modelo_devolvido=result.get("model_version", ""),
            tokens_entrada=result["input_tokens"],
            tokens_saida=result["output_tokens"],
            tokens_raciocinio=result.get("reasoning_tokens", 0),
            esforco_devolvido=result.get("reasoning_effort", ""),
            custo_usd=round(estimate_cost(provider, result["input_tokens"], result["output_tokens"]), 6),
        )
        self._write(entries)
        return entry

    def fail(self, index: int, reason: str) -> dict:
        """Tentativa sem resposta: a reserva fica como custo, até a conferência no console."""
        entries = self.entries()
        entries[index].update(situacao=self.NO_ANSWER, motivo=reason)
        self._write(entries)
        return entries[index]


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
    Uma chamada com até 3 tentativas (a primeira e até 2 novas, em 429, 5xx e falha de rede), com o
    tempo limite do provedor. Antes de CADA tentativa, confere o teto e reserva o custo de pior caso.
    Levanta BudgetExceeded ou CallFailed.
    """
    if not key:
        raise CallFailed("sem chave da API", 0, 0.0)
    payload = build_payload(provider, messages, response_format)
    started = clock()
    attempts = 0
    last = "erro desconhecido"
    while attempts <= MAX_RETRIES:
        ledger.check(provider, estimated_input_tokens)
        attempts += 1
        index = ledger.reserve(provider, case_id, attempts, estimated_input_tokens)
        try:
            data = transport(provider, payload, key, provider.timeout_s)
        except ApiError as exc:
            last = f"HTTP {exc.status}"
            ledger.fail(index, last)
            if exc.status in RETRY_STATUS and attempts <= MAX_RETRIES:
                sleep(2 ** (attempts - 1))
                continue
            break
        except (TimeoutError, OSError) as exc:
            last = f"rede: {type(exc).__name__}"
            ledger.fail(index, last)
            if attempts <= MAX_RETRIES:
                sleep(2 ** (attempts - 1))
                continue
            break
        result = {**parse_response(data), "latency_s": round(clock() - started, 3), "attempts": attempts}
        result["log"] = ledger.settle(index, provider, result)
        return result
    raise CallFailed(last, attempts, round(clock() - started, 3))
