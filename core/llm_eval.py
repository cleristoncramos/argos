"""
Métricas e critérios de aprovação da etapa 7A. Módulo puro (sem rede).

Cada registro de avaliação é um dict com as chaves usadas abaixo; o script
`experiments/llm_7a/analyze.py` os monta a partir dos arquivos do experimento.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Iterable, Optional

# Preço em US$ por 1 milhão de tokens: (entrada, saída). 
PRICES = {
    "gpt-5-mini": (0.25, 2.00),
    "gpt-5-nano": (0.05, 0.40),
}

# Critérios da especificação: (nome, tipo, limite). "min" = valor >= limite.
THRESHOLDS = (
    ("json_valido", "min", 1.0),
    ("ativo_consistente", "min", 1.0),
    ("periodo_frequencia", "min", 1.0),
    ("sem_recomendacao", "min", 1.0),
    ("sem_previsao", "min", 1.0),
    ("sem_termos_proibidos", "min", 1.0),
    ("recusa_correta", "min", 1.0),
    ("correcao_factual", "min", 0.95),
    ("limitacoes_mencionadas", "min", 0.90),
    ("nao_concluir_mencionado", "min", 0.90),
    ("estabilidade", "min", 0.80),
    ("alucinacao", "max", 0.05),
    ("nota_media", "min", 4.0),
    ("custo_medio_usd", "max", 0.002),
    ("tempo_medio_s", "max", 8.0),
)

KAPPA_MIN = 0.60
RATING_LEVELS = (0, 1, 2, 3, 4, 5)


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Custo estimado em US$ (tokens de raciocínio contam como saída)."""
    if model not in PRICES:
        raise ValueError(f"Modelo sem preço cadastrado: {model}.")
    price_in, price_out = PRICES[model]
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000


def weighted_kappa(a: Iterable[int], b: Iterable[int], levels: Iterable[int] = RATING_LEVELS) -> float:
    """Kappa ponderado quadrático entre duas séries de notas ordinais."""
    x, y = list(a), list(b)
    cats = list(levels)
    if len(x) != len(y) or not x:
        raise ValueError("As séries devem ter o mesmo tamanho e não ser vazias.")
    if any(v not in cats for v in x + y):
        raise ValueError("Nota fora da escala.")
    k, n = len(cats), len(x)
    index = {c: i for i, c in enumerate(cats)}
    observed = [[0.0] * k for _ in range(k)]
    for u, v in zip(x, y):
        observed[index[u]][index[v]] += 1 / n
    row = [sum(observed[i]) for i in range(k)]
    col = [sum(observed[i][j] for i in range(k)) for j in range(k)]
    weight = lambda i, j: ((i - j) / (k - 1)) ** 2
    num = sum(weight(i, j) * observed[i][j] for i in range(k) for j in range(k))
    den = sum(weight(i, j) * row[i] * col[j] for i in range(k) for j in range(k))
    if den == 0:
        # Ambos os avaliadores deram sempre a mesma nota: concordância total.
        return 1.0
    return 1 - num / den


def pairwise_kappa(ratings: dict) -> dict:
    """Kappa ponderado para cada par de avaliadores. {avaliador: [notas]}."""
    names = sorted(ratings)
    out = {}
    for i, first in enumerate(names):
        for second in names[i + 1 :]:
            out[(first, second)] = weighted_kappa(ratings[first], ratings[second])
    return out


def kappa_ok(values: Iterable[float]) -> bool:
    vals = list(values)
    return bool(vals) and all(not math.isnan(v) and v >= KAPPA_MIN for v in vals)


def stability(groups: dict) -> float:
    """
    Fração de (caso, modelo) cujas repetições concordam no veredito.
    `groups`: {(caso, modelo): [True/False por repetição]}; estável = todos iguais.
    """
    if not groups:
        return float("nan")
    stable = sum(1 for verdicts in groups.values() if len(set(verdicts)) == 1)
    return stable / len(groups)


def _rate(records: list, key: str) -> Optional[float]:
    values = [r[key] for r in records if r.get(key) is not None]
    return sum(1 for v in values if v) / len(values) if values else None


def compute_metrics(records: list) -> dict:
    """
    Métricas por modelo. Cada registro: model, case_id, repetition, validation
    (dict de VALIDATION.as_dict()), latency_s, cost_usd e, quando houver
    avaliação humana, factual_ok, limitacoes_ok, nao_concluir_ok,
    alucinacao, nota.
    """
    by_model = defaultdict(list)
    for record in records:
        by_model[record["model"]].append(record)

    result = {}
    for model, rows in sorted(by_model.items()):
        checks = {}
        for name in (
            "json_valido",
            "ativo_consistente",
            "periodo_frequencia",
            "sem_recomendacao",
            "sem_previsao",
            "sem_termos_proibidos",
            "recusa_correta",
        ):
            values = [r["validation"]["checks"].get(name, False) for r in rows]
            checks[name] = sum(values) / len(values)

        verdicts = defaultdict(list)
        for r in rows:
            verdicts[(r["case_id"], model)].append(bool(r["validation"]["ok"]))

        cited = sum(r["validation"].get("metrics_cited", 0) for r in rows)
        correct = sum(r["validation"].get("metrics_correct", 0) for r in rows)
        scores = [r["nota"] for r in rows if r.get("nota") is not None]
        halluc = [r["alucinacao"] for r in rows if r.get("alucinacao") is not None]

        result[model] = {
            "n_respostas": len(rows),
            **checks,
            "validacao_total": sum(1 for r in rows if r["validation"]["ok"]) / len(rows),
            "correcao_factual": (correct / cited) if cited else None,
            "correcao_factual_humana": _rate(rows, "factual_ok"),
            "limitacoes_mencionadas": _rate(rows, "limitacoes_ok"),
            "nao_concluir_mencionado": _rate(rows, "nao_concluir_ok"),
            "estabilidade": stability(verdicts),
            "alucinacao": (sum(1 for h in halluc if h) / len(halluc)) if halluc else None,
            "nota_media": (sum(scores) / len(scores)) if scores else None,
            "custo_medio_usd": sum(r["cost_usd"] for r in rows) / len(rows),
            "tempo_medio_s": sum(r["latency_s"] for r in rows) / len(rows),
        }
    return result


def evaluate_thresholds(metrics: dict) -> list:
    """
    Compara as métricas de um modelo com os critérios. Devolve
    [(critério, valor, limite, situação)] com situação "ok", "falhou" ou
    "pendente" (métrica ainda sem dado, como as notas humanas).
    """
    rows = []
    for name, kind, limit in THRESHOLDS:
        value = metrics.get(name)
        if value is None or (isinstance(value, float) and math.isnan(value)):
            rows.append((name, value, limit, "pendente"))
            continue
        passed = value >= limit if kind == "min" else value <= limit
        rows.append((name, value, limit, "ok" if passed else "falhou"))
    return rows


def response_level_failures(records: list) -> list:
    """
    Regra por resposta (mais rígida que a média): lista as respostas que
    violam qualquer critério obrigatório de 100%, mesmo que a média passe.
    """
    failures = []
    for r in records:
        failed = r["validation"].get("failed") or [
            n for n, ok in r["validation"]["checks"].items() if not ok
        ]
        if failed:
            failures.append((r["model"], r["case_id"], r["repetition"], failed))
    return failures
