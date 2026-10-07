from pathlib import Path

from core.assets import ASSETS
from core.catalog_notice import CATALOG_DISCLAIMER_TEXT, CATALOG_SELECTION_TEXT

DOC_PATH = Path(__file__).resolve().parents[1] / "docs" / "catalogo-de-ativos.md"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _tickers_from_doc(text: str) -> list[str]:
    section = text.split("Lista consolidada dos 120 tickers", 1)[1]
    block = section.split("```text", 1)[1].split("```", 1)[0]
    return [line.strip() for line in block.splitlines() if line.strip()]


def test_doc_ticker_list_matches_catalog():
    assert _tickers_from_doc(_read_doc()) == [a["ticker"] for a in ASSETS]


def test_doc_contains_selection_texts():
    normalized = " ".join(_read_doc().split())
    assert " ".join(CATALOG_SELECTION_TEXT.split()) in normalized
    assert " ".join(CATALOG_DISCLAIMER_TEXT.split()) in normalized