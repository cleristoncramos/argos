"""
Gera o pacote de dados da demonstração (data/demo/).

Execute UMA vez, com internet, antes do congelamento da versão:

    python scripts/gerar_dados_demo.py
    python scripts/gerar_dados_demo.py --years 5 --frozen-version v1.0-demo
    python scripts/gerar_dados_demo.py --verify      # só confere os hashes

Grava um CSV diário por ativo, o manifesto (data da coleta, período, fonte e
hash SHA-256 de cada arquivo) e, se ainda não existir, o arquivo vazio de
respostas de LLM salvas. Depois disso, a aplicação roda sem internet com
ARGOS_DEMO_MODE=true.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.demo_mode import (  # noqa: E402
    LLM_ANSWERS_NAME,
    MANIFEST_NAME,
    SCHEMA_VERSION,
    file_name_for,
    normalize_history,
    sha256_file,
    verify_package,
)

DEFAULT_ASSETS = [
    ("BTC-USD", "Bitcoin"),
    ("AAPL", "Apple"),
    ("PETR4.SA", "Petrobras PN"),
    ("^GSPC", "S&P 500"),
    ("GC=F", "Ouro (contratos futuros)"),
]
SOURCE = "Yahoo Finance via yfinance (auto_adjust=False)"
LLM_SKELETON = {
    "schema_version": SCHEMA_VERSION,
    "descricao": (
        "Respostas de LLM validadas para a demonstração. Cada item: id, text, "
        "model, prompt_version, generated_at, validations, approved. Só itens "
        "com approved=true são usados."
    ),
    "respostas": [],
}


def fetch_yahoo(ticker: str, start: str, end: str, retries: int = 3):
    """Baixa o histórico diário (end é exclusivo) com novas tentativas."""
    import yfinance as yf  # importado aqui: só o gerador precisa de rede

    last_error = None
    for attempt in range(retries):
        try:
            raw = yf.Ticker(ticker).history(
                start=start, end=end, interval="1d", auto_adjust=False
            )
            return normalize_history(raw)
        except Exception as exc:  # noqa: BLE001 - repetir em qualquer falha
            last_error = exc
            time.sleep(1.5)
    raise RuntimeError(f"Falha ao baixar {ticker}: {last_error}")


def build_package(
    fetch,
    assets,
    start: str,
    end: str,
    out_dir,
    frozen_version: str,
    collected_at: str,
) -> dict:
    """Grava CSVs e manifesto em ``out_dir``; devolve o manifesto."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    entries = []
    for ticker, name in assets:
        frame = fetch(ticker, start, end)
        if frame is None or frame.empty:
            raise RuntimeError(f"Sem dados para {ticker}.")
        frame = frame.copy()
        frame["Date"] = frame["Date"].dt.strftime("%Y-%m-%d")
        path = out / file_name_for(ticker)
        frame.to_csv(path, index=False, lineterminator="\n")
        entries.append(
            {
                "ticker": ticker,
                "name": name,
                "file": path.name,
                "rows": int(len(frame)),
                "first_date": str(frame["Date"].iloc[0]),
                "last_date": str(frame["Date"].iloc[-1]),
                "sha256": sha256_file(path),
            }
        )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "frozen_version": frozen_version,
        "collected_at": collected_at,
        "source": SOURCE,
        "interval": "1d",
        "period": {"start": start, "end_exclusive": end},
        "assets": entries,
    }
    (out / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    answers = out / LLM_ANSWERS_NAME
    if not answers.exists():
        answers.write_text(
            json.dumps(LLM_SKELETON, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return manifest


def main(argv=None, fetch=fetch_yahoo, today=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", default=os.path.join(PROJECT_ROOT, "data", "demo"))
    parser.add_argument("--years", type=int, default=5)
    parser.add_argument("--end", default=None, help="AAAA-MM-DD (exclusivo)")
    parser.add_argument("--frozen-version", default="v1.0-demo")
    parser.add_argument("--tickers", nargs="*", default=None)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)

    if args.verify:
        problems = verify_package(args.out)
        for problem in problems:
            print("PROBLEMA:", problem)
        print("Pacote íntegro." if not problems else "Pacote com problemas.")
        return 1 if problems else 0

    today = today or date.today()
    end = args.end or today.isoformat()
    start = (datetime.strptime(end, "%Y-%m-%d") - timedelta(days=365 * args.years)).strftime("%Y-%m-%d")
    names = dict(DEFAULT_ASSETS)
    tickers = args.tickers or [t for t, _ in DEFAULT_ASSETS]
    assets = [(t.upper(), names.get(t.upper(), t.upper())) for t in tickers]

    manifest = build_package(
        fetch, assets, start, end, args.out, args.frozen_version, today.isoformat()
    )
    for entry in manifest["assets"]:
        print(f"{entry['ticker']:10s} {entry['rows']:5d} linhas  {entry['first_date']} a {entry['last_date']}")
    problems = verify_package(args.out)
    print("Pacote gerado e verificado." if not problems else f"Problemas: {problems}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())