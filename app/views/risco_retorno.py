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
    format_context,
)


RISK_FREE_RATE_STATE_KEY = "risk_return_risk_free_rate_pct"
RISK_FREE_RATE_WIDGET_KEY = "risk_return_risk_free_rate_pct_widget"


# ==========================================================
# Funções de Formatação e Tabelas Customizadas
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


def build_table_styles(prefix: str) -> str:
    """Gera os estilos CSS comuns das tabelas HTML da página."""
    return (
        f"""
        <style>
        .{prefix}-wrapper {{
            width: 100%;
            overflow-x: auto;
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
            border-bottom: 3px solid #97b7c4; /* Borda customizada combinando com demais páginas */
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


def render_html_table(dataframe: pd.DataFrame, columns: list, prefix: str, is_details: bool = False) -> None:
    """Renderiza um DataFrame como tabela HTML customizada."""
    if dataframe is None or dataframe.empty:
        st.info("Não há dados disponíveis para exibição.")
        return

    display_df = dataframe[columns].copy()
    records = display_df.to_dict(orient="records")

    header_html = "".join(f"<th>{escape(str(c))}</th>" for c in columns)

    rows_html = []
    for position, record in enumerate(records):
        cells_html = []
        for column in columns:
            raw_val = record.get(column)

            if is_details:
                formatted_val = raw_val
                if column in ["Métrica", "Descrição"]:
                    cell_style = "text-align:left;white-space:normal;font-family:inherit;"
                else:
                    cell_style = "text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;"
            else:
                if column == "Date":
                    date_val = pd.to_datetime(raw_val, errors="coerce")
                    formatted_val = "—" if pd.isna(date_val) else date_val.strftime("%d/%m/%Y")
                    cell_style = "text-align:center;white-space:nowrap;"
                elif column in ["Value", "Running_Peak"]:
                    formatted_val = format_brazilian_number(raw_val)
                    cell_style = "text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;"
                elif column in ["Simple_Return", "Log_Return", "Drawdown"]:
                    formatted_val = format_percentage(raw_val)
                    cell_style = "text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;"
                else:
                    formatted_val = str(raw_val) if pd.notna(raw_val) else "—"
                    cell_style = "text-align:right;white-space:nowrap;"

            cells_html.append(f'<td style="{cell_style}">{escape(str(formatted_val))}</td>')

        row_class = f"{prefix}-row-even" if position % 2 == 0 else f"{prefix}-row-odd"
        rows_html.append(f'<tr class="{row_class}">{"".join(cells_html)}</tr>')

    table_height = 420 if is_details else 350
    table_html = (
        build_table_styles(prefix)
        + f'<div class="{prefix}-wrapper" style="max-height: {table_height}px; overflow-y: auto;">'
        + f'<table class="{prefix}-table">'
        + f"<thead><tr>{header_html}</tr></thead>"
        + f"<tbody>{''.join(rows_html)}</tbody>"
        + "</table>"
        + "</div>"
    )
    
    st.markdown(table_html, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, tooltip: str = "") -> None:
    """Renderiza um card estizado via HTML simulando aparência de dashboards modernos, com tooltip de info."""
    tooltip_html = f"""<span title="{escape(tooltip)}" style="cursor: help; color: #94a3b8; margin-left: 6px; font-size: 0.95rem;">&#9432;</span>""" if tooltip else ""
    html = f"""
    <div style="background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-direction: column; height: 100%;">
        <div style="color: #64748b; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; display: flex; align-items: center;">
            {title} {tooltip_html}
        </div>
        <div style="color: #0f172a; font-size: 1.8rem; font-weight: 700; margin-bottom: 0px; font-family: 'Inter', sans-serif; letter-spacing: -0.5px;">
            {value}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


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


# Expander para informações de contexto e processamento
with st.expander(f"✅ Análise gerada para {symbol.upper()}. Clique para visualizar os detalhes do processamento.", expanded=False):
    st.markdown(f"**Ativo Analisado:** {symbol.upper()}")
    st.markdown(f"**Período Selecionado:** {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')} | **Frequência:** {frequency}")
    st.markdown(f"**Observações Processadas:** {len(df_risk)} períodos.")
    st.markdown(
        f"**Metodologia Matemática:** A volatilidade e o Índice de Sharpe foram anualizados usando o fator multiplicador **{annualization_factor}**. "
        f"A taxa livre de risco anual considerada no cálculo foi de **{risk_free_rate_pct:.2f}%**."
    )


# =====================
# Métricas principais
# =====================
st.header("📊 Métricas Principais")

# Pré-cálculo dos Melhores/Piores períodos
best_period_val = df_risk["Simple_Return"].max()
worst_period_val = df_risk["Simple_Return"].min()
sharpe_value = metrics["Sharpe"]
str_sharpe = "N/A" if pd.isna(sharpe_value) else f"{sharpe_value:.2f}"

# Primeira Linha de Cards com Tooltips embutidos
col1, col2, col3, col4 = st.columns(4)

with col1:
    render_metric_card(
        title="Retorno Acumulado", 
        value=format_colored_pct(metrics["Retorno total"]),
        tooltip="Variação acumulada entre o primeiro e o último valor do período."
    )
with col2:
    render_metric_card(
        title="Retorno Médio / Período", 
        value=format_colored_pct(metrics["Retorno médio"]),
        tooltip="Média aritmética dos retornos simples na frequência selecionada."
    )
with col3:
    render_metric_card(
        title="Volatilidade Anualizada", 
        value=f"<span style='color: #475569;'>{format_percentage(metrics['Volatilidade'])}</span>",
        tooltip="Dispersão anualizada dos retornos; valores maiores indicam maior variação histórica e risco."
    )
with col4:
    render_metric_card(
        title="Índice de Sharpe", 
        value=f"<span style='color: #0f172a;'>{str_sharpe}</span>",
        tooltip="Relação anualizada entre o retorno excedente (acima da taxa livre de risco) e a volatilidade."
    )

st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

# Segunda Linha de Cards com Tooltips embutidos
col5, col6, col7, col8 = st.columns(4)

with col5:
    render_metric_card(
        title="Melhor Período", 
        value=format_colored_pct(best_period_val),
        tooltip="O maior ganho registrado em um único período."
    )
with col6:
    render_metric_card(
        title="Pior Período", 
        value=format_colored_pct(worst_period_val),
        tooltip="A maior perda registrada em um único período."
    )
with col7:
    render_metric_card(
        title="Períodos Positivos", 
        value=f"<span style='color: #166534;'>{format_percentage(metrics['Percentual positivo'])}</span>",
        tooltip="Proporção de períodos que registraram ganho (retorno simples superior a zero)."
    )
with col8:
    render_metric_card(
        title="Drawdown Máximo", 
        value=format_colored_pct(metrics["Drawdown máximo"]),
        tooltip="A maior queda percentual registrada a partir de um topo histórico anterior no período analisado."
    )
    
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
        config={"displayModeBar": False},
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

# Injeção do Marcador de Max Drawdown
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
        config={"displayModeBar": False},
    )


# =====================
# Distribuição
# =====================
st.header("📊 Distribuição de Retornos")

# Criação manual do histograma avançado (substituindo a função genérica)
rets = df_risk["Simple_Return"].dropna() * 100
if not rets.empty:
    
    # 1. Definir os intervalos fixos exigidos
    bins = [-np.inf, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, np.inf]
    x_labels = [
        "Abaixo de<br>-30%", "-30 a<br>-25%", "-25 a<br>-20%", "-20 a<br>-15%",
        "-15 a<br>-10%", "-10 a<br>-5%", "-5 a<br>0%", "0 a<br>5%",
        "5 a<br>10%", "10 a<br>15%", "15 a<br>20%", "20 a<br>25%",
        "25 a<br>30%", "Acima de<br>30%"
    ]
    
    # 2. Categorizar os retornos usando pd.cut
    categorized = pd.cut(rets, bins=bins, labels=x_labels, right=True)
    counts = categorized.value_counts(sort=False)
    
    # 3. Montar o gráfico
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
    
    # Remover o eixo Y completamente (títulos e valores) e alinhar margens
    histogram_figure.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, title_text="")
    
    with st.container(border=True):
        st.plotly_chart(
            histogram_figure,
            use_container_width=True,
            config={"displayModeBar": False},
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

render_html_table(
    dataframe=df_risk,
    columns=display_columns,
    prefix="argos-risk",
    is_details=False
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