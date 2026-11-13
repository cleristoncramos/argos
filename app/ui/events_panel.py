"""
Painel "Eventos históricos" (recurso trazido do projeto Previsão Financial Risk
em 13/11/2026). O período é o carregado na barra lateral. A lógica fica em
core/historical_events.py.
"""

from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.historical_events import (
    CSV_FORMAT_ERROR,
    EVENTS_NOTE,
    applies_to,
    available_categories,
    combine_events,
    event_traces,
    filter_events,
    load_events,
    new_user_event,
    parse_user_csv,
    sources_table,
    user_events_csv,
    user_events_frame,
)

USER_EVENTS_KEY = "eventos_usuario"
CATEGORIES_KEY = "eventos_categorias"
UPLOAD_READ_KEY = "eventos_upload_lido"
SELECT_ALL_KEY = "eventos_marcar_todas"


@st.cache_data(show_spinner=False)
def _base_events() -> pd.DataFrame:
    return load_events()


def _user_events() -> pd.DataFrame:
    return user_events_frame(st.session_state.get(USER_EVENTS_KEY, []))


def _refresh_categories() -> None:
    # Um evento novo deve aparecer já marcado no filtro de categorias. O filtro já foi
    # desenhado nesta execução, então a marcação é aplicada na próxima, antes dele.
    st.session_state[SELECT_ALL_KEY] = True
    st.rerun()


def _user_events_popover(data_min: date, data_max: date) -> None:
    with st.popover("Adicionar evento próprio", icon=":material/add_location_alt:", use_container_width=True):
        with st.form("form_evento_usuario", clear_on_submit=True, border=False):
            day = st.date_input("Data", value=data_max, min_value=data_min, max_value=data_max, format="DD/MM/YYYY")
            title = st.text_input("Título", max_chars=60, placeholder="Ex.: Queda das ações da NVIDIA")
            description = st.text_input("Descrição (opcional)", max_chars=160)
            if st.form_submit_button("Adicionar", type="primary", use_container_width=True):
                try:
                    st.session_state.setdefault(USER_EVENTS_KEY, []).append(new_user_event(day, title, description))
                except ValueError as error:
                    st.warning(str(error))
                else:
                    _refresh_categories()

        uploaded = st.file_uploader("Ou carregue um CSV de eventos salvo antes", type="csv", key="eventos_upload")
        if uploaded is not None and st.session_state.get(UPLOAD_READ_KEY) != uploaded.file_id:
            try:
                records = parse_user_csv(uploaded.getvalue())
            except ValueError:
                st.error(CSV_FORMAT_ERROR)
            else:
                st.session_state.setdefault(USER_EVENTS_KEY, []).extend(records)
                st.session_state[UPLOAD_READ_KEY] = uploaded.file_id
                _refresh_categories()

        mine = _user_events()
        if not mine.empty:
            st.caption(f"{len(mine)} evento(s) seu(s) nesta sessão. Baixe a lista para usar numa próxima visita.")
            st.download_button(
                "Baixar meus eventos (CSV)",
                data=user_events_csv(mine),
                file_name="meus_eventos.csv",
                mime="text/csv",
                use_container_width=True,
            )
            if st.button("Remover meus eventos", use_container_width=True):
                st.session_state.pop(USER_EVENTS_KEY, None)
                _refresh_categories()


def render_events_panel(df: pd.DataFrame, ticker: str | None = None, date_col: str = "Date") -> pd.DataFrame:
    """
    Escolha das categorias de eventos e eventos do usuário. Devolve os eventos que caem
    no período carregado na barra lateral (o mesmo dos gráficos) e que valem para o
    ativo analisado: os gerais e os ligados a ele (categoria "Do ativo").
    """
    data_min = df[date_col].min().date()
    data_max = df[date_col].max().date()

    st.markdown("#### Eventos históricos")
    st.caption(
        "Veja o que acontecia no mundo no período carregado na barra lateral. Os eventos "
        "aparecem nos gráficos de preço e de volatilidade abaixo."
    )

    events = combine_events(_base_events(), _user_events())
    events = events[applies_to(events, ticker)]
    categories = available_categories(events)
    if st.session_state.pop(SELECT_ALL_KEY, False) or CATEGORIES_KEY not in st.session_state:
        st.session_state[CATEGORIES_KEY] = categories
    else:   # categoria que deixou de existir (ex.: eventos do usuário removidos)
        st.session_state[CATEGORIES_KEY] = [c for c in st.session_state[CATEGORIES_KEY] if c in categories]
    col_categories, col_new = st.columns([1.4, 1], gap="large", vertical_alignment="bottom")
    with col_categories:
        shown = st.multiselect(
            "Eventos históricos nos gráficos",
            options=categories,
            help="Passe o mouse sobre a linha pontilhada para ver o evento; clique na legenda "
                 "do gráfico para ocultar uma categoria.",
            key=CATEGORIES_KEY,
            placeholder="Nenhuma categoria",
        )
    with col_new:
        _user_events_popover(data_min, data_max)

    st.caption(f"ℹ️ {EVENTS_NOTE}")
    selected = filter_events(events, shown, data_min, data_max, ticker)

    # Etapa 5 da DL2 (DL2-D): todo evento do sistema tem fonte, que pode ser conferida aqui.
    if not selected.empty:
        with st.expander(f"📚 Eventos no período e fontes ({len(selected)})"):
            st.dataframe(
                sources_table(selected),
                hide_index=True,
                use_container_width=True,
                column_config={"Endereço": st.column_config.LinkColumn("Endereço", display_text="Abrir fonte")},
            )
    return selected


def add_events(fig: go.Figure, events: pd.DataFrame, y_min: float, y_max: float) -> None:
    """Desenha os eventos e liga a legenda (só com as categorias de eventos)."""
    if events.empty:
        return
    for trace in fig.data:
        trace.showlegend = False
    for trace in event_traces(events, y_min, y_max):
        fig.add_trace(go.Scatter(**{k: v for k, v in trace.items() if k != "type"}))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=-0.12, x=0, title_text="Eventos: "),
    )
