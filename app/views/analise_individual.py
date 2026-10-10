import os
import sys
from datetime import datetime


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

from app.ui.asset_cards import render_asset_hero_logo
from app.ui.data_info import (
    render_availability_messages,
    render_catalog_notice,
    render_data_availability,
)
from app.ui.disclaimers import render_footer_disclaimer
from app.ui.education import render_glossary, render_what_it_means
from app.ui.metric_card import render_metric_card
from app.ui.sidebar import render_asset_controls
from app.ui.state import initialize_asset_state
from app.ui.tables import (
    date_cell,
    number_cell,
    percent_cell,
    render_table,
)
from core.analyzer import (
    ORDERED_MONTHS,
    calculate_percentage_change,
    calculate_statistics,
    create_monthly_return_matrix,
)
from core.assets import ASSETS
from core.currency import currency_info
from core.data_availability import assess_availability
from core.data_loader import download_active_data, validate_data
from core.data_processor import (
    aggregate_by_frequency,
    prepare_dataframe,
    select_primary_variable,
)
from core.seasonality import (
    SEASONALITY_METHOD_TEXT,
    SEASONALITY_WINDOW_NOTE,
    exclude_month_in_progress,
    filter_monthly_matrix,
    seasonal_summary,
    window_returns,
    window_summary,
)
from core.exports import csv_filename, dataframe_to_csv_bytes
from core.formatters import format_number_br
from core.returns_utils import simple_returns


st.set_page_config(
    page_title="Argos DataLab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# Configuração padrão da modebar do Plotly (zoom, pan, download, etc.)
# ==========================================================
PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
}

# Fator de anualização da volatilidade calculada sobre retornos DIÁRIOS
# (convenção do projeto: 252 dias de negociação por ano).
DAILY_ANNUALIZATION_FACTOR = 252


initialize_asset_state()


st.title("📊 Análise Individual")

st.markdown(
    "<p style='font-size: 1.1rem; color: #475569; margin-bottom: 2rem;'>"
    "Explore para entender a fundo o comportamento histórico e estatístico de um único ativo selecionado no sistema.<br>"
    "</p>",
    unsafe_allow_html=True
)


# ==========================================================
# Funções de Formatação e Componentes Visuais
# ==========================================================
def format_brazilian_integer(value) -> str:
    """Formata um número inteiro com ponto de milhar."""
    if value is None or pd.isna(value):
        return "—"
    try:
        numeric_value = int(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{numeric_value:,}".replace(",", ".")


def render_custom_metric_card(title: str, value: str) -> None:
    """Card de métrica (componente comum), aceitando HTML no value."""
    render_metric_card(title, value, value_size="2rem")


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
                f"Não foi possível carregar dados para o ativo '{symbol}'. "
                "Confira o código do ativo (ações brasileiras terminam em .SA) "
                "e o período, ou tente novamente em instantes."
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
        # Desvio-padrão dos retornos diários de cada mês, anualizado com
        # √252 (convenção do projeto, ver docs/metodologia_de_calculo.md, seção 2).
        # -----------------------------------------------------------------
        df_vol = df_prepared[['Date', 'Close']].copy()
        df_vol['Date'] = pd.to_datetime(df_vol['Date'])

        df_vol['Daily_Return'] = simple_returns(df_vol['Close'])
        df_vol['YearMonth'] = df_vol['Date'].dt.to_period('M')

        monthly_std = df_vol.groupby('YearMonth')['Daily_Return'].std()
        monthly_vol_annualized = (
            monthly_std * np.sqrt(DAILY_ANNUALIZATION_FACTOR) * 100
        )

        df_monthly_vol = monthly_vol_annualized.reset_index()
        df_monthly_vol.columns = ['Date', 'Volatility']
        df_monthly_vol['Date'] = df_monthly_vol['Date'].dt.to_timestamp()
        df_monthly_vol = df_monthly_vol.dropna()
        # -----------------------------------------------------------------

        df_aggregated = aggregate_by_frequency(df_prepared, frequency)
        df_primary = select_primary_variable(df_aggregated, "Close")

        # -----------------------------------------------------------------
        # DISPONIBILIDADE: período solicitado x período efetivamente disponível
        # -----------------------------------------------------------------
        availability = assess_availability(
            dates=df_prepared["Date"],
            requested_start=start_date,
            requested_end=end_date,
            period_observations=len(df_primary),
        )

        if availability.insufficient:
            st.session_state["asset_loaded"] = False
            st.session_state["asset_query"] = None
            render_availability_messages(availability)
            st.stop()

        df_with_change = calculate_percentage_change(df_primary, "Value")
        stats = calculate_statistics(df_with_change, "Value")

        st.session_state["asset_df"] = df_with_change
        st.session_state["asset_stats"] = stats
        st.session_state["asset_validation"] = validation
        st.session_state["asset_monthly_vol"] = df_monthly_vol
        st.session_state["asset_availability"] = availability
        st.session_state["asset_fetched_at"] = datetime.now()


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


# =====================
# Card visual do ativo (logo em destaque) lado a lado com o
# expander de detalhes da análise, na mesma fileira.
# =====================
current_asset = next((a for a in ASSETS if a["ticker"] == symbol), None)

# Ativos digitados fora do catálogo usam um registro mínimo
logo_asset = current_asset or {
    "ticker": symbol,
    "name": symbol,
    "group": "",
    "icon": "📊",
}

col_logo, col_expander = st.columns([1, 3], vertical_alignment="center")

with col_logo:
    render_asset_hero_logo(logo_asset)

with col_expander:
    with st.expander(f"✅ Análise gerada para {symbol}. Clique para visualizar detalhes e qualidade dos dados.", expanded=False):
        st.markdown(f"**Ativo Analisado:** {symbol}")
        st.markdown(f"**Período Selecionado:** {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')} | **Frequência:** {frequency}")
        st.markdown(f"**Observações Processadas:** {len(df)} períodos.")

        st.markdown("#### Qualidade e Validação dos Dados")
        st.markdown(f"- **Total de linhas brutas:** {validation['total_rows']}")
        st.markdown(f"- **Datas duplicadas:** {validation['duplicate_dates']}")
        st.markdown(f"- **Valores negativos (Fechamento):** {validation['negative_close']}")

        missing = validation["missing_values"]
        if isinstance(missing, (pd.Series, dict)):
            missing_str = ", ".join(
                [f"{idx}: {val}" for idx, val in dict(missing).items() if val > 0]
            )
            if not missing_str:
                missing_str = "Nenhum"
        else:
            missing_str = str(missing)
        st.markdown(f"- **Valores ausentes:** {missing_str}")

st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)


# =====================
# Disponibilidade dos dados: solicitado x disponível, fonte e consulta
# =====================
availability = st.session_state.get("asset_availability")
if availability is not None:
    render_data_availability(
        availability,
        st.session_state.get("asset_fetched_at"),
    )

st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)


# =====================
# Seção 1: Resumo
# =====================
st.header("📊 Visão Geral do Ativo")

col1, col2, col3, col4 = st.columns(4)

currency = currency_info(symbol)
prefix_currency = currency.prefix
value_suffix = "%" if currency.kind == "rate" else ""

with col1:
    render_custom_metric_card(
        "Primeiro Valor",
        f"<span style='font-size: 1.2rem; color: #64748b; font-weight: 600;'>{prefix_currency}</span>{format_number_br(stats['first_value'])}{value_suffix}"
    )

with col2:
    render_custom_metric_card(
        "Último Valor",
        f"<span style='font-size: 1.2rem; color: #64748b; font-weight: 600;'>{prefix_currency}</span>{format_number_br(stats['last_value'])}{value_suffix}"
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

st.caption(f"Unidade de cotação: {currency.label}.")

if currency.kind == "rate":
    st.caption(
        "Este ativo é uma taxa de juros: o \"Retorno Total\" mede a variação do "
        "nível da taxa, e não o retorno de um título."
    )

st.markdown("<br>", unsafe_allow_html=True)


# =====================
# Seção 2: Evolução Temporal
# =====================
value_label = "Taxa" if currency.kind == "rate" else "Preço"

st.markdown("### 📈 Evolução Temporal do Ativo")
st.markdown(
    "<p style='color: #64748b; font-size: 0.95rem; margin-top: -12px; margin-bottom: 24px;'>"
    f"Comportamento histórico de {'nível da taxa' if currency.kind == 'rate' else 'preço de fechamento'} para {symbol}."
    "</p>",
    unsafe_allow_html=True
)

fig_line = go.Figure()
formatted_y = df["Value"].apply(format_number_br)

fig_line.add_trace(go.Scatter(
    x=df["Date"],
    y=df["Value"],
    mode="lines",
    line=dict(color="#10B981", width=2.5),
    fill="tozeroy",
    fillcolor="rgba(16, 185, 129, 0.15)",
    customdata=formatted_y,
    hovertemplate=(
        f"<b>Data:</b> %{{x|%d/%m/%Y}}<br>"
        f"<b>{value_label}:</b> {prefix_currency}%{{customdata}}{value_suffix}"
        "<extra></extra>"
    ),
))

fig_line = apply_custom_layout(fig_line)

with st.container(border=True):
    st.plotly_chart(fig_line, use_container_width=True, config=PLOTLY_CONFIG)


# =====================
# Seção 3: Volatilidade por Mês
# =====================
st.markdown("### 🌪️ Volatilidade Anualizada por Mês")
st.markdown(
    "<p style='color: #64748b; font-size: 0.95rem; margin-top: -12px; margin-bottom: 24px;'>"
    "Volatilidade <b>anualizada</b>: desvio padrão dos retornos diários de cada mês, "
    f"convertido para base anual (fator √{DAILY_ANNUALIZATION_FACTOR}). Barras em destaque "
    "indicam os meses com maiores picos de volatilidade histórica."
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
            hovertemplate="<b>Mês:</b> %{x|%m/%Y}<br><b>Volatilidade anualizada:</b> %{customdata}<extra></extra>"
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
        st.plotly_chart(fig_vol, use_container_width=True, config=PLOTLY_CONFIG)

    if currency.kind == "rate":
        st.caption(
            "Para taxas de juros, a volatilidade descreve a oscilação da variação "
            "percentual do nível da taxa."
        )

    render_what_it_means("volatilidade")


# =====================
# Seção 4: Variação Percentual
# =====================
st.markdown(f"### 📉 Variação Percentual — {frequency}")
st.markdown(
    "<p style='color: #64748b; font-size: 0.95rem; margin-top: -12px; margin-bottom: 24px;'>"
    "Retorno de <b>cada período</b> em relação ao período anterior (não é a valorização "
    "acumulada desde o início, que aparece no card \"Retorno Total\")."
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
    st.plotly_chart(fig_bar, use_container_width=True, config=PLOTLY_CONFIG)


# =====================
# Seção 5: Matriz Anual x Mensal
# =====================
st.markdown("### 🗓️ Padrões Sazonais")
st.markdown(
    "<p style='color: #64748b; font-size: 0.95rem; margin-top: -12px; margin-bottom: 24px;'>"
    "Cada célula mostra a variação percentual de um mês de um ano específico "
    "(retorno mensal, não acumulado), calculada pelo último fechamento de cada mês, "
    "independentemente da frequência escolhida. Verde indica variação positiva e vermelho, negativa; "
    "células vazias indicam meses sem dados, o mês seguinte a uma lacuna e o primeiro mês da série "
    "(que não tem mês anterior para comparação)."
    "</p>",
    unsafe_allow_html=True
)

df_matrix = create_monthly_return_matrix(df, "Value")

if df_matrix.empty or df_matrix.isna().all().all():
    st.info(
        "O período selecionado não tem meses suficientes para calcular a variação mensal. "
        "Escolha um período mais longo para ver os padrões sazonais."
    )
else:
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
        st.plotly_chart(fig_heatmap, use_container_width=True, config=PLOTLY_CONFIG)

    render_what_it_means("sazonalidade")

    df_matrix_stats = exclude_month_in_progress(df_matrix)
    monthly_avg = df_matrix_stats.mean(axis=0)
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
        st.plotly_chart(fig_bar_season, use_container_width=True, config=PLOTLY_CONFIG)

    st.caption(
        "A média por mês do calendário usa poucos anos de histórico; amostras curtas "
        "geram médias instáveis, e padrões passados não garantem repetição futura."
    )

    if df_matrix.notna().sum().sum() != df_matrix_stats.notna().sum().sum():
        st.caption(
            "O mês em andamento aparece no mapa de calor, mas não entra nas médias, "
            "porque ainda não está completo."
        )

    # -------------------------------------------------------
    # Recorte por anos e meses (Plano 2, Bloco 2)
    # -------------------------------------------------------
    def _fmt_pct(value, signed=False):
        if value is None or pd.isna(value):
            return "—"
        text = f"{value:+.2f}" if signed else f"{value:.2f}"
        return text.replace(".", ",") + "%"

    def _fmt_pp(value):
        if value is None or pd.isna(value):
            return "—"
        return f"{value:+.2f}".replace(".", ",") + " p.p."

    st.markdown("#### 🔎 Recorte por anos e meses")
    st.caption(SEASONALITY_METHOD_TEXT)

    available_years = sorted(int(year) for year in df_matrix_stats.index)
    available_months = list(df_matrix_stats.columns)

    with st.form("season_filter_form"):
        col_years, col_months = st.columns(2)
        with col_years:
            selected_years = st.multiselect(
                "Anos do recorte",
                options=available_years,
                default=[],
                help="Compara o(s) ano(s) escolhido(s) com a média de todos os anos.",
            )
        with col_months:
            selected_months = st.multiselect(
                "Meses (opcional)",
                options=available_months,
                default=[],
                help="Sem seleção, todos os meses são exibidos.",
            )

        col_entry, col_exit = st.columns(2)
        with col_entry:
            entry_choice = st.selectbox(
                "Janela: mês de entrada (opcional)",
                options=["—"] + ORDERED_MONTHS,
            )
        with col_exit:
            exit_choice = st.selectbox(
                "Janela: mês de saída (opcional)",
                options=["—"] + ORDERED_MONTHS,
            )

        apply_clicked = st.form_submit_button("Aplicar filtro")

    if apply_clicked:
        if (entry_choice == "—") != (exit_choice == "—"):
            st.warning("Para usar a janela, escolha o mês de entrada e o mês de saída.")
            st.session_state["season_filter"] = None
        elif entry_choice != "—" and entry_choice == exit_choice:
            st.warning("Os meses de entrada e de saída devem ser diferentes.")
            st.session_state["season_filter"] = None
        elif not selected_years and entry_choice == "—":
            st.warning("Escolha ao menos um ano ou uma janela de entrada e saída.")
            st.session_state["season_filter"] = None
        else:
            st.session_state["season_filter"] = {
                "symbol": symbol,
                "years": list(selected_years),
                "months": list(selected_months),
                "entry": entry_choice,
                "exit": exit_choice,
            }

    applied_filter = st.session_state.get("season_filter")

    if applied_filter and applied_filter.get("symbol") == symbol:
        years_cut = [y for y in applied_filter["years"] if y in available_years]
        months_cut = applied_filter["months"] or None

        if years_cut:
            base_matrix = filter_monthly_matrix(df_matrix_stats, months=months_cut)
            summary = seasonal_summary(base_matrix, years=years_cut)
            years_label = ", ".join(str(y) for y in years_cut)

            fig_cut = go.Figure()
            fig_cut.add_trace(
                go.Bar(
                    x=summary.index,
                    y=summary["Média geral"],
                    name="Média de todos os anos",
                    marker_color="#94a3b8",
                    customdata=[
                        [_fmt_pct(v), int(n)]
                        for v, n in zip(summary["Média geral"], summary["N geral"])
                    ],
                    hovertemplate="Mês: %{x}<br>Média geral: %{customdata[0]}"
                    "<br>Anos com dado: %{customdata[1]}<extra></extra>",
                )
            )
            fig_cut.add_trace(
                go.Bar(
                    x=summary.index,
                    y=summary["Média do recorte"],
                    name=f"Média do recorte ({years_label})",
                    marker_color="#3b82f6",
                    customdata=[
                        [_fmt_pct(v), int(n)]
                        for v, n in zip(summary["Média do recorte"], summary["N do recorte"])
                    ],
                    hovertemplate="Mês: %{x}<br>Média do recorte: %{customdata[0]}"
                    "<br>Anos com dado: %{customdata[1]}<extra></extra>",
                )
            )
            fig_cut = apply_custom_layout(fig_cut)
            fig_cut.update_layout(
                barmode="group",
                margin=dict(l=40, r=20, t=40, b=20),
                xaxis_title=None,
                yaxis_title="Variação mensal (%)",
                legend=dict(orientation="h", y=1.12),
            )

            with st.container(border=True):
                st.markdown(
                    "<h5 style='text-align: center; color: #334155; margin-bottom: 10px; font-size: 1rem;'>"
                    "Média de todos os anos × média do recorte</h5>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(fig_cut, use_container_width=True, config=PLOTLY_CONFIG)

            summary_table = pd.DataFrame(
                {
                    "Mês": summary.index,
                    "Média de todos os anos": summary["Média geral"].map(_fmt_pct).values,
                    "Média do recorte": summary["Média do recorte"].map(_fmt_pct).values,
                    "Diferença": summary["Diferença (p.p.)"].map(_fmt_pp).values,
                    "Mediana do recorte": summary["Mediana do recorte"].map(_fmt_pct).values,
                    "Anos positivos no recorte": summary["Anos positivos recorte (%)"]
                    .map(lambda v: "—" if pd.isna(v) else f"{v:.0f}%")
                    .values,
                    "Anos (todos)": summary["N geral"].astype(int).values,
                    "Anos (recorte)": summary["N do recorte"].astype(int).values,
                }
            )
            st.dataframe(summary_table, hide_index=True, use_container_width=True)

            if (summary["N do recorte"] < 3).any():
                st.caption(
                    "Alguns meses têm menos de 3 anos no recorte. Médias e medianas "
                    "calculadas com tão poucos anos variam bastante de uma amostra para outra."
                )

        if applied_filter["entry"] != "—":
            entry_name, exit_name = applied_filter["entry"], applied_filter["exit"]
            window_all = window_returns(df, entry_name, exit_name, value_col="Value")
            window_cut = (
                window_returns(df, entry_name, exit_name, years=years_cut, value_col="Value")
                if years_cut
                else window_all
            )
            stats_all = window_summary(window_all)
            stats_cut = window_summary(window_cut)

            st.markdown(f"##### Janela: fechamento de {entry_name} → fechamento de {exit_name}")
            st.caption(SEASONALITY_WINDOW_NOTE)

            if window_all.empty:
                st.info(
                    "Nenhum ano tem os dois fechamentos disponíveis para essa janela "
                    "no período selecionado."
                )
            else:
                metric_cols = st.columns(4)
                metric_cols[0].metric("Média de todos os anos", _fmt_pct(stats_all["Média"]))
                metric_cols[1].metric("Mediana de todos os anos", _fmt_pct(stats_all["Mediana"]))
                metric_cols[2].metric(
                    "Anos com retorno positivo",
                    "—" if pd.isna(stats_all["Anos positivos (%)"])
                    else f"{stats_all['Anos positivos (%)']:.0f}%",
                )
                metric_cols[3].metric("Anos com dado (N)", stats_all["N"])

                if years_cut:
                    st.caption(
                        f"Recorte ({', '.join(str(y) for y in years_cut)}): média "
                        f"{_fmt_pct(stats_cut['Média'])}, mediana {_fmt_pct(stats_cut['Mediana'])}, "
                        f"N = {stats_cut['N']}."
                    )

                bar_years = window_all["Ano"].astype(str)
                highlight = set(years_cut)
                fig_window = go.Figure(
                    data=go.Bar(
                        x=bar_years,
                        y=window_all["Retorno (%)"],
                        marker_color=[
                            "#3b82f6" if int(year) in highlight else "#94a3b8"
                            for year in window_all["Ano"]
                        ],
                        customdata=[_fmt_pct(v) for v in window_all["Retorno (%)"]],
                        hovertemplate="Ano de entrada: %{x}<br>Retorno da janela: %{customdata}<extra></extra>",
                    )
                )
                if pd.notna(stats_all["Média"]):
                    fig_window.add_hline(
                        y=stats_all["Média"],
                        line_dash="dash",
                        line_color="#475569",
                        annotation_text=f"Média: {_fmt_pct(stats_all['Média'])}",
                    )
                fig_window = apply_custom_layout(fig_window)
                fig_window.update_layout(
                    margin=dict(l=40, r=20, t=40, b=20),
                    xaxis_title="Ano de entrada",
                    yaxis_title="Retorno da janela (%)",
                )

                with st.container(border=True):
                    st.plotly_chart(fig_window, use_container_width=True, config=PLOTLY_CONFIG)

                shown = window_cut if years_cut else window_all
                window_table = pd.DataFrame(
                    {
                        "Ano de entrada": shown["Ano"].astype(int).values,
                        "Fechamento de entrada": shown["Fechamento de entrada"].map(
                            lambda v: f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        ).values,
                        "Fechamento de saída": shown["Fechamento de saída"].map(
                            lambda v: f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        ).values,
                        "Retorno da janela": shown["Retorno (%)"].map(_fmt_pct).values,
                        "Diferença para a média": (
                            shown["Retorno (%)"] - stats_all["Média"]
                        ).map(_fmt_pp).values,
                    }
                )
                st.dataframe(window_table, hide_index=True, use_container_width=True)


# =====================
# Seção 6: Tabela de Dados
# =====================
st.header("📋 Dados Processados")

df_display = df.rename(columns={"Value": "Close"}).copy()
display_columns = ["Date", "Open", "High", "Low", "Close", "Pct_Change"]
available_columns = [col for col in display_columns if col in df_display.columns]

render_table(
    df_display,
    available_columns,
    {
        "Date": date_cell,
        "Open": number_cell,
        "High": number_cell,
        "Low": number_cell,
        "Close": number_cell,
        "Pct_Change": percent_cell(fraction=False, colored=True),
    },
    max_height=450,
)


# =====================
# Download
# =====================
st.download_button(
    label="⬇️ Baixar CSV",
    data=dataframe_to_csv_bytes(df),
    file_name=csv_filename(symbol, "dados_tratados"),
    mime="text/csv",
)


# =====================
# Glossário, catálogo e rodapé
# =====================
st.markdown("<br>", unsafe_allow_html=True)

render_glossary(["retorno", "volatilidade", "sazonalidade"])

render_catalog_notice()

render_footer_disclaimer()