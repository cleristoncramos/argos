import os
import sys
from datetime import datetime
from html import escape

# ==========================================================
# Correção de Caminho para Páginas Multi-página do Streamlit
# ==========================================================
PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
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


st.set_page_config(
    page_title="Argos DataLab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


initialize_asset_state()


st.title("📊 Argos DataLab")

st.markdown(
    "<p style='font-size: 1.1rem; color: #475569; margin-bottom: 2rem;'>"
    "Inteligência de Dados para Apoio à Decisão no Mercado Financeiro.<br>"
    "<b>Projeto PIBITI UFPI 2026–2027</b> · Orientador: Prof. Arlino Henrique Magalhães de Araújo"
    "</p>",
    unsafe_allow_html=True
)


# ==========================================================
# Funções de Formatação e Componentes Visuais
# ==========================================================
def format_brazilian_number(value) -> str:
    """Formata um número com ponto de milhar e vírgula decimal."""
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

def format_brazilian_integer(value) -> str:
    """Formata um número inteiro com ponto de milhar."""
    if value is None or pd.isna(value):
        return "—"
    try:
        numeric_value = int(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{numeric_value:,}".replace(",", ".")

def get_currency_prefix(ticker: str) -> str:
    """Retorna o prefixo da moeda correto com base na regra do Ticker."""
    if ticker.endswith(".SA"):
        return "R$ "
    elif ticker.endswith("=X"):
        return "" 
    elif ticker.startswith("^") or ticker.endswith(".SS"):
        return "Pts " 
    else:
        return "US$ "


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
            border-bottom: 3px solid #97b7c4; /* Borda customizada solicitada */
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


def render_html_table(dataframe: pd.DataFrame, columns: list, prefix: str) -> None:
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
            
            if column == "Date":
                date_val = pd.to_datetime(raw_val, errors="coerce")
                formatted_val = "—" if pd.isna(date_val) else date_val.strftime("%d/%m/%Y")
                cell_style = "text-align:center;white-space:nowrap;"
            elif column in ["Open", "High", "Low", "Close", "Value"]:
                formatted_val = format_brazilian_number(raw_val)
                cell_style = "text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;"
            elif column == "Pct_Change":
                if pd.isna(raw_val):
                    formatted_val = "—"
                    color = ""
                else:
                    formatted_val = f"{float(raw_val):,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
                    color = "color:#166534;font-weight:600;" if float(raw_val) > 0 else "color:#991b1b;font-weight:600;" if float(raw_val) < 0 else ""
                cell_style = f"text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;{color}"
            else:
                formatted_val = str(raw_val) if pd.notna(raw_val) else "—"
                cell_style = "text-align:right;white-space:nowrap;"

            cells_html.append(f'<td style="{cell_style}">{escape(str(formatted_val))}</td>')

        row_class = f"{prefix}-row-even" if position % 2 == 0 else f"{prefix}-row-odd"
        rows_html.append(f'<tr class="{row_class}">{"".join(cells_html)}</tr>')

    table_html = (
        build_table_styles(prefix)
        + f'<div class="{prefix}-wrapper" style="max-height: 450px; overflow-y: auto;">'
        + f'<table class="{prefix}-table">'
        + f"<thead><tr>{header_html}</tr></thead>"
        + f"<tbody>{''.join(rows_html)}</tbody>"
        + "</table>"
        + "</div>"
    )
    
    st.markdown(table_html, unsafe_allow_html=True)


def render_custom_metric_card(title: str, value: str) -> None:
    """Renderiza um card com design refinado, aceitando HTML no value."""
    html = f"""
    <div style="background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); border: 1px solid #e2e8f0; border-radius: 16px; padding: 24px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05), 0 4px 6px -2px rgba(0,0,0,0.025); display: flex; flex-direction: column; height: 100%; transition: all 0.3s ease;">
        <div style="color: #64748b; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
            {title}
        </div>
        <div style="color: #0f172a; font-size: 2rem; font-weight: 800; margin-bottom: 0px; font-family: 'Inter', sans-serif; letter-spacing: -0.5px;">
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
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        font=dict(family="Inter, Arial, sans-serif", color="#334155")
    )
    return fig


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
# Carregamento de dados e Cálculos
# =====================
if load_data:
    if start_date >= end_date:
        st.sidebar.error("A data inicial deve ser anterior à data final.")
        st.stop()

    if not symbol:
        st.sidebar.error("Informe um símbolo de ativo antes de carregar os dados.")
        st.stop()

    st.session_state["asset_loaded"] = True
    st.session_state["asset_query"] = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
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

        # -----------------------------------------------------------------
        # CÁLCULO DA VOLATILIDADE MENSAL ANUALIZADA
        # -----------------------------------------------------------------
        df_vol = df_prepared[['Date', 'Close']].copy()
        df_vol['Date'] = pd.to_datetime(df_vol['Date'])
        
        df_vol['Daily_Return'] = df_vol['Close'].pct_change()
        df_vol['YearMonth'] = df_vol['Date'].dt.to_period('M')
        
        monthly_std = df_vol.groupby('YearMonth')['Daily_Return'].std()
        monthly_vol_annualized = monthly_std * np.sqrt(365) * 100
        
        df_monthly_vol = monthly_vol_annualized.reset_index()
        df_monthly_vol.columns = ['Date', 'Volatility']
        df_monthly_vol['Date'] = df_monthly_vol['Date'].dt.to_timestamp()
        df_monthly_vol = df_monthly_vol.dropna()
        # -----------------------------------------------------------------

        df_aggregated = aggregate_by_frequency(df_prepared, frequency)
        df_primary = select_primary_variable(df_aggregated, "Close")
        df_with_change = calculate_percentage_change(df_primary, "Value")
        stats = calculate_statistics(df_with_change, "Value")

        st.session_state["asset_df"] = df_with_change
        st.session_state["asset_stats"] = stats
        st.session_state["asset_validation"] = validation
        st.session_state["asset_monthly_vol"] = df_monthly_vol


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
        "👈 Selecione a classe e o ativo na barra lateral e clique em "
        "**Carregar Dados**."
    )
    st.stop()


df = st.session_state["asset_df"]
stats = st.session_state["asset_stats"]
validation = st.session_state["asset_validation"]
df_monthly_vol = st.session_state.get("asset_monthly_vol")

symbol = query["symbol"]
start_date = query["start_date"]
end_date = query["end_date"]
frequency = query["frequency"]


# Expander para informações de contexto e processamento de qualidade
with st.expander(f"✅ Análise gerada para {symbol}. Clique para visualizar detalhes e qualidade dos dados.", expanded=False):
    st.markdown(f"**Ativo Analisado:** {symbol}")
    st.markdown(f"**Período Selecionado:** {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')} | **Frequência:** {frequency}")
    st.markdown(f"**Observações Processadas:** {len(df)} períodos.")
    
    st.markdown("#### Qualidade e Validação dos Dados")
    st.markdown(f"- **Total de linhas brutas:** {validation['total_rows']}")
    st.markdown(f"- **Datas duplicadas:** {validation['duplicate_dates']}")
    st.markdown(f"- **Valores negativos (Fechamento):** {validation['negative_close']}")
    
    missing = validation["missing_values"]
    if isinstance(missing, pd.Series):
        missing_str = ", ".join([f"{idx}: {val}" for idx, val in missing.items() if val > 0])
        if not missing_str: 
            missing_str = "Nenhum"
    else:
        missing_str = str(missing)
    st.markdown(f"- **Valores ausentes:** {missing_str}")


# =====================
# Seção 1: Resumo
# =====================
st.header("📊 Visão Geral do Ativo")

col1, col2, col3, col4 = st.columns(4)

prefix_currency = get_currency_prefix(symbol)

with col1:
    render_custom_metric_card(
        "Primeiro Valor", 
        f"<span style='font-size: 1.2rem; color: #64748b; font-weight: 600;'>{prefix_currency}</span>{format_brazilian_number(stats['first_value'])}"
    )

with col2:
    render_custom_metric_card(
        "Último Valor", 
        f"<span style='font-size: 1.2rem; color: #64748b; font-weight: 600;'>{prefix_currency}</span>{format_brazilian_number(stats['last_value'])}"
    )

with col3:
    total_return = stats["total_return"]
    return_str = f"{total_return:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    if total_return > 0:
        return_str = f"+{return_str}"
        
    color = "#166534" if total_return > 0 else "#991b1b" if total_return < 0 else "#0f172a"
    colored_value = f"<span style='color: {color};'>{return_str}</span>"
    
    render_custom_metric_card("Retorno Total", colored_value)

with col4:
    freq_label = "dias" if frequency == "Diário" else "semanas" if frequency == "Semanal" else "meses"
    count_formatted = format_brazilian_integer(stats["count"])
    render_custom_metric_card(
        "Períodos Analisados", 
        f"{count_formatted} <span style='font-size: 1rem; color: #64748b; font-weight: 500;'>{freq_label}</span>"
    )

st.markdown("<br>", unsafe_allow_html=True)


# =====================
# Seção 2: Evolução Temporal
# =====================
st.markdown("### 📈 Evolução Temporal do Ativo")
st.markdown(
    "<p style='color: #64748b; font-size: 0.95rem; margin-top: -12px; margin-bottom: 24px;'>"
    f"Comportamento histórico do preço de fechamento para {symbol}."
    "</p>",
    unsafe_allow_html=True
)

fig_line = go.Figure()
formatted_y = df["Value"].apply(format_brazilian_number)

fig_line.add_trace(go.Scatter(
    x=df["Date"],
    y=df["Value"],
    mode="lines",
    line=dict(color="#10B981", width=2.5), 
    fill="tozeroy",
    fillcolor="rgba(16, 185, 129, 0.15)",  
    customdata=formatted_y,
    hovertemplate=f"<b>Data:</b> %{{x|%d/%m/%Y}}<br><b>Preço:</b> {prefix_currency}%{{customdata}}<extra></extra>"
))

fig_line = apply_custom_layout(fig_line)

with st.container(border=True):
    st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})


# =====================
# Seção 3: Volatilidade por Mês
# =====================
st.markdown("### 🌪️ Volatilidade por Mês")
st.markdown(
    "<p style='color: #64748b; font-size: 0.95rem; margin-top: -12px; margin-bottom: 24px;'>"
    "Desvio padrão dos retornos diários, anualizado — barras em destaque indicam os meses com maiores picos de volatilidade histórica."
    "</p>",
    unsafe_allow_html=True
)

if df_monthly_vol is not None and not df_monthly_vol.empty:
    threshold = df_monthly_vol['Volatility'].quantile(0.95)
    colors = ["#F59E0B" if val >= threshold else "#10B981" for val in df_monthly_vol['Volatility']]
    
    formatted_vol = df_monthly_vol['Volatility'].apply(lambda x: f"{x:,.2f}%".replace(",", "X").replace(".", ",").replace("X", "."))
    
    fig_vol = go.Figure(
        data=go.Bar(
            x=df_monthly_vol['Date'],
            y=df_monthly_vol['Volatility'],
            marker_color=colors,
            customdata=formatted_vol,
            hovertemplate="<b>Mês:</b> %{x|%m/%Y}<br><b>Volatilidade:</b> %{customdata}<extra></extra>"
        )
    )
    
    fig_vol = apply_custom_layout(fig_vol)
    fig_vol.update_layout(
        margin=dict(l=10, r=20, t=20, b=20),
        xaxis_title=None,
        yaxis_title=None,
        yaxis_ticksuffix="%"
    )
    
    with st.container(border=True):
        st.plotly_chart(fig_vol, use_container_width=True, config={"displayModeBar": False})


# =====================
# Seção 4: Variação Percentual
# =====================
st.markdown(f"### 📉 Variação Percentual — {frequency}")
st.markdown(
    "<p style='color: #64748b; font-size: 0.95rem; margin-top: -12px; margin-bottom: 24px;'>"
    f"Distribuição das variações percentuais período a período."
    "</p>",
    unsafe_allow_html=True
)

df_chart = df.dropna(subset=["Pct_Change"]).copy()
fig_bar = px.bar(
    df_chart, x="Date", y="Pct_Change", color="Pct_Change", 
    color_continuous_scale="RdYlGn", template="plotly_white"
)
fig_bar = apply_custom_layout(fig_bar)
fig_bar.update_layout(coloraxis_showscale=False)

formatted_pct = df_chart["Pct_Change"].apply(lambda x: f"{x:,.2f}%".replace(",", "X").replace(".", ",").replace("X", "."))
fig_bar.update_traces(
    customdata=formatted_pct,
    hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Variação:</b> %{customdata}<extra></extra>",
    marker_line_width=0
)

with st.container(border=True):
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})


# =====================
# Seção 5: Matriz Anual x Mensal
# =====================
st.markdown("### 🗓️ Padrões Sazonais")
st.markdown(
    "<p style='color: #64748b; font-size: 0.95rem; margin-top: -12px; margin-bottom: 24px;'>"
    "Mapeamento da variação percentual média agregada por mês e ano."
    "</p>",
    unsafe_allow_html=True
)

df_matrix = create_year_month_matrix(df, "Pct_Change")

text_matrix = df_matrix.apply(
    lambda column: column.map(
        lambda value: (
            f"{value:.2f}%".replace(".", ",") if pd.notna(value) else ""
        )
    )
)

fig_heatmap = go.Figure(
    data=go.Heatmap(
        z=df_matrix.values,
        x=df_matrix.columns,
        y=df_matrix.index,
        colorscale=[[0.0, "#ef4444"], [0.5, "#ffffff"], [1.0, "#22c55e"]], 
        zmid=0, 
        text=text_matrix.values,
        texttemplate="%{text}",
        textfont={"size": 12, "color": "#1e293b", "family": "Inter, Arial"},
        customdata=text_matrix.values,
        hoverongaps=False,
        hovertemplate="Ano: %{y}<br>Mês: %{x}<br>Variação: %{customdata}<extra></extra>",
        showscale=False,
        xgap=3,
        ygap=3,
    )
)

fig_heatmap = apply_custom_layout(fig_heatmap)
fig_heatmap.update_layout(margin=dict(l=40, r=20, t=20, b=40))
fig_heatmap.update_yaxes(autorange="reversed")

with st.container(border=True):
    st.markdown("<h5 style='text-align: center; color: #334155; margin-bottom: 10px; font-size: 1rem;'>Variação Mensal Histórica</h5>", unsafe_allow_html=True)
    st.plotly_chart(fig_heatmap, use_container_width=True, config={"displayModeBar": False})

monthly_avg = df_matrix.mean(axis=0)
bar_colors = ["#22c55e" if val >= 0 else "#ef4444" for val in monthly_avg]
text_avg = [f"{val:.2f}%".replace(".", ",") if pd.notna(val) else "" for val in monthly_avg]

fig_bar_season = go.Figure(
    data=go.Bar(
        x=monthly_avg.index,
        y=monthly_avg.values,
        marker_color=bar_colors,
        text=text_avg,
        textposition="outside",
        textfont=dict(size=12, color="#475569", family="Inter, Arial"),
        hovertemplate="Mês: %{x}<br>Média: %{text}<extra></extra>"
    )
)

fig_bar_season = apply_custom_layout(fig_bar_season)
fig_bar_season.update_layout(
    margin=dict(l=40, r=20, t=40, b=20),
    xaxis_title=None,
    yaxis_title="Média de Variação (%)",
)

with st.container(border=True):
    st.markdown("<h5 style='text-align: center; color: #334155; margin-top: 10px; margin-bottom: 10px; font-size: 1rem;'>Média Consolidada por Mês do Calendário</h5>", unsafe_allow_html=True)
    st.plotly_chart(fig_bar_season, use_container_width=True, config={"displayModeBar": False})


# =====================
# Seção 6: Tabela de Dados
# =====================
st.header("📋 Dados Processados")

df_display = df.rename(columns={"Value": "Close"}).copy()
display_columns = ["Date", "Open", "High", "Low", "Close", "Pct_Change"]
available_columns = [col for col in display_columns if col in df_display.columns]

render_html_table(df_display, available_columns, prefix="argos-main")


# =====================
# Download
# =====================
csv_data = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Baixar CSV",
    data=csv_data,
    file_name=f"{symbol}_dados_tratados.csv",
    mime="text/csv",
)

# =====================
# Rodapé
# =====================
st.markdown("---")

st.caption(
    "⚠️ **Aviso:** Esta ferramenta é destinada a fins educacionais "
    "e de pesquisa. Os dados históricos não garantem resultados "
    "futuros. Não constitui recomendação de investimento."
)