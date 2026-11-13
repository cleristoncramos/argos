"""Rodada da fase 1 com o provedor xAI (etapa 6 da DL2): tudo com transporte simulado, sem rede."""

import json

import pytest

from core import llm_client
from core import llm_provider as lp
from core.llm_client import ApiError
from core.llm_exp_service import COMPLETE_FINISH, estimate_input_tokens, explain_experimental
from core.llm_service import MODE_LIVE, UsageLimiter
from experiments.llm_v1_exp import adversariais, rodada

FAKE_KEY = "chave-de-teste-nao-real"


@pytest.fixture(scope="module")
def dados():
    return rodada.carregar_conjunto()


@pytest.fixture(scope="module")
def respostas():
    return adversariais.respostas_congeladas()


def _resposta_xai(texto, status="completed", model="grok-4.3"):
    return {"model": model, "status": status,
            "output": [{"type": "message", "content": [{"type": "output_text", "text": texto}]}],
            "usage": {"input_tokens": 2500, "output_tokens": 600}}


def _transporte_template(respostas, bases):
    """Devolve, para cada contexto, a resposta congelada do template do caso correspondente."""
    def transport(provider, corpo, key, timeout):
        assert key == FAKE_KEY and corpo["model"] == provider.model
        contexto = json.loads(corpo["input"][1]["content"].split("Contexto JSON:\n", 1)[1].split("\n\n")[0])
        caso = next(c for c, ctx in bases if ctx == contexto)
        return _resposta_xai(json.dumps(respostas[caso], ensure_ascii=False))
    return transport


def test_plano_tem_33_casos_e_66_chamadas(dados):
    itens = rodada.plano(dados)
    ids = [i for i, _ in itens]
    assert len(ids) == 33 and ids[28:] == ["A01", "R01", "R02", "R03", "R04"]
    assert len(ids) * rodada.EXECUCOES == 66
    contextos = dict(itens)
    assert contextos["A01"]["estimate"] == {"disponivel": False, "motivo": "modelo_nao_autorizado"}
    assert contextos["R03"] == contextos["S07"] and contextos["R04"] == contextos["S11"]
    assert "A02" not in ids and "A03" not in ids        # sem chamada ao modelo


def test_conferencias_antes_da_primeira_chamada(tmp_path, monkeypatch):
    rodada.conferir_protocolo()                          # protocolo e template conferem
    adulterado = tmp_path / "casos.json"
    adulterado.write_text("{}", encoding="utf-8")
    with pytest.raises(rodada.RodadaRecusada, match="hash congelado"):
        rodada.carregar_conjunto(adulterado)
    monkeypatch.setattr(rodada, "current_hashes", lambda: {"prompt": "outro"})
    with pytest.raises(rodada.RodadaRecusada, match="hashes do protocolo"):
        rodada.conferir_protocolo()


def test_rodada_simulada_registra_versao_custo_e_resposta(tmp_path, dados, respostas):
    itens = [i for i in rodada.plano(dados) if i[0] in ("S01", "G01", "M01")]
    ledger = lp.BudgetLedger(tmp_path / "custos.jsonl")
    saida = tmp_path / "resultados" / "aquecimento.jsonl"
    linhas = rodada.executar(itens, 2, FAKE_KEY, ledger, saida, transport=_transporte_template(respostas, itens))
    assert [(l["caso"], l["execucao"]) for l in linhas] == [
        ("S01", 1), ("G01", 1), ("M01", 1), ("S01", 2), ("G01", 2), ("M01", 2)]
    assert {l["status"] for l in linhas} == {"avaliacao"}, [(l["caso"], l["motivo"], l["verificacoes_reprovadas"]) for l in linhas]
    assert all(l["versoes_devolvidas"] == ["grok-4.3"] and l["custo_usd"] == pytest.approx(0.004625) for l in linhas)
    assert json.loads(linhas[0]["resposta"]) == respostas["S01"]
    assert len(ledger.entries()) == 6 and ledger.spent() == pytest.approx(6 * 0.004625)
    gravado = saida.read_text(encoding="utf-8")
    assert FAKE_KEY not in gravado and FAKE_KEY not in (tmp_path / "custos.jsonl").read_text(encoding="utf-8")
    texto = rodada.resumo(linhas, ledger)
    assert "chamadas registradas: 6" in texto and "'avaliacao:rodada_de_avaliacao': 6" in texto and "grok-4.3" in texto


def test_rodada_para_no_teto(tmp_path, dados, respostas):
    itens = [i for i in rodada.plano(dados) if i[0] in ("S01", "G01")]
    ledger = lp.BudgetLedger(tmp_path / "custos.jsonl", max_calls=1)
    linhas = rodada.executar(itens, 2, FAKE_KEY, ledger, tmp_path / "s.jsonl",
                             transport=_transporte_template(respostas, itens))
    assert len(linhas) == 2 and linhas[-1]["motivo"].startswith("teto_da_rodada")
    assert len(ledger.entries()) == 1                     # a segunda nem chegou à API


def test_main(monkeypatch, tmp_path, capsys):
    assert rodada.main(["--plano"]) == 0 and "33 casos x 2 execuções = 66" in capsys.readouterr().out
    assert rodada.main(["--plano", "--casos", "S01,G01,M01", "--execucoes", "1"]) == 0
    assert "3 casos x 1 execuções = 3 chamadas" in capsys.readouterr().out
    assert rodada.main(["--casos", "X99"]) == 2 and "fora do plano" in capsys.readouterr().out
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    assert rodada.main(["--casos", "S01"]) == 2 and "XAI_API_KEY ausente" in capsys.readouterr().out
    monkeypatch.setattr(rodada, "carregar_conjunto", lambda: (_ for _ in ()).throw(rodada.RodadaRecusada("x")))
    assert rodada.main([]) == 2 and "Rodada recusada: x" in capsys.readouterr().out

    monkeypatch.undo()
    monkeypatch.setenv("XAI_API_KEY", FAKE_KEY)
    monkeypatch.setattr(rodada, "PASTA", tmp_path / "resultados")
    monkeypatch.setattr(rodada.lp, "LEDGER_FILE", tmp_path / "logs" / "c.jsonl")
    chamadas = []
    monkeypatch.setattr(rodada, "executar", lambda itens, execucoes, chave, ledger, saida: chamadas.append(
        (len(itens), execucoes, chave == FAKE_KEY, saida.parent)) or [])
    assert rodada.main(["--casos", "S01,G01,M01", "--execucoes", "1", "--rotulo", "aquecimento"]) == 0
    assert chamadas == [(3, 1, True, tmp_path / "resultados")]
    assert FAKE_KEY not in capsys.readouterr().out


# ---------------------------------------------------------------- caminho do provedor no serviço

def _contexto(dados):
    return dict(rodada.plano(dados))["S01"]


def test_servico_com_provedor_exige_contador(dados):
    with pytest.raises(ValueError, match="contador de custo"):
        explain_experimental(_contexto(dados), mode=MODE_LIVE, api_key=FAKE_KEY, evaluation_run=True,
                             provider=lp.XAI, transport=lambda *a: pytest.fail("não deveria chamar"))


def test_servico_com_provedor_usa_o_transporte_da_xai_por_padrao(monkeypatch, tmp_path, dados, respostas):
    vistos = []
    monkeypatch.setattr(lp, "http_transport", lambda prov, corpo, key, timeout: vistos.append(prov.model)
                        or _resposta_xai(json.dumps(respostas["S01"], ensure_ascii=False)))
    resultado = explain_experimental(_contexto(dados), mode=MODE_LIVE, api_key=FAKE_KEY, evaluation_run=True,
                                     provider=lp.XAI, ledger=lp.BudgetLedger(tmp_path / "c.jsonl"),
                                     known_tickers=["PETR4.SA"])
    assert vistos == ["grok-4.3"] and resultado.log["model"] == "grok-4.3" and resultado.log["provider"] == "xAI"
    assert resultado.log["calls"][0]["model_version"] == "grok-4.3"


def test_servico_com_provedor_incompleto_falha_e_teto(tmp_path, dados):
    contexto = _contexto(dados)
    incompleto = explain_experimental(
        contexto, mode=MODE_LIVE, api_key=FAKE_KEY, evaluation_run=True, provider=lp.XAI,
        ledger=lp.BudgetLedger(tmp_path / "a.jsonl"), transport=lambda *a: _resposta_xai("{}", status="incomplete"))
    assert incompleto.reason == "resposta_incompleta"

    def fora(*a):
        raise ApiError(503, "ocupado")

    falha = explain_experimental(contexto, mode=MODE_LIVE, api_key=FAKE_KEY, evaluation_run=True, provider=lp.XAI,
                                 ledger=lp.BudgetLedger(tmp_path / "b.jsonl"), transport=fora, sleep=lambda s: None)
    assert falha.reason.startswith("api_indisponivel") and falha.log["attempts"] == 3

    teto = explain_experimental(contexto, mode=MODE_LIVE, api_key=FAKE_KEY, evaluation_run=True, provider=lp.XAI,
                                ledger=lp.BudgetLedger(tmp_path / "c.jsonl", cap_usd=0.0),
                                transport=lambda *a: pytest.fail("não deveria chamar"))
    assert teto.reason.startswith("teto_da_rodada") and teto.status == "indisponivel"


def test_caminho_da_7b_nao_muda():
    assert COMPLETE_FINISH == ("stop", "completed")
    mensagens = [{"role": "user", "content": "abc"}]
    assert estimate_input_tokens(mensagens) == len(json.dumps(mensagens, ensure_ascii=False)) // 3 + 1
    assert UsageLimiter().max_calls > 0 and llm_client.MODEL == "gpt-5-mini"
