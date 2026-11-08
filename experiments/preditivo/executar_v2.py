"""
Ponto de entrada do piloto v2 (docs/preditivo/protocolo_piloto_v2.md). Uso, a partir da raiz:

    python -m experiments.preditivo.executar_v2 reproduzir-v1   # v2 restrita à grade da v1 = resultados oficiais da v1
    python -m experiments.preditivo.executar_v2 desenvolver     # desenvolvimento oficial (uma vez, com o código congelado)
    python -m experiments.preditivo.executar_v2 listar-datas    # só depois da decisão escrita de abertura
    python -m experiments.preditivo.executar_v2 final --confirmo-abertura   # travado (protocolo v2, seção 9)

Compartilha as funções testadas da v1 e usa configuração, registro, resultados e travas
próprios. Nada aqui altera arquivos da v1. O desenvolvimento treina, seleciona e avalia só
com dados anteriores ao 21º pregão de 2022: o arquivo é carregado inteiro e truncado antes.
"""

from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import pandas as pd

from core.clock import now_brasilia
from experiments.preditivo import config, config_v2
from experiments.preditivo.abertura import verificar_abertura
from experiments.preditivo.amostras import construir_amostras, realizadas_ate, validar_precos
from experiments.preditivo.avaliacao import prever_anos
from experiments.preditivo.dados import caminho_manifesto, carregar, carregar_brutos
from experiments.preditivo.elegibilidade import avaliar_v2, filtros_desenvolvimento_v2
from experiments.preditivo.estatistica import (
    acuracia_balanceada,
    alinhar,
    clark_west,
    diebold_mariano,
    diebold_mariano_contra_media,
    erros,
    r2_contra_media_nas_datas,
    r2_contra_referencia,
    r2_fora_da_amostra,
)
from experiments.preditivo.estrategia import backtest, datas_de_decisao
from experiments.preditivo.executar import embargos_periodo_final, primeira_data_final, resumo_previsoes
from experiments.preditivo.qualidade import carregar_politica, entradas_do_ativo, exigir_decidida, serie_derivada
from experiments.preditivo.registro import _hash_opcional, arquivos_alterados, registrar
from experiments.preditivo.util import sha256

COLUNAS_NUMERICAS = ("y", "yhat", "yhat_zero", "yhat_media")
COLUNAS_IDENTIDADE = ("decision_date", "entry_date", "label_end_date", "modelo_id", "ano_ajuste")


class ExecucaoRecusada(RuntimeError):
    pass


# ---------------------------------------------------------------- identificação

def hashes_v2() -> dict:
    return {
        "protocolo": _hash_opcional(config_v2.PROTOCOLO),
        "nota": _hash_opcional(config.NOTA),
        "configuracao": _hash_opcional(config.RAIZ / "config.py"),
        "configuracao_v2": _hash_opcional(config.RAIZ / "config_v2.py"),
        "manifesto_dados": _hash_opcional(caminho_manifesto()),
        "politica_qualidade": _hash_opcional(config.POLITICA_QUALIDADE),
    }


def registrar_v2(evento: str, dados: dict, avaliacao_final: bool = False) -> dict:
    return registrar(evento, dados, avaliacao_final=avaliacao_final, destino=config_v2.REGISTRO,
                     hashes=hashes_v2(), versao=config_v2.VERSAO)


def eventos_v2(registro=None) -> list[dict]:
    caminho = registro or config_v2.REGISTRO
    if not caminho.exists():
        return []
    return [json.loads(linha) for linha in caminho.read_text(encoding="utf-8").splitlines() if linha.strip()]


def exigir_v2_aberta(encerramento=None) -> None:
    caminho = encerramento or config_v2.ENCERRAMENTO
    if caminho.exists():
        raise ExecucaoRecusada(f"A v2 foi encerrada ({caminho.name}): não há nova execução oficial nesta versão.")


def exigir_codigo_congelado(alterados=None) -> None:
    """Protocolo v2, seção 12: o desenvolvimento oficial roda sobre código e configuração commitados."""
    alterados = arquivos_alterados() if alterados is None else alterados
    fora = [a for a in alterados if a not in config_v2.ALTERACOES_ACEITAS]
    if fora:
        raise ExecucaoRecusada("Código ou configuração não congelados (alterações não commitadas): " + ", ".join(fora))


# ---------------------------------------------------------------- desenvolvimento

def desenvolver_ativo_v2(ativo: str, precos: pd.DataFrame, politica: list | None = None,
                         bruto: pd.DataFrame | None = None, alphas=config_v2.ALPHAS):
    """Oito dobras de 2014 a 2021 com a grade informada e os registros da seção 4."""
    precos = validar_precos(precos)
    passado = precos[precos["Date"] < primeira_data_final(precos)].reset_index(drop=True)
    amostras = construir_amostras(passado, politica=politica, bruto=bruto)
    embargos = {ano: config.EMBARGO for ano in config.ANOS_DESENVOLVIMENTO}
    previsoes, ajustes = prever_anos(amostras, passado["Date"], config.ANOS_DESENVOLVIMENTO, embargos, ativo,
                                     alphas=alphas, registros_v2=True)
    dobras = []
    for ano in config.ANOS_DESENVOLVIMENTO:
        bloco = previsoes[previsoes["ano_ajuste"] == ano]
        realizadas = bloco.dropna(subset=["y"])
        dobras.append({"ano": ano, **resumo_previsoes(bloco),
                       "r2_contra_media_historica": r2_contra_referencia(
                           realizadas["y"], realizadas["yhat"], realizadas["yhat_media"])})
    return previsoes, ajustes, dobras


def _diferenca(a, b) -> float:
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    ambos_nan = np.isnan(a) & np.isnan(b)
    d = np.abs(a - b)
    d[ambos_nan] = 0.0
    return float(np.max(d)) if d.size else 0.0


def _dentro(a, b) -> bool:
    return bool(np.allclose(np.asarray(a, dtype=float), np.asarray(b, dtype=float),
                            rtol=config_v2.TOLERANCIA_RELATIVA, atol=config_v2.TOLERANCIA_ABSOLUTA, equal_nan=True))


def _valores(d: dict, prefixo=""):
    """Folhas numéricas de um dicionário aninhado, com o caminho."""
    for chave, valor in d.items():
        caminho = f"{prefixo}{chave}"
        if isinstance(valor, dict):
            yield from _valores(valor, caminho + ".")
        elif isinstance(valor, (int, float)) and not isinstance(valor, bool) or valor is None:
            yield caminho, valor


def comparar_com_v1(previsoes: pd.DataFrame, ajustes: list[dict], dobras: list[dict],
                    oficial_previsoes: pd.DataFrame, oficial: dict) -> dict:
    """Equivalência da v2 restrita à grade da v1 com os resultados oficiais da v1 (seção 11)."""
    problemas = []
    for coluna in COLUNAS_IDENTIDADE:
        a = previsoes[coluna].astype(str).reset_index(drop=True)
        b = oficial_previsoes[coluna].astype(str).reset_index(drop=True)
        if len(a) != len(b) or not a.equals(b):
            problemas.append(f"coluna {coluna} diferente")
    maiores = {}
    for coluna in COLUNAS_NUMERICAS:
        a, b = previsoes[coluna].to_numpy(dtype=float), oficial_previsoes[coluna].to_numpy(dtype=float)
        if len(a) != len(b):
            problemas.append(f"coluna {coluna} com tamanho diferente")
            continue
        maiores[coluna] = _diferenca(a, b)
        if not _dentro(a, b):
            problemas.append(f"coluna {coluna} fora da tolerância")
    for nosso, deles in zip(ajustes, oficial["ajustes"]):
        if nosso["alpha"] != deles["alpha"]:
            problemas.append(f"alpha diferente em {nosso['ano']}")
        for alpha, erro in deles["erros_internos"].items():
            if not _dentro(nosso["erros_internos"][float(alpha)], erro):
                problemas.append(f"erro interno de alpha {alpha} fora da tolerância em {nosso['ano']}")
    for nossa, deles in zip(dobras, oficial["dobras"]):
        valores = dict(_valores(nossa))
        for caminho, valor in _valores(deles):
            outro = valores.get(caminho)
            if (valor is None) != (outro is None) or (valor is not None and not _dentro(outro, valor)):
                problemas.append(f"métrica {caminho} da dobra {deles['ano']} fora da tolerância")
    return {"equivalente": not problemas, "problemas": problemas, "maior_diferenca_absoluta": maiores,
            "tolerancia": {"relativa": config_v2.TOLERANCIA_RELATIVA, "absoluta": config_v2.TOLERANCIA_ABSOLUTA}}


def conferir_valores_comuns(ajustes_v2: list[dict], oficial_v1: dict) -> dict:
    """No desenvolvimento oficial da v2: erros internos dos alphas comuns iguais aos da v1."""
    problemas = []
    for nosso, deles in zip(ajustes_v2, oficial_v1["ajustes"]):
        for alpha, erro in deles["erros_internos"].items():
            if not _dentro(nosso["erros_internos"][float(alpha)], erro):
                problemas.append(f"{nosso['ano']}: alpha {alpha}")
    return {"equivalente": not problemas, "problemas": problemas}


def oficiais_v1() -> tuple[dict, dict]:
    """Resultados oficiais da v1, conferidos pelos hashes do encerramento."""
    encerramento = json.loads(config_v2.ENCERRAMENTO_V1.read_text(encoding="utf-8"))
    for nome, esperado in encerramento["artefatos_de_resultado"].items():
        if sha256(config_v2.RESULTADOS_V1 / nome) != esperado:
            raise ExecucaoRecusada(f"Resultado oficial da v1 diferente do arquivado: {nome}.")
    resumo = json.loads((config_v2.RESULTADOS_V1 / "desenvolvimento_resumo.json").read_text(encoding="utf-8"))
    previsoes = {ativo: pd.read_csv(config_v2.RESULTADOS_V1 / f"desenvolvimento_{ativo.replace('.', '_')}.csv",
                                    parse_dates=["decision_date", "entry_date", "label_end_date"])
                 for ativo in resumo}
    return resumo, previsoes


def reproduzir_v1(precos, politica, brutos) -> dict:
    resumo, oficiais = oficiais_v1()
    relatorio = {}
    for ativo, serie in precos.items():
        entradas = [e for e in entradas_do_ativo(politica, ativo) if e.get("tratamento")]
        previsoes, ajustes, dobras = desenvolver_ativo_v2(ativo, serie, entradas, brutos[ativo],
                                                          alphas=config_v2.ALPHAS_V1)
        relatorio[ativo] = comparar_com_v1(previsoes, ajustes, dobras, oficiais[ativo], resumo[ativo])
    return {"equivalente": all(r["equivalente"] for r in relatorio.values()), "ativos": relatorio}


def comando_reproduzir(_args) -> int:
    _manifesto, precos, _cdi = carregar()
    politica = carregar_politica()
    exigir_decidida(politica)
    resultado = reproduzir_v1(precos, politica, carregar_brutos())
    config_v2.RESULTADOS.mkdir(parents=True, exist_ok=True)
    (config_v2.RESULTADOS / "reproducao_v1.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    registrar_v2("reproducao_v1", resultado)
    print(json.dumps({a: {k: r[k] for k in ("equivalente", "maior_diferenca_absoluta")}
                      for a, r in resultado["ativos"].items()}, ensure_ascii=False, indent=2))
    return 0 if resultado["equivalente"] else 1


def comando_desenvolver(_args) -> int:
    """Desenvolvimento oficial da v2: uma única vez, com código congelado e reprodução da v1 aprovada."""
    exigir_v2_aberta()
    exigir_codigo_congelado()
    resumo_oficial = config_v2.RESULTADOS / "desenvolvimento_resumo.json"
    if resumo_oficial.exists() or any(e["evento"] == "desenvolvimento" for e in eventos_v2()):
        raise ExecucaoRecusada("O desenvolvimento oficial da v2 já foi executado; resultados oficiais não são sobrescritos.")
    _manifesto, precos, _cdi = carregar()
    politica = carregar_politica()
    exigir_decidida(politica)
    brutos = carregar_brutos()
    reproducao = reproduzir_v1(precos, politica, brutos)
    if not reproducao["equivalente"]:
        registrar_v2("reproducao_v1", reproducao)
        raise ExecucaoRecusada("A reprodução da v1 falhou: o desenvolvimento oficial da v2 não prossegue.")
    oficial_v1, _ = oficiais_v1()
    config_v2.RESULTADOS.mkdir(parents=True, exist_ok=True)
    resumo = {}
    for ativo, serie in precos.items():
        entradas = [e for e in entradas_do_ativo(politica, ativo) if e.get("tratamento")]
        previsoes, ajustes, dobras = desenvolver_ativo_v2(ativo, serie, entradas, brutos[ativo])
        previsoes.to_csv(config_v2.RESULTADOS / f"desenvolvimento_{ativo.replace('.', '_')}.csv", index=False)
        resumo[ativo] = {
            "ajustes": ajustes,
            "dobras": dobras,
            "frequencia_alpha": {str(a): sum(1 for x in ajustes if x["alpha"] == a) for a in config_v2.ALPHAS},
            "escolhas_no_limite_superior": sum(1 for x in ajustes if x["alpha_no_limite_superior"]),
            "filtros_desenvolvimento": filtros_desenvolvimento_v2(
                [d["r2_fora_da_amostra"] for d in dobras], [d["r2_contra_media_historica"] for d in dobras]),
            "valores_comuns_iguais_a_v1": conferir_valores_comuns(ajustes, oficial_v1[ativo]),
        }
        registrar_v2("desenvolvimento", {"ativo": ativo, "politica": entradas, **resumo[ativo]})
    resumo["_declaracoes"] = {"nao_independencia": config_v2.DECLARACAO_NAO_INDEPENDENCIA,
                              "periodo_final": config_v2.PERIODO_RESERVADO,
                              "reproducao_v1": {a: r["maior_diferenca_absoluta"] for a, r in reproducao["ativos"].items()}}
    resumo_oficial.write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    for ativo, dados in resumo.items():
        if ativo.startswith("_"):
            continue
        print(f"{ativo}: zero " + ", ".join(f"{d['ano']}: {d['r2_fora_da_amostra']:+.4f}" for d in dados["dobras"]))
        print(f"  média  " + ", ".join(
            f"{d['ano']}: {d['r2_contra_media_historica']:+.4f}" if d["r2_contra_media_historica"] is not None
            else f"{d['ano']}: não calculável" for d in dados["dobras"]))
        print(f"  alpha: {dados['frequencia_alpha']}; filtros: {dados['filtros_desenvolvimento']['filtros']}")
    return 0


# ---------------------------------------------------------------- período final (travado)

def _desenvolvimento_v2_atende() -> bool:
    caminho = config_v2.RESULTADOS / "desenvolvimento_resumo.json"
    if not caminho.exists():
        return False
    resumo = json.loads(caminho.read_text(encoding="utf-8"))
    return all(d["filtros_desenvolvimento"]["atende"] for a, d in resumo.items() if not a.startswith("_"))


def _verificar_condicoes_para_lista(hashes: dict) -> None:
    if config_v2.DATAS_ELEGIVEIS.exists():
        raise ExecucaoRecusada("A lista de datas elegíveis da v2 já existe; não é refeita.")
    if config_v2.MARCA_FINAL_USADO.exists():
        raise ExecucaoRecusada("A avaliação final da v2 já foi usada.")
    if not config_v2.CONDICOES.exists():
        raise ExecucaoRecusada(f"Arquivo de condições ausente: {config_v2.CONDICOES.name}.")
    registro = json.loads(config_v2.CONDICOES.read_text(encoding="utf-8"))
    pendentes = [n for n in config_v2.CONDICOES_ABERTURA if registro.get("condicoes", {}).get(n) is not True]
    diferentes = [n for n, v in hashes.items() if n != "datas_elegiveis"
                  and (v is None or registro.get("hashes", {}).get(n) != v)]
    if pendentes or diferentes:
        raise ExecucaoRecusada("Lista do período final não autorizada: "
                               + "; ".join(filter(None, ["condições pendentes: " + ", ".join(pendentes) if pendentes else "",
                                                         "hashes diferentes: " + ", ".join(diferentes) if diferentes else ""]))
                               + ".")


def comando_listar_datas(_args) -> int:
    exigir_v2_aberta()
    if not _desenvolvimento_v2_atende():
        raise ExecucaoRecusada("O desenvolvimento oficial da v2 não existe ou não atendeu aos critérios 3 e 6.")
    _verificar_condicoes_para_lista(hashes_v2())
    _manifesto, precos, _cdi = carregar()
    politica = carregar_politica()
    exigir_decidida(politica)
    brutos = carregar_brutos()
    corte = pd.Timestamp(config.DATA_CORTE)
    lista = {}
    for ativo, serie in precos.items():
        serie = validar_precos(serie)
        amostras = construir_amostras(serie, politica=entradas_do_ativo(politica, ativo), bruto=brutos[ativo])
        elegiveis = amostras[(amostras["decision_date"] >= primeira_data_final(serie))
                             & realizadas_ate(amostras, corte) & amostras["y"].notna()]
        lista[ativo] = [d.date().isoformat() for d in elegiveis["decision_date"]]
    config_v2.DATAS_ELEGIVEIS.write_text(json.dumps(lista, ensure_ascii=False, indent=2), encoding="utf-8")
    registrar_v2("lista_datas_elegiveis", {"sha256": sha256(config_v2.DATAS_ELEGIVEIS),
                                           "quantidade": {a: len(d) for a, d in lista.items()}})
    return 0


def avaliar_final_ativo_v2(ativo, precos, cdi, elegiveis, politica, bruto) -> dict:
    precos = validar_precos(precos)
    amostras = construir_amostras(precos, politica=politica, bruto=bruto)
    previsoes, ajustes = prever_anos(amostras, precos["Date"], config.ANOS_FINAIS, embargos_periodo_final(), ativo,
                                     alphas=config_v2.ALPHAS, registros_v2=True)
    previsoes.to_csv(config_v2.RESULTADOS / f"final_{ativo.replace('.', '_')}.csv", index=False)
    datas = pd.to_datetime(elegiveis)
    amostra = previsoes[previsoes["decision_date"].isin(datas)]
    teste_dm = diebold_mariano(amostra, datas)
    alinhado, falha = alinhar(amostra, datas)
    r2 = None if falha else r2_fora_da_amostra(alinhado["y"], alinhado["yhat"])
    r2_media = r2_contra_media_nas_datas(amostra, datas)
    decisoes = datas_de_decisao(previsoes)
    custos = sorted(set(config.CUSTOS_SENSIBILIDADE) | {config.CUSTO_LADO_BASE, config.CUSTO_LADO_DOBRO})
    derivada = serie_derivada(precos, politica, bruto)
    backtests = {c: backtest(derivada, cdi, decisoes, c, config.DATA_CORTE) for c in custos}
    _p, _a, dobras = desenvolver_ativo_v2(ativo, precos, politica, bruto)
    decisao = avaliar_v2(r2, teste_dm, [d["r2_fora_da_amostra"] for d in dobras], r2_media,
                         [d["r2_contra_media_historica"] for d in dobras],
                         backtests[config.CUSTO_LADO_BASE], backtests[config.CUSTO_LADO_DOBRO])
    realizadas = decisoes.dropna(subset=["y"])
    return {
        "ativo": ativo, "versao": config_v2.VERSAO, "descricao": config.DESCRICAO_RESULTADO,
        "declaracao_nao_independencia": config_v2.DECLARACAO_NAO_INDEPENDENCIA,
        "ajustes": ajustes,
        "r2_fora_da_amostra": r2,
        "r2_contra_media_historica": r2_media,
        "diebold_mariano": teste_dm.como_dict(),
        "diagnosticos": {"diebold_mariano_contra_media": diebold_mariano_contra_media(amostra, datas).como_dict(),
                         "clark_west": clark_west(amostra, datas).como_dict()},
        "erros": {"ridge": erros(amostra["y"], amostra["yhat"]),
                  "retorno_zero": erros(amostra["y"], amostra["yhat_zero"]),
                  "media_historica": erros(amostra["y"], amostra["yhat_media"])},
        "acuracia_balanceada_nas_decisoes": acuracia_balanceada(realizadas["y"], realizadas["yhat"]),
        "estrategias_por_custo_lado": {str(c): {k: v.como_dict() for k, v in r.items()} for c, r in backtests.items()},
        "dobras_desenvolvimento": dobras,
        "elegibilidade": decisao,
    }


def comando_final(args) -> int:
    exigir_v2_aberta()
    if not _desenvolvimento_v2_atende():
        raise ExecucaoRecusada("O desenvolvimento oficial da v2 não existe ou não atendeu aos critérios 3 e 6.")
    verificar_abertura(args.confirmo_abertura, config_v2.CONDICOES, config_v2.MARCA_FINAL_USADO,
                       config_v2.DATAS_ELEGIVEIS, config_v2.ENCERRAMENTO, hashes=hashes_v2(),
                       versao=config_v2.VERSAO, condicoes_exigidas=config_v2.CONDICOES_ABERTURA)
    politica = carregar_politica()
    exigir_decidida(politica)
    brutos = carregar_brutos()
    _manifesto, precos, cdi = carregar()
    elegiveis = json.loads(config_v2.DATAS_ELEGIVEIS.read_text(encoding="utf-8"))
    config_v2.RESULTADOS.mkdir(parents=True, exist_ok=True)
    config_v2.MARCA_FINAL_USADO.write_text(json.dumps({"aberta_em": now_brasilia().isoformat(timespec="seconds")}),
                                           encoding="utf-8")
    resultados = {ativo: avaliar_final_ativo_v2(ativo, serie, cdi, elegiveis[ativo],
                                                entradas_do_ativo(politica, ativo), brutos[ativo])
                  for ativo, serie in precos.items()}
    (config_v2.RESULTADOS / "final_resultados.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    registrar_v2("avaliacao_final", resultados, avaliacao_final=True)
    for ativo, r in resultados.items():
        print(f"{ativo}: {r['elegibilidade']['mensagem']}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Piloto preditivo v2 do Argos (experimento local).")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("reproduzir-v1").set_defaults(funcao=comando_reproduzir)
    sub.add_parser("desenvolver").set_defaults(funcao=comando_desenvolver)
    sub.add_parser("listar-datas").set_defaults(funcao=comando_listar_datas)
    final = sub.add_parser("final")
    final.add_argument("--confirmo-abertura", action="store_true")
    final.set_defaults(funcao=comando_final)
    args = parser.parse_args(argv)
    return args.funcao(args)


if __name__ == "__main__":
    sys.exit(main())
