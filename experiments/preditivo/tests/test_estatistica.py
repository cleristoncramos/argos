"""Rotina do Diebold-Mariano e casos não calculáveis (nota metodológica, seção 7)."""

import math

import numpy as np
import pandas as pd
import pytest

from experiments.preditivo.estatistica import (
    NAO_CALCULAVEL,
    OK,
    _teste_media,
    acuracia_balanceada,
    clark_west,
    diebold_mariano,
    erros,
    phi,
    r2_fora_da_amostra,
    variancia_newey_west,
)


def _previsoes(y, yhat, inicio="2022-02-01"):
    datas = pd.bdate_range(inicio, periods=len(y))
    return pd.DataFrame({"decision_date": datas, "y": y, "yhat": yhat}), datas


# ---------- rotina matemática (amostras pequenas, sem o mínimo operacional)

def test_exemplo_conferido_a_mao():
    # d = [1, 2, 3, 4], L = 1: d̄ = 2,5; γ0 = 1,25; γ1 = 0,3125; w1 = 0,5; V̂ = 1,5625; DM = 4,0
    d = np.array([1.0, 2.0, 3.0, 4.0])
    assert variancia_newey_west(d, 1) == pytest.approx(1.5625)
    resultado = _teste_media(d, 1, 0.10, minimo=None)
    assert resultado.status == OK
    assert resultado.estatistica == pytest.approx(4.0)
    assert resultado.p == pytest.approx(1 - phi(4.0)) and resultado.atende


def test_convencao_de_sinal():
    rng = np.random.default_rng(3)
    y = rng.normal(0, 0.05, 60)
    perfeitas, datas = _previsoes(y, y)
    assert diebold_mariano(perfeitas, datas, minimo=None).media > 0
    nulas, datas = _previsoes(y, np.zeros_like(y))
    resultado = diebold_mariano(nulas, datas, minimo=None)
    assert resultado.status == NAO_CALCULAVEL and resultado.motivo == "variância de longo prazo nula"


def test_diferencial_constante_e_variancia_nula_e_nao_erro_numerico():
    resultado = _teste_media(np.full(30, 0.2), 19, 0.10, minimo=None)
    assert resultado.status == NAO_CALCULAVEL and resultado.motivo == "variância de longo prazo nula"


def test_variancia_de_bartlett_nunca_negativa():
    rng = np.random.default_rng(11)
    for _ in range(200):
        serie = rng.standard_t(3, size=rng.integers(5, 80))
        assert variancia_newey_west(serie, 19) >= -1e-15


def test_limiar_e_estrito_em_precisao_completa():
    d = np.array([0.5, 1.4, -0.3, 2.2, 0.9, 1.1, -0.2, 0.7])
    p = _teste_media(d, 1, 0.10, minimo=None).p
    assert not _teste_media(d, 1, p, minimo=None).atende          # p igual ao limiar não atende
    assert _teste_media(d, 1, math.nextafter(p, 1.0), minimo=None).atende


def test_clark_west_soma_o_quadrado_da_previsao():
    rng = np.random.default_rng(5)
    y, yhat = rng.normal(0, 0.05, 40), rng.normal(0, 0.01, 40)
    previsoes, datas = _previsoes(y, yhat)
    cw = clark_west(previsoes, datas, minimo=None)
    esperado = _teste_media(y ** 2 - (y - yhat) ** 2 + yhat ** 2, 19, 0.10, minimo=None)
    assert cw.estatistica == pytest.approx(esperado.estatistica)


def test_r2_coerente_com_o_sinal_e_denominador_nulo():
    rng = np.random.default_rng(8)
    for _ in range(50):
        y, yhat = rng.normal(0, 0.05, 30), rng.normal(0, 0.05, 30)
        d = y ** 2 - (y - yhat) ** 2
        assert np.sign(r2_fora_da_amostra(y, yhat)) == np.sign(d.mean())
    assert r2_fora_da_amostra(np.zeros(5), np.ones(5)) is None


def test_acuracia_balanceada_e_erros():
    assert acuracia_balanceada([0.1, -0.1, 0.2, -0.3], [0.05, 0.02, -0.01, -0.02]) == pytest.approx(0.5)
    assert acuracia_balanceada([0.1, 0.2], [0.1, 0.2]) is None
    assert erros([0.1, 0.3], [0.0, 0.1]) == {"mae": pytest.approx(0.15), "rmse": pytest.approx(math.sqrt(0.025)), "n": 2}


# ---------- requisito operacional e alinhamento

def test_minimo_de_200_datas():
    y = np.random.default_rng(1).normal(0, 0.05, 199)
    previsoes, datas = _previsoes(y, y * 0.5)
    resultado = diebold_mariano(previsoes, datas)
    assert resultado.status == NAO_CALCULAVEL and resultado.motivo == "amostra inferior ao mínimo previsto"
    assert not resultado.atende


def test_entrada_nao_finita():
    y = np.random.default_rng(2).normal(0, 0.05, 250)
    yhat = y * 0.5
    yhat[10] = np.nan
    previsoes, datas = _previsoes(y, yhat)
    assert diebold_mariano(previsoes, datas).motivo == "entrada não finita"


def test_previsao_ausente_nao_e_descartada_em_silencio():
    y = np.random.default_rng(4).normal(0, 0.05, 250)
    previsoes, datas = _previsoes(y, y * 0.5)
    resultado = diebold_mariano(previsoes.drop(index=7), datas)
    assert resultado.motivo == "previsão ausente em data elegível"
    assert resultado.datas_problema == (datas[7],)


def test_desalinhamento_de_datas():
    y = np.random.default_rng(6).normal(0, 0.05, 250)
    previsoes, datas = _previsoes(y, y * 0.5)
    resultado = diebold_mariano(previsoes, datas[:-1])
    assert resultado.motivo.startswith("desalinhamento")
