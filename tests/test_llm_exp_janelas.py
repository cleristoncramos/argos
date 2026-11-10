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
def test_classificacao_original_mantida_para_auditoria(variacao, drawdown, regime):
    assert j.classificar_original(variacao, drawdown) == regime


@pytest.mark.parametrize("variacao,regime", [
    (0.8372, "alta"), (0.1001, "alta"), (0.10, "lateral"), (0.0, "lateral"), (-0.10, "lateral"),
    (-0.1001, "baixa"), (-0.37, "baixa"),
    (0.100001, "alta"), (-0.100001, "baixa"),                      # ±10,0001%
    (110 / 100 - 1, "lateral"), (90 / 100 - 1, "lateral"),         # ±10,00% exatos em ponto flutuante
])
def test_classificacao_corrigida_so_pela_variacao(variacao, regime):
    assert j.classificar(variacao) == regime


def _serie(valores, inicio="2015-01-01"):
    return pd.Series(valores, index=pd.bdate_range(inicio, periods=len(valores)), dtype=float)


def test_metricas_da_janela_usam_n_retornos_e_drawdown_interno():
    serie = _serie([100, 120, 90, 110])
    m = j.metricas_janela(serie, serie.index[-1], 3)
    assert m["variacao"] == pytest.approx(0.10) and m["drawdown_maximo"] == pytest.approx(0.25)
    assert m["inicio"] == serie.index[0].date().isoformat() and m["regime"] == "lateral"
    diarios = serie.pct_change().dropna()
    assert m["volatilidade_anualizada"] == pytest.approx(diarios.std(ddof=1) * np.sqrt(252))
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


# ------------------------------------------------------------------ correção P1 isolada

def _petr4_em_torno_da_data_ex():
    datas = pd.to_datetime(["2014-04-01", "2014-04-02", "2014-04-03", "2014-04-04"])
    return pd.Series([3.706662178039551, 3.648049831390381, 3.8578712940216064, 3.8678903579711914], index=datas)


def test_p1_reproduz_o_valor_corrigido_conhecido():
    corrigido = j.corrigir_p1(_petr4_em_torno_da_data_ex())
    assert corrigido.loc["2014-04-02"] == pytest.approx(j.P1_VALOR_CORRIGIDO_CONHECIDO, abs=5e-5)
    assert j.razao_p1() == pytest.approx(1.004137, abs=1e-6)


def test_p1_reescala_so_antes_da_data_ex_e_nao_altera_a_entrada():
    original = _petr4_em_torno_da_data_ex()
    copia = original.copy()
    corrigido = j.corrigir_p1(original)
    pd.testing.assert_series_equal(original, copia)
    assert corrigido.loc["2014-04-01"] == pytest.approx(original.loc["2014-04-01"] * j.razao_p1())
    assert (corrigido.loc["2014-04-03":] == original.loc["2014-04-03":]).all()
    sem_data = _serie([1.0, 2.0], inicio="2016-01-04")
    pd.testing.assert_series_equal(j.corrigir_p1(sem_data), sem_data)


def test_p1_aplicada_so_na_petr4(tmp_path):
    datas = pd.to_datetime(["2014-04-01", "2014-04-02", "2014-04-03"])
    for nome in ("PETR4_SA_ajustado.csv", "VALE3_SA_ajustado.csv"):
        pd.DataFrame({"Date": datas, "Close": [3.7, 3.648049831390381, 3.86]}).to_csv(tmp_path / nome, index=False)
    (tmp_path / "manifest.json").write_text(json.dumps({"arquivos": {
        n: {"sha256": j._sha256(tmp_path / n)} for n in ("PETR4_SA_ajustado.csv", "VALE3_SA_ajustado.csv")}}),
        encoding="utf-8")
    assert j.carregar_fechamento("PETR4.SA", tmp_path).loc["2014-04-02"] == pytest.approx(3.8986, abs=5e-5)
    assert j.carregar_fechamento("VALE3.SA", tmp_path).loc["2014-04-02"] == pytest.approx(3.648049831390381)
    assert j.carregar_fechamento("PETR4.SA", tmp_path, corrigir=False).loc["2014-04-02"] == pytest.approx(3.648049831390381)


def test_exclusao_de_candidatas_por_data():
    serie = _serie(100 * np.exp(np.linspace(0, 1, 1500)), inicio="2013-06-03")
    todas = j.candidatas(serie, 126)
    data = todas[0]["fim"]
    sem = j.candidatas(serie, 126, excluir_datas=[data])
    removidas = [c for c in todas if j.contem(c, data)]               # todas as janelas que contêm a data
    assert removidas and len(sem) == len(todas) - len(removidas) and not any(j.contem(c, data) for c in sem)


# ------------------------------------------------------------------ casos de média e sazonalidade

from experiments.llm_v1_exp import medias as m  # noqa: E402


def _mensal_sintetica():
    datas = pd.bdate_range("2008-01-02", "2021-12-30")
    rng = np.random.default_rng(3)
    return pd.Series(100 * np.cumprod(1 + rng.normal(0.0003, 0.02, len(datas))), index=datas)


def test_retornos_mensais_e_anuais_nos_periodos_declarados():
    serie = _mensal_sintetica()
    mensais, anuais = m.retornos_mensais(serie), m.retornos_anuais(serie)
    assert mensais.index.min() == pd.Timestamp("2008-02-29") and len(mensais) == 167
    assert list(anuais.index) == list(range(2009, 2022))
    fim_jan, fim_fev = serie.loc["2008-01"].iloc[-1], serie.loc["2008-02"].iloc[-1]
    assert mensais.iloc[0] == pytest.approx(fim_fev / fim_jan - 1)


def test_sazonalidade_escolhe_maior_e_menor_media_com_empate_no_mes_mais_antigo():
    datas = pd.DatetimeIndex([f"{a}-{mes:02d}-28" for a in (2019, 2020) for mes in range(1, 13)])
    mensais = pd.Series([0.05 if mes in (3, 7) else (-0.04 if mes in (5, 9) else 0.0)
                         for _a in (2019, 2020) for mes in range(1, 13)], index=datas)
    maior, menor = m.sazonalidade("X", mensais)
    assert (maior["mes"], menor["mes"]) == (3, 5)
    assert maior["anos"] == 2 and maior["anos_positivos"] == 2 and maior["desvio_entre_anos"] == pytest.approx(0.0)


def test_oito_casos_na_ordem_declarada_com_metadados():
    serie = _mensal_sintetica()
    lista = m.casos({a: serie for a in j.ATIVOS})
    assert [c["tipo"] for c in lista] == ["sazonalidade", "sazonalidade", "frequencia_historica",
                                          "comparacao_entre_periodos"] * 2
    comp = lista[3]
    assert comp["meses_ultimo_ano"] == 12 and comp["meses_anos_anteriores"] == 60 and comp["anos"] == 6
    assert set(comp["retornos_anuais_anteriores"]) == set(m.ANOS_ANTERIORES)
    freq = lista[2]
    assert freq["meses"] == 167 and freq["anos"] == 13 and 0 <= freq["proporcao_anos_positivos"] <= 1


def test_p1_escopo_restrito_ao_fechamento_da_petr4(tmp_path):
    """A P1 local só reescala fechamentos antes da data ex e troca o de 02/04/2014; nada mais muda."""
    datas = pd.to_datetime(["2014-03-31", "2014-04-01", "2014-04-02", "2014-04-03", "2014-04-04"])
    quadro = pd.DataFrame({"Date": datas, "Open": [1.0, 2.0, 3.0, 4.0, 5.0], "High": [9.0] * 5, "Low": [0.5] * 5,
                           "Close": [3.7, 3.706662178039551, 3.648049831390381, 3.8578712940216064, 3.87]})
    nome = "PETR4_SA_ajustado.csv"
    quadro.to_csv(tmp_path / nome, index=False)
    hash_antes = j._sha256(tmp_path / nome)
    (tmp_path / "manifest.json").write_text(json.dumps({"arquivos": {nome: {"sha256": hash_antes}}}), encoding="utf-8")
    serie = j.carregar_fechamento("PETR4.SA", tmp_path)
    assert j._sha256(tmp_path / nome) == hash_antes                    # o arquivo congelado não é alterado
    assert serie.name == "Close" and list(serie.index) == list(datas)    # só o fechamento, mesmas datas
    original = quadro.set_index("Date")["Close"]
    mudou = serie[serie != original].index
    assert set(mudou) <= {pd.Timestamp(d) for d in ("2014-03-31", "2014-04-01", "2014-04-02")}
    assert (serie.loc["2014-04-03":] == original.loc["2014-04-03":]).all()
