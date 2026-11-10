"""
Janelas e regimes dos casos de síntese da fase 1 (decisões DL1-J e DL1-K, 09/11/2026).

Regra única, aplicada ao fechamento ajustado, sem julgamento visual:
- janelas fixas em pregões: curta = 126, longa = 504;
- variação = fechamento no fim / fechamento no início − 1, com o início 126 ou 504
  pregões antes do fim (a janela tem N retornos e N + 1 fechamentos);
- regimes (DL1-K, só pela variação): alta (> +10%), baixa (< −10%) e lateral (de −10% a
  +10%, inclusive). Mutuamente exclusivos e exaustivos, sem ordem de prioridade;
- drawdown máximo (maior queda em relação ao pico anterior dentro da janela) e volatilidade
  anualizada (desvio-padrão amostral dos retornos diários simples × raiz de 252) são
  metadados obrigatórios de cada caso: aparecem no contexto e não classificam nada;
- a definição original da DL1-J (que usava o drawdown no regime) foi trocada depois de
  ver os dados, por defeito de validade do construto ("lateral" com +83,72%), e fica em
  `classificar_original`, sem uso, só para auditoria;
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
PREGOES_ANO = 252


def _sha256(caminho: Path) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def carregar_fechamento(ativo: str, pasta: Path = SNAPSHOT, corrigir: bool = True) -> pd.Series:
    """Fechamento ajustado do snapshot congelado, com hash conferido, cortado na trava temporal e com a P1."""
    serie = _ler_fechamento(ativo, pasta)
    return corrigir_p1(serie) if corrigir and ativo == P1_ATIVO else serie


def _ler_fechamento(ativo: str, pasta: Path) -> pd.Series:
    nome = f"{ativo.replace('.', '_')}_ajustado.csv"
    manifesto = json.loads((pasta / "manifest.json").read_text(encoding="utf-8"))
    esperado = manifesto["arquivos"][nome]["sha256"]
    if _sha256(pasta / nome) != esperado:
        raise ValueError(f"Hash de {nome} diferente do manifesto do snapshot.")
    serie = pd.read_csv(pasta / nome, usecols=["Date", "Close"], parse_dates=["Date"])
    serie = serie[serie["Date"] <= pd.Timestamp(TRAVA_TEMPORAL)]          # corte antes de qualquer cálculo
    return serie.set_index("Date")["Close"].astype(float).dropna().sort_index()


# Correção P1 reimplementada de forma isolada, só para o fechamento ajustado da PETR4
# (relatório do snapshot, seção 7.2): o fechamento bruto de 02/04/2014 passa de 15,56 para
# 16,56 (B3), e o multiplicador do provento de 0,99757 com data ex em 03/04/2014 muda; todo o
# histórico anterior à data ex é reescalado pela razão constante. Na VALE3, a P1 só corrigiu
# máxima e mínima de 2012, que não entram em nenhum cálculo deste módulo.
P1_ATIVO = "PETR4.SA"
P1_DATA = "2014-04-02"
P1_DATA_EX = "2014-04-03"
P1_PROVENTO = 0.99757
P1_FECHAMENTO_ORIGINAL = 15.56
P1_FECHAMENTO_B3 = 16.56
P1_VALOR_CORRIGIDO_CONHECIDO = 3.8986        # fechamento ajustado de 02/04/2014 na visão derivada


def razao_p1() -> float:
    return (1 - P1_PROVENTO / P1_FECHAMENTO_B3) / (1 - P1_PROVENTO / P1_FECHAMENTO_ORIGINAL)


def corrigir_p1(fechamento: pd.Series) -> pd.Series:
    """Fechamento ajustado da PETR4 com a correção P1; a série recebida não é alterada."""
    corrigido = fechamento.copy()
    data = pd.Timestamp(P1_DATA)
    if data not in corrigido.index:
        return corrigido
    fator_do_dia = corrigido.loc[data] / P1_FECHAMENTO_ORIGINAL
    antes = corrigido.index < pd.Timestamp(P1_DATA_EX)
    corrigido[antes] = corrigido[antes] * razao_p1()
    corrigido.loc[data] = P1_FECHAMENTO_B3 * fator_do_dia * razao_p1()
    return corrigido


def classificar(variacao: float) -> str:
    """
    Regime pela variação no fim da janela (DL1-K). A variação é arredondada a 10 casas antes
    da comparação, para que +10% exatos (0,10000000000000009 em ponto flutuante) sejam lateral.
    """
    variacao = round(float(variacao), 10)
    if variacao > LIMITE_VARIACAO:
        return "alta"
    if variacao < -LIMITE_VARIACAO:
        return "baixa"
    return "lateral"


def classificar_original(variacao: float, drawdown: float) -> str:
    """Definição da DL1-J, substituída pela DL1-K. Sem uso; mantida para auditoria."""
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
    volatilidade = float(janela.pct_change().dropna().std(ddof=1) * np.sqrt(PREGOES_ANO))
    return {
        "inicio": janela.index[0].date().isoformat(),
        "fim": janela.index[-1].date().isoformat(),
        "pregoes": pregoes,
        "variacao": variacao,
        "drawdown_maximo": drawdown,
        "volatilidade_anualizada": volatilidade,
        "regime": classificar(variacao),
    }


def fins_de_mes(fechamento: pd.Series, inicio: str = INICIO_CANDIDATAS, fim: str = FIM_CANDIDATAS) -> list:
    """Último pregão de cada mês no intervalo das candidatas."""
    datas = fechamento.index[(fechamento.index >= pd.Timestamp(inicio)) & (fechamento.index <= pd.Timestamp(fim))]
    return list(pd.Series(datas, index=datas).groupby([datas.year, datas.month]).max())


def contem(janela: dict, data: str) -> bool:
    return janela["inicio"] <= data <= janela["fim"]


def candidatas(fechamento: pd.Series, pregoes: int, excluir_datas=()) -> list:
    """Candidatas da célula; `excluir_datas` retira as que contêm alguma data (checagem de sensibilidade)."""
    todas = [m for m in (metricas_janela(fechamento, d, pregoes) for d in fins_de_mes(fechamento)) if m is not None]
    return [m for m in todas if not any(contem(m, d) for d in excluir_datas)]


def escolher(lista: list) -> dict | None:
    """Variação mais próxima da mediana da célula; em empate, a janela mais antiga."""
    if not lista:
        return None
    mediana = float(np.median([c["variacao"] for c in lista]))
    return min(lista, key=lambda c: (abs(c["variacao"] - mediana), c["fim"])) | {"mediana_da_celula": mediana,
                                                                             "candidatas_na_celula": len(lista)}


def selecionar(fechamentos: dict, excluir_datas=()) -> list:
    """Uma janela por ativo × regime × comprimento, na ordem declarada; célula sem candidata fica vazia."""
    casos = []
    for ativo in ATIVOS:
        for nome, pregoes in JANELAS.items():
            todas = candidatas(fechamentos[ativo], pregoes, excluir_datas)
            for regime in REGIMES:
                escolhida = escolher([c for c in todas if c["regime"] == regime])
                casos.append({"ativo": ativo, "janela": nome, "regime_alvo": regime,
                              "candidatas_no_comprimento": len(todas), "escolhida": escolhida})
    return casos


JANELA_GRAFICO = 504
CONTROLES = ("S01", "S05", "S07", "S11")      # DL1-L: dois por ativo, um de cada janela


def janela_grafico(fechamento: pd.Series) -> dict:
    """
    Recorte dos casos por gráfico (DL1-L): definido pelo ativo, não pelo recurso. São os 504
    pregões que terminam no último pregão antes da trava, e os quatro recursos do ativo usam
    esse mesmo recorte.
    """
    return metricas_janela(fechamento, fechamento.index[-1], JANELA_GRAFICO)
