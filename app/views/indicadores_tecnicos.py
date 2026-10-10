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


import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.ui.chart_guide import render_chart_guide
from app.ui.asset_cards import render_asset_hero_logo
from app.ui.data_info import (
    render_availability_messages,
    render_catalog_notice,
    render_data_availability,
)
from app.ui.disclaimers import (
    render_footer_disclaimer,
    render_methodology_limitations,
)
from app.ui.indicator_docs import (
    render_indicator_glossary,
    render_indicator_note,
)
from app.ui.sidebar import render_asset_controls
from app.ui.state import initialize_asset_state
from app.ui.tables import date_cell, number_cell, render_table
from core.assets import ASSETS
from core.config import ANNUALIZATION_FACTORS
from core.currency import currency_info
from core.data_availability import assess_availability
from core.data_loader import download_active_data
from core.data_processor import prepare_dataframe
from core.exports import csv_filename, dataframe_to_csv_bytes
from core.formatters import format_number_br
from core.indicators import (
    add_bollinger_bands,
    add_exponential_moving_averages,
    add_macd,
    add_moving_averages,
    add_rsi,
)
from core.indicators_extra import add_atr, add_rolling_volatility
from core.visualizations import (
    create_candlestick_chart,
    create_macd_chart,
    create_price_indicator_chart,
    create_rsi_chart,
    create_volume_chart,
    format_context,
)


st.set_page_config(
    page_title="Argos DataLab",
    page_icon="📈",
    layout="wide",
)


initialize_asset_state()


st.title("📈 Indicadores Técnicos")

st.markdown(
    "<p style='font-size: 1.1rem; color: #475569; margin-bottom: 2rem;'>"
    "Explore indicadores técnicos calculados sobre dados históricos. "
    "Médias móveis, RSI, MACD, Bandas de Bollinger, ATR e volatilidade móvel "
    "ajudam a descrever tendência, momentum e dispersão de preços."
    "</p>",
    unsafe_allow_html=True
)


PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
}


# ==========================================================
# Gráficos auxiliares
# ==========================================================
def price_axis_label(symbol: str) -> str:
    """Título do eixo de preço com a unidade de cotação do ativo."""
    currency = currency_info(symbol)
    kind = "Taxa" if currency.kind == "rate" else "Preço"
    unit = currency.prefix.strip() or currency.label
    return f"{kind} ({unit})"


def build_simple_line_chart(
    dataframe: pd.DataFrame,
    column: str,
    name: str,
    color: str,
    y_suffix: str = "",
    scale: float = 1.0,
) -> go.Figure:
    """Gráfico de linha simples, usado para ATR e volatilidade móvel."""
    figure = go.Figure(
        go.Scatter(
            x=dataframe["Date"],
            y=dataframe[column] * scale,
            mode="lines",
            line=dict(color=color, width=2),
            name=name,
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b><br>"
                + name
                + ": %{y:.2f}"
                + y_suffix
                + "<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        showlegend=False,
        margin=dict(l=10, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", ticksuffix=y_suffix),
        font=dict(family="Inter, Arial, sans-serif", color="#334155"),
    )
    return figure


# =====================
# Controles compartilhados
# =====================
asset_params = render_asset_controls(
    title="⚙️ Parâmetros da Análise",
    button_label="📊 Gerar análise técnica",
    button_key="indicators_load_button",
)

symbol = asset_params["symbol"]
start_date = asset_params["start_date"]
end_date = asset_params["end_date"]
frequency = asset_params["frequency"]
load_analysis = asset_params["submitted"]


# =====================
# Controles específicos
# =====================
with st.sidebar:
    st.divider()

    chart_type = st.radio(
        "Tipo de gráfico principal",
        options=[
            "Linha de fechamento",
            "Candles",
        ],
        key="indicators_chart_type",
    )

    st.subheader("Médias móveis simples")

    show_sma_short = st.checkbox(
        "Exibir SMA curta",
        value=True,
        key="indicators_show_sma_short",
    )

    sma_short_window = st.slider(
        "Período da SMA curta",
        min_value=2,
        max_value=100,
        value=20,
        key="indicators_sma_short_window",
    )

    show_sma_long = st.checkbox(
        "Exibir SMA longa",
        value=True,
        key="indicators_show_sma_long",
    )

    sma_long_window = st.slider(
        "Período da SMA longa",
        min_value=2,
        max_value=250,
        value=50,
        key="indicators_sma_long_window",
    )

    st.subheader("Médias móveis exponenciais")

    show_ema_short = st.checkbox(
        "Exibir EMA curta",
        value=False,
        key="indicators_show_ema_short",
    )

    ema_short_window = st.slider(
        "Período da EMA curta",
        min_value=2,
        max_value=100,
        value=12,
        key="indicators_ema_short_window",
    )

    show_ema_long = st.checkbox(
        "Exibir EMA longa",
        value=False,
        key="indicators_show_ema_long",
    )

    ema_long_window = st.slider(
        "Período da EMA longa",
        min_value=2,
        max_value=250,
        value=26,
        key="indicators_ema_long_window",
    )

    st.subheader("Bandas de Bollinger")

    show_bollinger = st.checkbox(
        "Exibir Bandas de Bollinger",
        value=False,
        key="indicators_show_bollinger",
    )

    bollinger_window = st.slider(
        "Período das Bandas de Bollinger",
        min_value=2,
        max_value=100,
        value=20,
        key="indicators_bollinger_window",
    )

    bollinger_std = st.slider(
        "Desvios-padrão das Bandas",
        min_value=1.0,
        max_value=4.0,
        value=2.0,
        step=0.5,
        key="indicators_bollinger_std",
    )

    st.subheader("RSI")

    show_rsi = st.checkbox(
        "Exibir RSI",
        value=True,
        key="indicators_show_rsi",
    )

    rsi_window = st.slider(
        "Período do RSI",
        min_value=2,
        max_value=100,
        value=14,
        key="indicators_rsi_window",
    )

    rsi_upper = st.slider(
        "Nível superior do RSI",
        min_value=50,
        max_value=95,
        value=70,
        key="indicators_rsi_upper",
    )

    rsi_lower = st.slider(
        "Nível inferior do RSI",
        min_value=5,
        max_value=50,
        value=30,
        key="indicators_rsi_lower",
    )

    show_macd = st.checkbox(
        "Exibir MACD",
        value=True,
        key="indicators_show_macd",
    )

    st.subheader("ATR")

    show_atr = st.checkbox(
        "Exibir ATR",
        value=False,
        key="indicators_show_atr",
    )

    atr_window = st.slider(
        "Período do ATR",
        min_value=2,
        max_value=100,
        value=14,
        key="indicators_atr_window",
    )

    st.subheader("Volatilidade móvel")

    show_vol = st.checkbox(
        "Exibir volatilidade móvel",
        value=False,
        key="indicators_show_vol",
    )

    vol_window = st.slider(
        "Janela da volatilidade móvel",
        min_value=2,
        max_value=100,
        value=20,
        key="indicators_vol_window",
    )

    show_volume = st.checkbox(
        "Exibir volume",
        value=True,
        key="indicators_show_volume",
    )


# =====================
# Validação de parâmetros
# =====================
if sma_short_window >= sma_long_window:
    st.sidebar.warning(
        "A SMA curta normalmente deve ter período menor que a SMA longa."
    )

if ema_short_window >= ema_long_window:
    st.sidebar.warning(
        "A EMA curta normalmente deve ter período menor que a EMA longa."
    )

if rsi_lower >= rsi_upper:
    st.sidebar.error(
        "O nível inferior do RSI deve ser menor que o nível superior."
    )
    st.stop()


# =====================
# Processamento da análise
# =====================
if load_analysis:
    if not symbol:
        st.sidebar.error(
            "Informe um símbolo de ativo antes de gerar a análise."
        )
        st.stop()

    effective_chart_type = chart_type

    if chart_type == "Candles" and frequency == "Mensal":
        effective_chart_type = "Linha de fechamento"

        st.sidebar.warning(
            "O gráfico candle não é exibido para frequência mensal. "
            "A análise utilizará linha de fechamento."
        )

    st.session_state["indicators_loaded"] = True
    st.session_state["indicators_query"] = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
        "chart_type": effective_chart_type,
        "show_sma_short": show_sma_short,
        "sma_short_window": sma_short_window,
        "show_sma_long": show_sma_long,
        "sma_long_window": sma_long_window,
        "show_ema_short": show_ema_short,
        "ema_short_window": ema_short_window,
        "show_ema_long": show_ema_long,
        "ema_long_window": ema_long_window,
        "show_bollinger": show_bollinger,
        "bollinger_window": bollinger_window,
        "bollinger_std": bollinger_std,
        "show_rsi": show_rsi,
        "rsi_window": rsi_window,
        "rsi_upper": rsi_upper,
        "rsi_lower": rsi_lower,
        "show_macd": show_macd,
        "show_atr": show_atr,
        "atr_window": atr_window,
        "show_vol": show_vol,
        "vol_window": vol_window,
        "show_volume": show_volume,
    }

    with st.spinner("Carregando e calculando indicadores..."):
        df_raw = download_active_data(
            symbol=symbol,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            interval="1d",
        )

        if df_raw is None or df_raw.empty:
            st.session_state["indicators_loaded"] = False
            st.session_state["indicators_query"] = None

            st.error(
                f"Não foi possível carregar dados para '{symbol}'. "
                "Confira o código do ativo (ações brasileiras terminam em .SA) "
                "e o período, ou tente novamente em instantes."
            )
            st.stop()

        df = prepare_dataframe(df_raw)

        # Datas diárias baixadas, guardadas antes de agregar pela frequência
        daily_dates = df["Date"].copy()

        if frequency == "Semanal":
            df = (
                df
                .set_index("Date")
                .resample("W")
                .agg(
                    {
                        "Open": "first",
                        "High": "max",
                        "Low": "min",
                        "Close": "last",
                        "Volume": "sum",
                    }
                )
                .dropna()
                .reset_index()
            )

        elif frequency == "Mensal":
            df = (
                df
                .set_index("Date")
                .resample("ME")
                .agg(
                    {
                        "Open": "first",
                        "High": "max",
                        "Low": "min",
                        "Close": "last",
                        "Volume": "sum",
                    }
                )
                .dropna()
                .reset_index()
            )

        # Disponibilidade: período solicitado x período efetivamente disponível
        availability = assess_availability(
            dates=daily_dates,
            requested_start=start_date,
            requested_end=end_date,
            period_observations=len(df),
        )

        if availability.insufficient:
            st.session_state["indicators_loaded"] = False
            st.session_state["indicators_query"] = None
            render_availability_messages(availability)
            st.stop()

        df["Value"] = df["Close"]

        df = add_moving_averages(
            df,
            value_col="Value",
            short_window=sma_short_window,
            long_window=sma_long_window,
        )

        df = add_exponential_moving_averages(
            df,
            value_col="Value",
            short_window=ema_short_window,
            long_window=ema_long_window,
        )

        df = add_bollinger_bands(
            df,
            value_col="Value",
            window=bollinger_window,
            num_std=bollinger_std,
        )

        df = add_rsi(
            df,
            value_col="Value",
            window=rsi_window,
        )

        df = add_macd(
            df,
            value_col="Value",
            short_span=ema_short_window,
            long_span=ema_long_window,
            signal_span=9,
        )

        df = add_atr(
            df,
            window=atr_window,
        )

        df = add_rolling_volatility(
            df,
            window=vol_window,
            value_col="Value",
            annualization_factor=float(
                ANNUALIZATION_FACTORS.get(frequency, 252)
            ),
        )

        st.session_state["indicators_df"] = df
        st.session_state["indicators_availability"] = availability
        st.session_state["indicators_fetched_at"] = datetime.now()


# =====================
# Consulta confirmada
# =====================
query = st.session_state.get("indicators_query")

if (
    not st.session_state.get("indicators_loaded")
    or query is None
    or "indicators_df" not in st.session_state
):
    st.info(
        "Configure os parâmetros na barra lateral e clique em "
        "**Gerar análise técnica**."
    )
    st.stop()


df = st.session_state["indicators_df"]

symbol = query["symbol"]
start_date = query["start_date"]
end_date = query["end_date"]
frequency = query["frequency"]
chart_type = query["chart_type"]

show_sma_short = query["show_sma_short"]
sma_short_window = query["sma_short_window"]
show_sma_long = query["show_sma_long"]
sma_long_window = query["sma_long_window"]

show_ema_short = query["show_ema_short"]
ema_short_window = query["ema_short_window"]
show_ema_long = query["show_ema_long"]
ema_long_window = query["ema_long_window"]

show_bollinger = query["show_bollinger"]
show_rsi = query["show_rsi"]
rsi_window = query["rsi_window"]
rsi_upper = query["rsi_upper"]
rsi_lower = query["rsi_lower"]
show_macd = query["show_macd"]
show_atr = query.get("show_atr", False)
atr_window = query.get("atr_window", 14)
show_vol = query.get("show_vol", False)
vol_window = query.get("vol_window", 20)
show_volume = query["show_volume"]


context = format_context(
    symbol=symbol.upper(),
    start_date=start_date,
    end_date=end_date,
    frequency=frequency,
)

price_label = price_axis_label(symbol)


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
        st.markdown(f"**Observações Processadas:** {len(df)} períodos válidos calculados com sucesso.")
        st.markdown(
            "**Tratamento:** As médias móveis, RSI, MACD, Bandas de Bollinger, ATR e volatilidade móvel são calculados somente com dados disponíveis até cada data. "
            "As médias, o RSI, o MACD e a volatilidade usam o preço de **fechamento**; o ATR usa também máxima e mínima."
        )

st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)


# =====================
# Disponibilidade dos dados: solicitado x disponível, fonte e consulta
# =====================
availability = st.session_state.get("indicators_availability")
if availability is not None:
    render_data_availability(
        availability,
        st.session_state.get("indicators_fetched_at"),
    )

st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)


# =====================
# Preço e indicadores
# =====================
st.header("📊 Preço e Indicadores")

if chart_type == "Candles":
    candle_figure = create_candlestick_chart(
        df=df,
        symbol=symbol.upper(),
        context=context,
        price_label=price_label,
    )

    candle_figure.update_xaxes(title_text="")

    st.plotly_chart(
        candle_figure,
        width="stretch",
    )
    render_chart_guide("candles")

    st.caption(
        "Cada candle apresenta abertura, máxima, mínima e fechamento "
        "do período. Verde representa fechamento acima da abertura; "
        "vermelho representa fechamento abaixo da abertura."
    )

price_figure = create_price_indicator_chart(
    df=df,
    symbol=symbol.upper(),
    context=context,
    value_col="Value",
    show_sma_short=show_sma_short,
    sma_short_col=f"SMA_{sma_short_window}",
    show_sma_long=show_sma_long,
    sma_long_col=f"SMA_{sma_long_window}",
    show_ema_short=show_ema_short,
    ema_short_col=f"EMA_{ema_short_window}",
    show_ema_long=show_ema_long,
    ema_long_col=f"EMA_{ema_long_window}",
    show_bollinger=show_bollinger,
    price_label=price_label,
)

price_figure.update_xaxes(title_text="")

st.plotly_chart(
    price_figure,
    width="stretch",
)
render_chart_guide("preco_indicadores")

st.caption(
    "Preço exibido na moeda de origem do ativo. "
    "As médias móveis e bandas são calculadas a partir do fechamento."
)

if show_sma_short or show_sma_long:
    render_indicator_note("sma")

if show_ema_short or show_ema_long:
    render_indicator_note("ema")

if show_bollinger:
    render_indicator_note("bollinger")


# =====================
# Volume
# =====================
if show_volume and "Volume" in df.columns:
    st.markdown("### 📦 Volume")

    volume_figure = create_volume_chart(
        df=df,
        symbol=symbol.upper(),
        context=context,
    )

    formatted_volume = df["Volume"].apply(format_number_br)

    volume_figure.update_traces(
        customdata=formatted_volume,
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Volume: <b>%{customdata}</b><extra></extra>",
        marker_color="#64748B",
    )

    volume_figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, title=""),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        font=dict(family="Inter, Arial, sans-serif", color="#334155")
    )

    with st.container(border=True):
        st.plotly_chart(
            volume_figure,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )
        render_chart_guide("volume")

    render_indicator_note("volume")


# =====================
# RSI
# =====================
if show_rsi:
    st.header("📉 RSI")

    rsi_figure = create_rsi_chart(
        df=df,
        symbol=symbol.upper(),
        context=context,
        rsi_col=f"RSI_{rsi_window}",
        upper_level=float(rsi_upper),
        lower_level=float(rsi_lower),
    )

    rsi_figure.update_xaxes(title_text="")

    st.plotly_chart(
        rsi_figure,
        width="stretch",
    )
    render_chart_guide("rsi")

    st.caption(
        "O RSI varia entre 0 e 100. Os níveis de referência ajudam a "
        "contextualizar o indicador, mas não devem ser interpretados "
        "isoladamente como recomendação de investimento."
    )
    render_indicator_note("rsi")


# =====================
# MACD
# =====================
if show_macd:
    st.header("📊 MACD")

    macd_figure = create_macd_chart(
        df=df,
        symbol=symbol.upper(),
        context=context,
    )

    macd_figure.update_xaxes(title_text="")

    st.plotly_chart(
        macd_figure,
        width="stretch",
    )
    render_chart_guide("macd")

    st.caption(
        f"O MACD desta análise usa EMA curta de {ema_short_window} e EMA longa "
        f"de {ema_long_window} períodos (as mesmas definidas na barra lateral) "
        "e linha de sinal de 9 períodos."
    )
    render_indicator_note("macd")


# =====================
# ATR
# =====================
if show_atr and f"ATR_{atr_window}" in df.columns:
    st.header("📏 ATR")

    with st.container(border=True):
        st.plotly_chart(
            build_simple_line_chart(
                df,
                f"ATR_{atr_window}",
                "ATR",
                "#8B5CF6",
            ),
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )
        render_chart_guide("atr")

    render_indicator_note("atr")


# =====================
# Volatilidade móvel
# =====================
if show_vol and f"VOL_{vol_window}" in df.columns:
    st.header("🌪️ Volatilidade Móvel")

    with st.container(border=True):
        st.plotly_chart(
            build_simple_line_chart(
                df,
                f"VOL_{vol_window}",
                "Volatilidade",
                "#F59E0B",
                y_suffix="%",
                scale=100.0,
            ),
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )
        render_chart_guide("volatilidade_movel")

    render_indicator_note("volatilidade_movel")


# =====================
# Tabela e download
# =====================
st.header("📋 Dados com Indicadores")

display_columns = [
    column
    for column in [
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        f"SMA_{sma_short_window}",
        f"SMA_{sma_long_window}",
        f"EMA_{ema_short_window}",
        f"EMA_{ema_long_window}",
        "BB_Lower",
        "BB_Middle",
        "BB_Upper",
        f"RSI_{rsi_window}",
        "MACD",
        "MACD_Signal",
        "MACD_Histogram",
        f"ATR_{atr_window}",
        f"VOL_{vol_window}",
    ]
    if column in df.columns
]

table_formatters = {"Date": date_cell}
table_formatters.update(
    {column: number_cell for column in display_columns if column != "Date"}
)

render_table(
    df,
    display_columns,
    table_formatters,
    max_height=400,
    min_width=1600,
    iframe=True,
)


st.download_button(
    label="⬇️ Baixar dados com indicadores em CSV",
    data=dataframe_to_csv_bytes(df),
    file_name=csv_filename(symbol.upper(), "indicadores"),
    mime="text/csv",
)


# =====================
# Glossário, limitações, catálogo e rodapé
# =====================
st.markdown("<br>", unsafe_allow_html=True)

render_indicator_glossary()

render_methodology_limitations([
    "Todos os indicadores são calculados somente com dados disponíveis até cada data (sem informação futura); essa propriedade é verificada por testes automatizados.",
    "Os parâmetros (janelas, desvios-padrão, níveis do RSI) são convenções ajustáveis; os resultados mudam ao alterá-los.",
    "Indicadores descrevem o comportamento histórico do preço. Cruzamentos, faixas e níveis de referência não indicam compra, venda nem resultado futuro.",
    "Em frequência mensal ou semanal há menos observações, o que torna médias e janelas mais longas menos estáveis.",
    "Os primeiros valores de médias exponenciais e do MACD dependem do ponto inicial da série e são menos confiáveis (período de aquecimento).",
])

render_catalog_notice()

render_footer_disclaimer()