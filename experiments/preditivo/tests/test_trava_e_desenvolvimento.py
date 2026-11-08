"""Trava da avaliação final e separação entre desenvolvimento e período final."""

import json

import pandas as pd
import pytest

from experiments.preditivo import abertura
from experiments.preditivo import executar
from experiments.preditivo.abertura import (
    AberturaNegada,
    CONDICOES_SECAO_12,
    VersaoEncerrada,
    exigir_versao_aberta,
    modelo_condicoes,
    verificar_abertura,
)
from experiments.preditivo.executar import desenvolver_ativo, primeira_data_final
from experiments.preditivo.tests.auxiliares import precos_sinteticos


@pytest.fixture
def arquivos(tmp_path, monkeypatch):
    hashes = {"protocolo": "p", "nota": "n", "configuracao": "c", "manifesto_dados": "m"}
    monkeypatch.setattr(abertura, "hashes_atuais", lambda: dict(hashes))
    monkeypatch.setattr(abertura, "sha256", lambda _caminho: "d")
    datas = tmp_path / "datas.json"
    datas.write_text("{}", encoding="utf-8")
    return tmp_path, {**hashes, "datas_elegiveis": "d"}, datas


def _gravar(caminho, condicoes, hashes):
    caminho.write_text(json.dumps({"condicoes": condicoes, "hashes": hashes}), encoding="utf-8")


def test_sem_arquivo_de_condicoes_nao_abre(arquivos):
    pasta, _hashes, datas = arquivos
    with pytest.raises(AberturaNegada, match="arquivo de condições ausente"):
        verificar_abertura(True, pasta / "nao_existe.json", pasta / "marca.json", datas)


def test_condicao_pendente_ou_hash_diferente_nao_abre(arquivos):
    pasta, hashes, datas = arquivos
    condicoes = pasta / "condicoes.json"
    _gravar(condicoes, modelo_condicoes()["condicoes"], hashes)
    with pytest.raises(AberturaNegada, match="condições pendentes"):
        verificar_abertura(True, condicoes, pasta / "marca.json", datas)
    _gravar(condicoes, {n: True for n in CONDICOES_SECAO_12}, {**hashes, "protocolo": "outro"})
    with pytest.raises(AberturaNegada, match="hash de protocolo"):
        verificar_abertura(True, condicoes, pasta / "marca.json", datas)


def test_sem_confirmacao_ou_ja_usada_nao_abre(arquivos):
    pasta, hashes, datas = arquivos
    condicoes = pasta / "condicoes.json"
    _gravar(condicoes, {n: True for n in CONDICOES_SECAO_12}, hashes)
    with pytest.raises(AberturaNegada, match="confirmação explícita"):
        verificar_abertura(False, condicoes, pasta / "marca.json", datas)
    marca = pasta / "marca.json"
    marca.write_text("{}", encoding="utf-8")
    with pytest.raises(AberturaNegada, match="já foi usada"):
        verificar_abertura(True, condicoes, marca, datas)


def test_tudo_cumprido_libera(arquivos):
    pasta, hashes, datas = arquivos
    condicoes = pasta / "condicoes.json"
    _gravar(condicoes, {n: True for n in CONDICOES_SECAO_12}, hashes)
    verificar_abertura(True, condicoes, pasta / "marca.json", datas, pasta / "sem_encerramento.json")


def test_versao_encerrada_nao_abre_mesmo_com_tudo_cumprido(arquivos):
    pasta, hashes, datas = arquivos
    condicoes = pasta / "condicoes.json"
    _gravar(condicoes, {n: True for n in CONDICOES_SECAO_12}, hashes)
    encerramento = pasta / "encerramento.json"
    encerramento.write_text("{}", encoding="utf-8")
    with pytest.raises(AberturaNegada, match="encerrada por não elegibilidade"):
        verificar_abertura(True, condicoes, pasta / "marca.json", datas, encerramento)
    with pytest.raises(VersaoEncerrada, match="desenvolver --ensaio"):
        exigir_versao_aberta(encerramento)
    exigir_versao_aberta(pasta / "sem_encerramento.json")


def test_comandos_oficiais_recusados_na_versao_encerrada(tmp_path, monkeypatch):
    encerramento = tmp_path / "encerramento.json"
    encerramento.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(abertura, "ENCERRAMENTO", encerramento)
    monkeypatch.setattr(abertura.exigir_versao_aberta, "__defaults__", (encerramento,))
    for argv in (["coletar"], ["listar-datas"], ["desenvolver"]):
        with pytest.raises(VersaoEncerrada):
            executar.main(argv)
    monkeypatch.setattr(abertura.verificar_abertura, "__defaults__",
                        (*abertura.verificar_abertura.__defaults__[:3], encerramento))
    with pytest.raises(AberturaNegada, match="encerrada"):
        executar.main(["final", "--confirmo-abertura"])


def test_desenvolvimento_nao_le_o_periodo_final():
    serie = precos_sinteticos("2008-01-02", "2023-06-30")
    limite = primeira_data_final(serie)
    pregoes_2022 = serie[serie["Date"].dt.year == 2022]["Date"].reset_index(drop=True)
    assert limite == pregoes_2022[20]                       # 21º pregão de 2022
    previsoes, ajustes, dobras = desenvolver_ativo("TESTE", serie)
    assert [d["ano"] for d in dobras] == list(range(2014, 2022)) and len(ajustes) == 8
    assert previsoes["decision_date"].max() < limite
    assert previsoes["label_end_date"].dropna().max() < limite
    # O resultado não muda se o período final for alterado: ele não é lido.
    alterada = serie.copy()
    alterada.loc[alterada["Date"] >= limite, ["Open", "High", "Low", "Close"]] *= 3.0
    previsoes_b, _a, _d = desenvolver_ativo("TESTE", alterada)
    pd.testing.assert_frame_equal(previsoes, previsoes_b)


def test_embargo_so_na_fronteira_do_bloco_final_e_expurgo_em_cada_reestimacao():
    # Série sintética: nenhum dado real do período final é usado.
    from experiments.preditivo.amostras import construir_amostras
    from experiments.preditivo.avaliacao import prever_anos
    from experiments.preditivo.executar import embargos_periodo_final

    serie = precos_sinteticos("2008-01-02", "2023-12-29")
    embargos = embargos_periodo_final((2022, 2023))
    assert embargos == {2022: 20, 2023: 0}
    amostras = construir_amostras(serie)
    previsoes, ajustes = prever_anos(amostras, serie["Date"], (2022, 2023), embargos, "TESTE")
    pregoes = serie["Date"].reset_index(drop=True)
    p2022 = pregoes[pregoes.dt.year == 2022].reset_index(drop=True)
    p2023 = pregoes[pregoes.dt.year == 2023].reset_index(drop=True)
    assert previsoes["decision_date"].min() == p2022[20]           # 21º pregão de 2022
    assert ajustes[1]["data_ajuste"] == p2023[0].date().isoformat()  # sem nova interrupção em 2023
    datas = pd.DatetimeIndex(previsoes["decision_date"])
    esperadas = pregoes[(pregoes >= p2022[20]) & (pregoes <= amostras["decision_date"].max())]
    assert list(datas) == list(esperadas)                          # previsões contínuas no bloco
    for ajuste in ajustes:
        assert ajuste["fit_intercept"] is True and "previsoes_desvio" in ajuste
