"""
Rodada de avaliação da fase 1 com o provedor xAI (etapa 6 da DL2, DL2-I).

Chama o modelo nos 33 casos chamáveis do conjunto congelado (28 casos, o adversarial A01 e os
quatro controles), duas vezes cada, porque o provedor não documenta seed: 66 chamadas. O
template congelado é a referência; o Grok é a fonte experimental. Nada vai para a interface.

Antes de qualquer chamada, o script confere:
- o hash do conjunto congelado (fase1-v2) e os do template;
- os quatro hashes aprovados do protocolo (prompt, esquema, impressão e textos fixos);
- a chave em XAI_API_KEY (nunca impressa nem gravada).

Cada chamada passa por `explain_experimental` (política, validação das 17 verificações e a única
regeneração permitida) e pelo contador de custo, que recusa antes de passar de US$ 16 ou de 200
chamadas. As respostas brutas ficam em `resultados/` (fora do git), para a avaliação cega; o
registro guarda modelo pedido, versão devolvida, tokens, custo e situação de cada chamada.

Uso, a partir da raiz:
    python -m experiments.llm_v1_exp.rodada --plano                       # só lista, sem chamar
    python -m experiments.llm_v1_exp.rodada --casos S01,G01,M01 --execucoes 1   # aquecimento
    python -m experiments.llm_v1_exp.rodada                               # rodada: 33 x 2
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from core import llm_exp_context as ec
from core import llm_exp_policy as policy
from core import llm_provider as lp
from core.assets import ASSETS
from core.llm_exp_service import APPROVED_HASHES, current_hashes, explain_experimental
from core.llm_service import MODE_LIVE, UsageLimiter
from experiments.llm_v1_exp import adversariais, conjunto

PASTA = Path(__file__).resolve().parent / "resultados"
EXECUCOES = lp.RUNS_WITHOUT_SEED


class RodadaRecusada(Exception):
    """Alguma conferência anterior à primeira chamada falhou."""


def carregar_conjunto(arquivo: Path = conjunto.ARQUIVO) -> dict:
    if conjunto.sha256_arquivo(arquivo) != conjunto.HASH_CONGELADO:
        raise RodadaRecusada("O conjunto de casos não confere com o hash congelado (fase1-v2).")
    return json.loads(Path(arquivo).read_text(encoding="utf-8"))


def conferir_protocolo() -> None:
    if current_hashes() != APPROVED_HASHES:
        raise RodadaRecusada("Os hashes do protocolo não conferem com os aprovados.")
    adversariais.respostas_congeladas()      # levanta ValueError se o template não conferir


def contexto_a01(base: dict, regra: dict) -> dict:
    """A01: contexto de S01 com a estimativa fornecida e a política sem modelo autorizado."""
    contexto = copy.deepcopy(base)
    ativo = contexto["asset"]["ticker"] if isinstance(contexto["asset"], dict) else contexto["asset"]
    contexto["estimate"] = ec._estimate_block(regra["estimativa_fornecida"], ativo, policy.ENV_EXPERIMENTAL, None)
    return contexto


def plano(dados: dict) -> list[tuple[str, dict]]:
    """Os 33 casos chamáveis, na ordem do conjunto: 28 casos, A01 e os quatro controles."""
    por_id = {c["id"]: c["contexto"] for c in dados["casos"]}
    itens = [(c["id"], c["contexto"]) for c in dados["casos"]]
    a01 = next(a for a in dados["adversariais"] if a["id"] == "A01")
    itens.append(("A01", contexto_a01(por_id[a01["base"]], a01)))
    itens += [(r["id"], por_id[r["repete"]]) for r in dados["controles"]]
    return itens


def executar(
    itens: list[tuple[str, dict]],
    execucoes: int,
    chave: str,
    ledger: lp.BudgetLedger,
    saida: Path,
    transport: Callable = lp.http_transport,
    provider: lp.Provider = lp.XAI,
    agora: Callable = lambda: datetime.now(timezone.utc),
) -> list[dict]:
    """Uma linha por chamada em `saida` (JSONL): caso, execução, situação, versão, tokens e resposta."""
    conhecidos = [a["ticker"] for a in ASSETS]
    limiter = UsageLimiter(max_calls=lp.MAX_CALLS, max_cost_usd=lp.BUDGET_CAP_USD)
    linhas = []
    saida.parent.mkdir(parents=True, exist_ok=True)
    for execucao in range(1, execucoes + 1):
        for caso, contexto in itens:
            capturado: dict = {}

            def gravando(prov, corpo, key, timeout, _cap=capturado):
                resposta = transport(prov, corpo, key, timeout)
                _cap["raw"] = lp.parse_response(resposta)["raw"]   # a última tentativa válida
                return resposta

            resultado = explain_experimental(
                contexto, mode=MODE_LIVE, api_key=chave, transport=gravando, known_tickers=conhecidos,
                limiter=limiter, evaluation_run=True, provider=provider, ledger=ledger,
                case_id=f"{caso}#{execucao}", now=agora)
            log = resultado.log
            chamadas = log.get("calls", [])
            linha = {
                "caso": caso,
                "execucao": execucao,
                "status": resultado.status,
                "motivo": resultado.reason,
                "verificacoes_reprovadas": log.get("failed_checks", []),
                "regeneracoes": log.get("regenerations", 0),
                "modelo_pedido": provider.model,
                "versoes_devolvidas": sorted({c.get("model_version", "") for c in chamadas if c.get("model_version")}),
                "tokens_entrada": log.get("input_tokens", 0),
                "tokens_saida": log.get("output_tokens", 0),
                "custo_usd": log.get("cost_usd", 0.0),
                "resposta_sha256": log.get("response_sha256"),
                "resposta": capturado.get("raw"),
                "horario": log.get("timestamp"),
            }
            linhas.append(linha)
            with saida.open("a", encoding="utf-8") as arquivo:
                arquivo.write(json.dumps(linha, ensure_ascii=False) + "\n")
            if resultado.reason.startswith("teto_da_rodada"):
                return linhas
    return linhas


def resumo(linhas: list[dict], ledger: lp.BudgetLedger) -> str:
    from collections import Counter
    situacoes = Counter(f"{l['status']}:{l['motivo'].split(':')[0]}" for l in linhas)
    versoes = sorted({v for l in linhas for v in l["versoes_devolvidas"]})
    return (f"chamadas registradas: {len(ledger.entries())} | gasto: US$ {ledger.spent():.4f} | "
            f"situações: {dict(situacoes)} | versões devolvidas: {versoes}")


def main(argv: Optional[list] = None) -> int:
    args = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    args.add_argument("--casos", help="lista de casos (ex.: S01,G01,M01); padrão: os 33")
    args.add_argument("--execucoes", type=int, default=EXECUCOES)
    args.add_argument("--plano", action="store_true", help="só mostra o plano, sem chamar")
    args.add_argument("--rotulo", default="rodada", help="nome do arquivo de saída em resultados/")
    opts = args.parse_args(argv)

    try:
        dados = carregar_conjunto()
        conferir_protocolo()
    except (RodadaRecusada, ValueError) as erro:
        print(f"Rodada recusada: {erro}")
        return 2
    itens = plano(dados)
    if opts.casos:
        pedidos = [c.strip() for c in opts.casos.split(",") if c.strip()]
        faltam = [c for c in pedidos if c not in {i for i, _ in itens}]
        if faltam:
            print(f"Casos fora do plano: {faltam}")
            return 2
        itens = [i for i in itens if i[0] in pedidos]
    total = len(itens) * opts.execucoes
    print(f"Plano: {len(itens)} casos x {opts.execucoes} execuções = {total} chamadas ({lp.XAI.model}).")
    if opts.plano:
        print(", ".join(i for i, _ in itens))
        return 0
    chave = lp.api_key()
    if not chave:
        print("Rodada recusada: XAI_API_KEY ausente.")
        return 2
    ledger = lp.BudgetLedger(lp.LEDGER_FILE)
    saida = PASTA / f"{opts.rotulo}_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.jsonl"
    linhas = executar(itens, opts.execucoes, chave, ledger, saida)
    del chave
    print(resumo(linhas, ledger))
    print(f"Respostas: {saida}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
