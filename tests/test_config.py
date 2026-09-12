from core.config import (
    ANNUALIZATION_FACTORS,
    config,
)


def test_annualization_factors_have_expected_frequencies():
    assert ANNUALIZATION_FACTORS["Diário"] == 252
    assert ANNUALIZATION_FACTORS["Semanal"] == 52
    assert ANNUALIZATION_FACTORS["Mensal"] == 12


def test_config_has_frequencies():
    assert hasattr(config, "FREQUENCIES")
    assert len(config.FREQUENCIES) > 0


def test_config_frequencies_are_strings():
    assert all(
        isinstance(frequency, str)
        for frequency in config.FREQUENCIES
    )