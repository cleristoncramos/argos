from core.catalog_notice import (
    CATALOG_DISCLAIMER_TEXT,
    CATALOG_SELECTION_TEXT,
    CATALOG_SHORT_NOTE,
)
from core.disclaimers import contains_forbidden_phrase


def test_catalog_texts_use_neutral_language():
    for text in (CATALOG_SELECTION_TEXT, CATALOG_DISCLAIMER_TEXT, CATALOG_SHORT_NOTE):
        assert contains_forbidden_phrase(text) is None


def test_catalog_text_mentions_size_and_classes():
    assert "120" in CATALOG_SELECTION_TEXT
    assert "13 classes" in CATALOG_SELECTION_TEXT