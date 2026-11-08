"""
Coleta, congelamento e leitura dos dados do piloto (protocolo, seções 3 e 8.3).

- preços diários com abertura, máxima, mínima e fechamento ajustados pelo mesmo
  fator (yfinance, auto_adjust=True);
- série bruta (auto_adjust=False): OHLC corrigidos por desdobramentos, Adj Close, proventos e desdobramentos;
- CDI diário, série SGS 12 do Banco Central, em % ao dia, convertido para decimal.
Cada arquivo entra no manifesto com hash SHA-256. A leitura confere os hashes.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from core.clock import now_brasilia
from experiments.preditivo.config import ATIVOS, DADOS, DATA_CORTE, INICIO_COLETA, MANIFESTO, PROTOCOLO

SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial={ini}&dataFinal={fim}"
LIMIAR_TRIAGEM = 0.01   # diferença diária de 1 ponto percentual


def sha256(caminho: Path) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def _arquivo(ativo: str, tipo: str) -> Path:
    return DADOS / f"{ativo.replace('.', '_')}_{tipo}.csv"


def coletar_precos(ativo: str, inicio: str = INICIO_COLETA, corte: str = DATA_CORTE) -> tuple[pd.DataFrame, pd.DataFrame]:
    import yfinance as yf

    fim = (pd.Timestamp(corte) + timedelta(days=1)).strftime("%Y-%m-%d")   # o fim do yfinance é exclusivo
    ticker = yf.Ticker(ativo)
    ajustado = ticker.history(start=inicio, end=fim, interval="1d", auto_adjust=True, actions=False).reset_index()
    bruto = ticker.history(start=inicio, end=fim, interval="1d", auto_adjust=False, actions=True).reset_index()
    for df in (ajustado, bruto):
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    ajustado = ajustado[["Date", "Open", "High", "Low", "Close"]].dropna(subset=["Close"])
    colunas = [c for c in ("Date", "Open", "High", "Low", "Close", "Adj Close", "Dividends", "Stock Splits")
               if c in bruto.columns]
    return ajustado, bruto[colunas]


def coletar_cdi(inicio: str = INICIO_COLETA, corte: str = DATA_CORTE) -> pd.DataFrame:
    """SGS 12 em blocos de até 5 anos (a API limita janelas longas de séries diárias)."""
    partes, atual, fim = [], pd.Timestamp(inicio), pd.Timestamp(corte)
    while atual <= fim:
        bloco_fim = min(atual + pd.DateOffset(years=5) - pd.Timedelta(days=1), fim)
        url = SGS_URL.format(ini=atual.strftime("%d/%m/%Y"), fim=bloco_fim.strftime("%d/%m/%Y"))
        pedido = urllib.request.Request(url, headers={"User-Agent": "argos-piloto-preditivo"})
        with urllib.request.urlopen(pedido, timeout=60) as resposta:
            partes.extend(json.loads(resposta.read().decode("utf-8")))
        atual = bloco_fim + pd.Timedelta(days=1)
    cdi = pd.DataFrame(partes)
    cdi["data"] = pd.to_datetime(cdi["data"], format="%d/%m/%Y")
    cdi["taxa_percentual_ao_dia"] = cdi["valor"].astype(float)
    cdi["taxa"] = cdi["taxa_percentual_ao_dia"] / 100.0     # % ao dia → decimal
    return cdi[["data", "taxa_percentual_ao_dia", "taxa"]].drop_duplicates("data").sort_values("data")


def triagem_proventos(bruto: pd.DataFrame, limiar: float = LIMIAR_TRIAGEM) -> list[dict]:
    """
    Triagem de diferenças entre retorno de preço e retorno ajustado por proventos.

    No yfinance, o "Close" sem ajuste já vem corrigido por desdobramentos, então esta
    comparação não detecta desdobramentos (eles vão para `desdobramentos_na_fonte`).
    É só triagem: cada data é investigada e documentada, sem atribuir causa pelo tamanho.
    """
    if "Adj Close" not in bruto.columns:
        return []
    serie = bruto.sort_values("Date")
    diferenca = serie["Adj Close"].pct_change() - serie["Close"].pct_change()
    marcadas = serie.loc[diferenca.abs() > limiar]
    return [
        {"data": linha["Date"].date().isoformat(),
         "diferenca": float(diferenca.loc[linha.name]),
         "provento_na_fonte": float(linha.get("Dividends", 0.0) or 0.0),
         "investigacao": "pendente"}
        for _, linha in marcadas.iterrows()
    ]


def desdobramentos_na_fonte(bruto: pd.DataFrame) -> list[dict]:
    """Eventos de desdobramento ou grupamento informados pela fonte, para auditoria."""
    if "Stock Splits" not in bruto.columns:
        return []
    eventos = bruto[bruto["Stock Splits"].fillna(0) != 0]
    return [{"data": linha["Date"].date().isoformat(), "fator": float(linha["Stock Splits"])}
            for _, linha in eventos.iterrows()]


def _fora_da_faixa(abertura, maxima, minima, fechamento, tolerancia):
    alto, baixo = maxima * (1 + tolerancia), minima * (1 - tolerancia)
    return (fechamento > alto) | (fechamento < baixo) | (abertura > alto) | (abertura < baixo) | (minima > maxima)


def verificar_ohlc(bruto: pd.DataFrame, ajustado: pd.DataFrame, tolerancia: float = 1e-7) -> dict:
    """
    Conferência da faixa mínima <= abertura, fechamento <= máxima em bases comparáveis:

    1. base bruta da fonte (todas as colunas só corrigidas por desdobramentos);
    2. base ajustada reconstruída com o fator a_t = Adj Close / Close aplicado às
       quatro colunas, comparada também com a série usada no piloto (auto_adjust=True).

    Ocorrências ficam "em investigação": nada é corrigido automaticamente.
    """
    b = bruto.sort_values("Date").reset_index(drop=True)
    fora_bruto = _fora_da_faixa(b["Open"], b["High"], b["Low"], b["Close"], tolerancia)
    fator = b["Adj Close"] / b["Close"]
    reconstruido = pd.DataFrame({"Date": b["Date"], "Open": b["Open"] * fator, "High": b["High"] * fator,
                                 "Low": b["Low"] * fator, "Close": b["Adj Close"]})
    fora_ajustado = _fora_da_faixa(reconstruido["Open"], reconstruido["High"], reconstruido["Low"],
                                   reconstruido["Close"], tolerancia)
    usada = ajustado.merge(reconstruido, on="Date", suffixes=("", "_rec"))
    diferenca = None
    if len(usada):
        diferenca = max(float((usada[c] - usada[f"{c}_rec"]).abs().div(usada[f"{c}_rec"]).max())
                        for c in ("Open", "High", "Low", "Close"))

    ocorrencias = []
    for i in np.flatnonzero((fora_bruto | fora_ajustado).to_numpy()):
        ocorrencias.append({
            "data": b.loc[i, "Date"].date().isoformat(),
            "base_bruta": {k: float(b.loc[i, k]) for k in ("Open", "High", "Low", "Close")},
            "falha_na_base_bruta": bool(fora_bruto.iloc[i]),
            "falha_na_base_ajustada": bool(fora_ajustado.iloc[i]),
            "situacao": "em investigação",
            "observacao": ("Faixa mínima/máxima violada na mesma base de ajuste; investigar a integridade "
                           "antes de classificar como erro da fonte."),
        })
    return {"ocorrencias": ocorrencias, "maior_diferenca_relativa_usada_vs_reconstruida": diferenca}


def variacoes_do_fator(bruto: pd.DataFrame, tolerancia: float = 1e-6) -> list[dict]:
    """
    Datas em que o fator Adj Close / Close muda sem provento nem desdobramento na data.
    O fator só deveria mudar em datas de evento; mudança sem evento vai para investigação.
    """
    b = bruto.sort_values("Date").reset_index(drop=True)
    fator = b["Adj Close"] / b["Close"]
    variacao = fator / fator.shift(1) - 1
    proventos = b["Dividends"].fillna(0) if "Dividends" in b.columns else 0
    desdobramentos = b["Stock Splits"].fillna(0) if "Stock Splits" in b.columns else 0
    sem_evento = (variacao.abs() > tolerancia) & (proventos == 0) & (desdobramentos == 0)
    return [{"data": b.loc[i, "Date"].date().isoformat(), "variacao_do_fator": float(variacao.iloc[i]),
             "situacao": "em investigação"} for i in np.flatnonzero(sem_evento.to_numpy())]


def coletar_e_congelar(ativos=ATIVOS) -> dict:
    if MANIFESTO.exists():
        raise FileExistsError(f"Já existe um manifesto em {MANIFESTO}. Os dados congelados não são sobrescritos.")
    DADOS.mkdir(parents=True, exist_ok=True)
    arquivos, proventos, desdobramentos, ohlc, fatores = {}, {}, {}, {}, {}
    for ativo in ativos:
        ajustado, bruto = coletar_precos(ativo)
        for tipo, df in (("ajustado", ajustado), ("bruto", bruto)):
            caminho = _arquivo(ativo, tipo)
            df.to_csv(caminho, index=False, date_format="%Y-%m-%d")
            arquivos[caminho.name] = _descrever(caminho, df["Date"])
        proventos[ativo] = triagem_proventos(bruto)
        desdobramentos[ativo] = desdobramentos_na_fonte(bruto)
        ohlc[ativo] = verificar_ohlc(bruto, ajustado)
        fatores[ativo] = variacoes_do_fator(bruto)
    cdi = coletar_cdi()
    caminho = DADOS / "cdi_sgs12.csv"
    cdi.to_csv(caminho, index=False, date_format="%Y-%m-%d")
    arquivos[caminho.name] = _descrever(caminho, cdi["data"])

    manifesto = {
        "esquema": 1,
        "coletado_em": now_brasilia().isoformat(timespec="seconds"),
        "protocolo": {"arquivo": "docs/preditivo/protocolo_piloto_v1.md", "sha256": sha256(PROTOCOLO)},
        "fontes": {
            "precos": "Yahoo Finance via yfinance; auto_adjust=True (abertura, máxima, mínima e fechamento ajustados)",
            "bruto": ("Yahoo Finance via yfinance; auto_adjust=False (OHLC corrigidos por desdobramentos; "
                      "Adj Close; proventos e desdobramentos informados)"),
            "cdi": "Banco Central do Brasil, SGS 12 (CDI diário, % ao dia; coluna taxa em decimal)",
        },
        "parametros": {"inicio": INICIO_COLETA, "data_corte": DATA_CORTE, "ativos": list(ativos)},
        "natureza": "Reconstrução da fonte na data da coleta, com os ajustes conhecidos nesse momento",
        "arquivos": arquivos,
        "triagem_retorno_preco_vs_ajustado_por_proventos": proventos,
        "desdobramentos_na_fonte": desdobramentos,
        "verificacao_ohlc": ohlc,
        "variacoes_do_fator_sem_evento": fatores,
    }
    MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifesto


def _descrever(caminho: Path, datas: pd.Series) -> dict:
    datas = pd.to_datetime(datas)
    return {"sha256": sha256(caminho), "linhas": int(len(datas)),
            "inicio": datas.min().date().isoformat(), "fim": datas.max().date().isoformat()}


def carregar(manifesto_path: Path = MANIFESTO) -> tuple[dict, dict[str, pd.DataFrame], pd.DataFrame]:
    """Lê os dados congelados conferindo cada hash. Devolve (manifesto, preços por ativo, CDI)."""
    manifesto = json.loads(Path(manifesto_path).read_text(encoding="utf-8"))
    pasta = Path(manifesto_path).parent
    for nome, info in manifesto["arquivos"].items():
        atual = sha256(pasta / nome)
        if atual != info["sha256"]:
            raise ValueError(f"Hash de {nome} diferente do manifesto: os dados congelados mudaram.")
    precos = {}
    for ativo in manifesto["parametros"]["ativos"]:
        df = pd.read_csv(pasta / f"{ativo.replace('.', '_')}_ajustado.csv", parse_dates=["Date"])
        precos[ativo] = df
    cdi = pd.read_csv(pasta / "cdi_sgs12.csv", parse_dates=["data"])
    return manifesto, precos, cdi
