"""Trava da avaliação final e separação entre desenvolvimento e período final."""

import json

import pandas as pd
import pytest

from experiments.preditivo import abertura
from experiments.preditivo.abertura import AberturaNegada, CONDICOES_SECAO_12, modelo_condicoes, verificar_abertura
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
    verificar_abertura(True, condicoes, pasta / "marca.json", datas)


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
