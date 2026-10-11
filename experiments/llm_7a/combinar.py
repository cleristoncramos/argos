"""
Junta as respostas e os casos de mais de uma execução (casos principais + casos
de reserva) em um único par de arquivos, opcionalmente só de alguns modelos.

Serve para montar as planilhas cegas e o relatório final da 7A sobre o mesmo
conjunto: os arquivos de origem não são alterados.

  python -m experiments.llm_7a.combinar \
      --responses experiments/llm_7a/results/respostas.jsonl experiments/llm_7a/results/respostas_reserva_b.jsonl \
      --cases experiments/llm_7a/cases.json experiments/llm_7a/cases_holdout_b.json \
      --models gpt-5-mini --out-dir experiments/llm_7a/results/final
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def combine(cases_payloads: list, records_lists: list, models=None) -> tuple:
    """(payload de casos combinado, registros combinados). Exige o mesmo prompt em tudo."""
    first = cases_payloads[0]
    for payload in cases_payloads:
        if payload["prompt_fingerprint"] != first["prompt_fingerprint"]:
            raise SystemExit("Os arquivos de casos foram gerados com prompts diferentes.")
    cases, seen = [], set()
    for payload in cases_payloads:
        for case in payload["casos"]:
            if case["id"] in seen:
                raise SystemExit(f"Caso repetido entre os arquivos: {case['id']}")
            seen.add(case["id"])
            cases.append(case)
    records = []
    for lst in records_lists:
        for record in lst:
            if record["case_id"] not in seen:
                raise SystemExit(f"Resposta de caso desconhecido: {record['case_id']}")
            if record.get("prompt_fingerprint") != first["prompt_fingerprint"]:
                raise SystemExit("Há respostas gravadas com outro prompt.")
            if models and record["model"] not in models:
                continue
            records.append(record)
    return {**first, "conjunto": "combinado", "casos": cases}, records


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", nargs="+", required=True)
    parser.add_argument("--cases", nargs="+", required=True)
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)
    payloads = [json.loads(Path(p).read_text(encoding="utf-8")) for p in args.cases]
    lists = [
        [json.loads(x) for x in Path(p).read_text(encoding="utf-8").splitlines() if x.strip()]
        for p in args.responses
    ]
    payload, records = combine(payloads, lists, args.models)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "cases_combinado.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "respostas_combinado.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8"
    )
    print(f"{len(payload['casos'])} casos e {len(records)} respostas gravados em {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
