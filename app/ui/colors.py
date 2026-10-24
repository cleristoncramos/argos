"""Paleta e helpers de cor padronizados para retornos positivos/negativos."""

import pandas as pd

POSITIVE_FG, POSITIVE_BG = "#166534", "#dcfce7"
NEGATIVE_FG, NEGATIVE_BG = "#991b1b", "#fee2e2"
NEUTRAL_FG, NEUTRAL_BG = "#475569", "#f1f5f9"

_TONES = {
    "positive": (POSITIVE_FG, POSITIVE_BG),
    "negative": (NEGATIVE_FG, NEGATIVE_BG),
    "neutral": (NEUTRAL_FG, NEUTRAL_BG),
}


def tone_of(value) -> str:
    """'positive', 'negative' ou 'neutral' (zero, nulo ou NaN)."""
    if value is None or pd.isna(value):
        return "neutral"
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def tone_style(tone: str) -> tuple[str, str]:
    """(cor do texto, cor de fundo) para um tom."""
    return _TONES.get(tone, _TONES["neutral"])


def tone_icon(value) -> str:
    return {"positive": "▲", "negative": "▼"}.get(tone_of(value), "−")