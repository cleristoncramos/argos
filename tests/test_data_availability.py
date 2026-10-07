from datetime import date

import pandas as pd

from core.data_availability import (
    assess_availability,
    availability_messages,
    availability_summary,
)


def _dates(start, periods):
    return pd.date_range(start, periods=periods, freq="D")


def test_full_history_has_no_messages():
    a = assess_availability(_dates("2021-11-01", 400), date(2021, 11, 1), date(2022, 12, 5), 40)
    assert not a.shorter_history and not a.stale_end
    assert not a.insufficient and not a.limited
    assert availability_messages(a) == []


def test_shorter_history_detected():
    a = assess_availability(_dates("2023-06-01", 200), date(2021, 11, 1), date(2023, 12, 18), 30)
    assert a.shorter_history and a.start_gap_days > 10
    levels = [level for level, _ in availability_messages(a)]
    assert "warning" in levels


def test_stale_end_detected():
    a = assess_availability(_dates("2021-11-01", 100), date(2021, 11, 1), date(2022, 6, 1), 30)
    assert a.stale_end and a.end_gap_days > 7


def test_insufficient_observations():
    a = assess_availability(_dates("2021-11-01", 5), date(2021, 11, 1), date(2021, 11, 6), 1)
    assert a.insufficient
    messages = availability_messages(a)
    assert messages[0][0] == "error" and len(messages) == 1


def test_limited_observations_info():
    a = assess_availability(_dates("2021-11-01", 100), date(2021, 11, 1), date(2022, 2, 8), 5)
    assert a.limited and not a.insufficient
    assert ("info" in [level for level, _ in availability_messages(a)])


def test_empty_dates_is_insufficient():
    a = assess_availability([], date(2021, 11, 1), date(2022, 1, 1), 0)
    assert a.insufficient and a.available_start is None
    assert availability_summary(a)["available"] == "— a —"


def test_summary_formats_dates():
    a = assess_availability(_dates("2021-11-01", 30), date(2021, 11, 1), date(2021, 11, 30), 30)
    summary = availability_summary(a)
    assert summary["requested"] == "01/11/2021 a 30/11/2021"
    assert "30 diárias" in summary["observations"]