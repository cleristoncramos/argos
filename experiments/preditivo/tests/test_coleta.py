"""Coleta com fontes simuladas: snapshot identificado, sem sobrescrita e com hashes conferidos."""

import json

import numpy as np
import pandas as pd
import pytest

from experiments.preditivo.dados import carregar, coletar_e_congelar, conferir_serie, ler_ponteiro
from experiments.preditivo.tests.auxiliares import precos_sinteticos


def _fontes(com_problema=False):
    def precos(ativo):
        ajustado = precos_sinteticos("2008-01-02", "2009-06-30", semente=len(ativo))
        bruto = ajustado.assign(Close=ajustado["Close"] * 4.0, Open=ajustado["Open"] * 4.0,
                                High=ajustado["High"] * 4.0, Low=ajustado["Low"] * 4.0,
                                **{"Adj Close": ajustado["Close"], "Dividends": 0.0, "Stock Splits": 0.0})
        if com_problema:
            bruto.loc[10, "Close"] = bruto.loc[10, "Low"] * 0.9   # fechamento abaixo da mínima na base bruta
        return ajustado, bruto

    def cdi():
        return [{"data": d.strftime("%d/%m/%Y"), "valor": "0.041063"} for d in pd.bdate_range("2008-01-02", "2009-06-30")]
    return precos, cdi


@pytest.fixture
def pastas(tmp_path):
    return tmp_path / "dados", tmp_path / "snapshot.json"


def test_coleta_cria_snapshot_identificado_e_le_com_hashes(pastas):
    dados, ponteiro = pastas
    precos, cdi = _fontes()
    manifesto = coletar_e_congelar(("AAA.SA",), pasta=dados, ponteiro=ponteiro, buscar_precos=precos, buscar_cdi=cdi)
    assert manifesto["snapshot"].startswith("snap-") and manifesto["snapshot"].endswith("-01")
    assert manifesto["situacao"]["snapshot"] == "coletado e congelado"
    assert manifesto["situacao"]["verificacao_integridade"] == "sem pendência registrada"
    assert {"python", "pandas", "numpy", "yfinance", "scikit-learn"} <= set(manifesto["versoes"])
    assert manifesto["parametros"]["sgs"]["unidade_original"] == "% ao dia"
    pasta = dados / manifesto["snapshot"]
    resposta = json.loads((pasta / "cdi_sgs12_resposta.json").read_text(encoding="utf-8"))
    assert resposta[0]["valor"] == "0.041063"                    # resposta original preservada
    _m, lidos, tabela = carregar(ponteiro, dados)
    assert tabela["taxa"].iloc[0] == pytest.approx(0.00041063)   # % ao dia → decimal
    assert list(lidos) == ["AAA.SA"]


def test_nao_sobrescreve_e_nova_tentativa_preserva_a_anterior(pastas):
    dados, ponteiro = pastas
    precos, cdi = _fontes()
    primeiro = coletar_e_congelar(("AAA.SA",), pasta=dados, ponteiro=ponteiro, buscar_precos=precos, buscar_cdi=cdi)
    with pytest.raises(FileExistsError):
        coletar_e_congelar(("AAA.SA",), pasta=dados, ponteiro=ponteiro, buscar_precos=precos, buscar_cdi=cdi)
    segundo = coletar_e_congelar(("AAA.SA",), motivo_nova_tentativa="falha técnica", pasta=dados,
                                 ponteiro=ponteiro, buscar_precos=precos, buscar_cdi=cdi)
    assert segundo["snapshot"].endswith("-02") and segundo["tentativa_anterior"] == primeiro["snapshot"]
    assert (dados / primeiro["snapshot"] / "manifest.json").exists()
    registro = ler_ponteiro(ponteiro)
    assert registro["vigente"] == segundo["snapshot"] and len(registro["snapshots"]) == 2


def test_arquivo_alterado_depois_da_coleta_e_recusado(pastas):
    dados, ponteiro = pastas
    precos, cdi = _fontes()
    manifesto = coletar_e_congelar(("AAA.SA",), pasta=dados, ponteiro=ponteiro, buscar_precos=precos, buscar_cdi=cdi)
    arquivo = dados / manifesto["snapshot"] / "AAA_SA_ajustado.csv"
    arquivo.write_text(arquivo.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="diferente do manifesto"):
        carregar(ponteiro, dados)


def test_pendencia_de_integridade_fica_registrada_sem_correcao(pastas):
    dados, ponteiro = pastas
    precos, cdi = _fontes(com_problema=True)
    manifesto = coletar_e_congelar(("AAA.SA",), pasta=dados, ponteiro=ponteiro, buscar_precos=precos, buscar_cdi=cdi)
    assert manifesto["situacao"]["verificacao_integridade"] == "com pendência"
    assert manifesto["situacao"]["elegibilidade_para_modelagem"] == "aguarda tratamento documentado"
    assert manifesto["verificacao_ohlc"]["AAA.SA"]["ocorrencias"][0]["falha_na_base_bruta"]
    bruto = pd.read_csv(dados / manifesto["snapshot"] / "AAA_SA_bruto.csv")
    assert bruto.loc[10, "Close"] < bruto.loc[10, "Low"]          # o dado da fonte não foi alterado


def test_conferencia_da_serie_aponta_repeticao_ordem_e_nao_finitos():
    df = pd.DataFrame({"Date": pd.to_datetime(["2020-01-02", "2020-01-02", "2020-01-01"]),
                       "Close": [1.0, np.nan, 2.0]})
    conferencia = conferir_serie(df, "Date", ["Close"])
    assert conferencia["datas_repetidas"] == ["2020-01-02"] and not conferencia["ordenada"]
    assert conferencia["valores_nao_finitos"] == 1 and conferencia["linhas"] == 3
