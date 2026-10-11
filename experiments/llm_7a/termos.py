"""
Mostra, para cada resposta reprovada em `sem_termos_proibidos`, a frase e o
campo onde o termo apareceu.

  python -m experiments.llm_7a.termos --responses experiments/llm_7a/results/piloto.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from core import llm_validation as lv

FIELDS = ("resumo", "o_que_o_grafico_mostra", "limitacoes", "o_que_nao_pode_ser_concluido", "nota_educativa")


def find_terms(raw: str) -> list:
    """[(campo, frase, termo)] com os termos rígidos encontrados no JSON."""
    try:
        data = json.loads(raw)
    except ValueError:
        return []
    out = []
    for field in FIELDS:
        value = data.get(field, "")
        texts = value if isinstance(value, list) else [value]
        for text in texts:
            for sentence in re.split(r"(?<=[.!?])\s+", str(text)):
                for hit, _ in lv._forbidden_hits(lv.fold(sentence)):
                    out.append((field, sentence.strip(), hit))
    for metric in data.get("metricas_relevantes", []):
        for hit, _ in lv._forbidden_hits(lv.fold(str(metric.get("leitura", "")))):
            out.append(("metricas_relevantes.leitura", str(metric.get("leitura", "")), hit))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", default="experiments/llm_7a/results/piloto.jsonl")
    args = parser.parse_args(argv)
    records = [json.loads(x) for x in Path(args.responses).read_text(encoding="utf-8").splitlines() if x.strip()]
    for r in records:
        if "sem_termos_proibidos" not in (r["validation"].get("failed") or []):
            continue
        print(f"[{r['model']} {r['case_id']} #{r['repetition']}]")
        for field, sentence, term in find_terms(r.get("raw", "")):
            print(f"    {field}: «{term}» em: {sentence}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
