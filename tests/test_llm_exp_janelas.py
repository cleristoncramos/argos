"""Janelas e regimes dos casos de síntese da fase 1 (DL1-J): regra única, mediana da célula e trava temporal."""

import json

import numpy as np
import pandas as pd
import pytest

from experiments.llm_v1_exp import janelas as j


@pytest.mark.parametrize("variacao,drawdown,regime", [
    (0.12, 0.10, "alta"),
    (0.12, 0.15, "lateral"),        # alta com queda severa no meio
    (0.10, 0.05, "lateral"),        # limite exato não é alta
    (-0.10, 0.05, "lateral"),
    (-0.11, 0.30, "baixa"),         # baixa vale qualquer que seja o drawdown
    (0.0, 0.40, "lateral"),
])
def test_classificacao_por_regra_unica(variacao, drawdown, regime):
    assert j.classificar(variacao, drawdown) == regime


def _serie(valores, inicio="2015-01-01"):
    return pd.Series(valores, index=pd.bdate_range(inicio, periods=len(valores)), dtype=float)


def test_metricas_da_janela_usam_n_retornos_e_drawdown_interno():
    serie = _serie([100, 120, 90, 110])
    m = j.metricas_janela(serie, serie.index[-1], 3)
    assert m["variacao"] == pytest.approx(0.10) and m["drawdown_maximo"] == pytest.approx(0.25)
    assert m["inicio"] == serie.index[0].date().isoformat() and m["regime"] == "lateral"
    assert j.metricas_janela(serie, serie.index[2], 3) is None          # sem histórico suficiente


def test_candidatas_no_ultimo_pregao_de_cada_mes():
    serie = _serie(np.linspace(10, 20, 700), inicio="2015-06-01")
    fins = j.fins_de_mes(serie)
    assert all(d >= pd.Timestamp("2016-01-01") for d in fins)
    assert all(d == serie.index[(serie.index.year == d.year) & (serie.index.month == d.month)].max() for d in fins)


def test_escolha_pela_mediana_e_empate_pela_mais_antiga():
    lista = [{"variacao": v, "fim": f} for v, f in
             ((0.10, "2017-01-31"), (0.30, "2016-01-29"), (0.20, "2018-01-31"), (0.40, "2019-01-31"))]
    escolhida = j.escolher(lista)                                         # mediana 0,25: empate 0,20 × 0,30
    assert escolhida["fim"] == "2016-01-29" and escolhida["mediana_da_celula"] == pytest.approx(0.25)
    assert escolhida["candidatas_na_celula"] == 4 and j.escolher([]) is None


def test_selecao_declara_celula_vazia_em_vez_de_preencher():
    fechamentos = {a: _serie(100 * np.exp(np.linspace(0, 0.5, 2000)), inicio="2012-01-02") for a in j.ATIVOS}
    casos = j.selecionar(fechamentos)                                     # crescimento suave: tudo lateral
    assert len(casos) == 12
    assert [c for c in casos if c["escolhida"] is None]                  # células sem candidata ficam vazias
    assert all(c["escolhida"]["regime"] == c["regime_alvo"] for c in casos if c["escolhida"])


def test_trava_temporal_e_hash_do_snapshot(tmp_path):
    datas = pd.bdate_range("2021-12-20", "2022-01-10")
    csv = pd.DataFrame({"Date": datas, "Close": np.arange(len(datas), dtype=float) + 1})
    nome = "PETR4_SA_ajustado.csv"
    csv.to_csv(tmp_path / nome, index=False)
    (tmp_path / "manifest.json").write_text(json.dumps({"arquivos": {nome: {"sha256": j._sha256(tmp_path / nome)}}}),
                                            encoding="utf-8")
    serie = j.carregar_fechamento("PETR4.SA", tmp_path)
    assert serie.index.max() <= pd.Timestamp(j.TRAVA_TEMPORAL)
    (tmp_path / nome).write_text("Date,Close\n2021-12-20,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Hash"):
        j.carregar_fechamento("PETR4.SA", tmp_path)
