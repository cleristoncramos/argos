"""
Política de liberação da camada de linguagem v1.0-experimental.

Decide, fora do modelo de linguagem, se uma estimativa ou uma conclusão sobre
estratégia pode ser comunicada. O modelo de linguagem nunca decide isso: ele só
recebe o resultado desta política no contexto. Módulo puro (sem rede).

Estado em 08/11/2026: nenhum modelo preditivo e nenhum motor de decisão estão
autorizados. Os pilotos v1 (decisão D1) e v2 (decisão DV2) foram encerrados sem
modelo elegível, e a recomendação ao público continua desligada até o parecer
regulatório (plano de reformulação, seção 4). Incluir um item nos registros
abaixo é mudança da política: exige decisão escrita do orientador, nova versão
e nova impressão digital.
"""

from __future__ import annotations

import hashlib
import json

POLICY_VERSION = "1.0"

ENV_PUBLIC = "publico"
ENV_EXPERIMENTAL = "experimental_restrito"
ENVIRONMENTS = (ENV_PUBLIC, ENV_EXPERIMENTAL)

# model_id -> {"protocolo", "decisao", "ativos", "horizonte"}; vazio enquanto nenhum modelo for autorizado.
AUTHORIZED_MODELS: dict = {}
# engine_id -> {"protocolo", "decisao", "regras"}; vazio enquanto nenhum motor for autorizado.
AUTHORIZED_DECISION_ENGINES: dict = {}

# Recomendação ao público: desligada até o parecer regulatório.
RECOMMENDATION_ENABLED = False

REASON_PUBLIC = "ambiente_publico"
REASON_NO_MODEL = "sem_modelo_autorizado"
REASON_NOT_IN_REGISTRY = "modelo_nao_autorizado"
REASON_ASSET = "ativo_fora_da_autorizacao"
REASON_NO_ENGINE = "sem_motor_autorizado"
REASON_ENGINE_NOT_IN_REGISTRY = "motor_nao_autorizado"


def _check_environment(environment: str) -> None:
    if environment not in ENVIRONMENTS:
        raise ValueError(f"Ambiente inválido: {environment}.")


def estimate_authorization(model_id, asset: str, environment: str,
                           registry: dict | None = None) -> tuple[bool, str]:
    """(autorizada, motivo). No ambiente público nenhuma estimativa é liberada."""
    _check_environment(environment)
    registry = AUTHORIZED_MODELS if registry is None else registry
    if environment == ENV_PUBLIC:
        return False, REASON_PUBLIC
    if not model_id:
        return False, REASON_NO_MODEL
    entry = registry.get(model_id)
    if entry is None:
        return False, REASON_NOT_IN_REGISTRY
    if asset.upper() not in {a.upper() for a in entry.get("ativos", ())}:
        return False, REASON_ASSET
    return True, ""


def decision_authorization(engine_id, environment: str,
                           registry: dict | None = None) -> tuple[bool, str]:
    """(autorizada, motivo) para a conclusão do motor de decisão."""
    _check_environment(environment)
    registry = AUTHORIZED_DECISION_ENGINES if registry is None else registry
    if environment == ENV_PUBLIC:
        return False, REASON_PUBLIC
    if not engine_id:
        return False, REASON_NO_ENGINE
    if engine_id not in registry:
        return False, REASON_ENGINE_NOT_IN_REGISTRY
    return True, ""


def policy_fingerprint(models: dict | None = None, engines: dict | None = None,
                       recommendation_enabled: bool | None = None) -> str:
    """Hash curto da política vigente, gravado em cada registro de uso."""
    material = json.dumps(
        {
            "versao": POLICY_VERSION,
            "modelos": AUTHORIZED_MODELS if models is None else models,
            "motores": AUTHORIZED_DECISION_ENGINES if engines is None else engines,
            "recomendacao": RECOMMENDATION_ENABLED if recommendation_enabled is None else recommendation_enabled,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]
