"""
Gera o arquivo de respostas salvas do modo demonstração (7B) a partir dos
resultados da 7A (somente respostas válidas do gpt-5-mini com o prompt v0.6).

  python -m experiments.llm_7b.make_demo_store \
      --responses experiments/llm_7a/results/final/respostas_combinado.jsonl \
      --cases experiments/llm_7a/results/final/cases_combinado.json \
      --out data/llm_demo.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from core import llm_service


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--out", default="data/llm_demo.json")
    args = parser.parse_args(argv)
    records = [json.loads(x) for x in Path(args.responses).read_text(encoding="utf-8").splitlines() if x.strip()]
    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))["casos"]
    store = llm_service.build_demo_store(records, cases)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(store, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(store['respostas'])} respostas salvas em {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
