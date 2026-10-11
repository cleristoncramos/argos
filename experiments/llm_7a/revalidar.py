"""
Revalida, sem chamar a API (custo zero), respostas já gravadas com o validador atual.

Serve quando só o validador muda: o texto bruto do modelo continua o mesmo, então
não é preciso gastar de novo. O arquivo original NÃO é alterado; o resultado vai
para --out. Se o PROMPT mudar, as respostas antigas não valem e é preciso rodar de novo.

Uso:
    python -m experiments.llm_7a.revalidar --responses experiments/llm_7a/results/piloto.jsonl \
        --out experiments/llm_7a/results/piloto_revalidado.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from core import llm_validation
from experiments.llm_7a.run_experiment import known_tickers


def revalidate(cases_payload: dict, records: list) -> tuple:
    """(registros revalidados, quantos mudaram de aprovado para reprovado e vice-versa)."""
    cases = {c["id"]: c for c in cases_payload["casos"]}
    tickers = known_tickers(cases_payload)
    out, now_fail, now_pass = [], 0, 0
    for record in records:
        case = cases.get(record["case_id"])
        if case is None:
            raise SystemExit(f"Caso desconhecido no arquivo de respostas: {record['case_id']}")
        result = llm_validation.validate_response(record.get("raw", ""), case["contexto"], tickers)
        new = {**result.as_dict(), "failed": result.failed}
        old_ok = record.get("validation", {}).get("ok")
        now_fail += bool(old_ok and not new["ok"])
        now_pass += bool((old_ok is False) and new["ok"])
        out.append({**record, "validation": new})
    return out, (now_fail, now_pass)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="experiments/llm_7a/cases.json")
    parser.add_argument("--responses", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    lines = Path(args.responses).read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines if line.strip()]
    revalidated, (now_fail, now_pass) = revalidate(payload, records)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in revalidated), encoding="utf-8")
    print(f"{len(revalidated)} respostas revalidadas -> {out} | passaram a reprovar: {now_fail} | passaram a aprovar: {now_pass}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
