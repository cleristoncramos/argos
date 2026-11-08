"""
Ponto de entrada do piloto. Uso, a partir da raiz do repositório:

    python -m experiments.preditivo.executar coletar        # coleta e congela um snapshot (uma vez)
    python -m experiments.preditivo.executar listar-datas   # lista de datas elegíveis do período final
    python -m experiments.preditivo.executar desenvolver    # 8 dobras de 2014 a 2021, sem usar o período final
    python -m experiments.preditivo.executar final --confirmo-abertura   # travado até a seção 12 do protocolo

O desenvolvimento treina, seleciona e avalia só com dados anteriores à primeira data do
período final (o 21º pregão de 2022): o arquivo é carregado inteiro e truncado antes dela.

v1 encerrada (decisão D1): com encerramento_v1.json presente, coletar, listar-datas,
desenvolver (oficial) e final são recusados; qualidade e desenvolver --ensaio seguem disponíveis.
"""

from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import pandas as pd

from core.clock import now_brasilia
from experiments.preditivo import config
from experiments.preditivo.abertura import DATAS_ELEGIVEIS, exigir_versao_aberta, verificar_abertura
from experiments.preditivo.amostras import construir_amostras, realizadas_ate, validar_precos
from experiments.preditivo.avaliacao import prever_anos
from experiments.preditivo.dados import carregar, carregar_brutos, coletar_e_congelar
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
from experiments.preditivo.qualidade import carregar_politica, entradas_do_ativo, exigir_decidida, serie_derivada
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


def desenvolver_ativo(ativo: str, precos: pd.DataFrame, politica: list | None = None,
                      bruto: pd.DataFrame | None = None) -> tuple[pd.DataFrame, list[dict], list[dict]]:
    """Oito dobras anuais (2014 a 2021) só com preços anteriores à primeira data do período final."""
    precos = validar_precos(precos)
    limite = primeira_data_final(precos)
    passado = precos[precos["Date"] < limite].reset_index(drop=True)
    amostras = construir_amostras(passado, politica=politica, bruto=bruto)
    embargos = {ano: config.EMBARGO for ano in config.ANOS_DESENVOLVIMENTO}
    previsoes, ajustes = prever_anos(amostras, passado["Date"], config.ANOS_DESENVOLVIMENTO, embargos, ativo)
    dobras = []
    for ano in config.ANOS_DESENVOLVIMENTO:
        bloco = previsoes[previsoes["ano_ajuste"] == ano]
        dobras.append({"ano": ano, **resumo_previsoes(bloco)})
    return previsoes, ajustes, dobras


def comando_coletar(args) -> int:
    exigir_versao_aberta()
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
    exigir_versao_aberta()
    if DATAS_ELEGIVEIS.exists():
        print(f"A lista já existe em {DATAS_ELEGIVEIS}; não é refeita.")
        return 1
    _manifesto, precos, _cdi = carregar()
    politica = carregar_politica()
    exigir_decidida(politica)
    brutos = carregar_brutos()
    corte = pd.Timestamp(config.DATA_CORTE)
    lista = {}
    for ativo, serie in precos.items():
        serie = validar_precos(serie)
        amostras = construir_amostras(serie, politica=entradas_do_ativo(politica, ativo), bruto=brutos[ativo])
        primeira = primeira_data_final(serie)
        elegiveis = amostras[(amostras["decision_date"] >= primeira) & realizadas_ate(amostras, corte)
                             & amostras["y"].notna()]
        lista[ativo] = [d.date().isoformat() for d in elegiveis["decision_date"]]
    DATAS_ELEGIVEIS.write_text(json.dumps(lista, ensure_ascii=False, indent=2), encoding="utf-8")
    registrar("lista_datas_elegiveis", {"sha256": sha256(DATAS_ELEGIVEIS),
                                         "quantidade": {a: len(d) for a, d in lista.items()}})
    print({a: len(d) for a, d in lista.items()})
    return 0


def comando_desenvolver(args) -> int:
    """Rodada oficial: exige a política de qualidade decidida. `--ensaio` roda sem essa exigência e é registrado como ensaio."""
    _manifesto, precos, _cdi = carregar()
    politica = carregar_politica()
    if not args.ensaio:
        exigir_versao_aberta()
        exigir_decidida(politica)
    brutos = carregar_brutos()
    evento = "desenvolvimento_ensaio" if args.ensaio else "desenvolvimento"
    RESULTADOS.mkdir(exist_ok=True)
    resumo = {}
    for ativo, serie in precos.items():
        entradas = [e for e in entradas_do_ativo(politica, ativo) if e.get("tratamento")]
        previsoes, ajustes, dobras = desenvolver_ativo(ativo, serie, entradas, brutos[ativo])
        previsoes.to_csv(RESULTADOS / f"{evento}_{ativo.replace('.', '_')}.csv", index=False)
        frequencia = {str(a): sum(1 for x in ajustes if x["alpha"] == a) for a in config.ALPHAS}
        resumo[ativo] = {"ajustes": ajustes, "dobras": dobras, "frequencia_alpha": frequencia,
                         "dobras_com_r2_positivo": sum(1 for d in dobras if (d["r2_fora_da_amostra"] or 0) > 0)}
        registrar(evento, {"ativo": ativo, "politica": entradas, **resumo[ativo]})
    (RESULTADOS / f"{evento}_resumo.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    for ativo, dados in resumo.items():
        linhas = ", ".join(f"{d['ano']}: {d['r2_fora_da_amostra']:+.4f}" for d in dados["dobras"]
                           if d["r2_fora_da_amostra"] is not None)
        print(f"{ativo} — R² fora da amostra por dobra: {linhas}")
        print(f"  frequência de seleção do alpha: {dados['frequencia_alpha']}")
    return 0


def impacto_politica(precos: pd.DataFrame, entradas: list, bruto: pd.DataFrame) -> dict:
    """
    Impacto de um tratamento no desenvolvimento, sem ajustar nenhum modelo: amostras com
    variáveis completas, amostras com alvo, células de variáveis invalidadas e datas afetadas.
    """
    precos = validar_precos(precos)
    passado = precos[precos["Date"] < primeira_data_final(precos)].reset_index(drop=True)
    base = construir_amostras(passado).set_index("decision_date")
    tratada = construir_amostras(passado, politica=entradas, bruto=bruto).set_index("decision_date")
    sem_variaveis = base.index.difference(tratada.index)
    comuns = base.index.intersection(tratada.index)
    alvo_perdido = comuns[base.loc[comuns, "y"].notna().to_numpy() & tratada.loc[comuns, "y"].isna().to_numpy()]
    nomes = [c for c in base.columns if c not in ("entry_date", "label_end_date", "y")]
    celulas = int(base.loc[sem_variaveis, nomes].notna().to_numpy().sum())
    afetadas = sem_variaveis.union(alvo_perdido)
    dev = lambda idx: int(((idx.year >= config.ANOS_DESENVOLVIMENTO[0]) & (idx.year <= config.ANOS_DESENVOLVIMENTO[-1])).sum())
    return {
        "amostras_sem_politica": int(len(base)),
        "amostras_com_politica": int(len(tratada)),
        "amostras_invalidadas_por_variaveis": int(len(sem_variaveis)),
        "amostras_com_alvo_invalidado": int(len(alvo_perdido)),
        "celulas_de_variaveis_invalidadas": celulas,
        "datas_afetadas": {"primeira": afetadas.min().date().isoformat() if len(afetadas) else None,
                           "ultima": afetadas.max().date().isoformat() if len(afetadas) else None,
                           "quantidade": int(len(afetadas))},
        "amostras_afetadas_nas_validacoes_2014_2021": dev(afetadas),
        # As amostras que sobram têm as mesmas datas de entrada e de fim do alvo: nada foi deslocado.
        "calendario_preservado": bool(
            base.loc[comuns, ["entry_date", "label_end_date"]].equals(tratada.loc[comuns, ["entry_date", "label_end_date"]])),
        **_alteracoes(base, tratada, comuns, nomes),
    }


# Mudança material: diferença absoluta acima de 1e-9. Abaixo disso, ficam o ruído de ponto
# flutuante (até cerca de 1e-12 quando a série é reescalada por uma constante) e o resíduo
# que as médias recursivas carregam depois da janela afetada.
LIMIAR_ALTERACAO = 1e-9


def _alteracoes(base: pd.DataFrame, tratada: pd.DataFrame, comuns, nomes, limiar=LIMIAR_ALTERACAO) -> dict:
    """Amostras preservadas cujas variáveis ou cujo alvo mudaram de valor com a política."""
    a = base.loc[comuns, nomes + ["y"]].to_numpy(dtype=float)
    b = tratada.loc[comuns, nomes + ["y"]].to_numpy(dtype=float)
    diferenca = np.where(np.isnan(a) & np.isnan(b), 0.0, np.abs(a - b))
    resumo = {}
    for nome, limite in (("acima_de_1e-9", limiar), ("acima_de_1e-6", 1e-6)):
        diferente = diferenca > limite
        linhas = comuns[diferente.any(axis=1)]
        colunas = [c for c, mudou in zip(nomes + ["y"], diferente.any(axis=0)) if mudou]
        resumo[nome] = {
            "amostras": int(len(linhas)),
            "colunas": sorted({c.split("_lag")[0] for c in colunas}),
            "primeira": linhas.min().date().isoformat() if len(linhas) else None,
            "ultima": linhas.max().date().isoformat() if len(linhas) else None,
            "amostras_com_alvo_alterado": int(diferente[:, -1].sum()),
        }
    alvo = diferenca[:, -1]
    return {
        "amostras_preservadas_com_valores_alterados": resumo,
        "maior_variacao_absoluta_do_alvo": float(alvo.max()) if len(alvo) and alvo.max() > 0 else None,
    }


def comando_qualidade(_args) -> int:
    """
    Impacto da política sem rodar modelos. Com a política decidida, mede a política vigente
    (versão e hash) e confere a faixa OHLC das datas tratadas na visão derivada.
    """
    _manifesto, precos, _cdi = carregar()
    politica = carregar_politica()
    brutos = carregar_brutos()
    relatorio = {"politica": {"versao": politica.get("versao"), "sha256": sha256(config.POLITICA_QUALIDADE)}}
    for ativo, serie in precos.items():
        entradas = entradas_do_ativo(politica, ativo)
        if all(e.get("decisao") == "decidida" for e in entradas):
            derivada = serie_derivada(serie, entradas, brutos[ativo]).set_index("Date")
            faixa = {e["data"]: _faixa(derivada.loc[pd.Timestamp(e["data"])]) for e in entradas}
            relatorio[ativo] = {"politica_vigente": impacto_politica(serie, entradas, brutos[ativo]),
                                "faixa_ohlc_na_visao_derivada": faixa}
        else:
            relatorio[ativo] = {tratamento: impacto_politica(serie, [{**e, "tratamento": tratamento} for e in entradas],
                                                              brutos[ativo])
                                for tratamento in ("invalidar", "substituir_por_fonte_verificada")}
    RESULTADOS.mkdir(exist_ok=True)
    (RESULTADOS / "qualidade_impacto.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=2),
                                                        encoding="utf-8")
    registrar("impacto_politica_qualidade", relatorio)
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    return 0


def _faixa(linha) -> dict:
    return {"abertura": float(linha["Open"]), "maxima": float(linha["High"]), "minima": float(linha["Low"]),
            "fechamento": float(linha["Close"]),
            "consistente": bool(linha["Low"] <= linha["Open"] <= linha["High"] and linha["Low"] <= linha["Close"] <= linha["High"])}


def embargos_periodo_final(anos=config.ANOS_FINAIS) -> dict:
    """
    Embargo na fronteira do bloco de avaliação (início de 2022). Nas reestimações
    anuais dentro do bloco já iniciado não há nova interrupção das previsões; o
    treino usa só alvos realizados na data do ajuste (expurgo).
    """
    return {ano: (config.EMBARGO if ano == anos[0] or config.EMBARGO_NAS_REESTIMACOES_FINAIS else 0)
            for ano in anos}


def avaliar_final_ativo(ativo: str, precos: pd.DataFrame, cdi: pd.DataFrame, elegiveis: list[str],
                        politica: list, bruto: pd.DataFrame) -> dict:
    precos = validar_precos(precos)
    amostras = construir_amostras(precos, politica=politica, bruto=bruto)
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
    # A execução simulada usa a mesma visão derivada das variáveis e dos alvos.
    derivada = serie_derivada(precos, politica, bruto)
    backtests = {c: backtest(derivada, cdi, decisoes, c, config.DATA_CORTE) for c in custos}
    _p, _a, dobras = desenvolver_ativo(ativo, precos, politica, bruto)
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
    politica = carregar_politica()
    exigir_decidida(politica)
    brutos = carregar_brutos()
    _manifesto, precos, cdi = carregar()
    elegiveis = json.loads(DATAS_ELEGIVEIS.read_text(encoding="utf-8"))
    RESULTADOS.mkdir(exist_ok=True)
    config.MARCA_FINAL_USADO.write_text(json.dumps({"aberta_em": now_brasilia().isoformat(timespec="seconds")}),
                                        encoding="utf-8")
    resultados = {ativo: avaliar_final_ativo(ativo, serie, cdi, elegiveis[ativo],
                                             entradas_do_ativo(politica, ativo), brutos[ativo])
                  for ativo, serie in precos.items()}
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
    sub.add_parser("qualidade").set_defaults(funcao=comando_qualidade)
    desenvolver = sub.add_parser("desenvolver")
    desenvolver.add_argument("--ensaio", action="store_true",
                             help="roda sem exigir a política decidida; registrado como ensaio, não oficial")
    desenvolver.set_defaults(funcao=comando_desenvolver)
    final = sub.add_parser("final")
    final.add_argument("--confirmo-abertura", action="store_true")
    final.set_defaults(funcao=comando_final)
    args = parser.parse_args(argv)
    return args.funcao(args)


if __name__ == "__main__":
    sys.exit(main())
