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
    """Gera os estilos CSS comuns das tabelas HTML da página."""
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
# Heatmap: Correlação entre Retornos
# ==========================================================
def render_correlation_heatmap(
    correlation_matrix: pd.DataFrame,
) -> None:
    """
    Renderiza o heatmap de correlação em formato quadrado.

    O gráfico exibe somente o triângulo inferior da matriz e oculta
    a diagonal principal para eliminar a duplicidade visual.
    """
    if correlation_matrix is None or correlation_matrix.empty:
        st.info(
            "Não há dados coincidentes suficientes para calcular a correlação."
        )
        return

    correlation_plot = correlation_matrix.astype(float).copy()

    asset_order = correlation_plot.columns.tolist()

    correlation_plot = correlation_plot.reindex(
        index=asset_order,
        columns=asset_order,
    )

    values = correlation_plot.to_numpy(dtype=float)

    triangular_values = values.copy()

    triangular_values[
        np.triu_indices_from(
            triangular_values,
            k=0,
        )
    ] = np.nan

    text_values = np.empty(
        triangular_values.shape,
        dtype=object,
    )

    customdata = np.empty(
        triangular_values.shape,
        dtype=object,
    )

    for row_index in range(
        triangular_values.shape[0]
    ):
        for column_index in range(
            triangular_values.shape[1]
        ):
            value = triangular_values[
                row_index,
                column_index,
            ]

            if np.isnan(value):
                text_values[
                    row_index,
                    column_index,
                ] = ""

                customdata[
                    row_index,
                    column_index,
                ] = None
            else:
                text_values[
                    row_index,
                    column_index,
                ] = f"{value:.2f}".replace(
                    ".",
                    ",",
                )

                customdata[
                    row_index,
                    column_index,
                ] = float(value)

    heatmap = go.Heatmap(
        z=triangular_values,
        x=asset_order,
        y=asset_order,
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
        },
        hovertemplate=(
            "<b>%{y}</b> × <b>%{x}</b><br>"
            "Correlação: %{customdata:.2f}"
            "<extra></extra>"
        ),
        colorbar={
            "title": {
                "text": "Correlação",
                "side": "right",
            },
            "tickvals": [
                -1,
                -0.5,
                0,
                0.5,
                1,
            ],
            "ticktext": [
                "-1,00",
                "-0,50",
                "0,00",
                "0,50",
                "1,00",
            ],
            "thickness": 14,
            "len": 0.78,
            "outlinewidth": 0,
        },
    )

    figure_height = max(
        420,
        min(
            720,
            100 * len(asset_order) + 150,
        ),
    )

    fig_correlation = go.Figure(
        data=[heatmap]
    )

    fig_correlation.update_layout(
        title="",
        template="plotly_white",
        height=figure_height,
        margin={
            "l": 70,
            "r": 85,
            "t": 30,
            "b": 70,
        },
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        font={
            "family": "Inter, Arial, sans-serif",
            "color": "#334155",
        },
        xaxis={
            "title": None,
            "showgrid": False,
            "zeroline": False,
            "showline": False,
            "constrain": "domain",
            "categoryorder": "array",
            "categoryarray": asset_order,
            "tickfont": {
                "size": 12,
                "color": "#475569",
            },
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
            "categoryarray": asset_order,
            "tickfont": {
                "size": 12,
                "color": "#475569",
            },
            "fixedrange": True,
        },
    )

    st.plotly_chart(
        fig_correlation,
        width="stretch",
        config={
            "displayModeBar": False,
            "responsive": True,
        },
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
    "<p style='font-size: 1.1rem; color: #475569; margin-bottom: 2rem;'>"
    "Compare o comportamento histórico de diferentes ativos através de métricas de retorno, "
    "volatilidade, drawdown e correlação."
    "</p>",
    unsafe_allow_html=True
)

# Removida a mensagem informativa duplicada no topo sobre "finalidade histórica"
# (já presente no rodapé do dashboard de forma mais elegante).


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
# Metadados e Mensagens da consulta confirmada
# ==========================================================
if failed_symbols:
    st.warning(
        "Os seguintes símbolos não retornaram dados válidos: "
        + ", ".join(failed_symbols)
    )

# Agrupando as mensagens de sucesso, avisos técnicos e metodologia em um expander limpo
with st.expander(f"✅ Análise gerada para {len(asset_data)} ativos. Clique para visualizar a metodologia e parâmetros.", expanded=False):
    st.markdown(f"**Ativos Analisados:** {', '.join(asset_data.keys())}")
    st.markdown(f"**Período:** {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')} | **Frequência:** {frequency}")
    st.markdown(
        f"**Metodologia Matemática:** O Índice de Sharpe foi anualizado com uma taxa livre de risco de **{risk_free_rate_pct:.2f}% ao ano** "
        f"e fator de anualização **{annualization_factor}**. "
    )
    st.markdown(
        "**Tratamento de Dados:** A união das séries utiliza alinhamento completo por data, preservando dias sem negociação. "
        "As correlações consideram apenas pares de retornos válidos e coincidentes."
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
# Helper de Renderização dos Cartões Customizados
# ==========================================================
def render_custom_metric_card(title: str, asset: str, raw_value: float, formatted_str: str) -> None:
    """Renderiza um card estizado via HTML simulando aparência de dashboards modernos."""
    icon = "▲" if raw_value > 0 else "▼" if raw_value < 0 else "−"
    color_bg = "#dcfce7" if raw_value > 0 else "#fee2e2" if raw_value < 0 else "#f1f5f9"
    color_fg = "#166534" if raw_value > 0 else "#991b1b" if raw_value < 0 else "#475569"

    html = f"""
    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-direction: column; height: 100%;">
        <div style="color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
            {title}
        </div>
        <div style="color: #0f172a; font-size: 1.8rem; font-weight: 700; margin-bottom: 12px;">
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
        render_custom_metric_card(
            title="Melhor retorno",
            asset=best_row["Ativo"],
            raw_value=best_row["Retorno total"],
            formatted_str=format_return_pct(best_row["Retorno total"]),
        )

    with highlight_cols[1]:
        render_custom_metric_card(
            title="Menor retorno",
            asset=worst_row["Ativo"],
            raw_value=worst_row["Retorno total"],
            formatted_str=format_return_pct(worst_row["Retorno total"]),
        )

    with highlight_cols[2]:
        render_custom_metric_card(
            title="Menor perda máxima",
            asset=lowest_drawdown_row["Ativo"],
            raw_value=lowest_drawdown_row["Drawdown máximo"],
            formatted_str=format_return_pct(lowest_drawdown_row["Drawdown máximo"]),
        )
    
    st.markdown("<br>", unsafe_allow_html=True) # Espaçamento inferior


# ==========================================================
# Gráfico Base 100
# ==========================================================
st.markdown("### 📈 Evolução de Desempenho Histórico")
st.markdown(
    "<p style='color: #64748b; font-size: 0.95rem; margin-top: -12px; margin-bottom: 24px;'>"
    "Comparação de trajetória normalizada em <b>Base 100</b> no período inicial (ex: índice 120 = +20% de ganho)."
    "</p>",
    unsafe_allow_html=True
)


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
        labels={
            "Date": "Data",
            "Índice base 100": "Índice",
            "Ativo": "Ativo",
        },
        template="plotly_white",
    )

    fig_base_100.update_layout(
        hovermode="x unified",
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=10, r=20, t=40, b=20),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        font=dict(family="Inter, Arial, sans-serif", color="#334155")
    )

    fig_base_100.update_traces(
        connectgaps=True,
        line=dict(width=2.5),
    )

    with st.container(border=True):
        st.plotly_chart(
            fig_base_100,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
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


render_correlation_heatmap(
    correlation_matrix
)


st.caption(
    "A matriz exibe apenas a metade inferior para evitar duplicidade. "
    "A diagonal, que representa a correlação do ativo consigo mesmo, "
    "também foi ocultada."
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