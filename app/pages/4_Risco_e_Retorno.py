import os
import sys


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


import pandas as pd
import streamlit as st

from app.ui.sidebar import render_asset_controls
from app.ui.state import initialize_asset_state
from core.analyzer import calculate_returns
from core.config import ANNUALIZATION_FACTORS
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
from core.visualizations import (
    create_cumulative_return_chart,
    create_drawdown_chart,
    create_returns_histogram,
    format_context,
)


RISK_FREE_RATE_STATE_KEY = "risk_return_risk_free_rate_pct"
RISK_FREE_RATE_WIDGET_KEY = "risk_return_risk_free_rate_pct_widget"


def format_percentage(value) -> str:
    if value is None or pd.isna(value):
        return "N/A"

    return (
        f"{value * 100:,.2f}%"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def sync_risk_free_rate() -> None:
    """Copia o valor do widget para o estado persistente da página."""
    st.session_state[RISK_FREE_RATE_STATE_KEY] = float(
        st.session_state[RISK_FREE_RATE_WIDGET_KEY]
    )


st.set_page_config(
    page_title="Risco e Retorno | Argos DataLab",
    page_icon="🛡️",
    layout="wide",
)


initialize_asset_state()


if RISK_FREE_RATE_STATE_KEY not in st.session_state:
    st.session_state[RISK_FREE_RATE_STATE_KEY] = 0.0

if RISK_FREE_RATE_WIDGET_KEY not in st.session_state:
    st.session_state[RISK_FREE_RATE_WIDGET_KEY] = float(
        st.session_state[RISK_FREE_RATE_STATE_KEY]
    )


st.title("🛡️ Risco e Retorno")

st.markdown(
    """
Analise retorno acumulado, volatilidade anualizada, drawdown máximo,
percentual de períodos positivos e índice de Sharpe.
"""
)

st.warning(
    "As métricas são calculadas com dados históricos e dependem do período, "
    "da frequência e da taxa livre de risco informados. Elas não constituem "
    "recomendação de investimento."
)


# =====================
# Controles compartilhados
# =====================
asset_params = render_asset_controls(
    title="⚙️ Parâmetros de Risco e Retorno",
    button_label="📊 Analisar risco e retorno",
    button_key="risk_return_load_button",
)

symbol = asset_params["symbol"]
start_date = asset_params["start_date"]
end_date = asset_params["end_date"]
frequency = asset_params["frequency"]
load_analysis = asset_params["submitted"]


# =====================
# Controle específico
# =====================
with st.sidebar:
    st.divider()

    risk_free_rate_pct = st.number_input(
        "Taxa livre de risco anual (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.25,
        key=RISK_FREE_RATE_WIDGET_KEY,
        on_change=sync_risk_free_rate,
        help=(
            "Exemplo: 10,00 representa taxa livre de risco de 10% ao ano."
        ),
    )


# O valor vem do estado persistente, e não diretamente da chave do widget.
risk_free_rate_pct = float(
    st.session_state[RISK_FREE_RATE_STATE_KEY]
)

annual_risk_free_rate = risk_free_rate_pct / 100


# =====================
# Processamento
# =====================
if load_analysis:
    if not symbol:
        st.sidebar.error(
            "Informe um símbolo de ativo antes de calcular risco e retorno."
        )
        st.stop()

    risk_free_rate_pct = float(
        st.session_state[RISK_FREE_RATE_STATE_KEY]
    )

    annual_risk_free_rate = risk_free_rate_pct / 100

    with st.spinner("Carregando dados e calculando métricas..."):
        df_raw = download_active_data(
            symbol=symbol,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            interval="1d",
        )

        if df_raw is None or df_raw.empty:
            st.session_state["risk_return_loaded"] = False
            st.session_state["risk_return_query"] = None
            st.session_state.pop("risk_return_metrics", None)
            st.session_state.pop("risk_return_df", None)

            st.error(
                f"Não foi possível carregar dados para '{symbol}'. "
                "Verifique o símbolo e o período."
            )
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

        df_returns = calculate_returns(
            df_primary,
            "Value",
        )

        df_risk = calculate_drawdown(
            df_returns,
            "Value",
        )

        annualization_factor = ANNUALIZATION_FACTORS.get(
            frequency,
            252,
        )

        metrics = build_risk_summary(
            df=df_risk,
            value_col="Value",
            annualization_factor=float(annualization_factor),
            annual_risk_free_rate=annual_risk_free_rate,
        )

    st.session_state["risk_return_loaded"] = True
    st.session_state["risk_return_query"] = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
        "risk_free_rate_pct": risk_free_rate_pct,
    }
    st.session_state["risk_return_metrics"] = metrics
    st.session_state["risk_return_df"] = df_risk


# =====================
# Consulta confirmada
# =====================
query = st.session_state.get("risk_return_query")

if (
    not st.session_state.get("risk_return_loaded")
    or query is None
    or "risk_return_metrics" not in st.session_state
    or "risk_return_df" not in st.session_state
):
    st.info(
        "Configure os parâmetros na barra lateral e clique em "
        "**Analisar risco e retorno**."
    )
    st.stop()


df_risk = st.session_state["risk_return_df"]
metrics = st.session_state["risk_return_metrics"]

symbol = query["symbol"]
start_date = query["start_date"]
end_date = query["end_date"]
frequency = query["frequency"]

# Use a taxa confirmada junto com os dados e as métricas apresentados.
risk_free_rate_pct = float(query["risk_free_rate_pct"])
annual_risk_free_rate = risk_free_rate_pct / 100

annualization_factor = ANNUALIZATION_FACTORS.get(
    frequency,
    252,
)

context = format_context(
    symbol=symbol.upper(),
    start_date=start_date,
    end_date=end_date,
    frequency=frequency,
)


st.info(
    f"Ativo: **{symbol.upper()}** · "
    f"Período: **{start_date.strftime('%d/%m/%Y')} a "
    f"{end_date.strftime('%d/%m/%Y')}** · "
    f"Frequência: **{frequency}** · "
    f"Observações: **{len(df_risk)}**"
)

st.caption(
    f"Volatilidade e Sharpe anualizados com fator {annualization_factor}. "
    f"Taxa livre de risco anual adotada: {risk_free_rate_pct:.2f}%."
)


# =====================
# Métricas principais
# =====================
st.header("📊 Métricas Principais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Retorno acumulado",
        format_percentage(
            metrics["Retorno total"]
        ),
    )

with col2:
    st.metric(
        "Volatilidade anualizada",
        format_percentage(
            metrics["Volatilidade"]
        ),
    )

with col3:
    st.metric(
        "Drawdown máximo",
        format_percentage(
            metrics["Drawdown máximo"]
        ),
    )

with col4:
    sharpe_value = metrics["Sharpe"]

    st.metric(
        "Índice de Sharpe",
        (
            "N/A"
            if pd.isna(sharpe_value)
            else f"{sharpe_value:.2f}"
        ),
    )


# =====================
# Retorno acumulado
# =====================
st.header("📈 Retorno Acumulado")

cumulative_return_figure = create_cumulative_return_chart(
    df=df_risk,
    symbol=symbol.upper(),
    context=context,
    return_col="Simple_Return",
)

st.plotly_chart(
    cumulative_return_figure,
    width="stretch",
)


# =====================
# Drawdown
# =====================
st.header("📉 Drawdown")

drawdown_figure = create_drawdown_chart(
    df=df_risk,
    symbol=symbol.upper(),
    context=context,
    drawdown_col="Drawdown",
)

st.plotly_chart(
    drawdown_figure,
    width="stretch",
)


# =====================
# Distribuição
# =====================
st.header("📊 Distribuição de Retornos")

histogram_figure = create_returns_histogram(
    df=df_risk,
    symbol=symbol.upper(),
    context=context,
    return_col="Simple_Return",
)

st.plotly_chart(
    histogram_figure,
    width="stretch",
)


# =====================
# Detalhamento
# =====================
st.header("📋 Detalhamento das Métricas")

details = pd.DataFrame(
    [
        {
            "Métrica": "Retorno total",
            "Valor": format_percentage(
                metrics["Retorno total"]
            ),
            "Descrição": (
                "Variação acumulada entre o primeiro e o último "
                "valor do período."
            ),
        },
        {
            "Métrica": "Retorno médio por período",
            "Valor": format_percentage(
                metrics["Retorno médio"]
            ),
            "Descrição": (
                "Média dos retornos simples na frequência selecionada."
            ),
        },
        {
            "Métrica": "Volatilidade anualizada",
            "Valor": format_percentage(
                metrics["Volatilidade"]
            ),
            "Descrição": (
                "Dispersão anualizada dos retornos; valores maiores "
                "indicam maior variação histórica."
            ),
        },
        {
            "Métrica": "Drawdown máximo",
            "Valor": format_percentage(
                metrics["Drawdown máximo"]
            ),
            "Descrição": (
                "Maior queda percentual a partir de um pico anterior "
                "no período analisado."
            ),
        },
        {
            "Métrica": "Períodos positivos",
            "Valor": format_percentage(
                metrics["Percentual positivo"]
            ),
            "Descrição": (
                "Proporção de períodos com retorno simples superior a zero."
            ),
        },
        {
            "Métrica": "Índice de Sharpe",
            "Valor": (
                "N/A"
                if pd.isna(metrics["Sharpe"])
                else f"{metrics['Sharpe']:.2f}"
            ),
            "Descrição": (
                "Relação anualizada entre retorno excedente e "
                "volatilidade, considerando a taxa livre de risco."
            ),
        },
    ]
)

st.dataframe(
    details,
    width="stretch",
    hide_index=True,
)


# =====================
# Dados e download
# =====================
st.header("📄 Dados de Risco e Retorno")

st.dataframe(
    df_risk[
        [
            "Date",
            "Value",
            "Simple_Return",
            "Log_Return",
            "Running_Peak",
            "Drawdown",
        ]
    ],
    width="stretch",
    height=320,
)

csv_data = df_risk.to_csv(
    index=False,
).encode(
    "utf-8"
)

st.download_button(
    label="⬇️ Baixar dados de risco e retorno em CSV",
    data=csv_data,
    file_name=f"{symbol.upper()}_risco_retorno.csv",
    mime="text/csv",
)


# =====================
# Rodapé
# =====================
st.markdown("---")

st.caption(
    "⚠️ Esta ferramenta possui finalidade educacional e de pesquisa. "
    "Desempenho passado não garante resultados futuros. As métricas "
    "dependem da janela analisada e não constituem recomendação de investimento."
)