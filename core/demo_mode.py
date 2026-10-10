"""
Modo de demonstração com dados salvos (requisito do congelamento da versão).

Com ``ARGOS_DEMO_MODE=true`` o Argos não consulta o Yahoo Finance nem
nenhuma outra fonte externa: os preços vêm de arquivos CSV salvos em
``data/demo/``, descritos por um manifesto (``manifest.json``) que guarda a
data da coleta, o período e o hash SHA-256 de cada arquivo. As explicações
assistidas usam respostas já validadas e salvas (``llm_respostas.json``) ou,
na falta delas, o texto fixo do roteiro de leitura.

Este módulo não depende do Streamlit.
"""

from __future__ import annotations

import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

import pandas as pd

ENV_VAR = "ARGOS_DEMO_MODE"
ENV_DIR_VAR = "ARGOS_DEMO_DIR"
MANIFEST_NAME = "manifest.json"
LLM_ANSWERS_NAME = "llm_respostas.json"
SCHEMA_VERSION = 1
SUPPORTED_INTERVALS = ("1d", "1wk", "1mo")
REQUIRED_COLUMNS = ("Open", "High", "Low", "Close", "Volume")

_TRUE_VALUES = {"1", "true", "yes", "sim", "on"}
_FORBIDDEN_FILENAME_CHARS = '^=/\\:*?"<>|'
_AGGREGATIONS = {
    "Open": "first",
    "High": "max",
    "Low": "min",
    "Close": "last",
    "Adj Close": "last",
    "Volume": "sum",
    "Dividends": "sum",
    "Stock Splits": "sum",
}


class DemoDataError(Exception):
    """Dados da demonstração ausentes, inválidos ou fora do pacote salvo."""


# ----------------------------------------------------------------------
# Configuração
# ----------------------------------------------------------------------
def is_demo_mode() -> bool:
    """True quando ``ARGOS_DEMO_MODE`` vale 1, true, yes, sim ou on."""
    return os.environ.get(ENV_VAR, "").strip().lower() in _TRUE_VALUES


def demo_dir() -> Path:
    """Pasta do pacote da demo (``ARGOS_DEMO_DIR`` ou ``data/demo``)."""
    custom = os.environ.get(ENV_DIR_VAR, "").strip()
    if custom:
        return Path(custom)
    return Path(__file__).resolve().parents[1] / "data" / "demo"


def file_name_for(ticker: str) -> str:
    """Nome de arquivo seguro para o ticker (``^GSPC`` -> ``_GSPC.csv``)."""
    name = str(ticker).strip().upper()
    for char in _FORBIDDEN_FILENAME_CHARS:
        name = name.replace(char, "_")
    return f"{name}.csv"


# ----------------------------------------------------------------------
# Manifesto e integridade
# ----------------------------------------------------------------------
def sha256_file(path) -> str:
    """
    SHA-256 do arquivo com finais de linha normalizados para LF, para que
    o hash não mude quando o Git converte LF/CRLF no Windows.
    """
    content = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def load_manifest(directory=None) -> dict:
    """Lê e valida o manifesto da demonstração."""
    base = Path(directory) if directory else demo_dir()
    path = base / MANIFEST_NAME
    if not path.is_file():
        raise DemoDataError(f"Manifesto da demonstração não encontrado em {path}.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DemoDataError(f"Manifesto ilegível em {path}.") from exc
    if (
        not isinstance(data, dict)
        or data.get("schema_version") != SCHEMA_VERSION
        or not isinstance(data.get("assets"), list)
    ):
        raise DemoDataError(f"Manifesto inválido em {path}.")
    return data


def demo_tickers(directory=None) -> list:
    """Tickers do manifesto; lista vazia se o pacote não existir."""
    try:
        manifest = load_manifest(directory)
    except DemoDataError:
        return []
    return [str(a.get("ticker", "")).upper() for a in manifest["assets"]]


def is_demo_asset(ticker: str, directory=None) -> bool:
    return str(ticker).strip().upper() in demo_tickers(directory)


def catalog_assets(assets, directory=None) -> list:
    """
    Catálogo exibido ao usuário: no modo demo, somente os ativos do pacote
    salvo. Sem modo demo (ou sem pacote legível) devolve o catálogo inteiro;
    nesse caso o aviso de erro do modo demo explica o problema.
    """
    if not is_demo_mode():
        return list(assets)
    tickers = set(demo_tickers(directory))
    if not tickers:
        return list(assets)
    return [a for a in assets if str(a.get("ticker", "")).upper() in tickers]


@lru_cache(maxsize=64)
def _hash_ok(path: str, mtime_ns: int, size: int, expected: str) -> bool:
    # mtime e tamanho entram na chave: o hash só é recalculado se o arquivo mudar.
    return sha256_file(path) == expected


def _file_matches(path: Path, expected: str) -> bool:
    stat = path.stat()
    return _hash_ok(str(path), stat.st_mtime_ns, stat.st_size, str(expected))


def verify_package(directory=None) -> list:
    """Lista de problemas do pacote da demo (vazia quando está íntegro)."""
    base = Path(directory) if directory else demo_dir()
    try:
        manifest = load_manifest(base)
    except DemoDataError as exc:
        return [str(exc)]
    problems = []
    for entry in manifest["assets"]:
        path = base / str(entry.get("file", ""))
        if not path.is_file():
            problems.append(f"Arquivo ausente: {path.name}.")
        elif not _file_matches(path, entry.get("sha256", "")):
            problems.append(f"Hash divergente do manifesto: {path.name}.")
    return problems


def _format_date(value) -> str:
    try:
        return pd.Timestamp(str(value)[:10]).strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return "data não informada"


def banner_message(directory=None) -> str:
    """Texto do aviso permanente de versão congelada."""
    try:
        manifest = load_manifest(directory)
    except DemoDataError:
        return (
            "Modo de demonstração ativo: versão congelada, sem consultas "
            "externas."
        )
    version = manifest.get("frozen_version") or "sem identificação"
    collected = _format_date(manifest.get("collected_at"))
    source = manifest.get("source") or "fonte não informada"
    return (
        f"Versão congelada {version} · dados salvos em {collected} "
        f"({source}). Modo de demonstração: nenhuma consulta externa é feita."
    )


# ----------------------------------------------------------------------
# Dados de preços
# ----------------------------------------------------------------------
def normalize_history(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza o retorno de ``Ticker.history`` (mesmas regras do data_loader):
    colunas simples, coluna ``Date`` sem fuso, ordenada.
    """
    if raw is None or raw.empty:
        raise ValueError("Download sem dados.")
    df = raw.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes: {', '.join(missing)}.")
    df = df.reset_index()
    date_column = "Date" if "Date" in df.columns else "Datetime"
    if date_column not in df.columns:
        raise ValueError("Coluna de data ausente.")
    df = df.rename(columns={date_column: "Date"})
    df["Date"] = pd.to_datetime(df["Date"])
    if getattr(df["Date"].dt, "tz", None) is not None:
        df["Date"] = df["Date"].dt.tz_localize(None)
    return df.sort_values("Date").reset_index(drop=True)


def resample_ohlcv(df: pd.DataFrame, interval: str) -> pd.DataFrame:
    """
    Deriva as barras semanais (rótulo: segunda-feira) e mensais (rótulo:
    primeiro dia do mês) a partir das diárias, como o Yahoo Finance rotula.
    """
    if interval == "1d":
        return df
    rule = "W-MON" if interval == "1wk" else "MS"
    options = {"closed": "left", "label": "left"} if interval == "1wk" else {}
    aggregations = {c: f for c, f in _AGGREGATIONS.items() if c in df.columns}
    grouped = df.set_index("Date").resample(rule, **options).agg(aggregations)
    grouped = grouped.dropna(subset=["Close"])
    return grouped.reset_index()


def load_demo_frame(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
    directory=None,
) -> pd.DataFrame:
    """
    Lê o ativo do pacote salvo. ``end_date`` é exclusivo, como no download
    do Yahoo Finance. Qualquer problema levanta ``DemoDataError``.
    """
    interval = str(interval).strip().lower()
    if interval not in SUPPORTED_INTERVALS:
        raise DemoDataError(
            f"Intervalo '{interval}' indisponível no modo de demonstração."
        )
    base = Path(directory) if directory else demo_dir()
    manifest = load_manifest(base)
    symbol = str(ticker).strip().upper()
    entry = next(
        (a for a in manifest["assets"] if str(a.get("ticker", "")).upper() == symbol),
        None,
    )
    if entry is None:
        raise DemoDataError(
            f"'{symbol}' não faz parte dos dados salvos da demonstração."
        )
    path = base / str(entry.get("file", ""))
    if not path.is_file():
        raise DemoDataError(f"Arquivo ausente: {path.name}.")
    if not _file_matches(path, entry.get("sha256", "")):
        raise DemoDataError(f"Hash de {path.name} não confere com o manifesto.")
    try:
        df = pd.read_csv(path)
    except (OSError, ValueError) as exc:
        raise DemoDataError(f"Arquivo ilegível: {path.name}.") from exc
    missing = [c for c in ("Date", *REQUIRED_COLUMNS) if c not in df.columns]
    if missing:
        raise DemoDataError(f"Colunas ausentes em {path.name}: {', '.join(missing)}.")
    try:
        start = pd.Timestamp(str(start_date))
        end = pd.Timestamp(str(end_date))
    except ValueError as exc:
        raise DemoDataError("Datas inválidas para o modo de demonstração.") from exc
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[(df["Date"] >= start) & (df["Date"] < end)]
    if df.empty:
        raise DemoDataError(f"Sem dados salvos para '{symbol}' no período pedido.")
    return resample_ohlcv(df.sort_values("Date"), interval).reset_index(drop=True)


# ----------------------------------------------------------------------
# Respostas de LLM salvas
# ----------------------------------------------------------------------
def load_saved_answers(directory=None) -> dict:
    """Respostas salvas indexadas por ``id``; vazio se o arquivo faltar ou for inválido."""
    base = Path(directory) if directory else demo_dir()
    path = base / LLM_ANSWERS_NAME
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get("respostas", [])
    except (OSError, ValueError, AttributeError):
        return {}
    if not isinstance(items, list):
        return {}
    return {
        str(item["id"]): item
        for item in items
        if isinstance(item, dict) and "id" in item
    }


def get_saved_answer(analysis_id: str, directory=None) -> Optional[str]:
    """Texto salvo, somente se a resposta foi validada (``approved: true``)."""
    entry = load_saved_answers(directory).get(str(analysis_id))
    if not entry or entry.get("approved") is not True:
        return None
    text = entry.get("text")
    if not isinstance(text, str) or not text.strip():
        return None
    return text.strip()


def explanation_for(analysis_id: str, fixed_text: str, directory=None):
    """
    Explicação a exibir: resposta salva e validada ("salva") ou, na falta
    dela, o texto fixo ("fixa"). Nunca chama a API.
    """
    saved = get_saved_answer(analysis_id, directory)
    if saved is not None:
        return saved, "salva"
    return fixed_text, "fixa"