"""A05 montado a partir do template congelado, rastreável por hash no registro de execução."""

import json

import pytest

from core import llm_exp_validation as ev
from core.assets import ASSETS
from experiments.llm_v1_exp import adversariais, conjunto


@pytest.fixture(scope="module")
def montado():
    return json.loads(adversariais.ARQUIVO.read_text(encoding="utf-8"))


def test_a05_reconstruivel_a_partir_do_template_congelado(montado):
    assert adversariais.montar() == montado
    assert montado["conjunto_sha256"] == conjunto.HASH_CONGELADO
    assert montado["template_respostas_sha256"] == adversariais.HASH_TEMPLATE_RESPOSTAS


def test_registro_de_execucao_guarda_os_hashes(montado):
    entradas = [json.loads(linha) for linha in adversariais.REGISTRO.read_text(encoding="utf-8").splitlines()]
    entrada = [e for e in entradas if e["evento"] == "montagem_A05"][-1]
    assert entrada["A05_texto_sha256"] == montado["A05_texto_sha256"] == adversariais.sha_texto(montado["A05"])
    assert entrada["template_codigo_sha256"] == adversariais.HASH_TEMPLATE_CODIGO
    assert entrada["template_respostas_sha256"] == adversariais.HASH_TEMPLATE_RESPOSTAS
    assert entrada["arquivo_sha256"] == adversariais._sha(adversariais.ARQUIVO)


def test_a05_reprova_so_pela_verificacao_de_numero(montado):
    casos = json.loads(conjunto.ARQUIVO.read_text(encoding="utf-8"))["casos"]
    g05 = next(c for c in casos if c["id"] == "G05")
    resultado = ev.validate_experimental(json.dumps(montado["A05"]["resposta"], ensure_ascii=False), g05["contexto"],
                                         [a["ticker"] for a in ASSETS])
    assert resultado.failed == ["valores_rastreaveis"]
    assert float(montado["A05"]["valor_adulterado"].replace(",", ".")) == pytest.approx(
        float(montado["A05"]["valor_original"].replace(",", ".")) * 1.1, abs=0.005)


def test_template_alterado_impede_a_montagem(monkeypatch):
    monkeypatch.setattr(adversariais, "HASH_TEMPLATE_RESPOSTAS", "0" * 64)
    with pytest.raises(ValueError, match="congelamento"):
        adversariais.montar()
