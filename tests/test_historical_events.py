"""Período e eventos históricos nos gráficos (recurso trazido do projeto Previsão)."""

from datetime import date

import pandas as pd
import pytest

from core.disclaimers import contains_forbidden_phrase
from core.historical_events import (
    CATEGORY_COLORS,
    CSV_FORMAT_ERROR,
    EVENTS_NOTE,
    USER_CATEGORY,
    available_categories,
    combine_events,
    empty_events,
    event_traces,
    filter_events,
    load_events,
    new_user_event,
    parse_user_csv,
    user_events_csv,
    user_events_frame,
)


def test_base_do_sistema_tem_27_eventos_em_quatro_categorias():
    events = load_events()
    assert len(events) == 27
    assert events["data"].min() == pd.Timestamp("2016-06-23")
    assert events["data"].max() == pd.Timestamp("2026-10-25")
    assert events["categoria"].value_counts().to_dict() == {
        "Política": 9, "Mundo": 7, "Mercado e crises": 7, "Saúde": 4,
    }
    assert available_categories(events) == ["Mercado e crises", "Saúde", "Política", "Mundo"]
    circuit = events[events["titulo"].str.contains("Circuit breaker")]
    assert len(circuit) == 5          # seis interrupções: o dia 12/03/2020 teve duas
    for _, row in events.iterrows():
        assert row["titulo"] and row["descricao"]
        assert contains_forbidden_phrase(row["descricao"]) is None


def test_arquivo_ausente_devolve_base_vazia(tmp_path):
    events = load_events(tmp_path / "nao_existe.csv")
    assert events.empty and list(events.columns) == ["data", "categoria", "titulo", "descricao"]


def test_eventos_do_usuario_e_combinacao():
    assert user_events_frame([]).empty
    mine = user_events_frame([new_user_event(date(2024, 7, 10), "  Queda da NVIDIA ", None)])
    assert mine.iloc[0]["categoria"] == USER_CATEGORY and mine.iloc[0]["titulo"] == "Queda da NVIDIA"
    assert mine.iloc[0]["descricao"] == ""

    assert combine_events(empty_events(), empty_events()).empty
    both = combine_events(load_events(), mine)
    assert len(both) == 28 and available_categories(both)[-1] == USER_CATEGORY
    assert pd.api.types.is_datetime64_any_dtype(combine_events(empty_events(), mine)["data"])

    with pytest.raises(ValueError, match="título"):
        new_user_event(date(2024, 1, 1), "   ")


def test_filtro_por_categoria_e_periodo():
    events = load_events()
    covid = filter_events(events, ["Saúde"], date(2020, 1, 1), date(2020, 12, 31))
    assert list(covid["titulo"]) == [
        "Primeiro caso de COVID-19 no Brasil", "OMS declara pandemia", "Eficácia da vacina da Pfizer",
    ]
    assert filter_events(events, [], date(2016, 1, 1), date(2026, 12, 31)).empty


def test_linhas_pontilhadas_por_categoria():
    events = combine_events(
        filter_events(load_events(), ["Mundo", "Mercado e crises"], date(2020, 1, 1), date(2022, 12, 31)),
        user_events_frame([new_user_event(date(2021, 5, 5), "Meu evento", "Detalhe"),
                           {"data": "2021-06-01", "categoria": "Outra", "titulo": "Sem cor", "descricao": None}]),
    )
    traces = event_traces(events, 0.0, 50.0)
    assert [t["name"] for t in traces] == ["Mercado e crises", "Mundo", USER_CATEGORY, "Outra"]
    mundo = traces[1]
    assert mundo["line"]["dash"] == "dot" and mundo["line"]["color"] == CATEGORY_COLORS["Mundo"]
    assert mundo["y"][:3] == [0.0, 50.0, None] and len(mundo["x"]) == 3 * 2   # 2 eventos de 2022
    assert mundo["customdata"][0].startswith("<b>Invasão da Ucrânia</b> (24/02/2022)<br>Rússia")
    assert traces[3]["line"]["color"] == "#111827" and traces[3]["customdata"][0] == "<b>Sem cor</b> (01/06/2021)"
    assert event_traces(empty_events(), 0, 1) == []


def test_csv_do_usuario_ida_e_volta():
    mine = user_events_frame([new_user_event(date(2024, 7, 10), "Queda da NVIDIA", "Ações de tecnologia caem")])
    content = user_events_csv(mine)
    assert content.decode("utf-8-sig").splitlines()[0] == "data;titulo;descricao"
    assert "10/07/2024;Queda da NVIDIA;Ações de tecnologia caem" in content.decode("utf-8-sig")
    records = parse_user_csv(content)
    assert records == [{"data": pd.Timestamp("2024-07-10"), "categoria": USER_CATEGORY,
                        "titulo": "Queda da NVIDIA", "descricao": "Ações de tecnologia caem"}]

    sem_descricao = parse_user_csv("Data;Titulo\n01/02/2023;Evento A\n02/02/2023;\n".encode())
    assert len(sem_descricao) == 1 and sem_descricao[0]["descricao"] == ""


@pytest.mark.parametrize("content", [
    b"data;descricao\n01/02/2023;x\n",          # sem título
    b"data;titulo\n2023-02-01;Evento\n",        # data fora do formato dd/mm/aaaa
    b"",                                        # arquivo vazio
])
def test_csv_invalido(content):
    with pytest.raises(ValueError, match="colunas data e titulo"):
        parse_user_csv(content)
    assert "ponto e vírgula" in CSV_FORMAT_ERROR


def test_nota_nao_atribui_causa():
    assert "não indicam que o evento causou" in EVENTS_NOTE
    assert contains_forbidden_phrase(EVENTS_NOTE) is None
