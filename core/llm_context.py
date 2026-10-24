"""
Pacote de contexto para a explicação assistida (etapas 7A e 7B).

A LLM nunca recebe imagens nem calcula nada: recebe este pacote, montado
pelo Argos a partir de resultados já calculados. Módulo puro (sem rede).
"""

from __future__ import annotations

import math
from datetime import date
from typing import Iterable, Optional

CONTEXT_VERSION = 1

ANALYSIS_TYPES = (
    "analise_individual",
    "risco_retorno",
    "sazonalidade",
    "comparacao",
    "simulacao",
)
STATUSES = ("ok", "dados_insuficientes")
FREQUENCIES = ("Diário", "Semanal", "Mensal", "Semestral", "Anual")
REQUEST_TYPES = ("recomendacao", "previsao")

# Observações mínimas por frequência abaixo das quais a amostra é "pequena".
MIN_OBSERVATIONS = {"Diário": 60, "Semanal": 26, "Mensal": 24, "Semestral": 10, "Anual": 5}
MIN_YEARS = 5

LIMITATION_FLAGS = (
    "poucas_observacoes",
    "poucos_anos",
    "mes_em_andamento",
    "preco_nao_positivo",
)

# Palavras (sem acento, minúsculas): ao menos uma deve aparecer nas limitações
# quando o sinalizador correspondente estiver ativo.
LIMITATION_KEYWORDS = {
    "poucas_observacoes": ("poucas observacoes", "amostra pequena", "poucos dados", "observacoes"),
    "poucos_anos": ("poucos anos", "anos disponiveis", "amostra", "poucos"),
    "mes_em_andamento": (
        "em andamento", "incompleto", "parcial", "ainda nao terminou",
        "mes atual", "mes corrente", "mes vigente", "nao terminou", "excluid",
    ),
    "preco_nao_positivo": ("preco", "zero", "negativ", "nao positivo"),
}

# 100 (percentual), 0 e 1 (escala da correlação e contagens triviais).
ALWAYS_ALLOWED_NUMBERS = (100.0, 0.0, 1.0)


def metric(
    metric_id: str,
    label: str,
    value: float,
    unit: str,
    decimals: int = 2,
) -> dict:
    """Uma métrica já calculada, com valor arredondado e unidade explícita."""
    metric_id = str(metric_id).strip()
    if not metric_id:
        raise ValueError("A métrica precisa de um id.")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Valor inválido para a métrica '{metric_id}'.") from exc
    if not math.isfinite(number):
        raise ValueError(f"Valor não finito para a métrica '{metric_id}'.")
    if not isinstance(decimals, int) or decimals < 0:
        raise ValueError("decimals deve ser inteiro não negativo.")
    return {
        "id": metric_id,
        "label": str(label).strip(),
        "value": round(number, decimals),
        "unit": str(unit),
        "decimals": decimals,
    }


def derive_limitation_flags(
    *,
    n_observations: int,
    frequency: str,
    n_years: Optional[int] = None,
    incomplete_month: bool = False,
    nonpositive_price: bool = False,
) -> list:
    """Sinalizadores de limitação que a explicação é obrigada a mencionar."""
    flags = []
    if n_observations < MIN_OBSERVATIONS.get(frequency, 0):
        flags.append("poucas_observacoes")
    if n_years is not None and n_years < MIN_YEARS:
        flags.append("poucos_anos")
    if incomplete_month:
        flags.append("mes_em_andamento")
    if nonpositive_price:
        flags.append("preco_nao_positivo")
    return flags


def _iso(value, name: str) -> str:
    try:
        return date.fromisoformat(str(value)).isoformat()
    except ValueError as exc:
        raise ValueError(f"{name} deve estar no formato AAAA-MM-DD.") from exc


def build_context(
    *,
    analysis_type: str,
    assets: Iterable[str],
    period_start: str,
    period_end: str,
    frequency: str,
    n_observations: int,
    metrics: Iterable[dict] = (),
    status: str = "ok",
    limitation_flags: Iterable[str] = (),
    notes: Iterable[str] = (),
    asset_names: Optional[dict] = None,
    user_request: Optional[tuple] = None,
    extra_numbers: Iterable[float] = (),
) -> dict:
    """Valida e monta o pacote de contexto enviado ao modelo."""
    if analysis_type not in ANALYSIS_TYPES:
        raise ValueError(f"Tipo de análise inválido: {analysis_type}.")
    if status not in STATUSES:
        raise ValueError(f"Status inválido: {status}.")
    if frequency not in FREQUENCIES:
        raise ValueError(f"Frequência inválida: {frequency}.")

    asset_list = [str(a).strip() for a in assets]
    if not asset_list or any(not a for a in asset_list):
        raise ValueError("Informe ao menos um ativo.")
    if len({a.upper() for a in asset_list}) != len(asset_list):
        raise ValueError("Ativos repetidos.")

    start, end = _iso(period_start, "period_start"), _iso(period_end, "period_end")
    if start > end:
        raise ValueError("O início do período é posterior ao fim.")

    if not isinstance(n_observations, int) or n_observations < 0:
        raise ValueError("n_observations deve ser inteiro não negativo.")

    metric_list = [dict(m) for m in metrics]
    ids = [m["id"] for m in metric_list]
    if len(set(ids)) != len(ids):
        raise ValueError("Ids de métricas repetidos.")
    if status == "dados_insuficientes" and metric_list:
        raise ValueError("Com dados insuficientes não há métricas.")

    flags = list(dict.fromkeys(limitation_flags))
    unknown = [f for f in flags if f not in LIMITATION_FLAGS]
    if unknown:
        raise ValueError(f"Sinalizador de limitação desconhecido: {unknown[0]}.")

    request = None
    if user_request is not None:
        request_type, text = user_request
        if request_type not in REQUEST_TYPES:
            raise ValueError(f"Tipo de pedido inválido: {request_type}.")
        request = {"type": request_type, "text": str(text).strip()}

    return {
        "context_version": CONTEXT_VERSION,
        "analysis_type": analysis_type,
        "status": status,
        "assets": asset_list,
        "asset_names": dict(asset_names or {}),
        "filters": {
            "period_start": start,
            "period_end": end,
            "frequency": frequency,
        },
        "n_observations": n_observations,
        "metrics": metric_list,
        "limitation_flags": flags,
        "notes": [str(n) for n in notes],
        "user_request": request,
        "extra_numbers": [float(x) for x in extra_numbers],
    }


def allowed_numbers(context: dict) -> list:
    """Todos os números que a explicação pode citar (os demais são rejeitados)."""
    numbers = [float(m["value"]) for m in context["metrics"]]
    numbers.append(float(context["n_observations"]))
    numbers.extend(float(x) for x in context.get("extra_numbers", []))
    numbers.extend(ALWAYS_ALLOWED_NUMBERS)
    start = int(context["filters"]["period_start"][:4])
    end = int(context["filters"]["period_end"][:4])
    numbers.extend(float(year) for year in range(start, end + 1))
    # Duração do período em anos (exata, arredondada e truncada): "cerca de 5 anos".
    span = (
        date.fromisoformat(context["filters"]["period_end"])
        - date.fromisoformat(context["filters"]["period_start"])
    ).days / 365.25
    numbers.extend([round(span, 1), float(round(span)), float(int(span))])
    return numbers
