"""Período disponível do ativo para limitar as datas do menu lateral (DL2-B)."""

from datetime import date

import pandas as pd
import pytest

from core.asset_range import (
    AssetRange,
    adjusted_note,
    clamp_period,
    demo_range,
    online_range,
    range_caption,
    range_from_frame,
)

HOJE = date(2026, 11, 13)


def _frame(datas):
    return pd.DataFrame({"Date": pd.to_datetime(datas), "Close": range(len(datas))})


def test_range_from_frame():
    assert range_from_frame(_frame(["2020-07-13", "2026-11-12"])) == AssetRange(date(2020, 7, 13), date(2026, 11, 12))
    assert range_from_frame(None) is None and range_from_frame(pd.DataFrame()) is None
    assert range_from_frame(pd.DataFrame({"Close": [1]})) is None
    assert range_from_frame(pd.DataFrame({"Date": ["x"]})) is None


def test_demo_range_pelo_manifesto():
    manifesto = {"assets": [{"ticker": "BTC-USD", "first_date": "2020-12-01", "last_date": "2026-10-23"},
                            {"ticker": "RUIM", "first_date": "ontem"}]}
    assert demo_range("btc-usd", manifesto) == AssetRange(date(2020, 12, 1), date(2026, 10, 23))
    assert demo_range("RUIM", manifesto) is None
    assert demo_range("XYZ", manifesto) is None


def test_online_range_refina_o_primeiro_dia_no_primeiro_mes():
    chamadas = []

    def fetch(symbol, start, end, interval):
        chamadas.append((start, end, interval))
        if interval == "1mo":
            return _frame(["2020-07-01", "2026-11-01"])
        if start == "2026-11-01":
            return _frame(["2026-11-03", "2026-11-12"])
        return _frame(["2020-07-13", "2020-07-14"])

    rng = online_range("AVAX-USD", fetch, HOJE)
    assert rng == AssetRange(date(2020, 7, 13), date(2026, 11, 12))      # último pregão, não o rótulo mensal
    assert chamadas[0][2] == "1mo" and chamadas[1] == ("2020-07-01", "2020-08-15", "1d")
    assert chamadas[2] == ("2026-11-01", "2026-11-14", "1d")


def test_online_range_falhas_devolvem_none_ou_o_mes():
    def falha(*a):
        raise RuntimeError("sem rede")
    assert online_range("X", falha, HOJE) is None
    assert online_range("X", lambda *a: pd.DataFrame(), HOJE) is None

    def so_mensal(symbol, start, end, interval):
        return _frame(["2019-03-01", "2027-01-01"]) if interval == "1mo" else pd.DataFrame()
    assert online_range("X", so_mensal, HOJE) == AssetRange(date(2019, 3, 1), HOJE)


def test_clamp_period():
    rng = AssetRange(date(2020, 7, 13), date(2026, 11, 12))
    assert clamp_period(date(2016, 12, 1), date(2026, 11, 13), rng) == (date(2020, 7, 13), date(2026, 11, 13), True)
    assert clamp_period(date(2021, 1, 1), date(2026, 11, 13), rng) == (date(2021, 1, 1), date(2026, 11, 13), False)
    assert clamp_period(date(2016, 1, 1), date(2016, 6, 1), rng) == (date(2020, 7, 13), date(2020, 7, 13), True)
    assert clamp_period(date(2016, 1, 1), date(2026, 1, 1), None) == (date(2016, 1, 1), date(2026, 1, 1), False)


def test_textos_do_menu():
    rng = AssetRange(date(2020, 7, 13), date(2026, 11, 12))
    assert range_caption(rng) == "📅 Dados disponíveis de 13/07/2020 a 12/11/2026."
    nota = adjusted_note(rng, date(2016, 12, 1))
    assert "13/07/2020" in nota and "01/12/2016" in nota and nota.startswith("⚠️")
