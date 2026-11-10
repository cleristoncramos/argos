"""
Casos de média, sazonalidade e frequência histórica da fase 1 (decisão DL1-K, 09/11/2026).

Escolhidos por regra e calculados por código, sobre o fechamento ajustado com a correção P1
e a trava temporal de `janelas.py` (nada depois de 30/12/2021):
- retorno mensal: do último fechamento de um mês ao último do mês seguinte, de fev/2008 a
  dez/2021 (jan/2008 fica de fora porque a série começa em 02/01/2008, sem fechamento do mês
  anterior);
- retorno anual: do último fechamento de um ano ao último do ano seguinte, de 2009 a 2021;
- sazonalidade (4 casos): para cada ativo, o mês de maior e o de menor média de retorno
  mensal; em empate, o mês mais antigo do calendário;
- frequência histórica (2 casos): para cada ativo, a proporção de meses positivos e a de
  anos positivos;
- comparação entre períodos (2 casos): para cada ativo, a média do retorno mensal de 2021
  contra a média do retorno mensal de 2016 a 2020.

Todo caso traz os metadados de que o texto precisa no mesmo parágrafo: número de anos da
amostra, dispersão entre anos e não garantia de repetição (esta, pelo validador e pelo limite
do bloco). Os números são observação histórica, sem linguagem de expectativa.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from experiments.llm_v1_exp import janelas as j

ULTIMO_ANO = 2021
ANOS_ANTERIORES = (2016, 2017, 2018, 2019, 2020)


def retornos_mensais(fechamento: pd.Series) -> pd.Series:
    fim_de_mes = fechamento.groupby([fechamento.index.year, fechamento.index.month]).last()
    datas = fechamento.groupby([fechamento.index.year, fechamento.index.month]).apply(lambda s: s.index.max())
    serie = pd.Series(fim_de_mes.to_numpy(), index=pd.DatetimeIndex(datas.to_numpy()))
    return serie.pct_change().dropna()


def retornos_anuais(fechamento: pd.Series) -> pd.Series:
    fim_de_ano = fechamento.groupby(fechamento.index.year).last()
    return fim_de_ano.pct_change().dropna()


def _resumo(valores: pd.Series) -> dict:
    return {"media": float(valores.mean()), "mediana": float(valores.median()),
            "desvio_entre_anos": float(valores.std(ddof=1)), "minimo": float(valores.min()),
            "maximo": float(valores.max()), "anos_positivos": int((valores > 0).sum()), "anos": int(len(valores))}


def sazonalidade(ativo: str, mensais: pd.Series) -> list:
    por_mes = {m: mensais[mensais.index.month == m] for m in range(1, 13)}
    medias = {m: float(v.mean()) for m, v in por_mes.items()}
    maior = min(medias, key=lambda m: (-medias[m], m))
    menor = min(medias, key=lambda m: (medias[m], m))
    return [{"ativo": ativo, "tipo": "sazonalidade", "escolha": escolha, "mes": mes,
             "periodo": f"{por_mes[mes].index.min().year}-{por_mes[mes].index.max().year}",
             **_resumo(por_mes[mes])}
            for escolha, mes in (("maior_media", maior), ("menor_media", menor))]


def frequencia(ativo: str, mensais: pd.Series, anuais: pd.Series) -> dict:
    return {"ativo": ativo, "tipo": "frequencia_historica",
            "meses_positivos": int((mensais > 0).sum()), "meses": int(len(mensais)),
            "proporcao_meses_positivos": float((mensais > 0).mean()),
            "anos_positivos": int((anuais > 0).sum()), "anos": int(len(anuais)),
            "proporcao_anos_positivos": float((anuais > 0).mean()),
            "desvio_entre_anos": float(anuais.std(ddof=1)),
            "periodo_mensal": f"{mensais.index.min():%Y-%m}..{mensais.index.max():%Y-%m}",
            "periodo_anual": f"{int(anuais.index.min())}-{int(anuais.index.max())}"}


def comparacao(ativo: str, mensais: pd.Series, anuais: pd.Series) -> dict:
    ultimo = mensais[mensais.index.year == ULTIMO_ANO]
    anteriores = mensais[mensais.index.year.isin(ANOS_ANTERIORES)]
    return {"ativo": ativo, "tipo": "comparacao_entre_periodos",
            "media_mensal_ultimo_ano": float(ultimo.mean()), "meses_ultimo_ano": int(len(ultimo)),
            "media_mensal_anos_anteriores": float(anteriores.mean()), "meses_anos_anteriores": int(len(anteriores)),
            "ultimo_ano": ULTIMO_ANO, "anos_anteriores": f"{ANOS_ANTERIORES[0]}-{ANOS_ANTERIORES[-1]}",
            "anos": len(ANOS_ANTERIORES) + 1,
            "desvio_entre_anos_anteriores": float(anuais[anuais.index.isin(ANOS_ANTERIORES)].std(ddof=1)),
            "retornos_anuais_anteriores": {int(a): float(v) for a, v in anuais[anuais.index.isin(ANOS_ANTERIORES)].items()},
            "retorno_anual_ultimo_ano": float(anuais.loc[ULTIMO_ANO])}


def casos(fechamentos: dict) -> list:
    """Os 8 casos, na ordem: por ativo, maior e menor mês, frequência e comparação."""
    lista = []
    for ativo in j.ATIVOS:
        mensais, anuais = retornos_mensais(fechamentos[ativo]), retornos_anuais(fechamentos[ativo])
        lista += sazonalidade(ativo, mensais) + [frequencia(ativo, mensais, anuais), comparacao(ativo, mensais, anuais)]
    return lista
