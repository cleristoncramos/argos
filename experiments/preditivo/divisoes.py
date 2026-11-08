"""
Divisões temporais com embargo e expurgo pelas datas (protocolo, seção 6.2).

Regra de cada divisão, nesta ordem:
1. datas destinadas à avaliação (um ano do calendário da série);
2. embargo: exclui os primeiros `embargo` pregões desse intervalo;
3. expurgo: remove do treino toda amostra com label_end_date ≥ primeira data avaliada;
4. as divisões internas da escolha do alpha seguem as mesmas regras.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from experiments.preditivo.config import EMBARGO


class FronteiraViolada(RuntimeError):
    """Uma amostra de treino enxerga a avaliação: o experimento deve parar."""


@dataclass(frozen=True)
class Divisao:
    ano: int
    primeira_data: pd.Timestamp   # primeira data efetivamente avaliada
    ultima_data: pd.Timestamp     # última data do intervalo de avaliação
    treino: np.ndarray            # índices (posição) das amostras de treino
    avaliacao: np.ndarray         # índices das amostras avaliadas (alvo pode não estar realizado)


def datas_do_ano(calendario: pd.Series, ano: int) -> pd.DatetimeIndex:
    datas = pd.DatetimeIndex(pd.to_datetime(calendario)).sort_values()
    return datas[datas.year == ano]


def primeira_data_avaliada(calendario: pd.Series, ano: int, embargo: int = EMBARGO) -> pd.Timestamp:
    """Data inicial do ano depois do embargo, contada no calendário da série."""
    datas = datas_do_ano(calendario, ano)
    if len(datas) <= embargo:
        raise ValueError(f"O ano {ano} tem {len(datas)} pregões; não sobra data depois do embargo de {embargo}.")
    return datas[embargo]


def verificar_fronteira(amostras: pd.DataFrame, treino: np.ndarray, primeira: pd.Timestamp) -> None:
    """Teste obrigatório: toda amostra de treino tem label_end_date < primeira data avaliada."""
    fim = amostras["label_end_date"].to_numpy()[treino]
    if len(fim) and (pd.isna(fim).any() or (pd.DatetimeIndex(fim) >= primeira).any()):
        raise FronteiraViolada(f"Amostra de treino com alvo que alcança {primeira.date()} ou não realizado.")


def treino_ate(amostras: pd.DataFrame, primeira: pd.Timestamp, inicio_treino=None) -> np.ndarray:
    """Expurgo: amostras decididas e com alvo realizado antes da primeira data avaliada."""
    decisao = amostras["decision_date"]
    fim = amostras["label_end_date"]
    # Alvo ausente por política de qualidade (y = NaN) não entra no treino.
    mascara = (decisao < primeira) & fim.notna() & (fim < primeira) & amostras["y"].notna()
    if inicio_treino is not None:
        mascara &= decisao >= pd.Timestamp(inicio_treino)
    return np.flatnonzero(mascara.to_numpy())


def dividir_ano(
    amostras: pd.DataFrame,
    calendario: pd.Series,
    ano: int,
    embargo: int = EMBARGO,
    limite_avaliacao=None,
) -> Divisao:
    """
    Divisão de um ano de avaliação. `limite_avaliacao` (exclusivo) corta o fim
    do intervalo, por exemplo na primeira data do período final, para que o
    desenvolvimento não avalie datas que pertencem ao teste.
    """
    datas = datas_do_ano(calendario, ano)
    primeira = primeira_data_avaliada(calendario, ano, embargo)
    ultima = datas[-1]
    decisao = amostras["decision_date"]
    avaliacao = (decisao >= primeira) & (decisao <= ultima)
    if limite_avaliacao is not None:
        avaliacao &= decisao < pd.Timestamp(limite_avaliacao)
    treino = treino_ate(amostras, primeira)
    verificar_fronteira(amostras, treino, primeira)
    return Divisao(ano, primeira, ultima, treino, np.flatnonzero(avaliacao.to_numpy()))


def divisoes_internas(
    amostras: pd.DataFrame,
    calendario: pd.Series,
    treino: np.ndarray,
    primeira_externa: pd.Timestamp,
    quantidade: int,
    embargo: int = EMBARGO,
) -> list[Divisao]:
    """
    Validações internas para escolher o alpha: os `quantidade` últimos anos
    completos do treino, cada um com embargo e expurgo pelas datas. As
    avaliações internas usam só amostras do treino externo (alvos realizados
    antes da primeira data avaliada externa).
    """
    sub = amostras.iloc[treino]
    anos = sorted(set(sub["decision_date"].dt.year))
    completos = [a for a in anos if a < primeira_externa.year]
    escolhidos = completos[-quantidade:]
    if len(escolhidos) < quantidade:
        raise ValueError(f"O treino tem {len(completos)} anos completos; são necessários {quantidade}.")

    internas = []
    conjunto = set(treino.tolist())
    for ano in escolhidos:
        primeira = primeira_data_avaliada(calendario, ano, embargo)
        ultima = datas_do_ano(calendario, ano)[-1]
        decisao = amostras["decision_date"]
        mascara = (decisao >= primeira) & (decisao <= ultima)
        avaliacao = np.array([i for i in np.flatnonzero(mascara.to_numpy()) if i in conjunto], dtype=int)
        treino_interno = np.array([i for i in treino_ate(amostras, primeira) if i in conjunto], dtype=int)
        verificar_fronteira(amostras, treino_interno, primeira)
        internas.append(Divisao(ano, primeira, ultima, treino_interno, avaliacao))
    return internas
