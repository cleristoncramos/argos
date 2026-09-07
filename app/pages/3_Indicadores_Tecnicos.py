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
from core.data_loader import download_active_data
from core.data_processor import prepare_dataframe
from core.indicators import (
    add_bollinger_bands,
    add_exponential_moving_averages,
    add_macd,
    add_moving_averages,
    add_rsi,
)
from core.visualizations import (
    create_candlestick_chart,
    create_macd_chart,
    create_price_indicator_chart,
    create_rsi_chart,
    create_volume_chart,
    format_context,
)


st.set_page_config(
    page_title="Indicadores Técnicos | Argos DataLab",
    page_icon="📈",
    layout="wide",
)


initialize_asset_state()


st.title("📈 Indicadores Técnicos")

st.markdown(
    """
Explore indicadores técnicos calculados sobre dados históricos.
Médias móveis, RSI, MACD e Bandas de Bollinger ajudam a descrever
tendência, momentum e dispersão de preços.
"""
)

st.warning(
    "Indicadores técnicos descrevem dados históricos. Eles não constituem "
    "sinal automático de compra, venda ou recomendação de investimento."
)


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
                "Verifique o símbolo e o período."
            )
            st.stop()

        df = prepare_dataframe(df_raw)

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

        st.session_state["indicators_df"] = df


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
show_volume = query["show_volume"]


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
    f"Observações: **{len(df)}**"
)


# =====================
# Preço e indicadores
# =====================
st.header("📊 Preço e Indicadores")

if chart_type == "Candles":
    candle_figure = create_candlestick_chart(
        df=df,
        symbol=symbol.upper(),
        context=context,
    )

    st.plotly_chart(
        candle_figure,
        width="stretch",
    )

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
)

st.plotly_chart(
    price_figure,
    width="stretch",
)

st.caption(
    "Preço exibido na moeda de origem do ativo. "
    "As médias móveis e bandas são calculadas a partir do fechamento."
)


# =====================
# Volume
# =====================
if show_volume and "Volume" in df.columns:
    st.header("📦 Volume")

    volume_figure = create_volume_chart(
        df=df,
        symbol=symbol.upper(),
        context=context,
    )

    st.plotly_chart(
        volume_figure,
        width="stretch",
    )


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

    st.plotly_chart(
        rsi_figure,
        width="stretch",
    )

    st.caption(
        "O RSI varia entre 0 e 100. Os níveis de referência ajudam a "
        "contextualizar o indicador, mas não devem ser interpretados "
        "isoladamente como recomendação de investimento."
    )


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

    st.plotly_chart(
        macd_figure,
        width="stretch",
    )


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
    ]
    if column in df.columns
]

st.dataframe(
    df[display_columns],
    width="stretch",
    height=350,
)

csv_data = df.to_csv(
    index=False,
).encode(
    "utf-8"
)

st.download_button(
    label="⬇️ Baixar dados com indicadores em CSV",
    data=csv_data,
    file_name=f"{symbol.upper()}_indicadores.csv",
    mime="text/csv",
)


# =====================
# Rodapé
# =====================
st.markdown("---")

st.caption(
    "⚠️ Esta ferramenta possui finalidade educacional e de pesquisa. "
    "Indicadores técnicos e dados históricos não garantem resultados "
    "futuros e não constituem recomendação de investimento."
)