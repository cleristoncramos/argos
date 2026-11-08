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


def aplicar_aos_precos(serie: pd.DataFrame, entradas: list[dict], bruto: pd.DataFrame | None = None) -> pd.DataFrame:
    """Visão derivada dos preços: mesmas datas, campos tratados conforme a política."""
    derivada = serie.copy()
    fatores = None
    if bruto is not None:
        b = bruto.assign(Date=pd.to_datetime(bruto["Date"]))
        fatores = (b["Adj Close"] / b["Close"]).set_axis(b["Date"])
    for entrada in entradas:
        data = pd.Timestamp(entrada["data"])
        linha = derivada.index[derivada["Date"] == data]
        if len(linha) != 1:
            raise ValueError(f"Data {entrada['data']} da política não encontrada uma única vez na série.")
        for campo in entrada["campos"]:
            if entrada["tratamento"] == "invalidar":
                derivada.loc[linha, campo] = np.nan
            elif entrada["tratamento"] == "substituir_por_fonte_verificada":
                if fatores is None:
                    raise ValueError("A substituição exige a série bruta para o fator de ajuste.")
                derivada.loc[linha, campo] = float(entrada["fonte"]["valores"][campo]) * float(fatores.loc[data])
            else:
                raise PoliticaPendente(f"Tratamento não decidido para {entrada['ativo']} {entrada['data']}.")
    return derivada


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
