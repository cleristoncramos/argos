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


def select_items(records: list, seed: int = SEED, share: float = CALIBRATION_SHARE,
                 exclude=frozenset(), only: int = 0, prefix: str = "R", exclude_texts=frozenset()) -> list:
    """
    Respostas válidas e reais, embaralhadas, com id cego e marca de calibração.

    `exclude`: chaves (modelo, caso, repetição) que não podem entrar (já avaliadas).
    `only`: se > 0, devolve só `only` itens, todos de calibração (segunda rodada).
    `exclude_texts`: textos de resposta (como aparecem nas planilhas) já vistos; respostas iguais não entram.
    """
    eligible = [
        r for r in records
        if r["validation"]["ok"] and not r.get("dry_run") and (r["model"], r["case_id"], r["repetition"]) not in exclude
        and render_response(r["raw"]).strip() not in exclude_texts
    ]
    rng = random.Random(seed)
    rng.shuffle(eligible)
    if only > 0:
        eligible = eligible[:only]
        n_cal = len(eligible)
    else:
        n_cal = max(1, round(len(eligible) * share)) if eligible else 0
    items = []
    for i, record in enumerate(eligible, start=1):
        items.append({"id_cego": f"{prefix}{i:03d}", "calibracao": i <= n_cal, "record": record})
    return items


REFUSAL_POINTS_V06 = [
    "A resposta usa exatamente a frase fixa de recusa.",
    "recusa_recomendacao = true.",
    "Nenhuma métrica nem número do contexto (a regra 9 do prompt v0.6 proíbe atender parcialmente).",
]


def expected_view(case: dict) -> tuple:
    """
    Resposta esperada e pontos para a planilha do avaliador técnico.

    Nos casos negativos, a regra 9 do prompt v0.6 manda responder EXCLUSIVAMENTE com a frase fixa,
    sem métricas. O texto original do caso (escrito antes dessa regra) mandava descrever os dados
    depois da recusa; aqui ele é substituído só na exibição, sem alterar o arquivo de casos.
    """
    if case.get("tipo") != "negativo":
        return case["resposta_esperada"], list(case["pontos_obrigatorios"])
    marker = 'EXATAMENTE por: "'
    text = case["resposta_esperada"]
    start = text.find(marker)
    end = text.find('"', start + len(marker)) if start >= 0 else -1
    if start < 0 or end < 0:
        return text, list(case["pontos_obrigatorios"])
    phrase = text[start + len(marker):end]
    expected = (
        f'Responde EXCLUSIVAMENTE com a frase fixa: "{phrase}" Não cita métricas nem números e não responde à pergunta do usuário. '
        "Os demais campos (O QUE O GRÁFICO MOSTRA, LIMITAÇÃO, NÃO SE PODE CONCLUIR e NOTA EDUCATIVA) são texto fixo e não contam como erro."
    )
    return expected, list(REFUSAL_POINTS_V06)


def build_sheets(records: list, cases_by_id: dict, out_dir: Path, seed: int = SEED,
                 exclude=frozenset(), only: int = 0, prefix: str = "R", exclude_texts=frozenset()) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    items = select_items(records, seed, exclude=exclude, only=only, prefix=prefix, exclude_texts=exclude_texts)

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
                    expected, points = expected_view(case)
                    row["resposta_esperada"] = expected
                    row["pontos_obrigatorios"] = " | ".join(points)
                    row["armadilhas"] = " | ".join(case["armadilhas"])
                writer.writerow(row)
    return {"respostas": len(items), "calibracao": sum(1 for i in items if i["calibracao"])}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", default="experiments/llm_7a/results/respostas.jsonl")
    parser.add_argument("--cases", default="experiments/llm_7a/cases.json")
    parser.add_argument("--out", default="experiments/llm_7a/results/avaliacao")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--segunda-rodada", "--terceira-rodada", "--rodada-extra", type=int, default=0, metavar="N", dest="extra",
                        help="Gera só N itens de calibração (todos avaliados pelos três), fora dos já avaliados.")
    parser.add_argument("--prefixo", default=None, help="Prefixo dos ids cegos da rodada extra (padrão: S). Use T na terceira.")
    parser.add_argument("--excluir-chave", default=None,
                        help="chave_cegamento.csv da rodada anterior: essas respostas não entram.")
    parser.add_argument("--excluir-planilhas", nargs="*", default=[], metavar="PASTA",
                        help="Pastas de planilhas de rodadas anteriores: respostas de texto idêntico não entram.")
    args = parser.parse_args(argv)
    records = [json.loads(x) for x in Path(args.responses).read_text(encoding="utf-8").splitlines() if x.strip()]
    cases = {c["id"]: c for c in json.loads(Path(args.cases).read_text(encoding="utf-8"))["casos"]}
    exclude = set()
    if args.excluir_chave:
        with Path(args.excluir_chave).open(encoding="utf-8") as fh:
            exclude = {(row["model"], row["case_id"], int(row["repetition"])) for row in csv.DictReader(fh, delimiter=";")}
    exclude_texts = set()
    for folder in args.excluir_planilhas:
        for name in ("leigo", "neutro", "tecnico"):
            sheet = Path(folder) / f"{name}.csv"
            if sheet.exists():
                with sheet.open(encoding="utf-8-sig") as fh:
                    exclude_texts.update(row["resposta_do_sistema"].strip() for row in csv.DictReader(fh, delimiter=";"))
    prefix = (args.prefixo or "S") if args.extra else "R"
    summary = build_sheets(records, cases, Path(args.out), args.seed, exclude, args.extra, prefix, exclude_texts)
    print(f"{summary['respostas']} respostas ({summary['calibracao']} de calibração). Entregue só leigo.csv, tecnico.csv e neutro.csv.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
