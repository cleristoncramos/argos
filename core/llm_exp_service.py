"""
Serviço da camada de linguagem v1.0-experimental.

Fluxo fechado, igual ao da v0.6:
    contexto do Argos -> (modelo ou resposta salva) -> validador v1.0 -> exibir ou fallback.

Diferenças:
- só roda no ambiente experimental restrito (no público é bloqueado antes de
  qualquer chamada);
- nos modos ao vivo e de demonstração, só produz texto para exibir se a
  impressão digital e os hashes do prompt, do esquema e dos textos fixos forem
  os aprovados (`APPROVED_FINGERPRINT` e `APPROVED_HASHES`);
  enquanto não houver aprovação, o resultado é bloqueado com o motivo
  `protocolo_nao_aprovado`, exceto em rodadas de avaliação explicitamente
  marcadas, cujo resultado nunca é exibido;
- o registro de uso grava família, versão e impressão do prompt, impressão da
  política, ambiente e situação da estimativa e da conclusão, sem texto gerado,
  sem contexto e sem chave.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Callable, Iterable, Optional

from core import llm_client, llm_eval
from core import llm_exp_context as ec
from core import llm_exp_policy as policy
from core import llm_exp_prompts as ep
from core import llm_exp_validation as ev
from core import llm_service
from core.llm_service import (
    MODE_DEMO,
    MODE_LIVE,
    MODE_OFF,
    MODES,
    STATUS_BLOCKED,
    STATUS_DEMO,
    STATUS_OFF,
    STATUS_OK,
    STATUS_UNAVAILABLE,
    Explanation,
    UsageLimiter,
    context_key,
)

# Hashes ratificados pelo orientador em 09/11/2026 (aprovação DL1-H), referentes ao commit c106f6d.
# A aprovação vale só para estes valores exatos: qualquer mudança em prompt, esquema ou texto
# fixo muda um dos hashes e bloqueia a exibição (`protocolo_nao_aprovado`) até nova ratificação,
# sem reaproveitar o mesmo valor. A aprovação dos hashes é só uma das seis condições do portão
# de ativação; nenhuma tela usa esta camada.
APPROVED_HASHES = {
    "prompt": "b5ef179c9376",
    "esquema": "9a4cb5cb5a0c",
    "impressao": "6f50a1cadd7c",
    "textos_fixos": "95845577dba9",
}
APPROVED_FINGERPRINT: Optional[str] = APPROVED_HASHES["impressao"]
STATUS_EVALUATION = "avaliacao"

FALLBACK_TEXT = ep.FALLBACK_TEXT
# Correção 1 (DL1-B): só a falha da ressalva sobre média histórica dá direito a uma
# regeneração; se falhar de novo (ou se falhar qualquer outra verificação), abstenção.
REGENERABLE_CHECKS = ("ressalva_media_historica",)
MAX_REGENERATIONS = 1

REQUIRED_KEYS = ("protocol_family", "scope", "status", "asset", "filters", "n_observations", "historical",
                 "estimate", "decision", "release", "required_limits")


def build_payload(context: dict) -> dict:
    return {
        "model": llm_client.MODEL,
        "messages": ep.build_messages(context),
        "response_format": ep.response_format(),
        "max_completion_tokens": llm_client.MAX_OUTPUT_TOKENS,
        "reasoning_effort": llm_client.REASONING_EFFORT,
    }


def current_hashes() -> dict:
    return {"prompt": ep.prompt_hash(), "esquema": ep.schema_hash(), "impressao": ep.prompt_fingerprint(),
            "textos_fixos": ep.fixed_text_hashes()["conjunto"]}


def _problem(context: dict, mode: str, evaluation_run: bool, approved: Optional[str],
             approved_hashes: Optional[dict]) -> Optional[str]:
    if not isinstance(context, dict) or any(k not in context for k in REQUIRED_KEYS):
        return "contexto_invalido"
    if context["protocol_family"] != ec.PROTOCOL_FAMILY:
        return "familia_de_protocolo_divergente"
    if context["release"].get("ambiente") != policy.ENV_EXPERIMENTAL:
        return "fora_do_ambiente_experimental"
    if context.get("user_request") and not evaluation_run:
        return "entrada_livre_nao_permitida"
    if not evaluation_run:
        hashes = current_hashes()
        expected = approved_hashes if approved_hashes is not None else {**hashes, "impressao": approved}
        if approved is None or hashes["impressao"] != approved or hashes != expected:
            return "protocolo_nao_aprovado"
    return None


def _log(mode: str, context: dict, now: Callable) -> dict:
    ctx = context if isinstance(context, dict) else {}
    return {
        "timestamp": now().isoformat(timespec="seconds"),
        "protocol_family": ec.PROTOCOL_FAMILY,
        "mode": mode,
        "model": llm_client.MODEL if mode == MODE_LIVE else None,
        "prompt_version": ep.PROMPT_VERSION,
        "prompt_fingerprint": ep.prompt_fingerprint(),
        "prompt_hash": ep.prompt_hash(),
        "schema_hash": ep.schema_hash(),
        "fixed_texts_hash": ep.fixed_text_hashes()["conjunto"],
        "policy_fingerprint": policy.policy_fingerprint(),
        "environment": (ctx.get("release") or {}).get("ambiente"),
        "estimate_available": bool((ctx.get("estimate") or {}).get("disponivel")),
        "decision_available": bool((ctx.get("decision") or {}).get("disponivel")),
        "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "latency_s": 0.0, "attempts": 0,
        "failed_checks": [],
        "regenerations": 0,
        "calls": [],
    }


class ExperimentalExplanation(Explanation):
    """
    Resultado da camada experimental. Em todo bloqueio ou indisponibilidade não há dados para
    exibir (abstenção). O texto de abstenção é o fallback experimental só se o conjunto dos
    cinco textos fixos tiver o hash aprovado; senão é o fallback da v0.6, aprovado na 7B e
    independente desta camada. Nunca se mostra versão anterior de resposta ou de texto.
    """

    @property
    def fallback_text(self) -> Optional[str]:
        return None if self.shown else safe_fallback_text()


def safe_fallback_text() -> str:
    if ep.fixed_text_hashes()["conjunto"] == APPROVED_HASHES["textos_fixos"]:
        return ep.FALLBACK_TEXT
    return llm_service.FALLBACK_TEXT


def _result(status: str, data, reason: str, log: dict, sink) -> Explanation:
    log["status"], log["reason"] = status, reason
    if sink is not None:
        sink(log)
    return ExperimentalExplanation(status, data, reason, log)


def explain_experimental(
    context: dict,
    *,
    mode: str = MODE_OFF,
    api_key: Optional[str] = None,
    transport: Callable = llm_client.http_transport,
    known_tickers: Iterable[str] = (),
    demo_store: Optional[dict] = None,
    limiter: Optional[UsageLimiter] = None,
    log_sink: Optional[Callable] = None,
    evaluation_run: bool = False,
    approved_fingerprint: Optional[str] = APPROVED_FINGERPRINT,
    approved_hashes: Optional[dict] = None,
    sleep: Callable = time.sleep,
    clock: Callable = time.monotonic,
    now: Callable = lambda: datetime.now(timezone.utc),
) -> Explanation:
    """Explicação validada para um contexto v1.0-experimental, ou o fallback."""
    if mode not in MODES:
        raise ValueError(f"Modo inválido: {mode}.")
    log = _log(mode, context, now)
    if mode == MODE_OFF:
        return _result(STATUS_OFF, None, "desativado", log, log_sink)
    if approved_hashes is None and approved_fingerprint == APPROVED_FINGERPRINT:
        approved_hashes = APPROVED_HASHES
    problem = _problem(context, mode, evaluation_run, approved_fingerprint, approved_hashes)
    if problem:
        return _result(STATUS_BLOCKED, None, problem, log, log_sink)
    log["context_key"] = context_key(context)

    if mode == MODE_DEMO:
        raw = (demo_store or {}).get(log["context_key"])
        if raw is None:
            return _result(STATUS_UNAVAILABLE, None, "demo_sem_resposta_salva", log, log_sink)
        return _finish(raw, context, known_tickers, log, log_sink, STATUS_EVALUATION if evaluation_run else STATUS_DEMO)

    if not api_key:
        return _result(STATUS_UNAVAILABLE, None, "sem_chave", log, log_sink)
    limiter = limiter if limiter is not None else UsageLimiter()
    limited = limiter.check()
    if limited:
        return _result(STATUS_UNAVAILABLE, None, limited, log, log_sink)
    status = STATUS_EVALUATION if evaluation_run else STATUS_OK
    while True:
        try:
            call = llm_client.call_model(context, api_key, transport, sleep, clock, payload=build_payload(context))
        except llm_client.CallFailed as exc:
            limiter.record(0.0)
            log["attempts"] += exc.attempts
            log["latency_s"] = round(log["latency_s"] + exc.latency_s, 3)
            log["calls"].append({"tipo": _call_type(log), "status": "falha_do_provedor", "attempts": exc.attempts,
                                 "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0,
                                 "latency_s": exc.latency_s})
            return _result(STATUS_UNAVAILABLE, None, f"api_indisponivel:{exc}", log, log_sink)
        cost = llm_eval.estimate_cost(llm_client.MODEL, call["input_tokens"], call["output_tokens"])
        limiter.record(cost)
        record = {"tipo": _call_type(log), "status": "resposta", "attempts": call["attempts"],
                  "input_tokens": call["input_tokens"], "output_tokens": call["output_tokens"],
                  "cost_usd": round(cost, 6), "latency_s": call["latency_s"], "failed_checks": []}
        log["calls"].append(record)
        log.update(input_tokens=log["input_tokens"] + call["input_tokens"],
                   output_tokens=log["output_tokens"] + call["output_tokens"],
                   cost_usd=round(log["cost_usd"] + cost, 6),
                   latency_s=round(log["latency_s"] + call["latency_s"], 3),
                   attempts=log["attempts"] + call["attempts"])
        if call["finish_reason"] != "stop":
            return _result(STATUS_BLOCKED, None, "resposta_incompleta", log, log_sink)
        failed = ev.validate_experimental(call["raw"], context, known_tickers).failed
        record["failed_checks"] = failed
        regenerable = failed and all(name in REGENERABLE_CHECKS for name in failed)
        if not regenerable or log["regenerations"] >= MAX_REGENERATIONS or limiter.check():
            return _finish(call["raw"], context, known_tickers, log, log_sink, status)
        log["regenerations"] += 1


def _call_type(log: dict) -> str:
    """Primeira chamada ou regeneração (correção 1), para o custo por caso ser rastreável."""
    return "primeira" if not log["calls"] else "regeneracao"


def _finish(raw, context: dict, known_tickers, log: dict, sink, ok_status: str) -> Explanation:
    """Validação obrigatória; numa rodada de avaliação, a resposta aprovada nunca vai para exibição."""
    log["response_sha256"] = hashlib.sha256(str(raw).encode("utf-8")).hexdigest()[:16]
    result = ev.validate_experimental(raw, context, known_tickers)
    log["validation"] = {c.name: c.ok for c in result.checks}
    if not result.ok:
        log["failed_checks"] = result.failed
        return _result(STATUS_BLOCKED, None, "validacao_reprovada", log, sink)
    data = json.loads(raw) if not isinstance(raw, dict) else raw
    if ok_status == STATUS_EVALUATION:
        return _result(STATUS_EVALUATION, None, "rodada_de_avaliacao", log, sink)
    return _result(ok_status, data, "", log, sink)
