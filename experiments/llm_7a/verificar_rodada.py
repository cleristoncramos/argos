"""
Confere uma pasta de planilhas ANTES de entregá-la aos avaliadores.

Verifica: prefixo dos ids, mesmo conjunto de itens nas três planilhas, todos de calibração,
frase "EXCLUSIVAMENTE" nas recusas da planilha técnica (e ausência do texto antigo), e se
alguma resposta é idêntica às de planilhas de rodadas anteriores.

Uso:
  python -m experiments.llm_7a.verificar_rodada --planilhas experiments/llm_7a/results/final/avaliacao4 \
      --prefixo T --anteriores experiments/llm_7a/results/final/avaliacao_rodada1 experiments/llm_7a/results/final/avaliacao2
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def _rows(path: Path) -> list:
    with path.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def check(folder: Path, prefix: str, previous: list) -> list:
    """Devolve a lista de problemas (vazia = tudo certo)."""
    problems = []
    sheets = {}
    for name in ("leigo", "neutro", "tecnico"):
        path = folder / f"{name}.csv"
        if not path.exists():
            problems.append(f"Falta {name}.csv")
        else:
            sheets[name] = _rows(path)
    if problems:
        return problems
    ids = {name: [r["id_cego"] for r in rows] for name, rows in sheets.items()}
    if not (ids["leigo"] == ids["neutro"] == ids["tecnico"]):
        problems.append("As três planilhas não têm os mesmos ids, na mesma ordem.")
    if not ids["leigo"]:
        problems.append("Planilhas vazias.")
    bad = [i for i in ids["leigo"] if not i.startswith(prefix)]
    if bad:
        problems.append(f"Ids sem o prefixo {prefix}: {', '.join(bad[:5])}")
    if any(r["calibracao"] != "sim" for rows in sheets.values() for r in rows):
        problems.append("Há itens que não são de calibração (todos devem ser avaliados pelos três).")
    for r in sheets["tecnico"]:
        negative = r["caso"].startswith("Negativo")
        text = r["resposta_esperada"]
        if negative and "EXCLUSIVAMENTE" not in text:
            problems.append(f"{r['id_cego']}: recusa sem 'EXCLUSIVAMENTE' na resposta esperada.")
        if "apenas descreve" in text or "e depois apenas" in text:
            problems.append(f"{r['id_cego']}: resposta esperada ainda é a versão antiga.")
    old = set()
    for prev in previous:
        for name in ("leigo", "neutro", "tecnico"):
            path = Path(prev) / f"{name}.csv"
            if path.exists():
                old.update(r["resposta_do_sistema"].strip() for r in _rows(path))
    repeated = [r["id_cego"] for r in sheets["leigo"] if r["resposta_do_sistema"].strip() in old]
    if repeated:
        problems.append(f"Respostas idênticas às de rodadas anteriores: {', '.join(repeated)}")
    for name, rows in sheets.items():
        if any((r.get("nota_clareza") or "").strip() for r in rows):
            problems.append(f"{name}.csv já tem notas preenchidas (entregue planilhas em branco).")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--planilhas", required=True)
    parser.add_argument("--prefixo", default="T")
    parser.add_argument("--anteriores", nargs="*", default=[])
    args = parser.parse_args(argv)
    problems = check(Path(args.planilhas), args.prefixo, args.anteriores)
    if problems:
        print("PROBLEMAS ENCONTRADOS (não entregue as planilhas):")
        for p in problems:
            print(" -", p)
        return 1
    n = len(_rows(Path(args.planilhas) / "leigo.csv"))
    print(f"OK: {n} itens, ids com prefixo {args.prefixo}, recusas com 'EXCLUSIVAMENTE', nenhuma resposta repetida.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
