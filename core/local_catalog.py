"""
Catálogo editável e preferências da página Configurações (etapa 4 da DL2).

- O catálogo base (core/assets.py, 148 ativos) não muda. Por cima dele, uma camada
  local em SQLite guarda grupos novos e ativos acrescentados pelo usuário.
- DL2-E: a edição só vale na instalação local. Ela fica ligada apenas quando a
  variável de ambiente ARGOS_CATALOGO_EDITAVEL vale on/1/true/sim e o modo de
  demonstração está desligado. Na versão pública a variável não existe, e o catálogo
  é fixo e somente leitura.
- O ticker é validado na fonte antes de ser salvo (mesma regra do "Digitar ticker").
- A mesma base guarda a referência padrão (B1) da instalação local.

Sem Streamlit: o acesso à fonte de dados é recebido como função.
"""

from __future__ import annotations

import os
import re
import sqlite3
import unicodedata
from contextlib import closing
from pathlib import Path
from typing import Callable, Iterable, Mapping, Optional

from core.assets import ASSET_GROUPS, CATEGORY_METADATA
from core.demo_mode import is_demo_mode
from core.ticker_input import validate_ticker

ENV_VAR = "ARGOS_CATALOGO_EDITAVEL"
_TRUE_VALUES = {"on", "1", "true", "sim", "yes"}
DB_FILE = Path(__file__).resolve().parent.parent / "data" / "catalogo_local.sqlite"
DB_ENV_VAR = "ARGOS_CATALOGO_ARQUIVO"   # outro arquivo SQLite (opcional; usado nos testes)
LOCAL_GROUP_PREFIX = "local_"
LOCAL_GROUP_ICON = "⭐"
LOCAL_SUBCATEGORY = "Adicionado por você"
LOCAL_MARKET = "Catálogo local"
REFERENCE_SETTING = "referencia_padrao"

SCHEMA = """
CREATE TABLE IF NOT EXISTS grupos (
    chave TEXT PRIMARY KEY,
    rotulo TEXT NOT NULL UNIQUE,
    classe TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ativos (
    ticker TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    grupo TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS preferencias (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL
);
"""


class CatalogError(ValueError):
    """Operação recusada, com mensagem pronta para o usuário."""


def editable_enabled() -> bool:
    """True só numa instalação local com a edição ligada e fora do modo de demonstração."""
    return os.environ.get(ENV_VAR, "").strip().lower() in _TRUE_VALUES and not is_demo_mode()


def db_path() -> Path:
    """Arquivo SQLite da camada local: ARGOS_CATALOGO_ARQUIVO, se definido; senão, data/."""
    custom = os.environ.get(DB_ENV_VAR, "").strip()
    return Path(custom) if custom else DB_FILE


def _slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


class LocalCatalog:
    """Camada editável do catálogo, guardada em SQLite."""

    def __init__(self, path: Path | str = DB_FILE, base_assets: Iterable[Mapping] = ()) -> None:
        self.path = Path(path)
        self.base_tickers = {str(a["ticker"]).upper() for a in base_assets}
        self.base_groups = {g["key"]: g for g in ASSET_GROUPS}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db:
            db.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _query(self, sql: str, params: tuple = ()) -> list[tuple]:
        with closing(self._connect()) as db:
            return db.execute(sql, params).fetchall()

    def _execute(self, sql: str, params: tuple = ()) -> None:
        with closing(self._connect()) as db, db:
            db.execute(sql, params)

    # ------------------------------------------------------------ grupos
    def groups(self) -> list[dict]:
        rows = self._query("SELECT chave, rotulo, classe FROM grupos ORDER BY rotulo")
        return [{"key": k, "label": f"{LOCAL_GROUP_ICON} {r}", "name": r, "class": c} for k, r, c in rows]

    def add_group(self, label: str, asset_class: str) -> str:
        label = (label or "").strip()
        if not label:
            raise CatalogError("Informe o nome do grupo.")
        if asset_class not in CATEGORY_METADATA:
            raise CatalogError("Escolha a classe dos ativos do grupo.")
        slug = _slug(label)
        if not slug:
            raise CatalogError("Use letras ou números no nome do grupo.")
        taken = {g["name"].lower() for g in self.groups()} | {
            g["label"].split(" ", 1)[-1].lower() for g in ASSET_GROUPS
        }
        if label.lower() in taken:
            raise CatalogError(f"Já existe um grupo chamado \"{label}\".")
        key = LOCAL_GROUP_PREFIX + slug
        self._execute("INSERT INTO grupos (chave, rotulo, classe) VALUES (?, ?, ?)", (key, label, asset_class))
        return key

    def remove_group(self, key: str) -> None:
        if self._query("SELECT 1 FROM ativos WHERE grupo = ?", (key,)):
            raise CatalogError("Remova os ativos do grupo antes de removê-lo.")
        self._execute("DELETE FROM grupos WHERE chave = ?", (key,))

    def group_class(self, key: str) -> Optional[str]:
        if key in self.base_groups:
            return self.base_groups[key]["class"]
        return next((g["class"] for g in self.groups() if g["key"] == key), None)

    # ------------------------------------------------------------ ativos
    def assets(self) -> list[dict]:
        rows = self._query("SELECT ticker, nome, grupo FROM ativos ORDER BY grupo, nome")
        return [{"ticker": t, "name": n, "group": g} for t, n, g in rows]

    def add_asset(self, raw_ticker: str, name: str, group: str, fetch: Callable[[str], object]) -> str:
        """Acrescenta um ativo a um grupo, depois de conferir o ticker na fonte."""
        if self.group_class(group) is None:
            raise CatalogError("Escolha um grupo existente.")
        result = validate_ticker(raw_ticker, fetch)
        if not result.ok:
            raise CatalogError(result.message)
        ticker = result.ticker
        if ticker in self.base_tickers:
            raise CatalogError(f"{ticker} já faz parte do catálogo base do Argos.")
        if self._query("SELECT 1 FROM ativos WHERE ticker = ?", (ticker,)):
            raise CatalogError(f"{ticker} já está no seu catálogo.")
        self._execute(
            "INSERT INTO ativos (ticker, nome, grupo) VALUES (?, ?, ?)",
            (ticker, (name or "").strip() or ticker, group),
        )
        return ticker

    def remove_asset(self, ticker: str) -> None:
        self._execute("DELETE FROM ativos WHERE ticker = ?", (ticker,))

    def records(self) -> list[dict]:
        """Ativos locais no formato do catálogo base (core/assets.py)."""
        out = []
        for item in self.assets():
            asset_class = self.group_class(item["group"])
            if asset_class is None:
                continue
            meta = CATEGORY_METADATA[asset_class]
            out.append({
                "ticker": item["ticker"],
                "name": item["name"],
                "class": asset_class,
                "subcategory": LOCAL_SUBCATEGORY,
                "market": LOCAL_MARKET,
                "description": "Ativo incluído no catálogo local desta instalação.",
                "group": item["group"],
                "icon": meta["icon"],
                "category_color": meta["category_color"],
                "data_type": meta["data_type"],
                "local": "sim",
            })
        return out

    # ------------------------------------------------------------ preferências
    def get_setting(self, key: str) -> Optional[str]:
        rows = self._query("SELECT valor FROM preferencias WHERE chave = ?", (key,))
        return rows[0][0] if rows else None

    def set_setting(self, key: str, value: Optional[str]) -> None:
        if value is None:
            self._execute("DELETE FROM preferencias WHERE chave = ?", (key,))
        else:
            self._execute(
                "INSERT INTO preferencias (chave, valor) VALUES (?, ?) "
                "ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor",
                (key, value),
            )


def merged_catalog(base: Iterable[Mapping], local: Iterable[Mapping]) -> list:
    """Catálogo base seguido dos ativos locais."""
    return [*base, *local]


def local_group_labels(groups: Iterable[Mapping]) -> dict[str, str]:
    return {g["key"]: g["label"] for g in groups}
