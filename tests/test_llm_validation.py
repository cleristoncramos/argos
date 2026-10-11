"""Validador da resposta da explicação assistida."""

import copy
import json

import pytest

from core import llm_context as lc
from core import llm_prompts as lp
from core import llm_validation as lv

TICKERS = ["AAPL", "BTC-USD", "PETR4.SA", "^GSPC", "GC=F"]


def _context(**over):
    base = dict(
        analysis_type="risco_retorno",
        assets=["AAPL"],
        period_start="2020-01-01",
        period_end="2024-12-31",
        frequency="Diário",
        n_observations=1250,
        metrics=[
            lc.metric("retorno_total", "Retorno total", 180.46, "%"),
            lc.metric("volatilidade", "Volatilidade anualizada", 31.2, "%", decimals=1),
        ],
        asset_names={"AAPL": "Apple Inc."},
    )
    base.update(over)
    return lc.build_context(**base)


def _good(**over):
    data = {
        "resumo": "Entre 2020 e 2024, o preço de AAPL variou 180,46% no histórico analisado.",
        "recusa_recomendacao": False,
        "filtros_aplicados": {
            "ativos": ["AAPL"],
            "periodo_inicio": "2020-01-01",
            "periodo_fim": "2024-12-31",
            "frequencia": "Diário",
        },
        "o_que_o_grafico_mostra": "Mostra como o preço mudou ao longo do período, em 1250 observações.",
        "metricas_relevantes": [
            {"id": "retorno_total", "valor": 180.46, "unidade": "%", "leitura": "Variação total do preço."},
            {"id": "volatilidade", "valor": 31.2, "unidade": "%", "leitura": "Quanto os retornos oscilaram."},
        ],
        "limitacoes": ["Resultados passados descrevem o histórico e não indicam o futuro."],
        "o_que_nao_pode_ser_concluido": ["Não é possível concluir que o ativo é adequado para alguém."],
        "nota_educativa": "Volatilidade mede a oscilação dos retornos.",
    }
    data.update(over)
    return data


def _run(data=None, ctx=None, raw=None):
    ctx = ctx or _context()
    payload = raw if raw is not None else json.dumps(data if data is not None else _good())
    return lv.validate_response(payload, ctx, TICKERS)


def _fails(data=None, ctx=None, raw=None):
    return _run(data, ctx, raw).failed


def test_good_response_passes():
    result = _run()
    assert result.ok, result.as_dict()
    assert result.metrics_cited == 2 and result.metrics_correct == 2
    assert result.passed("json_valido")
    assert [c.name for c in result.checks] == list(lv.CHECK_NAMES)
    assert result.as_dict()["ok"] is True


def test_accepts_dict_input():
    assert lv.validate_response(_good(), _context(), TICKERS).ok


@pytest.mark.parametrize("raw", ["não é json", "[1, 2]", None, "123"])
def test_invalid_json(raw):
    result = lv.validate_response(raw, _context(), TICKERS)
    assert result.failed[0] == "json_valido"
    assert len(result.checks) == len(lv.CHECK_NAMES)
    assert not result.ok
    assert "JSON" in result.as_dict()["details"]["json_valido"]


def _mutated(path, value):
    data = copy.deepcopy(_good())
    target = data
    for key in path[:-1]:
        target = target[key]
    if value is lv:  # remove
        del target[path[-1]]
    else:
        target[path[-1]] = value
    return data


@pytest.mark.parametrize(
    "path,value",
    [
        (["resumo"], lv),
        (["resumo"], ""),
        (["resumo"], 5),
        (["resumo"], "x" * 800),
        (["o_que_o_grafico_mostra"], "x" * 1000),
        (["recusa_recomendacao"], "não"),
        (["filtros_aplicados"], "texto"),
        (["filtros_aplicados", "frequencia"], lv),
        (["filtros_aplicados", "ativos"], "AAPL"),
        (["metricas_relevantes"], "x"),
        (["metricas_relevantes"], [{"id": "retorno_total"}]),
        (["metricas_relevantes"], ["texto"]),
        (["metricas_relevantes"], [{"id": "a", "valor": "1", "unidade": "%", "leitura": "x"}]),
        (["metricas_relevantes"], [{"id": "a", "valor": True, "unidade": "%", "leitura": "x"}]),
        (["metricas_relevantes"], [{"id": 1, "valor": 1, "unidade": "%", "leitura": "x"}]),
        (["metricas_relevantes"], [{"id": "a", "valor": 1, "unidade": "%", "leitura": "x"}] * 13),
        (["limitacoes"], []),
        (["limitacoes"], "texto"),
        (["limitacoes"], ["a"] * 7),
        (["limitacoes"], [" "]),
        (["limitacoes"], ["x" * 1000]),
        (["o_que_nao_pode_ser_concluido"], [1]),
    ],
)
def test_structure_failures(path, value):
    result = _run(_mutated(path, value))
    assert result.failed[0] == "campos_obrigatorios"
    assert len(result.checks) == len(lv.CHECK_NAMES)


def test_asset_mismatch_and_other_asset():
    assert "ativo_consistente" in _fails(_mutated(["filtros_aplicados", "ativos"], ["BTC-USD"]))
    data = _good(resumo="AAPL variou 180,46%, bem mais que BTC-USD.")
    result = _run(data)
    assert "ativo_consistente" in result.failed
    assert "BTC-USD" in result.as_dict()["details"]["ativo_consistente"]


def test_short_or_lowercase_tickers_do_not_cause_false_alarms():
    ctx = _context()
    data = _good(resumo="A volatilidade de AAPL foi de 31,2% no período.")
    # "A" (código curto) e "gc" em minúsculas não contam como outro ativo
    result = lv.validate_response(json.dumps(data), ctx, TICKERS + ["A", "T", "gc=f"])
    assert result.passed("ativo_consistente")
    data = _good(resumo="Diferente de GC=F, AAPL variou 180,46%.")
    result = lv.validate_response(json.dumps(data), ctx, TICKERS + ["A"])
    assert not result.passed("ativo_consistente")


def test_period_and_frequency():
    assert "periodo_frequencia" in _fails(_mutated(["filtros_aplicados", "periodo_inicio"], "2019-01-01"))
    assert "periodo_frequencia" in _fails(_mutated(["filtros_aplicados", "periodo_fim"], "2024-06-30"))
    assert "periodo_frequencia" in _fails(_mutated(["filtros_aplicados", "frequencia"], "Mensal"))
    assert "periodo_frequencia" not in _fails(_mutated(["filtros_aplicados", "frequencia"], "diario"))


def test_metric_checks():
    bad_id = _good(metricas_relevantes=[{"id": "sharpe", "valor": 1.0, "unidade": "", "leitura": "x"}])
    assert "inexistente" in _run(bad_id).as_dict()["details"]["metricas_no_contexto"]
    bad_value = _good(metricas_relevantes=[{"id": "retorno_total", "valor": 150.0, "unidade": "%", "leitura": "x"}])
    result = _run(bad_value)
    assert "metricas_no_contexto" in result.failed
    assert result.metrics_correct == 0
    bad_unit = _good(metricas_relevantes=[{"id": "retorno_total", "valor": 180.46, "unidade": "R$", "leitura": "x"}])
    assert "metricas_no_contexto" in _fails(bad_unit)
    none = _good(metricas_relevantes=[])
    assert "nenhuma métrica" in _run(none).as_dict()["details"]["metricas_no_contexto"]


def test_untraceable_numbers():
    result = _run(_good(resumo="Em 2024 o preço variou 180,46% e subiu 42% em um ano."))
    assert "valores_rastreaveis" in result.failed
    assert "42" in result.as_dict()["details"]["valores_rastreaveis"]


def test_traceable_numbers_forms():
    ok = _good(
        resumo="De 2020-01-01 a 31/12/2024, com 1.250 observações, AAPL teve 180,46% (volatilidade 31,2%), de 100%.",
    )
    assert "valores_rastreaveis" not in _fails(ok)
    assert "valores_rastreaveis" not in _fails(_good(resumo="Variação de -180,46% no exemplo."))
    assert "valores_rastreaveis" not in _fails(_good(resumo="O 1º gráfico mostra a série de AAPL."))
    # arredondamento por menos casas decimais é aceito
    assert "valores_rastreaveis" not in _fails(_good(resumo="A volatilidade foi de cerca de 31%."))
    assert "valores_rastreaveis" in _fails(_good(resumo="A volatilidade foi de 33,2%."))


def test_decimal_point_numbers_are_not_read_as_thousands():
    # "0.056" é decimal (milhar nunca começa com zero); "1.250" vale 1250 ou 1,25
    ctx = _context(metrics=[lc.metric("retorno_medio", "Retorno médio", 0.056, "%", 3)])
    data = _good(
        resumo="O retorno médio foi de 0.056% por observação, em 1.250 observações.",
        metricas_relevantes=[{"id": "retorno_medio", "valor": 0.056, "unidade": "%", "leitura": "Média."}],
    )
    assert "valores_rastreaveis" not in lv.validate_response(json.dumps(data), ctx, TICKERS).failed
    data = _good(
        resumo="Com 1250 observações o retorno médio foi de 0,056%.",
        metricas_relevantes=data["metricas_relevantes"],
    )
    assert "valores_rastreaveis" not in lv.validate_response(json.dumps(data), ctx, TICKERS).failed
    # 12.345,6 (milhar com decimal brasileiro) que não está no contexto continua reprovado
    bad = _good(resumo="A variação foi de 12.345,6 pontos.", metricas_relevantes=data["metricas_relevantes"])
    assert "valores_rastreaveis" in lv.validate_response(json.dumps(bad), ctx, TICKERS).failed
    big = _context(extra_numbers=[1250.5], metrics=ctx["metrics"])
    good = _good(resumo="Foram 1.250,5 pontos.", metricas_relevantes=data["metricas_relevantes"])
    assert "valores_rastreaveis" not in lv.validate_response(json.dumps(good), big, TICKERS).failed
    assert "valores_rastreaveis" in lv.validate_response(json.dumps(good), ctx, TICKERS).failed


def test_asset_name_digits_are_ignored():
    ctx = _context(assets=["PETR4.SA"], asset_names={"PETR4.SA": "Petrobras PN 4"})
    data = _good(
        resumo="PETR4.SA (Petrobras PN 4) variou 180,46%.",
    )
    data["filtros_aplicados"]["ativos"] = ["PETR4.SA"]
    assert "valores_rastreaveis" not in lv.validate_response(json.dumps(data), ctx, TICKERS).failed


def test_status_insufficient():
    ctx = _context(
        status="dados_insuficientes",
        metrics=[],
        n_observations=10,
        limitation_flags=["poucas_observacoes"],
    )
    ok = _good(
        resumo="Os dados são insuficientes para calcular as métricas.",
        o_que_o_grafico_mostra="Não há observações suficientes para descrever o período.",
        metricas_relevantes=[],
        limitacoes=["Há poucas observações no período escolhido."],
    )
    assert lv.validate_response(json.dumps(ok), ctx, TICKERS).ok
    cited = copy.deepcopy(ok)
    cited["metricas_relevantes"] = _good()["metricas_relevantes"]
    detail = lv.validate_response(json.dumps(cited), ctx, TICKERS).as_dict()["details"]["metricas_no_contexto"]
    assert "não deve citar" in detail
    no_mention = _good(resumo="Tudo certo com a análise.", metricas_relevantes=[], limitacoes=["Há poucas observações."])
    detail = lv.validate_response(json.dumps(no_mention), ctx, TICKERS).as_dict()["details"]["metricas_no_contexto"]
    assert "insuficientes" in detail


@pytest.mark.parametrize(
    "phrase",
    [
        "Seria bom investir em setembro.",
        "Compre agora este ativo.",
        "O ativo está barato.",
        "É um bom momento para entrar.",
        "Vale a pena olhar este ativo.",
        "Não compre; ainda assim, o ativo está caro.",
        "O melhor investimento do período foi AAPL.",
        "O ativo parece subvalorizado.",
        "A hora de comprar chegou.",
        "Deve investir com calma.",
        "O preço justo seria menor.",
    ],
)
def test_hard_terms_are_rejected(phrase):
    result = _run(_good(resumo=phrase))
    assert "sem_termos_proibidos" in result.failed


def test_hard_term_even_negated():
    assert "sem_termos_proibidos" in _fails(_good(nota_educativa="Não invista agora."))
    assert "sem_termos_proibidos" in _fails(_good(nota_educativa="Não aposte nisso."))


def test_price_judgments_allowed_only_when_negated():
    ok = _good(o_que_nao_pode_ser_concluido=[
        "Não indica se o ativo está barato ou caro.",
        "A análise não determina se o ativo 'vai subir' ou 'vai cair'.",
        "Não permite dizer qual é o melhor investimento.",
        "A análise não determina qual ativo seria melhor ou pior.",
        "Não indica se vale a pena ou se é um bom momento para qualquer decisão.",
    ])
    assert "sem_termos_proibidos" not in _fails(ok)
    for phrase in ("O ativo está barato.", "Parece caro neste momento.", "O preço vai subir.",
                   "O ativo está sobrevalorizado.", "Este é o melhor investimento.",
                   "Vale a pena olhar este ativo.", "Seria melhor esperar.", "É um bom momento para entrar.",
                   "Esta é a hora de comprar."):
        result = _run(_good(resumo=phrase))
        assert "sem_termos_proibidos" in result.failed, phrase
    detail = _run(_good(resumo="O ativo está barato.")).as_dict()["details"]["sem_termos_proibidos"]
    assert "barato" in detail and "«" in detail


@pytest.mark.parametrize(
    "phrase",
    [
        "Recomendo observar este ativo.",
        "Convém aplicar parte da renda aqui.",
        "Pode ser uma boa ideia comprar na baixa.",
        "Vale alocar mais neste ativo.",
    ],
)
def test_recommendation_language(phrase):
    assert "sem_recomendacao" in _fails(_good(resumo=phrase))


@pytest.mark.parametrize(
    "phrase",
    [
        "O preço vai se valorizar nos próximos meses.",
        "O ativo tende a repetir o padrão.",
        "No próximo ano deve haver nova alta.",
        "Certamente o padrão se repetirá.",
        "A previsão é de alta.",
        "Espera-se que o preço continue crescendo.",
        "Com certeza o retorno será positivo.",
        "Isso garante novos ganhos.",
    ],
)
def test_prediction_language(phrase):
    assert "sem_previsao" in _fails(_good(resumo=phrase))


def test_negated_soft_terms_are_allowed():
    ok = _good(
        resumo="Isto não é recomendação de investimento e não faz previsão.",
        limitacoes=["O histórico não permite prever o futuro nem garante repetição."],
        o_que_nao_pode_ser_concluido=["Nenhuma recomendação de comprar ou vender pode ser extraída."],
    )
    result = _run(ok)
    assert result.ok, result.as_dict()


def test_negation_must_precede_the_term():
    # a negação vem depois do termo: continua reprovado
    assert "sem_recomendacao" in _fails(_good(resumo="Recomendo isso, não há dúvida."))


@pytest.mark.parametrize("phrase", [
    "Sem dúvida, o ativo está barato.",
    "Não há dúvida de que o ativo está barato.",
    "Isso não é previsão, mas o ativo está caro.",
    "Não faz previsão e fala de muitas coisas diferentes entre dados, gráficos, tabelas e médias, de modo que o ativo está caro.",
])
def test_negation_must_be_explicit_and_close(phrase):
    assert "sem_termos_proibidos" in _fails(_good(resumo=phrase))


def test_negation_close_but_with_distance_is_allowed():
    resumo = "Não é possível concluir, com base apenas nestes dados históricos, se o ativo está barato."
    assert "sem_termos_proibidos" not in _fails(_good(resumo=resumo))


def test_limitation_flags_required():
    ctx = _context(limitation_flags=["poucos_anos", "mes_em_andamento", "preco_nao_positivo", "poucas_observacoes"])
    result = lv.validate_response(json.dumps(_good()), ctx, TICKERS)
    assert "limitacoes" in result.failed
    assert "poucos_anos" in result.as_dict()["details"]["limitacoes"]
    full = _good(
        limitacoes=[
            "Há poucos anos disponíveis.",
            "O mês atual está em andamento.",
            "Há preço zero ou negativo.",
            "Poucas observações.",
        ]
    )
    assert lv.validate_response(json.dumps(full), ctx, TICKERS).passed("limitacoes")


def test_refusal_checks():
    ctx = _context(user_request=("recomendacao", "Seria bom investir em setembro?"))
    good = _good(
        resumo=lp.REFUSAL_TEXT + " No período, o preço variou 180,46%.",
        recusa_recomendacao=True,
    )
    assert lv.validate_response(json.dumps(good), ctx, TICKERS).ok
    # sem recusa
    assert "recusa_correta" in lv.validate_response(json.dumps(_good()), ctx, TICKERS).failed
    # recusou, mas sem a frase fixa
    weak = _good(resumo="Prefiro não responder.", recusa_recomendacao=True)
    assert "recusa_correta" in lv.validate_response(json.dumps(weak), ctx, TICKERS).failed
    # frase da previsão não serve para recomendação
    wrong = _good(resumo=lp.REFUSAL_FORECAST_TEXT, recusa_recomendacao=True)
    assert "recusa_correta" in lv.validate_response(json.dumps(wrong), ctx, TICKERS).failed


def test_forecast_refusal_and_spurious_refusal():
    ctx = _context(user_request=("previsao", "O preço vai subir?"))
    good = _good(resumo=lp.REFUSAL_FORECAST_TEXT, recusa_recomendacao=True)
    result = lv.validate_response(json.dumps(good), ctx, TICKERS)
    assert result.passed("recusa_correta")
    spurious = _good(resumo=lp.REFUSAL_TEXT, recusa_recomendacao=True)
    result = _run(spurious)
    assert "recusa_correta" in result.failed
    assert "sem pedido" in result.as_dict()["details"]["recusa_correta"]


def test_refusal_texts_pass_language_checks():
    # as frases fixas da recusa não podem ser reprovadas pelo próprio validador
    for text, kind in ((lp.REFUSAL_TEXT, "recomendacao"), (lp.REFUSAL_FORECAST_TEXT, "previsao")):
        ctx = _context(user_request=(kind, "pedido"))
        data = _good(resumo=text, recusa_recomendacao=True)
        result = lv.validate_response(json.dumps(data), ctx, TICKERS)
        assert result.ok, result.as_dict()


def test_fold():
    assert lv.fold("Previsão ÇÃO") == "previsao cao"


def test_buy_sell_nouns_are_soft_terms():
    ok = _good(o_que_nao_pode_ser_concluido=["Não é um sinal de compra ou de venda de nenhum ativo."])
    assert "sem_recomendacao" not in _fails(ok)
    bad = _good(resumo="Há um sinal de venda neste ativo.")
    result = _run(bad)
    assert "sem_recomendacao" in result.failed
    assert "venda" in result.as_dict()["details"]["sem_recomendacao"]


def test_details_show_the_offending_sentence():
    result = _run(_good(resumo="Os retornos tendem a se repetir."))
    detail = result.as_dict()["details"]["sem_previsao"]
    assert "tende" in detail and "repetir" in detail


def test_year_month_and_scale_numbers_are_accepted():
    data = _good(resumo="De 2020-01 a 2024-12 (01/2020 a 12/2024), a correlação fica entre -1 e 1, com 0 sendo nula.")
    assert "valores_rastreaveis" not in _fails(data)
    # duração do período (cerca de 5 anos) é derivada das datas do contexto
    assert "valores_rastreaveis" not in _fails(_good(resumo="São cerca de 5 anos de dados."))
    assert "valores_rastreaveis" in _fails(_good(resumo="São cerca de 8 anos de dados."))


def test_insufficient_wording_variants():
    ctx = _context(status="dados_insuficientes", metrics=[], n_observations=10, limitation_flags=["poucas_observacoes"])
    for resumo in (
        "Os dados não são suficientes para calcular as métricas.",
        "Não há dados suficientes para esta análise.",
        "Os dados são insuficientes para a análise.",
    ):
        data = _good(
            resumo=resumo,
            o_que_o_grafico_mostra="Não há observações suficientes para descrever o período.",
            metricas_relevantes=[],
            limitacoes=["Há poucas observações no período."],
        )
        assert lv.validate_response(json.dumps(data), ctx, TICKERS).ok, resumo


def test_day_first_dates_and_metric_mismatch_detail():
    assert "valores_rastreaveis" not in _fails(_good(resumo="De 11-10-2021 a 09-10-2026, AAPL variou 180,46%."))
    bad = _good(metricas_relevantes=[{"id": "retorno_total", "valor": 1.8, "unidade": "%", "leitura": "x"}])
    detail = _run(bad).as_dict()["details"]["metricas_no_contexto"]
    assert "esperado 180.46" in detail and "recebido 1.8" in detail
