import os
import sys


PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT,
    )


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.ui.sidebar import render_asset_controls
from app.ui.state import (
    initialize_asset_state,
    persist_asset_widget_state,
)
from core.analyzer import (
    calculate_percentage_change,
    calculate_statistics,
    create_year_month_matrix,
)
from core.data_loader import download_active_data, validate_data
from core.data_processor import (
    aggregate_by_frequency,
    prepare_dataframe,
    select_primary_variable,
)
from core.formatters import format_brl


st.set_page_config(
    page_title="Argos DataLab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


initialize_asset_state()


st.title("📊 Argos DataLab")

st.markdown(
    "### Inteligência de Dados para Apoio à Decisão no Mercado Financeiro"
)

st.caption(
    "Projeto PIBITI UFPI 2026–2027 · "
    "Orientador: Arlino Henrique Magalhães de Araújo"
)


# =====================
# Controles compartilhados
# =====================
asset_params = render_asset_controls(
    title="⚙️ Configurações",
    button_label="🔄 Carregar Dados",
    button_key="asset_load_button",
)

symbol = asset_params["symbol"]
start_date = asset_params["start_date"]
end_date = asset_params["end_date"]
frequency = asset_params["frequency"]
load_data = asset_params["submitted"]


# =====================
# Carregamento de dados
# =====================
if load_data:
    persist_asset_widget_state()

    if start_date >= end_date:
        st.sidebar.error(
            "A data inicial deve ser anterior à data final."
        )
        st.stop()

    if not symbol:
        st.sidebar.error(
            "Informe um símbolo de ativo antes de carregar os dados."
        )
        st.stop()

    st.session_state["asset_loaded"] = True
    st.session_state["asset_query"] = {
        "symbol": st.session_state["asset_symbol"],
        "start_date": st.session_state["asset_start_date"],
        "end_date": st.session_state["asset_end_date"],
        "frequency": st.session_state["asset_frequency"],
    }
    
    with st.spinner("Baixando e processando dados..."):
        df_raw = download_active_data(
            symbol=symbol,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            interval="1d",
        )

        if df_raw is None or df_raw.empty:
            st.session_state["asset_loaded"] = False
            st.session_state["asset_query"] = None

            st.error(
                f"Não foi possível carregar dados para o ativo "
                f"'{symbol}'. Verifique o símbolo e o período informado."
            )
            st.stop()

        validation = validate_data(df_raw)

        if not validation["has_data"]:
            st.session_state["asset_loaded"] = False
            st.session_state["asset_query"] = None

            st.error("❌ Dados inválidos.")
            st.stop()

        df_prepared = prepare_dataframe(df_raw)

        df_aggregated = aggregate_by_frequency(
            df_prepared,
            frequency,
        )

        df_primary = select_primary_variable(
            df_aggregated,
            "Close",
        )

        df_with_change = calculate_percentage_change(
            df_primary,
            "Value",
        )

        stats = calculate_statistics(
            df_with_change,
            "Value",
        )

        st.session_state["asset_df"] = df_with_change
        st.session_state["asset_stats"] = stats
        st.session_state["asset_validation"] = validation

        st.success(
            f"✅ Dados carregados: {symbol} | "
            f"{len(df_with_change)} períodos"
        )

# =====================
# Consulta confirmada
# =====================
query = st.session_state.get("asset_query")

if (
    not st.session_state.get("asset_loaded")
    or query is None
    or "asset_df" not in st.session_state
):
    st.info(
        "👈 Configure os parâmetros na barra lateral e clique em "
        "**Carregar Dados**."
    )
    st.stop()


df = st.session_state["asset_df"]
stats = st.session_state["asset_stats"]
validation = st.session_state["asset_validation"]

symbol = query["symbol"]
start_date = query["start_date"]
end_date = query["end_date"]
frequency = query["frequency"]


st.info(
    f"Ativo analisado: **{symbol}** · "
    f"Período: **{start_date.strftime('%d/%m/%Y')}** a "
    f"**{end_date.strftime('%d/%m/%Y')}** · "
    f"Frequência: **{frequency}**"
)


# =====================
# Seção 1: Resumo
# =====================
st.header("📊 Visão Geral do Ativo")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Primeiro Valor",
        format_brl(stats["first_value"]),
    )

with col2:
    st.metric(
        "Último Valor",
        format_brl(stats["last_value"]),
    )

with col3:
    total_return = stats["total_return"]

    st.metric(
        label="Retorno Total",
        value=f"{total_return:.2f}%".replace(".", ","),
        delta=f"{total_return:.2f}%".replace(".", ","),
    )

with col4:
    st.metric(
        label="Períodos",
        value=stats["count"],
    )


# =====================
# Seção 2: Evolução Temporal
# =====================
st.header("📈 Evolução Temporal do Ativo")

fig_line = px.line(
    df,
    x="Date",
    y="Value",
    title=f"Evolução do Preço de Fechamento — {symbol}",
    labels={
        "Date": "Data",
        "Value": "Preço",
    },
    template="plotly_white",
)

fig_line.update_traces(
    line=dict(width=2),
)

st.plotly_chart(
    fig_line,
    width="stretch",
)


# =====================
# Seção 3: Variação Percentual
# =====================
st.header(f"📉 Variação Percentual — {frequency}")

df_chart = df.dropna(
    subset=["Pct_Change"],
).copy()

fig_bar = px.bar(
    df_chart,
    x="Date",
    y="Pct_Change",
    title=f"Variação Percentual entre Períodos — {frequency}",
    labels={
        "Date": "Data",
        "Pct_Change": "Variação (%)",
    },
    color="Pct_Change",
    color_continuous_scale="RdYlGn",
    template="plotly_white",
)

st.plotly_chart(
    fig_bar,
    width="stretch",
)


# =====================
# Seção 4: Matriz Anual x Mensal
# =====================
st.header("🗓️ Padrões Sazonais")

df_matrix = create_year_month_matrix(
    df,
    "Pct_Change",
)

text_matrix = df_matrix.apply(
    lambda column: column.map(
        lambda value: (
            f"{value:.2f}%".replace(".", ",")
            if pd.notna(value)
            else ""
        )
    )
)

fig_heatmap = go.Figure(
    data=go.Heatmap(
        z=df_matrix.values,
        x=df_matrix.columns,
        y=df_matrix.index,
        colorscale="RdYlGn",
        text=text_matrix.values,
        texttemplate="%{text}",
        textfont={
            "size": 11,
            "color": "black",
        },
        customdata=text_matrix.values,
        hoverongaps=False,
        hovertemplate=(
            "Ano: %{y}<br>"
            "Mês: %{x}<br>"
            "Variação: %{customdata}"
            "<extra></extra>"
        ),
    )
)

fig_heatmap.update_layout(
    title="Variação Média por Ano e Mês",
    xaxis_title="Mês",
    yaxis_title="Ano",
    template="plotly_white",
)

fig_heatmap.update_yaxes(
    autorange="reversed",
)

st.plotly_chart(
    fig_heatmap,
    width="stretch",
)


# =====================
# Seção 5: Tabela de Dados
# =====================
st.header("📋 Dados Processados")

display_columns = [
    "Date",
    "Open",
    "High",
    "Low",
    "Value",
    "Pct_Change",
]

available_columns = [
    column
    for column in display_columns
    if column in df.columns
]

df_display = df[available_columns].copy()

df_display = df_display.rename(
    columns={
        "Value": "Close",
    }
)

df_display["Date"] = pd.to_datetime(
    df_display["Date"],
    errors="coerce",
).dt.strftime(
    "%d/%m/%Y"
)

monetary_columns = [
    column
    for column in ["Open", "High", "Low", "Close"]
    if column in df_display.columns
]

for column in monetary_columns:
    df_display[column] = df_display[column].map(
        format_brl,
    )

if "Pct_Change" in df_display.columns:
    df_display["Pct_Change"] = df_display["Pct_Change"].map(
        lambda value: (
            "—"
            if pd.isna(value)
            else f"{float(value):.2f}%".replace(".", ",")
        )
    )


def color_pct_change(value):
    """
    Aplica cor conforme o sinal da variação percentual exibida.
    """
    if pd.isna(value) or value == "—":
        return ""

    try:
        numeric_value = float(
            str(value)
            .replace("%", "")
            .replace(".", "")
            .replace(",", ".")
        )
    except ValueError:
        return ""

    if numeric_value > 0:
        return "color: green; font-weight: 600;"

    if numeric_value < 0:
        return "color: red; font-weight: 600;"

    return ""


styled_df = df_display.style

if "Pct_Change" in df_display.columns:
    styled_df = styled_df.map(
        color_pct_change,
        subset=["Pct_Change"],
    )

st.dataframe(
    styled_df,
    width="stretch",
    hide_index=True,
)


# =====================
# Download
# =====================
csv_data = df.to_csv(
    index=False,
).encode(
    "utf-8"
)

st.download_button(
    label="⬇️ Baixar CSV",
    data=csv_data,
    file_name=f"{symbol}_dados_tratados.csv",
    mime="text/csv",
)


# =====================
# Seção 6: Validação
# =====================
st.header("🔍 Qualidade e Validação dos Dados")

col_v1, col_v2 = st.columns(2)

with col_v1:
    st.subheader("Qualidade")
    st.write(f"**Total de linhas:** {validation['total_rows']}")
    st.write(
        f"**Datas duplicadas:** {validation['duplicate_dates']}"
    )
    st.write(
        f"**Valores negativos (Close):** "
        f"{validation['negative_close']}"
    )

with col_v2:
    st.subheader("Valores Ausentes")
    st.write(validation["missing_values"])


# =====================
# Rodapé
# =====================
st.markdown("---")

st.caption(
    "⚠️ **Aviso:** Esta ferramenta é destinada a fins educacionais "
    "e de pesquisa. Os dados históricos não garantem resultados "
    "futuros. Não constitui recomendação de investimento."
)