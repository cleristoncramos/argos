"""
Coleta, congelamento e leitura dos dados do piloto (protocolo, seções 3 e 8.3).

- preços diários com abertura, máxima, mínima e fechamento ajustados pelo mesmo
  fator (yfinance, auto_adjust=True);
- série para triagem de eventos (auto_adjust=False): fechamento e fechamento ajustado;
- CDI diário, série SGS 12 do Banco Central, em % ao dia, convertido para decimal.
Cada arquivo entra no manifesto com hash SHA-256. A leitura confere os hashes.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import timedelta
from pathlib import Path

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
    colunas = [c for c in ("Date", "Close", "Adj Close", "Dividends", "Stock Splits") if c in bruto.columns]
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


def triagem_eventos(bruto: pd.DataFrame, limiar: float = LIMIAR_TRIAGEM) -> list[dict]:
    """
    Datas em que o retorno diário com ajuste difere do sem ajuste por mais de `limiar`.
    É só triagem: cada data é investigada e documentada. No yfinance, o "Close" sem
    ajuste já vem corrigido por desdobramentos; a diferença aponta sobretudo proventos.
    """
    if "Adj Close" not in bruto.columns:
        return []
    serie = bruto.sort_values("Date")
    diferenca = serie["Adj Close"].pct_change() - serie["Close"].pct_change()
    marcadas = serie.loc[diferenca.abs() > limiar]
    eventos = []
    for _, linha in marcadas.iterrows():
        eventos.append({
            "data": linha["Date"].date().isoformat(),
            "diferenca": float(diferenca.loc[linha.name]),
            "provento_na_fonte": float(linha.get("Dividends", 0.0) or 0.0),
            "desdobramento_na_fonte": float(linha.get("Stock Splits", 0.0) or 0.0),
            "investigacao": "pendente",
        })
    return eventos


def inconsistencias_ohlc(ajustado: pd.DataFrame, tolerancia: float = 1e-7) -> list[dict]:
    """
    Datas em que abertura ou fechamento ficam fora da faixa entre mínima e máxima.
    São registradas para investigação, sem correção automática (protocolo, seções 3 e 10).
    """
    alto = ajustado["High"] * (1 + tolerancia)
    baixo = ajustado["Low"] * (1 - tolerancia)
    fora = ((ajustado["Close"] > alto) | (ajustado["Close"] < baixo)
            | (ajustado["Open"] > alto) | (ajustado["Open"] < baixo) | (ajustado["Low"] > ajustado["High"]))
    return [
        {"data": linha["Date"].date().isoformat(), "abertura": float(linha["Open"]), "maxima": float(linha["High"]),
         "minima": float(linha["Low"]), "fechamento": float(linha["Close"]), "investigacao": "pendente"}
        for _, linha in ajustado.loc[fora].iterrows()
    ]


def coletar_e_congelar(ativos=ATIVOS) -> dict:
    if MANIFESTO.exists():
        raise FileExistsError(f"Já existe um manifesto em {MANIFESTO}. Os dados congelados não são sobrescritos.")
    DADOS.mkdir(parents=True, exist_ok=True)
    arquivos, triagem, ohlc = {}, {}, {}
    for ativo in ativos:
        ajustado, bruto = coletar_precos(ativo)
        for tipo, df in (("ajustado", ajustado), ("triagem", bruto)):
            caminho = _arquivo(ativo, tipo)
            df.to_csv(caminho, index=False, date_format="%Y-%m-%d")
            arquivos[caminho.name] = _descrever(caminho, df["Date"])
        triagem[ativo] = triagem_eventos(bruto)
        ohlc[ativo] = inconsistencias_ohlc(ajustado)
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
            "triagem": "Yahoo Finance via yfinance; auto_adjust=False (Close já corrigido por desdobramentos; Adj Close)",
            "cdi": "Banco Central do Brasil, SGS 12 (CDI diário, % ao dia; coluna taxa em decimal)",
        },
        "parametros": {"inicio": INICIO_COLETA, "data_corte": DATA_CORTE, "ativos": list(ativos)},
        "natureza": "Reconstrução da fonte na data da coleta, com os ajustes conhecidos nesse momento",
        "arquivos": arquivos,
        "triagem_eventos": triagem,
        "inconsistencias_ohlc": ohlc,
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
