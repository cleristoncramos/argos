"""Modo da explicação por IA com e sem o modo de dados salvos."""

import pytest

from core import llm_mode, llm_service


def test_modes_match_service_constants():
    assert set(llm_mode.MODES) == set(llm_service.MODES)


@pytest.mark.parametrize(
    "configured, expected",
    [
        (None, "off"),
        ("", "off"),
        ("off", "off"),
        ("demo", "demo"),
        ("live", "live"),
        ("LIVE", "live"),
        ("  demo ", "demo"),
        ("qualquer", "off"),
    ],
)
def test_without_demo_data_mode_follows_configuration(configured, expected):
    assert llm_mode.resolve_mode(configured, False, False) == expected
    assert llm_mode.resolve_mode(configured, False, True) == expected


@pytest.mark.parametrize("configured", [None, "", "demo", "qualquer"])
def test_demo_data_mode_defaults_to_saved_answers(configured):
    assert llm_mode.resolve_mode(configured, True, False) == "demo"
    assert llm_mode.resolve_mode(configured, True, True) == "demo"


def test_demo_data_mode_keeps_explicit_off():
    assert llm_mode.resolve_mode("off", True, False) == "off"
    assert llm_mode.resolve_mode("OFF", True, True) == "off"


def test_demo_data_mode_never_calls_api_unless_recording():
    assert llm_mode.resolve_mode("live", True, False) == "demo"


def test_demo_data_mode_allows_live_only_to_record():
    assert llm_mode.resolve_mode("live", True, True) == "live"