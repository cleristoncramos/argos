import os
import sys
from datetime import datetime, timedelta
from html import escape

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.ui.asset_cards import render_selected_asset_cards
from app.ui.colors import tone_icon, tone_of
from app.ui.comparison_info import render_comparison_notes
from app.ui.data_info import DATA_SOURCE, render_catalog_notice
from app.ui.disclaimers import (
    render_footer_disclaimer,
    render_methodology_limitations,
    render_profile_limitation_notice,
)
from app.ui.education import render_what_it_means
from app.ui.metric_card import render_metric_card
from app.ui.sidebar import (
    GROUP_MAPPING,
    fetch_recent,
    inject_compact_dropdown_script,
    inject_compact_sidebar_css,
)
from app.ui.state import initialize_asset_state
from app.ui.tables import (
    date_cell,
    number_cell,
    percent_cell,
    render_table,
    text_cell,
)

from core.analyzer import calculate_returns
from core.assets import ASSETS
from core.comparison import (
    build_base_100_table,
    build_price_table,
    calculate_correlation_matrix,
    calculate_returns_table,
    create_comparison_summary,
    format_return_pct,
)
from core.comparison_texts import (
    HIGHLIGHT_LABELS,
    LEGEND_HINT,
    SEASONALITY_COMPARISON_NOTE,
)
from core.comparison_checks import (
    build_spans,
    check_period_divergence,
    comparison_notes,
)
from core.config import ANNUALIZATION_FACTORS, config
from core.currency import currency_info
from core.data_loader import download_active_data
from core.data_processor import (
    aggregate_by_frequency,
    prepare_dataframe,
    select_primary_variable,
)
from core.date_validation import validate_date_range
from core.exports import csv_filename, dataframe_to_csv_bytes
from core.formatters import format_number_br
from core.periods import (
    DEFAULT_PERIOD,
    PERIOD_OPTIONS,
    period_start_date,
)
from core.risk_metrics import build_risk_summary, calculate_drawdown
from core.seasonality import SEASONALITY_METHOD_TEXT, compare_monthly_averages
from core.ticker_input import validate_ticker


MAX_COMPARED = 5

NON_POSITIVE_WARNING = (
    "Símbolos excluídos por terem preços iguais ou abaixo de zero no período, "
    "o que impede o cálculo de retorno, drawdown e Base 100 (ex.: petróleo WTI "
    "em abril de 2020): "
)

PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "responsive": True,
}


# ==========================================================
# Chaves de estado
# ==========================================================
COMPARISON_PERIOD_STATE_KEY = "comparison_period"
COMPARISON_START_DATE_STATE_KEY = "comparison_start_date"
COMPARISON_END_DATE_STATE_KEY = "comparison_end_date"
COMPARISON_FREQUENCY_STATE_KEY = "comparison_frequency"
COMPARISON_RISK_FREE_RATE_STATE_KEY = "comparison_risk_free_rate_pct"
COMPARISON_SYMBOLS_STATE_KEY = "comparison_symbols_input"
COMPARISON_CLASS_STATE_KEY = "comparison_selected_class"
COMPARISON_CUSTOM_MSG_KEY = "comparison_custom_msg"

COMPARISON_PERIOD_WIDGET_KEY = "comparison_period_widget"
COMPARISON_START_DATE_WIDGET_KEY = "comparison_start_date_widget"
COMPARISON_END_DATE_WIDGET_KEY = "comparison_end_date_widget"
COMPARISON_FREQUENCY_WIDGET_KEY = "comparison_frequency_widget"
COMPARISON_RISK_FREE_RATE_WIDGET_KEY = "comparison_risk_free_rate_pct_widget"
COMPARISON_CLASS_WIDGET_KEY = "comparison_class_widget"
COMPARISON_SYMBOLS_WIDGET_KEY = "comparison_symbols_widget"
COMPARISON_CUSTOM_INPUT_KEY = "comparison_custom_ticker_input"
COMPARISON_COMMON_PERIOD_KEY = "comparison_common_period_widget"


# ==========================================================
# Utilitários de catálogo
# ==========================================================
def asset_meta(ticker: str) -> dict | None:
    return next((a for a in ASSETS if a["ticker"] == ticker), None)


def asset_or_placeholder(ticker: str) -> dict:
    """Metadados do catálogo ou um registro mínimo para tickers digitados."""
    return asset_meta(ticker) or {
        "ticker": ticker,
        "name": ticker,
        "group": "",
        "icon": "📊",
    }


def get_asset_full_name(ticker: str) -> str:
    asset = asset_meta(ticker)
    if asset:
        return f"{asset['name']} ({ticker})"
    return ticker


def get_asset_multiline_name(ticker: str) -> str:
    asset = asset_meta(ticker)
    if asset:
        return f"{asset['name']}<br>({ticker})"
    return ticker


def format_multiselect_option(ticker: str) -> str:
    """Embeleza o ticker exibido no multiselect usando os dados originais do ativo."""
    a = asset_meta(ticker)
    if not a:
        return f"{ticker} — fora do catálogo"
    if a.get("group", a.get("class", "")) == "forex":
        return f"{a['ticker']} — {a.get('description', a.get('descricao', a.get('name')))}"
    return f"{a['ticker']} — {a.get('name')}"


# ==========================================================
# Sincronização de widgets
# ==========================================================
def sync_comparison_period() -> None:
    st.session_state[COMPARISON_PERIOD_STATE_KEY] = st.session_state[
        COMPARISON_PERIOD_WIDGET_KEY
    ]

def sync_comparison_start_date() -> None:
    st.session_state[COMPARISON_START_DATE_STATE_KEY] = st.session_state[
        COMPARISON_START_DATE_WIDGET_KEY
    ]

def sync_comparison_end_date() -> None:
    st.session_state[COMPARISON_END_DATE_STATE_KEY] = st.session_state[
        COMPARISON_END_DATE_WIDGET_KEY
    ]

def sync_comparison_frequency() -> None:
    st.session_state[COMPARISON_FREQUENCY_STATE_KEY] = st.session_state[
        COMPARISON_FREQUENCY_WIDGET_KEY
    ]

def sync_comparison_risk_free_rate() -> None:
    st.session_state[COMPARISON_RISK_FREE_RATE_STATE_KEY] = float(
        st.session_state[COMPARISON_RISK_FREE_RATE_WIDGET_KEY]
    )

def sync_comparison_class() -> None:
    """Sincroniza a classe selecionada no callback, antes do rerun."""
    st.session_state[COMPARISON_CLASS_STATE_KEY] = st.session_state[
        COMPARISON_CLASS_WIDGET_KEY
    ]

def sync_comparison_symbols() -> None:
    """Sincroniza os tickers selecionados no callback, antes do rerun."""
    selected = st.session_state[COMPARISON_SYMBOLS_WIDGET_KEY]
    st.session_state[COMPARISON_SYMBOLS_STATE_KEY] = ",".join(selected)


def add_custom_ticker() -> None:
    """
    Valida um ticker digitado e o acrescenta à seleção. Roda como callback
    do botão, portanto pode alterar o estado do multiselect com segurança.
    A validação consulta a fonte e pode levar alguns segundos.
    """
    raw = st.session_state.get(COMPARISON_CUSTOM_INPUT_KEY, "")
    current = list(st.session_state.get(COMPARISON_SYMBOLS_WIDGET_KEY, []))

    result = validate_ticker(raw, fetch_recent)

    if not result.ok:
        st.session_state[COMPARISON_CUSTOM_MSG_KEY] = ("error", result.message)
        return

    if result.ticker in current:
        st.session_state[COMPARISON_CUSTOM_MSG_KEY] = (
            "info", f"{result.ticker} já está na seleção.",
        )
        return

    if len(current) >= MAX_COMPARED:
        st.session_state[COMPARISON_CUSTOM_MSG_KEY] = (
            "error", f"A comparação aceita no máximo {MAX_COMPARED} ativos.",
        )
        return

    current.append(result.ticker)
    st.session_state[COMPARISON_SYMBOLS_WIDGET_KEY] = current
    st.session_state[COMPARISON_SYMBOLS_STATE_KEY] = ",".join(current)
    st.session_state[COMPARISON_CUSTOM_INPUT_KEY] = ""
    st.session_state[COMPARISON_CUSTOM_MSG_KEY] = (
        "success", f"{result.ticker} adicionado à seleção.",
    )


# ==========================================================
# Estado inicial
# ==========================================================
def initialize_comparison_state() -> None:
    today = datetime.now().date()
    asset_period = st.session_state.get("comparison_period", DEFAULT_PERIOD)

    asset_start_date = st.session_state.get(
        "comparison_start_date",
        period_start_date(DEFAULT_PERIOD, today),
    )
    asset_end_date = st.session_state.get("comparison_end_date", today)
    asset_frequency = st.session_state.get("comparison_frequency", "Mensal")
    asset_class = st.session_state.get(COMPARISON_CLASS_STATE_KEY, None)

    symbols_str = st.session_state.get(COMPARISON_SYMBOLS_STATE_KEY, "")
    symbols_list = [s.strip() for s in symbols_str.split(",") if s.strip()]

    defaults = {
        COMPARISON_PERIOD_STATE_KEY: asset_period,
        COMPARISON_START_DATE_STATE_KEY: asset_start_date,
        COMPARISON_END_DATE_STATE_KEY: asset_end_date,
        COMPARISON_FREQUENCY_STATE_KEY: asset_frequency,
        COMPARISON_RISK_FREE_RATE_STATE_KEY: 0.0,
        COMPARISON_SYMBOLS_STATE_KEY: symbols_str,
        COMPARISON_CLASS_STATE_KEY: asset_class,
        COMPARISON_CUSTOM_MSG_KEY: None,
        COMPARISON_PERIOD_WIDGET_KEY: asset_period,
        COMPARISON_START_DATE_WIDGET_KEY: asset_start_date,
        COMPARISON_END_DATE_WIDGET_KEY: asset_end_date,
        COMPARISON_FREQUENCY_WIDGET_KEY: asset_frequency,
        COMPARISON_RISK_FREE_RATE_WIDGET_KEY: 0.0,
        COMPARISON_CLASS_WIDGET_KEY: asset_class,
        COMPARISON_SYMBOLS_WIDGET_KEY: symbols_list,
        COMPARISON_CUSTOM_INPUT_KEY: "",
        COMPARISON_COMMON_PERIOD_KEY: False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ==========================================================
# Layout e cards
# ==========================================================
def apply_custom_layout(fig):
    fig.update_layout(
        title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        font=dict(family="Inter, Arial, sans-serif", color="#334155")
    )
    return fig


def render_custom_metric_card(
    title: str,
    asset: str,
    raw_value: float,
    formatted_str: str,
    subtitle: str | None = None,
) -> None:
    """Card de destaque: nome do ativo + selo colorido com o valor."""
    render_metric_card(
        title,
        escape(asset),
        value_size="1.1rem",
        subtitle=subtitle,
        badge=(f"{tone_icon(raw_value)} {formatted_str}", tone_of(raw_value)),
    )


def extreme_row(dataframe: pd.DataFrame, column: str, largest: bool = True):
    """Linha com o maior/menor valor da coluna, ignorando NaN (None se vazia)."""
    if column not in dataframe.columns:
        return None
    values = dataframe[column].dropna()
    if values.empty:
        return None
    index = values.idxmax() if largest else values.idxmin()
    return dataframe.loc[index]


def render_highlight(title: str, row, value_column: str, formatter) -> None:
    if row is None:
        render_metric_card(title, "N/A", value_size="1.1rem")
        return
    raw_value = row[value_column]
    render_custom_metric_card(
        title,
        get_asset_full_name(row["Ativo"]),
        raw_value,
        formatter(raw_value),
        subtitle="No período analisado",
    )


# ==========================================================
# Tabelas (componente padrão app/ui/tables.py)
# ==========================================================
_NUMERIC_STYLE = "text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;"
_CENTER_STYLE = "text-align:center;white-space:nowrap;font-variant-numeric:tabular-nums;"


def asset_cell(value):
    """Ticker -> 'Nome (TICKER)', alinhado à esquerda."""
    if value is None or pd.isna(value):
        return "—", "text-align:left;white-space:nowrap;"
    return get_asset_full_name(str(value)), "text-align:left;white-space:nowrap;"


def integer_cell(value):
    if value is None or pd.isna(value):
        return "—", _NUMERIC_STYLE
    return str(int(value)), _NUMERIC_STYLE


def correlation_cell(value):
    if value is None or pd.isna(value):
        return "—", _CENTER_STYLE
    try:
        return f"{float(value):.2f}".replace(".", ","), _CENTER_STYLE
    except (TypeError, ValueError):
        return str(value), _CENTER_STYLE


def render_summary_table(dataframe: pd.DataFrame) -> None:
    columns = [
        "Ativo", "Observações", "Primeiro valor", "Último valor",
        "Retorno total", "Retorno médio", "Volatilidade",
        "Drawdown máximo", "Percentual positivo", "Sharpe",
    ]
    columns = [c for c in columns if c in dataframe.columns]

    render_table(
        dataframe,
        columns,
        {
            "Ativo": asset_cell,
            "Observações": integer_cell,
            "Primeiro valor": number_cell,
            "Último valor": number_cell,
            "Retorno total": percent_cell(colored=True),
            "Retorno médio": percent_cell(colored=True),
            "Volatilidade": percent_cell(),
            "Drawdown máximo": percent_cell(),
            "Percentual positivo": percent_cell(),
            "Sharpe": number_cell,
        },
        max_height=None,
    )


def render_correlation_table(correlation_matrix: pd.DataFrame) -> None:
    if correlation_matrix is None or correlation_matrix.empty:
        st.info("Não há dados suficientes para exibir a correlação.")
        return

    display_df = correlation_matrix.copy()
    display_df.index = display_df.index.map(get_asset_full_name)
    display_df.columns = display_df.columns.map(get_asset_full_name)
    display_df.index.name = "Ativo"
    display_df = display_df.reset_index()
    columns = display_df.columns.tolist()

    formatters = {"Ativo": text_cell}
    formatters.update({c: correlation_cell for c in columns if c != "Ativo"})

    render_table(display_df, columns, formatters, max_height=None)


def render_asset_metrics_table(dataframe: pd.DataFrame) -> None:
    columns = [
        "Ativo", "Retorno total", "Retorno médio", "Volatilidade",
        "Drawdown máximo", "Percentual positivo", "Sharpe",
    ]
    columns = [c for c in columns if c in dataframe.columns]

    display_df = dataframe[columns].sort_values(
        by="Retorno total",
        ascending=False,
        na_position="last",
    )

    render_table(
        display_df,
        columns,
        {
            "Ativo": asset_cell,
            "Retorno total": percent_cell(colored=True),
            "Retorno médio": percent_cell(colored=True),
            "Volatilidade": percent_cell(),
            "Drawdown máximo": percent_cell(),
            "Percentual positivo": percent_cell(),
            "Sharpe": number_cell,
        },
        header_labels={"Percentual positivo": "Períodos positivos"},
        max_height=None,
    )


def render_normalized_data_table(dataframe: pd.DataFrame) -> None:
    if dataframe is None or dataframe.empty:
        st.info("Não há dados normalizados disponíveis para exibição.")
        return

    columns = dataframe.columns.tolist()
    if "Date" in columns:
        columns = ["Date"] + [c for c in columns if c != "Date"]

    display_df = dataframe[columns].copy()
    display_df = display_df.rename(
        columns={c: get_asset_full_name(c) for c in columns if c != "Date"}
    )
    columns = display_df.columns.tolist()

    formatters = {"Date": date_cell}
    formatters.update({c: number_cell for c in columns if c != "Date"})

    render_table(display_df, columns, formatters, max_height=450)


def render_asset_metadata_table(tickers: list[str], used_spans) -> None:
    """Metadados do catálogo + período efetivamente usado de cada ativo."""
    spans_by_ticker = {s.ticker: s for s in used_spans}
    rows = []
    for ticker in tickers:
        meta = asset_meta(ticker)
        span = spans_by_ticker.get(ticker)
        rows.append({
            "Ativo": get_asset_full_name(ticker),
            "Classe": meta["class"] if meta else "Fora do catálogo",
            "Subclasse": meta["subcategory"] if meta else "—",
            "Mercado": meta["market"] if meta else "—",
            "Unidade": currency_info(ticker).label,
            "Início": span.start if span else None,
            "Fim": span.end if span else None,
            "Obs. diárias": span.observations if span else None,
        })

    render_table(
        pd.DataFrame(rows),
        ["Ativo", "Classe", "Subclasse", "Mercado", "Unidade", "Início", "Fim", "Obs. diárias"],
        {
            "Ativo": text_cell,
            "Classe": text_cell,
            "Subclasse": text_cell,
            "Mercado": text_cell,
            "Unidade": text_cell,
            "Início": date_cell,
            "Fim": date_cell,
            "Obs. diárias": integer_cell,
        },
        max_height=None,
        min_width=900,
    )


# ==========================================================
# Heatmap de correlação
# ==========================================================
def render_correlation_heatmap(correlation_matrix: pd.DataFrame) -> None:
    if correlation_matrix is None or correlation_matrix.empty:
        st.info("Não há dados suficientes para calcular a correlação.")
        return

    correlation_plot = correlation_matrix.astype(float).copy()
    asset_order = correlation_plot.columns.tolist()

    if len(asset_order) < 2:
        st.info("São necessários pelo menos dois ativos.")
        return

    correlation_plot = correlation_plot.reindex(
        index=asset_order,
        columns=asset_order,
    )

    x_assets = asset_order[:-1]
    y_assets = asset_order[1:]

    x_names = [get_asset_multiline_name(t) for t in x_assets]
    y_names = [get_asset_multiline_name(t) for t in y_assets]

    triangular_values = np.full(
        (len(y_assets), len(x_assets)),
        np.nan,
        dtype=float,
    )
    text_values = np.empty(triangular_values.shape, dtype=object)
    customdata = np.empty(triangular_values.shape, dtype=object)

    for row_index, y_asset in enumerate(y_assets):
        for column_index, x_asset in enumerate(x_assets):
            orig_x_idx = asset_order.index(x_asset)
            orig_y_idx = asset_order.index(y_asset)

            if orig_x_idx >= orig_y_idx:
                text_values[row_index, column_index] = ""
                customdata[row_index, column_index] = None
                continue

            value = correlation_plot.loc[y_asset, x_asset]
            triangular_values[row_index, column_index] = value
            text_values[row_index, column_index] = (
                f"{value:.2f}".replace(".", ",")
            )
            customdata[row_index, column_index] = float(value)

    heatmap = go.Heatmap(
        z=triangular_values,
        x=x_names,
        y=y_names,
        zmin=-1,
        zmax=1,
        colorscale=[
            [0.00, "#4575B4"],
            [0.25, "#91BFDB"],
            [0.50, "#F7F7F7"],
            [0.75, "#FC8D59"],
            [1.00, "#D73027"],
        ],
        xgap=2,
        ygap=2,
        customdata=customdata,
        text=text_values,
        texttemplate="%{text}",
        textfont={
            "family": "Inter, Arial, sans-serif",
            "size": 14,
            "color": "#334155",
        },
        hovertemplate=(
            "<b>%{y}</b> × <b>%{x}</b><br>"
            "Correlação: %{customdata:.2f}<extra></extra>"
        ),
        colorbar={
            "title": {"text": "Correlação", "side": "right"},
            "tickvals": [-1, -0.5, 0, 0.5, 1],
            "ticktext": ["-1,00", "-0,50", "0,00", "0,50", "1,00"],
            "thickness": 14,
            "len": 0.78,
            "outlinewidth": 0,
        },
    )

    figure_size = max(420, min(720, 100 * len(x_assets) + 150))
    figure = go.Figure(data=[heatmap])
    figure = apply_custom_layout(figure)
    figure.update_layout(
        height=figure_size,
        xaxis={
            "title": None,
            "showgrid": False,
            "zeroline": False,
            "showline": False,
            "constrain": "domain",
            "categoryorder": "array",
            "categoryarray": x_names,
            "tickfont": {"size": 12, "color": "#475569"},
            "fixedrange": True,
        },
        yaxis={
            "title": None,
            "showgrid": False,
            "zeroline": False,
            "showline": False,
            "autorange": "reversed",
            "scaleanchor": "x",
            "scaleratio": 1,
            "categoryorder": "array",
            "categoryarray": y_names,
            "tickfont": {"size": 12, "color": "#475569"},
            "fixedrange": True,
        },
    )

    with st.container(border=True):
        st.plotly_chart(
            figure,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )


# ==========================================================
# Configuração da página
# ==========================================================
st.set_page_config(
    page_title="Argos DataLab",
    page_icon="⚖️",
    layout="wide",
)

initialize_asset_state()
initialize_comparison_state()

st.title("⚖️ Comparação de Ativos")
st.markdown(
    "<p style='font-size:1.1rem;color:#475569;margin-bottom:2rem;'>"
    "Compare o comportamento histórico de diferentes ativos através de métricas de retorno, "
    "volatilidade, drawdown e correlação.</p>",
    unsafe_allow_html=True,
)


# ==========================================================
# Parâmetros da comparação
# ==========================================================
with st.sidebar:
    inject_compact_sidebar_css()
    inject_compact_dropdown_script()

    st.header("⚙️ Parâmetros da Comparação")

    groups = []
    for asset in ASSETS:
        g = asset.get("group", asset.get("class", "Outros"))
        if g not in groups:
            groups.append(g)

    st.selectbox(
        "Classe do Ativo:",
        options=groups,
        placeholder="Selecione uma classe...",
        format_func=lambda x: GROUP_MAPPING.get(str(x).lower(), str(x).replace("_", " ").title()),
        key=COMPARISON_CLASS_WIDGET_KEY,
        on_change=sync_comparison_class,
    )

    selected_class = st.session_state[COMPARISON_CLASS_STATE_KEY]

    previously_selected_tickers = st.session_state.get(
        COMPARISON_SYMBOLS_WIDGET_KEY,
        [],
    )

    valid_options_tickers = []
    seen = set()

    # O ticker entra nas opções se for da classe selecionada OU se já estiver
    # selecionado (permite comparar classes diferentes e tickers digitados).
    for asset in ASSETS:
        asset_group = asset.get("group", asset.get("class", "Outros"))
        is_in_group = (asset_group == selected_class)
        is_selected = (asset["ticker"] in previously_selected_tickers)

        if (is_in_group or is_selected) and asset["ticker"] not in seen:
            valid_options_tickers.append(asset["ticker"])
            seen.add(asset["ticker"])

    for ticker in previously_selected_tickers:
        if ticker not in seen:
            valid_options_tickers.append(ticker)
            seen.add(ticker)

    st.multiselect(
        "Símbolo/Nome do Ativo:",
        options=valid_options_tickers,
        max_selections=MAX_COMPARED,
        format_func=format_multiselect_option,
        disabled=(selected_class is None and not previously_selected_tickers),
        placeholder="Selecione um ativo",
        help="Selecione uma classe acima para habilitar." if selected_class is None else "Digite para buscar por nome ou código na classe selecionada.",
        key=COMPARISON_SYMBOLS_WIDGET_KEY,
        on_change=sync_comparison_symbols,
    )

    with st.expander("⌨️ Digitar ticker (avançado)", expanded=False):
        st.text_input(
            "Ticker (código do Yahoo Finance)",
            key=COMPARISON_CUSTOM_INPUT_KEY,
            placeholder="Ex.: PETR4.SA, AAPL, BTC-USD",
            help=(
                "Para usuários avançados. Ações brasileiras terminam em .SA, "
                "criptomoedas em -USD e câmbio em =X. A validação consulta a "
                "fonte e pode levar alguns segundos."
            ),
        )
        st.button(
            "➕ Adicionar ao comparativo",
            key="comparison_add_custom",
            on_click=add_custom_ticker,
            use_container_width=True,
        )
        custom_message = st.session_state.get(COMPARISON_CUSTOM_MSG_KEY)
        if custom_message:
            {"error": st.error, "success": st.success}.get(
                custom_message[0], st.info
            )(custom_message[1])

    selected_tickers = st.session_state[COMPARISON_SYMBOLS_WIDGET_KEY]
    symbols_input = st.session_state[COMPARISON_SYMBOLS_STATE_KEY]

    st.divider()

    st.selectbox(
        "Período",
        options=PERIOD_OPTIONS,
        key=COMPARISON_PERIOD_WIDGET_KEY,
        on_change=sync_comparison_period,
    )

    selected_period = st.session_state[COMPARISON_PERIOD_STATE_KEY]
    today = datetime.now().date()

    if selected_period == "Personalizado":
        st.date_input(
            "Data inicial",
            key=COMPARISON_START_DATE_WIDGET_KEY,
            on_change=sync_comparison_start_date,
        )

        st.date_input(
            "Data final",
            key=COMPARISON_END_DATE_WIDGET_KEY,
            on_change=sync_comparison_end_date,
        )
    else:
        st.session_state[COMPARISON_START_DATE_STATE_KEY] = period_start_date(
            selected_period, today
        )
        st.session_state[COMPARISON_END_DATE_STATE_KEY] = today

    st.selectbox(
        "Frequência",
        options=config.FREQUENCIES,
        key=COMPARISON_FREQUENCY_WIDGET_KEY,
        on_change=sync_comparison_frequency,
    )

    st.checkbox(
        "Comparar apenas o período comum",
        key=COMPARISON_COMMON_PERIOD_KEY,
        help=(
            "Quando os ativos têm históricos de tamanhos diferentes, corta todos "
            "para o intervalo em que todos têm dados. Torna as métricas "
            "diretamente comparáveis, mas usa menos histórico."
        ),
    )

    st.number_input(
        "Taxa livre de risco anual (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.25,
        key=COMPARISON_RISK_FREE_RATE_WIDGET_KEY,
        on_change=sync_comparison_risk_free_rate,
        help="Exemplo: 10,00 representa 10% ao ano.",
    )

    load_comparison = st.button(
        "📊 Comparar ativos",
        type="primary",
        key="comparison_load_button",
        use_container_width=True
    )

start_date = st.session_state[COMPARISON_START_DATE_STATE_KEY]
end_date = st.session_state[COMPARISON_END_DATE_STATE_KEY]
frequency = st.session_state[COMPARISON_FREQUENCY_STATE_KEY]
risk_free_rate_pct = float(
    st.session_state[COMPARISON_RISK_FREE_RATE_STATE_KEY]
)
annual_risk_free_rate = risk_free_rate_pct / 100


# ==========================================================
# Processamento da comparação
# ==========================================================
if load_comparison:
    symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]

    if len(symbols) < 2:
        st.sidebar.error("Selecione pelo menos dois ativos para comparar.")
        st.stop()

    date_check = validate_date_range(start_date, end_date, today)
    if not date_check.ok:
        st.sidebar.error(date_check.message)
        st.stop()

    use_common_period = bool(st.session_state.get(COMPARISON_COMMON_PERIOD_KEY, False))

    downloaded = {}
    failed_symbols = []

    with st.spinner("Baixando os ativos..."):
        for symbol in symbols:
            df_raw = download_active_data(
                symbol=symbol,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                interval="1d",
            )

            if df_raw is None or df_raw.empty:
                failed_symbols.append(symbol)
                continue

            downloaded[symbol] = prepare_dataframe(df_raw)

    if len(downloaded) < 2:
        st.session_state["comparison_loaded"] = False
        st.session_state["comparison_query"] = None
        st.error(
            "Não foi possível obter dados válidos para pelo menos dois ativos."
        )
        if failed_symbols:
            st.warning(
                "Símbolos sem dados válidos: " + ", ".join(failed_symbols)
            )
        st.stop()

    # Períodos históricos de cada ativo (datas diárias, antes de agregar)
    period_check = check_period_divergence(
        build_spans({s: d["Date"] for s, d in downloaded.items()})
    )

    if use_common_period:
        if not period_check.has_common_period:
            st.session_state["comparison_loaded"] = False
            st.session_state["comparison_query"] = None
            st.error(
                "Os ativos selecionados não possuem período em comum no intervalo "
                "consultado. Desative a opção de período comum ou troque os ativos."
            )
            st.stop()

        common_start_ts = pd.Timestamp(period_check.common_start)
        common_end_ts = pd.Timestamp(period_check.common_end) + timedelta(days=1)
        downloaded = {
            symbol: frame[
                (frame["Date"] >= common_start_ts) & (frame["Date"] < common_end_ts)
            ].reset_index(drop=True)
            for symbol, frame in downloaded.items()
        }

    asset_data = {}
    non_positive_symbols = []

    with st.spinner("Processando os ativos..."):
        for symbol, df_prepared in downloaded.items():
            df_aggregated = aggregate_by_frequency(df_prepared, frequency)
            df_primary = select_primary_variable(df_aggregated, "Close")

            if len(df_primary) < 2:
                failed_symbols.append(symbol)
                continue

            try:
                df_returns = calculate_returns(df_primary, "Value")
                asset_data[symbol] = calculate_drawdown(df_returns, "Value")
            except ValueError:
                # Preços iguais ou abaixo de zero (ex.: petróleo WTI em abril de
                # 2020) impedem retorno percentual, drawdown e Base 100.
                non_positive_symbols.append(symbol)

    if len(asset_data) < 2:
        st.session_state["comparison_loaded"] = False
        st.session_state["comparison_query"] = None
        st.error(
            "Não foi possível obter dados suficientes para pelo menos dois ativos."
        )
        if failed_symbols:
            st.warning(
                "Símbolos sem dados válidos ou com dados insuficientes: "
                + ", ".join(failed_symbols)
            )
        if non_positive_symbols:
            st.warning(NON_POSITIVE_WARNING + ", ".join(non_positive_symbols))
        st.stop()

    used_spans = build_spans(
        {s: d["Date"] for s, d in downloaded.items() if s in asset_data}
    )

    # Mensal/semanal: alinha por fim do período (calendário), não pelo
    # último pregão de cada ativo. Só usa PeriodEnd se todos os ativos o têm.
    can_align_by_period = frequency in ("Semanal", "Mensal") and all(
        "PeriodEnd" in frame.columns for frame in asset_data.values()
    )
    align_col = "PeriodEnd" if can_align_by_period else "Date"

    base_100_table = build_base_100_table(asset_data, align_col=align_col)
    price_table = build_price_table(asset_data, align_col=align_col)
    returns_table = calculate_returns_table(price_table)
    correlation_matrix = calculate_correlation_matrix(returns_table)
    summary = create_comparison_summary(asset_data)

    annualization_factor = ANNUALIZATION_FACTORS.get(
        frequency,
        252,
    )

    risk_rows = []
    for symbol, dataframe in asset_data.items():
        metrics = build_risk_summary(
            df=dataframe,
            value_col="Value",
            annualization_factor=float(annualization_factor),
            annual_risk_free_rate=annual_risk_free_rate,
        )
        risk_rows.append(
            {
                "Ativo": symbol,
                "Volatilidade": metrics.get("Volatilidade"),
                "Drawdown máximo": metrics.get("Drawdown máximo"),
                "Percentual positivo": metrics.get("Percentual positivo"),
                "Sharpe": metrics.get("Sharpe"),
            }
        )

    summary = summary.merge(
        pd.DataFrame(risk_rows),
        on="Ativo",
        how="left",
    )

    st.session_state["comparison_loaded"] = True
    st.session_state["comparison_query"] = {
        "symbols_input": symbols_input,
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
        "risk_free_rate_pct": risk_free_rate_pct,
        "common_period": use_common_period,
    }
    st.session_state["comparison_asset_data"] = asset_data
    st.session_state["comparison_failed_symbols"] = failed_symbols
    st.session_state["comparison_non_positive_symbols"] = non_positive_symbols
    st.session_state["comparison_base_100_table"] = base_100_table
    st.session_state["comparison_price_table"] = price_table
    st.session_state["comparison_returns_table"] = returns_table
    st.session_state["comparison_correlation_matrix"] = correlation_matrix
    st.session_state["comparison_summary"] = summary
    st.session_state["comparison_period_check"] = period_check
    st.session_state["comparison_used_spans"] = used_spans
    st.session_state["comparison_fetched_at"] = datetime.now()


# ==========================================================
# Consulta confirmada
# ==========================================================
query = st.session_state.get("comparison_query")

if (
    not st.session_state.get("comparison_loaded")
    or query is None
    or "comparison_base_100_table" not in st.session_state
    or "comparison_correlation_matrix" not in st.session_state
    or "comparison_summary" not in st.session_state
):
    st.info(
        "Selecione de 2 a 5 ativos no menu lateral; "
        "depois clique em **Comparar ativos**."
    )
    st.stop()

asset_data = st.session_state["comparison_asset_data"]
failed_symbols = st.session_state["comparison_failed_symbols"]
non_positive_symbols = st.session_state.get("comparison_non_positive_symbols", [])
base_100_table = st.session_state["comparison_base_100_table"]
correlation_matrix = st.session_state["comparison_correlation_matrix"]
summary = st.session_state["comparison_summary"]
period_check = st.session_state.get("comparison_period_check")
used_spans = st.session_state.get("comparison_used_spans", [])
fetched_at = st.session_state.get("comparison_fetched_at")
start_date = query["start_date"]
end_date = query["end_date"]
frequency = query["frequency"]
risk_free_rate_pct = float(query["risk_free_rate_pct"])
aligned_to_common = bool(query.get("common_period", False))
annualization_factor = ANNUALIZATION_FACTORS.get(frequency, 252)
compared_tickers = list(asset_data.keys())

if failed_symbols:
    st.warning(
        "Os seguintes símbolos não retornaram dados válidos ou suficientes: "
        + ", ".join(failed_symbols)
    )

if non_positive_symbols:
    st.warning(NON_POSITIVE_WARNING + ", ".join(non_positive_symbols))


# =====================
# Cards visuais dos ativos comparados (logo/ícone + ticker + nome)
# =====================
render_selected_asset_cards([asset_or_placeholder(t) for t in compared_tickers])
st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)


# =====================
# Comparabilidade: períodos divergentes, moedas, taxas, calendários
# =====================
if period_check is not None:
    render_comparison_notes(
        comparison_notes(
            period_check,
            compared_tickers,
            frequency,
            aligned_to_common=aligned_to_common,
        )
    )

consulted = fetched_at.strftime("%d/%m/%Y às %H:%M") if fetched_at else "—"
st.caption(
    f"Fonte: {DATA_SOURCE} · Consulta realizada em {consulted} · "
    f"Todos os ativos usam a frequência **{frequency}**, então as métricas "
    "são calculadas sobre o mesmo tipo de período."
)


# =====================
# Metodologia e metadados dos ativos comparados
# =====================
with st.expander(
    f"✅ Análise gerada para {len(asset_data)} ativos. "
    "Clique para visualizar a metodologia e os ativos comparados.",
    expanded=False,
):
    st.markdown(
        f"**Período solicitado:** {start_date.strftime('%d/%m/%Y')} a "
        f"{end_date.strftime('%d/%m/%Y')} | **Frequência:** {frequency}"
    )
    st.markdown(
        f"**Índice de Sharpe:** taxa livre de risco de "
        f"**{risk_free_rate_pct:.2f}% ao ano** e fator de anualização "
        f"**{annualization_factor}**."
    )
    st.markdown(
        "**Tratamento de dados:** alinhamento por data, com correlações "
        "calculadas somente entre retornos válidos e coincidentes."
    )
    if aligned_to_common:
        st.markdown("**Período comum:** aplicado (todos os ativos cortados para o mesmo intervalo).")

    st.markdown("#### Ativos comparados")
    render_asset_metadata_table(compared_tickers, used_spans)

summary_numeric = summary.copy()
summary_display = summary_numeric.sort_values(
    by="Retorno total",
    ascending=False,
    na_position="last",
).copy()


# ==========================================================
# Paleta de Cores Dinâmica (Multi-linha)
# ==========================================================
color_palette = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]
color_map = {}
for i, symbol in enumerate(summary_numeric["Ativo"].tolist()):
    color_map[symbol] = color_palette[i % len(color_palette)]


# ==========================================================
# Destaques (descrevem o histórico; não são recomendação)
# ==========================================================
st.header("📌 Destaques do Período")

if not summary_numeric.empty:
    highlight_cols = st.columns(4)
    with highlight_cols[0]:
        render_highlight(
            HIGHLIGHT_LABELS["max_return"],
            extreme_row(summary_numeric, "Retorno total", largest=True),
            "Retorno total",
            format_return_pct,
        )
    with highlight_cols[1]:
        render_highlight(
            HIGHLIGHT_LABELS["min_return"],
            extreme_row(summary_numeric, "Retorno total", largest=False),
            "Retorno total",
            format_return_pct,
        )
    with highlight_cols[2]:
        render_highlight(
            HIGHLIGHT_LABELS["min_drawdown"],
            extreme_row(summary_numeric, "Drawdown máximo", largest=True),
            "Drawdown máximo",
            format_return_pct,
        )
    with highlight_cols[3]:
        render_highlight(
            HIGHLIGHT_LABELS["max_sharpe"],
            extreme_row(summary_numeric, "Sharpe", largest=True),
            "Sharpe",
            lambda v: f"Sharpe: {format_number_br(v)}",
        )

    st.caption(
        "Os destaques descrevem o desempenho observado no período analisado. "
        "Não indicam qual ativo é melhor nem recomendam compra ou venda."
    )

render_profile_limitation_notice()

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================================
# Seções: Desempenho, Risco, Correlação e Dados
# ==========================================================
tab_performance, tab_risk, tab_correlation, tab_seasonality, tab_data = st.tabs([
    "📈 Desempenho",
    "🛡️ Risco",
    "🔗 Correlação",
    "🗓️ Sazonalidade",
    "📋 Dados",
])


# ---------- Desempenho ----------
with tab_performance:
    st.markdown("### Evolução de Desempenho Histórico")
    st.markdown(
        "<p style='color:#64748b;font-size:0.95rem;margin-top:-12px;"
        "margin-bottom:24px;'>Comparação de trajetória normalizada em "
        "<b>Base 100</b> no período inicial.</p>",
        unsafe_allow_html=True,
    )

    if not base_100_table.empty:
        base_100_melted = base_100_table.melt(
            id_vars="Date",
            var_name="Ativo",
            value_name="Índice base 100",
        )

        base_100_melted["Nome Ativo"] = base_100_melted["Ativo"].apply(get_asset_full_name)
        color_map_names = {get_asset_full_name(ticker): color for ticker, color in color_map.items()}
        base_100_melted["Tooltip_Value"] = base_100_melted["Índice base 100"].apply(format_number_br)

        fig_base_100 = px.line(
            base_100_melted,
            x="Date",
            y="Índice base 100",
            color="Nome Ativo",
            color_discrete_map=color_map_names,
            custom_data=["Tooltip_Value"]
        )

        fig_base_100 = apply_custom_layout(fig_base_100)

        fig_base_100.update_layout(
            hovermode="x unified",
            legend={
                "title": "",
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
        )

        fig_base_100.update_xaxes(title_text="")
        fig_base_100.update_yaxes(title_text="")

        fig_base_100.update_traces(
            connectgaps=True,
            line={"width": 2.5},
            hovertemplate="%{customdata}<extra></extra>"
        )

        with st.container(border=True):
            st.plotly_chart(
                fig_base_100,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )

        st.caption(
            "Na Base 100, todos os ativos partem de 100 na data inicial. "
            "Compara trajetórias, não preços, e não incorpora variação cambial."
        )
        st.caption(LEGEND_HINT)

    render_what_it_means("base_100")
    render_what_it_means("retorno")


# ---------- Risco ----------
with tab_risk:
    st.markdown("### Métricas de Risco e Retorno por Ativo")
    st.caption(
        f"Volatilidade e Sharpe anualizados com fator **{annualization_factor}** "
        f"(frequência {frequency}) e taxa livre de risco de **{risk_free_rate_pct:.2f}% ao ano**."
    )
    render_asset_metrics_table(summary_numeric)

    render_what_it_means("volatilidade")
    render_what_it_means("drawdown")
    render_what_it_means("sharpe")


# ---------- Correlação ----------
with tab_correlation:
    st.markdown("### Correlação entre Retornos")
    render_correlation_heatmap(correlation_matrix)
    st.caption(
        "A matriz exibe apenas as correlações únicas entre pares de ativos. "
        "A diagonal e os valores duplicados foram ocultados para reduzir "
        "a redundância visual."
    )
    render_correlation_table(correlation_matrix)
    st.caption(
        "A correlação é calculada com retornos históricos coincidentes. "
        "Ela não representa causalidade nem garante comportamento futuro."
    )
    render_what_it_means("correlacao")


# ---------- Sazonalidade ----------
with tab_seasonality:
    st.markdown("### Sazonalidade Mensal Comparada")
    st.caption(SEASONALITY_METHOD_TEXT)
    st.caption(SEASONALITY_COMPARISON_NOTE)

    season_means, season_counts = compare_monthly_averages(asset_data)

    if season_means.empty:
        st.info(
            "Os ativos selecionados não têm meses suficientes para calcular a "
            "variação mensal. Escolha um período mais longo."
        )
    else:
        def _fmt_season(value):
            if pd.isna(value):
                return "—"
            return f"{value:.2f}".replace(".", ",") + "%"

        fig_season = go.Figure()
        for ticker in season_means.columns:
            fig_season.add_trace(
                go.Bar(
                    x=season_means.index,
                    y=season_means[ticker],
                    name=get_asset_full_name(ticker),
                    marker_color=color_map.get(ticker),
                    customdata=[
                        [_fmt_season(v), int(n)]
                        for v, n in zip(season_means[ticker], season_counts[ticker])
                    ],
                    hovertemplate=(
                        "Mês: %{x}<br>Média: %{customdata[0]}"
                        "<br>Anos com dado: %{customdata[1]}<extra>"
                        + escape(ticker)
                        + "</extra>"
                    ),
                )
            )
        fig_season = apply_custom_layout(fig_season)
        fig_season.update_layout(
            barmode="group",
            margin=dict(l=40, r=20, t=40, b=20),
            xaxis_title=None,
            yaxis_title="Média do retorno mensal (%)",
            legend={"title": "", "orientation": "h", "y": 1.12},
        )

        with st.container(border=True):
            st.plotly_chart(fig_season, use_container_width=True, config=PLOTLY_CONFIG)
        st.caption(LEGEND_HINT)

        season_table = pd.DataFrame({"Mês": season_means.index})
        for ticker in season_means.columns:
            season_table[ticker] = [
                f"{_fmt_season(value)} (N={int(n)})"
                for value, n in zip(season_means[ticker], season_counts[ticker])
            ]
        st.dataframe(season_table, hide_index=True, use_container_width=True)

        if (season_counts.replace(0, np.nan).min().min() < 3):
            st.caption(
                "Alguns meses têm menos de 3 anos de dados em algum ativo; "
                "médias com tão poucos anos variam bastante de uma amostra para outra."
            )

    render_what_it_means("sazonalidade")


# ---------- Dados ----------
with tab_data:
    st.markdown("### Resumo Comparativo")
    render_summary_table(summary_display)

    st.markdown("### Dados Normalizados (Base 100)")
    render_normalized_data_table(base_100_table)

    st.download_button(
        label="⬇️ Baixar comparação em CSV",
        data=dataframe_to_csv_bytes(base_100_table),
        file_name=csv_filename("comparacao_ativos_base_100"),
        mime="text/csv",
    )


# ==========================================================
# Limitações, catálogo e rodapé
# ==========================================================
render_methodology_limitations([
    "A correlação usa apenas retornos coincidentes no tempo e não representa causalidade nem garante comportamento futuro.",
    "Quando os ativos têm históricos de tamanhos diferentes, as métricas de cada um valem para o período dele, a menos que a opção \"Comparar apenas o período comum\" esteja ativa.",
    "Ativos em moedas diferentes não têm variação cambial incorporada nos retornos percentuais nem na Base 100.",
    "Taxas de juros (yields) medem o nível da taxa; seus retornos não são equivalentes aos de preços de ativos.",
    f"O fator de anualização usado foi {annualization_factor} (frequência {frequency}) e a taxa livre de risco anual foi {risk_free_rate_pct:.2f}%; alterar esses parâmetros altera Sharpe e volatilidade.",
    "Os destaques descrevem desempenho histórico no período analisado e não indicam qual ativo é melhor, nem compra ou venda.",
    "A sazonalidade comparada usa todos os anos disponíveis de cada ativo; ativos com históricos mais curtos têm menos anos (N) e médias menos estáveis.",
])

render_catalog_notice()

render_footer_disclaimer()