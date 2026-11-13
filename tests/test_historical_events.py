"""Eventos históricos nos gráficos (projeto Previsão; fontes e eventos por ativo na etapa 5 da DL2)."""

from datetime import date

import pandas as pd
import pytest

from core.disclaimers import contains_forbidden_phrase
from core.historical_events import (
    ASSET_CATEGORY,
    CATEGORY_COLORS,
    EVENT_COLUMNS,
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
    sources_table,
    user_events_csv,
    user_events_frame,
)


def test_base_do_sistema_tem_39_eventos_com_fonte():
    events = load_events()
    assert len(events) == 39
    assert events["data"].min() == pd.Timestamp("2016-06-23")
    assert events["data"].max() == pd.Timestamp("2026-11-12")
    assert events["categoria"].value_counts().to_dict() == {
        "Política": 9, "Do ativo": 9, "Mundo": 8, "Mercado e crises": 8, "Saúde": 5,
    }
    assert available_categories(events) == ["Mercado e crises", "Saúde", "Política", "Mundo", ASSET_CATEGORY]
    circuit = events[events["titulo"].str.contains("Circuit breaker")]
    assert len(circuit) == 5          # seis interrupções: o dia 12/03/2020 teve duas
    for _, row in events.iterrows():
        assert row["titulo"] and row["descricao"]
        assert contains_forbidden_phrase(row["descricao"]) is None
        # DL2-D: nenhum evento do sistema sem fonte.
        assert row["fonte"] and row["url"].startswith("https://"), row["titulo"]
        # Evento "Do ativo" sempre diz a que ativos se aplica; evento geral não restringe.
        assert bool(row["ativos"]) == (row["categoria"] == ASSET_CATEGORY), row["titulo"]


def test_eventos_por_ativo():
    events = load_events()
    nvda = events[events["ativos"].str.contains("NVDA")]
    assert list(nvda["titulo"]) == [
        "DeepSeek", "Caso de espionagem na NVIDIA", "Jensen Huang deixa o comando da NVIDIA",
    ]
    todos = list(events["categoria"].unique())
    period = (date(2016, 1, 1), date(2026, 12, 31))
    so_nvda = filter_events(events, todos, *period, ticker="nvda")
    assert set(so_nvda[so_nvda["categoria"] == ASSET_CATEGORY]["ativos"]) == {"NVDA"}
    assert len(so_nvda) == 30 + 3                       # 30 gerais + 3 da NVIDIA
    sem_ativo = filter_events(events, todos, *period)
    assert ASSET_CATEGORY not in set(sem_ativo["categoria"]) and len(sem_ativo) == 30
    cripto = filter_events(events, todos, *period, ticker="ETH-USD")
    assert list(cripto[cripto["categoria"] == ASSET_CATEGORY]["titulo"]) == ["Falência da FTX"]


def test_arquivo_ausente_devolve_base_vazia(tmp_path):
    events = load_events(tmp_path / "nao_existe.csv")
    assert events.empty and list(events.columns) == EVENT_COLUMNS


def test_eventos_do_usuario_e_combinacao():
    assert user_events_frame([]).empty
    mine = user_events_frame([new_user_event(date(2024, 7, 10), "  Queda da NVIDIA ", None)])
    assert mine.iloc[0]["categoria"] == USER_CATEGORY and mine.iloc[0]["titulo"] == "Queda da NVIDIA"
    assert mine.iloc[0]["descricao"] == ""

    assert combine_events(empty_events(), empty_events()).empty
    both = combine_events(load_events(), mine)
    assert len(both) == 40 and available_categories(both)[-1] == USER_CATEGORY
    assert mine.iloc[0]["fonte"] == "" and mine.iloc[0]["ativos"] == ""
    assert pd.api.types.is_datetime64_any_dtype(combine_events(empty_events(), mine)["data"])

    with pytest.raises(ValueError, match="título"):
        new_user_event(date(2024, 1, 1), "   ")


def test_filtro_por_categoria_e_periodo():
    events = load_events()
    covid = filter_events(events, ["Saúde"], date(2020, 1, 1), date(2020, 12, 31))
    assert list(covid["titulo"]) == [
        "Primeiro caso de COVID-19 no Brasil", "OMS caracteriza a COVID-19 como pandemia",
        "Eficácia da vacina da Pfizer",
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
    assert mundo["y"][:3] == [0.0, 50.0, None] and len(mundo["x"]) == 3 * 3   # Fed 2020 e 2 de 2022
    assert mundo["customdata"][3].startswith("<b>Invasão da Ucrânia</b> (24/02/2022)<br>Rússia")
    assert mundo["customdata"][3].endswith("<br><i>Fonte: Nações Unidas</i>")
    assert traces[3]["line"]["color"] == "#111827" and traces[3]["customdata"][0] == "<b>Sem cor</b> (01/06/2021)"
    assert event_traces(empty_events(), 0, 1) == []


def test_csv_do_usuario_ida_e_volta():
    mine = user_events_frame([new_user_event(date(2024, 7, 10), "Queda da NVIDIA", "Ações de tecnologia caem")])
    content = user_events_csv(mine)
    assert content.decode("utf-8-sig").splitlines()[0] == "data;titulo;descricao"
    assert "10/07/2024;Queda da NVIDIA;Ações de tecnologia caem" in content.decode("utf-8-sig")
    records = parse_user_csv(content)
    assert records == [{"data": pd.Timestamp("2024-07-10"), "categoria": USER_CATEGORY,
                        "titulo": "Queda da NVIDIA", "descricao": "Ações de tecnologia caem",
                        "fonte": "", "url": "", "ativos": ""}]

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


def test_tabela_de_fontes():
    events = combine_events(
        filter_events(load_events(), ["Saúde"], date(2020, 3, 1), date(2020, 3, 31)),
        user_events_frame([new_user_event(date(2020, 3, 20), "Meu evento")]),
    )
    table = sources_table(events)
    assert list(table.columns) == ["Data", "Categoria", "Evento", "Fonte", "Endereço"]
    assert table.iloc[0]["Data"] == "11/03/2020" and table.iloc[0]["Fonte"] == "Organização Mundial da Saúde"
    assert table.iloc[1]["Fonte"] == "Evento seu (sem fonte)" and pd.isna(table.iloc[1]["Endereço"])


def test_nota_nao_atribui_causa():
    assert "não indicam que o evento causou" in EVENTS_NOTE
    assert contains_forbidden_phrase(EVENTS_NOTE) is None
