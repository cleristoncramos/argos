"""
Modo de demonstração com dados salvos (docs/demonstracao.md, seção 2.4).

Cobre: pacote e manifesto com hash, leitura diária/semanal/mensal, integridade,
respostas de LLM salvas, aviso de versão congelada, logos sem rede, gerador do
pacote e o fluxo completo com a rede bloqueada.
"""

import atexit
import contextlib
import json
import os
import re
import shutil
import socket
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core import asset_logos, data_loader, demo_mode, seasonality
from core.demo_mode import DemoDataError
from scripts import gerar_dados_demo as gerador

ROOT = Path(__file__).resolve().parents[1]
ASSETS = [("BTC-USD", "Bitcoin"), ("AAPL", "Apple"), ("^GSPC", "S&P 500"), ("GC=F", "Ouro")]
_TMP = []


@pytest.fixture(autouse=True)
def _no_sleep_and_fresh_cache(monkeypatch):
    """Isola o cache e as variáveis de ambiente entre os testes."""
    monkeypatch.setattr(data_loader.time, "sleep", lambda *_: None)
    for func in (
        data_loader._download_active_data_cached,
        data_loader._load_demo_data_cached,
    ):
        clear = getattr(func, "clear", None)
        if callable(clear):
            clear()
    demo_mode._hash_ok.cache_clear()
    asset_logos.get_asset_logo_url.cache_clear()
    saved = {k: os.environ.pop(k, None) for k in (demo_mode.ENV_VAR, demo_mode.ENV_DIR_VAR)}
    yield
    for key, value in saved.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@contextlib.contextmanager
def _env(**values):
    old = {k: os.environ.get(k) for k in values}
    for key, value in values.items():
        os.environ[key] = value
    try:
        yield
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


@contextlib.contextmanager
def _no_network():
    """Qualquer tentativa de abrir conexão falha, como num computador offline."""
    def boom(*args, **kwargs):
        raise OSError("rede bloqueada pelo teste")

    originals = (socket.socket.connect, socket.getaddrinfo, socket.create_connection)
    socket.socket.connect = boom
    socket.getaddrinfo = boom
    socket.create_connection = boom
    try:
        yield
    finally:
        socket.socket.connect, socket.getaddrinfo, socket.create_connection = originals


def _fake_fetch(ticker, start, end):
    """Série diária sintética e determinística (cripto inclui fins de semana)."""
    freq = "D" if ticker == "BTC-USD" else "B"
    dates = pd.date_range(start, pd.Timestamp(end) - pd.Timedelta(days=1), freq=freq)
    seed = sum(ord(c) for c in ticker)
    close = 100 + np.cumsum(np.random.default_rng(seed).normal(0.2, 1.0, len(dates)))
    return pd.DataFrame(
        {
            "Date": dates,
            "Open": close - 0.5,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Adj Close": close,
            "Volume": np.arange(len(dates)) + 1000,
            "Dividends": 0.0,
            "Stock Splits": 0.0,
        }
    )


def _new_package(assets=ASSETS, start="2023-01-02", end="2024-07-01"):
    tmp = tempfile.mkdtemp(prefix="argos_demo_")
    _TMP.append(tmp)
    gerador.build_package(_fake_fetch, assets, start, end, tmp, "v1.0-demo", "2026-10-10")
    return Path(tmp)


atexit.register(lambda: [shutil.rmtree(t, ignore_errors=True) for t in _TMP])


# ----------------------------------------------------------------------
# Configuração
# ----------------------------------------------------------------------
def test_is_demo_mode_reads_environment():
    assert demo_mode.is_demo_mode() is False
    for value in ("true", "TRUE", " 1 ", "yes", "sim", "on"):
        with _env(ARGOS_DEMO_MODE=value):
            assert demo_mode.is_demo_mode() is True
    for value in ("false", "0", "", "talvez"):
        with _env(ARGOS_DEMO_MODE=value):
            assert demo_mode.is_demo_mode() is False


def test_demo_dir_default_and_override():
    assert demo_mode.demo_dir() == ROOT / "data" / "demo"
    with _env(ARGOS_DEMO_DIR="/tmp/outra_pasta"):
        assert demo_mode.demo_dir() == Path("/tmp/outra_pasta")


def test_file_name_for_is_filesystem_safe():
    assert demo_mode.file_name_for("^GSPC") == "_GSPC.csv"
    assert demo_mode.file_name_for(" gc=f ") == "GC_F.csv"
    assert demo_mode.file_name_for("PETR4.SA") == "PETR4.SA.csv"


# ----------------------------------------------------------------------
# Pacote, manifesto e integridade
# ----------------------------------------------------------------------
def test_build_package_writes_files_and_manifest():
    pkg = _new_package()
    manifest = demo_mode.load_manifest(pkg)
    assert manifest["frozen_version"] == "v1.0-demo"
    assert manifest["collected_at"] == "2026-10-10"
    assert manifest["interval"] == "1d"
    assert [a["ticker"] for a in manifest["assets"]] == [t for t, _ in ASSETS]
    for entry in manifest["assets"]:
        path = pkg / entry["file"]
        assert path.is_file()
        assert entry["sha256"] == demo_mode.sha256_file(path)
        assert entry["rows"] > 100
    assert (pkg / demo_mode.LLM_ANSWERS_NAME).is_file()
    assert demo_mode.verify_package(pkg) == []
    assert demo_mode.demo_tickers(pkg) == ["BTC-USD", "AAPL", "^GSPC", "GC=F"]
    assert demo_mode.is_demo_asset(" aapl ", pkg) is True
    assert demo_mode.is_demo_asset("PETR4.SA", pkg) is False


def test_hash_ignores_line_ending_conversion():
    pkg = _new_package()
    path = pkg / "AAPL.csv"
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert demo_mode.verify_package(pkg) == []


def test_verify_package_detects_problems():
    pkg = _new_package()
    (pkg / "AAPL.csv").write_text("Date,Open\n2024-01-01,1\n", encoding="utf-8")
    (pkg / "GC_F.csv").unlink()
    problems = demo_mode.verify_package(pkg)
    assert any("Hash divergente" in p and "AAPL.csv" in p for p in problems)
    assert any("Arquivo ausente" in p and "GC_F.csv" in p for p in problems)


def test_manifest_errors():
    empty = Path(tempfile.mkdtemp(prefix="argos_demo_"))
    _TMP.append(str(empty))
    with pytest.raises(DemoDataError, match="não encontrado"):
        demo_mode.load_manifest(empty)
    assert demo_mode.demo_tickers(empty) == []
    assert "não encontrado" in demo_mode.verify_package(empty)[0]

    (empty / demo_mode.MANIFEST_NAME).write_text("{ não é json", encoding="utf-8")
    with pytest.raises(DemoDataError, match="ilegível"):
        demo_mode.load_manifest(empty)

    (empty / demo_mode.MANIFEST_NAME).write_text(json.dumps({"schema_version": 99}), encoding="utf-8")
    with pytest.raises(DemoDataError, match="inválido"):
        demo_mode.load_manifest(empty)

    (empty / demo_mode.MANIFEST_NAME).write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(DemoDataError, match="inválido"):
        demo_mode.load_manifest(empty)


# ----------------------------------------------------------------------
# Leitura dos dados
# ----------------------------------------------------------------------
def test_load_daily_range_has_exclusive_end():
    pkg = _new_package()
    df = demo_mode.load_demo_frame("aapl", "2023-03-01", "2023-04-01", "1d", pkg)
    assert list(df.columns[:6]) == ["Date", "Open", "High", "Low", "Close", "Adj Close"]
    assert df["Date"].min() >= pd.Timestamp("2023-03-01")
    assert df["Date"].max() < pd.Timestamp("2023-04-01")
    assert df["Date"].is_monotonic_increasing
    assert df["Date"].dt.tz is None


def test_load_weekly_aggregates_monday_labels():
    pkg = _new_package()
    daily = demo_mode.load_demo_frame("AAPL", "2023-01-02", "2023-06-01", "1d", pkg)
    weekly = demo_mode.load_demo_frame("AAPL", "2023-01-02", "2023-06-01", "1wk", pkg)
    assert (weekly["Date"].dt.dayofweek == 0).all()
    week = daily[(daily["Date"] >= "2023-03-06") & (daily["Date"] <= "2023-03-10")]
    row = weekly[weekly["Date"] == pd.Timestamp("2023-03-06")].iloc[0]
    assert row["Open"] == week["Open"].iloc[0]
    assert row["Close"] == week["Close"].iloc[-1]
    assert row["High"] == week["High"].max()
    assert row["Low"] == week["Low"].min()
    assert row["Volume"] == week["Volume"].sum()


def test_load_monthly_aggregates_first_day_labels():
    pkg = _new_package()
    daily = demo_mode.load_demo_frame("BTC-USD", "2023-01-02", "2024-06-01", "1d", pkg)
    monthly = demo_mode.load_demo_frame("BTC-USD", "2023-01-02", "2024-06-01", "1mo", pkg)
    assert (monthly["Date"].dt.day == 1).all()
    march = daily[(daily["Date"] >= "2023-03-01") & (daily["Date"] < "2023-04-01")]
    row = monthly[monthly["Date"] == pd.Timestamp("2023-03-01")].iloc[0]
    assert row["Close"] == march["Close"].iloc[-1]
    assert row["Volume"] == march["Volume"].sum()


def test_resample_without_optional_columns():
    df = _fake_fetch("AAPL", "2023-01-02", "2023-03-01")[["Date", "Open", "High", "Low", "Close", "Volume"]]
    out = demo_mode.resample_ohlcv(df, "1mo")
    assert list(out.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    assert demo_mode.resample_ohlcv(df, "1d") is df


def test_load_errors():
    pkg = _new_package()
    with pytest.raises(DemoDataError, match="indisponível"):
        demo_mode.load_demo_frame("AAPL", "2023-01-02", "2023-02-01", "1h", pkg)
    with pytest.raises(DemoDataError, match="não faz parte"):
        demo_mode.load_demo_frame("PETR4.SA", "2023-01-02", "2023-02-01", "1d", pkg)
    with pytest.raises(DemoDataError, match="Sem dados salvos"):
        demo_mode.load_demo_frame("AAPL", "2010-01-01", "2010-02-01", "1d", pkg)
    with pytest.raises(DemoDataError, match="Datas inválidas"):
        demo_mode.load_demo_frame("AAPL", "ontem", "hoje", "1d", pkg)

    (pkg / "GC_F.csv").unlink()
    with pytest.raises(DemoDataError, match="Arquivo ausente"):
        demo_mode.load_demo_frame("GC=F", "2023-01-02", "2023-02-01", "1d", pkg)

    (pkg / "AAPL.csv").write_text("alterado", encoding="utf-8")
    with pytest.raises(DemoDataError, match="não confere"):
        demo_mode.load_demo_frame("AAPL", "2023-01-02", "2023-02-01", "1d", pkg)


def _rewrite_with_valid_hash(pkg, ticker, content):
    """Troca o conteúdo do CSV e atualiza o hash do manifesto (arquivo íntegro, mas inválido)."""
    manifest = demo_mode.load_manifest(pkg)
    entry = next(a for a in manifest["assets"] if a["ticker"] == ticker)
    path = pkg / entry["file"]
    path.write_text(content, encoding="utf-8")
    entry["sha256"] = demo_mode.sha256_file(path)
    (pkg / demo_mode.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")


def test_load_rejects_unreadable_or_incomplete_csv():
    pkg = _new_package()
    _rewrite_with_valid_hash(pkg, "AAPL", "")
    with pytest.raises(DemoDataError, match="ilegível"):
        demo_mode.load_demo_frame("AAPL", "2023-01-02", "2023-02-01", "1d", pkg)
    _rewrite_with_valid_hash(pkg, "^GSPC", "Date,Open\n2023-01-02,1\n")
    with pytest.raises(DemoDataError, match="Colunas ausentes"):
        demo_mode.load_demo_frame("^GSPC", "2023-01-02", "2023-02-01", "1d", pkg)


# ----------------------------------------------------------------------
# Aviso de versão congelada
# ----------------------------------------------------------------------
def test_banner_message():
    pkg = _new_package()
    text = demo_mode.banner_message(pkg)
    assert "v1.0-demo" in text and "10/10/2026" in text and "Yahoo Finance" in text
    assert "nenhuma consulta externa" in text

    manifest = demo_mode.load_manifest(pkg)
    manifest["collected_at"] = "sem data"
    manifest["frozen_version"] = ""
    manifest["source"] = ""
    (pkg / demo_mode.MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
    text = demo_mode.banner_message(pkg)
    assert "sem identificação" in text and "data não informada" in text and "fonte não informada" in text

    missing = Path(tempfile.mkdtemp(prefix="argos_demo_"))
    _TMP.append(str(missing))
    assert "versão congelada" in demo_mode.banner_message(missing)


# ----------------------------------------------------------------------
# Respostas de LLM salvas
# ----------------------------------------------------------------------
def _write_answers(pkg, payload):
    (pkg / demo_mode.LLM_ANSWERS_NAME).write_text(
        payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8"
    )


def test_saved_answers_only_approved_are_used():
    pkg = _new_package()
    assert demo_mode.load_saved_answers(pkg) == {}
    (pkg / demo_mode.LLM_ANSWERS_NAME).unlink()
    assert demo_mode.load_saved_answers(pkg) == {}
    assert demo_mode.explanation_for("a1", "fixo", pkg) == ("fixo", "fixa")
    _write_answers(
        pkg,
        {
            "respostas": [
                {"id": "a1", "text": "  Texto validado.  ", "approved": True},
                {"id": "a2", "text": "Não validado.", "approved": False},
                {"id": "a3", "text": "   ", "approved": True},
                {"id": "a4", "text": 5, "approved": True},
                {"sem_id": True},
                "lixo",
            ]
        },
    )
    assert demo_mode.get_saved_answer("a1", pkg) == "Texto validado."
    assert demo_mode.get_saved_answer("a2", pkg) is None
    assert demo_mode.get_saved_answer("a3", pkg) is None
    assert demo_mode.get_saved_answer("a4", pkg) is None
    assert demo_mode.get_saved_answer("inexistente", pkg) is None
    assert demo_mode.explanation_for("a1", "fixo", pkg) == ("Texto validado.", "salva")
    assert demo_mode.explanation_for("a2", "fixo", pkg) == ("fixo", "fixa")


def test_saved_answers_tolerate_invalid_files():
    pkg = _new_package()
    _write_answers(pkg, "{ quebrado")
    assert demo_mode.load_saved_answers(pkg) == {}
    _write_answers(pkg, "[1, 2]")
    assert demo_mode.load_saved_answers(pkg) == {}
    _write_answers(pkg, {"respostas": "texto"})
    assert demo_mode.load_saved_answers(pkg) == {}
    assert demo_mode.explanation_for("x", "texto fixo", pkg) == ("texto fixo", "fixa")


# ----------------------------------------------------------------------
# normalize_history
# ----------------------------------------------------------------------
def test_normalize_history_variants():
    frame = _fake_fetch("AAPL", "2024-01-02", "2024-01-20").set_index("Date")
    out = demo_mode.normalize_history(frame)
    assert out.columns[0] == "Date" and len(out) == len(frame)

    cols = pd.MultiIndex.from_product([["Open", "High", "Low", "Close", "Volume"], ["AAA"]])
    multi = pd.DataFrame(
        np.ones((3, 5)),
        index=pd.date_range("2024-01-02", periods=3, name="Date"),
        columns=cols,
    )
    assert list(demo_mode.normalize_history(multi).columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]

    tz = frame.copy()
    tz.index = tz.index.tz_localize("America/Sao_Paulo")
    tz.index.name = "Datetime"
    assert demo_mode.normalize_history(tz.iloc[::-1])["Date"].dt.tz is None

    with pytest.raises(ValueError, match="sem dados"):
        demo_mode.normalize_history(pd.DataFrame())
    with pytest.raises(ValueError, match="Colunas ausentes"):
        demo_mode.normalize_history(frame[["Open"]])
    with pytest.raises(ValueError, match="data ausente"):
        demo_mode.normalize_history(frame.reset_index(drop=True))


# ----------------------------------------------------------------------
# data_loader em modo demo
# ----------------------------------------------------------------------
class _ExplodingTicker:
    def __init__(self, *args, **kwargs):
        raise AssertionError("o Yahoo Finance não pode ser consultado no modo demo")


def test_demo_mode_never_calls_yahoo_and_works_offline(monkeypatch):
    pkg = _new_package()
    monkeypatch.setattr(data_loader.yf, "Ticker", _ExplodingTicker)
    with _env(ARGOS_DEMO_MODE="true", ARGOS_DEMO_DIR=str(pkg)), _no_network():
        df = data_loader.download_active_data("aapl", "2023-03-01", "2023-03-31", "1D")
        assert df is not None and not df.empty
        # a data final é inclusiva para o chamador (o loader soma 1 dia)
        assert df["Date"].max() == pd.Timestamp("2023-03-31")
        again = data_loader.download_active_data("AAPL", "2023-03-01", "2023-03-31", "1d")
        assert again.equals(df)
        assert data_loader.validate_data(df)["has_data"] is True


def test_demo_mode_returns_none_outside_package(monkeypatch):
    pkg = _new_package()
    monkeypatch.setattr(data_loader.yf, "Ticker", _ExplodingTicker)
    with _env(ARGOS_DEMO_MODE="true", ARGOS_DEMO_DIR=str(pkg)), _no_network():
        assert data_loader.download_active_data("PETR4.SA", "2023-03-01", "2023-03-31") is None
        assert data_loader.download_active_data("AAPL", "2023-03-01", "2023-03-31", "5m") is None
        assert data_loader.download_active_data("  ", "2023-03-01", "2023-03-31") is None
        (pkg / "AAPL.csv").write_text("corrompido", encoding="utf-8")
        assert data_loader.download_active_data("AAPL", "2023-03-01", "2023-03-31") is None


def test_normal_mode_still_uses_the_source(monkeypatch):
    calls = []
    frame = _fake_fetch("AAPL", "2024-01-02", "2024-02-01").set_index("Date")

    class FakeTicker:
        def __init__(self, symbol):
            calls.append(symbol)

        def history(self, **kwargs):
            return frame.copy()

    monkeypatch.setattr(data_loader.yf, "Ticker", FakeTicker)
    df = data_loader.download_active_data("aapl", "2024-01-02", "2024-01-31", "1d")
    assert calls == ["AAPL"] and len(df) == len(frame)


# ----------------------------------------------------------------------
# Logos sem rede
# ----------------------------------------------------------------------
def test_logos_are_disabled_in_demo_mode():
    assert asset_logos.get_asset_logo_url("BTC-USD", "crypto").startswith("https://")
    assert asset_logos.get_asset_logo_url("^GSPC", "indexes").startswith("https://")
    assert asset_logos.get_asset_logo_url("GC=F", "commodities") is None
    assert asset_logos.get_asset_logo_url("aapl", "us_stocks").endswith("/AAPL.png")
    with _env(ARGOS_DEMO_MODE="true"):
        assert asset_logos.get_asset_logo_url("BTC-USD", "crypto") is None
        assert asset_logos.get_asset_logo_url("AAPL", "us_stocks") is None
        assert asset_logos.get_asset_logo_url("^GSPC", "indexes") is None


# ----------------------------------------------------------------------
# Gerador do pacote
# ----------------------------------------------------------------------
def test_generator_requires_data():
    tmp = tempfile.mkdtemp(prefix="argos_demo_")
    _TMP.append(tmp)
    with pytest.raises(RuntimeError, match="Sem dados"):
        gerador.build_package(lambda *a: pd.DataFrame(), ASSETS[:1], "2023-01-02", "2023-02-01", tmp, "v", "2026-10-10")
    with pytest.raises(RuntimeError, match="Sem dados"):
        gerador.build_package(lambda *a: None, ASSETS[:1], "2023-01-02", "2023-02-01", tmp, "v", "2026-10-10")


def test_generator_keeps_existing_llm_answers():
    pkg = _new_package(assets=ASSETS[:1])
    _write_answers(pkg, {"respostas": [{"id": "x", "text": "t", "approved": True}]})
    gerador.build_package(_fake_fetch, ASSETS[:1], "2023-01-02", "2023-02-01", pkg, "v", "2026-10-10")
    assert demo_mode.get_saved_answer("x", pkg) == "t"


def test_generator_main_and_verify():
    from datetime import date

    tmp = tempfile.mkdtemp(prefix="argos_demo_")
    _TMP.append(tmp)
    code = gerador.main(
        ["--out", tmp, "--years", "1", "--tickers", "aapl", "xyz", "--frozen-version", "v9"],
        fetch=_fake_fetch,
        today=date(2026, 10, 10),
    )
    assert code == 0
    manifest = demo_mode.load_manifest(tmp)
    assert [(a["ticker"], a["name"]) for a in manifest["assets"]] == [("AAPL", "Apple"), ("XYZ", "XYZ")]
    assert manifest["period"] == {"start": "2025-10-10", "end_exclusive": "2026-10-10"}
    assert manifest["frozen_version"] == "v9"
    assert gerador.main(["--out", tmp, "--verify"]) == 0

    (Path(tmp) / "AAPL.csv").write_text("x", encoding="utf-8")
    assert gerador.main(["--out", tmp, "--verify"]) == 1
    code = gerador.main(["--out", tmp, "--end", "2026-01-31", "--tickers", "AAPL"], fetch=_fake_fetch)
    assert code == 0
    assert demo_mode.load_manifest(tmp)["period"]["end_exclusive"] == "2026-01-31"


def test_generator_default_assets_match_the_plan():
    assert [t for t, _ in gerador.DEFAULT_ASSETS] == ["BTC-USD", "AAPL", "PETR4.SA", "^GSPC", "GC=F"]


def test_fetch_yahoo_retries_then_fails(monkeypatch):
    import yfinance

    attempts = []
    frame = _fake_fetch("AAPL", "2024-01-02", "2024-02-01").set_index("Date")

    class Flaky:
        def __init__(self, symbol):
            pass

        def history(self, **kwargs):
            attempts.append(kwargs["interval"])
            if len(attempts) < 2:
                raise ConnectionError("falha temporária")
            return frame.copy()

    monkeypatch.setattr(yfinance, "Ticker", Flaky)
    monkeypatch.setattr(gerador.time, "sleep", lambda *_: None)
    assert len(gerador.fetch_yahoo("AAPL", "2024-01-02", "2024-02-01")) == len(frame)
    assert attempts == ["1d", "1d"]

    class Broken(Flaky):
        def history(self, **kwargs):
            raise ConnectionError("fora do ar")

    monkeypatch.setattr(yfinance, "Ticker", Broken)
    with pytest.raises(RuntimeError, match="Falha ao baixar AAPL"):
        gerador.fetch_yahoo("AAPL", "2024-01-02", "2024-02-01", retries=2)


# ----------------------------------------------------------------------
# Fluxo completo da demo com a rede bloqueada
# ----------------------------------------------------------------------
def test_full_demo_flow_offline(monkeypatch):
    pkg = _new_package()
    monkeypatch.setattr(data_loader.yf, "Ticker", _ExplodingTicker)
    with _env(ARGOS_DEMO_MODE="true", ARGOS_DEMO_DIR=str(pkg)), _no_network():
        assert demo_mode.verify_package() == []
        for ticker in demo_mode.demo_tickers():
            for interval in ("1d", "1wk", "1mo"):
                df = data_loader.download_active_data(ticker, "2023-01-02", "2024-06-30", interval)
                assert df is not None and len(df) > 5, (ticker, interval)
            monthly = seasonality.monthly_closes(df.rename(columns={"Close": "Value"}))
            assert len(monthly) >= 12
        text, source = demo_mode.explanation_for("sem-resposta", "Texto fixo do roteiro.")
        assert (text, source) == ("Texto fixo do roteiro.", "fixa")
        assert "Versão congelada" in demo_mode.banner_message()


# ----------------------------------------------------------------------
# Estrutura do código: sem rede fora dos pontos previstos
# ----------------------------------------------------------------------
NETWORK_MODULES = r"^\s*(?:import|from)\s+(requests|urllib|urllib3|httpx|aiohttp|http\.client|socket|yfinance)\b"
NETWORK_ALLOWED = {"core/data_loader.py", "scripts/gerar_dados_demo.py"}
REMOTE_RESOURCE_PATTERNS = [
    r"""src\s*=\s*["']https?://""",
    r"""<link[^>]+href\s*=\s*["']https?://""",
    r"""url\(\s*["']?https?://""",
    r"""@import\s+(?:url\()?["']?https?://""",
    r"""st\.image\(\s*["']https?://""",
]
# Logos remotos ficam só em asset_logos, que devolve None no modo demo.
REMOTE_RESOURCE_ALLOWED_FILES = {"core/asset_logos.py"}


def _python_sources():
    for folder in ("app", "core", "scripts"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            yield path.relative_to(ROOT).as_posix(), path.read_text(encoding="utf-8")


def test_network_libraries_only_where_expected():
    offenders = []
    for rel, text in _python_sources():
        if rel in NETWORK_ALLOWED:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if re.search(NETWORK_MODULES, line):
                offenders.append(f"{rel}:{number}: {line.strip()}")
    assert offenders == [], "Acesso à rede fora de data_loader/gerador:\n" + "\n".join(offenders)


def test_no_remote_resources_in_pages():
    offenders = []
    for rel, text in _python_sources():
        if rel in REMOTE_RESOURCE_ALLOWED_FILES:
            continue
        for pattern in REMOTE_RESOURCE_PATTERNS:
            for match in re.finditer(pattern, text):
                line = text.count("\n", 0, match.start()) + 1
                offenders.append(f"{rel}:{line}: {match.group(0)}")
    assert offenders == [], "Recursos remotos que exigem internet na demo:\n" + "\n".join(offenders)


def test_main_renders_the_demo_banner_before_running_the_page():
    source = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    assert "from app.ui.demo_banner import render_demo_banner" in source
    assert source.index("render_demo_banner()") < source.index("pg.run()")