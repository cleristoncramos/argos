"""Etapa 3 da DL2: aviso de não determinismo, anos fora do padrão e dicas de leitura."""

import pandas as pd

from app.ui.season_explorer import describe_pattern_breaks
from core.chart_guides import CHART_TIPS, chart_tip
from core.disclaimers import DECISION_SUPPORT_NOTE, NON_DETERMINISM_WARNING, contains_forbidden_phrase
from core.seasonality import pattern_breaks


def _janela(pares):
    return pd.DataFrame({"Ano": [a for a, _ in pares], "Retorno (%)": [v for _, v in pares]})


def test_aviso_obrigatorio_com_a_redacao_da_dl2g():
    assert NON_DETERMINISM_WARNING == (
        "Os resultados podem variar entre execuções. O padrão histórico não garante repetição."
    )
    assert "apoio à decisão" in DECISION_SUPPORT_NOTE and "não de investimento" in DECISION_SUPPORT_NOTE


def test_padrao_quebrado_nos_dois_ultimos_anos():
    # O exemplo da reunião: setembro → outubro subiu na maioria dos anos, mas não nos dois últimos.
    janela = _janela([(2019, 3.0), (2020, 5.0), (2021, 2.0), (2022, 4.0), (2023, 1.0), (2024, -2.0), (2025, -1.5)])
    r = pattern_breaks(janela)
    assert r == {"direction": "alta", "following": 5, "n": 7, "breaks": [2024, 2025],
                 "recent_breaks": [2024, 2025], "recent_years": [2024, 2025]}
    texto = describe_pattern_breaks(r, "Set", "Out")
    assert texto.startswith("Do fechamento de setembro ao fechamento de outubro, o preço subiu em 5 de 7 anos")
    assert "não seguiu esse sentido em 2024 e 2025" in texto
    assert "Inclusive nos 2 anos mais recentes (2024 e 2025)" in texto


def test_padrao_de_queda_com_excecao_antiga_e_uma_recente():
    janela = _janela([(2021, 1.0), (2022, -1.0), (2023, -2.0), (2024, 0.5), (2025, -3.0), (2026, None)])
    r = pattern_breaks(janela)
    assert r["direction"] == "queda" and r["breaks"] == [2021, 2024] and r["recent_breaks"] == [2024]
    texto = describe_pattern_breaks(r, "Nov", "Fev")
    assert "o preço caiu em 3 de 5 anos" in texto and "do ano seguinte" in texto
    assert "Nos 2 anos mais recentes (2024 e 2025), fugiu do padrão em 2024." in texto


def test_sem_excecao_empate_e_poucos_anos():
    r = pattern_breaks(_janela([(2023, 1.0), (2024, 2.0), (2025, 0.5)]))
    assert r["breaks"] == [] and "sem exceção" in describe_pattern_breaks(r, "Set", "Out")
    assert "próximo ano seja diferente" in describe_pattern_breaks(r, "Set", "Out")

    antigo = pattern_breaks(_janela([(2020, -1.0), (2021, 1.0), (2022, 2.0), (2023, 1.0)]))
    assert antigo["breaks"] == [2020] and antigo["recent_breaks"] == []
    assert describe_pattern_breaks(antigo, "Set", "Out").endswith("em 2020**.")

    empate = pattern_breaks(_janela([(2024, 1.0), (2025, -1.0)]))
    assert empate["direction"] is None and empate["n"] == 2
    assert "empataram" in describe_pattern_breaks(empate, "Set", "Out")

    um = pattern_breaks(_janela([(2025, 1.0)]))
    assert um["direction"] is None and "anos de menos" in describe_pattern_breaks(um, "Set", "Out")

    vazio = pattern_breaks(pd.DataFrame(columns=["Ano", "Retorno (%)"]))
    assert vazio["n"] == 0 and vazio["breaks"] == []


def test_dicas_curtas_dos_graficos():
    for cid in ("mapa_sazonal", "media_mensal", "recorte_anos", "recorte_anos_lado_a_lado", "janela_retorno"):
        dica = chart_tip(cid)
        assert dica and len(dica) < 260 and contains_forbidden_phrase(dica) is None
    assert chart_tip("inexistente") is None
    assert "linha do zero é a média" in CHART_TIPS["recorte_anos"]
