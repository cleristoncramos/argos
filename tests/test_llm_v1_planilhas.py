"""Planilhas cegas da fase 1 (DL2-I, escopo de 13/11/2026): 20 casos S+G, 60 aplicações."""

import csv
import json
import re

import pytest

from experiments.llm_v1_exp import adversariais, planilhas, rodada


@pytest.fixture(scope="module")
def dados():
    return rodada.carregar_conjunto()


@pytest.fixture(scope="module")
def template():
    return adversariais.respostas_congeladas()


def _rodada_simulada(tmp_path, template, faltando=()):
    """Arquivo no formato da rodada, com as saídas do template no lugar das do Grok."""
    linhas = []
    for caso in [*planilhas.CASOS_RUBRICA, "M01", "A01", "R01"]:
        for execucao in (1, 2):
            if (caso, execucao) in faltando:
                continue
            status = "bloqueada" if caso == "M01" else "avaliacao"
            linhas.append(json.dumps({"caso": caso, "execucao": execucao, "status": status,
                                      "resposta": json.dumps(template.get(caso, template["S01"]), ensure_ascii=False)}))
    arquivo = tmp_path / "rodada.jsonl"
    arquivo.write_text("\n".join(linhas) + "\n\n", encoding="utf-8")
    return arquivo


def _ler(caminho):
    with open(caminho, encoding="utf-8-sig") as arquivo:
        return list(csv.DictReader(arquivo, delimiter=";"))


def test_escopo_e_rubrica():
    assert len(planilhas.CASOS_RUBRICA) == 20 and planilhas.CASOS_RUBRICA[0] == "S01"
    assert planilhas.CASOS_RUBRICA[-1] == "G08"
    assert not any(c.startswith(("M", "A", "R")) for c in planilhas.CASOS_RUBRICA)
    assert [c for c, _, _ in planilhas.RUBRICA] == [
        "fidelidade_numeros", "tres_camadas", "calibracao_incerteza", "sem_promessa", "utilidade"]


def test_sessenta_aplicacoes(tmp_path, dados, template):
    grok = planilhas.respostas_grok(_rodada_simulada(tmp_path, template))
    assert len(grok) == 40 and ("M01", 1) not in grok and ("A01", 1) not in grok
    lista = planilhas.itens(dados, template, grok)
    assert len(lista) == 60
    assert sum(1 for i in lista if i["fonte"] == "template") == 20
    assert sum(1 for i in lista if i["fonte"] == "grok-4.3") == 40

    with pytest.raises(ValueError, match="G03, execução 2"):
        planilhas.itens(dados, template, planilhas.respostas_grok(
            _rodada_simulada(tmp_path, template, faltando={("G03", 2)})))


def test_planilhas_sao_cegas(tmp_path, dados, template):
    lista = planilhas.itens(dados, template, planilhas.respostas_grok(_rodada_simulada(tmp_path, template)))
    manifesto = planilhas.montar(lista, tmp_path / "avaliacao")
    assert manifesto["aplicacoes"] == 60 and manifesto["por_fonte"] == {"template": 20, "grok-4.3": 40}

    chave = _ler(tmp_path / "avaliacao" / "chave_cegamento.csv")
    assert len(chave) == 60 and {r["fonte"] for r in chave} == {"template", "grok-4.3"}
    ids = {r["id_cego"] for r in chave}

    ordens = []
    for avaliador in planilhas.AVALIADORES:
        planilha = _ler(tmp_path / "avaliacao" / f"{avaliador}.csv")
        assert {r["id_cego"] for r in planilha} == ids                # as mesmas 60 aplicações
        assert "fonte" not in planilha[0] and "caso" not in planilha[0] and "execucao" not in planilha[0]
        texto = json.dumps(planilha, ensure_ascii=False).lower()
        for marca in ("grok", "template", "xai", "modelo de linguagem", "execução"):
            assert marca not in texto, marca                           # nenhuma marca da fonte
        assert "{" not in planilha[0]["saida_do_sistema"]               # sem JSON
        for linha in planilha:                                          # nenhuma data ISO (DL2-I)
            for campo in ("contexto_dado_ao_sistema", "saida_do_sistema"):
                assert not re.search(r"\b(19|20)\d\d-\d\d-\d\d\b", linha[campo]), linha[campo][:80]
        ordens.append([r["id_cego"] for r in planilha])
    assert ordens[0] != ordens[1]                                       # ordem própria por avaliador

    instrucoes = (tmp_path / "avaliacao" / "instrucoes_avaliadores.md").read_text(encoding="utf-8")
    assert "60 explicações" in instrucoes and "0 a 5" in instrucoes and "grok" not in instrucoes.lower()


def test_embaralhamento_reproduzivel(tmp_path, dados, template):
    lista = planilhas.itens(dados, template, planilhas.respostas_grok(_rodada_simulada(tmp_path, template)))
    planilhas.montar(lista, tmp_path / "a")
    planilhas.montar(lista, tmp_path / "b")
    assert (tmp_path / "a" / "chave_cegamento.csv").read_bytes() == (tmp_path / "b" / "chave_cegamento.csv").read_bytes()
    planilhas.montar(lista, tmp_path / "c", semente=1)
    assert (tmp_path / "a" / "chave_cegamento.csv").read_bytes() != (tmp_path / "c" / "chave_cegamento.csv").read_bytes()


def test_main(tmp_path, template, capsys, monkeypatch):
    arquivo = _rodada_simulada(tmp_path, template)
    assert planilhas.main(["--rodada", str(arquivo), "--saida", str(tmp_path / "saida")]) == 0
    manifesto = json.loads((tmp_path / "saida" / "manifesto.json").read_text(encoding="utf-8"))
    assert manifesto["rodada_sha256"] and manifesto["template_sha256"] and manifesto["semente"] == planilhas.SEMENTE
    assert "60 aplicações" in capsys.readouterr().out

    incompleto = _rodada_simulada(tmp_path, template, faltando={("S01", 1)})
    assert planilhas.main(["--rodada", str(incompleto), "--saida", str(tmp_path / "x")]) == 2
    assert "Falta a saída aprovada do Grok para S01" in capsys.readouterr().out


def test_normalizacao_de_datas_so_de_formato():
    assert planilhas.normalizar_datas("de 2014-06-17 a 2016-06-30") == "de 17/06/2014 a 30/06/2016"
    assert planilhas.normalizar_datas("29/07/2016 e 2021-12-30.") == "29/07/2016 e 30/12/2021."
    intocado = "504 pregões; 2016-13-01; 12-2016; 2016-7-1"
    assert planilhas.normalizar_datas(intocado) == intocado


def test_mesma_funcao_nas_duas_fontes_e_respostas_intactas(dados, template):
    import copy
    resposta = copy.deepcopy(template["S01"])
    resposta["resumo"] = "Entre 2016-07-29 e 2017-01-31 o preço subiu."
    original = copy.deepcopy(resposta)
    texto = planilhas.texto_saida(resposta)
    assert "29/07/2016" in texto and "2016-07-29" not in texto
    assert resposta == original                                         # a resposta não é alterada
    contexto = dict(rodada.plano(dados))["S01"]
    assert "29/07/2016 a 31/01/2017" in planilhas.texto_contexto(contexto)
    assert contexto["filters"]["period_start"] == "2016-07-29"          # o contexto também não
