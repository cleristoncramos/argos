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

from app.ui.page_header import render_page_header
from app.ui.charts import apply_custom_layout
from app.ui.chart_guide import render_chart_guide
from app.ui.data_info import (
    render_availability_messages,
    render_catalog_notice,
    render_analysis_summary,
)
from app.ui.disclaimers import render_footer_disclaimer
from app.ui.education import render_glossary, render_what_it_means
from app.ui.llm_explain import asset_name, render_explain_section
from app.ui.metric_card import render_metric_card
from app.ui.season_explorer import (
    FULL_MONTH_NAMES,
    PP_NOTE,
    WINDOW_INTRO,
    WINDOW_NOTE,
    YEARS_INTRO,
    center_cell,
    describe_window,
    describe_year_comparison,
    fmt_pct,
    fmt_pp,
    month_label,
    pct_cell,
    pp_cell,
    price_cell,
    share_cell,
    window_label,
    year_comparison_highlights,
    years_label,
)
from app.ui.sidebar import render_asset_controls
from app.ui.state import initialize_asset_state
from app.ui.trailing_table import (
    FORMATTERS as TRAILING_FORMATTERS,
    HEADER_LABELS,
    RATE_NOTE,
    TRAILING_NOTES,
    build_trailing_display,
    trailing_intro,
)
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
from core.config import ANNUALIZATION_FACTORS
from core.currency import currency_info
from core.data_availability import assess_availability
from core.data_quality import assess_data_quality
from app.ui.data_cache import download_active_data
from core.data_loader import validate_data
from core.data_processor import (
    aggregate_by_frequency,
    prepare_dataframe,
    select_primary_variable,
)
from core.seasonality import (
    SEASONALITY_METHOD_TEXT,
    exclude_month_in_progress,
    filter_monthly_matrix,
    monthly_closes,
    seasonal_summary,
    window_returns,
    window_summary,
)
from core.exports import csv_filename, dataframe_to_csv_bytes
from core.formatters import format_number_br
from core.llm_builders import individual_context, window_context
from core.returns_utils import simple_returns
from core.trailing_returns import base_description, trailing_returns


st.set_page_config(
    page_title="Argos",
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


render_page_header(
    "views/analise_individual.py",
    "Comportamento histórico e estatístico de um ativo: preço, retorno, volatilidade mensal e padrões sazonais.",
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


# =====================
# Controles compartilhados
# =====================
asset_params = render_asset_controls(
    title="Configurações",
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
            frequency=frequency,
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
        st.session_state["asset_quality"] = assess_data_quality(df_prepared, symbol, start_date)
        st.session_state["asset_daily"] = df_prepared[["Date", "Close"]].copy()


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
        "👈 Selecione o grupo e o ativo na barra lateral e clique em "
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

missing = validation["missing_values"]
if isinstance(missing, (pd.Series, dict)):
    missing_str = ", ".join(
        [f"{idx}: {val}" for idx, val in dict(missing).items() if val > 0]
    ) or "Nenhum"
else:
    missing_str = str(missing)

render_analysis_summary(
    logo_asset,
    st.session_state.get("asset_availability"),
    st.session_state.get("asset_fetched_at"),
    [
        ("Ativo", symbol),
        ("Frequência", frequency),
        ("Observações processadas", f"{len(df)} períodos"),
        ("Linhas brutas baixadas", str(validation["total_rows"])),
        ("Datas duplicadas", str(validation["duplicate_dates"])),
        ("Fechamentos negativos", str(validation["negative_close"])),
        ("Valores ausentes", missing_str),
    ],
    details_label="Detalhes do processamento e qualidade dos dados",
    quality_alerts=st.session_state.get("asset_quality"),
)

st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)


# =====================
# Seção 1: Resumo
# =====================
st.header("Visão Geral do Ativo")

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
    freq_label = {
        "Diário": "dias", "Semanal": "semanas", "Mensal": "meses",
        "Semestral": "semestres", "Anual": "anos",
    }.get(frequency, "períodos")
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

_llm_notes = [f"Unidade de cotação: {currency.label}."]
if currency.kind == "rate":
    _llm_notes.append("Este ativo é uma taxa de juros: o retorno total mede a variação do nível da taxa.")
render_explain_section(
    lambda: individual_context(
        df,
        symbol.upper(),
        frequency,
        float(ANNUALIZATION_FACTORS.get(frequency, DAILY_ANNUALIZATION_FACTOR)),
        name=asset_name(symbol),
        notes=_llm_notes,
    ),
    key="analise_individual",
)

# -------------------------------------------------------
# Variação por prazo (A1): janelas fixas até a última observação
# -------------------------------------------------------
st.markdown("### Variação por prazo")

daily_closes = st.session_state.get("asset_daily")
trailing_base = base_description(daily_closes)

if currency.kind == "rate":
    st.caption(RATE_NOTE)
elif trailing_base is None:
    st.info("Carregue os dados novamente para ver a variação por prazo.")
else:
    st.markdown(trailing_intro(*trailing_base))
    render_table(
        build_trailing_display(trailing_returns(daily_closes)),
        list(HEADER_LABELS),
        TRAILING_FORMATTERS,
        header_labels=HEADER_LABELS,
        max_height=None,
        min_width=720,
        wrap_header=True,
    )
    st.caption(TRAILING_NOTES)

st.markdown("<br>", unsafe_allow_html=True)


# =====================
# Seção 2: Evolução Temporal
# =====================
value_label = "Taxa" if currency.kind == "rate" else "Preço"

st.markdown("### Evolução Temporal do Ativo")
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
    render_chart_guide("evolucao_temporal")


# =====================
# Seção 3: Volatilidade por Mês
# =====================
st.markdown("### Volatilidade Anualizada por Mês")
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
        render_chart_guide("volatilidade_mensal")

    if currency.kind == "rate":
        st.caption(
            "Para taxas de juros, a volatilidade descreve a oscilação da variação "
            "percentual do nível da taxa."
        )

    render_what_it_means("volatilidade")


# =====================
# Seção 4: Variação Percentual
# =====================
st.markdown(f"### Variação Percentual — {frequency}")
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
    render_chart_guide("variacao_percentual")


# =====================
# Seção 5: Matriz Anual x Mensal
# =====================
st.markdown("### Padrões Sazonais")
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
        render_chart_guide("mapa_sazonal")

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
        render_chart_guide("media_mensal")

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
    # Explorar anos e meses (Plano 2, Bloco 2): duas perguntas, uma por aba
    # -------------------------------------------------------
    st.markdown("#### Explorar anos e meses")
    st.markdown(
        "Os gráficos acima resumem todos os anos juntos. Aqui você pode olhar com "
        "mais detalhe: comparar anos específicos com a média ou medir a variação "
        "entre dois meses do calendário em cada ano."
    )
    st.caption(SEASONALITY_METHOD_TEXT)

    available_years = sorted(int(year) for year in df_matrix_stats.index)
    # Ano sugerido: o último com os 12 meses completos (ou o último disponível).
    complete_years = [
        int(year) for year, row in df_matrix_stats.iterrows() if row.notna().sum() == 12
    ]
    default_year = max(complete_years) if complete_years else available_years[-1]
    tab_years, tab_window = st.tabs(["Anos comparados à média", "Variação entre dois meses"])

    with tab_years:
        st.markdown(YEARS_INTRO)

        col_years, col_months = st.columns(2)
        with col_years:
            selected_years = st.multiselect(
                "Anos para comparar",
                options=available_years,
                default=[default_year],
                key=f"season_years_{symbol}",
                placeholder="Escolha um ou mais anos",
            )
        with col_months:
            selected_months = st.multiselect(
                "Meses exibidos (opcional)",
                options=ORDERED_MONTHS,
                format_func=month_label,
                key=f"season_months_{symbol}",
                placeholder="Todos os meses",
            )

        if not selected_years:
            st.info("Escolha ao menos um ano para ver a comparação.")
        else:
            years_cut = sorted(selected_years)
            chosen = years_label(years_cut)
            base_matrix = filter_monthly_matrix(df_matrix_stats, months=selected_months or None)
            summary = seasonal_summary(base_matrix, years=years_cut)
            highlights = year_comparison_highlights(summary)

            st.markdown(describe_year_comparison(highlights, years_cut))

            with st.container(key="highlight_cards_years"):
                cards = st.columns(4)
                with cards[0]:
                    render_metric_card(
                        "Meses acima da média",
                        f"{highlights['above']} de {highlights['months']}",
                        value_size="1.4rem",
                    )
                with cards[1]:
                    render_metric_card(
                        "Meses abaixo da média",
                        f"{highlights['below']} de {highlights['months']}",
                        value_size="1.4rem",
                    )
                for column, title, item, tone in (
                    (cards[2], "Maior diferença para cima", highlights["largest_above"], "positive"),
                    (cards[3], "Maior diferença para baixo", highlights["largest_below"], "negative"),
                ):
                    with column:
                        if item:
                            render_metric_card(
                                title,
                                month_label(item[0]),
                                value_size="1.4rem",
                                badge=(fmt_pp(item[1]), tone),
                            )
                        else:
                            render_metric_card(title, "—", value_size="1.4rem")

            period_years = f"{available_years[0]}–{available_years[-1]}"
            fig_cut = go.Figure()
            fig_cut.add_trace(
                go.Bar(
                    x=summary.index,
                    y=summary["Média geral"],
                    name=f"Média de todos os anos ({period_years})",
                    marker_color="#A8A29E",
                    customdata=[[fmt_pct(v), int(n)] for v, n in zip(summary["Média geral"], summary["N geral"])],
                    hovertemplate="%{x}: %{customdata[0]}<br>Anos no cálculo: %{customdata[1]}<extra></extra>",
                )
            )
            fig_cut.add_trace(
                go.Bar(
                    x=summary.index,
                    y=summary["Média do recorte"],
                    name=chosen if len(years_cut) == 1 else f"Média de {chosen}",
                    marker_color="#C8102E",
                    customdata=[[fmt_pct(v), int(n)] for v, n in zip(summary["Média do recorte"], summary["N do recorte"])],
                    hovertemplate="%{x}: %{customdata[0]}<br>Anos no cálculo: %{customdata[1]}<extra></extra>",
                )
            )
            fig_cut.add_hline(y=0, line_color="#475569", line_width=1)
            fig_cut = apply_custom_layout(fig_cut, show_legend=True)
            fig_cut.update_layout(
                barmode="group",
                margin=dict(l=40, r=20, t=50, b=20),
                xaxis_title=None,
                yaxis_title="Variação no mês (%)",
                legend=dict(orientation="h", y=1.14, x=0),
            )

            with st.container(border=True):
                st.markdown(
                    "<h5 style='text-align: center; color: #334155; margin-bottom: 10px; font-size: 1rem;'>"
                    f"Variação em cada mês: {escape(chosen)} × média de todos os anos</h5>",
                    unsafe_allow_html=True,
                )
                st.plotly_chart(fig_cut, use_container_width=True, config=PLOTLY_CONFIG)
                render_chart_guide("recorte_anos")

            years_table = pd.DataFrame(
                {
                    "Mês": [month_label(m) for m in summary.index],
                    "Média": summary["Média geral"].values,
                    "Escolhidos": summary["Média do recorte"].values,
                    "Diferença": summary["Diferença (p.p.)"].values,
                    "Alta": summary["Anos positivos recorte (%)"].values,
                    "N": [
                        f"{int(a)} / {int(c)}" if len(years_cut) > 1 else str(int(a))
                        for a, c in zip(summary["N geral"], summary["N do recorte"])
                    ],
                }
            )
            # Com um único ano, "anos com alta" seria só 0% ou 100%: a coluna sai.
            table_columns = ["Mês", "Média", "Escolhidos", "Diferença"]
            table_columns += ["Alta", "N"] if len(years_cut) > 1 else ["N"]
            render_table(
                years_table,
                table_columns,
                {
                    "Média": pct_cell,
                    "Escolhidos": pct_cell,
                    "Diferença": pp_cell,
                    "Alta": share_cell,
                    "N": center_cell,
                },
                header_labels={
                    "Média": "Média de todos os anos",
                    "Escolhidos": "Média dos anos escolhidos" if len(years_cut) > 1 else f"Variação em {chosen}",
                    "Diferença": "Diferença",
                    "Alta": "Anos escolhidos com alta",
                    "N": "Anos no cálculo (todos / escolhidos)" if len(years_cut) > 1 else "Anos na média",
                },
                max_height=None,
                min_width=640,
            )
            st.caption(PP_NOTE)

            if len(years_cut) > 1 and (summary["N do recorte"].dropna() < 3).any():
                st.caption(
                    "Alguns meses têm menos de 3 anos entre os escolhidos. Médias "
                    "calculadas com tão poucos anos variam bastante de uma amostra para outra."
                )

    with tab_window:
        st.markdown(WINDOW_INTRO)

        col_entry, col_exit, col_mark = st.columns([1, 1, 1.4])
        with col_entry:
            entry_name = st.selectbox(
                "Mês de partida (fechamento)",
                options=ORDERED_MONTHS,
                index=ORDERED_MONTHS.index("Jun"),
                format_func=month_label,
                key=f"season_entry_{symbol}",
            )
        with col_exit:
            exit_name = st.selectbox(
                "Mês de chegada (fechamento)",
                options=ORDERED_MONTHS,
                index=ORDERED_MONTHS.index("Dez"),
                format_func=month_label,
                key=f"season_exit_{symbol}",
                help="Se vier antes do mês de partida no calendário, é o do ano seguinte.",
            )
        with col_mark:
            marked_years = st.multiselect(
                "Destacar anos no gráfico (opcional)",
                options=available_years,
                key=f"season_marked_{symbol}",
                placeholder="Nenhum",
            )

        if entry_name == exit_name:
            st.warning("Escolha meses de partida e de chegada diferentes.")
        else:
            window_all = window_returns(df, entry_name, exit_name, value_col="Value")
            stats_all = window_summary(window_all)

            st.markdown(describe_window(stats_all, entry_name, exit_name))

            if not window_all.empty:
                positives = round(stats_all["Anos positivos (%)"] / 100 * stats_all["N"])
                low = window_all.loc[window_all["Retorno (%)"].idxmin()]
                high = window_all.loc[window_all["Retorno (%)"].idxmax()]

                with st.container(key="highlight_cards_window"):
                    cards = st.columns(4)
                    with cards[0]:
                        render_metric_card(
                            "Anos com alta",
                            f"{positives} de {stats_all['N']}",
                            value_size="1.4rem",
                            badge=(f"{stats_all['Anos positivos (%)']:.0f}% dos anos", "neutral"),
                        )
                    with cards[1]:
                        render_metric_card(
                            "Variação média",
                            fmt_pct(stats_all["Média"]),
                            value_size="1.4rem",
                            subtitle="Soma das variações dividida pelo número de anos",
                        )
                    with cards[2]:
                        render_metric_card(
                            "Variação mediana",
                            fmt_pct(stats_all["Mediana"]),
                            value_size="1.4rem",
                            subtitle="Valor do meio, menos afetado por extremos",
                        )
                    with cards[3]:
                        render_metric_card(
                            "Faixa observada",
                            f"{fmt_pct(low['Retorno (%)'])} a {fmt_pct(high['Retorno (%)'])}",
                            value_size="1.15rem",
                            subtitle=f"Menor em {int(low['Ano'])} · maior em {int(high['Ano'])}",
                        )

                render_explain_section(
                    lambda: window_context(
                        stats_all,
                        entry_name,
                        exit_name,
                        symbol.upper(),
                        df["Date"].iloc[0],
                        df["Date"].iloc[-1],
                        len(monthly_closes(df, "Value", "Date")),
                        incomplete_month=bool(
                            df_matrix.notna().sum().sum() != df_matrix_stats.notna().sum().sum()
                        ),
                        name=asset_name(symbol),
                    ),
                    key="janela_sazonal",
                )

                highlight = set(marked_years)
                fig_window = go.Figure(
                    data=go.Bar(
                        x=window_all["Ano"].astype(str),
                        y=window_all["Retorno (%)"],
                        marker_color=["#15803D" if v >= 0 else "#B91C1C" for v in window_all["Retorno (%)"]],
                        marker_opacity=[
                            1.0 if not highlight or int(year) in highlight else 0.3
                            for year in window_all["Ano"]
                        ],
                        customdata=[fmt_pct(v) for v in window_all["Retorno (%)"]],
                        hovertemplate="Partida em %{x}<br>Variação: %{customdata}<extra></extra>",
                    )
                )
                fig_window.add_hline(y=0, line_color="#475569", line_width=1)
                fig_window.add_hline(
                    y=stats_all["Média"],
                    line_dash="dash",
                    line_color="#475569",
                    annotation_text=f"Média: {fmt_pct(stats_all['Média'])}",
                    annotation_position="top right",
                    annotation_bgcolor="rgba(255, 255, 255, 0.9)",
                )
                fig_window = apply_custom_layout(fig_window)
                fig_window.update_layout(
                    margin=dict(l=40, r=20, t=40, b=20),
                    xaxis_title="Ano de partida",
                    xaxis_type="category",
                    yaxis_title="Variação no intervalo (%)",
                )

                with st.container(border=True):
                    st.markdown(
                        "<h5 style='text-align: center; color: #334155; margin-bottom: 10px; font-size: 1rem;'>"
                        f"Variação {escape(window_label(entry_name, exit_name))}, ano a ano</h5>",
                        unsafe_allow_html=True,
                    )
                    st.plotly_chart(fig_window, use_container_width=True, config=PLOTLY_CONFIG)
                    render_chart_guide("janela_retorno")

                window_table = window_all.assign(
                    Diferenca=window_all["Retorno (%)"] - stats_all["Média"]
                )
                render_table(
                    window_table,
                    ["Ano", "Fechamento de entrada", "Fechamento de saída", "Retorno (%)", "Diferenca"],
                    {
                        "Ano": lambda v: (str(int(v)), "text-align:center;"),
                        "Fechamento de entrada": price_cell,
                        "Fechamento de saída": price_cell,
                        "Retorno (%)": pct_cell,
                        "Diferenca": pp_cell,
                    },
                    header_labels={
                        "Ano": "Ano de partida",
                        "Fechamento de entrada": f"Fechamento de {FULL_MONTH_NAMES[entry_name]}",
                        "Fechamento de saída": f"Fechamento de {FULL_MONTH_NAMES[exit_name]}",
                        "Retorno (%)": "Variação",
                        "Diferenca": "Diferença para a média",
                    },
                    max_height=360,
                    min_width=640,
                )

            st.caption(WINDOW_NOTE)

# =====================
# Seção 6: Tabela de Dados
# =====================
st.header("Dados Processados")

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
