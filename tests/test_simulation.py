import numpy as np
import pandas as pd
import pytest

from core.simulation import (
    SIMULATION_DISCLAIMER,
    WHAT_IF_LOOKBACKS,
    compare_strategies,
    lookback_start,
    non_simulable_reason,
    rolling_window_outcomes,
    simulate_lump_sum,
    simulate_periodic,
    simulation_notes,
    summarize_simulation,
    summarize_windows,
    what_if,
)


def make_prices(values, start="2024-01-31"):
    dates = pd.date_range(start, periods=len(values), freq="ME")
    return pd.DataFrame({"Date": dates, "Value": values})


# ---------- aporte único ----------

def test_lump_sum_doubles_when_price_doubles():
    path = simulate_lump_sum(make_prices([100.0, 150.0, 200.0]), 1000.0)

    assert path["Invested"].tolist() == [1000.0, 1000.0, 1000.0]
    assert path["Portfolio_Value"].iloc[-1] == pytest.approx(2000.0)
    assert path["Return"].iloc[-1] == pytest.approx(1.0)
    assert path["Result"].iloc[-1] == pytest.approx(1000.0)


def test_lump_sum_constant_price_has_zero_return():
    path = simulate_lump_sum(make_prices([50.0, 50.0, 50.0]), 500.0)

    assert (path["Return"] == 0).all()


# ---------- aportes periódicos ----------

def test_periodic_every_period_uses_each_price():
    # unidades: 100/100 + 100/50 + 100/100 = 4 ; valor final = 4 * 100
    path = simulate_periodic(make_prices([100.0, 50.0, 100.0]), 100.0)

    assert path["Invested"].iloc[-1] == pytest.approx(300.0)
    assert path["Units"].iloc[-1] == pytest.approx(4.0)
    assert path["Portfolio_Value"].iloc[-1] == pytest.approx(400.0)
    assert path["Return"].iloc[-1] == pytest.approx(1 / 3)


def test_periodic_every_two_skips_observations():
    path = simulate_periodic(
        make_prices([100.0, 50.0, 100.0]), 100.0, every=2
    )

    assert path["Contribution"].tolist() == [100.0, 0.0, 100.0]
    assert path["Invested"].iloc[-1] == pytest.approx(200.0)
    assert path["Portfolio_Value"].iloc[-1] == pytest.approx(200.0)


def test_periodic_sorts_dates_and_drops_missing():
    df = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                ["2024-03-31", "2024-01-31", "2024-02-29", "2024-04-30"]
            ),
            "Value": [100.0, 100.0, np.nan, 100.0],
        }
    )

    path = simulate_periodic(df, 10.0)

    assert len(path) == 3
    assert path["Date"].is_monotonic_increasing


# ---------- comparação ----------

def test_compare_strategies_uses_same_total_invested():
    result = compare_strategies(make_prices([100.0, 80.0, 120.0, 110.0]), 100.0)

    periodic = result["periodic"]
    lump = result["lump_sum"]

    assert periodic["Invested"].iloc[-1] == pytest.approx(400.0)
    assert lump["Invested"].iloc[-1] == pytest.approx(400.0)
    # aporte único: 400 a 100, valor final 400 * 110/100
    assert lump["Portfolio_Value"].iloc[-1] == pytest.approx(440.0)


def test_summarize_simulation_values():
    path = simulate_periodic(make_prices([100.0, 50.0, 100.0]), 100.0)

    summary = summarize_simulation(path)

    assert summary["Total investido"] == pytest.approx(300.0)
    assert summary["Valor final"] == pytest.approx(400.0)
    assert summary["Resultado"] == pytest.approx(100.0)
    assert summary["Número de aportes"] == 3
    # após o 2º aporte: 3 unidades a 50 = 150 sobre 200 investidos
    assert summary["Menor retorno no caminho"] == pytest.approx(-0.25)


# ---------- janelas históricas ----------

def test_rolling_windows_lump_return_constant_growth():
    prices = [100.0, 110.0, 121.0, 133.1]
    outcomes = rolling_window_outcomes(make_prices(prices), horizon=1)

    assert len(outcomes) == 3
    assert outcomes["Lump_Return"].tolist() == pytest.approx([0.10] * 3)
    assert outcomes["Contributions"].tolist() == [2, 2, 2]


def test_rolling_windows_periodic_matches_simulation():
    prices = [100.0, 50.0, 100.0, 80.0, 120.0]
    df = make_prices(prices)

    outcomes = rolling_window_outcomes(df, horizon=2)
    expected = simulate_periodic(df.iloc[0:3], 1.0)["Return"].iloc[-1]

    assert outcomes["Periodic_Return"].iloc[0] == pytest.approx(expected)


def test_summarize_windows_worst_and_best():
    prices = [100.0, 110.0, 99.0, 150.0]
    outcomes = rolling_window_outcomes(make_prices(prices), horizon=1)

    summary = summarize_windows(outcomes)

    assert summary["Janelas analisadas"] == 3
    assert summary["Pior janela"] == pytest.approx(99.0 / 110.0 - 1)
    assert summary["Melhor janela"] == pytest.approx(150.0 / 99.0 - 1)
    assert summary["Início da pior janela"] == outcomes["Start_Date"].iloc[1]
    assert summary["Início da melhor janela"] == outcomes["Start_Date"].iloc[2]
    assert summary["Janelas com retorno positivo"] == pytest.approx(2 / 3)


def test_summarize_windows_requires_data():
    with pytest.raises(ValueError):
        summarize_windows(pd.DataFrame())

    with pytest.raises(ValueError):
        summarize_windows(None)

    with pytest.raises(ValueError):
        summarize_windows(pd.DataFrame({"x": [1]}))


# ---------- validações ----------

@pytest.mark.parametrize("amount", [0, -5, float("nan"), float("inf")])
def test_invalid_amount_is_rejected(amount):
    with pytest.raises(ValueError):
        simulate_lump_sum(make_prices([1.0, 2.0]), amount)

    with pytest.raises(ValueError):
        simulate_periodic(make_prices([1.0, 2.0]), amount)


@pytest.mark.parametrize("every", [0, -1, 1.5])
def test_invalid_every_is_rejected(every):
    with pytest.raises(ValueError):
        simulate_periodic(make_prices([1.0, 2.0, 3.0]), 10.0, every=every)

    with pytest.raises(ValueError):
        rolling_window_outcomes(make_prices([1.0, 2.0, 3.0]), 1, every=every)


@pytest.mark.parametrize("horizon", [0, -2, 1.5, 3, 10])
def test_invalid_horizon_is_rejected(horizon):
    with pytest.raises(ValueError):
        rolling_window_outcomes(make_prices([1.0, 2.0, 3.0]), horizon)


def test_invalid_prices_are_rejected():
    with pytest.raises(ValueError):
        simulate_lump_sum(None, 10.0)

    with pytest.raises(ValueError):
        simulate_lump_sum(pd.DataFrame(), 10.0)

    with pytest.raises(ValueError):
        simulate_lump_sum(pd.DataFrame({"Date": [1], "Other": [1]}), 10.0)

    with pytest.raises(ValueError):
        simulate_lump_sum(make_prices([10.0]), 10.0)

    with pytest.raises(ValueError):
        simulate_lump_sum(make_prices([10.0, 0.0, 5.0]), 10.0)

    with pytest.raises(ValueError):
        simulate_lump_sum(make_prices([10.0, -3.0]), 10.0)


# ---------- avisos ----------

@pytest.mark.parametrize("symbol", ["^TNX", "^irx", " ^FVX ", "^TYX", "^VIX"])
def test_non_simulable_tickers_have_reason(symbol):
    assert non_simulable_reason(symbol)


@pytest.mark.parametrize("symbol", ["AAPL", "BTC-USD", "^GSPC", "GC=F", "BIL"])
def test_simulable_tickers_have_no_reason(symbol):
    assert non_simulable_reason(symbol) is None


def test_simulation_notes_by_asset_type():
    assert simulation_notes("AAPL") == []
    assert len(simulation_notes("^GSPC")) == 1
    assert len(simulation_notes("GC=F")) == 1
    assert len(simulation_notes("USDBRL=X")) == 1


def test_disclaimer_states_limits():
    text = SIMULATION_DISCLAIMER.lower()

    assert "não é previsão" in text
    assert "não é recomendação" in text
    assert "dividendos" in text


# ---------- calculadora "Se você tivesse investido" ----------

def make_daily(values, start="2020-01-01", freq="D"):
    dates = pd.date_range(start, periods=len(values), freq=freq)
    return pd.DataFrame({"Date": dates, "Value": values})


def test_what_if_doubles_and_tracks_extremes():
    result = what_if(make_prices([100.0, 80.0, 250.0, 200.0]), 1000.0)

    assert result["Valor final"] == pytest.approx(2000.0)
    assert result["Resultado"] == pytest.approx(1000.0)
    assert result["Retorno total"] == pytest.approx(1.0)
    assert result["Menor valor"] == pytest.approx(800.0)
    assert result["Maior valor"] == pytest.approx(2500.0)
    assert result["Data do menor valor"] == pd.Timestamp("2024-02-29")
    assert result["Preço na compra"] == 100.0 and result["Preço final"] == 200.0
    assert result["Trajetória"]["Value"].iloc[0] == pytest.approx(1000.0)
    # Menos de 1 ano: não anualiza.
    assert result["Retorno anualizado"] is None


def test_what_if_annualizes_over_one_year():
    # 2 anos e um dia com o preço quadruplicando: ~100% ao ano.
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2020-01-01", "2022-01-02"]),
        "Value": [10.0, 40.0],
    })
    result = what_if(df, 500.0)

    assert result["Anos"] == pytest.approx(732 / 365.25)
    assert result["Retorno anualizado"] == pytest.approx(4 ** (365.25 / 732) - 1)


def test_what_if_starts_at_first_observation_on_or_after_date():
    df = make_daily([10.0, 20.0, 40.0, 30.0])
    result = what_if(df, 100.0, start_date="2020-01-02")

    assert result["Data da compra"] == pd.Timestamp("2020-01-02")
    assert result["Valor final"] == pytest.approx(150.0)


def test_what_if_rejects_late_start_and_bad_amount():
    df = make_daily([10.0, 20.0, 30.0])

    with pytest.raises(ValueError, match="2 observações"):
        what_if(df, 100.0, start_date="2020-01-03")
    with pytest.raises(ValueError):
        what_if(df, 0.0)


def test_lookback_start_and_options():
    assert lookback_start("2025-06-15 16:00", 3) == pd.Timestamp("2022-06-15")
    assert lookback_start("2024-02-29", 1) == pd.Timestamp("2023-02-28")
    assert list(WHAT_IF_LOOKBACKS.values()) == [1, 2, 3, 5, 10]
    with pytest.raises(ValueError):
        lookback_start("2025-01-01", 0)
