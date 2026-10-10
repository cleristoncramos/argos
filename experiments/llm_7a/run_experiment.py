"""
Linha de comando do experimento 7A.

  python -m experiments.llm_7a.run_experiment --dry-run
  python -m experiments.llm_7a.run_experiment --probe
  python -m experiments.llm_7a.run_experiment --max-cost 2

A chave é lida de OPENAI_API_KEY. Os resultados vão para
experiments/llm_7a/results/respostas.jsonl (fora do Git).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from experiments.llm_7a import runner

try:  # catálogo para detectar ativos de fora do contexto
    from core.assets import ASSETS
    KNOWN = [asset["ticker"] for asset in ASSETS]
except Exception:  # pragma: no cover - o catálogo é opcional aqui
    KNOWN = []


def known_tickers(cases_payload: dict) -> list:
    tickers = set()
    for case in cases_payload["casos"]:
        tickers.update(case["contexto"]["assets"])
    return sorted(tickers | {t for t in KNOWN if isinstance(t, str)})


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="experiments/llm_7a/cases.json")
    parser.add_argument("--out", default="experiments/llm_7a/results/respostas.jsonl")
    parser.add_argument("--models", nargs="+", default=list(runner.DEFAULT_MODELS))
    parser.add_argument("--repetitions", type=int, default=runner.DEFAULT_REPETITIONS)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--max-cost", type=float, default=2.0, help="Teto de custo em US$ desta execução.")
    parser.add_argument("--reasoning-effort", default="minimal", help="'' para não enviar.")
    parser.add_argument("--only", nargs="*", default=None, help="Ids de casos a rodar.")
    parser.add_argument("--dry-run", action="store_true", help="Cliente simulado, sem rede e sem custo.")
    parser.add_argument("--probe", action="store_true", help="Uma chamada por modelo no primeiro caso.")
    args = parser.parse_args(argv)

    payload = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    missing = [c["id"] for c in payload["casos"] if not str(c.get("resposta_esperada", "")).strip()]
    if missing:
        raise SystemExit(f"Casos sem resposta esperada escrita: {', '.join(missing)}")

    digest = hashlib.sha256(Path(args.cases).read_bytes()).hexdigest()[:16]
    print(f"cases.json sha256={digest} | prompt {payload['prompt_version']} ({payload['prompt_fingerprint']})")

    params = {"reasoning_effort": args.reasoning_effort} if args.reasoning_effort else {}
    if args.dry_run:
        transport, key = runner.fake_transport, "dry-run"
    else:
        transport, key = runner.http_transport, runner.get_api_key()

    out = Path(args.out)
    repetitions, only = args.repetitions, args.only
    if args.probe:
        out = out.with_name("sonda.jsonl")
        repetitions, only = 1, [payload["casos"][0]["id"]]

    summary = runner.run_experiment(
        payload, out, args.models, repetitions, key, transport, args.max_tokens,
        params, args.max_cost, known_tickers(payload), only, args.dry_run,
    )
    print(json.dumps(summary, ensure_ascii=False))
    if args.probe:
        for line in out.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            print(f"{r['model']}: tokens saída={r['output_tokens']} fim={r.get('finish_reason')} "
                  f"removidos={r.get('params_removed')} latência={r['latency_s']}s custo=US${r['cost_usd']:.5f} "
                  f"válido={r['validation']['ok']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
