import streamlit as st

from core.chart_guides import GUIDE_FIELDS, GUIDE_LABELS, chart_guide
from core.edu_layer import edu_layer_enabled


def render_chart_guide(chart_id: str) -> None:
    """Botão discreto "Como ler este gráfico" com o roteiro fixo do gráfico."""
    if not edu_layer_enabled():
        return

    guide = chart_guide(chart_id)

    with st.expander("ℹ️ Como ler este gráfico", expanded=False):
        for field in GUIDE_FIELDS:
            st.markdown(f"**{GUIDE_LABELS[field]}.** {guide[field]}")