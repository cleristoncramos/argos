import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# Adiciona a raiz do projeto ao caminho de importação.
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    ),
)

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


st.set_page_config(
    page_title="Comparação de Ativos | Argos DataLab",
    page_icon="⚖️",
    layout="wide",
)

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
# PARÂMETROS DA COMPARAÇÃO
# ==========================================================

st.sidebar.header("⚙️ Parâmetros da Comparação")

symbols_input = st.sidebar.text_input(
    "Símbolos dos ativos",
    value="BTC-USD,AAPL,USD=BRL,SPY",
    help=(
        "Informe de 2 a 5 símbolos separados por vírgula. "
        "Exemplo: BTC-USD,AAPL,USD=BRL,SPY"
    ),
)

start_date = st.sidebar.date_input(
    "Data inicial",
    value=datetime(2020, 1, 1),
)

end_date = st.sidebar.date_input(
    "Data final",
    value=datetime(2025, 12, 31),
)

frequency = st.sidebar.selectbox(
    "Frequência",
    options=config.FREQUENCIES,
    index=config.FREQUENCIES.index("Mensal"),
)

risk_free_rate_pct = st.sidebar.number_input(
    "Taxa livre de risco anual (%)",
    min_value=0.0,
    max_value=100.0,
    value=0.0,
    step=0.25,
    help=(
        "Informe uma taxa anual em percentual. "
        "Exemplo: 10,00 representa 10% ao ano."
    ),
)

annual_risk_free_rate = risk_free_rate_pct / 100

load_comparison = st.sidebar.button(
    "📊 Comparar ativos",
    type="primary",
)

# ==========================================================
# VALIDAÇÃO DAS ENTRADAS
# ==========================================================

if start_date >= end_date:
    st.sidebar.error(
        "A data inicial deve ser anterior à data final."
    )
    st.stop()

if not load_comparison:
    st.info(
        "Informe os símbolos, selecione o período e clique em "
        "**Comparar ativos**."
    )
    st.stop()

try:
    symbols = parse_symbols(symbols_input)
except ValueError as error:
    st.error(str(error))
    st.stop()

# ==========================================================
# COLETA E PROCESSAMENTO DOS ATIVOS
# ==========================================================

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
    st.error(
        "Não foi possível obter dados válidos para pelo menos dois ativos."
    )

    if failed_symbols:
        st.warning(
            "Símbolos sem dados válidos: "
            + ", ".join(failed_symbols)
        )

    st.stop()

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
# PREPARAÇÃO DE DADOS COMPARATIVOS
# ==========================================================

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

# ==========================================================
# FORMATAÇÃO PARA EXIBIÇÃO
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
        summary_display[column] = (
            summary_display[column]
            .map(format_return_pct)
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
    "USD=BRL": "#10B981",
    "SPY": "#8B5CF6",
}

for symbol in summary_numeric["Ativo"].tolist():
    if symbol not in color_map:
        color_map[symbol] = "#64748B"

# ==========================================================
# METODOLOGIA DO SHARPE
# ==========================================================

st.caption(
    f"Índice de Sharpe anualizado calculado com taxa livre de risco de "
    f"{risk_free_rate_pct:.2f}% ao ano e fator de anualização "
    f"{annualization_factor} para frequência {frequency}."
)

# ==========================================================
# DESTAQUES DA COMPARAÇÃO
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
# GRÁFICO BASE 100
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
# TABELA RESUMO
# ==========================================================

st.header("📊 Resumo Comparativo")

st.dataframe(
    summary_display,
    width="stretch",
    hide_index=True,
)

# ==========================================================
# CORRELAÇÃO
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
# MÉTRICAS POR ATIVO
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
# DADOS E EXPORTAÇÃO
# ==========================================================

st.header("📋 Dados Normalizados")

st.dataframe(
    base_100_table,
    width="stretch",
    height=300,
)

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
    "Dados históricos, indicadores e métricas de risco não garantem "
    "resultados futuros e não constituem recomendação de investimento."
)