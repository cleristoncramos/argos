"""
Janelas e regimes dos casos de síntese da fase 1 (decisão DL1-J, 09/11/2026).

Regra única, aplicada ao fechamento ajustado, sem julgamento visual:
- janelas fixas em pregões: curta = 126, longa = 504;
- variação = fechamento no fim / fechamento no início − 1, com o início 126 ou 504
  pregões antes do fim (a janela tem N retornos e N + 1 fechamentos);
- drawdown máximo = maior queda do fechamento em relação ao pico anterior dentro da janela;
- regimes: alta (variação > +10% e drawdown < 15%), baixa (variação < −10%) e lateral
  (os demais: variação entre −10% e +10%, ou variação > +10% com drawdown ≥ 15%).
  Com variação < −10%, vale baixa, qualquer que seja o drawdown (interpretação a confirmar);
- candidatas: janelas que terminam no último pregão de cada mês, de jan/2016 a dez/2021;
- escolha: em cada célula (ativo × regime × comprimento), a candidata de variação mais
  próxima da mediana da célula; em empate, a mais antiga.

Trava temporal: a série é cortada em 30/12/2021 logo depois da leitura, antes de qualquer
cálculo; nenhum caso usa dado do bloco reservado da linha preditiva. Não executa código do
pipeline preditivo: lê o CSV congelado e confere o hash pelo manifesto.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
SNAPSHOT = RAIZ / "experiments" / "preditivo" / "dados" / "snap-20261108-01"
ATIVOS = ("PETR4.SA", "VALE3.SA")
JANELAS = {"curta": 126, "longa": 504}
LIMITE_VARIACAO = 0.10
LIMITE_DRAWDOWN = 0.15
INICIO_CANDIDATAS = "2016-01-01"
FIM_CANDIDATAS = "2021-12-31"
TRAVA_TEMPORAL = "2021-12-30"
REGIMES = ("alta", "baixa", "lateral")


def _sha256(caminho: Path) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def carregar_fechamento(ativo: str, pasta: Path = SNAPSHOT) -> pd.Series:
    """Fechamento ajustado do snapshot congelado, com hash conferido e cortado na trava temporal."""
    nome = f"{ativo.replace('.', '_')}_ajustado.csv"
    manifesto = json.loads((pasta / "manifest.json").read_text(encoding="utf-8"))
    esperado = manifesto["arquivos"][nome]["sha256"]
    if _sha256(pasta / nome) != esperado:
        raise ValueError(f"Hash de {nome} diferente do manifesto do snapshot.")
    serie = pd.read_csv(pasta / nome, usecols=["Date", "Close"], parse_dates=["Date"])
    serie = serie[serie["Date"] <= pd.Timestamp(TRAVA_TEMPORAL)]          # corte antes de qualquer cálculo
    return serie.set_index("Date")["Close"].astype(float).dropna().sort_index()


def classificar(variacao: float, drawdown: float) -> str:
    if variacao < -LIMITE_VARIACAO:
        return "baixa"
    if variacao > LIMITE_VARIACAO and drawdown < LIMITE_DRAWDOWN:
        return "alta"
    return "lateral"


def metricas_janela(fechamento: pd.Series, fim: pd.Timestamp, pregoes: int) -> dict | None:
    """Métricas da janela de `pregoes` retornos que termina em `fim`; None se faltar histórico."""
    posicao = fechamento.index.get_loc(fim)
    if posicao < pregoes:
        return None
    janela = fechamento.iloc[posicao - pregoes: posicao + 1]
    variacao = float(janela.iloc[-1] / janela.iloc[0] - 1)
    drawdown = float((1 - janela / janela.cummax()).max())
    return {
        "inicio": janela.index[0].date().isoformat(),
        "fim": janela.index[-1].date().isoformat(),
        "pregoes": pregoes,
        "variacao": variacao,
        "drawdown_maximo": drawdown,
        "regime": classificar(variacao, drawdown),
    }


def fins_de_mes(fechamento: pd.Series, inicio: str = INICIO_CANDIDATAS, fim: str = FIM_CANDIDATAS) -> list:
    """Último pregão de cada mês no intervalo das candidatas."""
    datas = fechamento.index[(fechamento.index >= pd.Timestamp(inicio)) & (fechamento.index <= pd.Timestamp(fim))]
    return list(pd.Series(datas, index=datas).groupby([datas.year, datas.month]).max())


def candidatas(fechamento: pd.Series, pregoes: int) -> list:
    return [m for m in (metricas_janela(fechamento, d, pregoes) for d in fins_de_mes(fechamento)) if m is not None]


def escolher(lista: list) -> dict | None:
    """Variação mais próxima da mediana da célula; em empate, a janela mais antiga."""
    if not lista:
        return None
    mediana = float(np.median([c["variacao"] for c in lista]))
    return min(lista, key=lambda c: (abs(c["variacao"] - mediana), c["fim"])) | {"mediana_da_celula": mediana,
                                                                             "candidatas_na_celula": len(lista)}


def selecionar(fechamentos: dict) -> list:
    """Uma janela por ativo × regime × comprimento (12 com dois ativos), na ordem declarada."""
    casos = []
    for ativo in ATIVOS:
        for nome, pregoes in JANELAS.items():
            todas = candidatas(fechamentos[ativo], pregoes)
            for regime in REGIMES:
                escolhida = escolher([c for c in todas if c["regime"] == regime])
                casos.append({"ativo": ativo, "janela": nome, "regime_alvo": regime,
                              "candidatas_no_comprimento": len(todas), "escolhida": escolhida})
    return casos
