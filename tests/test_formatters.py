import math

import pytest

from core.formatters import (
    format_brl,
    format_number_br,
    format_return_pct,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (9350.53, "9.350,53"),
        (42156.90, "42.156,90"),
        (0, "0,00"),
        (-1234.5, "-1.234,50"),
        (1.005, "1,00"),
        ("2500.5", "2.500,50"),
    ],
)
def test_format_number_br_formats_valid_values(
    value,
    expected,
):
    assert format_number_br(value) == expected


def test_format_number_br_supports_prefix():
    assert format_number_br(
        9350.53,
        prefix="R$ ",
    ) == "R$ 9.350,53"


@pytest.mark.parametrize(
    "value",
    [
        None,
        "invalid",
        [],
        {},
        float("nan"),
        math.nan,
    ],
)
def test_format_number_br_returns_dash_for_invalid_values(
    value,
):
    assert format_number_br(value) == "—"


def test_format_brl_delegates_to_format_number_br():
    assert format_brl(9350.53) == "9.350,53"
    assert format_brl(
        9350.53,
        prefix="R$ ",
    ) == "R$ 9.350,53"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.20, "20,00%"),
        (-0.15, "-15,00%"),
        (0.0, "0,00%"),
        (1.0, "100,00%"),
        ("0.125", "12,50%"),
        (1.2345, "123,45%"),
    ],
)
def test_format_return_pct_formats_decimal_values(
    value,
    expected,
):
    assert format_return_pct(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        None,
        "invalid",
        [],
        {},
        float("nan"),
        math.nan,
    ],
)
def test_format_return_pct_returns_dash_for_invalid_values(
    value,
):
    assert format_return_pct(value) == "—"