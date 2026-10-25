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

from app.ui.page_header import render_page_header
from app.ui.data_info import render_analysis_summary, render_availability_messages
from app.ui.colors import tone_of
from app.ui.tables import date_cell, percent_cell, render_table
from app.ui.what_if import WHAT_IF_CSS, WHAT_IF_HOW_TO_READ, build_what_if_html, format_money
from app.ui.chart_guide import render_chart_guide
from app.ui.llm_explain import asset_name, render_explain_section
from app.ui.sidebar import render_asset_controls
from app.ui.state import initialize_asset_state
from core.assets import ASSETS
from core.currency import currency_info
from core.data_availability import assess_availability
from core.data_quality import assess_data_quality
from app.ui.data_cache import download_active_data
from core.llm_builders import simulation_context
from core.data_processor import (
    aggregate_by_frequency,
    prepare_dataframe,
    select_primary_variable,
)
from core.formatters import format_return_pct
from core.simulation_texts import (
    SIMULATION_ASSUMPTIONS,
    SIMULATION_MANDATORY_TEXT,
    SIMULATION_STRATEGY_CAPTION,
    SIMULATION_WINDOW_LABELS,
)
from core.simulation import (
    SIMULATION_DISCLAIMER,
    WHAT_IF_LOOKBACKS,
    compare_strategies,
    lookback_start,
    non_simulable_reason,
    rolling_window_outcomes,
    simulation_notes,
    summarize_simulation,
    summarize_windows,
    what_if,
)


st.set_page_config(
    page_title="Argos",
    page_icon="📈",
    layout="wide",
)


initialize_asset_state()


render_page_header(
    "views/simulacao_aportes.py",
    "O que teria acontecido com um valor hipotético aplicado de uma só vez ou em aportes periódicos. Descreve o passado e não indica o que fazer.",
)

st.warning(SIMULATION_MANDATORY_TEXT, icon="⚠️")
st.caption(SIMULATION_DISCLAIMER)


# ==========================================================
# Funções auxiliares
# ==========================================================
def format_number(value) -> str:
    """Formata número com 2 casas no padrão brasileiro."""
    if value is None or pd.isna(value):
        return "—"

    return (
        f"{float(value):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def format_date(value) -> str:
    """Formata data como dd/mm/aaaa."""
    parsed = pd.to_datetime(value, errors="coerce")

    if pd.isna(parsed):
        return "—"

    return parsed.strftime("%d/%m/%Y")


def build_path_chart(paths: dict, symbol: str) -> go.Figure:
    """Valor da carteira hipotética ao longo do tempo, por estratégia."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=paths["lump_sum"]["Date"],
            y=paths["lump_sum"]["Portfolio_Value"],
            name="Aporte único",
            mode="lines",
            line=dict(color="#2563EB", width=2.5),
            hovertemplate=(
                "%{x|%d/%m/%Y}<br>Aporte único: %{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=paths["periodic"]["Date"],
            y=paths["periodic"]["Portfolio_Value"],
            name="Aportes periódicos",
            mode="lines",
            line=dict(color="#F59E0B", width=2.5),
            hovertemplate=(
                "%{x|%d/%m/%Y}<br>Aportes periódicos: %{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=paths["periodic"]["Date"],
            y=paths["periodic"]["Invested"],
            name="Total investido (periódicos)",
            mode="lines",
            line=dict(color="#64748B", width=1.5, dash="dot"),
            hovertemplate=(
                "%{x|%d/%m/%Y}<br>Investido: %{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=f"Valor da carteira hipotética — {symbol}",
        xaxis_title="",
        yaxis_title="Valor na moeda do ativo",
        template="plotly_white",
        hovermode="x unified",
        legend_title_text="Séries",
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=40, r=20, t=70, b=40),
    )

    return fig


def build_what_if_chart(result: dict, symbol: str, prefix: str) -> go.Figure:
    """Quanto o valor investido valeria em cada data, desde a compra."""
    path = result["Trajetória"]
    amount = result["Valor investido"]
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=path["Date"],
            y=path["Value"],
            name="Valor do investimento",
            mode="lines",
            line=dict(color="#C8102E", width=2.2),
            fill="tozeroy",
            fillcolor="rgba(200, 16, 46, 0.07)",
            hovertemplate=(
                f"%{{x|%d/%m/%Y}}<br>Valor: {prefix}%{{y:,.2f}}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=amount,
        line_color="#475569",
        line_width=1,
        line_dash="dot",
        annotation_text="Valor investido",
        annotation_position="bottom right",
    )

    low = path["Value"].min()
    high = path["Value"].max()
    padding = (high - low) * 0.08 or amount * 0.05

    fig.update_layout(
        title=f"Quanto o valor investido valeria em cada data — {symbol}",
        xaxis_title="",
        yaxis_title="Valor do investimento",
        yaxis_range=[max(min(low, amount) - padding, 0), max(high, amount) + padding],
        template="plotly_white",
        showlegend=False,
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=40, r=20, t=70, b=40),
        height=340,
    )

    return fig


def build_windows_chart(outcomes: pd.DataFrame, symbol: str) -> go.Figure:
    """Retorno de cada janela histórica, por data inicial."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=outcomes["Start_Date"],
            y=outcomes["Lump_Return"] * 100,
            name="Aporte único",
            mode="lines",
            line=dict(color="#2563EB", width=2),
            hovertemplate=(
                "Início: %{x|%d/%m/%Y}<br>Aporte único: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=outcomes["Start_Date"],
            y=outcomes["Periodic_Return"] * 100,
            name="Aportes periódicos",
            mode="lines",
            line=dict(color="#F59E0B", width=2),
            hovertemplate=(
                "Início: %{x|%d/%m/%Y}<br>Aportes periódicos: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_hline(y=0, line_color="#475569", line_width=1)

    fig.update_layout(
        title=f"Retorno de cada janela histórica — {symbol}",
        xaxis_title="Data de início da janela",
        yaxis_title="Retorno sobre o total investido (%)",
        template="plotly_white",
        hovermode="x unified",
        legend_title_text="Séries",
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#FFFFFF",
        margin=dict(l=40, r=20, t=70, b=40),
    )

    return fig


# ==========================================================
# Controles
# ==========================================================
asset_params = render_asset_controls(
    title="Parâmetros da Simulação",
    button_label="🧪 Carregar histórico",
    button_key="simulation_load_button",
)

symbol = asset_params["symbol"]
start_date = asset_params["start_date"]
end_date = asset_params["end_date"]
frequency = asset_params["frequency"]
load_history = asset_params["submitted"]


with st.sidebar:
    st.divider()
    st.subheader("Valores hipotéticos")

    amount = st.number_input(
        "Valor de cada aporte (moeda do ativo)",
        min_value=1.0,
        value=1000.0,
        step=100.0,
        key="simulation_amount",
        help=(
            "Valor hipotético. No aporte único, o total investido é igual "
            "à soma de todos os aportes periódicos."
        ),
    )

    every = st.slider(
        "Aportar a cada N períodos",
        min_value=1,
        max_value=12,
        value=1,
        key="simulation_every",
        help="O período segue a frequência escolhida (diária, semanal, mensal, semestral ou anual).",
    )

    horizon = st.slider(
        "Duração de cada janela histórica (períodos)",
        min_value=2,
        max_value=120,
        value=12,
        key="simulation_horizon",
        help=(
            "Usada na análise de cenários: o sistema testa todas as datas "
            "de início possíveis e mostra como cada janela terminou."
        ),
    )


# ==========================================================
# Carregamento
# ==========================================================
if load_history:
    if not symbol:
        st.sidebar.error("Selecione um ativo antes de carregar o histórico.")
        st.stop()

    reason = non_simulable_reason(symbol)

    if reason:
        st.session_state["simulation_loaded"] = False
        st.error(
            f"Não é possível simular '{symbol}': {reason}. "
            "Escolha um ativo com preço negociável."
        )
        st.stop()

    with st.spinner("Carregando histórico..."):
        try:
            df_raw = download_active_data(
                symbol=symbol,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                interval="1d",
            )
        except Exception:
            df_raw = None

        if df_raw is None or df_raw.empty:
            st.session_state["simulation_loaded"] = False
            st.error(
                f"Não foi possível carregar dados para '{symbol}' neste "
                "período. Verifique o símbolo e as datas."
            )
            st.stop()

        df_prepared = prepare_dataframe(df_raw)
        # Série diária para a calculadora "Se você tivesse investido";
        # a agregada pela frequência alimenta as estratégias e as janelas.
        df_daily = select_primary_variable(df_prepared)
        df = select_primary_variable(aggregate_by_frequency(df_prepared, frequency))

        availability = assess_availability(
            dates=df_prepared["Date"],
            requested_start=start_date,
            requested_end=end_date,
            period_observations=len(df),
            frequency=frequency,
        )

        if availability.insufficient:
            st.session_state["simulation_loaded"] = False
            render_availability_messages(availability)
            st.stop()

    st.session_state["simulation_loaded"] = True
    st.session_state["simulation_prices"] = df
    st.session_state["simulation_daily"] = df_daily
    st.session_state["simulation_availability"] = availability
    st.session_state["simulation_fetched_at"] = datetime.now()
    st.session_state["simulation_quality"] = assess_data_quality(df_prepared, symbol, start_date)
    st.session_state["simulation_query"] = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "frequency": frequency,
    }


query = st.session_state.get("simulation_query")

if (
    not st.session_state.get("simulation_loaded")
    or query is None
    or "simulation_prices" not in st.session_state
):
    st.info(
        "Escolha o ativo e o período na barra lateral e clique em "
        "**Carregar histórico**. Os valores do aporte podem ser ajustados "
        "depois, sem recarregar os dados."
    )
    st.stop()


prices = st.session_state["simulation_prices"]
symbol = query["symbol"]
frequency = query["frequency"]

try:
    paths = compare_strategies(
        prices,
        periodic_amount=float(amount),
        every=int(every),
    )
except ValueError as error:
    st.error(f"Não foi possível simular este ativo: {error}")
    st.stop()


periodic_summary = summarize_simulation(paths["periodic"])
lump_summary = summarize_simulation(paths["lump_sum"])

render_analysis_summary(
    next((a for a in ASSETS if a["ticker"] == symbol), None),
    st.session_state.get("simulation_availability"),
    st.session_state.get("simulation_fetched_at"),
    [
        ("Ativo", symbol.upper()),
        ("Frequência das estratégias", frequency),
        ("Observações na frequência", f"{len(paths['periodic'])} períodos"),
        (
            "Período usado nas estratégias",
            f"{format_date(paths['periodic']['Date'].iloc[0])} a "
            f"{format_date(paths['periodic']['Date'].iloc[-1])}",
        ),
        ("Premissas", SIMULATION_ASSUMPTIONS[0].upper() + SIMULATION_ASSUMPTIONS[1:]),
    ],
    details_label="Detalhes do processamento e premissas",
    quality_alerts=st.session_state.get("simulation_quality"),
)

for note in simulation_notes(symbol):
    st.caption(f"ℹ️ {note}")


# ==========================================================
# 1. Se você tivesse investido
# ==========================================================
st.header("Se você tivesse investido")

st.markdown(WHAT_IF_HOW_TO_READ)

_currency = currency_info(symbol)
# Índices, taxas e câmbio não têm moeda própria: o valor fica sem prefixo.
money_prefix = _currency.prefix if _currency.kind == "price" else ""

daily = st.session_state.get("simulation_daily", prices)
first_day = pd.Timestamp(daily["Date"].min())
last_day = pd.Timestamp(daily["Date"].max())

# Só oferece prazos cobertos pelo histórico carregado (tolerância de uma
# semana para fins de semana e feriados no início da série).
lookbacks = {
    label: years
    for label, years in WHAT_IF_LOOKBACKS.items()
    if lookback_start(last_day, years) >= first_day - pd.Timedelta(days=7)
}
WHOLE_PERIOD = "Todo o período carregado"
CUSTOM_DATE = "Escolher a data"
period_options = list(lookbacks) + [WHOLE_PERIOD, CUSTOM_DATE]

col_amount, col_period, col_date = st.columns([1.1, 1.1, 1])

with col_amount:
    what_if_amount = st.number_input(
        f"Valor investido ({_currency.label})" if money_prefix else "Valor investido",
        min_value=1.0,
        value=1000.0,
        step=100.0,
        format="%.2f",
        key="what_if_amount",
    )

with col_period:
    period_choice = st.selectbox(
        "Há quanto tempo",
        period_options,
        index=0,
        key="what_if_period",
        help="Os prazos aparecem conforme o histórico carregado na barra lateral.",
    )

with col_date:
    custom_date = st.date_input(
        "Data da compra",
        value=first_day.date(),
        min_value=first_day.date(),
        max_value=(last_day - pd.Timedelta(days=1)).date(),
        format="DD/MM/YYYY",
        key="what_if_date",
        disabled=period_choice != CUSTOM_DATE,
        help="Usada quando o prazo é \"Escolher a data\".",
    )

if period_choice in lookbacks:
    what_if_start = lookback_start(last_day, lookbacks[period_choice])
    period_label = period_choice
elif period_choice == CUSTOM_DATE:
    what_if_start, period_label = pd.Timestamp(custom_date), ""
else:
    what_if_start, period_label = None, ""

try:
    what_if_result = what_if(daily, float(what_if_amount), what_if_start)
except ValueError as error:
    st.info(f"Não foi possível calcular para este prazo: {error}")
else:
    st.markdown(WHAT_IF_CSS, unsafe_allow_html=True)
    st.markdown(
        build_what_if_html(
            what_if_result,
            symbol=symbol.upper(),
            period_label=period_label,
            prefix=money_prefix,
        ),
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        build_what_if_chart(what_if_result, symbol.upper(), money_prefix),
        width="stretch",
    )
    render_chart_guide("simulacao_se_investido")


# ==========================================================
# 2. Aporte único x aportes periódicos
# ==========================================================
st.header("Aporte único ou aportes periódicos")

st.markdown(
    "Mostra o que teria ocorrido com o mesmo total investido de duas formas no "
    f"período carregado: tudo de uma vez no início ou **{format_number(amount)} a cada {int(every)} período(s)** "
    f"({frequency.lower()}). Os valores ficam na barra lateral, em *Valores hipotéticos*."
)

col_lump, col_periodic = st.columns(2)

for column, title, summary in (
    (col_lump, "Aporte único", lump_summary),
    (col_periodic, "Aportes periódicos", periodic_summary),
):
    with column:
        with st.container(border=True):
            st.markdown(f"#### {title}")
            # Ordem de leitura: quanto entrou, quanto valeria e a variação.
            st.metric(
                "Total investido",
                format_money(summary["Total investido"], money_prefix),
            )
            st.metric(
                "Valor final hipotético",
                format_money(summary["Valor final"], money_prefix),
            )
            # A chave dá a classe CSS que pinta o retorno de verde ou vermelho
            # (app/ui/design.py).
            return_tone = tone_of(summary["Retorno sobre o investido"])
            with st.container(key=f"sim_return_{return_tone}_{title.split()[-1].lower()}"):
                st.metric(
                    "Retorno sobre o investido",
                    format_return_pct(summary["Retorno sobre o investido"]),
                )
            st.caption(
                f"Menor retorno ao longo do caminho: "
                f"{format_return_pct(summary['Menor retorno no caminho'])} · "
                f"Aportes realizados: {summary['Número de aportes']}"
            )

st.plotly_chart(
    build_path_chart(paths, symbol.upper()),
    width="stretch",
)
render_chart_guide("simulacao_caminho")

st.caption(SIMULATION_STRATEGY_CAPTION)

render_explain_section(
    lambda: simulation_context(
        paths,
        symbol.upper(),
        frequency,
        _currency.prefix.strip() or _currency.label,
        float(amount),
        int(every),
        periodic_summary,
        lump_summary,
        name=asset_name(symbol),
    ),
    key="simulacao_aportes",
)


# ==========================================================
# 3. Janelas históricas
# ==========================================================
st.header("Como terminaram as diferentes janelas")

st.markdown(
    "O resultado acima depende da data de início. Aqui o sistema testa "
    f"**todas as datas de início possíveis**, cada uma com duração de "
    f"**{int(horizon)} períodos**, e resume como cada janela terminou."
)

try:
    outcomes = rolling_window_outcomes(
        prices,
        horizon=int(horizon),
        every=int(every),
    )
except ValueError as error:
    st.info(
        f"Não há dados suficientes para janelas de {int(horizon)} períodos "
        f"({error}). Reduza a duração ou amplie o período."
    )
    st.stop()

rows = []

for label, column in (
    ("Aporte único", "Lump_Return"),
    ("Aportes periódicos", "Periodic_Return"),
):
    summary = summarize_windows(outcomes, column)

    rows.append(
        {
            "Estratégia": label,
            "Janelas analisadas": summary["Janelas analisadas"],
            SIMULATION_WINDOW_LABELS["Pior janela"]: summary["Pior janela"],
            SIMULATION_WINDOW_LABELS["Início da pior janela"]: summary["Início da pior janela"],
            SIMULATION_WINDOW_LABELS["Mediana"]: summary["Mediana"],
            SIMULATION_WINDOW_LABELS["Melhor janela"]: summary["Melhor janela"],
            SIMULATION_WINDOW_LABELS["Início da melhor janela"]: summary["Início da melhor janela"],
            SIMULATION_WINDOW_LABELS["Janelas com retorno positivo"]: summary["Janelas com retorno positivo"],
        }
    )

windows_table = pd.DataFrame(rows)
return_cell = percent_cell(colored=True, center=True)
render_table(
    windows_table,
    list(windows_table.columns),
    {
        "Janelas analisadas": lambda v: (str(int(v)), "text-align:center;"),
        SIMULATION_WINDOW_LABELS["Pior janela"]: return_cell,
        SIMULATION_WINDOW_LABELS["Início da pior janela"]: date_cell,
        SIMULATION_WINDOW_LABELS["Mediana"]: return_cell,
        SIMULATION_WINDOW_LABELS["Melhor janela"]: return_cell,
        SIMULATION_WINDOW_LABELS["Início da melhor janela"]: date_cell,
        SIMULATION_WINDOW_LABELS["Janelas com retorno positivo"]: percent_cell(center=True),
    },
    max_height=None,
    wrap_header=True,
)

st.plotly_chart(
    build_windows_chart(outcomes, symbol.upper()),
    width="stretch",
)
render_chart_guide("simulacao_janelas")

st.caption(
    "As janelas se sobrepõem, então não são observações independentes. "
    "Os extremos mostram a dispersão de resultados que já ocorreu e não "
    "são limites do que pode ocorrer. Um período curto de queda não prova "
    "que o ativo esteja barato ou caro."
)


# ==========================================================
# Rodapé
# ==========================================================
st.markdown("---")

st.caption(
    "⚠️ Ferramenta com finalidade educacional e de pesquisa. "
    + SIMULATION_DISCLAIMER
)
