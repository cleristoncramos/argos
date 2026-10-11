"""
Consolida validação automática + notas humanas e escreve o relatório 7A.

  python -m experiments.llm_7a.analyze --ratings experiments/llm_7a/results/avaliacao

Os arquivos preenchidos devem se chamar leigo.csv, tecnico.csv e neutro.csv
(mesmo formato das planilhas geradas, separador ";").
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

from core import llm_eval
from experiments.llm_7a.make_rating_sheets import RATERS


def _read_csv(path: Path) -> list:
    with path.open(newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def _num(value):
    text = str(value or "").strip().replace(",", ".")
    if not text:
        return None
    number = float(text)
    if number != int(number) or not 0 <= number <= 5:
        raise ValueError(f"Nota inválida (use inteiros de 0 a 5): {value}")
    return int(number)


def _flag(value):
    text = str(value or "").strip().lower()
    if not text:
        return None
    if text in ("1", "sim", "s", "true"):
        return True
    if text in ("0", "nao", "não", "n", "false"):
        return False
    raise ValueError(f"Marcação inválida (use sim/nao ou 1/0): {value}")


def load_ratings(directory: Path) -> dict:
    """{rater: {id_cego: linha}}; avaliadores sem arquivo ficam de fora."""
    out = {}
    for rater in RATERS:
        path = Path(directory) / f"{rater}.csv"
        if path.exists():
            out[rater] = {row["id_cego"]: row for row in _read_csv(path)}
    return out


def merge(records: list, key_rows: list, ratings: dict) -> tuple:
    """Acrescenta as notas humanas aos registros. Devolve (registros, kappas)."""
    by_key = {(r["model"], r["case_id"], r["repetition"]): r for r in records}
    dim_of = {rater: info["dimensao"] for rater, info in RATERS.items()}
    kappas, calibration_scores = {}, defaultdict(dict)
    merged = [dict(r) for r in records]
    index = {(r["model"], r["case_id"], r["repetition"]): r for r in merged}

    for row in key_rows:
        k = (row["model"], row["case_id"], int(row["repetition"]))
        if k not in by_key:
            continue
        record = index[k]
        notes = defaultdict(list)
        for rater, rows in ratings.items():
            line = rows.get(row["id_cego"])
            if line is None:
                continue
            for dim in ("clareza", "correcao", "neutralidade"):
                own = dim == dim_of[rater]
                if not own and row["calibracao"] != "sim":
                    continue
                value = _num(line.get(f"nota_{dim}"))
                if value is not None:
                    notes[dim].append(value)
                    if row["calibracao"] == "sim":
                        calibration_scores[dim].setdefault(rater, {})[row["id_cego"]] = value
        scores = {dim: sum(v) / len(v) for dim, v in notes.items() if v}
        record["notas_dimensao"] = scores
        if len(scores) == 3:
            record["nota"] = sum(scores.values()) / 3
        tech = ratings.get("tecnico", {}).get(row["id_cego"])
        if tech:
            for field, target in (
                ("correcao_factual_ok", "factual_ok"),
                ("limitacoes_ok", "limitacoes_ok"),
                ("nao_concluir_ok", "nao_concluir_ok"),
                ("alucinacao", "alucinacao"),
            ):
                value = _flag(tech.get(field))
                if value is not None:
                    record[target] = value

    for dim, per_rater in calibration_scores.items():
        common = set.intersection(*(set(v) for v in per_rater.values())) if len(per_rater) > 1 else set()
        if len(per_rater) > 1 and common:
            ordered = sorted(common)
            series = {rater: [per_rater[rater][i] for i in ordered] for rater in per_rater}
            kappas[dim] = {f"{a}-{b}": round(v, 3) for (a, b), v in llm_eval.pairwise_kappa(series).items()}
    return merged, kappas


def _fmt(value):
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def build_report(records: list, kappas: dict, cases_by_id: dict, meta: dict) -> str:
    metrics = llm_eval.compute_metrics(records)
    lines = [
        "# Relatório de validação 7A (gerado automaticamente)",
        "",
        f"Prompt {meta.get('prompt_version')} ({meta.get('prompt_fingerprint')}) · {len(records)} respostas · "
        f"{len({r['case_id'] for r in records})} casos.",
        "",
    ]
    if any(r.get("dry_run") for r in records):
        lines += ["> **ATENÇÃO:** há registros de simulação (`--dry-run`). Este relatório NÃO vale como resultado oficial.", ""]
    for model, m in metrics.items():
        lines += [f"## {model}", "", "| Critério | Valor | Limite | Situação |", "|---|---|---|---|"]
        for name, value, limit, status in llm_eval.evaluate_thresholds(m):
            lines.append(f"| {name} | {_fmt(value)} | {limit} | {status} |")
        lines.append("")
    lines += ["## Concordância entre avaliadores (kappa ponderado, calibração)", ""]
    if kappas:
        lines += ["| Dimensão | Par | Kappa | Situação |", "|---|---|---|---|"]
        for dim, pairs in sorted(kappas.items()):
            for pair, value in sorted(pairs.items()):
                lines.append(f"| {dim} | {pair} | {value} | {'ok' if value >= llm_eval.KAPPA_MIN else 'abaixo de 0,60'} |")
    else:
        lines.append("Pendente: sem notas de calibração dos três avaliadores.")
    lines += ["", "## Taxas das verificações automáticas informativas", "",
              "| Modelo | métricas no contexto | números rastreáveis | limitações obrigatórias |", "|---|---|---|---|"]
    for model, m in metrics.items():
        lines.append(f"| {model} | {_fmt(m['auto_metricas_no_contexto'])} | {_fmt(m['auto_valores_rastreaveis'])} | {_fmt(m['auto_limitacoes'])} |")
    lines += ["", "## Respostas que violam critério obrigatório (regra por resposta)", ""]
    failures = llm_eval.response_level_failures(records)
    if failures:
        lines += ["| Modelo | Caso | Repetição | Verificações reprovadas |", "|---|---|---|---|"]
        for model, case, rep, failed in failures:
            lines.append(f"| {model} | {case} | {rep} | {', '.join(failed)} |")
    else:
        lines.append("Nenhuma.")
    lines += ["", "## Respostas que reprovam só verificações informativas", ""]
    others = llm_eval.other_check_failures(records)
    if others:
        lines += ["| Modelo | Caso | Repetição | Verificações reprovadas |", "|---|---|---|---|"]
        for model, case, rep, failed in others:
            lines.append(f"| {model} | {case} | {rep} | {', '.join(failed)} |")
    else:
        lines.append("Nenhuma.")
    weak = [
        (r["model"], r["case_id"], r["repetition"], r["notas_dimensao"])
        for r in records
        if r.get("notas_dimensao") and (min(r["notas_dimensao"].values()) <= 2 or r.get("alucinacao"))
    ]
    lines += ["", "## Respostas com nota ≤ 2 em alguma dimensão ou alucinação apontada", ""]
    if weak:
        lines += ["| Modelo | Caso | Repetição | Notas |", "|---|---|---|---|"]
        lines += [f"| {m} | {c} | {r} | {n} |" for m, c, r, n in weak]
    else:
        lines.append("Nenhuma (ou avaliação humana ainda pendente).")
    lines += ["", "## Nota", "",
              "Aprovar a etapa exige todos os critérios em `ok`, kappa ≥ 0,60 e nenhuma resposta na regra por resposta. "
              "Critérios `pendente` dependem das notas humanas."]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", default="experiments/llm_7a/results/respostas.jsonl")
    parser.add_argument("--cases", default="experiments/llm_7a/cases.json")
    parser.add_argument("--ratings", default="experiments/llm_7a/results/avaliacao")
    parser.add_argument("--out", default="experiments/llm_7a/results/relatorio.md")
    args = parser.parse_args(argv)

    records = [json.loads(x) for x in Path(args.responses).read_text(encoding="utf-8").splitlines() if x.strip()]
    cases_payload = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    cases = {c["id"]: c for c in cases_payload["casos"]}
    ratings_dir = Path(args.ratings)
    ratings = load_ratings(ratings_dir)
    key_path = ratings_dir / "chave_cegamento.csv"
    kappas = {}
    if ratings and key_path.exists():
        records, kappas = merge(records, _read_csv(key_path), ratings)
    report = build_report(records, kappas, cases, cases_payload)
    Path(args.out).write_text(report, encoding="utf-8")
    print(f"Relatório gravado em {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
