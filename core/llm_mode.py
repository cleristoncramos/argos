"""
Resolução do modo da explicação por IA quando o modo de dados salvos
(``ARGOS_DEMO_MODE``) está ativo. Função pura, sem Streamlit e sem rede.

Regras:
- Fora do modo de dados salvos, vale o que foi configurado em
  ``ARGOS_LLM_MODE``; valor ausente ou desconhecido equivale a ``off``.
- Com o modo de dados salvos ativo, a explicação nunca chama a API: o padrão
  passa a ser ``demo`` (respostas salvas). Duas exceções:
    * ``off`` explícito continua desligando o recurso;
    * ``live`` só é aceito junto com a gravação de respostas
      (``ARGOS_LLM_RECORD``), para o pesquisador gravar as respostas sobre os
      dados congelados.
"""

from __future__ import annotations

from typing import Optional

MODE_OFF = "off"
MODE_DEMO = "demo"
MODE_LIVE = "live"
MODES = (MODE_OFF, MODE_DEMO, MODE_LIVE)


def resolve_mode(
    configured: Optional[str], demo_data_mode: bool, recording: bool
) -> str:
    """Devolve ``off``, ``demo`` ou ``live`` conforme a configuração e o modo de dados."""
    value = (configured or "").strip().lower()
    if demo_data_mode:
        if value == MODE_OFF:
            return MODE_OFF
        if value == MODE_LIVE and recording:
            return MODE_LIVE
        return MODE_DEMO
    return value if value in MODES else MODE_OFF