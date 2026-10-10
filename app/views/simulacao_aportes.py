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
import plotly.graph_objects as go
import streamlit as st

from app.ui.sidebar import render_asset_controls
from app.ui.state import initialize_asset_state
from core.data_loader import download_active_data
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
    compare_strategies,
    non_simulable_reason,
    rolling_window_outcomes,
    simulation_notes,
    summarize_simulation,
    summarize_windows,
)


st.set_page_config(
    page_title="Argos DataLab",
    page_icon="📈",
    layout="wide",
)


initialize_asset_state()


st.title("🧪 Simulação Histórica de Aportes")

st.markdown(
    "<p style='font-size: 1.1rem; color: #475569; margin-bottom: 1rem;'>"
    "Veja o que teria acontecido historicamente com um valor hipotético, "
    "aplicado de uma só vez ou em aportes periódicos. É uma ferramenta "
    "de estudo: ela descreve o passado e não indica o que fazer."
    "</p>",
    unsafe_allow_html=True,
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
    title="⚙️ Parâmetros da Simulação",
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
        help="O período segue a frequência escolhida (diária, semanal ou mensal).",
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

        df = prepare_dataframe(df_raw)
        df = aggregate_by_frequency(df, frequency)
        df = select_primary_variable(df)

    st.session_state["simulation_loaded"] = True
    st.session_state["simulation_prices"] = df
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

for note in simulation_notes(symbol):
    st.caption(f"ℹ️ {note}")


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

first_date = paths["periodic"]["Date"].iloc[0]
last_date = paths["periodic"]["Date"].iloc[-1]

with st.expander(
    f"✅ Histórico carregado para {symbol.upper()}. Clique para ver os detalhes.",
    expanded=False,
):
    st.markdown(f"**Ativo:** {symbol.upper()}")
    st.markdown(
        f"**Período efetivamente usado:** {format_date(first_date)} a "
        f"{format_date(last_date)} | **Frequência:** {frequency}"
    )
    st.markdown(f"**Observações:** {len(paths['periodic'])}")
    st.markdown("**Premissas:** " + SIMULATION_ASSUMPTIONS)


# ==========================================================
# 1. Resultado histórico
# ==========================================================
st.header("📊 O que teria ocorrido no período")

col_lump, col_periodic = st.columns(2)

for column, title, summary in (
    (col_lump, "Aporte único", lump_summary),
    (col_periodic, "Aportes periódicos", periodic_summary),
):
    with column:
        with st.container(border=True):
            st.subheader(title)
            st.metric(
                "Valor final hipotético",
                format_number(summary["Valor final"]),
            )
            st.metric(
                "Total investido",
                format_number(summary["Total investido"]),
            )
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

st.caption(SIMULATION_STRATEGY_CAPTION)


# ==========================================================
# 2. Janelas históricas
# ==========================================================
st.header("🗓️ Como terminaram as diferentes janelas")

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
            SIMULATION_WINDOW_LABELS["Pior janela"]: format_return_pct(
                summary["Pior janela"]
            ),
            SIMULATION_WINDOW_LABELS["Início da pior janela"]: format_date(
                summary["Início da pior janela"]
            ),
            SIMULATION_WINDOW_LABELS["Mediana"]: format_return_pct(
                summary["Mediana"]
            ),
            SIMULATION_WINDOW_LABELS["Melhor janela"]: format_return_pct(
                summary["Melhor janela"]
            ),
            SIMULATION_WINDOW_LABELS["Início da melhor janela"]: format_date(
                summary["Início da melhor janela"]
            ),
            SIMULATION_WINDOW_LABELS["Janelas com retorno positivo"]: format_return_pct(
                summary["Janelas com retorno positivo"]
            ),
        }
    )

st.table(pd.DataFrame(rows).set_index("Estratégia"))

st.plotly_chart(
    build_windows_chart(outcomes, symbol.upper()),
    width="stretch",
)

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