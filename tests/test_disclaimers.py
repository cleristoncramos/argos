from core.disclaimers import (
    FORBIDDEN_PHRASES,
    contains_forbidden_phrase,
    get_metric_explanation,
)


def test_clean_text_returns_none():
    assert contains_forbidden_phrase(
        "Este período apresentou retorno histórico positivo."
    ) is None


def test_forbidden_phrase_detected_case_insensitive():
    assert contains_forbidden_phrase("Este é o MOMENTO DE COMPRAR!") == "momento de comprar"


def test_known_metric_explanation():
    explanation = get_metric_explanation("sharpe")
    assert explanation is not None
    assert explanation.unit.startswith("Índice")


def test_unknown_metric_returns_none():
    assert get_metric_explanation("inexistente") is None


def test_forbidden_list_is_lowercase():
    assert all(p == p.lower() for p in FORBIDDEN_PHRASES)