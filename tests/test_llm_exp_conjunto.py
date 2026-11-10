"""Conjunto de casos congelado da fase 1: hash, composição, trava temporal e ausência do valor alternativo."""

import json

import pytest

from core import llm_exp_context as ec
from core import llm_exp_prompts as ep
from core import llm_exp_service as es
from experiments.llm_v1_exp import conjunto, janelas


@pytest.fixture(scope="module")
def dados():
    return json.loads(conjunto.ARQUIVO.read_text(encoding="utf-8"))


def test_arquivo_congelado_confere_com_o_hash_registrado():
    assert conjunto.sha256_arquivo() == conjunto.HASH_CONGELADO


def test_composicao_dos_38_registros(dados):
    ids = [c["id"] for c in dados["casos"]]
    assert ids == [f"S{n:02d}" for n in range(1, 13)] + [f"G{n:02d}" for n in range(1, 9)] + [f"M{n:02d}" for n in range(1, 9)]
    assert [a["id"] for a in dados["adversariais"]] == [f"A{n:02d}" for n in range(1, 7)]
    assert [(r["id"], r["repete"]) for r in dados["controles"]] == [("R01", "S01"), ("R02", "S05"), ("R03", "S07"), ("R04", "S11")]
    contagem = dados["parametros"]["contagem"]
    assert len(ids) + len(dados["adversariais"]) + len(dados["controles"]) == contagem["registros"] == 38
    assert contagem["chamadas_reais_por_modelo"] == 33 and contagem["pior_caso"] == 132
    assert contagem["saidas_avaliacao_humana"] == 84 == 28 * 3


def test_contextos_validos_e_sem_dado_depois_da_trava(dados):
    for caso in dados["casos"]:
        ctx = caso["contexto"]
        assert ctx["protocol_family"] == ec.PROTOCOL_FAMILY and ctx["release"]["recomendacao_habilitada"] is False
        assert ctx["estimate"]["disponivel"] is False and ctx["decision"]["disponivel"] is False
        assert ctx["filters"]["period_end"] <= janelas.TRAVA_TEMPORAL, caso["id"]
        assert ctx["user_request"] is None and ctx["required_limits"]


def _numeros(objeto):
    if isinstance(objeto, dict):
        for valor in objeto.values():
            yield from _numeros(valor)
    elif isinstance(objeto, list):
        for valor in objeto:
            yield from _numeros(valor)
    elif isinstance(objeto, (int, float)) and not isinstance(objeto, bool):
        yield float(objeto)


def test_valor_alternativo_de_dezembro_fora_do_contexto_de_m04_e_m08(dados):
    """DL1-M: as leituras com dezembro de 2021 (+2,15% e +0,72%) e o retorno anual de 2021 não entram."""
    proibidos = {"M04": {2.15, 23.51}, "M08": {0.72, 4.87}}
    for caso in dados["casos"]:
        if caso["id"] in proibidos:
            ctx = caso["contexto"]
            assert not {round(v, 2) for v in _numeros(ctx)} & proibidos[caso["id"]], caso["id"]
            assert "dezembro" not in json.dumps(ctx, ensure_ascii=False).lower()
            assert "retorno_anual_ultimo_ano" not in caso["metadados"]
            media = next(m for m in ctx["historical"]["metrics"] if m["id"] == "media_mensal_2021")
            assert media["value"] == {"M04": 1.56, "M08": -0.25}[caso["id"]]


def test_adversariais_com_desfecho_declarado(dados):
    for adv in dados["adversariais"]:
        assert adv["desfecho_esperado"] and adv["verificacao"] and adv["classe"]
    a02 = next(a for a in dados["adversariais"] if a["id"] == "A02")
    assert a02["pedido"]["type"] == "garantia" and ep.fixed_text_hashes()["recusa_garantia"] == "de703a62818b"
    assert es.policy_refusal(a02["pedido"]["type"]).reason == "bloqueio_politica"


def test_parametros_registram_protocolo_ratificado(dados):
    protocolo = dados["parametros"]["protocolo"]
    assert protocolo == {"prompt": "f41d1cf2a5fc", "esquema": "9a4cb5cb5a0c", "impressao": "b1ee60720f24",
                         "textos_fixos": "95845577dba9", "verificacoes": 17}


def test_regenerar_a_partir_dos_dados_reproduz_o_arquivo():
    if not (janelas.SNAPSHOT / "PETR4_SA_ajustado.csv").exists():
        pytest.skip("snapshot do piloto fora do Git; regeneração só no ambiente do pesquisador")
    assert conjunto.main([]) == 0


def test_autoconsistencia_todo_numero_do_contexto_e_citavel(dados):
    """DL1-O: nenhum rótulo ou nota pode citar número que a verificação 6 recusaria."""
    for caso in dados["casos"]:
        assert conjunto.numeros_nao_citaveis(caso["contexto"]) == [], caso["id"]


def test_autoconsistencia_detecta_o_defeito_antigo(dados):
    caso = json.loads(json.dumps(next(c for c in dados["casos"] if c["id"] == "G02")))
    caso["contexto"]["extra_numbers"] = []                              # como no conjunto fase1-v1
    caso["contexto"]["historical"]["notes"] = ["Recorte de 504 pregões."]
    assert set(conjunto.numeros_nao_citaveis(caso["contexto"])) == {504.0, 14.0}


def test_rotulos_de_janela_e_nota_de_g08(dados):
    por_id = {c["id"]: c for c in dados["casos"]}
    assert "126 pregões de variação (127 observações)" in por_id["S01"]["contexto"]["historical"]["notes"][0]
    assert "504 pregões de variação (505 observações)" in por_id["G01"]["contexto"]["historical"]["notes"][0]
    nota_g08 = "Queda de 41,34% iniciada em 28/07/2021, não recuperada até 30/12/2021."
    assert nota_g08 in por_id["G08"]["contexto"]["historical"]["notes"]
    assert por_id["G02"]["contexto"]["extra_numbers"] == [504.0, 14.0, 12.0, 26.0, 9.0]
    assert dados["versao"] == "fase1-v2" and conjunto.HASH_ANTERIOR.startswith("6080cc05")
