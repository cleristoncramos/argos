"""Alinhamento das datas (condição 4) e expurgo externo e interno (condição 5)."""

import numpy as np
import pandas as pd
import pytest

from experiments.preditivo.amostras import construir_amostras, nomes_variaveis, realizadas_ate, validar_precos
from experiments.preditivo.divisoes import (
    FronteiraViolada,
    dividir_ano,
    divisoes_internas,
    primeira_data_avaliada,
    verificar_fronteira,
)
from experiments.preditivo.tests.auxiliares import precos_sinteticos


@pytest.fixture(scope="module")
def serie():
    return precos_sinteticos("2008-01-02", "2016-12-30")


@pytest.fixture(scope="module")
def amostras(serie):
    return construir_amostras(serie)


def test_datas_de_cada_amostra_seguem_o_calendario(serie, amostras):
    datas = list(serie["Date"])
    posicao = {d: i for i, d in enumerate(datas)}
    com_alvo = amostras.dropna(subset=["label_end_date"])
    for _, linha in com_alvo.sample(50, random_state=1).iterrows():
        i = posicao[linha["decision_date"]]
        assert linha["entry_date"] == datas[i + 1]
        assert linha["label_end_date"] == datas[i + 21]


def test_alvo_e_o_retorno_entre_a_entrada_e_a_saida(serie, amostras):
    preco = serie.set_index("Date")["Close"]
    linha = amostras.dropna(subset=["y"]).iloc[100]
    esperado = preco[linha["label_end_date"]] / preco[linha["entry_date"]] - 1
    assert linha["y"] == pytest.approx(esperado, rel=1e-12)


def test_ultimas_amostras_ficam_sem_alvo(serie, amostras):
    ultimas = amostras.tail(21)
    assert ultimas["label_end_date"].isna().all() and ultimas["y"].isna().all()
    assert amostras["label_end_date"].dropna().max() == serie["Date"].max()
    assert not realizadas_ate(amostras, serie["Date"].max()).iloc[-1]


def test_variaveis_nao_usam_informacao_futura(serie):
    completa = construir_amostras(serie)
    corte = serie["Date"].iloc[1500]
    truncada = construir_amostras(serie[serie["Date"] <= corte])
    nomes = nomes_variaveis(completa)
    a = completa.set_index("decision_date").loc[truncada["decision_date"], nomes]
    b = truncada.set_index("decision_date")[nomes]
    np.testing.assert_allclose(a.to_numpy(), b.to_numpy(), rtol=1e-10, atol=1e-12)


def test_aquecimento_sai_e_nada_e_preenchido(amostras):
    nomes = nomes_variaveis(amostras)
    assert np.isfinite(amostras[nomes].to_numpy()).all()
    assert {"ret_20", "ret_60", "dist_pico_252", "atr_over_close"} <= set(nomes)


def test_precos_invalidos_sao_recusados(serie):
    with pytest.raises(ValueError):
        validar_precos(serie.drop(columns=["High"]))
    ruim = serie.copy()
    ruim.loc[5, "Low"] = -1.0
    with pytest.raises(ValueError):
        validar_precos(ruim)
    with pytest.raises(ValueError):
        validar_precos(pd.concat([serie.head(3), serie.head(1)]))


def test_embargo_exclui_os_primeiros_20_pregoes(serie, amostras):
    divisao = dividir_ano(amostras, serie["Date"], 2014)
    pregoes_2014 = serie[serie["Date"].dt.year == 2014]["Date"].reset_index(drop=True)
    assert divisao.primeira_data == pregoes_2014[20]
    avaliadas = amostras.iloc[divisao.avaliacao]["decision_date"]
    assert avaliadas.min() == pregoes_2014[20] and avaliadas.max() <= pregoes_2014.iloc[-1]


def test_expurgo_externo_pelas_datas(serie, amostras):
    for ano in (2014, 2015, 2016):
        divisao = dividir_ano(amostras, serie["Date"], ano)
        treino = amostras.iloc[divisao.treino]
        assert (treino["label_end_date"] < divisao.primeira_data).all()
        assert (treino["decision_date"] < divisao.primeira_data).all()
        # Nenhuma amostra que alcança a avaliação sobrou no treino.
        alcancam = amostras[(amostras["decision_date"] < divisao.primeira_data)
                            & (amostras["label_end_date"] >= divisao.primeira_data)]
        assert not set(alcancam.index) & set(treino.index)


def test_expurgo_nas_divisoes_internas(serie, amostras):
    externa = dividir_ano(amostras, serie["Date"], 2016)
    internas = divisoes_internas(amostras, serie["Date"], externa.treino, externa.primeira_data, 3)
    assert [d.ano for d in internas] == [2013, 2014, 2015]
    for d in internas:
        assert (amostras.iloc[d.treino]["label_end_date"] < d.primeira_data).all()
        assert set(d.treino) <= set(externa.treino) and set(d.avaliacao) <= set(externa.treino)
        assert amostras.iloc[d.avaliacao]["decision_date"].min() == primeira_data_avaliada(serie["Date"], d.ano)


def test_fronteira_violada_interrompe(amostras):
    primeira = pd.Timestamp("2014-03-03")
    vazamento = np.flatnonzero((amostras["decision_date"] < primeira).to_numpy())
    with pytest.raises(FronteiraViolada):
        verificar_fronteira(amostras, vazamento, primeira)


def test_limite_de_avaliacao_corta_o_periodo_final(serie, amostras):
    divisao = dividir_ano(amostras, serie["Date"], 2016, limite_avaliacao="2016-06-01")
    assert amostras.iloc[divisao.avaliacao]["decision_date"].max() < pd.Timestamp("2016-06-01")
