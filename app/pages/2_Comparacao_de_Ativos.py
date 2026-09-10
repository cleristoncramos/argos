import os
import sys
from datetime import datetime
from html import escape

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../..",
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT,
    )

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.ui.state import initialize_asset_state
from core.analyzer import calculate_returns
from core.comparison import (
    build_base_100_table,
    build_price_table,
    calculate_correlation_matrix,
    calculate_returns_table,
    create_comparison_summary,
    format_return_pct,
    parse_symbols,
)
from core.config import ANNUALIZATION_FACTORS, config
from core.data_loader import download_active_data
from core.data_processor import (
    aggregate_by_frequency,
    prepare_dataframe,
    select_primary_variable,
)
from core.risk_metrics import (
    build_risk_summary,
    calculate_drawdown,
)


# ==========================================================
# Chaves de estado
# ==========================================================
COMPARISON_SYMBOLS_STATE_KEY = "comparison_symbols_input"
COMPARISON_START_DATE_STATE_KEY = "comparison_start_date"
COMPARISON_END_DATE_STATE_KEY = "comparison_end_date"
COMPARISON_FREQUENCY_STATE_KEY = "comparison_frequency"
COMPARISON_RISK_FREE_RATE_STATE_KEY = (
    "comparison_risk_free_rate_pct"
)

COMPARISON_SYMBOLS_WIDGET_KEY = "comparison_symbols_input_widget"
COMPARISON_START_DATE_WIDGET_KEY = "comparison_start_date_widget"
COMPARISON_END_DATE_WIDGET_KEY = "comparison_end_date_widget"
COMPARISON_FREQUENCY_WIDGET_KEY = "comparison_frequency_widget"
COMPARISON_RISK_FREE_RATE_WIDGET_KEY = (
    "comparison_risk_free_rate_pct_widget"
)


# ==========================================================
# Sincronização de widgets
# ==========================================================
def sync_comparison_symbols() -> None:
    """Sincroniza a lista de símbolos com o estado persistente."""
    st.session_state[COMPARISON_SYMBOLS_STATE_KEY] = (
        st.session_state[COMPARISON_SYMBOLS_WIDGET_KEY]
    )


def sync_comparison_start_date() -> None:
    """Sincroniza a data inicial com o estado persistente."""
    st.session_state[COMPARISON_START_DATE_STATE_KEY] = (
        st.session_state[COMPARISON_START_DATE_WIDGET_KEY]
    )


def sync_comparison_end_date() -> None:
    """Sincroniza a data final com o estado persistente."""
    st.session_state[COMPARISON_END_DATE_STATE_KEY] = (
        st.session_state[COMPARISON_END_DATE_WIDGET_KEY]
    )


def sync_comparison_frequency() -> None:
    """Sincroniza a frequência com o estado persistente."""
    st.session_state[COMPARISON_FREQUENCY_STATE_KEY] = (
        st.session_state[COMPARISON_FREQUENCY_WIDGET_KEY]
    )


def sync_comparison_risk_free_rate() -> None:
    """Sincroniza a taxa livre de risco com o estado persistente."""
    st.session_state[COMPARISON_RISK_FREE_RATE_STATE_KEY] = float(
        st.session_state[COMPARISON_RISK_FREE_RATE_WIDGET_KEY]
    )


# ==========================================================
# Inicialização de estado
# ==========================================================
def initialize_comparison_state() -> None:
    """
    Inicializa estado persistente e temporário da comparação.

    Quando disponíveis, período e frequência da análise individual
    são utilizados como valores iniciais.
    """
    asset_start_date = st.session_state.get(
        "asset_start_date",
        datetime(2020, 1, 1),
    )

    asset_end_date = st.session_state.get(
        "asset_end_date",
        datetime(2025, 12, 31),
    )

    asset_frequency = st.session_state.get(
        "asset_frequency",
        "Mensal",
    )

    defaults = {
        COMPARISON_SYMBOLS_STATE_KEY: "BTC-USD,AAPL,USDBRL=X,SPY",
        COMPARISON_START_DATE_STATE_KEY: asset_start_date,
        COMPARISON_END_DATE_STATE_KEY: asset_end_date,
        COMPARISON_FREQUENCY_STATE_KEY: asset_frequency,
        COMPARISON_RISK_FREE_RATE_STATE_KEY: 0.0,
        COMPARISON_SYMBOLS_WIDGET_KEY: "BTC-USD,AAPL,USDBRL=X,SPY",
        COMPARISON_START_DATE_WIDGET_KEY: asset_start_date,
        COMPARISON_END_DATE_WIDGET_KEY: asset_end_date,
        COMPARISON_FREQUENCY_WIDGET_KEY: asset_frequency,
        COMPARISON_RISK_FREE_RATE_WIDGET_KEY: 0.0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ==========================================================
# Formatação
# ==========================================================
def format_brazilian_number(value) -> str:
    """Formata um número com duas casas decimais no padrão brasileiro."""
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


def format_summary_value(
    value,
    column: str,
) -> str:
    """Formata valores usados no resumo e na tabela de métricas."""
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

    if column in {
        "Primeiro valor",
        "Último valor",
    }:
        return format_brazilian_number(value)

    if column == "Sharpe":
        return f"{float(value):.2f}"

    if column == "Observações":
        return f"{int(value)}"

    return str(value)


def format_normalized_value(
    value,
    column: str,
) -> str:
    """
    Formata valores dos Dados Normalizados.

    Date é exibida como dd/mm/aaaa e os ativos com duas casas decimais.
    """
    if value is None or pd.isna(value):
        return "—"

    if column == "Date":
        date_value = pd.to_datetime(
            value,
            errors="coerce",
        )

        if pd.isna(date_value):
            return "—"

        return date_value.strftime("%d/%m/%Y")

    return format_brazilian_number(value)


def format_correlation_value(value) -> str:
    """Formata coeficientes de correlação com duas casas decimais."""
    if value is None or pd.isna(value):
        return "—"

    try:
        return f"{float(value):.2f}".replace(".", ",")
    except (TypeError, ValueError):
        return str(value)


# ==========================================================
# Estilos reutilizáveis para tabelas
# ==========================================================
def build_table_styles(
    prefix: str,
) -> str:
    """
    Gera os estilos CSS comuns das tabelas HTML da página.
    """
    return (
        "<style>"
        f".{prefix}-wrapper {{"
        "width:100%;"
        "overflow-x:auto;"
        "border:1px solid #D9E2EC;"
        "border-radius:10px;"
        "background:#FFFFFF;"
        "}"
        f".{prefix}-table {{"
        "width:100%;"
        "border-collapse:separate;"
        "border-spacing:0;"
        "table-layout:fixed;"
        "font-size:14px;"
        "color:#26364A;"
        "}"
        f".{prefix}-table th {{"
        "background:#E8EEF7;"
        "color:#26364A;"
        "text-align:center;"
        "vertical-align:middle;"
        "font-weight:700;"
        "white-space:normal;"
        "border-right:1px solid #D9E2EC;"
        "border-bottom:2px solid #B7C7D9;"
        "padding:10px 8px;"
        "}"
        f".{prefix}-table th:last-child {{"
        "border-right:none;"
        "}"
        f".{prefix}-table td {{"
        "vertical-align:middle;"
        "border-right:1px solid #E7EDF3;"
        "border-bottom:1px solid #E7EDF3;"
        "padding:10px 8px;"
        "}"
        f".{prefix}-table td:last-child {{"
        "border-right:none;"
        "}"
        f".{prefix}-table tbody tr:last-child td {{"
        "border-bottom:none;"
        "}"
        f".{prefix}-row-even {{"
        "background:#FFFFFF;"
        "}"
        f".{prefix}-row-odd {{"
        "background:#F8FAFC;"
        "}"
        f".{prefix}-table tbody tr:hover {{"
        "background:#EEF5FF;"
        "}"
        "</style>"
    )


# ==========================================================
# Tabela: Resumo Comparativo
# ==========================================================
def render_summary_table(
    dataframe: pd.DataFrame,
) -> None:
    """
    Renderiza o resumo comparativo sem índice Pandas.

    A tabela utiliza apenas colunas explicitamente definidas e uma
    linha por ativo, sem incluir o índice 0, 1, 2, 3.
    """
    summary_columns = [
        "Ativo",
        "Observações",
        "Primeiro valor",
        "Último valor",
        "Retorno total",
        "Retorno médio",
        "Volatilidade",
        "Drawdown máximo",
        "Percentual positivo",
        "Sharpe",
    ]

    available_columns = [
        column
        for column in summary_columns
        if column in dataframe.columns
    ]

    display_df = dataframe[
        available_columns
    ].copy()

    records = display_df.to_dict(
        orient="records",
    )

    header_html = "".join(
        "<th>" + escape(str(column)) + "</th>"
        for column in available_columns
    )

    rows_html = []

    for position, record in enumerate(records):
        cells_html = []

        for column in available_columns:
            formatted_value = format_summary_value(
                record.get(column),
                column,
            )

            if column == "Ativo":
                cell_style = (
                    "text-align:left;"
                    "white-space:nowrap;"
                    "font-family:inherit;"
                )
            else:
                cell_style = (
                    "text-align:right;"
                    "white-space:nowrap;"
                    "font-variant-numeric:tabular-nums;"
                    "font-family:ui-monospace,SFMono-Regular,Menlo,"
                    "Monaco,Consolas,'Liberation Mono',monospace;"
                )

            cells_html.append(
                '<td style="'
                + cell_style
                + '">'
                + escape(str(formatted_value))
                + "</td>"
            )

        row_class = (
            "argos-summary-row-even"
            if position % 2 == 0
            else "argos-summary-row-odd"
        )

        rows_html.append(
            '<tr class="'
            + row_class
            + '">'
            + "".join(cells_html)
            + "</tr>"
        )

    table_html = (
        build_table_styles("argos-summary")
        + '<div class="argos-summary-wrapper">'
        + '<table class="argos-summary-table" '
        + 'style="min-width:1120px;">'
        + "<thead><tr>"
        + header_html
        + "</tr></thead>"
        + "<tbody>"
        + "".join(rows_html)
        + "</tbody>"
        + "</table>"
        + "</div>"
    )

    st.components.v1.html(
        table_html,
        height=260,
        scrolling=True,
    )


# ==========================================================
# Tabela: Correlação entre Retornos
# ==========================================================
def render_correlation_table(
    correlation_matrix: pd.DataFrame,
) -> None:
    """
    Renderiza a matriz de correlação com o padrão visual da página.

    O índice original é transformado explicitamente na coluna Ativo.
    Com quatro ativos, a coluna Ativo e as quatro colunas de ativos
    ocupam 20% cada e ficam centralizadas.
    """
    if correlation_matrix is None or correlation_matrix.empty:
        st.info(
            "Não há dados coincidentes suficientes para exibir a tabela "
            "de correlação."
        )
        return

    display_df = correlation_matrix.copy()

    display_df.index.name = "Ativo"

    display_df = display_df.reset_index()

    columns = display_df.columns.tolist()

    asset_columns = [
        column
        for column in columns
        if column != "Ativo"
    ]

    label_width = "20%"

    asset_width = (
        f"{80 / len(asset_columns):.2f}%"
        if asset_columns
        else "100%"
    )

    records = display_df.to_dict(
        orient="records",
    )

    header_html = "".join(
        (
            '<th style="width:'
            + (
                label_width
                if column == "Ativo"
                else asset_width
            )
            + ';">'
            + escape(str(column))
            + "</th>"
        )
        for column in columns
    )

    rows_html = []

    for position, record in enumerate(records):
        cells_html = []

        for column in columns:
            value = record.get(column)

            if column == "Ativo":
                formatted_value = (
                    "—"
                    if pd.isna(value)
                    else str(value)
                )
                cell_width = label_width
            else:
                formatted_value = format_correlation_value(
                    value
                )
                cell_width = asset_width

            cell_style = (
                "width:"
                + cell_width
                + ";"
                + "text-align:center;"
                + "white-space:nowrap;"
                + "font-variant-numeric:tabular-nums;"
                + "font-family:ui-monospace,SFMono-Regular,Menlo,"
                + "Monaco,Consolas,'Liberation Mono',monospace;"
            )

            cells_html.append(
                '<td style="'
                + cell_style
                + '">'
                + escape(str(formatted_value))
                + "</td>"
            )

        row_class = (
            "argos-correlation-row-even"
            if position % 2 == 0
            else "argos-correlation-row-odd"
        )

        rows_html.append(
            '<tr class="'
            + row_class
            + '">'
            + "".join(cells_html)
            + "</tr>"
        )

    table_html = (
        build_table_styles("argos-correlation")
        + '<div class="argos-correlation-wrapper">'
        + '<table class="argos-correlation-table" '
        + 'style="min-width:720px;">'
        + "<thead><tr>"
        + header_html
        + "</tr></thead>"
        + "<tbody>"
        + "".join(rows_html)
        + "</tbody>"
        + "</table>"
        + "</div>"
    )

    st.components.v1.html(
        table_html,
        height=280,
        scrolling=True,
    )


# ==========================================================
# Tabela: Métricas por Ativo
# ==========================================================
def render_asset_metrics_table(
    dataframe: pd.DataFrame,
) -> None:
    """
    Renderiza uma tabela consolidada de métricas por ativo.

    Substitui os cartões individuais e permite comparar todos os
    ativos em uma única estrutura visual organizada.
    """
    metric_columns = [
        "Ativo",
        "Retorno total",
        "Retorno médio",
        "Volatilidade",
        "Drawdown máximo",
        "Percentual positivo",
        "Sharpe",
    ]

    available_columns = [
        column
        for column in metric_columns
        if column in dataframe.columns
    ]

    display_df = dataframe[
        available_columns
    ].copy()

    if "Retorno total" in display_df.columns:
        display_df = display_df.sort_values(
            by="Retorno total",
            ascending=False,
            na_position="last",
        )

    header_labels = {
        "Ativo": "Ativo",
        "Retorno total": "Retorno total",
        "Retorno médio": "Retorno médio",
        "Volatilidade": "Volatilidade",
        "Drawdown máximo": "Drawdown máximo",
        "Percentual positivo": "Períodos positivos",
        "Sharpe": "Sharpe",
    }

    records = display_df.to_dict(
        orient="records",
    )

    header_html = "".join(
        (
            "<th>"
            + escape(
                header_labels.get(
                    column,
                    column,
                )
            )
            + "</th>"
        )
        for column in available_columns
    )

    rows_html = []

    for position, record in enumerate(records):
        cells_html = []

        for column in available_columns:
            value = record.get(column)

            if column == "Ativo":
                formatted_value = (
                    "—"
                    if value is None or pd.isna(value)
                    else str(value)
                )

                cell_style = (
                    "text-align:left;"
                    "white-space:nowrap;"
                    "font-family:inherit;"
                )
            else:
                formatted_value = format_summary_value(
                    value,
                    column,
                )

                cell_style = (
                    "text-align:right;"
                    "white-space:nowrap;"
                    "font-variant-numeric:tabular-nums;"
                    "font-family:ui-monospace,SFMono-Regular,Menlo,"
                    "Monaco,Consolas,'Liberation Mono',monospace;"
                )

            cells_html.append(
                '<td style="'
                + cell_style
                + '">'
                + escape(str(formatted_value))
                + "</td>"
            )

        row_class = (
            "argos-metrics-row-even"
            if position % 2 == 0
            else "argos-metrics-row-odd"
        )

        rows_html.append(
            '<tr class="'
            + row_class
            + '">'
            + "".join(cells_html)
            + "</tr>"
        )

    table_html = (
        build_table_styles("argos-metrics")
        + '<div class="argos-metrics-wrapper">'
        + '<table class="argos-metrics-table" '
        + 'style="min-width:900px;">'
        + "<thead><tr>"
        + header_html
        + "</tr></thead>"
        + "<tbody>"
        + "".join(rows_html)
        + "</tbody>"
        + "</table>"
        + "</div>"
    )

    st.components.v1.html(
        table_html,
        height=260,
        scrolling=True,
    )


# ==========================================================
# Tabela: Dados Normalizados
# ==========================================================
def render_normalized_data_table(
    dataframe: pd.DataFrame,
) -> None:
    """
    Renderiza Dados Normalizados sem índice Pandas.

    Com quatro ativos:
    - Date ocupa 20%.
    - Cada ativo ocupa 20%.
    - Todos os valores ficam centralizados.
    """
    if dataframe is None or dataframe.empty:
        st.info(
            "Não há dados normalizados disponíveis para exibição."
        )
        return

    columns = dataframe.columns.tolist()

    if "Date" in columns:
        columns = ["Date"] + [
            column
            for column in columns
            if column != "Date"
        ]

    display_df = dataframe[
        columns
    ].copy()

    asset_columns = [
        column
        for column in columns
        if column != "Date"
    ]

    date_width = "20%"

    asset_width = (
        f"{80 / len(asset_columns):.2f}%"
        if asset_columns
        else "100%"
    )

    records = display_df.to_dict(
        orient="records",
    )

    header_html = "".join(
        (
            '<th style="width:'
            + (
                date_width
                if column == "Date"
                else asset_width
            )
            + ';">'
            + escape(str(column))
            + "</th>"
        )
        for column in columns
    )

    rows_html = []

    for position, record in enumerate(records):
        cells_html = []

        for column in columns:
            formatted_value = format_normalized_value(
                record.get(column),
                column,
            )

            cell_width = (
                date_width
                if column == "Date"
                else asset_width
            )

            cell_style = (
                "width:"
                + cell_width
                + ";"
                + "text-align:center;"
                + "white-space:nowrap;"
                + "font-variant-numeric:tabular-nums;"
                + "font-family:ui-monospace,SFMono-Regular,Menlo,"
                + "Monaco,Consolas,'Liberation Mono',monospace;"
            )

            cells_html.append(
                '<td style="'
                + cell_style
                + '">'
                + escape(str(formatted_value))
                + "</td>"
            )

        row_class = (
            "argos-normalized-row-even"
            if position % 2 == 0
            else "argos-normalized-row-odd"
        )

        rows_html.append(
            '<tr class="'
            + row_class
            + '">'
            + "".join(cells_html)
            + "</tr>"
        )

    table_html = (
        build_table_styles("argos-normalized")
        + '<div class="argos-normalized-wrapper">'
        + '<table class="argos-normalized-table" '
        + 'style="min-width:760px;">'
        + "<thead><tr>"
        + header_html
        + "</tr></thead>"
        + "<tbody>"
        + "".join(rows_html)
        + "</tbody>"
        + "</table>"
        + "</div>"
    )

    st.components.v1.html(
        table_html,
        height=360,
        scrolling=True,
    )


# ==========================================================
# Configuração da página
# ==========================================================
st.set_page_config(
    page_title="Comparação de Ativos | Argos DataLab",
    page_icon="⚖️",
    layout="wide",
)

initialize_asset_state()
initialize_comparison_state()

st.title("⚖️ Comparação de Ativos")

st.markdown(
    """
Compare o comportamento histórico de diferentes ativos por meio de
retorno acumulado, normalização base 100, volatilidade, drawdown,
índice de Sharpe e correlação de retornos.
"""
)

st.info(
    "Esta comparação possui finalidade histórica, educacional e exploratória. "
    "Ela não constitui recomendação de investimento."
)


# ==========================================================
# Parâmetros da comparação
# ==========================================================
with st.sidebar:
    st.header("⚙️ Parâmetros da Comparação")

    st.text_input(
        "Símbolos dos ativos",
        key=COMPARISON_SYMBOLS_WIDGET_KEY,
        on_change=sync_comparison_symbols,
        help=(
            "Informe de 2 a 5 símbolos separados por vírgula. "
            "Exemplo: BTC-USD,AAPL,USDBRL=X,SPY"
        ),
    )

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
    )


symbols_input = st.session_state[
    COMPARISON_SYMBOLS_STATE_KEY
]

start_date = st.session_state[
    COMPARISON_START_DATE_STATE_KEY
]

end_date = st.session_state[
    COMPARISON_END_DATE_STATE_KEY
]

frequency = st.session_state[
    COMPARISON_FREQUENCY_STATE_KEY
]

risk_free_rate_pct = float(
    st.session_state[
        COMPARISON_RISK_FREE_RATE_STATE_KEY
    ]
)

annual_risk_free_rate = risk_free_rate_pct / 100


# ==========================================================
# Processamento da comparação
# ==========================================================
if load_comparison:
    if start_date >= end_date:
        st.sidebar.error(
            "A data inicial deve ser anterior à data final."
        )
        st.stop()

    try:
        symbols = parse_symbols(symbols_input)
    except ValueError as error:
        st.sidebar.error(str(error))
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

            df_returns = calculate_returns(
                df_primary,
                "Value",
            )

            df_risk = calculate_drawdown(
                df_returns,
                "Value",
            )

            asset_data[symbol] = df_risk

    if len(asset_data) < 2:
        st.session_state["comparison_loaded"] = False
        st.session_state["comparison_query"] = None

        st.session_state.pop(
            "comparison_asset_data",
            None,
        )

        st.session_state.pop(
            "comparison_failed_symbols",
            None,
        )

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

    returns_table = calculate_returns_table(
        price_table
    )

    correlation_matrix = calculate_correlation_matrix(
        returns_table
    )

    summary = create_comparison_summary(
        asset_data
    )

    annualization_factor = ANNUALIZATION_FACTORS.get(
        frequency,
        252,
    )

    risk_rows = []

    for symbol, df in asset_data.items():
        metrics = build_risk_summary(
            df=df,
            value_col="Value",
            annualization_factor=float(
                annualization_factor
            ),
            annual_risk_free_rate=annual_risk_free_rate,
        )

        risk_rows.append(
            {
                "Ativo": symbol,
                "Volatilidade": metrics.get(
                    "Volatilidade"
                ),
                "Drawdown máximo": metrics.get(
                    "Drawdown máximo"
                ),
                "Percentual positivo": metrics.get(
                    "Percentual positivo"
                ),
                "Sharpe": metrics.get("Sharpe"),
            }
        )

    risk_table = pd.DataFrame(risk_rows)

    summary = summary.merge(
        risk_table,
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

    st.session_state["comparison_failed_symbols"] = (
        failed_symbols
    )

    st.session_state["comparison_base_100_table"] = (
        base_100_table
    )

    st.session_state["comparison_price_table"] = price_table

    st.session_state["comparison_returns_table"] = (
        returns_table
    )

    st.session_state["comparison_correlation_matrix"] = (
        correlation_matrix
    )

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
        "Informe os símbolos, selecione o período e clique em "
        "**Comparar ativos**."
    )
    st.stop()


asset_data = st.session_state["comparison_asset_data"]

failed_symbols = st.session_state[
    "comparison_failed_symbols"
]

base_100_table = st.session_state[
    "comparison_base_100_table"
]

correlation_matrix = st.session_state[
    "comparison_correlation_matrix"
]

summary = st.session_state["comparison_summary"]

start_date = query["start_date"]

end_date = query["end_date"]

frequency = query["frequency"]

risk_free_rate_pct = float(
    query["risk_free_rate_pct"]
)

annualization_factor = ANNUALIZATION_FACTORS.get(
    frequency,
    252,
)


# ==========================================================
# Mensagens da consulta confirmada
# ==========================================================
if failed_symbols:
    st.warning(
        "Os seguintes símbolos não retornaram dados válidos: "
        + ", ".join(failed_symbols)
    )

st.success(
    f"Comparação gerada para {len(asset_data)} ativos: "
    + ", ".join(asset_data.keys())
)

st.info(
    "A união das séries usa alinhamento completo por data e preserva "
    "dias sem negociação. As correlações consideram apenas pares de "
    "retornos válidos e coincidentes."
)


# ==========================================================
# Dados numéricos e ordenação
# ==========================================================
summary_numeric = summary.copy()

summary_display = summary_numeric.sort_values(
    by="Retorno total",
    ascending=False,
    na_position="last",
).copy()


# ==========================================================
# Cores dos ativos
# ==========================================================
color_map = {
    "BTC-USD": "#F59E0B",
    "AAPL": "#3B82F6",
    "USDBRL=X": "#10B981",
    "SPY": "#8B5CF6",
}

for symbol in summary_numeric["Ativo"].tolist():
    if symbol not in color_map:
        color_map[symbol] = "#64748B"


# ==========================================================
# Metodologia do Sharpe
# ==========================================================
st.caption(
    f"Índice de Sharpe anualizado calculado com taxa livre de risco de "
    f"{risk_free_rate_pct:.2f}% ao ano e fator de anualização "
    f"{annualization_factor} para frequência {frequency}."
)


# ==========================================================
# Destaques
# ==========================================================
st.header("📌 Destaques da Comparação")

if not summary_numeric.empty:
    best_row = summary_numeric.loc[
        summary_numeric["Retorno total"].idxmax()
    ]

    worst_row = summary_numeric.loc[
        summary_numeric["Retorno total"].idxmin()
    ]

    lowest_drawdown_row = summary_numeric.loc[
        summary_numeric["Drawdown máximo"].idxmax()
    ]

    highlight_cols = st.columns(3)

    with highlight_cols[0]:
        st.metric(
            "Melhor retorno",
            best_row["Ativo"],
            format_return_pct(
                best_row["Retorno total"]
            ),
        )

    with highlight_cols[1]:
        st.metric(
            "Menor retorno",
            worst_row["Ativo"],
            format_return_pct(
                worst_row["Retorno total"]
            ),
        )

    with highlight_cols[2]:
        st.metric(
            "Menor perda máxima",
            lowest_drawdown_row["Ativo"],
            format_return_pct(
                lowest_drawdown_row["Drawdown máximo"]
            ),
        )


# ==========================================================
# Gráfico Base 100
# ==========================================================
st.header("📈 Evolução Normalizada — Base 100")

if not base_100_table.empty:
    base_100_melted = base_100_table.melt(
        id_vars="Date",
        var_name="Ativo",
        value_name="Índice base 100",
    )

    fig_base_100 = px.line(
        base_100_melted,
        x="Date",
        y="Índice base 100",
        color="Ativo",
        color_discrete_map=color_map,
        title="Comparação de Desempenho Relativo",
        labels={
            "Date": "Data",
            "Índice base 100": "Índice base 100",
            "Ativo": "Ativo",
        },
        template="plotly_white",
        markers=True,
    )

    fig_base_100.update_layout(
        hovermode="x unified",
        legend_title_text="Ativo",
        paper_bgcolor="#F8FAFC",
    )

    fig_base_100.update_traces(
        connectgaps=False
    )

    st.plotly_chart(
        fig_base_100,
        width="stretch",
    )

st.caption(
    "Cada ativo inicia em 100 no seu primeiro período válido. "
    "Por exemplo, valor 120 representa valorização acumulada de 20%."
)


# ==========================================================
# Resumo Comparativo
# ==========================================================
st.header("📊 Resumo Comparativo")

render_summary_table(
    summary_display
)


# ==========================================================
# Correlação entre Retornos
# ==========================================================
st.header("🔗 Correlação entre Retornos")

if correlation_matrix.empty:
    st.info(
        "Não há dados coincidentes suficientes para calcular a correlação."
    )
else:
    fig_correlation = go.Figure(
        data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            zmin=-1,
            zmax=1,
            colorscale="RdBu_r",
            colorbar=dict(
                title="Correlação"
            ),
            text=np.round(
                correlation_matrix.values,
                2,
            ),
            texttemplate="%{text}",
            hovertemplate=(
                "Ativo X: %{x}<br>"
                "Ativo Y: %{y}<br>"
                "Correlação: %{z:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig_correlation.update_layout(
        title="Correlação entre Retornos dos Ativos",
        xaxis_title="Ativo",
        yaxis_title="Ativo",
        template="plotly_white",
        paper_bgcolor="#F8FAFC",
    )

    st.plotly_chart(
        fig_correlation,
        width="stretch",
    )

    render_correlation_table(
        correlation_matrix
    )

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
    "facilitar a comparação entre os ativos. A análise considera risco "
    "e perda máxima intermediária, não apenas a valorização final."
)

render_asset_metrics_table(
    summary_numeric
)


# ==========================================================
# Dados Normalizados
# ==========================================================
st.header("📋 Dados Normalizados")

render_normalized_data_table(
    base_100_table
)


# ==========================================================
# Download
# ==========================================================
csv_data = base_100_table.to_csv(
    index=False,
).encode("utf-8")

st.download_button(
    label="⬇️ Baixar comparação em CSV",
    data=csv_data,
    file_name="comparacao_ativos_base_100.csv",
    mime="text/csv",
)


# ==========================================================
# Rodapé
# ==========================================================
st.markdown("---")

st.caption(
    "⚠️ Esta ferramenta possui finalidade educacional e de pesquisa. "
    "Dados históricos, indicadores e métricas de risco não garantem "
    "resultados futuros e não constituem recomendação de investimento."
)