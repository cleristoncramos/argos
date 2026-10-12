"""
Apresentação da explicação validada (7B): converte o JSON aprovado em seções
de texto seguras para exibir. Módulo puro (sem Streamlit).
"""

from __future__ import annotations

import re
from typing import Optional

_MARKDOWN_SPECIAL = re.compile(r"([\\`*_\[\]$~<>])")


def escape_markdown(text: str) -> str:
    """Impede que o texto gerado vire formatação, link ou fórmula na página."""
    return _MARKDOWN_SPECIAL.sub(r"\\\1", str(text))


def format_value(value: float, unit: str = "") -> str:
    """Valor no padrão brasileiro (vírgula decimal, ponto de milhar), sem casas inventadas."""
    number = float(value)
    text = f"{number:,.4f}".rstrip("0").rstrip(".")
    text = text.replace(",", "X").replace(".", ",").replace("X", ".")
    unit = str(unit).strip()
    if unit == "%":
        return f"{text}%"
    return f"{text} {unit}".strip()


def explanation_view(data: dict, context: Optional[dict] = None) -> dict:
    """Seções prontas para exibir, com o texto já escapado."""
    labels = {m["id"]: m["label"] for m in (context or {}).get("metrics", [])}
    return {
        "resumo": escape_markdown(data["resumo"]),
        "grafico": escape_markdown(data["o_que_o_grafico_mostra"]),
        "metricas": [
            (
                escape_markdown(labels.get(m["id"], m["id"])),
                escape_markdown(format_value(m["valor"], m["unidade"])),
                escape_markdown(m["leitura"]),
            )
            for m in data["metricas_relevantes"]
        ],
        "limitacoes": [escape_markdown(x) for x in data["limitacoes"]],
        "nao_concluir": [escape_markdown(x) for x in data["o_que_nao_pode_ser_concluido"]],
        "nota": escape_markdown(data["nota_educativa"]),
    }
