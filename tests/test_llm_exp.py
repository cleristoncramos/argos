"""Camada de linguagem v1.0-experimental: política, contexto, prompt, validador e serviço (casos adversariais)."""

import copy
import json

import pytest

from core import llm_client
from core import llm_context as lc
from core import llm_exp_context as ec
from core import llm_exp_policy as policy
from core import llm_exp_prompts as ep
from core import llm_exp_service as es
from core import llm_exp_validation as ev
from core import llm_prompts, llm_service

MODELS = {"ridge-teste": {"protocolo": "teste", "ativos": ["PETR4.SA"]}}
ENGINES = {"motor-teste": {"protocolo": "teste"}}
ESTIMATE = {
    "model_id": "ridge-teste",
    "horizonte": {"valor": 20, "unidade": "pregões"},
    "data_corte": "2025-12-30",
    "ponto": lc.metric("retorno_estimado", "Retorno estimado", 1.5, "%", 2),
    "incerteza": [lc.metric("limite_inferior", "Limite inferior", -6.2, "%", 2),
                  lc.metric("limite_superior", "Limite superior", 8.4, "%", 2)],
    "desempenho_teste": [lc.metric("r2_teste", "R² fora da amostra", 0.8, "%", 2)],
}
DECISION = {"engine_id": "motor-teste", "regra_id": "R1", "codigo": "sinal_favoravel"}


def _metrics():
    return [lc.metric("retorno_total", "Retorno total", 12.34, "%", 2),
            lc.metric("volatilidade", "Volatilidade anualizada", 25.1, "%", 1)]


def ctx(**over):
    base = dict(scope="grafico", chart_type="sazonalidade", asset="PETR4.SA", asset_name="Petrobras PN",
                period_start="2021-01-04", period_end="2025-12-30", frequency="Mensal", n_observations=60,
                metrics=_metrics(), environment=policy.ENV_EXPERIMENTAL)
    base.update(over)
    return ec.build_experimental_context(**base)


def authorized_ctx(**over):
    return ctx(chart_type="previsao", estimate=ESTIMATE, decision=DECISION, model_registry=MODELS,
               engine_registry=ENGINES, **over)


def resposta(context, **over):
    data = {
        "resumo": "No período, o ativo teve retorno total de 12,34%.",
        "tratamento_do_pedido": "sem_pedido",
        "filtros_aplicados": {"ativos": [context["asset"]], "periodo_inicio": context["filters"]["period_start"],
                              "periodo_fim": context["filters"]["period_end"],
                              "frequencia": context["filters"]["frequency"]},
        "observacao_historica": {
            "rotulo": ep.BLOCK_LABELS["observacao_historica"],
            "texto": "No recorte selecionado, a volatilidade anualizada foi de 25,1%.",
            "metricas_relevantes": [{"id": "retorno_total", "valor": 12.34, "unidade": "%",
                                     "leitura": "O preço subiu no período analisado."}],
            "limite_da_evidencia": "A amostra é limitada e o resultado passado é só um recorte.",
        },
        "estimativa": {"rotulo": ep.BLOCK_LABELS["estimativa"], "situacao": "abstencao", "texto": ep.ESTIMATE_ABSTENTION,
                       "metricas_relevantes": [], "incerteza": ""},
        "conclusao_experimental": {"rotulo": ep.BLOCK_LABELS["conclusao_experimental"], "situacao": "nao_disponivel",
                                   "texto": ep.CONCLUSION_UNAVAILABLE},
        "limitacoes": ["Os dados são históricos e não indicam o futuro."],
        "o_que_nao_pode_ser_concluido": list(context["required_limits"]),
        "nota_educativa": ep.EDUCATIONAL_NOTE,
    }
    for key, value in over.items():
        data[key] = value
    return data


def resposta_autorizada(context):
    data = resposta(context, tratamento_do_pedido="sem_pedido")
    data["estimativa"] = {
        "rotulo": ep.BLOCK_LABELS["estimativa"],
        "situacao": "apresentada",
        "texto": "Para o horizonte de 20 pregões, com dados até 2025, o modelo estimou retorno de 1,5%.",
        "metricas_relevantes": [{"id": "retorno_estimado", "valor": 1.5, "unidade": "%", "leitura": "Ponto central."},
                                {"id": "limite_inferior", "valor": -6.2, "unidade": "%", "leitura": "Limite baixo."}],
        "incerteza": "O intervalo foi de -6,2% a 8,4%; no teste, o R² fora da amostra foi de 0,8%.",
    }
    data["conclusao_experimental"] = {"rotulo": ep.BLOCK_LABELS["conclusao_experimental"], "situacao": "emitida_pelo_motor",
                                      "texto": context["decision"]["texto_conclusao"]}
    return data


def check(data, context, registries=False):
    kwargs = {"model_registry": MODELS, "engine_registry": ENGINES} if registries else {}
    return ev.validate_experimental(json.dumps(data, ensure_ascii=False), context, ["PETR4.SA", "VALE3.SA"], **kwargs)


# ------------------------------------------------------------------ política

def test_politica_vigente_nao_autoriza_nada():
    assert policy.AUTHORIZED_MODELS == {} and policy.AUTHORIZED_DECISION_ENGINES == {}
    assert policy.RECOMMENDATION_ENABLED is False
    assert policy.estimate_authorization("ridge-teste", "PETR4.SA", policy.ENV_EXPERIMENTAL) == (
        False, policy.REASON_NOT_IN_REGISTRY)
    assert policy.decision_authorization("motor-teste", policy.ENV_EXPERIMENTAL) == (
        False, policy.REASON_ENGINE_NOT_IN_REGISTRY)


@pytest.mark.parametrize("model_id,asset,env,esperado", [
    ("ridge-teste", "PETR4.SA", policy.ENV_PUBLIC, (False, policy.REASON_PUBLIC)),
    (None, "PETR4.SA", policy.ENV_EXPERIMENTAL, (False, policy.REASON_NO_MODEL)),
    ("ridge-teste", "VALE3.SA", policy.ENV_EXPERIMENTAL, (False, policy.REASON_ASSET)),
    ("ridge-teste", "petr4.sa", policy.ENV_EXPERIMENTAL, (True, "")),
])
def test_autorizacao_de_estimativa(model_id, asset, env, esperado):
    assert policy.estimate_authorization(model_id, asset, env, MODELS) == esperado


def test_autorizacao_de_conclusao_e_ambiente_invalido():
    assert policy.decision_authorization("motor-teste", policy.ENV_PUBLIC, ENGINES) == (False, policy.REASON_PUBLIC)
    assert policy.decision_authorization(None, policy.ENV_EXPERIMENTAL, ENGINES) == (False, policy.REASON_NO_ENGINE)
    assert policy.decision_authorization("motor-teste", policy.ENV_EXPERIMENTAL, ENGINES) == (True, "")
    with pytest.raises(ValueError, match="Ambiente"):
        policy.estimate_authorization("x", "PETR4.SA", "producao")


def test_impressao_da_politica_muda_com_o_registro():
    assert policy.policy_fingerprint() != policy.policy_fingerprint(models=MODELS)
    assert policy.policy_fingerprint() != policy.policy_fingerprint(recommendation_enabled=True)


# ------------------------------------------------------------------ contexto

def test_contexto_sem_autorizacao_nao_leva_numeros_da_estimativa():
    context = ctx(chart_type="previsao", estimate=ESTIMATE, decision=DECISION)
    assert context["estimate"] == {"disponivel": False, "motivo": policy.REASON_NOT_IN_REGISTRY}
    assert context["decision"] == {"disponivel": False, "motivo": policy.REASON_ENGINE_NOT_IN_REGISTRY}
    assert "1.5" not in json.dumps(context) and ec.estimate_allowed_numbers(context) == []
    assert context["required_limits"] == [ec.CHART_LIMITS["previsao"]]


def test_ambiente_publico_descarta_estimativa_mesmo_registrada():
    context = ctx(chart_type="previsao", estimate=ESTIMATE, decision=DECISION, model_registry=MODELS,
                  engine_registry=ENGINES, environment=policy.ENV_PUBLIC)
    assert context["estimate"]["disponivel"] is False and context["estimate"]["motivo"] == policy.REASON_PUBLIC
    assert context["decision"]["disponivel"] is False


def test_contexto_autorizado_traz_estimativa_e_texto_do_motor():
    context = authorized_ctx()
    assert context["estimate"]["disponivel"] and context["estimate"]["ponto_id"] == "retorno_estimado"
    assert "regra experimental R1" in context["decision"]["texto_conclusao"]
    assert 20.0 in ec.estimate_allowed_numbers(context) and 2025.0 in ec.estimate_allowed_numbers(context)


def test_conclusao_sem_estimativa_autorizada_nao_e_comunicada():
    context = ctx(decision=DECISION, engine_registry=ENGINES)
    assert context["decision"] == {"disponivel": False, "motivo": "conclusao_sem_estimativa_autorizada"}


def test_sintese_usa_o_limite_da_sintese():
    context = ctx(scope="sintese_ativo", chart_type=None, charts=["preco_medias", "drawdown", "preco_medias"])
    assert context["charts"] == ["preco_medias", "drawdown"] and context["required_limits"] == [ec.SYNTHESIS_LIMIT]


@pytest.mark.parametrize("over,mensagem", [
    ({"scope": "pagina"}, "Escopo"),
    ({"chart_type": "pizza"}, "gráfico"),
    ({"scope": "sintese_ativo", "chart_type": None, "charts": []}, "síntese"),
    ({"scope": "sintese_ativo", "chart_type": None, "charts": ["pizza"]}, "síntese"),
    ({"status": "parcial"}, "Status"),
    ({"frequency": "Horária"}, "Frequência"),
    ({"asset": "  "}, "ativo"),
    ({"period_start": "2021/01/04"}, "AAAA-MM-DD"),
    ({"period_start": "2026-01-01"}, "posterior"),
    ({"n_observations": -1}, "n_observations"),
    ({"status": "dados_insuficientes"}, "insuficientes"),
    ({"limitation_flags": ["chuva"]}, "Sinalizador"),
    ({"user_request": ("palpite", "x")}, "pedido"),
    ({"metrics": _metrics() + [_metrics()[0]]}, "repetidos"),
])
def test_contexto_invalido(over, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        ctx(**over)


@pytest.mark.parametrize("estimativa,mensagem", [
    ({**ESTIMATE, "incerteza": []}, "incerteza"),
    ({**ESTIMATE, "horizonte": {"valor": 0, "unidade": "pregões"}}, "horizonte"),
    ({**ESTIMATE, "horizonte": {"valor": 20}}, "horizonte"),
])
def test_estimativa_autorizada_incompleta_e_recusada_pelo_argos(estimativa, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        ctx(estimate=estimativa, model_registry=MODELS)


def test_conclusao_autorizada_com_codigo_desconhecido_e_recusada():
    with pytest.raises(ValueError, match="código"):
        ctx(estimate=ESTIMATE, decision={**DECISION, "codigo": "compre"}, model_registry=MODELS,
            engine_registry=ENGINES)


# ------------------------------------------------------------------ prompt

def test_prompt_novo_e_v06_intacta():
    assert ep.PROMPT_VERSION == "v1.0-experimental"
    assert llm_prompts.PROMPT_VERSION == "v0.6" and llm_prompts.prompt_fingerprint() == "e3b3574b7430"
    assert ep.prompt_fingerprint() != llm_prompts.prompt_fingerprint() and len(ep.prompt_fingerprint()) == 12
    assert ep.REFUSAL_RECOMMENDATION == llm_prompts.REFUSAL_TEXT
    assert ep.response_format()["json_schema"]["strict"] is True


def test_mensagens_com_e_sem_pedido():
    assert "local" in ep.user_prompt(ctx()) and "síntese" in ep.user_prompt(
        ctx(scope="sintese_ativo", chart_type=None, charts=["drawdown"]))
    pedido = ep.build_messages(ctx(user_request=("garantia", "Garante lucro?")))
    assert pedido[0]["role"] == "system" and "regra 10" in pedido[1]["content"]


def test_cliente_v06_mantem_o_corpo_padrao():
    seen = {}

    def transport(payload, key, timeout):
        seen["payload"] = payload
        return {"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}], "usage": {}}

    context = {"analysis_type": "risco_retorno"}
    llm_client.call_model(context | lc.build_context(analysis_type="risco_retorno", assets=["PETR4.SA"],
                                                     period_start="2021-01-04", period_end="2021-12-30",
                                                     frequency="Diário", n_observations=200), "k", transport,
                          sleep=lambda s: None)
    assert seen["payload"]["response_format"] == llm_prompts.response_format()


# ------------------------------------------------------------------ validador: casos válidos

def test_resposta_valida_sem_estimativa():
    result = check(resposta(ctx()), ctx())
    assert result.ok, result.as_dict()
    assert set(ev.CHECK_NAMES) == {c.name for c in result.checks}


def test_resposta_valida_com_estimativa_e_conclusao_autorizadas():
    context = authorized_ctx()
    result = check(resposta_autorizada(context), context, registries=True)
    assert result.ok, result.as_dict()


def test_dados_insuficientes_validos():
    context = ctx(status="dados_insuficientes", metrics=[], limitation_flags=["poucas_observacoes"])
    data = resposta(context, resumo="Os dados são insuficientes para a análise neste recorte.",
                    limitacoes=["Há poucas observações no período."])
    data["observacao_historica"]["metricas_relevantes"] = []
    data["observacao_historica"]["texto"] = "O recorte tem poucas observações."
    assert check(data, context).ok


# ------------------------------------------------------------------ validador: adversariais

def test_contexto_vazio_ou_resposta_vazia():
    result = ev.validate_experimental("", ctx())
    assert not result.ok and result.failed[0] == "json_valido" and len(result.failed) == len(ev.CHECK_NAMES)


def test_dado_faltante_com_metrica_citada_reprova():
    context = ctx(status="dados_insuficientes", metrics=[])
    result = check(resposta(context), context)
    assert "metricas_por_camada" in result.failed


def test_numero_divergente_reprova():
    context = ctx()
    data = resposta(context)
    data["observacao_historica"]["metricas_relevantes"][0]["valor"] = 12.5
    assert "metricas_por_camada" in check(data, context).failed
    data = resposta(context, resumo="No período, o ativo teve retorno total de 13%.")
    assert "valores_rastreaveis" in check(data, context).failed


def test_dados_insuficientes_sem_aviso_e_metricas_omitidas_reprovam():
    context = ctx(status="dados_insuficientes", metrics=[])
    data = resposta(context)
    data["observacao_historica"]["metricas_relevantes"] = []
    assert "metricas_por_camada" in check(data, context).failed     # resumo sem o aviso
    context = ctx()
    data = resposta(context)
    data["observacao_historica"]["metricas_relevantes"] = []
    assert "metricas_por_camada" in check(data, context).failed     # nenhuma métrica histórica


def test_metrica_inexistente_reprova():
    context = ctx()
    data = resposta(context)
    data["observacao_historica"]["metricas_relevantes"][0]["id"] = "sharpe"
    assert "metricas_por_camada" in check(data, context).failed


def test_numero_historico_usado_como_estimativa_reprova():
    context = authorized_ctx()
    data = resposta_autorizada(context)
    data["estimativa"]["incerteza"] = "O intervalo foi de -6,2% a 12,34%."
    assert "valores_rastreaveis" in check(data, context, registries=True).failed


def test_estimativa_sem_autorizacao_reprova():
    context = ctx(chart_type="previsao", estimate=ESTIMATE)
    data = resposta_autorizada(authorized_ctx())
    data["conclusao_experimental"] = resposta(context)["conclusao_experimental"]
    failed = check(data, context).failed
    assert "estimativa_autorizada" in failed


def test_estimativa_autorizada_sem_incerteza_reprova():
    context = authorized_ctx()
    data = resposta_autorizada(context)
    data["estimativa"]["metricas_relevantes"] = data["estimativa"]["metricas_relevantes"][:1]
    assert "estimativa_autorizada" in check(data, context, registries=True).failed


def test_abstencao_com_texto_proprio_reprova():
    context = ctx()
    data = resposta(context)
    data["estimativa"]["texto"] = "Não há estimativa."
    assert "estimativa_autorizada" in check(data, context).failed


def test_futuro_na_camada_historica_reprova():
    context = ctx()
    data = resposta(context)
    data["observacao_historica"]["texto"] = "O preço vai subir no próximo mês."
    failed = check(data, context).failed
    assert "sem_futuro_fora_da_estimativa" in failed and "sem_termos_proibidos" in failed


def test_conclusao_propria_reprova():
    context = ctx()
    data = resposta(context)
    data["conclusao_experimental"] = {"rotulo": ep.BLOCK_LABELS["conclusao_experimental"], "situacao": "emitida_pelo_motor", "texto": "Sinal favorável."}
    assert "conclusao_autorizada" in check(data, context).failed
    context = authorized_ctx()
    data = resposta_autorizada(context)
    data["conclusao_experimental"]["texto"] += " Vale a pena."
    assert "conclusao_autorizada" in check(data, context, registries=True).failed


def test_conclusao_indisponivel_sem_texto_fixo_reprova():
    context = ctx()
    data = resposta(context)
    data["conclusao_experimental"]["texto"] = "Sem conclusão."
    assert "conclusao_autorizada" in check(data, context).failed


def test_pedido_de_garantia_de_lucro():
    context = ctx(user_request=("garantia", "Garante que vou lucrar?"))
    data = resposta(context, resumo=ep.REFUSAL_GUARANTEE, tratamento_do_pedido="recusa_garantia",
                    o_que_nao_pode_ser_concluido=[ep.REFUSAL_LIMIT])
    data["observacao_historica"] = {"rotulo": ep.BLOCK_LABELS["observacao_historica"], "texto": ep.NOT_APPLICABLE, "metricas_relevantes": [],
                                    "limite_da_evidencia": ep.REFUSAL_LIMIT}
    assert check(data, context).ok, check(data, context).as_dict()
    promessa = copy.deepcopy(data)
    promessa["resumo"] = "Com este ativo o retorno garantido é certo."
    failed = check(promessa, context).failed
    assert "sem_promessa_nem_persuasao" in failed and "pedido_tratado" in failed


def test_pedido_de_recomendacao_direta():
    context = ctx(user_request=("recomendacao", "Devo comprar PETR4 agora?"))
    data = resposta(context, resumo=ep.REFUSAL_RECOMMENDATION, tratamento_do_pedido="recusa_recomendacao",
                    o_que_nao_pode_ser_concluido=[ep.REFUSAL_LIMIT])
    data["observacao_historica"] = {"rotulo": ep.BLOCK_LABELS["observacao_historica"], "texto": ep.NOT_APPLICABLE, "metricas_relevantes": [],
                                    "limite_da_evidencia": ep.REFUSAL_LIMIT}
    assert check(data, context).ok
    atende = resposta(context, resumo="Compre agora, aproveite a queda.")
    failed = check(atende, context).failed
    assert {"sem_termos_proibidos", "sem_promessa_nem_persuasao", "pedido_tratado"} <= set(failed)
    com_numero = copy.deepcopy(data)
    com_numero["limitacoes"] = ["No período foram 60 observações."]
    assert "valores_rastreaveis" in check(com_numero, context).failed
    com_metrica = copy.deepcopy(data)
    com_metrica["observacao_historica"]["metricas_relevantes"] = resposta(context)["observacao_historica"][
        "metricas_relevantes"]
    assert "metricas_por_camada" in check(com_metrica, context).failed


def test_pedido_de_previsao_sem_e_com_modelo():
    context = ctx(user_request=("previsao", "Quanto vai render?"))
    data = resposta(context, tratamento_do_pedido="previsao_abstencao",
                    resumo=ep.ESTIMATE_ABSTENTION + " O retorno total foi de 12,34%.")
    assert check(data, context).ok
    assert "pedido_tratado" in check(resposta(context, tratamento_do_pedido="previsao_abstencao"), context).failed
    context = authorized_ctx(user_request=("previsao", "Quanto vai render?"))
    data = resposta_autorizada(context)
    data["tratamento_do_pedido"] = "previsao_explicada"
    assert check(data, context, registries=True).ok
    data["estimativa"] = resposta(context)["estimativa"]
    assert "pedido_tratado" in check(data, context, registries=True).failed


def test_tratamento_sem_pedido_reprova():
    context = ctx()
    assert "pedido_tratado" in check(resposta(context, tratamento_do_pedido="recusa_garantia"), context).failed


def test_limite_do_grafico_ausente_reprova():
    context = ctx()
    data = resposta(context, o_que_nao_pode_ser_concluido=["Outra frase qualquer."])
    assert "limite_da_evidencia" in check(data, context).failed


def test_limitacao_sinalizada_ausente_reprova():
    context = ctx(limitation_flags=["poucos_anos"])
    assert "limitacoes" in check(resposta(context), context).failed


def test_ativo_e_periodo_divergentes_reprovam():
    context = ctx()
    data = resposta(context)
    data["filtros_aplicados"]["ativos"] = ["VALE3.SA"]
    data["filtros_aplicados"]["frequencia"] = "Diário"
    failed = check(data, context).failed
    assert "ativo_consistente" in failed and "periodo_frequencia" in failed
    data = resposta(context, resumo="No período, PETR4.SA e VALE3.SA tiveram retorno total de 12,34%.")
    assert "ativo_consistente" in check(data, context).failed


def test_recomendacao_propria_reprova():
    context = ctx()
    data = resposta(context)
    data["limitacoes"] = ["Convém investir aos poucos."]
    assert "sem_recomendacao_propria" in check(data, context).failed


def test_contexto_adulterado_reprova_na_politica():
    context = authorized_ctx()
    data = resposta_autorizada(context)
    assert "politica_de_liberacao" in check(data, context, registries=False).failed
    adulterado = copy.deepcopy(context)
    adulterado["release"]["recomendacao_habilitada"] = True
    assert "politica_de_liberacao" in check(data, adulterado, registries=True).failed


def _estrutura(data, caminho, valor):
    alvo = data
    for chave in caminho[:-1]:
        alvo = alvo[chave]
    if valor is KeyError:
        del alvo[caminho[-1]]
    else:
        alvo[caminho[-1]] = valor
    return data


@pytest.mark.parametrize("caminho,valor", [
    (("resumo",), KeyError),
    (("resumo",), "   "),
    (("tratamento_do_pedido",), "outro"),
    (("filtros_aplicados", "frequencia"), KeyError),
    (("filtros_aplicados", "ativos"), "PETR4.SA"),
    (("observacao_historica", "limite_da_evidencia"), KeyError),
    (("estimativa", "incerteza"), KeyError),
    (("conclusao_experimental", "situacao"), KeyError),
    (("observacao_historica", "texto"), ""),
    (("estimativa", "incerteza"), 3),
    (("estimativa", "situacao"), "parcial"),
    (("observacao_historica", "metricas_relevantes"), [{"id": "x"}]),
    (("observacao_historica", "metricas_relevantes"), [{"id": "x", "valor": True, "unidade": "%", "leitura": "a"}]),
    (("observacao_historica", "metricas_relevantes"), [{"id": 1, "valor": 1, "unidade": "%", "leitura": "a"}]),
    (("observacao_historica", "metricas_relevantes"), "lista"),
    (("limitacoes",), []),
    (("nota_educativa",), "Outra nota."),
    (("observacao_historica", "rotulo"), "Observação histórica"),
    (("conclusao_experimental", "rotulo"), KeyError),
])
def test_estrutura_invalida_reprova(caminho, valor):
    context = ctx()
    result = check(_estrutura(resposta(context), caminho, valor), context)
    assert result.failed[0] == "campos_obrigatorios" and len(result.failed) == len(ev.CHECK_NAMES) - 1


# ------------------------------------------------------------------ serviço

def _transport(conteudo, finish="stop"):
    def transport(payload, key, timeout):
        transport.payload = payload
        return {"choices": [{"message": {"content": conteudo}, "finish_reason": finish}],
                "usage": {"prompt_tokens": 1000, "completion_tokens": 400}}
    return transport


def explain(context, **kw):
    params = dict(mode=es.MODE_LIVE, api_key="sk-teste-secreto", known_tickers=["PETR4.SA"],
                  approved_fingerprint=ep.prompt_fingerprint(), sleep=lambda s: None)
    params.update(kw)
    return es.explain_experimental(context, **params)


def test_servico_mostra_resposta_valida_e_registra_sem_segredo():
    context = ctx()
    logs = []
    result = explain(context, transport=_transport(json.dumps(resposta(context), ensure_ascii=False)),
                     log_sink=logs.append)
    assert result.status == es.STATUS_OK and result.shown
    registro = json.dumps(logs[0], ensure_ascii=False)
    assert "sk-teste-secreto" not in registro and "12,34" not in registro
    assert logs[0]["protocol_family"] == "v1.0-experimental" and logs[0]["estimate_available"] is False
    assert logs[0]["policy_fingerprint"] == policy.policy_fingerprint()


def test_servico_bloqueia_resposta_invalida_com_fallback():
    context = ctx()
    data = resposta(context, resumo="Compre agora.")
    result = explain(context, transport=_transport(json.dumps(data, ensure_ascii=False)))
    assert result.status == es.STATUS_BLOCKED and result.fallback_text == llm_service.FALLBACK_TEXT
    assert "sem_termos_proibidos" in result.log["failed_checks"]


def test_falha_do_provedor_vira_indisponivel():
    def falha(payload, key, timeout):
        raise llm_client.ApiError(503, "indisponível")
    result = explain(ctx(), transport=falha)
    assert result.status == es.STATUS_UNAVAILABLE and result.reason.startswith("api_indisponivel")
    assert result.log["attempts"] == llm_client.MAX_RETRIES + 1


def test_resposta_cortada_e_bloqueada():
    result = explain(ctx(), transport=_transport("{}", finish="length"))
    assert result.reason == "resposta_incompleta"


@pytest.mark.parametrize("context,kw,motivo", [
    ({}, {}, "contexto_invalido"),
    ({**ctx(), "protocol_family": "v0.6"}, {}, "familia_de_protocolo_divergente"),
    (ctx(environment=policy.ENV_PUBLIC), {}, "fora_do_ambiente_experimental"),
    (ctx(user_request=("garantia", "x")), {}, "entrada_livre_nao_permitida"),
    (ctx(), {"approved_fingerprint": None}, "protocolo_nao_aprovado"),
    (ctx(), {"approved_fingerprint": "000000000000"}, "protocolo_nao_aprovado"),
])
def test_bloqueios_antes_da_chamada(context, kw, motivo):
    def nunca(*a):
        raise AssertionError("não deveria chamar o provedor")
    result = explain(context, transport=nunca, **kw)
    assert result.status == es.STATUS_BLOCKED and result.reason == motivo


def test_protocolo_ainda_nao_aprovado_por_padrao():
    assert es.APPROVED_FINGERPRINT is None
    result = es.explain_experimental(ctx(), mode=es.MODE_LIVE, api_key="k")
    assert result.reason == "protocolo_nao_aprovado"


def test_rodada_de_avaliacao_nunca_exibe():
    context = ctx(user_request=("garantia", "Garante lucro?"))
    data = resposta(context, resumo=ep.REFUSAL_GUARANTEE, tratamento_do_pedido="recusa_garantia",
                    o_que_nao_pode_ser_concluido=[ep.REFUSAL_LIMIT])
    data["observacao_historica"] = {"rotulo": ep.BLOCK_LABELS["observacao_historica"], "texto": ep.NOT_APPLICABLE, "metricas_relevantes": [],
                                    "limite_da_evidencia": ep.REFUSAL_LIMIT}
    result = explain(context, transport=_transport(json.dumps(data, ensure_ascii=False)), evaluation_run=True,
                     approved_fingerprint=None)
    assert result.status == es.STATUS_EVALUATION and not result.shown and all(result.log["validation"].values())
    demo = {llm_service.context_key(context): json.dumps(data, ensure_ascii=False)}
    result = explain(context, mode=es.MODE_DEMO, demo_store=demo, evaluation_run=True, approved_fingerprint=None)
    assert result.status == es.STATUS_EVALUATION and not result.shown


def test_modos_desligado_demo_sem_chave_e_limite():
    context = ctx()
    assert explain(context, mode=es.MODE_OFF).status == es.STATUS_OFF
    with pytest.raises(ValueError, match="Modo"):
        explain(context, mode="turbo")
    assert explain(context, mode=es.MODE_DEMO, demo_store={}).reason == "demo_sem_resposta_salva"
    demo = {llm_service.context_key(context): json.dumps(resposta(context), ensure_ascii=False)}
    assert explain(context, mode=es.MODE_DEMO, demo_store=demo).status == es.STATUS_DEMO
    assert explain(context, api_key=None).reason == "sem_chave"
    cheio = llm_service.UsageLimiter(max_calls=0)
    assert explain(context, limiter=cheio).reason == "limite_de_uso"


def test_servico_aceita_resposta_ja_decodificada():
    context = ctx()
    demo = {llm_service.context_key(context): resposta(context)}
    assert explain(context, mode=es.MODE_DEMO, demo_store=demo).shown


# ------------------------------------------------------------------ DL1-B: correções 1 e 4

def test_textos_fixos_com_marca_de_experimental_e_motor_intacto():
    for texto in (ep.REFUSAL_GUARANTEE, ep.ESTIMATE_ABSTENTION, ep.CONCLUSION_UNAVAILABLE):
        assert "experimental" in texto
    assert "estratégia experimental" in ep.CONCLUSION_UNAVAILABLE and "decisão experimental" in ep.CONCLUSION_UNAVAILABLE
    assert ec.CONCLUSION_TEXTS["sinal_favoravel"].startswith("Para o horizonte selecionado, o modelo produziu")
    assert es.FALLBACK_TEXT == ep.FALLBACK_TEXT


def test_hashes_separados_de_prompt_esquema_e_textos():
    hashes = ep.fixed_text_hashes()
    assert set(hashes) == set(ep.APPROVED_TEXT_IDS) | {"conjunto"}
    assert len({ep.prompt_hash(), ep.schema_hash(), ep.prompt_fingerprint(), hashes["conjunto"]}) == 4
    assert all(len(h) == 12 for h in hashes.values())


SAZONAL = ("No recorte selecionado, outubro apresentou média histórica superior à de setembro. "
           "Entretanto, houve anos com resultado negativo e a amostra é limitada.")


@pytest.mark.parametrize("texto,ok", [
    (SAZONAL + " Isso não indica que o próximo período repetirá o resultado.", True),
    ("A mediana de outubro foi positiva em poucos anos; o resultado pode não se repetir.", True),
    (SAZONAL, False),                                                           # sem a não repetição
    ("A média histórica de outubro foi positiva. Isso não indica que o próximo período repetirá o resultado.",
     False),                                                                    # sem a amostra limitada
    ("O preço ficou acima das médias móveis no período.", True),               # indicador, não média histórica
])
def test_ressalva_sobre_media_historica(texto, ok):
    context = ctx()
    data = resposta(context)
    data["observacao_historica"]["texto"] = texto
    data["observacao_historica"]["limite_da_evidencia"] = "O resultado depende do recorte escolhido."
    assert ("ressalva_media_historica" not in check(data, context).failed) is ok


def test_ressalva_vale_por_paragrafo():
    context = ctx()
    data = resposta(context, resumo="A média de outubro foi positiva no período.")
    data["observacao_historica"]["limite_da_evidencia"] = (
        "A amostra é limitada e o resultado não se repete necessariamente.")
    assert "ressalva_media_historica" in check(data, context).failed       # ressalva em outro parágrafo
    data["resumo"] = "A média de outubro foi positiva, com amostra limitada; isso pode não se repetir."
    assert check(data, context).ok, check(data, context).as_dict()


@pytest.mark.parametrize("frase,ok", [
    ("O sinal do indicador não garante reversão do preço.", True),
    ("O RSI subiu no período analisado.", True),
    ("A estratégia é recomendada para este ativo.", False),
    ("O modelo foi aprovado e é confiável.", False),
])
def test_atribuicao_a_indicador_estrategia_ou_modelo(frase, ok):
    context = ctx()
    data = resposta(context)
    data["limitacoes"] = [frase]
    assert ("sem_recomendacao_propria" not in check(data, context).failed) is ok


def _sequencia(*conteudos):
    respostas = list(conteudos)

    def transport(payload, key, timeout):
        transport.chamadas = getattr(transport, "chamadas", 0) + 1
        return {"choices": [{"message": {"content": respostas.pop(0)}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 1000, "completion_tokens": 400}}
    return transport


def test_uma_regeneracao_quando_so_falta_a_ressalva():
    context = ctx()
    sem = resposta(context, resumo="A média de outubro foi positiva no período.")
    com = resposta(context, resumo="A média de outubro foi positiva, com amostra limitada; isso pode não se repetir.")
    transport = _sequencia(json.dumps(sem, ensure_ascii=False), json.dumps(com, ensure_ascii=False))
    result = explain(context, transport=transport)
    assert result.shown and result.log["regenerations"] == 1 and transport.chamadas == 2
    assert result.log["input_tokens"] == 2000 and result.log["attempts"] == 2
    transport = _sequencia(json.dumps(sem, ensure_ascii=False), json.dumps(sem, ensure_ascii=False))
    result = explain(context, transport=transport)
    assert result.status == es.STATUS_BLOCKED and result.log["regenerations"] == 1 and transport.chamadas == 2


def test_outras_falhas_nao_regeneram_e_limite_impede_regeneracao():
    context = ctx()
    ruim = resposta(context, resumo="Compre agora; a média de outubro foi positiva.")
    transport = _sequencia(json.dumps(ruim, ensure_ascii=False))
    assert explain(context, transport=transport).log["regenerations"] == 0 and transport.chamadas == 1
    sem = resposta(context, resumo="A média de outubro foi positiva no período.")
    transport = _sequencia(json.dumps(sem, ensure_ascii=False))
    result = explain(context, transport=transport, limiter=llm_service.UsageLimiter(max_calls=1))
    assert result.status == es.STATUS_BLOCKED and transport.chamadas == 1


def test_falha_do_provedor_na_regeneracao():
    context = ctx()
    sem = json.dumps(resposta(context, resumo="A média de outubro foi positiva no período."), ensure_ascii=False)
    estado = {"n": 0}

    def transport(payload, key, timeout):
        estado["n"] += 1
        if estado["n"] > 1:
            raise llm_client.ApiError(503, "fora")
        return {"choices": [{"message": {"content": sem}, "finish_reason": "stop"}], "usage": {}}
    result = explain(context, transport=transport)
    assert result.status == es.STATUS_UNAVAILABLE and result.log["regenerations"] == 1


def test_registro_traz_hashes_separados():
    logs = []
    explain(ctx(), mode=es.MODE_OFF, log_sink=logs.append)
    assert logs[0]["prompt_hash"] == ep.prompt_hash() and logs[0]["schema_hash"] == ep.schema_hash()
    assert logs[0]["fixed_texts_hash"] == ep.fixed_text_hashes()["conjunto"]
