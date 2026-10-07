from datetime import date, datetime

from core.date_validation import validate_date_range

TODAY = date(2026, 10, 7)


def test_valid_range():
    check = validate_date_range(date(2026, 1, 1), date(2026, 10, 1), TODAY)

    assert check.ok is True
    assert check.message == ""


def test_end_today_is_allowed():
    assert validate_date_range(date(2026, 10, 6), TODAY, TODAY).ok is True


def test_start_after_end_is_rejected():
    check = validate_date_range(date(2026, 10, 5), date(2026, 10, 1), TODAY)

    assert check.ok is False
    assert "anterior" in check.message


def test_same_day_is_rejected():
    check = validate_date_range(date(2026, 10, 1), date(2026, 10, 1), TODAY)

    assert check.ok is False
    assert "anterior" in check.message


def test_future_end_is_rejected():
    check = validate_date_range(date(2026, 1, 1), date(2026, 10, 8), TODAY)

    assert check.ok is False
    assert "futuro" in check.message
    assert "07/10/2026" in check.message


def test_missing_dates_are_rejected():
    assert validate_date_range(None, date(2026, 10, 1), TODAY).ok is False
    assert validate_date_range(date(2026, 1, 1), None, TODAY).ok is False
    assert "Informe" in validate_date_range(None, None, TODAY).message


def test_datetime_values_are_accepted():
    check = validate_date_range(
        datetime(2026, 1, 1, 10, 30), datetime(2026, 10, 1, 8, 0), TODAY
    )

    assert check.ok is True


def test_today_defaults_to_current_date():
    assert validate_date_range(date(2000, 1, 1), date(2000, 12, 31)).ok is True
    assert validate_date_range(date(2000, 1, 1), date(9999, 1, 1)).ok is False