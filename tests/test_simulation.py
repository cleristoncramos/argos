import numpy as np
import pandas as pd
import pytest

from core.simulation import (
    SIMULATION_DISCLAIMER,
    compare_strategies,
    non_simulable_reason,
    rolling_window_outcomes,
    simulate_lump_sum,
    simulate_periodic,
    simulation_notes,
    summarize_simulation,
    summarize_windows,
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