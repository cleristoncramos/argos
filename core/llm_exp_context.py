"""
Pacote de contexto da camada de linguagem v1.0-experimental.

O contexto separa três camadas: observação histórica, estimativa e conclusão
experimental. Todos os números vêm do Argos; o modelo de linguagem não calcula
nada. A estimativa e a conclusão só entram com seus números quando a política
de liberação (`core.llm_exp_policy`) as autoriza; caso contrário, o contexto
leva apenas o motivo da abstenção, sem nenhum número delas. Módulo puro.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable, Optional

from core import llm_context as lc
from core import llm_exp_policy as policy

PROTOCOL_FAMILY = "v1.0-experimental"
CONTEXT_VERSION = "1.0-experimental"

SCOPE_CHART = "grafico"
SCOPE_SYNTHESIS = "sintese_ativo"
SCOPES = (SCOPE_CHART, SCOPE_SYNTHESIS)

# Regra de redação por gráfico (A.3): cada explicação local leva o limite do que a
# evidência permite concluir, copiado literalmente em "o_que_nao_pode_ser_concluido".
CHART_LIMITS = {
    "preco_medias": "A direção passada e o afastamento das médias não indicam que a trajetória continuará.",
    "rsi_macd": "Um sinal de indicador não garante reversão do preço.",
    "sazonalidade": "A média histórica de um mês não indica que o próximo mês repetirá esse resultado.",
    "volatilidade": "Volatilidade alta não implica retorno alto.",
    "drawdown": "A profundidade de uma queda passada não indica que o preço encontrou o fundo.",
    "aportes": "O resultado histórico de uma forma de aporte não mostra que ela é sempre superior.",
    "referencia_mercado": "Ter superado a referência no período não indica que isso continuará.",
    "previsao": "Uma estimativa para um horizonte definido não indica um ponto ótimo conhecido de entrada.",
}
CHART_TYPES = tuple(CHART_LIMITS)
SYNTHESIS_LIMIT = (
    "Nenhuma evidência desta síntese, isolada ou combinada, permite concluir o que acontecerá com o ativo."
)

REQUEST_RECOMMENDATION = "recomendacao"
REQUEST_FORECAST = "previsao"
REQUEST_GUARANTEE = "garantia"
REQUEST_TYPES = (REQUEST_RECOMMENDATION, REQUEST_FORECAST, REQUEST_GUARANTEE)

# Conclusões que o motor de decisão pode emitir. O texto é do Argos, não do modelo de
# linguagem: o modelo só pode copiá-lo.
CONCLUSION_TEXTS = {
    "sinal_favoravel": (
        "Para o horizonte selecionado, o modelo produziu sinal favorável segundo a regra experimental {regra}. "
        "A estimativa apresenta incerteza e o desempenho observado no teste está resumido abaixo."
    ),
    "sinal_desfavoravel": (
        "Para o horizonte selecionado, o modelo não produziu sinal favorável segundo a regra experimental {regra}. "
        "A estimativa apresenta incerteza e o desempenho observado no teste está resumido abaixo."
    ),
}


def _iso(value, name: str) -> str:
    try:
        return date.fromisoformat(str(value)).isoformat()
    except ValueError as exc:
        raise ValueError(f"{name} deve estar no formato AAAA-MM-DD.") from exc


def _metric_list(metrics: Iterable[dict], name: str) -> list:
    items = [dict(m) for m in metrics]
    ids = [m["id"] for m in items]
    if len(set(ids)) != len(ids):
        raise ValueError(f"Ids de métricas repetidos em {name}.")
    return items


def _estimate_block(estimate: Optional[dict], asset: str, environment: str, registry) -> dict:
    """Bloco de estimativa: com números só se a política autorizar."""
    model_id = (estimate or {}).get("model_id")
    authorized, reason = policy.estimate_authorization(model_id, asset, environment, registry)
    if estimate is None or not authorized:
        return {"disponivel": False, "motivo": reason}
    point = estimate.get("ponto")
    uncertainty = _metric_list(estimate.get("incerteza", ()), "incerteza")
    performance = _metric_list(estimate.get("desempenho_teste", ()), "desempenho_teste")
    horizon = estimate.get("horizonte") or {}
    if not point or not uncertainty or not performance:
        raise ValueError("Estimativa autorizada exige ponto, medida de incerteza e desempenho no teste.")
    if not isinstance(horizon.get("valor"), int) or horizon["valor"] <= 0 or not horizon.get("unidade"):
        raise ValueError("Estimativa autorizada exige horizonte inteiro positivo com unidade.")
    metrics = _metric_list([point, *uncertainty, *performance], "estimativa")
    return {
        "disponivel": True,
        "motivo": "",
        "model_id": model_id,
        "horizonte": {"valor": horizon["valor"], "unidade": str(horizon["unidade"])},
        "data_corte": _iso(estimate.get("data_corte"), "data_corte"),
        "ponto_id": point["id"],
        "incerteza_ids": [m["id"] for m in uncertainty],
        "metrics": metrics,
    }


def _decision_block(decision: Optional[dict], estimate_block: dict, environment: str, registry) -> dict:
    engine_id = (decision or {}).get("engine_id")
    authorized, reason = policy.decision_authorization(engine_id, environment, registry)
    if decision is None or not authorized:
        return {"disponivel": False, "motivo": reason}
    if not estimate_block["disponivel"]:
        # Conclusão sem estimativa autorizada não é comunicada.
        return {"disponivel": False, "motivo": "conclusao_sem_estimativa_autorizada"}
    code = decision.get("codigo")
    rule = str(decision.get("regra_id", "")).strip()
    if code not in CONCLUSION_TEXTS or not rule:
        raise ValueError("Conclusão autorizada exige código conhecido e identificador da regra.")
    return {
        "disponivel": True,
        "motivo": "",
        "engine_id": engine_id,
        "regra_id": rule,
        "codigo": code,
        "texto_conclusao": CONCLUSION_TEXTS[code].format(regra=rule),
    }


def build_experimental_context(
    *,
    scope: str,
    asset: str,
    period_start: str,
    period_end: str,
    frequency: str,
    n_observations: int,
    environment: str,
    chart_type: Optional[str] = None,
    charts: Iterable[str] = (),
    metrics: Iterable[dict] = (),
    status: str = "ok",
    limitation_flags: Iterable[str] = (),
    notes: Iterable[str] = (),
    asset_name: Optional[str] = None,
    estimate: Optional[dict] = None,
    decision: Optional[dict] = None,
    user_request: Optional[tuple] = None,
    extra_numbers: Iterable[float] = (),
    model_registry: Optional[dict] = None,
    engine_registry: Optional[dict] = None,
) -> dict:
    """Valida e monta o contexto v1.0-experimental para um gráfico ou para a síntese de um ativo."""
    if scope not in SCOPES:
        raise ValueError(f"Escopo inválido: {scope}.")
    if scope == SCOPE_CHART:
        if chart_type not in CHART_TYPES:
            raise ValueError(f"Tipo de gráfico inválido: {chart_type}.")
        chart_list, limits = [chart_type], [CHART_LIMITS[chart_type]]
    else:
        chart_list = list(dict.fromkeys(charts))
        if not chart_list or any(c not in CHART_TYPES for c in chart_list):
            raise ValueError("A síntese exige a lista dos gráficos considerados, todos de tipos conhecidos.")
        limits = [SYNTHESIS_LIMIT]
    if status not in lc.STATUSES:
        raise ValueError(f"Status inválido: {status}.")
    if frequency not in lc.FREQUENCIES:
        raise ValueError(f"Frequência inválida: {frequency}.")
    asset = str(asset).strip()
    if not asset:
        raise ValueError("Informe o ativo.")
    start, end = _iso(period_start, "period_start"), _iso(period_end, "period_end")
    if start > end:
        raise ValueError("O início do período é posterior ao fim.")
    if not isinstance(n_observations, int) or n_observations < 0:
        raise ValueError("n_observations deve ser inteiro não negativo.")
    historical = _metric_list(metrics, "observação histórica")
    if status == "dados_insuficientes" and historical:
        raise ValueError("Com dados insuficientes não há métricas.")
    flags = list(dict.fromkeys(limitation_flags))
    unknown = [f for f in flags if f not in lc.LIMITATION_FLAGS]
    if unknown:
        raise ValueError(f"Sinalizador de limitação desconhecido: {unknown[0]}.")
    request = None
    if user_request is not None:
        request_type, text = user_request
        if request_type not in REQUEST_TYPES:
            raise ValueError(f"Tipo de pedido inválido: {request_type}.")
        request = {"type": request_type, "text": str(text).strip()}

    estimate_block = _estimate_block(estimate, asset, environment, model_registry)
    decision_block = _decision_block(decision, estimate_block, environment, engine_registry)
    return {
        "protocol_family": PROTOCOL_FAMILY,
        "context_version": CONTEXT_VERSION,
        "scope": scope,
        "charts": chart_list,
        "status": status,
        "asset": asset,
        "asset_name": asset_name or "",
        "filters": {"period_start": start, "period_end": end, "frequency": frequency},
        "n_observations": n_observations,
        "historical": {"metrics": historical, "limitation_flags": flags, "notes": [str(n) for n in notes]},
        "estimate": estimate_block,
        "decision": decision_block,
        "release": {
            "ambiente": environment,
            "recomendacao_habilitada": policy.RECOMMENDATION_ENABLED,
            "politica_versao": policy.POLICY_VERSION,
            "politica_impressao": policy.policy_fingerprint(model_registry, engine_registry),
        },
        "required_limits": limits,
        "user_request": request,
        "extra_numbers": [float(x) for x in extra_numbers],
    }


def historical_allowed_numbers(context: dict) -> list:
    """Números que a camada histórica pode citar (as mesmas regras da v0.6)."""
    pseudo = {
        "metrics": context["historical"]["metrics"],
        "n_observations": context["n_observations"],
        "extra_numbers": context.get("extra_numbers", []),
        "filters": context["filters"],
    }
    return lc.allowed_numbers(pseudo)


def estimate_allowed_numbers(context: dict) -> list:
    """Números da estimativa autorizada: métricas, horizonte e ano de corte."""
    block = context["estimate"]
    if not block.get("disponivel"):
        return []
    numbers = [float(m["value"]) for m in block["metrics"]]
    numbers.append(float(block["horizonte"]["valor"]))
    numbers.append(float(block["data_corte"][:4]))
    numbers.extend(lc.ALWAYS_ALLOWED_NUMBERS)
    return numbers
