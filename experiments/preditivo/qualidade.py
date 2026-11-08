"""
Política de qualidade dos dados: visão derivada para a modelagem.

Os arquivos do snapshot nunca são alterados. A política é lida de
`politica_qualidade.json` (versionado) e aplicada na memória, por campo e por
dependência de cálculo, preservando o calendário original (nenhuma data é removida).

Tratamentos possíveis de um campo questionado:
- "invalidar": o valor passa a ser ausente (NaN). Nenhum cálculo o usa e nada é
  estimado no lugar dele. Janelas finitas que o incluiriam ficam inválidas (o core
  usa min_periods igual à janela); as variáveis recursivas seguem sem essa observação
  e ficam inválidas por uma janela de reaquecimento (REAQUECIMENTO pregões), a mesma
  convenção do aquecimento inicial das médias exponenciais em core/features.py.
- "substituir_por_fonte_verificada": o valor da fonte externa é convertido para a base
  ajustada pelo fator a_t = Adj Close / Close da própria data e usado na visão derivada.
A política só pode ser usada na rodada oficial quando todas as entradas estiverem decididas.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from experiments.preditivo import config

TRATAMENTOS = ("invalidar", "substituir_por_fonte_verificada")
REAQUECIMENTO = 78   # 3 × 26, a convenção de aquecimento das médias exponenciais em core/features.py

# Colunas de preço que cada variável consome (antes das defasagens _lag1 a _lag3).
DEPENDENCIAS = {
    "ret_1": {"Close"},
    "close_over_sma_short": {"Close"},
    "close_over_sma_long": {"Close"},
    "ema_spread": {"Close"},
    "rsi": {"Close"},
    "macd_hist_over_close": {"Close"},
    "bb_percent_b": {"Close"},
    "atr_over_close": {"High", "Low", "Close"},
    "vol_rolling": {"Close"},
    "ret_20": {"Close"},
    "ret_60": {"Close"},
    "dist_pico_252": {"Close"},
}
RECURSIVAS = {"ema_spread", "rsi", "macd_hist_over_close", "atr_over_close"}
CAMPOS_DO_ALVO_E_DA_EXECUCAO = {"Close"}   # alvo P(t+21)/P(t+1) − 1 e execução no fechamento


class PoliticaPendente(RuntimeError):
    """A política tem entradas sem decisão: a rodada oficial não pode usar a visão derivada."""


def carregar_politica(caminho: Path = config.POLITICA_QUALIDADE) -> dict:
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def entradas_do_ativo(politica: dict, ativo: str) -> list[dict]:
    return [e for e in politica.get("entradas", []) if e["ativo"] == ativo]


def exigir_decidida(politica: dict) -> None:
    pendentes = [f"{e['ativo']} {e['data']}" for e in politica.get("entradas", [])
                 if e.get("decisao") != "decidida" or e.get("tratamento") not in TRATAMENTOS]
    if pendentes:
        raise PoliticaPendente("Política de qualidade com decisão pendente: " + ", ".join(pendentes) + ".")


def campos_por_variavel(nome: str) -> set:
    base = nome.split("_lag")[0]
    return DEPENDENCIAS[base]


class TransformacaoNaoReproduzivel(RuntimeError):
    """O método de ajuste não reproduz a fonte nas datas afetadas: a substituição não pode ser usada."""


TOLERANCIA_REPRODUCAO = 1e-5   # diferença relativa máxima entre o fator reconstruído e o da fonte
CAMPOS_PRECO = ("Open", "High", "Low", "Close")


def fator_reconstruido(bruto: pd.DataFrame) -> pd.Series:
    """
    Fator de ajuste por proventos pelo método multiplicativo: os preços anteriores a cada
    data ex são multiplicados por (1 − provento / fechamento da véspera). A série bruta da
    fonte já vem corrigida por desdobramentos. Devolve o fator indexado pela data.
    """
    b = bruto.sort_values("Date").reset_index(drop=True)
    fator = np.ones(len(b))
    proventos = b["Dividends"].fillna(0.0).to_numpy(dtype=float) if "Dividends" in b.columns else np.zeros(len(b))
    fechamento = b["Close"].to_numpy(dtype=float)
    for i in np.flatnonzero(proventos > 0):
        if i == 0:
            raise TransformacaoNaoReproduzivel("Provento na primeira data da série: sem fechamento da véspera.")
        fator[:i] *= 1.0 - proventos[i] / fechamento[i - 1]
    return pd.Series(fator, index=pd.DatetimeIndex(pd.to_datetime(b["Date"])))


def _bruto_indexado(bruto: pd.DataFrame) -> pd.DataFrame:
    b = bruto.assign(Date=pd.to_datetime(bruto["Date"])).sort_values("Date")
    return b.set_index("Date")


def aplicar_substituicoes(serie: pd.DataFrame, bruto: pd.DataFrame, entradas: list[dict]) -> pd.DataFrame:
    """
    Substitui campos da base bruta pelos valores da fonte verificada e leva a correção para a
    base ajustada recalculando o fator: a razão entre o fator com a correção e o fator original
    multiplica as quatro colunas em cada data (vale 1,0 onde nada muda). Antes, confere que o
    método reproduz o fator da fonte nas datas afetadas; depois, confere a faixa OHLC.
    """
    if not entradas:
        return serie
    b = _bruto_indexado(bruto)
    datas = pd.DatetimeIndex(pd.to_datetime(serie["Date"]))
    if not datas.isin(b.index).all():
        raise TransformacaoNaoReproduzivel("Datas da série ajustada ausentes na série bruta.")
    corrigido = b.copy()
    substituidas = []
    for entrada in entradas:
        data = pd.Timestamp(entrada["data"])
        for campo in entrada["campos"]:
            corrigido.loc[data, campo] = float(entrada["substituicoes"][campo]["b3"])
            substituidas.append((data, campo))
    fator_fonte = b["Adj Close"] / b["Close"]
    original = fator_reconstruido(b.reset_index())
    novo = fator_reconstruido(corrigido.reset_index())
    razao = novo / original
    afetadas = razao.index[(razao != 1.0).to_numpy()].union(pd.DatetimeIndex([d for d, _ in substituidas]))
    erro = (original.loc[afetadas] / fator_fonte.loc[afetadas] - 1.0).abs()
    if len(erro) and float(erro.max()) > TOLERANCIA_REPRODUCAO:
        raise TransformacaoNaoReproduzivel(
            f"O método de ajuste não reproduz a fonte nas datas afetadas (maior diferença relativa {erro.max():.2e}).")

    derivada = serie.copy().reset_index(drop=True)
    fator_datas = razao.loc[datas].to_numpy()
    for campo in CAMPOS_PRECO:
        derivada[campo] = derivada[campo].to_numpy(dtype=float) * fator_datas
    for data, campo in substituidas:
        linha = derivada.index[derivada["Date"] == data][0]
        derivada.loc[linha, campo] = float(corrigido.loc[data, campo]) * float(fator_fonte.loc[data]) * float(razao.loc[data])
    for data in {d for d, _ in substituidas}:
        r = derivada.loc[derivada["Date"] == data].iloc[0]
        alto, baixo = r["High"] * (1 + 1e-9), r["Low"] * (1 - 1e-9)
        if not (baixo <= r["Open"] <= alto and baixo <= r["Close"] <= alto and r["Low"] <= r["High"]):
            raise TransformacaoNaoReproduzivel(f"A faixa OHLC continua violada em {data.date()} depois da substituição.")
    return derivada


def aplicar_aos_precos(serie: pd.DataFrame, entradas: list[dict], bruto: pd.DataFrame | None = None) -> pd.DataFrame:
    """Visão derivada dos preços: mesmas datas, campos tratados conforme a política."""
    for entrada in entradas:
        if entrada.get("tratamento") not in TRATAMENTOS:
            raise PoliticaPendente(f"Tratamento não decidido para {entrada['ativo']} {entrada['data']}.")
    substituir = [e for e in entradas if e["tratamento"] == "substituir_por_fonte_verificada"]
    if substituir:
        if bruto is None:
            raise ValueError("A substituição exige a série bruta para recalcular o fator de ajuste.")
        serie = aplicar_substituicoes(serie, bruto, substituir)
    derivada = serie.copy()
    for entrada in (e for e in entradas if e["tratamento"] == "invalidar"):
        linha = derivada.index[derivada["Date"] == pd.Timestamp(entrada["data"])]
        if len(linha) != 1:
            raise ValueError(f"Data {entrada['data']} da política não encontrada uma única vez na série.")
        for campo in entrada["campos"]:
            derivada.loc[linha, campo] = np.nan
    return derivada


def serie_derivada(precos: pd.DataFrame, entradas: list[dict] | None, bruto: pd.DataFrame | None) -> pd.DataFrame:
    """Série de preços da visão derivada (usada nas variáveis, nos alvos e na execução simulada)."""
    from experiments.preditivo.amostras import validar_precos

    serie = validar_precos(precos)
    return aplicar_aos_precos(serie, entradas, bruto) if entradas else serie


def invalidar_recursivas(variaveis: pd.DataFrame, datas: pd.Series, entradas: list[dict]) -> pd.DataFrame:
    """
    Reaquecimento: variáveis recursivas que dependem de um campo invalidado ficam ausentes
    da data questionada até REAQUECIMENTO pregões depois (contados no calendário original).
    """
    resultado = variaveis.copy()
    datas = pd.DatetimeIndex(pd.to_datetime(datas))
    for entrada in entradas:
        if entrada["tratamento"] != "invalidar":
            continue
        posicao = datas.get_loc(pd.Timestamp(entrada["data"]))
        fim = min(posicao + REAQUECIMENTO, len(datas) - 1)
        campos = set(entrada["campos"])
        for nome in resultado.columns:
            if nome == "Date" or nome.split("_lag")[0] not in RECURSIVAS:
                continue
            if campos & campos_por_variavel(nome):
                resultado.iloc[posicao:fim + 1, resultado.columns.get_loc(nome)] = np.nan
    return resultado
