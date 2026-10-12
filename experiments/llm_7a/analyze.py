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
import math
import sys
from collections import Counter, defaultdict
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


def complementary(key_rows: list, ratings: dict) -> dict:
    """
    Indicadores que complementam o kappa (itens de calibração):
    concordância exata e dentro de 1 ponto por par, e distribuição das notas por avaliador.
    """
    series = defaultdict(lambda: defaultdict(dict))
    for row in key_rows:
        if row["calibracao"] != "sim":
            continue
        for rater, rows in ratings.items():
            line = rows.get(row["id_cego"])
            if line is None:
                continue
            for dim in ("clareza", "correcao", "neutralidade"):
                value = _num(line.get(f"nota_{dim}"))
                if value is not None:
                    series[dim][rater][row["id_cego"]] = value
    pairs, distribution = {}, {}
    for dim, per_rater in series.items():
        distribution[dim] = {rater: dict(sorted(Counter(vals.values()).items())) for rater, vals in sorted(per_rater.items())}
        raters = sorted(per_rater)
        for i, a in enumerate(raters):
            for b in raters[i + 1:]:
                common = sorted(set(per_rater[a]) & set(per_rater[b]))
                if common:
                    exact, within = llm_eval.agreement([per_rater[a][k] for k in common], [per_rater[b][k] for k in common])
                    pairs.setdefault(dim, {})[f"{a}-{b}"] = (exact, within, len(common))
    return {"pares": pairs, "distribuicao": distribution}


def _fmt(value):
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


ALERT_SHARE = 0.95
ALERT_MIN_NOTES = 10


def rater_alerts(ratings: dict) -> list:
    """Por avaliador, quanto as notas variam. Alerta se quase todas forem iguais."""
    out = []
    for rater, rows in sorted(ratings.items()):
        dim = RATERS[rater]["dimensao"]
        values = [v for v in (_num(r.get(f"nota_{dim}")) for r in rows.values()) if v is not None]
        if not values:
            continue
        share = llm_eval.dominant_share(values)
        out.append({
            "avaliador": rater, "dimensao": dim, "n": len(values), "media": sum(values) / len(values),
            "mais_frequente": max(set(values), key=values.count), "parcela": share,
            "alerta": len(values) >= ALERT_MIN_NOTES and share >= ALERT_SHARE,
        })
    return out


def build_report(records: list, kappas: dict, cases_by_id: dict, meta: dict, alerts=None, extra=None) -> str:
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
                if math.isnan(value):
                    status, shown = "indeterminado: sem variação nas notas (não prova concordância)", "n/d"
                else:
                    status, shown = ("ok" if value >= llm_eval.KAPPA_MIN else "abaixo de 0,60"), value
                lines.append(f"| {dim} | {pair} | {shown} | {status} |")
    else:
        lines.append("Pendente: sem notas de calibração dos três avaliadores.")
    if extra and extra.get("pares"):
        lines += ["", "## Concordância complementar (não substitui o kappa)", "",
                  "| Dimensão | Par | Itens | Concordância exata | Dentro de 1 ponto |", "|---|---|---|---|---|"]
        for dim, pairs in sorted(extra["pares"].items()):
            for pair, (exact, within, n) in sorted(pairs.items()):
                lines.append(f"| {dim} | {pair} | {n} | {exact:.0%} | {within:.0%} |")
        lines += ["", "### Distribuição das notas (calibração)", "", "| Dimensão | Avaliador | Distribuição (nota: quantidade) |", "|---|---|---|"]
        for dim, per_rater in sorted(extra["distribuicao"].items()):
            for rater, dist in per_rater.items():
                lines.append(f"| {dim} | {rater} | " + ", ".join(f"{k:g}: {v}" for k, v in dist.items()) + " |")
    if alerts:
        lines += ["", "## Variação das notas humanas (sinal de alerta)", "",
                  "| Avaliador | Dimensão | Notas | Média | Nota mais frequente | Parcela dessa nota | Situação |", "|---|---|---|---|---|---|---|"]
        for a in alerts:
            flag = "ALERTA: quase sem variação" if a["alerta"] else "ok"
            lines.append(f"| {a['avaliador']} | {a['dimensao']} | {a['n']} | {_fmt(a['media'])} | {_fmt(a['mais_frequente'])} | "
                         f"{a['parcela']:.0%} | {flag} |")
        if any(a["alerta"] for a in alerts):
            lines += ["", "> Notas quase todas iguais não demonstram qualidade: a rubrica pode não ter discriminado respostas. "
                          "Rever com os avaliadores antes de usar este resultado."]
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
    kappas, extra = {}, None
    if ratings and key_path.exists():
        key_rows = _read_csv(key_path)
        records, kappas = merge(records, key_rows, ratings)
        extra = complementary(key_rows, ratings)
    report = build_report(records, kappas, cases, cases_payload, rater_alerts(ratings), extra)
    Path(args.out).write_text(report, encoding="utf-8")
    print(f"Relatório gravado em {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
