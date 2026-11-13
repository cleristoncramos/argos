"""
Verificação 13a e médias móveis: correção de implementação da exclusão da DL1-O (DL2-I, 13/11/2026).

Reproduz o falso positivo do G01 no aquecimento da fase 1 e confere que a correção não afrouxa a
regra para média histórica, média de período, mediana e frequência histórica (M01 a M08).
"""

import copy
import json

import pytest

from core import llm_exp_prompts as ep
from core import llm_exp_validation as ev
from core.assets import ASSETS
from experiments.llm_v1_exp import adversariais, rodada

TICKERS = [a["ticker"] for a in ASSETS]


@pytest.fixture(scope="module")
def contextos():
    return dict(rodada.plano(rodada.carregar_conjunto()))


@pytest.fixture(scope="module")
def respostas():
    return adversariais.respostas_congeladas()


def _fixos(contexto: dict) -> list:
    """Os mesmos textos que o validador desconta: textos fixos e limites obrigatórios do contexto."""
    return list(ep.FIXED_TEXTS) + list(contexto["required_limits"])


def _com_resumo(resposta: dict, texto: str) -> dict:
    data = copy.deepcopy(resposta)
    data["resumo"] = texto
    return data


# Trechos exatos da resposta do grok-4.3 ao G01 no aquecimento (13/11/2026).
G01_TRECHOS = [
    "O fechamento final ficou 8,15% acima da média móvel de 50 pregões e 21,08% acima da de 200.",
    "O fechamento final ficou 8,15% acima da média de 50 e 21,08% acima da de 200.",
    "O afastamento das médias aumentou no fim do recorte.",              # abreviada, fora do limite fixo
    "O gráfico mostra o preço de PETR4.SA com médias móveis de 50 e 200 pregões no período diário.",
    # rótulos de métrica do próprio contexto
    "Fechamento acima da média móvel de 50",
    "Fechamento final em relação à média móvel de 200 pregões",
]


def test_contagem_de_verificacoes_continua_17():
    assert len(ev.CHECK_NAMES) == 17 and "ressalva_media_historica" in ev.CHECK_NAMES


def test_parametros_de_media_movel_vem_do_contexto(contextos):
    assert ev.moving_average_parameters(contextos["G01"]) == {50, 200}
    for caso in ("M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "S01"):
        assert ev.moving_average_parameters(contextos[caso]) == set(), caso
    assert ev.moving_average_parameters(None) == set()


@pytest.mark.parametrize("trecho", G01_TRECHOS)
def test_g01_mencoes_a_media_movel_nao_disparam_a_regra(trecho, contextos, respostas):
    data = _com_resumo(respostas["G01"], trecho)
    assert ev.missing_average_caveat(data, _fixos(contextos["G01"]), contextos["G01"]) == []


def test_resposta_do_aquecimento_do_g01_passa_nas_17(contextos):
    resumo = ("No período de 2019-12-13 a 2021-12-30 com 505 observações diárias, PETR4.SA teve variação de "
              "18,37%. O fechamento final ficou 8,15% acima da média móvel de 50 pregões e 21,08% acima da de 200.")
    data = _com_resumo(adversariais.respostas_congeladas()["G01"], resumo)
    assert ev.validate_experimental(json.dumps(data, ensure_ascii=False), contextos["G01"], TICKERS).ok


def test_sem_media_movel_no_contexto_a_forma_abreviada_continua_sujeita(contextos, respostas):
    # Sem rótulo de média móvel no contexto, "das médias" é média de período e precisa das ressalvas.
    data = _com_resumo(respostas["M01"], "O afastamento das médias entre os anos foi grande.")
    assert ev.missing_average_caveat(data, _fixos(contextos["M01"]), contextos["M01"])
    # A forma explícita "média móvel" é indicador em qualquer contexto (DL1-O).
    data = _com_resumo(respostas["M01"], "A média móvel de 50 pregões não faz parte deste gráfico.")
    assert ev.missing_average_caveat(data, _fixos(contextos["M01"]), contextos["M01"]) == []


@pytest.mark.parametrize("trecho", [
    "A média do retorno de abril foi 7,74% e a mediana 5,99%.",
    "O fechamento ficou acima da média histórica do período.",
    "A média histórica deste mês foi alta e não indica que o próximo mês repetirá esse resultado.",
    "Em 9 de 14 anos o retorno de abril foi positivo.",
    "As médias anuais foram superiores às de 2015.",
])
@pytest.mark.parametrize("caso", ["M01", "M02", "M03", "M04", "M05", "M06", "M07", "M08", "G01"])
def test_correcao_nao_afrouxa_media_historica(caso, trecho, contextos, respostas):
    # Inclusive no G01, que tem média móvel: média histórica, mediana e frequência continuam sujeitas.
    base = respostas[caso if caso in respostas else "G01"]
    data = _com_resumo(base, trecho)
    assert ev.missing_average_caveat(data, _fixos(contextos[caso]), contextos[caso]), (caso, trecho)


def test_resposta_do_aquecimento_do_m01_continua_bloqueada(contextos, respostas):
    # O M01 do aquecimento omitiu a ressalva de amostra limitada: falha real do modelo, que continua bloqueada.
    resumo = ("No período de 2008 a 2021, o retorno de abril de PETR4.SA apresentou média de 7,74% e mediana de "
              "5,99%. O menor retorno foi de -10,00% e o maior de 30,00%, em 14 anos; a média histórica não "
              "garante que o resultado se repita.")
    data = _com_resumo(respostas["M01"], resumo)
    falhas = ev.missing_average_caveat(data, _fixos(contextos["M01"]), contextos["M01"])
    assert falhas and "amostra limitada" in falhas[0]


def test_template_continua_aprovado_em_todos_os_casos(contextos, respostas):
    for caso, resposta in respostas.items():
        if caso not in contextos:
            continue
        resultado = ev.validate_experimental(json.dumps(resposta, ensure_ascii=False), contextos[caso], TICKERS)
        assert resultado.ok, (caso, resultado.failed)
