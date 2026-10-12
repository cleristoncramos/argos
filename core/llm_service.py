"""
Serviço de explicação assistida (etapa 7B, primeiro bloco: sem interface).

Fluxo único e fechado:
    contexto JSON do Argos -> (LLM ou resposta salva) -> validador -> exibir ou fallback.
Nada é devolvido para exibição sem passar pelo validador. Em qualquer falha,
bloqueio ou indisponibilidade o resultado traz o texto educativo fixo.

Não aceita entrada livre do usuário (contexto com `user_request` é recusado
antes de qualquer chamada). Não registra a chave da API nem o texto da resposta.

Premissas de projeto (a confirmar com o orientador):
- limite padrão de uso por sessão: 20 chamadas e US$ 0,50 de custo estimado;
- o registro de uso guarda hashes, tokens, custo, status e motivo, sem o texto gerado.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable, Optional

from core import llm_client, llm_eval, llm_prompts, llm_validation

APPROVED_PROMPT_VERSION = "v0.6"
APPROVED_FINGERPRINT = "e3b3574b7430"

MODE_OFF = "off"
MODE_DEMO = "demo"
MODE_LIVE = "live"
MODES = (MODE_OFF, MODE_DEMO, MODE_LIVE)

STATUS_OK = "ok"
STATUS_DEMO = "demo"
STATUS_BLOCKED = "bloqueada"
STATUS_UNAVAILABLE = "indisponivel"
STATUS_OFF = "desativada"

FALLBACK_TEXT = (
    "A explicação automática não está disponível agora. Os gráficos, as métricas e os textos "
    "educativos do Argos DataLab continuam disponíveis. Os dados são históricos e a análise "
    "tem finalidade educativa; não é recomendação de investimento."
)

REQUIRED_CONTEXT_KEYS = (
    "analysis_type", "status", "assets", "filters", "n_observations",
    "metrics", "limitation_flags", "notes",
)

DEFAULT_MAX_CALLS = 20
DEFAULT_MAX_COST_USD = 0.50


@dataclass
class UsageLimiter:
    """Limite de uso e de custo (por sessão). Conta toda chamada tentada."""

    max_calls: int = DEFAULT_MAX_CALLS
    max_cost_usd: float = DEFAULT_MAX_COST_USD
    calls: int = 0
    cost_usd: float = 0.0

    def check(self) -> Optional[str]:
        if self.calls >= self.max_calls:
            return "limite_de_uso"
        if self.cost_usd >= self.max_cost_usd:
            return "limite_de_custo"
        return None

    def record(self, cost_usd: float = 0.0) -> None:
        self.calls += 1
        self.cost_usd += cost_usd


@dataclass
class Explanation:
    status: str
    data: Optional[dict]
    reason: str
    log: dict = field(default_factory=dict)

    @property
    def shown(self) -> bool:
        """True se há resposta validada para exibir (viva ou salva)."""
        return self.data is not None

    @property
    def fallback_text(self) -> Optional[str]:
        return None if self.shown else FALLBACK_TEXT


def context_key(context: dict) -> str:
    """Identificador estável do contexto (hash do JSON canônico)."""
    material = json.dumps(context, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def load_demo_store(path) -> dict:
    """Respostas salvas: {chave_do_contexto: texto JSON bruto}. Arquivo ausente -> vazio."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("respostas", {}) if isinstance(data, dict) else {}


def build_demo_store(records: Iterable[dict], cases: Iterable[dict], model: str = llm_client.MODEL) -> dict:
    """
    Monta o arquivo de demonstração a partir de registros da 7A: só respostas
    válidas do modelo principal, sem simulação (dry-run) e do prompt aprovado,
    uma por contexto.
    """
    contexts = {c["id"]: c["contexto"] for c in cases}
    store: dict = {}
    for record in records:
        if (
            record.get("model") != model
            or record.get("dry_run")
            or not record.get("validation", {}).get("ok")
            or record.get("prompt_fingerprint") != APPROVED_FINGERPRINT
            or record.get("case_id") not in contexts
        ):
            continue
        store.setdefault(context_key(contexts[record["case_id"]]), record["raw"])
    return {
        "prompt_version": APPROVED_PROMPT_VERSION,
        "prompt_fingerprint": APPROVED_FINGERPRINT,
        "modelo": model,
        "respostas": store,
    }


def append_log(path, record: dict) -> None:
    """Acrescenta um registro de uso (JSONL). Nunca recebe a chave nem o texto gerado."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _config_problem(context: dict) -> Optional[str]:
    if llm_prompts.PROMPT_VERSION != APPROVED_PROMPT_VERSION or llm_prompts.prompt_fingerprint() != APPROVED_FINGERPRINT:
        return "prompt_divergente"
    if not isinstance(context, dict) or any(k not in context for k in REQUIRED_CONTEXT_KEYS):
        return "contexto_invalido"
    if context.get("user_request"):
        return "entrada_livre_nao_permitida"
    return None


def _result(status: str, data: Optional[dict], reason: str, log: dict, log_sink) -> Explanation:
    log["status"] = status
    log["reason"] = reason
    if log_sink is not None:
        log_sink(log)
    return Explanation(status, data, reason, log)


def explain(
    context: dict,
    *,
    mode: str = MODE_OFF,
    api_key: Optional[str] = None,
    transport: Callable = llm_client.http_transport,
    known_tickers: Iterable[str] = (),
    demo_store: Optional[dict] = None,
    limiter: Optional[UsageLimiter] = None,
    log_sink: Optional[Callable] = None,
    sleep: Callable = time.sleep,
    clock: Callable = time.monotonic,
    now: Callable = lambda: datetime.now(timezone.utc),
) -> Explanation:
    """Gera (ou recupera) a explicação validada para um contexto, ou o fallback."""
    if mode not in MODES:
        raise ValueError(f"Modo inválido: {mode}.")
    log = {
        "timestamp": now().isoformat(timespec="seconds"),
        "mode": mode,
        "model": llm_client.MODEL if mode == MODE_LIVE else None,
        "prompt_version": llm_prompts.PROMPT_VERSION,
        "prompt_fingerprint": llm_prompts.prompt_fingerprint(),
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
        "latency_s": 0.0,
        "attempts": 0,
        "failed_checks": [],
    }
    if mode == MODE_OFF:
        return _result(STATUS_OFF, None, "desativado", log, log_sink)

    problem = _config_problem(context)
    if problem:
        return _result(STATUS_BLOCKED, None, problem, log, log_sink)
    log["context_key"] = context_key(context)

    if mode == MODE_DEMO:
        raw = (demo_store or {}).get(log["context_key"])
        if raw is None:
            return _result(STATUS_UNAVAILABLE, None, "demo_sem_resposta_salva", log, log_sink)
        return _finish(raw, context, known_tickers, log, log_sink, STATUS_DEMO)

    # modo ao vivo ------------------------------------------------------
    if not api_key:
        return _result(STATUS_UNAVAILABLE, None, "sem_chave", log, log_sink)
    limiter = limiter if limiter is not None else UsageLimiter()
    limited = limiter.check()
    if limited:
        return _result(STATUS_UNAVAILABLE, None, limited, log, log_sink)
    try:
        call = llm_client.call_model(context, api_key, transport, sleep, clock)
    except llm_client.CallFailed as exc:
        limiter.record(0.0)
        log["attempts"], log["latency_s"] = exc.attempts, exc.latency_s
        return _result(STATUS_UNAVAILABLE, None, f"api_indisponivel:{exc}", log, log_sink)
    cost = llm_eval.estimate_cost(llm_client.MODEL, call["input_tokens"], call["output_tokens"])
    limiter.record(cost)
    log.update(
        input_tokens=call["input_tokens"], output_tokens=call["output_tokens"],
        cost_usd=round(cost, 6), latency_s=call["latency_s"], attempts=call["attempts"],
    )
    if call["finish_reason"] != "stop":
        return _result(STATUS_BLOCKED, None, "resposta_incompleta", log, log_sink)
    return _finish(call["raw"], context, known_tickers, log, log_sink, STATUS_OK)


def _finish(raw: str, context: dict, known_tickers, log: dict, log_sink, ok_status: str) -> Explanation:
    """Validação obrigatória antes de qualquer exibição."""
    log["response_sha256"] = hashlib.sha256(str(raw).encode("utf-8")).hexdigest()[:16]
    result = llm_validation.validate_response(raw, context, known_tickers)
    if not result.ok:
        log["failed_checks"] = result.failed
        return _result(STATUS_BLOCKED, None, "validacao_reprovada", log, log_sink)
    return _result(ok_status, json.loads(raw), "", log, log_sink)
