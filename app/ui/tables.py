"""Tabela HTML padrão do Argos (cabeçalho fixo, zebra, formatação pt-BR)."""

from html import escape
from typing import Callable

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from app.ui.colors import NEGATIVE_FG, POSITIVE_FG
from core.formatters import format_number_br, format_return_pct

# (texto, estilo CSS da célula)
Cell = tuple[str, str]
Formatter = Callable[[object], Cell]

_RIGHT = "text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;"
_CENTER = "text-align:center;white-space:nowrap;"
_LEFT = "text-align:left;white-space:nowrap;"

_TABLE_CSS = (
    ".argos-table-wrapper{width:100%;overflow-x:auto;border:1px solid #E2E8F0;border-radius:12px;"
    "background:#FFFFFF;margin-bottom:1rem;box-shadow:0 1px 3px 0 rgba(0,0,0,0.1);}"
    ".argos-table{width:100%;border-collapse:collapse;font-size:0.9rem;color:#334155;"
    "font-family:'Inter',Arial,sans-serif;}"
    ".argos-table th{background-color:#F8FAFC;color:#1E293B;text-align:center;vertical-align:middle;"
    "font-weight:700;padding:14px 16px;border-bottom:3px solid #97B7C4;border-right:1px solid #E2E8F0;"
    "white-space:nowrap;position:sticky;top:0;z-index:10;}"
    ".argos-table th:last-child{border-right:none;}"
    ".argos-table td{vertical-align:middle;padding:12px 16px;border-bottom:1px solid #E2E8F0;"
    "border-right:1px solid #E2E8F0;}"
    ".argos-table td:last-child{border-right:none;}"
    ".argos-table tr:last-child td{border-bottom:none;}"
    ".argos-row-even{background-color:#FFFFFF;}"
    ".argos-row-odd{background-color:#F1F5F9;}"
    ".argos-table tbody tr:hover{background-color:#E2E8F0;}"
)


# ----------------------------------------------------------
# Formatadores de célula (a formatação numérica vem de core/formatters.py)
# ----------------------------------------------------------
def date_cell(value) -> Cell:
    parsed = pd.to_datetime(value, errors="coerce")
    return ("—" if pd.isna(parsed) else parsed.strftime("%d/%m/%Y")), _CENTER


def number_cell(value) -> Cell:
    return format_number_br(value), _RIGHT


def percent_cell(*, fraction: bool = True, colored: bool = False) -> Formatter:
    """
    fraction=True: valor em fração (0,12 -> 12,00%).
    fraction=False: valor já em percentual (12 -> 12,00%).
    colored=True: verde para positivo, vermelho para negativo.
    """
    def _format(value) -> Cell:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return "—", _RIGHT
        if pd.isna(number):
            return "—", _RIGHT

        text = format_return_pct(number if fraction else number / 100)
        style = _RIGHT
        if colored and number != 0:
            color = POSITIVE_FG if number > 0 else NEGATIVE_FG
            style += f"color:{color};font-weight:600;"
        return text, style
    return _format


def text_cell(value) -> Cell:
    return ("—" if value is None or pd.isna(value) else str(value)), _LEFT


# ----------------------------------------------------------
# Construção e renderização
# ----------------------------------------------------------
def build_table_html(
    dataframe: pd.DataFrame,
    columns: list[str],
    formatters: dict[str, Formatter] | None = None,
    *,
    header_labels: dict[str, str] | None = None,
    max_height: int | None = None,
    min_width: int = 800,
) -> str:
    """HTML da tabela. Todo texto de célula e cabeçalho é escapado."""
    formatters = formatters or {}
    header_labels = header_labels or {}

    header = "".join(
        f"<th>{escape(str(header_labels.get(c, c)))}</th>" for c in columns
    )

    rows = []
    for position, record in enumerate(dataframe[columns].to_dict(orient="records")):
        cells = []
        for column in columns:
            text, style = formatters.get(column, text_cell)(record.get(column))
            cells.append(f'<td style="{style}">{escape(str(text))}</td>')
        row_class = "argos-row-even" if position % 2 == 0 else "argos-row-odd"
        rows.append(f'<tr class="{row_class}">{"".join(cells)}</tr>')

    height_style = f"max-height:{max_height}px;overflow-y:auto;" if max_height else ""
    return (
        f"<style>{_TABLE_CSS}</style>"
        f'<div class="argos-table-wrapper" style="{height_style}">'
        f'<table class="argos-table" style="min-width:{min_width}px;">'
        f"<thead><tr>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def render_table(
    dataframe: pd.DataFrame | None,
    columns: list[str],
    formatters: dict[str, Formatter] | None = None,
    *,
    header_labels: dict[str, str] | None = None,
    max_height: int | None = 400,
    min_width: int = 800,
    iframe: bool = False,
) -> None:
    """
    iframe=True isola a tabela em um iframe com rolagem própria
    (usado quando há muitas colunas, como em Indicadores Técnicos).
    """
    if dataframe is None or dataframe.empty:
        st.info("Não há dados disponíveis para exibição.")
        return

    html = build_table_html(
        dataframe, columns, formatters,
        header_labels=header_labels, max_height=max_height, min_width=min_width,
    )
    if iframe:
        components.html(html, height=(max_height or 400) + 20, scrolling=True)
    else:
        st.markdown(html, unsafe_allow_html=True)