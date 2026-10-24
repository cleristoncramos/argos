"""Paleta e helpers de cor padronizados para retornos positivos/negativos."""

import pandas as pd

POSITIVE_FG, POSITIVE_BG = "#4ADE80", "rgba(74,222,128,0.14)"
NEGATIVE_FG, NEGATIVE_BG = "#F87171", "rgba(248,113,113,0.14)"
NEUTRAL_FG, NEUTRAL_BG = "#94A3B8", "rgba(148,163,184,0.14)"

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