"""Funções auxiliares sem dependência de outros módulos do piloto."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from experiments.preditivo.config import PROJETO


def sha256(caminho: Path) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def git(*argumentos: str) -> str:
    try:
        return subprocess.run(["git", *argumentos], cwd=PROJETO, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def versoes() -> dict:
    """Versões do interpretador e das bibliotecas usadas na coleta e na modelagem."""
    import platform
    from importlib import metadata

    pacotes = {}
    for nome in ("pandas", "numpy", "yfinance", "scikit-learn"):
        try:
            pacotes[nome] = metadata.version(nome)
        except metadata.PackageNotFoundError:
            pacotes[nome] = None
    return {"python": platform.python_version(), **pacotes}
