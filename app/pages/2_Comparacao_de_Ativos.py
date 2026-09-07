import os
import sys
from datetime import datetime


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


COMPARISON_SYMBOLS_STATE_KEY = "comparison_symbols_input"
COMPARISON_START_DATE_STATE_KEY = "comparison_start_date"
COMPARISON_END_DATE_STATE_KEY = "comparison_end_date"
COMPARISON_FREQUENCY_STATE_KEY = "comparison_frequency"
COMPARISON_RISK_FREE_RATE_STATE_KEY = "comparison_risk_free_rate_pct"

COMPARISON_SYMBOLS_WIDGET_KEY = "comparison_symbols_input_widget"
COMPARISON_START_DATE_WIDGET_KEY = "comparison_start_date_widget"
COMPARISON_END_DATE_WIDGET_KEY = "comparison_end_date_widget"
COMPARISON_FREQUENCY_WIDGET_KEY = "comparison_frequency_widget"
COMPARISON_RISK_FREE_RATE_WIDGET_KEY = (
    "comparison_risk_free_rate_pct_widget"
)


def sync_comparison_symbols() -> None:
    """Sincroniza a lista de símbolos informada no widget."""
    st.session_state[COMPARISON_SYMBOLS_STATE_KEY] = (
        st.session_state[COMPARISON_SYMBOLS_WIDGET_KEY]
    )


def sync_comparison_start_date() -> None:
    """Sincroniza a data inicial informada no widget."""
    st.session_state[COMPARISON_START_DATE_STATE_KEY] = (
        st.session_state[COMPARISON_START_DATE_WIDGET_KEY]
    )


def sync_comparison_end_date() -> None:
    """Sincroniza a data final informada no widget."""
    st.session_state[COMPARISON_END_DATE_STATE_KEY] = (
        st.session_state[COMPARISON_END_DATE_WIDGET_KEY]
    )


def sync_comparison_frequency() -> None:
    """Sincroniza a frequência informada no widget."""
    st.session_state[COMPARISON_FREQUENCY_STATE_KEY] = (
        st.session_state[COMPARISON_FREQUENCY_WIDGET_KEY]
    )


def sync_comparison_risk_free_rate() -> None:
    """Sincroniza a taxa livre de risco informada no widget."""
    st.session_state[COMPARISON_RISK_FREE_RATE_STATE_KEY] = float(
        st.session_state[COMPARISON_RISK_FREE_RATE_WIDGET_KEY]
    )


def initialize_comparison_state() -> None:
    """Inicializa os estados persistentes e temporários da comparação."""
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

    default_symbols = "BTC-USD,AAPL,USDBRL=X,SPY"

    if COMPARISON_SYMBOLS_STATE_KEY not in st.session_state:
        st.session_state[COMPARISON_SYMBOLS_STATE_KEY] = default_symbols

    if COMPARISON_START_DATE_STATE_KEY not in st.session_state:
        st.session_state[COMPARISON_START_DATE_STATE_KEY] = asset_start_date

    if COMPARISON_END_DATE_STATE_KEY not in st.session_state:
        st.session_state[COMPARISON_END_DATE_STATE_KEY] = asset_end_date

    if COMPARISON_FREQUENCY_STATE_KEY not in st.session_state:
        st.session_state[COMPARISON_FREQUENCY_STATE_KEY] = asset_frequency

    if COMPARISON_RISK_FREE_RATE_STATE_KEY not in st.session_state:
        st.session_state[COMPARISON_RISK_FREE_RATE_STATE_KEY] = 0.0

    if COMPARISON_SYMBOLS_WIDGET_KEY not in st.session_state:
        st.session_state[COMPARISON_SYMBOLS_WIDGET_KEY] = (
            st.session_state[COMPARISON_SYMBOLS_STATE_KEY]
        )

    if COMPARISON_START_DATE_WIDGET_KEY not in st.session_state:
        st.session_state[COMPARISON_START_DATE_WIDGET_KEY] = (
            st.session_state[COMPARISON_START_DATE_STATE_KEY]
        )

    if COMPARISON_END_DATE_WIDGET_KEY not in st.session_state:
        st.session_state[COMPARISON_END_DATE_WIDGET_KEY] = (
            st.session_state[COMPARISON_END_DATE_STATE_KEY]
        )

    if COMPARISON_FREQUENCY_WIDGET_KEY not in st.session_state:
        st.session_state[COMPARISON_FREQUENCY_WIDGET_KEY] = (
            st.session_state[COMPARISON_FREQUENCY_STATE_KEY]
        )

    if COMPARISON_RISK_FREE_RATE_WIDGET_KEY not in st.session_state:
        st.session_state[COMPARISON_RISK_FREE_RATE_WIDGET_KEY] = float(
            st.session_state[COMPARISON_RISK_FREE_RATE_STATE_KEY]
        )


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

    symbols_input = st.text_input(
        "Símbolos dos ativos",
        key=COMPARISON_SYMBOLS_WIDGET_KEY,
        on_change=sync_comparison_symbols,
        help=(
            "Informe de 2 a 5 símbolos separados por vírgula. "
            "Exemplo: BTC-USD,AAPL,USDBRL=X,SPY"
        ),
    )

    start_date = st.date_input(
        "Data inicial",
        key=COMPARISON_START_DATE_WIDGET_KEY,
        on_change=sync_comparison_start_date,
    )

    end_date = st.date_input(
        "Data final",
        key=COMPARISON_END_DATE_WIDGET_KEY,
        on_change=sync_comparison_end_date,
    )

    frequency = st.selectbox(
        "Frequência",
        options=config.FREQUENCIES,
        key=COMPARISON_FREQUENCY_WIDGET_KEY,
        on_change=sync_comparison_frequency,
    )

    risk_free_rate_pct = st.number_input(
        "Taxa livre de risco anual (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.25,
        key=COMPARISON_RISK_FREE_RATE_WIDGET_KEY,
        on_change=sync_comparison_risk_free_rate,
        help=(
            "Informe uma taxa anual em percentual. "
            "Exemplo: 10,00 representa 10% ao ano."
        ),
    )

    load_comparison = st.button(
        "📊 Comparar ativos",
        type="primary",
        key="comparison_load_button",
    )


symbols_input = st.session_state[COMPARISON_SYMBOLS_STATE_KEY]
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
        st.session_state.pop("comparison_asset_data", None)
        st.session_state.pop("comparison_failed_symbols", None)

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

    correlation_matrix = calculate_correlation_matrix(
        returns_table
    )

    summary = create_comparison_summary(asset_data)

    annualization_factor = ANNUALIZATION_FACTORS.get(
        frequency,
        252,
    )

    risk_rows = []

    for symbol, df in asset_data.items():
        metrics = build_risk_summary(
            df=df,
            value_col="Value",
            annualization_factor=float(annualization_factor),
            annual_risk_free_rate=annual_risk_free_rate,
        )

        risk_rows.append(
            {
                "Ativo": symbol,
                "Volatilidade": metrics.get("Volatilidade"),
                "Drawdown máximo": metrics.get("Drawdown máximo"),
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
        "Informe os símbolos, selecione o período e clique em "
        "**Comparar ativos**."
    )
    st.stop()


asset_data = st.session_state["comparison_asset_data"]
failed_symbols = st.session_state["comparison_failed_symbols"]
base_100_table = st.session_state["comparison_base_100_table"]
price_table = st.session_state["comparison_price_table"]
returns_table = st.session_state["comparison_returns_table"]
correlation_matrix = st.session_state["comparison_correlation_matrix"]
summary = st.session_state["comparison_summary"]

symbols_input = query["symbols_input"]
start_date = query["start_date"]
end_date = query["end_date"]
frequency = query["frequency"]
risk_free_rate_pct = float(query["risk_free_rate_pct"])
annual_risk_free_rate = risk_free_rate_pct / 100

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
# Formatação para exibição
# ==========================================================
summary_numeric = summary.copy()

summary_display = summary_numeric.sort_values(
    by="Retorno total",
    ascending=False,
    na_position="last",
).copy()

percentage_columns = [
    "Retorno total",
    "Retorno médio",
    "Volatilidade",
    "Drawdown máximo",
    "Percentual positivo",
]

for column in percentage_columns:
    if column in summary_display.columns:
        summary_display[column] = summary_display[column].map(
            format_return_pct
        )

for column in ["Primeiro valor", "Último valor"]:
    if column in summary_display.columns:
        summary_display[column] = summary_display[column].map(
            lambda value: (
                f"{value:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
                if pd.notna(value)
                else "—"
            )
        )

if "Sharpe" in summary_display.columns:
    summary_display["Sharpe"] = summary_display["Sharpe"].map(
        lambda value: (
            f"{value:.2f}"
            if pd.notna(value)
            else "N/A"
        )
    )


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
# Gráfico base 100
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
# Tabela resumo
# ==========================================================
st.header("📊 Resumo Comparativo")

st.dataframe(
    summary_display,
    width="stretch",
    hide_index=True,
)


# ==========================================================
# Correlação
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
            colorbar=dict(title="Correlação"),
            text=np.round(correlation_matrix.values, 2),
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

    correlation_display = correlation_matrix.copy().round(2)

    st.dataframe(
        correlation_display,
        width="stretch",
    )

st.caption(
    "A correlação é calculada com retornos históricos coincidentes. "
    "Ela não representa causalidade nem garante comportamento futuro."
)


# ==========================================================
# Métricas por ativo
# ==========================================================
st.header("🧮 Métricas por Ativo")

for _, row in summary_numeric.iterrows():
    st.subheader(row["Ativo"])

    metric_cols = st.columns(6)

    metric_items = [
        (
            "Retorno total",
            format_return_pct(
                row["Retorno total"]
            ),
        ),
        (
            "Retorno médio",
            format_return_pct(
                row["Retorno médio"]
            ),
        ),
        (
            "Volatilidade",
            format_return_pct(
                row["Volatilidade"]
            ),
        ),
        (
            "Drawdown máximo",
            format_return_pct(
                row["Drawdown máximo"]
            ),
        ),
        (
            "Positivo",
            format_return_pct(
                row["Percentual positivo"]
            ),
        ),
        (
            "Sharpe",
            (
                "N/A"
                if pd.isna(row["Sharpe"])
                else f"{row['Sharpe']:.2f}"
            ),
        ),
    ]

    for column, (label, value) in zip(
        metric_cols,
        metric_items,
    ):
        column.metric(label, value)

    st.caption(
        "A comparação considera retorno, volatilidade e perda máxima "
        "intermediária, não apenas a valorização final."
    )


# ==========================================================
# Dados e exportação
# ==========================================================
st.header("📋 Dados Normalizados")

st.dataframe(
    base_100_table,
    width="stretch",
    height=300,
)

csv_data = base_100_table.to_csv(
    index=False,
).encode(
    "utf-8"
)

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