"""
Diagnóstico das respostas reprovadas: mostra, por falha, o motivo, o fim da
geração (stop/length), os tokens e um trecho do texto.

  python -m experiments.llm_7a.diagnose --responses experiments/llm_7a/results/piloto.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def summarize(records: list, width: int = 220) -> str:
    lines = []
    failed = [r for r in records if not r["validation"]["ok"]]
    lines.append(f"Reprovadas: {len(failed)} de {len(records)}")
    by_model = Counter(r["model"] for r in failed)
    lines.append("Por modelo: " + ", ".join(f"{m}={n}" for m, n in sorted(by_model.items())))
    first = Counter()
    for r in failed:
        names = r["validation"].get("failed") or []
        first[names[0] if names else "?"] += 1
    lines.append("Primeira verificação reprovada: " + ", ".join(f"{k}={v}" for k, v in first.most_common()))
    lengths = [r for r in records if r.get("finish_reason") == "length"]
    lines.append(f"Respostas cortadas por limite de tokens (finish_reason=length): {len(lengths)}")
    lines.append("")
    for r in failed:
        v = r["validation"]
        lines.append(
            f"[{r['model']} {r['case_id']} #{r['repetition']}] fim={r.get('finish_reason')} "
            f"tokens_saida={r.get('output_tokens')} reprovou={','.join(v.get('failed', []))}"
        )
        for name, detail in (v.get("details") or {}).items():
            lines.append(f"    {name}: {detail}")
        raw = (r.get("raw") or "").replace("\n", " ")
        try:
            resumo = json.loads(raw).get("resumo", "")
        except ValueError:
            resumo = "(JSON inválido) ..." + raw[-width:]
        lines.append(f"    resumo: {resumo[:width]}")
        if r.get("error"):
            lines.append(f"    erro: {r['error']}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", default="experiments/llm_7a/results/respostas.jsonl")
    parser.add_argument("--out", default=None, help="Grava em arquivo (UTF-8) além de imprimir.")
    args = parser.parse_args(argv)
    records = [json.loads(x) for x in Path(args.responses).read_text(encoding="utf-8").splitlines() if x.strip()]
    text = summarize(records)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
