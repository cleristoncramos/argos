"""
Gera as planilhas CEGAS para os 3 avaliadores humanos a partir de respostas.jsonl.

- Só entram respostas que passaram na validação automática (as demais nunca
  seriam mostradas ao usuário e são contadas à parte na análise).
- A identidade do modelo fica apenas em chave_cegamento.csv (não entregar).
- ~20% das respostas formam o subconjunto de CALIBRAÇÃO, avaliado pelos três
  em todas as dimensões; nas demais, cada avaliador preenche só a sua.

  python -m experiments.llm_7a.make_rating_sheets
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

RATERS = {
    "leigo": {"dimensao": "clareza", "descricao": "Entendi o que o texto quer dizer?"},
    "tecnico": {"dimensao": "correcao", "descricao": "Os números e conceitos estão corretos?"},
    "neutro": {"dimensao": "neutralidade", "descricao": "O texto evita induzir uma decisão ou prever?"},
}
CALIBRATION_SHARE = 0.20
SEED = 7001


def render_response(raw: str) -> str:
    """Texto legível da resposta JSON (o avaliador não vê JSON)."""
    data = json.loads(raw)
    lines = [
        f"RESUMO: {data['resumo']}",
        f"O QUE O GRÁFICO MOSTRA: {data['o_que_o_grafico_mostra']}",
    ]
    for m in data["metricas_relevantes"]:
        lines.append(f"MÉTRICA {m['id']}: {m['valor']} {m['unidade']} — {m['leitura']}")
    lines += [f"LIMITAÇÃO: {x}" for x in data["limitacoes"]]
    lines += [f"NÃO SE PODE CONCLUIR: {x}" for x in data["o_que_nao_pode_ser_concluido"]]
    lines.append(f"NOTA EDUCATIVA: {data['nota_educativa']}")
    return "\n".join(lines)


def render_context(context: dict) -> str:
    parts = [
        f"Ativo(s): {', '.join(context['assets'])} | Período: {context['filters']['period_start']} a "
        f"{context['filters']['period_end']} | Frequência: {context['filters']['frequency']} | "
        f"Observações: {context['n_observations']}"
    ]
    parts += [f"- {m['label']}: {m['value']} {m['unit']}".rstrip() for m in context["metrics"]]
    parts += [f"Nota: {n}" for n in context["notes"]]
    if context.get("user_request"):
        parts.append(f"Pergunta do usuário: {context['user_request']['text']}")
    return "\n".join(parts)


def select_items(records: list, seed: int = SEED, share: float = CALIBRATION_SHARE) -> list:
    """Respostas válidas e reais, embaralhadas, com id cego e marca de calibração."""
    eligible = [r for r in records if r["validation"]["ok"] and not r.get("dry_run")]
    rng = random.Random(seed)
    rng.shuffle(eligible)
    n_cal = max(1, round(len(eligible) * share)) if eligible else 0
    items = []
    for i, record in enumerate(eligible, start=1):
        items.append({"id_cego": f"R{i:03d}", "calibracao": i <= n_cal, "record": record})
    return items


def build_sheets(records: list, cases_by_id: dict, out_dir: Path, seed: int = SEED) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    items = select_items(records, seed)

    with (out_dir / "chave_cegamento.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter=";")
        writer.writerow(["id_cego", "model", "case_id", "repetition", "calibracao"])
        for it in items:
            r = it["record"]
            writer.writerow([it["id_cego"], r["model"], r["case_id"], r["repetition"], "sim" if it["calibracao"] else "nao"])

    for rater, info in RATERS.items():
        columns = ["id_cego", "calibracao", "caso", "contexto_dado_ao_modelo"]
        if rater == "tecnico":
            columns += ["resposta_esperada", "pontos_obrigatorios", "armadilhas"]
        columns += ["resposta_do_sistema", "nota_clareza", "nota_correcao", "nota_neutralidade"]
        if rater == "tecnico":
            columns += ["correcao_factual_ok", "limitacoes_ok", "nao_concluir_ok", "alucinacao", "comentario"]
        else:
            columns += ["comentario"]
        with (out_dir / f"{rater}.csv").open("w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns, delimiter=";")
            writer.writeheader()
            for it in items:
                r = it["record"]
                case = cases_by_id[r["case_id"]]
                row = {
                    "id_cego": it["id_cego"],
                    "calibracao": "sim" if it["calibracao"] else "nao",
                    "caso": case["titulo"],
                    "contexto_dado_ao_modelo": render_context(case["contexto"]),
                    "resposta_do_sistema": render_response(r["raw"]),
                }
                if rater == "tecnico":
                    row["resposta_esperada"] = case["resposta_esperada"]
                    row["pontos_obrigatorios"] = " | ".join(case["pontos_obrigatorios"])
                    row["armadilhas"] = " | ".join(case["armadilhas"])
                writer.writerow(row)
    return {"respostas": len(items), "calibracao": sum(1 for i in items if i["calibracao"])}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", default="experiments/llm_7a/results/respostas.jsonl")
    parser.add_argument("--cases", default="experiments/llm_7a/cases.json")
    parser.add_argument("--out", default="experiments/llm_7a/results/avaliacao")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args(argv)
    records = [json.loads(x) for x in Path(args.responses).read_text(encoding="utf-8").splitlines() if x.strip()]
    cases = {c["id"]: c for c in json.loads(Path(args.cases).read_text(encoding="utf-8"))["casos"]}
    summary = build_sheets(records, cases, Path(args.out), args.seed)
    print(f"{summary['respostas']} respostas ({summary['calibracao']} de calibração). Entregue só leigo.csv, tecnico.csv e neutro.csv.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
