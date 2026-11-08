"""Piloto v2: grade ampliada, critério 6, registros por ajuste, separação por versão e reprodução da v1."""

import json

import numpy as np
import pandas as pd
import pytest

from experiments.preditivo import config, config_v2, executar_v2
from experiments.preditivo.amostras import construir_amostras
from experiments.preditivo.avaliacao import prever_anos
from experiments.preditivo.elegibilidade import MENSAGEM_V2_SEM_ABERTURA, avaliar_v2, filtros_desenvolvimento_v2
from experiments.preditivo.estatistica import (
    NAO_CALCULAVEL,
    OK,
    ResultadoTeste,
    _teste_media,
    diebold_mariano_contra_media,
    r2_contra_media_nas_datas,
    r2_contra_referencia,
)
from experiments.preditivo.executar import desenvolver_ativo
from experiments.preditivo.tests.auxiliares import precos_sinteticos


@pytest.fixture(scope="module")
def serie():
    return precos_sinteticos("2008-01-02", "2023-06-30")


@pytest.fixture(scope="module")
def v1_e_v2(serie):
    """Desenvolvimento pela rotina oficial da v1 e pela da v2 restrita à grade da v1."""
    v1 = desenvolver_ativo("TESTE", serie)
    v2_grade_v1 = executar_v2.desenvolver_ativo_v2("TESTE", serie, alphas=config_v2.ALPHAS_V1)
    v2 = executar_v2.desenvolver_ativo_v2("TESTE", serie)
    return v1, v2_grade_v1, v2


# ------------------------------------------------------------- configuração

def test_grade_da_v2_amplia_a_da_v1_ate_o_limite_fixo():
    assert config_v2.ALPHAS[:len(config.ALPHAS)] == config.ALPHAS
    assert config_v2.ALPHAS[len(config.ALPHAS):] == (1e4, 1e5, 1e6)
    assert config_v2.LIMITE_SUPERIOR == 1e6 and config.ALPHAS == (0.1, 1.0, 10.0, 100.0, 1000.0)


def test_arquivos_da_v2_sao_distintos_dos_da_v1():
    v1 = {config.REGISTRO, config.CONDICOES, config.MARCA_FINAL_USADO, config.PROTOCOLO,
          config.RAIZ / "datas_elegiveis.json", config.RAIZ / "encerramento_v1.json"}
    v2 = {config_v2.REGISTRO, config_v2.CONDICOES, config_v2.MARCA_FINAL_USADO, config_v2.PROTOCOLO,
          config_v2.DATAS_ELEGIVEIS, config_v2.ENCERRAMENTO}
    assert not v1 & v2 and config_v2.RESULTADOS != config_v2.RESULTADOS_V1


# ------------------------------------------------------------- R² contra a média (seção 5)

def test_r2_contra_referencia_valor_e_casos_nao_calculaveis():
    y, yhat, ref = np.array([0.1, -0.2, 0.05]), np.array([0.05, -0.1, 0.0]), np.array([0.0, 0.0, 0.0])
    esperado = 1 - np.sum((y - yhat) ** 2) / np.sum((y - ref) ** 2)
    assert r2_contra_referencia(y, yhat, ref) == pytest.approx(esperado, rel=1e-15)
    assert r2_contra_referencia(y, yhat, y) is None                         # denominador nulo
    assert r2_contra_referencia(y, [0.05, np.nan, 0.0], ref) is None        # previsão ausente
    assert r2_contra_referencia(y, yhat, [0.0, np.inf, 0.0]) is None        # referência não finita
    assert r2_contra_referencia([], [], []) is None
    assert r2_contra_referencia(y, yhat[:2], ref) is None                   # datas diferentes


def _previsoes(n=260, semente=3, media_ausente=False):
    rng = np.random.default_rng(semente)
    datas = pd.bdate_range("2022-02-01", periods=n)
    y = rng.normal(0.01, 0.05, n)
    previsoes = pd.DataFrame({"decision_date": datas, "y": y, "yhat": y * 0.3 + rng.normal(0, 0.03, n),
                              "yhat_media": np.full(n, 0.008)})
    if media_ausente:
        previsoes.loc[5, "yhat_media"] = np.nan
    return previsoes, datas


def test_diebold_mariano_contra_media_usa_o_diferencial_certo_e_trata_ausencias():
    previsoes, datas = _previsoes()
    y, yhat, media = (previsoes[c].to_numpy() for c in ("y", "yhat", "yhat_media"))
    esperado = _teste_media((y - media) ** 2 - (y - yhat) ** 2, config.NW_DEFASAGENS, config.P_LIMIAR, config.T_MINIMO)
    obtido = diebold_mariano_contra_media(previsoes, datas)
    assert obtido.status == OK and obtido.estatistica == pytest.approx(esperado.estatistica, rel=1e-15)
    com_falta, datas = _previsoes(media_ausente=True)
    assert diebold_mariano_contra_media(com_falta, datas).status == NAO_CALCULAVEL
    assert r2_contra_media_nas_datas(com_falta, datas) is None


# ------------------------------------------------------------- critério 6 e filtros

def _economico(atende=True):
    class R:
        def __init__(self, retorno, drawdown):
            self.retorno, self.drawdown_maximo = retorno, drawdown
    estrategia = R(0.5 if atende else -0.1, 0.1)
    return {"estrategia": estrategia, "caixa": R(0.2, 0.0), "comprar_manter": R(0.3, 0.4)}


def test_criterio_6_obrigatorio_e_cumulativo():
    dm = ResultadoTeste(OK, p=0.01, atende=True)
    zero = [0.1] * 8
    ok = avaliar_v2(0.05, dm, zero, 0.02, [0.1] * 5 + [-0.1] * 3, _economico(), _economico())
    assert ok["elegivel"] and ok["criterios"]["6_ganho_sobre_media_historica"]
    for r2_media_final, dobras_media in ((None, [0.1] * 8), (0.0, [0.1] * 8), (0.02, [0.1] * 4 + [None] * 4)):
        falha = avaliar_v2(0.05, dm, zero, r2_media_final, dobras_media, _economico(), _economico())
        assert not falha["elegivel"] and not falha["criterios"]["6_ganho_sobre_media_historica"]
        assert all(v for k, v in falha["criterios"].items() if not k.startswith("6"))


def test_filtros_de_desenvolvimento_e_mensagem_de_encerramento():
    assert filtros_desenvolvimento_v2([0.1] * 5 + [-0.1] * 3, [0.1] * 5 + [None] * 3)["atende"]
    falha = filtros_desenvolvimento_v2([0.1] * 8, [0.1] * 4 + [0.0] * 4)   # zero não é positivo
    assert not falha["atende"] and falha["mensagem"] == MENSAGEM_V2_SEM_ABERTURA
    assert not filtros_desenvolvimento_v2([0.1] * 4 + [None] * 4, [0.1] * 8)["atende"]


# ------------------------------------------------------------- registros e grade

def test_registros_por_ajuste_e_limite_superior(v1_e_v2):
    _v1, _v2_grade_v1, (_previsoes_v2, ajustes, dobras) = v1_e_v2
    for ajuste in ajustes:
        assert set(ajuste["erros_internos"]) == set(config_v2.ALPHAS)
        assert ajuste["alpha_no_limite_superior"] == (ajuste["alpha"] == 1e6)
        assert ajuste["norma_coeficientes"] >= 0 and ajuste["afastamento_media_historica"]["datas"] > 0
        # A média do treino e a média histórica expansiva são séries distintas, registradas à parte.
        assert "media_alvo_treino" in ajuste and "media_historica_nas_datas" in ajuste
    assert all("r2_contra_media_historica" in d for d in dobras)


def test_alpha_maior_encolhe_os_coeficientes(serie):
    amostras = construir_amostras(serie[serie["Date"] < "2016-01-01"].reset_index(drop=True))
    calendario = serie[serie["Date"] < "2016-01-01"]["Date"].reset_index(drop=True)
    normas = []
    for alpha in (1000.0, 1e6):
        _p, ajustes = prever_anos(amostras, calendario, (2015,), {2015: 20}, "X", alphas=(alpha,), registros_v2=True)
        normas.append(ajustes[0]["norma_coeficientes"])
    assert normas[1] < normas[0]


def test_valores_comuns_da_grade_iguais_aos_da_v1(v1_e_v2):
    (_p1, ajustes_v1, _d1), _v2g, (_p2, ajustes_v2, _d2) = v1_e_v2
    oficial = json.loads(json.dumps({"ajustes": ajustes_v1}))          # chaves como texto, como no arquivo
    assert executar_v2.conferir_valores_comuns(ajustes_v2, oficial)["equivalente"]


def test_v2_restrita_a_grade_da_v1_reproduz_a_v1_e_detecta_divergencia(v1_e_v2, tmp_path):
    (p1, a1, d1), (p2, a2, d2), _v2 = v1_e_v2
    arquivo = tmp_path / "v1.csv"
    p1.to_csv(arquivo, index=False)
    oficial_previsoes = pd.read_csv(arquivo, parse_dates=["decision_date", "entry_date", "label_end_date"])
    oficial = json.loads(json.dumps({"ajustes": a1, "dobras": d1}, default=str))
    resultado = executar_v2.comparar_com_v1(p2, a2, d2, oficial_previsoes, oficial)
    assert resultado["equivalente"], resultado["problemas"]
    alterado = p2.copy()
    alterado.loc[10, "yhat"] += 1e-8                                     # acima da tolerância documentada
    falha = executar_v2.comparar_com_v1(alterado, a2, d2, oficial_previsoes, oficial)
    assert not falha["equivalente"] and "coluna yhat fora da tolerância" in falha["problemas"]
    dentro = p2.copy()
    dentro.loc[10, "yhat"] += 1e-13                                      # ruído numérico abaixo dela
    assert executar_v2.comparar_com_v1(dentro, a2, d2, oficial_previsoes, oficial)["equivalente"]


# ------------------------------------------------------------- separação e travas

@pytest.fixture
def v2_isolada(tmp_path, monkeypatch):
    for nome in ("REGISTRO", "CONDICOES", "MARCA_FINAL_USADO", "DATAS_ELEGIVEIS", "ENCERRAMENTO"):
        monkeypatch.setattr(config_v2, nome, tmp_path / getattr(config_v2, nome).name)
    monkeypatch.setattr(config_v2, "RESULTADOS", tmp_path / "resultados_v2")
    monkeypatch.setattr(executar_v2, "arquivos_alterados", lambda: [])
    return tmp_path


def test_codigo_nao_congelado_recusa_o_desenvolvimento_oficial():
    executar_v2.exigir_codigo_congelado(["docs/versao_congelada.md", "experiments/preditivo/registro_v2.jsonl"])
    with pytest.raises(executar_v2.ExecucaoRecusada, match="não congelados"):
        executar_v2.exigir_codigo_congelado(["experiments/preditivo/config_v2.py"])


def test_resultado_oficial_da_v2_nao_e_sobrescrito(v2_isolada):
    config_v2.RESULTADOS.mkdir()
    (config_v2.RESULTADOS / "desenvolvimento_resumo.json").write_text("{}", encoding="utf-8")
    with pytest.raises(executar_v2.ExecucaoRecusada, match="não são sobrescritos"):
        executar_v2.main(["desenvolver"])


def test_registro_anterior_tambem_impede_nova_rodada_oficial(v2_isolada):
    config_v2.REGISTRO.write_text(json.dumps({"evento": "desenvolvimento"}) + "\n", encoding="utf-8")
    with pytest.raises(executar_v2.ExecucaoRecusada, match="já foi executado"):
        executar_v2.main(["desenvolver"])


def test_v2_encerrada_recusa_execucoes(v2_isolada):
    config_v2.ENCERRAMENTO.write_text("{}", encoding="utf-8")
    for argv in (["desenvolver"], ["listar-datas"], ["final", "--confirmo-abertura"]):
        with pytest.raises(executar_v2.ExecucaoRecusada, match="encerrada"):
            executar_v2.main(argv)


def test_periodo_final_da_v2_travado_sem_desenvolvimento_e_sem_condicoes(v2_isolada):
    for argv in (["listar-datas"], ["final", "--confirmo-abertura"]):
        with pytest.raises(executar_v2.ExecucaoRecusada, match="critérios 3 e 6"):
            executar_v2.main(argv)
    config_v2.RESULTADOS.mkdir()
    resumo = {"X": {"filtros_desenvolvimento": {"atende": True}}, "_declaracoes": {}}
    (config_v2.RESULTADOS / "desenvolvimento_resumo.json").write_text(json.dumps(resumo), encoding="utf-8")
    with pytest.raises(executar_v2.ExecucaoRecusada, match="condições ausente"):
        executar_v2.main(["listar-datas"])
    config_v2.CONDICOES.write_text(json.dumps({"condicoes": {n: True for n in config_v2.CONDICOES_ABERTURA[:-1]},
                                               "hashes": {}}), encoding="utf-8")
    with pytest.raises(executar_v2.ExecucaoRecusada, match="7_nova_decisao_escrita_de_abertura"):
        executar_v2.main(["listar-datas"])
    from experiments.preditivo.abertura import AberturaNegada
    with pytest.raises(AberturaNegada, match="condições pendentes"):
        executar_v2.main(["final", "--confirmo-abertura"])


def test_filtro_reprovado_no_desenvolvimento_mantem_o_final_travado(v2_isolada):
    config_v2.RESULTADOS.mkdir()
    resumo = {"X": {"filtros_desenvolvimento": {"atende": True}}, "Y": {"filtros_desenvolvimento": {"atende": False}}}
    (config_v2.RESULTADOS / "desenvolvimento_resumo.json").write_text(json.dumps(resumo), encoding="utf-8")
    with pytest.raises(executar_v2.ExecucaoRecusada, match="critérios 3 e 6"):
        executar_v2.main(["final", "--confirmo-abertura"])


def test_registro_da_v2_identifica_versao_e_alteracoes(v2_isolada):
    linha = executar_v2.registrar_v2("teste", {"a": 1})
    gravada = json.loads(config_v2.REGISTRO.read_text(encoding="utf-8").splitlines()[-1])
    assert linha["versao"] == gravada["versao"] == "v2"
    assert "arquivos_alterados" in gravada and set(gravada["hashes"]) >= {"protocolo", "configuracao_v2"}


def test_encerramento_da_v1_nao_bloqueia_a_v2_e_continua_valendo_para_a_v1(v2_isolada):
    from experiments.preditivo.abertura import VersaoEncerrada, exigir_versao_aberta
    executar_v2.exigir_v2_aberta()                                     # sem encerramento_v2: aberta
    if (config.RAIZ / "encerramento_v1.json").exists():
        with pytest.raises(VersaoEncerrada):
            exigir_versao_aberta()
