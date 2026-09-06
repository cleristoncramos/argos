from typing import Iterable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


COLORS = {
    "price": "#2563EB",
    "sma_short": "#F59E0B",
    "sma_long": "#7C3AED",
    "ema_short": "#10B981",
    "ema_long": "#EC4899",
    "bollinger": "rgba(59, 130, 246, 0.18)",
    "volume": "#64748B",
    "rsi": "#8B5CF6",
    "macd": "#2563EB",
    "signal": "#F59E0B",
    "positive": "#16A34A",
    "negative": "#DC2626",
    "neutral": "#475569",
}


def format_context(
    symbol: str,
    start_date,
    end_date,
    frequency: str,
) -> str:
    """
    Gera texto padronizado de contexto para títulos de gráficos.
    """
    start = pd.to_datetime(start_date).strftime("%d/%m/%Y")
    end = pd.to_datetime(end_date).strftime("%d/%m/%Y")

    return (
        f"{symbol} · {start} a {end} · "
        f"Frequência: {frequency}"
    )


def validate_columns(
    df: pd.DataFrame,
    required_columns: Iterable[str],
) -> None:
    """
    Verifica se todas as colunas obrigatórias existem no DataFrame.
    """
    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Colunas obrigatórias ausentes: "
            + ", ".join(missing)
        )


def create_price_indicator_chart(
    df: pd.DataFrame,
    symbol: str,
    context: str,
    value_col: str = "Value",
    show_sma_short: bool = False,
    sma_short_col: str = "SMA_20",
    show_sma_long: bool = False,
    sma_long_col: str = "SMA_50",
    show_ema_short: bool = False,
    ema_short_col: str = "EMA_12",
    show_ema_long: bool = False,
    ema_long_col: str = "EMA_26",
    show_bollinger: bool = False,
    bb_lower_col: str = "BB_Lower",
    bb_middle_col: str = "BB_Middle",
    bb_upper_col: str = "BB_Upper",
) -> go.Figure:
    """
    Cria gráfico de preço de fechamento com camadas opcionais
    de médias móveis e bandas de Bollinger.
    """
    validate_columns(df, ["Date", value_col])

    fig = go.Figure()

    if show_bollinger:
        validate_columns(
            df,
            [bb_lower_col, bb_middle_col, bb_upper_col],
        )

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[bb_upper_col],
                name="Bollinger superior",
                mode="lines",
                line=dict(
                    color="rgba(59, 130, 246, 0.35)",
                    width=1,
                ),
                hovertemplate=(
                    "Data: %{x|%d/%m/%Y}<br>"
                    "Banda superior: %{y:,.2f}"
                    "<extra></extra>"
                ),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[bb_lower_col],
                name="Bollinger inferior",
                mode="lines",
                line=dict(
                    color="rgba(59, 130, 246, 0.35)",
                    width=1,
                ),
                fill="tonexty",
                fillcolor=COLORS["bollinger"],
                hovertemplate=(
                    "Data: %{x|%d/%m/%Y}<br>"
                    "Banda inferior: %{y:,.2f}"
                    "<extra></extra>"
                ),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[bb_middle_col],
                name="Média Bollinger",
                mode="lines",
                line=dict(
                    color="#64748B",
                    width=1,
                    dash="dot",
                ),
                hovertemplate=(
                    "Data: %{x|%d/%m/%Y}<br>"
                    "Média Bollinger: %{y:,.2f}"
                    "<extra></extra>"
                ),
            )
        )

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[value_col],
            name="Preço de fechamento",
            mode="lines",
            line=dict(
                color=COLORS["price"],
                width=2.5,
            ),
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}<br>"
                "Fechamento: %{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    if show_sma_short:
        validate_columns(df, [sma_short_col])

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[sma_short_col],
                name=sma_short_col.replace("_", " "),
                mode="lines",
                line=dict(
                    color=COLORS["sma_short"],
                    width=1.8,
                ),
            )
        )

    if show_sma_long:
        validate_columns(df, [sma_long_col])

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[sma_long_col],
                name=sma_long_col.replace("_", " "),
                mode="lines",
                line=dict(
                    color=COLORS["sma_long"],
                    width=1.8,
                ),
            )
        )

    if show_ema_short:
        validate_columns(df, [ema_short_col])

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[ema_short_col],
                name=ema_short_col.replace("_", " "),
                mode="lines",
                line=dict(
                    color=COLORS["ema_short"],
                    width=1.6,
                    dash="dash",
                ),
            )
        )

    if show_ema_long:
        validate_columns(df, [ema_long_col])

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df[ema_long_col],
                name=ema_long_col.replace("_", " "),
                mode="lines",
                line=dict(
                    color=COLORS["ema_long"],
                    width=1.6,
                    dash="dash",
                ),
            )
        )

    fig.update_layout(
        title=f"Preço de Fechamento e Indicadores — {symbol}",
        xaxis_title="Data",
        yaxis_title="Preço na moeda de origem",
        template="plotly_white",
        hovermode="x unified",
        legend_title_text="Séries",
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=40, r=20, t=70, b=40),
    )

    fig.add_annotation(
        text=context,
        xref="paper",
        yref="paper",
        x=0,
        y=1.10,
        showarrow=False,
        font=dict(size=11, color="#475569"),
        align="left",
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E2E8F0",
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E2E8F0",
    )

    return fig


def create_candlestick_chart(
    df: pd.DataFrame,
    symbol: str,
    context: str,
) -> go.Figure:
    """
    Cria gráfico candle com Open, High, Low e Close.

    O gráfico deve ser usado apenas com dados diários ou semanais.
    """
    validate_columns(
        df,
        ["Date", "Open", "High", "Low", "Close"],
    )

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["Date"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name=symbol,
                increasing=dict(
                    line=dict(color=COLORS["positive"]),
                    fillcolor=COLORS["positive"],
                ),
                decreasing=dict(
                    line=dict(color=COLORS["negative"]),
                    fillcolor=COLORS["negative"],
                ),
                hovertemplate=(
                    "Data: %{x|%d/%m/%Y}<br>"
                    "Abertura: %{open:,.2f}<br>"
                    "Máxima: %{high:,.2f}<br>"
                    "Mínima: %{low:,.2f}<br>"
                    "Fechamento: %{close:,.2f}"
                    "<extra></extra>"
                ),
            )
        ]
    )

    fig.update_layout(
        title=f"Gráfico Candle — {symbol}",
        xaxis_title="Data",
        yaxis_title="Preço na moeda de origem",
        template="plotly_white",
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        xaxis_rangeslider_visible=False,
        margin=dict(l=40, r=20, t=70, b=40),
    )

    fig.add_annotation(
        text=context,
        xref="paper",
        yref="paper",
        x=0,
        y=1.10,
        showarrow=False,
        font=dict(size=11, color="#475569"),
        align="left",
    )

    return fig


def create_volume_chart(
    df: pd.DataFrame,
    symbol: str,
    context: str,
) -> go.Figure:
    """
    Cria gráfico de volume por período.
    """
    validate_columns(df, ["Date", "Volume"])

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["Volume"],
            name="Volume",
            marker_color=COLORS["volume"],
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}<br>"
                "Volume: %{y:,.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=f"Volume Negociado — {symbol}",
        xaxis_title="Data",
        yaxis_title="Volume",
        template="plotly_white",
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=40, r=20, t=70, b=40),
    )

    fig.add_annotation(
        text=context,
        xref="paper",
        yref="paper",
        x=0,
        y=1.10,
        showarrow=False,
        font=dict(size=11, color="#475569"),
        align="left",
    )

    return fig


def create_rsi_chart(
    df: pd.DataFrame,
    symbol: str,
    context: str,
    rsi_col: str = "RSI_14",
    upper_level: float = 70.0,
    lower_level: float = 30.0,
) -> go.Figure:
    """
    Cria gráfico do RSI com linhas de referência configuráveis.
    """
    validate_columns(df, ["Date", rsi_col])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[rsi_col],
            name="RSI",
            mode="lines",
            line=dict(
                color=COLORS["rsi"],
                width=2,
            ),
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}<br>"
                "RSI: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=upper_level,
        line_dash="dash",
        line_color=COLORS["negative"],
        annotation_text=f"Referência superior ({upper_level:.0f})",
        annotation_position="top right",
    )

    fig.add_hline(
        y=lower_level,
        line_dash="dash",
        line_color=COLORS["positive"],
        annotation_text=f"Referência inferior ({lower_level:.0f})",
        annotation_position="bottom right",
    )

    fig.add_hline(
        y=50,
        line_dash="dot",
        line_color=COLORS["neutral"],
    )

    fig.update_layout(
        title=f"Índice de Força Relativa (RSI) — {symbol}",
        xaxis_title="Data",
        yaxis_title="RSI (0 a 100)",
        yaxis=dict(range=[0, 100]),
        template="plotly_white",
        hovermode="x unified",
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=40, r=20, t=70, b=40),
    )

    fig.add_annotation(
        text=context,
        xref="paper",
        yref="paper",
        x=0,
        y=1.10,
        showarrow=False,
        font=dict(size=11, color="#475569"),
        align="left",
    )

    return fig


def create_macd_chart(
    df: pd.DataFrame,
    symbol: str,
    context: str,
) -> go.Figure:
    """
    Cria gráfico de MACD, linha de sinal e histograma.
    """
    validate_columns(
        df,
        ["Date", "MACD", "MACD_Signal", "MACD_Histogram"],
    )

    histogram_colors = [
        COLORS["positive"]
        if value >= 0
        else COLORS["negative"]
        for value in df["MACD_Histogram"].fillna(0)
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=df["MACD_Histogram"],
            name="Histograma",
            marker_color=histogram_colors,
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}<br>"
                "Histograma: %{y:.4f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["MACD"],
            name="MACD",
            mode="lines",
            line=dict(
                color=COLORS["macd"],
                width=2,
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["MACD_Signal"],
            name="Sinal",
            mode="lines",
            line=dict(
                color=COLORS["signal"],
                width=2,
            ),
        )
    )

    fig.add_hline(
        y=0,
        line_color=COLORS["neutral"],
        line_width=1,
    )

    fig.update_layout(
        title=f"MACD — {symbol}",
        xaxis_title="Data",
        yaxis_title="Valor do indicador",
        template="plotly_white",
        hovermode="x unified",
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        barmode="relative",
        margin=dict(l=40, r=20, t=70, b=40),
    )

    fig.add_annotation(
        text=context,
        xref="paper",
        yref="paper",
        x=0,
        y=1.10,
        showarrow=False,
        font=dict(size=11, color="#475569"),
        align="left",
    )

    return fig


def create_cumulative_return_chart(
    df: pd.DataFrame,
    symbol: str,
    context: str,
    return_col: str = "Simple_Return",
) -> go.Figure:
    """
    Cria curva de retorno acumulado a partir dos retornos simples.
    """
    validate_columns(df, ["Date", return_col])

    result = df.copy()

    result["Cumulative_Return"] = (
        (1 + result[return_col].fillna(0)).cumprod() - 1
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=result["Date"],
            y=result["Cumulative_Return"] * 100,
            name="Retorno acumulado",
            mode="lines",
            line=dict(
                color=COLORS["price"],
                width=2.5,
            ),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.12)",
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}<br>"
                "Retorno acumulado: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=0,
        line_color=COLORS["neutral"],
        line_width=1,
    )

    fig.update_layout(
        title=f"Retorno Acumulado — {symbol}",
        xaxis_title="Data",
        yaxis_title="Retorno acumulado (%)",
        template="plotly_white",
        hovermode="x unified",
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=40, r=20, t=70, b=40),
    )

    fig.add_annotation(
        text=context,
        xref="paper",
        yref="paper",
        x=0,
        y=1.10,
        showarrow=False,
        font=dict(size=11, color="#475569"),
        align="left",
    )

    return fig


def create_drawdown_chart(
    df: pd.DataFrame,
    symbol: str,
    context: str,
    drawdown_col: str = "Drawdown",
) -> go.Figure:
    """
    Cria curva de drawdown em percentual.
    """
    validate_columns(df, ["Date", drawdown_col])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df[drawdown_col] * 100,
            name="Drawdown",
            mode="lines",
            line=dict(
                color=COLORS["negative"],
                width=2,
            ),
            fill="tozeroy",
            fillcolor="rgba(220, 38, 38, 0.18)",
            hovertemplate=(
                "Data: %{x|%d/%m/%Y}<br>"
                "Drawdown: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=0,
        line_color=COLORS["neutral"],
        line_width=1,
    )

    fig.update_layout(
        title=f"Drawdown — {symbol}",
        xaxis_title="Data",
        yaxis_title="Queda desde o pico (%)",
        template="plotly_white",
        hovermode="x unified",
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=40, r=20, t=70, b=40),
    )

    fig.add_annotation(
        text=context,
        xref="paper",
        yref="paper",
        x=0,
        y=1.10,
        showarrow=False,
        font=dict(size=11, color="#475569"),
        align="left",
    )

    return fig


def create_returns_histogram(
    df: pd.DataFrame,
    symbol: str,
    context: str,
    return_col: str = "Simple_Return",
) -> go.Figure:
    """
    Cria histograma dos retornos por período.
    """
    validate_columns(df, [return_col])

    returns_pct = df[return_col].dropna() * 100

    fig = px.histogram(
        returns_pct,
        nbins=30,
        labels={
            "value": "Retorno por período (%)",
            "count": "Frequência",
        },
        template="plotly_white",
    )

    fig.update_traces(
        marker_color=COLORS["price"],
        marker_line_color="#1E3A8A",
        marker_line_width=0.5,
    )

    fig.update_layout(
        title=f"Distribuição dos Retornos — {symbol}",
        xaxis_title="Retorno por período (%)",
        yaxis_title="Frequência",
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=40, r=20, t=70, b=40),
    )

    fig.add_annotation(
        text=context,
        xref="paper",
        yref="paper",
        x=0,
        y=1.10,
        showarrow=False,
        font=dict(size=11, color="#475569"),
        align="left",
    )

    return fig