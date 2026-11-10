"""Template determinístico da fase 1: composição, ressalva estrutural e validação das 28 saídas."""

import copy
import json

import pytest

from core import llm_exp_validation as ev
from core.assets import ASSETS
from experiments.llm_v1_exp import conjunto, template

TICKERS = [a["ticker"] for a in ASSETS]


@pytest.fixture(scope="module")
def casos():
    return json.loads(conjunto.ARQUIVO.read_text(encoding="utf-8"))["casos"]


def test_as_28_saidas_passam_nas_17_verificacoes(casos):
    for caso in casos:
        resposta = template.responder(caso)
        resultado = ev.validate_experimental(json.dumps(resposta, ensure_ascii=False), caso["contexto"], TICKERS)
        assert resultado.ok, (caso["id"], resultado.failed)


def test_composicao_sem_defeitos(casos):
    for caso in casos:
        assert template.defeitos_de_composicao(template.responder(caso), caso) == [], caso["id"]


def test_casos_de_media_trazem_a_ressalva_estrutural_no_mesmo_paragrafo(casos):
    for caso in (c for c in casos if c["bloco"] == "media"):
        texto = template.responder(caso)["observacao_historica"]["texto"]
        assert texto.endswith(template.RESSALVA_FINAL)
        assert "anos de amostra" in texto and "desvio-padrão" in texto and "variou" in texto


def test_media_sem_ressalva_reprova_o_template_mesmo_se_o_validador_aprovar(casos):
    caso = next(c for c in casos if c["id"] == "M01")
    resposta = template.responder(caso)
    variante = copy.deepcopy(resposta)
    # Redação aceita pelo validador (classes de expressão), mas fora da estrutura fixa do template.
    variante["observacao_historica"]["texto"] = (
        "Em 14 anos, abril teve média de 7,74%, com amostra pequena e resultado que variou de -9,31% a 35,2%; "
        "isso pode não se repetir.")
    assert ev.validate_experimental(json.dumps(variante, ensure_ascii=False), caso["contexto"], TICKERS).ok
    assert template.defeitos_de_composicao(variante, caso)                 # defeito de composição
    sem = copy.deepcopy(resposta)
    sem["observacao_historica"]["texto"] = "No recorte selecionado, o retorno de abril teve média de 7,74%."
    assert template.defeitos_de_composicao(sem, caso)


def test_sintese_nao_cita_recurso_fora_do_contexto(casos):
    caso = next(c for c in casos if c["bloco"] == "sintese")
    resposta = template.responder(caso)
    assert template.defeitos_de_composicao(resposta, caso) == []
    resposta["limitacoes"] = ["O RSI ficou sobrecomprado no período."]
    assert "recurso fora do contexto: RSI" in template.defeitos_de_composicao(resposta, caso)


def test_queda_nao_recuperada_sem_prazo(casos):
    caso = next(c for c in casos if c["id"] == "G08")
    texto = template.responder(caso)["observacao_historica"]["texto"]
    assert "não foi recuperada até 30/12/2021" in texto and "ainda" not in texto.lower()
    resposta = template.responder(caso)
    resposta["limitacoes"] = ["A queda ainda não foi recuperada."]
    assert any("ainda" in d for d in template.defeitos_de_composicao(resposta, caso))


def test_template_nao_cita_parametros_ausentes_do_contexto(casos):
    """O conjunto congelado não lista 50, 200, 14, 20, 126 e 504 como números citáveis."""
    for caso in casos:
        corpo = json.dumps(template.responder(caso), ensure_ascii=False)
        for numero in (" 50 ", " 200 ", " 14 pregões", " 20 pregões", " 126 ", " 504 "):
            assert numero not in corpo, (caso["id"], numero)
