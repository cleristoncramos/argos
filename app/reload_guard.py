"""
Recarga dos módulos do projeto depois de um deploy.

O Streamlit só recarrega, entre execuções, os módulos que estão na pasta do
script principal (`app/`). Os módulos de `core/` ficam fora dela: depois de
um push, o servidor do Streamlit Community Cloud continuava executando a
versão antiga de `core/` que já estava na memória, misturada com páginas
novas (o que causou um TypeError em `download_active_data`).

`reload_if_changed` compara uma impressão digital dos arquivos `.py` de
`core/` e `app/` com a da execução anterior e, se mudou, remove esses módulos
de `sys.modules` para que sejam importados de novo, já atualizados.
Não depende do Streamlit.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Iterable

PACKAGES = ("core", "app")
_STATE_MODULE = "_argos_reload_state"


def code_fingerprint(root: Path, packages: Iterable[str] = PACKAGES) -> tuple:
    """Caminho, data de modificação e tamanho de cada arquivo .py dos pacotes."""
    entries = []
    for package in packages:
        for path in sorted((root / package).rglob("*.py")):
            stat = path.stat()
            entries.append((path.relative_to(root).as_posix(), stat.st_mtime_ns, stat.st_size))
    return tuple(entries)


def purge_project_modules(packages: Iterable[str] = PACKAGES) -> list[str]:
    """Remove de sys.modules os módulos dos pacotes do projeto; devolve os nomes."""
    prefixes = tuple(f"{package}." for package in packages)
    names = [
        name for name in list(sys.modules)
        if name in packages or name.startswith(prefixes)
    ]
    for name in names:
        sys.modules.pop(name, None)
    return names


def _state() -> types.ModuleType:
    # Guardado em um módulo próprio, que sobrevive entre as execuções do script
    # e não é removido pelo purge.
    if _STATE_MODULE not in sys.modules:
        sys.modules[_STATE_MODULE] = types.ModuleType(_STATE_MODULE)
    return sys.modules[_STATE_MODULE]


def reload_if_changed(root: Path, packages: Iterable[str] = PACKAGES) -> bool:
    """
    Descarta os módulos do projeto se os arquivos mudaram desde a última
    execução (ou se é a primeira). Devolve True quando houve descarte.
    """
    state = _state()
    fingerprint = code_fingerprint(root, packages)
    if getattr(state, "fingerprint", None) == fingerprint:
        return False
    purge_project_modules(packages)
    state.fingerprint = fingerprint
    return True
