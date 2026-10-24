"""Recarga dos módulos do projeto após um deploy (app/reload_guard.py)."""

import importlib
import os
import sys
import time

import pytest

from app import reload_guard


@pytest.fixture
def fake_project(tmp_path, monkeypatch):
    """Pacote temporário 'pkgdeploy' com um módulo, importável pelo sys.path."""
    package = tmp_path / "pkgdeploy"
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "loader.py").write_text("def download(symbol):\n    return 'v1'\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.delitem(sys.modules, reload_guard._STATE_MODULE, raising=False)
    yield tmp_path, package
    for name in [n for n in sys.modules if n == "pkgdeploy" or n.startswith("pkgdeploy.")]:
        sys.modules.pop(name, None)
    sys.modules.pop(reload_guard._STATE_MODULE, None)


def _touch_later(path, text):
    path.write_text(text, encoding="utf-8")
    future = time.time() + 5
    os.utime(path, (future, future))


def test_fingerprint_changes_when_a_file_changes(fake_project):
    root, package = fake_project
    before = reload_guard.code_fingerprint(root, ("pkgdeploy",))
    _touch_later(package / "loader.py", "def download(symbol, *, fetch=None):\n    return 'v2'\n")
    assert reload_guard.code_fingerprint(root, ("pkgdeploy",)) != before


def test_purge_removes_only_project_modules(fake_project):
    importlib.import_module("pkgdeploy.loader")
    removed = reload_guard.purge_project_modules(("pkgdeploy",))
    assert set(removed) == {"pkgdeploy", "pkgdeploy.loader"}
    assert "pkgdeploy.loader" not in sys.modules
    assert "pytest" in sys.modules


def test_stale_module_is_reloaded_after_deploy(fake_project):
    """Cenário do erro no Streamlit Cloud: o arquivo muda, a memória não."""
    root, package = fake_project
    packages = ("pkgdeploy",)

    assert reload_guard.reload_if_changed(root, packages) is True   # primeira execução
    assert importlib.import_module("pkgdeploy.loader").download("X") == "v1"
    assert reload_guard.reload_if_changed(root, packages) is False  # nada mudou

    # Deploy: a nova versão aceita o parâmetro fetch
    _touch_later(package / "loader.py", "def download(symbol, *, fetch=None):\n    return 'v2'\n")
    stale = sys.modules["pkgdeploy.loader"]
    with pytest.raises(TypeError):
        stale.download("X", fetch=None)  # o que acontecia sem a recarga

    assert reload_guard.reload_if_changed(root, packages) is True
    fresh = importlib.import_module("pkgdeploy.loader")
    assert fresh.download("X", fetch=None) == "v2"


def test_project_fingerprint_covers_core_and_app():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    files = {entry[0] for entry in reload_guard.code_fingerprint(root)}
    assert "core/data_loader.py" in files and "app/ui/data_cache.py" in files
