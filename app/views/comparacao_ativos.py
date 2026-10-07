import os
import sys
from datetime import datetime
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
from app.ui.metric_card import render_metric_card
from app.ui.sidebar import (
    GROUP_MAPPING,
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
from core.config import ANNUALIZATION_FACTORS, config
from core.data_loader import download_active_data
from core.data_processor import (
    aggregate_by_frequency,
    prepare_dataframe,
    select_primary_variable,
)
from core.formatters import format_number_br
from core.periods import (
    DEFAULT_PERIOD,
    PERIOD_OPTIONS,
    period_start_date,
)
from core.risk_metrics import build_risk_summary, calculate_drawdown


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

COMPARISON_PERIOD_WIDGET_KEY = "comparison_period_widget"
COMPARISON_START_DATE_WIDGET_KEY = "comparison_start_date_widget"
COMPARISON_END_DATE_WIDGET_KEY = "comparison_end_date_widget"
COMPARISON_FREQUENCY_WIDGET_KEY = "comparison_frequency_widget"
COMPARISON_RISK_FREE_RATE_WIDGET_KEY = "comparison_risk_free_rate_pct_widget"
COMPARISON_CLASS_WIDGET_KEY = "comparison_class_widget"
COMPARISON_SYMBOLS_WIDGET_KEY = "comparison_symbols_widget"


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
    """
    Sincroniza a classe selecionada IMEDIATAMENTE no callback on_change,
    antes do script ser executado novamente. Isso evita o atraso de uma
    execução que causava a necessidade de clicar duas vezes.
    """
    st.session_state[COMPARISON_CLASS_STATE_KEY] = st.session_state[
        COMPARISON_CLASS_WIDGET_KEY
    ]

def sync_comparison_symbols() -> None:
    """
    Sincroniza os tickers selecionados IMEDIATAMENTE no callback on_change.
    Antes, o valor exibido dependia de uma variável (`default_list`)
    recalculada a cada rerun a partir do estado ANTERIOR ao clique --
    por isso o primeiro clique nunca "aparecia" de fato, exigindo um
    segundo clique para ser refletido na tela.
    """
    selected = st.session_state[COMPARISON_SYMBOLS_WIDGET_KEY]
    st.session_state[COMPARISON_SYMBOLS_STATE_KEY] = ",".join(selected)


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
    asset_end_date = st.session_state.get(
        "comparison_end_date",
        today,
    )
    asset_frequency = st.session_state.get(
        "comparison_frequency",
        "Mensal",
    )
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
        COMPARISON_PERIOD_WIDGET_KEY: asset_period,
        COMPARISON_START_DATE_WIDGET_KEY: asset_start_date,
        COMPARISON_END_DATE_WIDGET_KEY: asset_end_date,
        COMPARISON_FREQUENCY_WIDGET_KEY: asset_frequency,
        COMPARISON_RISK_FREE_RATE_WIDGET_KEY: 0.0,
        COMPARISON_CLASS_WIDGET_KEY: asset_class,
        COMPARISON_SYMBOLS_WIDGET_KEY: symbols_list,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ==========================================================
# Utilitários
# ==========================================================
def get_asset_full_name(ticker: str) -> str:
    asset = next((a for a in ASSETS if a["ticker"] == ticker), None)
    if asset:
        return f"{asset['name']} ({ticker})"
    return ticker

def get_asset_multiline_name(ticker: str) -> str:
    asset = next((a for a in ASSETS if a["ticker"] == ticker), None)
    if asset:
        return f"{asset['name']}<br>({ticker})"
    return ticker


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


def render_custom_metric_card(title: str, asset: str, raw_value: float, formatted_str: str) -> None:
    """Card de destaque: nome do ativo + selo colorido com o valor."""
    render_metric_card(
        title,
        escape(asset),
        value_size="1.1rem",
        badge=(f"{tone_icon(raw_value)} {formatted_str}", tone_of(raw_value)),
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
            config={"displayModeBar": False, "responsive": True},
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
def format_multiselect_option(ticker: str) -> str:
    """Embeleza o ticker exibido no multiselect usando os dados originais do ativo."""
    a = next((item for item in ASSETS if item["ticker"] == ticker), None)
    if not a:
        return ticker
    if a.get("group", a.get("class", "")) == "forex":
        return f"{a['ticker']} — {a.get('description', a.get('descricao', a.get('name')))}"
    return f"{a['ticker']} — {a.get('name')}"


with st.sidebar:
    # Injeta a compactação via CSS e JS padrão da sidebar
    inject_compact_sidebar_css()
    inject_compact_dropdown_script()

    st.header("⚙️ Parâmetros da Comparação")

    # ==========================================================
    # SELEÇÃO DE ATIVOS (key + on_change eliminam o atraso de uma
    # execução que exigia clicar duas vezes)
    # ==========================================================
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

    # O valor confirmado vem do estado sincronizado no callback,
    # já refletindo o clique mais recente sem atraso.
    selected_class = st.session_state[COMPARISON_CLASS_STATE_KEY]

    # Tickers já selecionados (persistidos automaticamente pela key
    # do próprio widget entre execuções).
    previously_selected_tickers = st.session_state.get(
        COMPARISON_SYMBOLS_WIDGET_KEY,
        [],
    )

    valid_options_tickers = []
    seen = set()

    # Estratégia de retenção: o ticker entra nas opções se for da
    # classe selecionada OU se já estiver selecionado (permite
    # comparação entre ativos de classes diferentes).
    for asset in ASSETS:
        asset_group = asset.get("group", asset.get("class", "Outros"))
        is_in_group = (asset_group == selected_class)
        is_selected = (asset["ticker"] in previously_selected_tickers)

        if (is_in_group or is_selected) and asset["ticker"] not in seen:
            valid_options_tickers.append(asset["ticker"])
            seen.add(asset["ticker"])

    st.multiselect(
        "Símbolo/Nome do Ativo:",
        options=valid_options_tickers,
        max_selections=5,
        format_func=format_multiselect_option,
        disabled=(selected_class is None),
        placeholder="Selecione um ativo",
        help="Selecione uma classe acima para habilitar." if selected_class is None else "Digite para buscar por nome ou código na classe selecionada.",
        key=COMPARISON_SYMBOLS_WIDGET_KEY,
        on_change=sync_comparison_symbols,
    )

    # Valor confirmado, já sincronizado pelo callback -- sem atraso.
    selected_tickers = st.session_state[COMPARISON_SYMBOLS_WIDGET_KEY]
    symbols_input = st.session_state[COMPARISON_SYMBOLS_STATE_KEY]
    # ==========================================================

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
    try:
        symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]
    except ValueError as error:
        st.sidebar.error(str(error))
        st.stop()

    if len(symbols) < 2:
        st.sidebar.error("Selecione pelo menos dois ativos para comparar.")
        st.stop()

    if start_date >= end_date:
        st.sidebar.error("A data inicial deve ser anterior à data final.")
        st.stop()

    asset_data = {}
    failed_symbols = []

    with st.spinner("Carregando e processando os ativos..."):
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

            df_prepared = prepare_dataframe(df_raw)
            df_aggregated = aggregate_by_frequency(
                df_prepared,
                frequency,
            )
            df_primary = select_primary_variable(
                df_aggregated,
                "Close",
            )
            df_returns = calculate_returns(df_primary, "Value")
            asset_data[symbol] = calculate_drawdown(
                df_returns,
                "Value",
            )

    if len(asset_data) < 2:
        st.session_state["comparison_loaded"] = False
        st.session_state["comparison_query"] = None
        st.error(
            "Não foi possível obter dados válidos para pelo menos dois ativos."
        )
        if failed_symbols:
            st.warning(
                "Símbolos sem dados válidos: "
                + ", ".join(failed_symbols)
            )
        st.stop()

    base_100_table = build_base_100_table(asset_data)
    price_table = build_price_table(asset_data)
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
    }
    st.session_state["comparison_asset_data"] = asset_data
    st.session_state["comparison_failed_symbols"] = failed_symbols
    st.session_state["comparison_base_100_table"] = base_100_table
    st.session_state["comparison_price_table"] = price_table
    st.session_state["comparison_returns_table"] = returns_table
    st.session_state["comparison_correlation_matrix"] = correlation_matrix
    st.session_state["comparison_summary"] = summary


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
base_100_table = st.session_state["comparison_base_100_table"]
correlation_matrix = st.session_state["comparison_correlation_matrix"]
summary = st.session_state["comparison_summary"]
start_date = query["start_date"]
end_date = query["end_date"]
frequency = query["frequency"]
risk_free_rate_pct = float(query["risk_free_rate_pct"])
annualization_factor = ANNUALIZATION_FACTORS.get(frequency, 252)

if failed_symbols:
    st.warning(
        "Os seguintes símbolos não retornaram dados válidos: "
        + ", ".join(failed_symbols)
    )


# =====================
# Cards visuais dos ativos comparados (logo/ícone + ticker + nome)
# =====================
selected_assets_for_cards = [
    a for a in ASSETS if a["ticker"] in asset_data.keys()
]
render_selected_asset_cards(selected_assets_for_cards)
st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)


with st.expander(
    f"✅ Análise gerada para {len(asset_data)} ativos. "
    "Clique para visualizar a metodologia e parâmetros.",
    expanded=False,
):
    st.markdown(
        "**Ativos analisados:** "
        + ", ".join(asset_data.keys())
    )
    st.markdown(
        f"**Período:** {start_date.strftime('%d/%m/%Y')} a "
        f"{end_date.strftime('%d/%m/%Y')} | **Frequência:** {frequency}"
    )
    st.markdown(
        f"**Índice de Sharpe:** taxa livre de risco de "
        f"**{risk_free_rate_pct:.2f}% ao ano** e fator de anualização "
        f"**{annualization_factor}**."
    )
    st.markdown(
        "**Tratamento de dados:** alinhamento completo por data, com "
        "correlações calculadas somente entre retornos válidos e coincidentes."
    )

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
# Destaques (4 Cards Analíticos)
# ==========================================================
st.header("📌 Destaques da Comparação")

if not summary_numeric.empty:
    best_row = summary_numeric.loc[summary_numeric["Retorno total"].idxmax()]
    worst_row = summary_numeric.loc[summary_numeric["Retorno total"].idxmin()]
    lowest_drawdown_row = summary_numeric.loc[summary_numeric["Drawdown máximo"].idxmax()]
    best_sharpe_row = summary_numeric.loc[summary_numeric["Sharpe"].idxmax()]

    highlight_cols = st.columns(4)
    with highlight_cols[0]:
        render_custom_metric_card(
            "Melhor retorno",
            get_asset_full_name(best_row["Ativo"]),
            best_row["Retorno total"],
            format_return_pct(best_row["Retorno total"])
        )
    with highlight_cols[1]:
        render_custom_metric_card(
            "Menor retorno",
            get_asset_full_name(worst_row["Ativo"]),
            worst_row["Retorno total"],
            format_return_pct(worst_row["Retorno total"])
        )
    with highlight_cols[2]:
        render_custom_metric_card(
            "Menor perda máxima",
            get_asset_full_name(lowest_drawdown_row["Ativo"]),
            lowest_drawdown_row["Drawdown máximo"],
            format_return_pct(lowest_drawdown_row["Drawdown máximo"])
        )
    with highlight_cols[3]:
        sharpe_val = best_sharpe_row["Sharpe"]
        sharpe_str = "N/A" if pd.isna(sharpe_val) else f"{sharpe_val:.2f}"
        render_custom_metric_card(
            "Melhor Risco-Retorno",
            get_asset_full_name(best_sharpe_row["Ativo"]),
            sharpe_val if not pd.isna(sharpe_val) else 0,
            f"Sharpe: {sharpe_str}"
        )

    st.markdown("<br>", unsafe_allow_html=True)


# ==========================================================
# Gráfico Base 100
# ==========================================================
st.markdown("### 📈 Evolução de Desempenho Histórico")
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
            config={"displayModeBar": False},
        )


# ==========================================================
# Resumo Comparativo
# ==========================================================
st.header("📊 Resumo Comparativo")
render_summary_table(summary_display)


# ==========================================================
# Correlação entre Retornos
# ==========================================================
st.header("🔗 Correlação entre Retornos")
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


# ==========================================================
# Métricas por Ativo
# ==========================================================
st.header("🧮 Métricas por Ativo")
st.caption(
    "A tabela consolida retorno, volatilidade, drawdown e Sharpe para "
    "facilitar a comparação entre os ativos."
)
render_asset_metrics_table(summary_numeric)


# ==========================================================
# Dados Normalizados
# ==========================================================
st.header("📋 Dados Normalizados")
render_normalized_data_table(base_100_table)


# ==========================================================
# Download e rodapé
# ==========================================================
csv_data = base_100_table.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Baixar comparação em CSV",
    data=csv_data,
    file_name="comparacao_ativos_base_100.csv",
    mime="text/csv",
)

st.markdown("---")
st.caption(
    "⚠️ Esta ferramenta possui finalidade educacional e de pesquisa. "
    "Dados históricos, indicadores de risco e resultados passados não "
    "garantem resultados futuros e não constituem recomendação de investimento."
)