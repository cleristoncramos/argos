"""
Ponto de entrada do piloto. Uso, a partir da raiz do repositório:

    python -m experiments.preditivo.executar coletar        # coleta e congela um snapshot (uma vez)
    python -m experiments.preditivo.executar listar-datas   # lista de datas elegíveis do período final
    python -m experiments.preditivo.executar desenvolver    # 8 dobras de 2014 a 2021, sem ler o período final
    python -m experiments.preditivo.executar final --confirmo-abertura   # travado até a seção 12 do protocolo

O desenvolvimento usa apenas preços anteriores à primeira data do período final
(o 21º pregão de 2022): o período final não é lido.
"""

from __future__ import annotations

import argparse
import json
import sys

import pandas as pd

from core.clock import now_brasilia
from experiments.preditivo import config
from experiments.preditivo.abertura import DATAS_ELEGIVEIS, verificar_abertura
from experiments.preditivo.amostras import construir_amostras, realizadas_ate, validar_precos
from experiments.preditivo.avaliacao import prever_anos
from experiments.preditivo.dados import carregar, coletar_e_congelar
from experiments.preditivo.divisoes import primeira_data_avaliada
from experiments.preditivo.elegibilidade import avaliar
from experiments.preditivo.estatistica import (
    acuracia_balanceada,
    alinhar,
    clark_west,
    diebold_mariano,
    erros,
    r2_fora_da_amostra,
)
from experiments.preditivo.estrategia import backtest, datas_de_decisao
from experiments.preditivo.registro import registrar
from experiments.preditivo.util import sha256

RESULTADOS = config.RAIZ / "resultados"


def primeira_data_final(precos: pd.DataFrame) -> pd.Timestamp:
    return primeira_data_avaliada(precos["Date"], config.ANOS_FINAIS[0], config.EMBARGO)


def resumo_previsoes(previsoes: pd.DataFrame) -> dict:
    realizadas = previsoes.dropna(subset=["y"])
    y = realizadas["y"].to_numpy(dtype=float)
    decisoes = datas_de_decisao(previsoes).dropna(subset=["y"])
    return {
        "n": int(len(realizadas)),
        "r2_fora_da_amostra": r2_fora_da_amostra(y, realizadas["yhat"].to_numpy(dtype=float)),
        "ridge": erros(y, realizadas["yhat"]),
        "retorno_zero": erros(y, realizadas["yhat_zero"]),
        "media_historica": erros(y, realizadas["yhat_media"]),
        "acuracia_balanceada_nas_decisoes": acuracia_balanceada(decisoes["y"], decisoes["yhat"]),
    }


def desenvolver_ativo(ativo: str, precos: pd.DataFrame) -> tuple[pd.DataFrame, list[dict], list[dict]]:
    """Oito dobras anuais (2014 a 2021) só com preços anteriores à primeira data do período final."""
    precos = validar_precos(precos)
    limite = primeira_data_final(precos)
    passado = precos[precos["Date"] < limite].reset_index(drop=True)
    amostras = construir_amostras(passado)
    embargos = {ano: config.EMBARGO for ano in config.ANOS_DESENVOLVIMENTO}
    previsoes, ajustes = prever_anos(amostras, passado["Date"], config.ANOS_DESENVOLVIMENTO, embargos, ativo)
    dobras = []
    for ano in config.ANOS_DESENVOLVIMENTO:
        bloco = previsoes[previsoes["ano_ajuste"] == ano]
        dobras.append({"ano": ano, **resumo_previsoes(bloco)})
    return previsoes, ajustes, dobras


def comando_coletar(args) -> int:
    manifesto = coletar_e_congelar(motivo_nova_tentativa=args.nova_tentativa)
    verificacoes = {chave: manifesto[chave] for chave in (
        "triagem_retorno_preco_vs_ajustado_por_proventos", "desdobramentos_na_fonte",
        "verificacao_ohlc", "variacoes_do_fator_sem_evento")}
    registrar("coleta", {"snapshot": manifesto["snapshot"], "situacao": manifesto["situacao"],
                         "arquivos": manifesto["arquivos"], "conferencia_das_series": manifesto["conferencia_das_series"],
                         **verificacoes})
    print(f"Snapshot {manifesto['snapshot']} congelado em {config.DADOS / manifesto['snapshot']}.")
    print(f"  situação: {manifesto['situacao']}")
    for nome, serie in manifesto["conferencia_das_series"].items():
        print(f"  {nome}: {serie['linhas']} linhas, {serie['inicio']} a {serie['fim']}, "
              f"repetidas {len(serie['datas_repetidas'])}, não finitos {serie['valores_nao_finitos']}, "
              f"sha256 {manifesto['arquivos'][nome]['sha256'][:16]}…")
    for ativo in manifesto["parametros"]["ativos"]:
        print(f"  {ativo}: "
              f"{len(verificacoes['triagem_retorno_preco_vs_ajustado_por_proventos'][ativo])} datas na triagem de proventos; "
              f"{len(verificacoes['desdobramentos_na_fonte'][ativo])} desdobramentos; "
              f"{len(verificacoes['verificacao_ohlc'][ativo]['ocorrencias'])} ocorrências OHLC; "
              f"{len(verificacoes['variacoes_do_fator_sem_evento'][ativo])} variações do fator sem evento "
              "(investigar e documentar)")
    return 0


def comando_listar_datas(_args) -> int:
    """N1: lista fixada pelo calendário, horizonte e disponibilidade do alvo, sem consultar erros."""
    if DATAS_ELEGIVEIS.exists():
        print(f"A lista já existe em {DATAS_ELEGIVEIS}; não é refeita.")
        return 1
    _manifesto, precos, _cdi = carregar()
    corte = pd.Timestamp(config.DATA_CORTE)
    lista = {}
    for ativo, serie in precos.items():
        serie = validar_precos(serie)
        amostras = construir_amostras(serie)
        primeira = primeira_data_final(serie)
        elegiveis = amostras[(amostras["decision_date"] >= primeira) & realizadas_ate(amostras, corte)]
        lista[ativo] = [d.date().isoformat() for d in elegiveis["decision_date"]]
    DATAS_ELEGIVEIS.write_text(json.dumps(lista, ensure_ascii=False, indent=2), encoding="utf-8")
    registrar("lista_datas_elegiveis", {"sha256": sha256(DATAS_ELEGIVEIS),
                                         "quantidade": {a: len(d) for a, d in lista.items()}})
    print({a: len(d) for a, d in lista.items()})
    return 0


def comando_desenvolver(_args) -> int:
    _manifesto, precos, _cdi = carregar()
    RESULTADOS.mkdir(exist_ok=True)
    resumo = {}
    for ativo, serie in precos.items():
        previsoes, ajustes, dobras = desenvolver_ativo(ativo, serie)
        previsoes.to_csv(RESULTADOS / f"desenvolvimento_{ativo.replace('.', '_')}.csv", index=False)
        frequencia = {str(a): sum(1 for x in ajustes if x["alpha"] == a) for a in config.ALPHAS}
        resumo[ativo] = {"ajustes": ajustes, "dobras": dobras, "frequencia_alpha": frequencia,
                         "dobras_com_r2_positivo": sum(1 for d in dobras if (d["r2_fora_da_amostra"] or 0) > 0)}
        registrar("desenvolvimento", {"ativo": ativo, **resumo[ativo]})
    (RESULTADOS / "desenvolvimento_resumo.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    for ativo, dados in resumo.items():
        linhas = ", ".join(f"{d['ano']}: {d['r2_fora_da_amostra']:+.4f}" for d in dados["dobras"]
                           if d["r2_fora_da_amostra"] is not None)
        print(f"{ativo} — R² fora da amostra por dobra: {linhas}")
        print(f"  frequência de seleção do alpha: {dados['frequencia_alpha']}")
    return 0


def embargos_periodo_final(anos=config.ANOS_FINAIS) -> dict:
    """
    Embargo na fronteira do bloco de avaliação (início de 2022). Nas reestimações
    anuais dentro do bloco já iniciado não há nova interrupção das previsões; o
    treino usa só alvos realizados na data do ajuste (expurgo).
    """
    return {ano: (config.EMBARGO if ano == anos[0] or config.EMBARGO_NAS_REESTIMACOES_FINAIS else 0)
            for ano in anos}


def avaliar_final_ativo(ativo: str, precos: pd.DataFrame, cdi: pd.DataFrame, elegiveis: list[str]) -> dict:
    precos = validar_precos(precos)
    amostras = construir_amostras(precos)
    embargos = embargos_periodo_final()
    previsoes, ajustes = prever_anos(amostras, precos["Date"], config.ANOS_FINAIS, embargos, ativo)
    previsoes.to_csv(RESULTADOS / f"final_{ativo.replace('.', '_')}.csv", index=False)

    datas = pd.to_datetime(elegiveis)
    amostra_teste = previsoes[previsoes["decision_date"].isin(datas)]
    teste_dm = diebold_mariano(amostra_teste, datas)
    diagnostico_cw = clark_west(amostra_teste, datas)
    # O R² usa a mesma amostra do teste; com previsão ausente ou desalinhada, é não calculável.
    alinhado, falha = alinhar(amostra_teste, datas)
    r2 = None if falha else r2_fora_da_amostra(alinhado["y"], alinhado["yhat"])

    decisoes = datas_de_decisao(previsoes)
    custos = sorted(set(config.CUSTOS_SENSIBILIDADE) | {config.CUSTO_LADO_BASE, config.CUSTO_LADO_DOBRO})
    backtests = {c: backtest(precos, cdi, decisoes, c, config.DATA_CORTE) for c in custos}
    _p, _a, dobras = desenvolver_ativo(ativo, precos)
    decisao = avaliar(r2, teste_dm, [d["r2_fora_da_amostra"] for d in dobras],
                      backtests[config.CUSTO_LADO_BASE], backtests[config.CUSTO_LADO_DOBRO])
    realizadas_decisao = decisoes.dropna(subset=["y"])
    return {
        "ativo": ativo,
        "descricao": config.DESCRICAO_RESULTADO,
        "ajustes": ajustes,
        "r2_fora_da_amostra": r2,
        "diebold_mariano": teste_dm.como_dict(),
        "clark_west_diagnostico": diagnostico_cw.como_dict(),
        "erros": {"ridge": erros(amostra_teste["y"], amostra_teste["yhat"]),
                  "retorno_zero": erros(amostra_teste["y"], amostra_teste["yhat_zero"]),
                  "media_historica": erros(amostra_teste["y"], amostra_teste["yhat_media"])},
        "acuracia_balanceada_nas_decisoes": acuracia_balanceada(realizadas_decisao["y"], realizadas_decisao["yhat"]),
        "estrategias_por_custo_lado": {str(c): {k: v.como_dict() for k, v in r.items()} for c, r in backtests.items()},
        "dobras_desenvolvimento": dobras,
        "elegibilidade": decisao,
    }


def comando_final(args) -> int:
    verificar_abertura(args.confirmo_abertura)
    _manifesto, precos, cdi = carregar()
    elegiveis = json.loads(DATAS_ELEGIVEIS.read_text(encoding="utf-8"))
    RESULTADOS.mkdir(exist_ok=True)
    config.MARCA_FINAL_USADO.write_text(json.dumps({"aberta_em": now_brasilia().isoformat(timespec="seconds")}),
                                        encoding="utf-8")
    resultados = {ativo: avaliar_final_ativo(ativo, serie, cdi, elegiveis[ativo]) for ativo, serie in precos.items()}
    (RESULTADOS / "final_resultados.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    registrar("avaliacao_final", resultados, avaliacao_final=True)
    for ativo, r in resultados.items():
        print(f"{ativo}: {r['elegibilidade']['mensagem']}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Piloto preditivo do Argos (experimento local).")
    sub = parser.add_subparsers(dest="comando", required=True)
    coletar = sub.add_parser("coletar")
    coletar.add_argument("--nova-tentativa", metavar="MOTIVO", default=None,
                         help="motivo de uma nova coleta (a anterior é preservada)")
    coletar.set_defaults(funcao=comando_coletar)
    sub.add_parser("listar-datas").set_defaults(funcao=comando_listar_datas)
    sub.add_parser("desenvolver").set_defaults(funcao=comando_desenvolver)
    final = sub.add_parser("final")
    final.add_argument("--confirmo-abertura", action="store_true")
    final.set_defaults(funcao=comando_final)
    args = parser.parse_args(argv)
    return args.funcao(args)


if __name__ == "__main__":
    sys.exit(main())
