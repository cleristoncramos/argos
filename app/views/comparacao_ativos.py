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

from app.ui.state import initialize_asset_state

try:
    from app.ui.assets_selector import render_multi_asset_selector
except ModuleNotFoundError:
    try:
        from app.ui.asset_selector import render_multi_asset_selector
    except ModuleNotFoundError:
        st.error("❌ O arquivo 'assets_selector.py' (ou 'asset_selector.py') não foi encontrado na pasta 'app/ui/'. Verifique se você salvou o arquivo corretamente.")
        st.stop()

from core.analyzer import calculate_returns
from core.assets import ASSETS, get_assets
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

COMPARISON_PERIOD_WIDGET_KEY = "comparison_period_widget"
COMPARISON_START_DATE_WIDGET_KEY = "comparison_start_date_widget"
COMPARISON_END_DATE_WIDGET_KEY = "comparison_end_date_widget"
COMPARISON_FREQUENCY_WIDGET_KEY = "comparison_frequency_widget"
COMPARISON_RISK_FREE_RATE_WIDGET_KEY = "comparison_risk_free_rate_pct_widget"


# ==========================================================
# Sincronização de widgets
# ==========================================================
def sync_comparison_symbols() -> None:
    selected_list = st.session_state.get(COMPARISON_SYMBOLS_WIDGET_KEY, [])
    st.session_state[COMPARISON_SYMBOLS_STATE_KEY] = ",".join(selected_list)

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


# ==========================================================
# Estado inicial
# ==========================================================
def initialize_comparison_state() -> None:
    today = datetime.now().date()
    asset_period = st.session_state.get("comparison_period", "5 anos")
    
    target_year_init = today.year - 5
    target_month_init = today.month + 1
    if target_month_init > 12:
        target_month_init = 1
        target_year_init += 1
        
    asset_start_date = st.session_state.get(
        "comparison_start_date",
        datetime(target_year_init, target_month_init, 1).date(),
    )
    asset_end_date = st.session_state.get(
        "comparison_end_date",
        today,
    )
    asset_frequency = st.session_state.get(
        "comparison_frequency",
        "Mensal",
    )

    defaults = {
        COMPARISON_PERIOD_STATE_KEY: asset_period,
        COMPARISON_START_DATE_STATE_KEY: asset_start_date,
        COMPARISON_END_DATE_STATE_KEY: asset_end_date,
        COMPARISON_FREQUENCY_STATE_KEY: asset_frequency,
        COMPARISON_RISK_FREE_RATE_STATE_KEY: 0.0,
        COMPARISON_SYMBOLS_STATE_KEY: "", 
        COMPARISON_PERIOD_WIDGET_KEY: asset_period,
        COMPARISON_START_DATE_WIDGET_KEY: asset_start_date,
        COMPARISON_END_DATE_WIDGET_KEY: asset_end_date,
        COMPARISON_FREQUENCY_WIDGET_KEY: asset_frequency,
        COMPARISON_RISK_FREE_RATE_WIDGET_KEY: 0.0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ==========================================================
# Utilitários e Formatação
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

def format_brazilian_number(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return str(value)
    return (
        f"{numeric_value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def format_summary_value(value, column: str) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    if column in {
        "Retorno total",
        "Retorno médio",
        "Volatilidade",
        "Drawdown máximo",
        "Percentual positivo",
    }:
        return format_return_pct(value)
    if column in {"Primeiro valor", "Último valor"}:
        return format_brazilian_number(value)
    if column == "Sharpe":
        return f"{float(value):.2f}"
    if column == "Observações":
        return f"{int(value)}"
    return str(value)


def format_normalized_value(value, column: str) -> str:
    if value is None or pd.isna(value):
        return "—"
    if column == "Date":
        date_value = pd.to_datetime(value, errors="coerce")
        if pd.isna(date_value):
            return "—"
        return date_value.strftime("%d/%m/%Y")
    return format_brazilian_number(value)


def format_correlation_value(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    try:
        return f"{float(value):.2f}".replace(".", ",")
    except (TypeError, ValueError):
        return str(value)


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
    icon = "▲" if raw_value > 0 else "▼" if raw_value < 0 else "−"
    color_bg = "#dcfce7" if raw_value > 0 else "#fee2e2" if raw_value < 0 else "#f1f5f9"
    color_fg = "#166534" if raw_value > 0 else "#991b1b" if raw_value < 0 else "#475569"

    html = f"""
    <div style="background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-direction: column; height: 100%;">
        <div style="color: #64748b; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
            {title}
        </div>
        <div style="color: #0f172a; font-size: 1.1rem; font-weight: 700; margin-bottom: 12px; line-height: 1.2;">
            {asset}
        </div>
        <div>
            <span style="font-size: 0.85rem; font-weight: 600; padding: 4px 8px; border-radius: 6px; display: inline-block; background-color: {color_bg}; color: {color_fg};">
                {icon} {formatted_str}
            </span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ==========================================================
# Tabelas HTML Premium
# ==========================================================
def build_table_styles(prefix: str) -> str:
    return (
        f"""
        <style>
        .{prefix}-wrapper {{
            width: 100%;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            background: #FFFFFF;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1);
        }}
        .{prefix}-table {{
            width: 100%;
            min-width: 800px;
            border-collapse: collapse;
            font-size: 0.9rem;
            color: #334155;
            font-family: 'Inter', Arial, sans-serif;
        }}
        .{prefix}-table th {{
            background-color: #F8FAFC;
            color: #1E293B;
            text-align: center;
            vertical-align: middle;
            font-weight: 700;
            padding: 14px 16px;
            border-bottom: 3px solid #97B7C4;
            border-right: 1px solid #E2E8F0;
            white-space: nowrap;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .{prefix}-table th:last-child {{ border-right: none; }}
        .{prefix}-table td {{
            vertical-align: middle;
            padding: 12px 16px;
            border-bottom: 1px solid #E2E8F0;
            border-right: 1px solid #E2E8F0;
        }}
        .{prefix}-table td:last-child {{ border-right: none; }}
        .{prefix}-table tr:last-child td {{ border-bottom: none; }}
        .{prefix}-row-even {{ background-color: #FFFFFF; }}
        .{prefix}-row-odd {{ background-color: #F1F5F9; }}
        .{prefix}-table tr:hover {{ background-color: #E2E8F0; transition: background-color 0.2s; }}
        </style>
        """
    )


def render_summary_table(dataframe: pd.DataFrame) -> None:
    columns = [
        "Ativo", "Observações", "Primeiro valor", "Último valor",
        "Retorno total", "Retorno médio", "Volatilidade",
        "Drawdown máximo", "Percentual positivo", "Sharpe",
    ]
    columns = [column for column in columns if column in dataframe.columns]
    
    display_df = dataframe[columns].copy()
    if "Ativo" in display_df.columns:
        display_df["Ativo"] = display_df["Ativo"].apply(get_asset_full_name)
    records = display_df.to_dict(orient="records")

    header = "".join(f"<th>{escape(str(column))}</th>" for column in columns)
    rows = []

    for position, record in enumerate(records):
        cells = []
        for column in columns:
            value = format_summary_value(record.get(column), column)
            alignment = "left" if column == "Ativo" else "right"
            font_family = "inherit" if column == "Ativo" else "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
            cells.append(
                f'<td style="text-align:{alignment}; white-space:nowrap; font-variant-numeric:tabular-nums; font-family:{font_family}">'
                f"{escape(str(value))}</td>"
            )
        row_class = "argos-summary-row-even" if position % 2 == 0 else "argos-summary-row-odd"
        rows.append(f'<tr class="{row_class}">{"".join(cells)}</tr>')

    html = (
        build_table_styles("argos-summary")
        + '<div class="argos-summary-wrapper" style="overflow-x: auto;">'
        + '<table class="argos-summary-table">'
        + f"<thead><tr>{header}</tr></thead>"
        + f'<tbody>{"".join(rows)}</tbody></table></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


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
    
    widths = {column: f"{80 / (len(columns)-1):.2f}%" for column in columns if column != "Ativo"}
    widths["Ativo"] = "20%" 
    records = display_df.to_dict(orient="records")

    header = "".join(
        f'<th style="width:{widths[column]};">{escape(str(column))}</th>'
        for column in columns
    )
    rows = []

    for position, record in enumerate(records):
        cells = []
        for column in columns:
            value = record.get(column)
            formatted = (
                "—" if column == "Ativo" and pd.isna(value)
                else str(value) if column == "Ativo"
                else format_correlation_value(value)
            )
            cells.append(
                f'<td style="width:{widths[column]}; text-align:center; white-space:nowrap; font-variant-numeric:tabular-nums; font-family:ui-monospace, SFMono-Regular, Menlo, monospace;">'
                f"{escape(formatted)}</td>"
            )
        row_class = "argos-correlation-row-even" if position % 2 == 0 else "argos-correlation-row-odd"
        rows.append(f'<tr class="{row_class}">{"".join(cells)}</tr>')

    html = (
        build_table_styles("argos-correlation")
        + '<div class="argos-correlation-wrapper" style="overflow-x: auto;">'
        + '<table class="argos-correlation-table">'
        + f"<thead><tr>{header}</tr></thead>"
        + f'<tbody>{"".join(rows)}</tbody></table></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_asset_metrics_table(dataframe: pd.DataFrame) -> None:
    columns = [
        "Ativo", "Retorno total", "Retorno médio", "Volatilidade",
        "Drawdown máximo", "Percentual positivo", "Sharpe",
    ]
    columns = [column for column in columns if column in dataframe.columns]
    
    display_df = dataframe[columns].sort_values(
        by="Retorno total",
        ascending=False,
        na_position="last",
    )
    if "Ativo" in display_df.columns:
        display_df["Ativo"] = display_df["Ativo"].apply(get_asset_full_name)
        
    records = display_df.to_dict(orient="records")

    labels = {"Percentual positivo": "Períodos positivos"}
    header = "".join(
        f"<th>{escape(labels.get(column, column))}</th>"
        for column in columns
    )
    rows = []

    for position, record in enumerate(records):
        cells = []
        for column in columns:
            value = record.get(column)
            formatted = (
                "—" if column == "Ativo" and pd.isna(value)
                else str(value) if column == "Ativo"
                else format_summary_value(value, column)
            )
            alignment = "left" if column == "Ativo" else "right"
            font_family = "inherit" if column == "Ativo" else "ui-monospace, SFMono-Regular, Menlo, monospace"
            cells.append(
                f'<td style="text-align:{alignment}; white-space:nowrap; font-variant-numeric:tabular-nums; font-family:{font_family}">'
                f"{escape(formatted)}</td>"
            )
        row_class = "argos-metrics-row-even" if position % 2 == 0 else "argos-metrics-row-odd"
        rows.append(f'<tr class="{row_class}">{"".join(cells)}</tr>')

    html = (
        build_table_styles("argos-metrics")
        + '<div class="argos-metrics-wrapper" style="overflow-x: auto;">'
        + '<table class="argos-metrics-table">'
        + f"<thead><tr>{header}</tr></thead>"
        + f'<tbody>{"".join(rows)}</tbody></table></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_normalized_data_table(dataframe: pd.DataFrame) -> None:
    if dataframe is None or dataframe.empty:
        st.info("Não há dados normalizados disponíveis para exibição.")
        return

    columns = dataframe.columns.tolist()
    if "Date" in columns:
        columns = ["Date"] + [column for column in columns if column != "Date"]
        
    display_df = dataframe[columns].copy()
    
    rename_dict = {col: get_asset_full_name(col) for col in columns if col != "Date"}
    display_df = display_df.rename(columns=rename_dict)
    
    columns = display_df.columns.tolist()
    records = display_df.to_dict(orient="records")
    
    widths = {column: f"{80 / (len(columns)-1):.2f}%" for column in columns if column != "Date"}
    widths["Date"] = "20%" 

    header = "".join(
        f'<th style="width:{widths[column]};">{escape(str(column))}</th>'
        for column in columns
    )
    rows = []

    for position, record in enumerate(records):
        cells = []
        for column in columns:
            value = format_normalized_value(record.get(column), column)
            cells.append(
                f'<td style="width:{widths[column]}; text-align:center; white-space:nowrap; font-variant-numeric:tabular-nums; font-family:ui-monospace, SFMono-Regular, Menlo, monospace;">'
                f"{escape(str(value))}</td>"
            )
        row_class = "argos-normalized-row-even" if position % 2 == 0 else "argos-normalized-row-odd"
        rows.append(f'<tr class="{row_class}">{"".join(cells)}</tr>')

    html = (
        build_table_styles("argos-normalized")
        + '<div class="argos-normalized-wrapper" style="max-height: 450px; overflow-y: auto; overflow-x: auto;">'
        + '<table class="argos-normalized-table">'
        + f"<thead><tr>{header}</tr></thead>"
        + f'<tbody>{"".join(rows)}</tbody></table></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


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
with st.sidebar:
    st.header("⚙️ Parâmetros da Comparação")

    default_str = st.session_state.get(COMPARISON_SYMBOLS_STATE_KEY, "")
    default_list = [s.strip() for s in default_str.split(",") if s.strip()]

    selected_tickers = render_multi_asset_selector(
        key_prefix="comparison",
        default_tickers=default_list,
        max_selections=5
    )

    st.session_state[COMPARISON_SYMBOLS_STATE_KEY] = ",".join(selected_tickers)
    symbols_input = st.session_state[COMPARISON_SYMBOLS_STATE_KEY]

    st.divider()

    period_options = ["1 ano", "3 anos", "5 anos", "10 anos", "Personalizado"]
    
    st.selectbox(
        "Período",
        options=period_options,
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
        end_date = today
        years_to_subtract = int(selected_period.split()[0])
        
        target_year = today.year - years_to_subtract
        target_month = today.month + 1
        
        if target_month > 12:
            target_month = 1
            target_year += 1
            
        start_date = datetime(target_year, target_month, 1).date()
        
        st.session_state[COMPARISON_START_DATE_STATE_KEY] = start_date
        st.session_state[COMPARISON_END_DATE_STATE_KEY] = end_date

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
    base_100_melted["Tooltip_Value"] = base_100_melted["Índice base 100"].apply(format_brazilian_number)

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