"""Card de métrica reutilizável, com tooltip educativo opcional."""

from html import escape

import streamlit as st

from app.ui.disclaimers import render_metric_tooltip_icon
from app.ui.colors import tone_style


def build_metric_card_html(
    title: str,
    value: str,
    *,
    tooltip: str = "",
    metric_key: str | None = None,
    subtitle: str | None = None,
    badge: tuple[str, str] | None = None,
    value_size: str = "1.8rem",
) -> str:
    """
    `value` é HTML confiável (pode conter <span> colorido).
    `badge` = (texto, tom), com tom em {"positive","negative","neutral"}.
    `metric_key` usa a explicação central de core/disclaimers.py;
    sem ele, `tooltip` é texto livre.
    """
    if metric_key:
        tooltip_html = render_metric_tooltip_icon(metric_key)
    elif tooltip:
        tooltip_html = (
            f'<span title="{escape(tooltip, quote=True)}" '
            'style="cursor:help;color:#94a3b8;margin-left:6px;font-size:0.95rem;">&#9432;</span>'
        )
    else:
        tooltip_html = ""

    subtitle_html = (
        f'<div style="color:#64748b;font-size:0.8rem;margin-top:6px;">{escape(subtitle)}</div>'
        if subtitle else ""
    )

    badge_html = ""
    if badge:
        text, tone = badge
        fg, bg = tone_style(tone)
        badge_html = (
            '<div style="margin-top:12px;">'
            f'<span style="font-size:0.85rem;font-weight:600;padding:4px 8px;border-radius:6px;'
            f'display:inline-block;background-color:{bg};color:{fg};">{escape(text)}</span>'
            "</div>"
        )

    return (
        '<div style="background:linear-gradient(180deg,#ffffff 0%,#f8fafc 100%);'
        "border:1px solid #e2e8f0;border-radius:12px;padding:20px;"
        "box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);display:flex;flex-direction:column;height:100%;\">"
        '<div style="color:#64748b;font-size:0.75rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.5px;margin-bottom:8px;display:flex;align-items:center;">'
        f"{escape(title)} {tooltip_html}</div>"
        f'<div style="color:#0f172a;font-size:{value_size};font-weight:700;line-height:1.2;'
        f"font-family:'Inter',sans-serif;letter-spacing:-0.5px;\">{value}</div>"
        f"{subtitle_html}{badge_html}</div>"
    )


def render_metric_card(
    title: str,
    value: str,
    *,
    tooltip: str = "",
    metric_key: str | None = None,
    subtitle: str | None = None,
    badge: tuple[str, str] | None = None,
    value_size: str = "1.8rem",
) -> None:
    st.markdown(
        build_metric_card_html(
            title, value,
            tooltip=tooltip, metric_key=metric_key,
            subtitle=subtitle, badge=badge, value_size=value_size,
        ),
        unsafe_allow_html=True,
    )