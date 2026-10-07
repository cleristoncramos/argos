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


import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.ui.asset_cards import render_asset_hero_logo
from app.ui.disclaimers import (
    render_footer_disclaimer,
    render_methodology_limitations,
    render_profile_limitation_notice,
)
from app.ui.education import render_what_it_means
from app.ui.metric_card import render_metric_card
from app.ui.sidebar import render_asset_controls
from app.ui.state import initialize_asset_state
from app.ui.tables import (
    date_cell,
    number_cell,
    percent_cell,
    render_table,
)
from core.analyzer import calculate_returns
from core.assets import ASSETS
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
    format_context,
)


RISK_FREE_RATE_STATE_KEY = "risk_return_risk_free_rate_pct"
RISK_FREE_RATE_WIDGET_KEY = "risk_return_risk_free_rate_pct_widget"


# ==========================================================
# Configuração padrão da modebar do Plotly (zoom, pan, download, etc.)
# ==========================================================
PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
}


# ==========================================================
# Funções de Formatação
# ==========================================================
def format_percentage(value) -> str:
    """Formata em porcentagem no padrão brasileiro."""
    if value is None or pd.isna(value):
        return "N/A"
    return (
        f"{value * 100:,.2f}%"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def format_colored_pct(value, neutral_if_nan=False) -> str:
    """Formata porcentagem com cor dinâmica injetada via HTML."""
    if value is None or pd.isna(value):
        return "N/A"
    color = "#166534" if value > 0 else "#991b1b" if value < 0 else "#0f172a"
    sign = "+" if value > 0 else ""
    formatted_str = f"{sign}{value * 100:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"<span style='color: {color};'>{formatted_str}</span>"


def apply_custom_layout(fig):
    """Limpa o fundo e ajusta o layout base do gráfico Plotly."""
    fig.update_layout(
        title="",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, title_text=""),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        font=dict(family="Inter, Arial, sans-serif", color="#334155")
    )
    return fig


def sync_risk_free_rate() -> None:
    """Copia o valor do widget para o estado persistente da página."""
    st.session_state[RISK_FREE_RATE_STATE_KEY] = float(
        st.session_state[RISK_FREE_RATE_WIDGET_KEY]
    )


# ==========================================================
# Configuração da página
# ==========================================================
st.set_page_config(
    page_title="Argos DataLab",
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
    "<p style='font-size: 1.1rem; color: #475569; margin-bottom: 2rem;'>"
    "Analise retorno acumulado, volatilidade anualizada, drawdown máximo, "
    "percentual de períodos positivos e índice de Sharpe."
    "</p>",
    unsafe_allow_html=True
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


# =====================
# Card visual do ativo (logo em destaque) lado a lado com o
# expander de detalhes do processamento, na mesma fileira.
# =====================
current_asset = next((a for a in ASSETS if a["ticker"] == symbol), None)

col_logo, col_expander = st.columns([1, 3], vertical_alignment="center")

with col_logo:
    if current_asset:
        render_asset_hero_logo(current_asset)

with col_expander:
    with st.expander(f"✅ Análise gerada para {symbol.upper()}. Clique para visualizar os detalhes do processamento.", expanded=False):
        st.markdown(f"**Ativo Analisado:** {symbol.upper()}")
        st.markdown(f"**Período Selecionado:** {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')} | **Frequência:** {frequency}")
        st.markdown(f"**Observações Processadas:** {len(df_risk)} períodos.")
        st.markdown(
            f"**Metodologia Matemática:** A volatilidade e o Índice de Sharpe foram anualizados usando o fator multiplicador **{annualization_factor}**. "
            f"A taxa livre de risco anual considerada no cálculo foi de **{risk_free_rate_pct:.2f}%**."
        )

st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)


# =====================
# Aviso de limitação de perfil (não personalizado ao usuário)
# =====================
render_profile_limitation_notice()

st.markdown("<br>", unsafe_allow_html=True)


# =====================
# Métricas principais
# =====================
st.header("📊 Métricas Principais")

# Pré-cálculo dos Melhores/Piores períodos
best_period_val = df_risk["Simple_Return"].max()
worst_period_val = df_risk["Simple_Return"].min()
sharpe_value = metrics["Sharpe"]
str_sharpe = "N/A" if pd.isna(sharpe_value) else f"{sharpe_value:.2f}"

# Data do pior drawdown
if not df_risk.empty and not df_risk["Drawdown"].isna().all():
    worst_drawdown_idx = df_risk["Drawdown"].idxmin()
    worst_drawdown_date = df_risk.loc[worst_drawdown_idx, "Date"]
    worst_drawdown_date_str = pd.to_datetime(worst_drawdown_date).strftime("%d/%m/%Y")
else:
    worst_drawdown_date_str = "N/A"

# Primeira linha de cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    render_metric_card(
        "Retorno Acumulado",
        format_colored_pct(metrics["Retorno total"]),
        metric_key="retorno_total",
    )
with col2:
    render_metric_card(
        "Retorno Médio / Período",
        format_colored_pct(metrics["Retorno médio"]),
        metric_key="retorno_medio",
    )
with col3:
    render_metric_card(
        "Volatilidade Anualizada",
        f"<span style='color: #475569;'>{format_percentage(metrics['Volatilidade'])}</span>",
        metric_key="volatilidade",
    )
with col4:
    render_metric_card(
        "Índice de Sharpe",
        f"<span style='color: #0f172a;'>{str_sharpe}</span>",
        metric_key="sharpe",
    )

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

# Segunda linha de cards
col5, col6, col7, col8 = st.columns(4)

with col5:
    render_metric_card(
        "Melhor Período",
        format_colored_pct(best_period_val),
        tooltip="O maior ganho registrado em um único período dentro do intervalo analisado.",
    )
with col6:
    render_metric_card(
        "Pior Período",
        format_colored_pct(worst_period_val),
        tooltip="A maior perda registrada em um único período dentro do intervalo analisado.",
    )
with col7:
    render_metric_card(
        "Períodos Positivos",
        f"<span style='color: #166534;'>{format_percentage(metrics['Percentual positivo'])}</span>",
        metric_key="win_rate",
    )
with col8:
    render_metric_card(
        "Drawdown Máximo",
        format_colored_pct(metrics["Drawdown máximo"]),
        metric_key="drawdown_maximo",
    )

st.caption(f"📅 Data do pior drawdown no período: **{worst_drawdown_date_str}**")

render_what_it_means("drawdown")
render_what_it_means("sharpe")

st.markdown("<br>", unsafe_allow_html=True)


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

cumulative_return_figure = apply_custom_layout(cumulative_return_figure)

# Cálculo local do retorno acumulado para injetar os marcadores de topo e fundo
df_risk["Cum_Ret"] = (1 + df_risk["Simple_Return"].fillna(0)).cumprod() - 1
if not df_risk.empty and not df_risk["Cum_Ret"].isna().all():
    max_idx = df_risk["Cum_Ret"].idxmax()
    min_idx = df_risk["Cum_Ret"].idxmin()
    max_date = df_risk.loc[max_idx, "Date"]
    max_val = df_risk.loc[max_idx, "Cum_Ret"]
    min_date = df_risk.loc[min_idx, "Date"]
    min_val = df_risk.loc[min_idx, "Cum_Ret"]

    cumulative_return_figure.add_trace(go.Scatter(
        x=[max_date], y=[max_val],
        mode="markers+text",
        marker=dict(color="#166534", size=12, symbol="triangle-up"),
        text=[f"Máx: {max_val*100:.2f}%"],
        textposition="top center",
        textfont=dict(color="#166534", size=11, family="Inter, Arial, sans-serif"),
        hoverinfo="skip"
    ))

    cumulative_return_figure.add_trace(go.Scatter(
        x=[min_date], y=[min_val],
        mode="markers+text",
        marker=dict(color="#991b1b", size=12, symbol="triangle-down"),
        text=[f"Mín: {min_val*100:.2f}%"],
        textposition="bottom center",
        textfont=dict(color="#991b1b", size=11, family="Inter, Arial, sans-serif"),
        hoverinfo="skip"
    ))

with st.container(border=True):
    st.plotly_chart(
        cumulative_return_figure,
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )

st.caption(
    "Os marcadores indicam o maior e o menor valor acumulado dentro do "
    "período analisado -- não representam, isoladamente, pontos de "
    "entrada ou saída recomendados."
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

drawdown_figure = apply_custom_layout(drawdown_figure)

# Marcador do drawdown máximo
if not df_risk.empty and not df_risk["Drawdown"].isna().all():
    min_dd_idx = df_risk["Drawdown"].idxmin()
    min_dd_date = df_risk.loc[min_dd_idx, "Date"]
    min_dd_val = df_risk.loc[min_dd_idx, "Drawdown"]

    drawdown_figure.add_trace(go.Scatter(
        x=[min_dd_date], y=[min_dd_val],
        mode="markers+text",
        marker=dict(color="#991b1b", size=10, symbol="x"),
        text=[f"Pior Queda: {min_dd_val*100:.2f}%"],
        textposition="bottom center",
        textfont=dict(color="#991b1b", size=11, family="Inter, Arial, sans-serif"),
        hoverinfo="skip"
    ))

with st.container(border=True):
    st.plotly_chart(
        drawdown_figure,
        use_container_width=True,
        config=PLOTLY_CONFIG,
    )


# =====================
# Distribuição
# =====================
st.header("📊 Distribuição de Retornos")

rets = df_risk["Simple_Return"].dropna() * 100
if not rets.empty:

    bins = [-np.inf, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, np.inf]
    x_labels = [
        "Abaixo de<br>-30%", "-30 a<br>-25%", "-25 a<br>-20%", "-20 a<br>-15%",
        "-15 a<br>-10%", "-10 a<br>-5%", "-5 a<br>0%", "0 a<br>5%",
        "5 a<br>10%", "10 a<br>15%", "15 a<br>20%", "20 a<br>25%",
        "25 a<br>30%", "Acima de<br>30%"
    ]

    categorized = pd.cut(rets, bins=bins, labels=x_labels, right=True)
    counts = categorized.value_counts(sort=False)

    histogram_figure = go.Figure(
        go.Bar(
            x=counts.index.astype(str),
            y=counts.values,
            text=counts.values,
            textposition="outside",
            marker_color="#3B82F6",
            marker_line_color="#FFFFFF",
            marker_line_width=1,
            hovertemplate="<b>Intervalo:</b> %{x}<br><b>Frequência:</b> %{y} ocorrências<extra></extra>"
        )
    )

    histogram_figure = apply_custom_layout(histogram_figure)
    histogram_figure.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, title_text="")

    with st.container(border=True):
        st.plotly_chart(
            histogram_figure,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )

    st.caption(
        "A distribuição mostra a frequência histórica de retornos em cada "
        "faixa percentual -- um retrato estatístico do passado, não uma "
        "projeção de resultados futuros."
    )


# =====================
# Dados e download
# =====================
st.header("📄 Dados de Risco e Retorno")

display_columns = [
    "Date",
    "Value",
    "Simple_Return",
    "Log_Return",
    "Running_Peak",
    "Drawdown",
]

render_table(
    df_risk,
    display_columns,
    {
        "Date": date_cell,
        "Value": number_cell,
        "Running_Peak": number_cell,
        "Simple_Return": percent_cell(),
        "Log_Return": percent_cell(),
        "Drawdown": percent_cell(),
    },
    max_height=350,
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
# Limitações metodológicas
# =====================
render_methodology_limitations([
    "O Índice de Sharpe depende diretamente da taxa livre de risco e do fator de anualização escolhidos; alterar esses parâmetros altera o resultado.",
    f"Nesta análise, o fator de anualização utilizado foi **{annualization_factor}**, correspondente à frequência **{frequency}**, e a taxa livre de risco anual informada foi **{risk_free_rate_pct:.2f}%**.",
    "O drawdown máximo reflete um único evento histórico dentro do período selecionado e não indica a frequência com que perdas dessa magnitude costumam ocorrer.",
    "Todas as métricas desta página dependem do período e da frequência escolhidos -- resultados podem variar significativamente ao alterar esses parâmetros.",
    "Nenhuma métrica apresentada nesta página deve ser interpretada isoladamente como indicação de compra, venda ou adequação do ativo ao perfil do usuário.",
])


# =====================
# Rodapé
# =====================
render_footer_disclaimer()