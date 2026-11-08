"""Política de qualidade: campos tratados na memória, por dependência, sem comprimir o calendário."""

import numpy as np
import pandas as pd
import pytest

from experiments.preditivo.amostras import construir_amostras, nomes_variaveis
from experiments.preditivo.divisoes import treino_ate
from experiments.preditivo.qualidade import (
    REAQUECIMENTO,
    PoliticaPendente,
    aplicar_aos_precos,
    exigir_decidida,
)
from experiments.preditivo.tests.auxiliares import precos_sinteticos


@pytest.fixture(scope="module")
def serie():
    return precos_sinteticos("2008-01-02", "2013-12-31")


def _entrada(data, campos, tratamento="invalidar", valores=None):
    return {"ativo": "X", "data": data, "campos": campos, "tratamento": tratamento, "decisao": "decidida",
            "fonte": {"valores": valores or {}}}


def test_snapshot_nao_e_alterado_e_o_calendario_fica_igual(serie):
    data = serie["Date"].iloc[900]
    original = serie.copy()
    derivada = aplicar_aos_precos(serie, [_entrada(data, ["Close"])])
    pd.testing.assert_frame_equal(serie, original)                     # entrada intocada
    assert len(derivada) == len(serie) and derivada["Date"].equals(serie["Date"])
    assert np.isnan(derivada.loc[900, "Close"])


def test_fechamento_invalidado_afeta_variaveis_e_alvos_sem_deslocar_datas(serie):
    data = serie["Date"].iloc[900]
    base = construir_amostras(serie).set_index("decision_date")
    tratada = construir_amostras(serie, politica=[_entrada(data, ["Close"])]).set_index("decision_date")
    datas = list(serie["Date"])
    # Sem variáveis válidas: a própria data e as janelas que a incluem (até 252 pregões depois).
    assert data not in tratada.index and datas[900 + 251] not in tratada.index
    assert datas[900 + 252] in tratada.index
    # Alvos com entrada ou fim do alvo na data questionada ficam ausentes.
    assert np.isnan(tratada.loc[datas[900 - 1], "y"]) and np.isnan(tratada.loc[datas[900 - 21], "y"])
    assert tratada.loc[datas[900 - 22], "y"] == pytest.approx(base.loc[datas[900 - 22], "y"])
    # Calendário preservado: entradas e fins de alvo iguais nas amostras que sobram.
    comuns = base.index.intersection(tratada.index)
    assert base.loc[comuns, ["entry_date", "label_end_date"]].equals(tratada.loc[comuns, ["entry_date", "label_end_date"]])


def test_variaveis_recursivas_reaquecem_e_as_de_janela_finita_voltam_iguais(serie):
    data = serie["Date"].iloc[900]
    base = construir_amostras(serie).set_index("decision_date")
    tratada = construir_amostras(serie, politica=[_entrada(data, ["High"])]).set_index("decision_date")
    datas = list(serie["Date"])
    # Só o ATR usa a máxima: ele fica ausente na janela de reaquecimento e o resto não muda.
    dentro = [d for d in datas[900:900 + REAQUECIMENTO + 1] if d in base.index]
    assert not set(dentro) & set(tratada.index)
    depois = datas[900 + REAQUECIMENTO + 5]
    outras = [c for c in nomes_variaveis(base) if not c.startswith("atr_over_close")]
    pd.testing.assert_series_equal(base.loc[depois, outras], tratada.loc[depois, outras], check_names=False)
    assert tratada.loc[depois, "atr_over_close"] == pytest.approx(base.loc[depois, "atr_over_close"], rel=0.05)


def test_abertura_questionada_nao_afeta_nenhum_calculo(serie):
    # A abertura não entra nas variáveis, no alvo nem na execução deste piloto.
    data = serie["Date"].iloc[900]
    base = construir_amostras(serie)
    tratada = construir_amostras(serie, politica=[_entrada(data, ["Open"])])
    pd.testing.assert_frame_equal(base, tratada)


def test_substituicao_usa_o_fator_de_ajuste_da_data(serie):
    data = serie["Date"].iloc[900]
    bruto = serie.assign(**{"Adj Close": serie["Close"] * 0.25})
    derivada = aplicar_aos_precos(serie, [_entrada(data, ["Close"], "substituir_por_fonte_verificada",
                                                   {"Close": 16.56})], bruto)
    assert derivada.loc[900, "Close"] == pytest.approx(16.56 * 0.25)


def test_politica_pendente_e_recusada():
    with pytest.raises(PoliticaPendente):
        exigir_decidida({"entradas": [{"ativo": "X", "data": "2014-04-02", "tratamento": None, "decisao": "pendente"}]})
    exigir_decidida({"entradas": [_entrada("2014-04-02", ["Close"])]})


def test_alvo_invalidado_nao_entra_no_treino(serie):
    data = serie["Date"].iloc[900]
    tratada = construir_amostras(serie, politica=[_entrada(data, ["Close"])])
    treino = tratada.iloc[treino_ate(tratada, serie["Date"].iloc[1300])]
    assert treino["y"].notna().all()
