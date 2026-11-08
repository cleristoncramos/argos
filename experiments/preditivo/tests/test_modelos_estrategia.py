"""Referências, Ridge, backtest (condição 6) e critérios de elegibilidade."""

import numpy as np
import pandas as pd
import pytest

from experiments.preditivo.amostras import construir_amostras
from experiments.preditivo.divisoes import dividir_ano
from experiments.preditivo.elegibilidade import MENSAGEM_SEM_EVIDENCIA, avaliar, condicao_economica
from experiments.preditivo.estatistica import NAO_CALCULAVEL, OK, ResultadoTeste
from experiments.preditivo.estrategia import CaixaCDI, ResultadoEstrategia, backtest, datas_de_decisao
from experiments.preditivo.modelos import ajustar_ridge, escolher_alpha, prever_media_historica
from experiments.preditivo.tests.auxiliares import cdi_sintetico, precos_sinteticos


# ---------- modelos

def test_media_historica_usa_so_alvos_realizados():
    amostras = pd.DataFrame({
        "label_end_date": pd.to_datetime(["2020-01-10", "2020-01-20", "2020-02-01"]),
        "y": [0.1, 0.3, 0.9],
    })
    decisoes = pd.Series(pd.to_datetime(["2020-01-05", "2020-01-10", "2020-01-25", "2020-03-01"]))
    media = prever_media_historica(amostras, decisoes)
    assert np.isnan(media[0])
    assert media[1:] == pytest.approx([0.1, 0.2, (0.1 + 0.3 + 0.9) / 3])


def test_empate_escolhe_o_maior_alpha():
    assert escolher_alpha({0.1: 2.0, 10.0: 1.0, 1000.0: 1.0}) == 1000.0
    assert escolher_alpha({0.1: 0.5, 1.0: 1.0}) == 0.1


def test_ridge_escolhe_na_grade_com_validacoes_internas():
    serie = precos_sinteticos("2008-01-02", "2015-12-30")
    amostras = construir_amostras(serie)
    divisao = dividir_ano(amostras, serie["Date"], 2015)
    ridge = ajustar_ridge(amostras, serie["Date"], divisao.treino, divisao.primeira_data)
    assert ridge.alpha in (0.1, 1.0, 10.0, 100.0, 1000.0)
    assert ridge.anos_internos == (2012, 2013, 2014)
    assert set(ridge.erros_internos) == {0.1, 1.0, 10.0, 100.0, 1000.0}
    assert np.isfinite(ridge.prever(amostras, divisao.avaliacao)).all()


# ---------- backtest

def _precos(valores, inicio="2022-01-03"):
    datas = pd.bdate_range(inicio, periods=len(valores))
    return pd.DataFrame({"Date": datas, "Close": valores})


def test_exposto_o_tempo_todo_paga_so_entrada_e_saida():
    precos = _precos([10.0, 11.0, 12.0, 12.0, 13.2])
    cdi = cdi_sintetico("2021-12-01", "2022-02-28", taxa=0.0)
    decisoes = pd.DataFrame({"entry_date": precos["Date"].iloc[[0, 2]], "yhat": [0.05, 0.05]})
    r = backtest(precos, cdi, decisoes, custo=0.001, corte=precos["Date"].iloc[-1])
    assert r["estrategia"].retorno == pytest.approx(1.32 * 0.999 * 0.999 - 1)
    assert r["estrategia"].trocas == 2                    # permanecer exposto não gera custo
    assert r["comprar_manter"].retorno == pytest.approx(r["estrategia"].retorno)


def test_caixa_rende_o_cdi_e_sair_cobra_venda():
    precos = _precos([10.0, 10.0, 10.0, 10.0])
    cdi = cdi_sintetico("2021-12-01", "2022-02-28", taxa=0.001)
    decisoes = pd.DataFrame({"entry_date": precos["Date"].iloc[[0, 2]], "yhat": [0.01, 0.0]})
    r = backtest(precos, cdi, decisoes, custo=0.001, corte=precos["Date"].iloc[-1])
    # compra no dia 0, fica exposto até o dia 2 (preço parado), vende e rende o CDI por 1 dia
    assert r["estrategia"].retorno == pytest.approx(0.999 * 0.999 * 1.001 - 1)
    assert r["caixa"].retorno == pytest.approx(1.001 ** 3 - 1)
    assert r["estrategia"].exposicao == pytest.approx(2 / 3)


def test_limiar_e_custo_de_ida_e_volta():
    precos = _precos([10.0, 10.5, 11.0])
    cdi = cdi_sintetico("2021-12-01", "2022-02-28")
    abaixo = pd.DataFrame({"entry_date": precos["Date"].iloc[[0]], "yhat": [0.002]})
    r = backtest(precos, cdi, abaixo, custo=0.001, corte=precos["Date"].iloc[-1])
    assert r["estrategia"].trocas == 0                    # ŷ = c não supera o limiar


def test_cdi_composto_entre_fechamentos_e_lacuna_interrompe():
    cdi = pd.DataFrame({"data": pd.to_datetime(["2022-01-03", "2022-01-04", "2022-01-05"]), "taxa": [0.01, 0.02, 0.03]})
    caixa = CaixaCDI(cdi)
    assert caixa.fator(pd.Timestamp("2022-01-03"), pd.Timestamp("2022-01-05")) == pytest.approx(1.02 * 1.03)
    with pytest.raises(ValueError):
        caixa.fator(pd.Timestamp("2022-01-05"), pd.Timestamp("2022-01-06"))


def test_drawdown_em_magnitude_positiva():
    precos = _precos([10.0, 8.0, 9.0, 12.0])
    cdi = cdi_sintetico("2021-12-01", "2022-02-28")
    decisoes = pd.DataFrame({"entry_date": precos["Date"].iloc[[0]], "yhat": [0.1]})
    r = backtest(precos, cdi, decisoes, custo=0.0, corte=precos["Date"].iloc[-1])
    assert r["comprar_manter"].drawdown_maximo == pytest.approx(0.2)


def test_decisoes_a_cada_20_datas_sem_sobreposicao():
    previsoes = pd.DataFrame({"decision_date": pd.bdate_range("2022-02-01", periods=65)})
    decisoes = datas_de_decisao(previsoes)
    assert len(decisoes) == 4 and (decisoes["decision_date"].diff().dropna() > pd.Timedelta(days=20)).all()


# ---------- elegibilidade

def _r(retorno, queda):
    return ResultadoEstrategia("x", retorno, 0.0, 0.0, queda, 0, 0.0, pd.DataFrame())


def test_condicao_economica_com_parenteses_explicitos():
    # (A ∧ B): acima do caixa e queda menor
    assert condicao_economica({"estrategia": _r(0.2, 0.1), "caixa": _r(0.1, 0), "comprar_manter": _r(0.5, 0.3)})["atende"]
    # A sem B e sem C: não atende
    assert not condicao_economica({"estrategia": _r(0.2, 0.4), "caixa": _r(0.1, 0), "comprar_manter": _r(0.5, 0.3)})["atende"]
    # C com queda maior: atende, com destaque obrigatório
    c = condicao_economica({"estrategia": _r(0.6, 0.5), "caixa": _r(0.1, 0), "comprar_manter": _r(0.5, 0.3)})
    assert c["atende"] and c["destaque_queda_maior_no_ramo_C"]


def test_todos_os_criterios_sao_obrigatorios():
    bom = {"estrategia": _r(0.2, 0.1), "caixa": _r(0.1, 0), "comprar_manter": _r(0.5, 0.3)}
    dm_ok = ResultadoTeste(OK, p=0.05, atende=True)
    dobras = [0.01] * 5 + [-0.01] * 3
    assert avaliar(0.01, dm_ok, dobras, bom, bom)["elegivel"]
    assert avaliar(0.0, dm_ok, dobras, bom, bom)["mensagem"] == MENSAGEM_SEM_EVIDENCIA      # R² = 0 não basta
    assert not avaliar(None, dm_ok, dobras, bom, bom)["elegivel"]                            # não calculável
    assert not avaliar(0.01, ResultadoTeste(NAO_CALCULAVEL), dobras, bom, bom)["elegivel"]
    assert not avaliar(0.01, dm_ok, [0.01] * 4 + [-0.01] * 4, bom, bom)["elegivel"]
    ruim = {"estrategia": _r(0.0, 0.4), "caixa": _r(0.1, 0), "comprar_manter": _r(0.5, 0.3)}
    assert not avaliar(0.01, dm_ok, dobras, bom, ruim)["criterios"]["5_robustez_ao_custo"]


def _bruto_2014():
    # Valores da fonte para PETR4 (base bruta, corrigida só por desdobramentos), com fator constante.
    bruto = pd.DataFrame({"Date": pd.to_datetime(["2014-04-01", "2014-04-02", "2014-04-03"]),
                          "Open": [15.72, 15.71, 15.53], "High": [15.85, 16.60, 15.65],
                          "Low": [15.48, 15.70, 15.12], "Close": [15.81, 15.56, 15.40],
                          "Dividends": [0.0, 0.0, 0.0], "Stock Splits": [0.0, 0.0, 0.0]})
    bruto["Adj Close"] = bruto["Close"] * 0.2344
    ajustado = bruto[["Date"]].assign(**{c: bruto[c] * 0.2344 for c in ("Open", "High", "Low", "Close")})
    return bruto, ajustado


def test_ohlc_conferido_na_mesma_base_sem_correcao():
    from experiments.preditivo.dados import verificar_ohlc
    bruto, ajustado = _bruto_2014()
    resultado = verificar_ohlc(bruto, ajustado)
    assert [o["data"] for o in resultado["ocorrencias"]] == ["2014-04-02"]
    ocorrencia = resultado["ocorrencias"][0]
    assert ocorrencia["falha_na_base_bruta"] and ocorrencia["falha_na_base_ajustada"]
    assert ocorrencia["situacao"] == "em investigação"
    assert resultado["maior_diferenca_relativa_usada_vs_reconstruida"] == pytest.approx(0.0, abs=1e-12)
    assert bruto.loc[1, "Close"] == 15.56                  # nada é corrigido


def test_adj_close_fora_da_faixa_bruta_nao_e_erro_se_a_base_bate():
    from experiments.preditivo.dados import verificar_ohlc
    bruto, ajustado = _bruto_2014()
    bruto.loc[1, "Close"] = 15.80                          # dentro da faixa bruta
    bruto["Adj Close"] = bruto["Close"] * 0.2344            # Adj Close está fora de [Low, High] brutos, mas é outra escala
    ajustado = bruto[["Date"]].assign(**{c: bruto[c] * 0.2344 for c in ("Open", "High", "Low", "Close")})
    assert verificar_ohlc(bruto, ajustado)["ocorrencias"] == []


def test_variacao_do_fator_sem_evento_e_desdobramentos():
    from experiments.preditivo.dados import desdobramentos_na_fonte, variacoes_do_fator
    bruto, _ = _bruto_2014()
    bruto.loc[2, "Adj Close"] = 15.40 * 0.2505              # fator muda sem provento registrado
    assert [v["data"] for v in variacoes_do_fator(bruto)] == ["2014-04-03"]
    bruto.loc[2, "Dividends"] = 0.5                         # com provento na data, não é marcada
    assert variacoes_do_fator(bruto) == []
    bruto.loc[1, "Stock Splits"] = 2.0
    assert desdobramentos_na_fonte(bruto) == [{"data": "2014-04-02", "fator": 2.0}]
