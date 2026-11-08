"""
Registro de execuções (protocolo, seção 10): uma linha JSON por execução, com
commit, hashes do protocolo, da nota, da configuração e do manifesto do snapshot
vigente. Configurações rejeitadas também ficam registradas.
"""

from __future__ import annotations

import json
from pathlib import Path

from core.clock import now_brasilia
from experiments.preditivo import config
from experiments.preditivo.dados import caminho_manifesto
from experiments.preditivo.util import git, sha256


def _hash_opcional(caminho: Path | None) -> str | None:
    return sha256(caminho) if caminho is not None and Path(caminho).exists() else None


def hashes_atuais() -> dict:
    return {
        "protocolo": _hash_opcional(config.PROTOCOLO),
        "nota": _hash_opcional(config.NOTA),
        "configuracao": _hash_opcional(config.RAIZ / "config.py"),
        "manifesto_dados": _hash_opcional(caminho_manifesto()),
        "politica_qualidade": _hash_opcional(config.POLITICA_QUALIDADE),
    }


def registrar(evento: str, dados: dict, avaliacao_final: bool = False, destino: Path | None = None) -> dict:
    linha = {
        "quando": now_brasilia().isoformat(timespec="seconds"),
        "evento": evento,
        "avaliacao_final": avaliacao_final,
        "commit": git("rev-parse", "HEAD"),
        "arvore_alterada": bool(git("status", "--porcelain")),
        "hashes": hashes_atuais(),
        "dados": dados,
    }
    alvo = destino or config.REGISTRO
    with open(alvo, "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(linha, ensure_ascii=False, default=str) + "\n")
    return linha
