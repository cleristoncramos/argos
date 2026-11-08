"""
Coleta, congelamento e leitura dos dados do piloto (protocolo, seções 3 e 8.3).

Cada coleta gera um snapshot com identificador próprio (`snap-AAAAMMDD-NN`) numa
pasta nova de `dados/`; nada é sobrescrito. O snapshot guarda exatamente o que as
fontes retornaram, sem correções:
- preços diários com abertura, máxima, mínima e fechamento ajustados pelo mesmo
  fator (yfinance, auto_adjust=True);
- série bruta (auto_adjust=False): OHLC corrigidos por desdobramentos, Adj Close,
  proventos e desdobramentos informados;
- CDI diário, série SGS 12 do Banco Central: a resposta original (% ao dia) e uma
  tabela com a conversão para decimal.
O manifesto registra parâmetros, versões, commit, hashes, conferências das séries
e as verificações de integridade. `snapshot.json` (versionado) aponta o snapshot vigente.
"""

from __future__ import annotations

import json
import urllib.request
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from core.clock import now_brasilia
from experiments.preditivo import config
from experiments.preditivo.util import git, sha256, versoes

SGS_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados?formato=json&dataInicial={ini}&dataFinal={fim}"
LIMIAR_TRIAGEM = 0.01   # diferença diária de 1 ponto percentual
PARAMETROS_YFINANCE = {
    "ajustado": {"interval": "1d", "auto_adjust": True, "actions": False},
    "bruto": {"interval": "1d", "auto_adjust": False, "actions": True},
}


# ---------- coleta (rede)

def _fim_exclusivo(corte: str) -> str:
    return (pd.Timestamp(corte) + timedelta(days=1)).strftime("%Y-%m-%d")   # o fim do yfinance é exclusivo


def coletar_precos(ativo: str, inicio: str = config.INICIO_COLETA,
                   corte: str = config.DATA_CORTE) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devolve (ajustado, bruto) como a fonte retornou, só com a data normalizada para o dia."""
    import yfinance as yf

    ticker = yf.Ticker(ativo)
    fim = _fim_exclusivo(corte)
    ajustado = ticker.history(start=inicio, end=fim, **PARAMETROS_YFINANCE["ajustado"]).reset_index()
    bruto = ticker.history(start=inicio, end=fim, **PARAMETROS_YFINANCE["bruto"]).reset_index()
    for df in (ajustado, bruto):
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
    ajustado = ajustado[[c for c in ("Date", "Open", "High", "Low", "Close") if c in ajustado.columns]]
    bruto = bruto[[c for c in ("Date", "Open", "High", "Low", "Close", "Adj Close", "Dividends", "Stock Splits")
                   if c in bruto.columns]]
    return ajustado, bruto


def coletar_cdi(inicio: str = config.INICIO_COLETA, corte: str = config.DATA_CORTE) -> list[dict]:
    """Resposta original da SGS 12, em blocos de até 5 anos (a API limita janelas longas)."""
    partes, atual, fim = [], pd.Timestamp(inicio), pd.Timestamp(corte)
    while atual <= fim:
        bloco_fim = min(atual + pd.DateOffset(years=5) - pd.Timedelta(days=1), fim)
        url = SGS_URL.format(ini=atual.strftime("%d/%m/%Y"), fim=bloco_fim.strftime("%d/%m/%Y"))
        pedido = urllib.request.Request(url, headers={"User-Agent": "argos-piloto-preditivo"})
        with urllib.request.urlopen(pedido, timeout=60) as resposta:
            partes.extend(json.loads(resposta.read().decode("utf-8")))
        atual = bloco_fim + pd.Timedelta(days=1)
    return partes


def tabela_cdi(resposta: list[dict]) -> pd.DataFrame:
    """Conversão da resposta original: % ao dia → decimal, sem remover nem reordenar linhas."""
    cdi = pd.DataFrame(resposta)
    cdi["data"] = pd.to_datetime(cdi["data"], format="%d/%m/%Y")
    cdi["taxa_percentual_ao_dia"] = cdi["valor"].astype(float)
    cdi["taxa"] = cdi["taxa_percentual_ao_dia"] / 100.0
    return cdi[["data", "taxa_percentual_ao_dia", "taxa"]]


# ---------- conferências (sem correção)

def conferir_serie(df: pd.DataFrame, coluna_data: str, colunas_valor) -> dict:
    """Cobertura, contagem, ordenação, datas repetidas e valores não finitos."""
    datas = pd.to_datetime(df[coluna_data])
    valores = df[list(colunas_valor)].to_numpy(dtype=float)
    nao_finitos = ~np.isfinite(valores)
    linhas_nao_finitas = df.loc[nao_finitos.any(axis=1), coluna_data]
    return {
        "linhas": int(len(df)),
        "inicio": datas.min().date().isoformat() if len(df) else None,
        "fim": datas.max().date().isoformat() if len(df) else None,
        "ordenada": bool(datas.is_monotonic_increasing),
        "datas_repetidas": [d.date().isoformat() for d in datas[datas.duplicated()]],
        "valores_nao_finitos": int(nao_finitos.sum()),
        "datas_com_nao_finitos": [pd.Timestamp(d).date().isoformat() for d in linhas_nao_finitas],
    }


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


# ---------- snapshots

def ler_ponteiro(ponteiro: Path = config.SNAPSHOT) -> dict:
    if not Path(ponteiro).exists():
        return {"vigente": None, "snapshots": []}
    return json.loads(Path(ponteiro).read_text(encoding="utf-8"))


def proximo_identificador(pasta: Path = config.DADOS, data=None) -> str:
    dia = (data or now_brasilia()).strftime("%Y%m%d")
    n = 1
    while (Path(pasta) / f"snap-{dia}-{n:02d}").exists():
        n += 1
    return f"snap-{dia}-{n:02d}"


def _nome(ativo: str, tipo: str) -> str:
    return f"{ativo.replace('.', '_')}_{tipo}.csv"


def coletar_e_congelar(ativos=config.ATIVOS, motivo_nova_tentativa: str | None = None,
                       pasta: Path = config.DADOS, ponteiro: Path = config.SNAPSHOT,
                       buscar_precos=coletar_precos, buscar_cdi=coletar_cdi) -> dict:
    """
    Cria um snapshot novo. Se já houver um vigente, só prossegue com `motivo_nova_tentativa`
    (por exemplo, falha técnica): a tentativa anterior é preservada e registrada.
    """
    registro = ler_ponteiro(ponteiro)
    if registro["vigente"] and not motivo_nova_tentativa:
        raise FileExistsError(f"Já existe o snapshot vigente {registro['vigente']}. Uma nova coleta exige "
                              "um motivo registrado (--nova-tentativa) e não apaga a anterior.")
    identificador = proximo_identificador(pasta)
    destino = Path(pasta) / identificador
    destino.mkdir(parents=True, exist_ok=False)

    arquivos, series, proventos, desdobramentos, ohlc, fatores = {}, {}, {}, {}, {}, {}
    for ativo in ativos:
        ajustado, bruto = buscar_precos(ativo)
        for tipo, df in (("ajustado", ajustado), ("bruto", bruto)):
            nome = _nome(ativo, tipo)
            df.to_csv(destino / nome, index=False, date_format="%Y-%m-%d")
            arquivos[nome] = {"sha256": sha256(destino / nome)}
            colunas = [c for c in ("Open", "High", "Low", "Close", "Adj Close") if c in df.columns]
            series[nome] = conferir_serie(df, "Date", colunas)
        proventos[ativo] = triagem_proventos(bruto)
        desdobramentos[ativo] = desdobramentos_na_fonte(bruto)
        ohlc[ativo] = verificar_ohlc(bruto, ajustado)
        fatores[ativo] = variacoes_do_fator(bruto)

    resposta = buscar_cdi()
    (destino / "cdi_sgs12_resposta.json").write_text(json.dumps(resposta, ensure_ascii=False), encoding="utf-8")
    arquivos["cdi_sgs12_resposta.json"] = {"sha256": sha256(destino / "cdi_sgs12_resposta.json")}
    cdi = tabela_cdi(resposta)
    cdi.to_csv(destino / "cdi_sgs12.csv", index=False, date_format="%Y-%m-%d")
    arquivos["cdi_sgs12.csv"] = {"sha256": sha256(destino / "cdi_sgs12.csv")}
    series["cdi_sgs12.csv"] = conferir_serie(cdi, "data", ["taxa_percentual_ao_dia", "taxa"])

    pendencias = (any(o["ocorrencias"] for o in ohlc.values()) or any(fatores.values())
                  or any(s["datas_repetidas"] or s["valores_nao_finitos"] or not s["ordenada"]
                         for s in series.values()))
    manifesto = {
        "esquema": 2,
        "snapshot": identificador,
        "coletado_em": now_brasilia().isoformat(timespec="seconds"),
        "data_corte": config.DATA_CORTE,
        "implementacao": {"commit": git("rev-parse", "HEAD"), "arvore_alterada": bool(git("status", "--porcelain"))},
        "versoes": versoes(),
        "protocolo": {"arquivo": "docs/preditivo/protocolo_piloto_v1.md", "sha256": sha256(config.PROTOCOLO)},
        "parametros": {
            "ativos": list(ativos), "inicio": config.INICIO_COLETA, "data_corte": config.DATA_CORTE,
            "yfinance": {tipo: {**p, "start": config.INICIO_COLETA, "end_exclusivo": _fim_exclusivo(config.DATA_CORTE)}
                         for tipo, p in PARAMETROS_YFINANCE.items()},
            "sgs": {"serie": 12, "unidade_original": "% ao dia", "blocos_anos": 5},
        },
        "fontes": {
            "ajustado": "Yahoo Finance via yfinance, auto_adjust=True",
            "bruto": "Yahoo Finance via yfinance, auto_adjust=False (OHLC corrigidos por desdobramentos; Adj Close; eventos)",
            "cdi": "Banco Central do Brasil, SGS 12; resposta original e conversão para decimal",
        },
        "natureza": "Reconstrução da fonte na data da coleta, com os ajustes conhecidos nesse momento; sem correções",
        "situacao": {
            "snapshot": "coletado e congelado",
            "verificacao_integridade": "com pendência" if pendencias else "sem pendência registrada",
            "elegibilidade_para_modelagem": "aguarda tratamento documentado" if pendencias else "aguarda conferência",
        },
        "arquivos": arquivos,
        "conferencia_das_series": series,
        "triagem_retorno_preco_vs_ajustado_por_proventos": proventos,
        "desdobramentos_na_fonte": desdobramentos,
        "verificacao_ohlc": ohlc,
        "variacoes_do_fator_sem_evento": fatores,
        "tentativa_anterior": registro["vigente"],
        "motivo_nova_tentativa": motivo_nova_tentativa,
    }
    (destino / "manifest.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")

    registro["snapshots"].append({"id": identificador, "coletado_em": manifesto["coletado_em"],
                                  "manifesto_sha256": sha256(destino / "manifest.json"),
                                  "situacao": manifesto["situacao"], "motivo_nova_tentativa": motivo_nova_tentativa})
    registro["vigente"] = identificador
    Path(ponteiro).write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifesto


def caminho_manifesto(ponteiro: Path = config.SNAPSHOT, pasta: Path = config.DADOS) -> Path | None:
    vigente = ler_ponteiro(ponteiro)["vigente"]
    return Path(pasta) / vigente / "manifest.json" if vigente else None


def carregar(ponteiro: Path = config.SNAPSHOT, pasta: Path = config.DADOS):
    """Lê o snapshot vigente conferindo cada hash. Devolve (manifesto, preços por ativo, CDI)."""
    manifesto_path = caminho_manifesto(ponteiro, pasta)
    if manifesto_path is None:
        raise FileNotFoundError("Nenhum snapshot vigente: rode a coleta oficial.")
    registro = ler_ponteiro(ponteiro)
    esperado = next(s["manifesto_sha256"] for s in registro["snapshots"] if s["id"] == registro["vigente"])
    if sha256(manifesto_path) != esperado:
        raise ValueError("O manifesto do snapshot vigente mudou depois da coleta.")
    manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
    for nome, info in manifesto["arquivos"].items():
        if sha256(manifesto_path.parent / nome) != info["sha256"]:
            raise ValueError(f"Hash de {nome} diferente do manifesto: os dados congelados mudaram.")
    precos = {ativo: pd.read_csv(manifesto_path.parent / _nome(ativo, "ajustado"), parse_dates=["Date"])
              for ativo in manifesto["parametros"]["ativos"]}
    cdi = pd.read_csv(manifesto_path.parent / "cdi_sgs12.csv", parse_dates=["data"])
    return manifesto, precos, cdi


def carregar_brutos(ponteiro: Path = config.SNAPSHOT, pasta: Path = config.DADOS) -> dict[str, pd.DataFrame]:
    """Séries brutas do snapshot vigente (hashes conferidos por `carregar`), para o fator de ajuste."""
    manifesto, _precos, _cdi = carregar(ponteiro, pasta)
    base = caminho_manifesto(ponteiro, pasta).parent
    return {ativo: pd.read_csv(base / _nome(ativo, "bruto"), parse_dates=["Date"])
            for ativo in manifesto["parametros"]["ativos"]}
