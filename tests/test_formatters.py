from core.formatters import format_brl


def test_format_brl_formats_thousands_and_decimal_separator():
    assert format_brl(9350.53) == "9.350,53"


def test_format_brl_formats_large_value():
    assert format_brl(42156.90) == "42.156,90"


def test_format_brl_supports_prefix():
    assert format_brl(9350.53, "R$ ") == "R$ 9.350,53"


def test_format_brl_handles_none():
    assert format_brl(None) == "—"


def test_format_brl_handles_invalid_value():
    assert format_brl("invalid") == "—"