"""Modal de informações acadêmicas, aberto pelo botão da página inicial."""

import streamlit as st

from app.ui.landing import (
    ACADEMIC_MODAL_CSS,
    build_academic_header_html,
    build_data_sources_html,
    build_identification_html,
    build_name_story_html,
    build_technologies_html,
    catalog_stats,
    institutional_logo_uri,
)
from core.assets import ASSETS


@st.dialog("Informações acadêmicas", width="large")
def show_academic_dialog() -> None:
    st.markdown(ACADEMIC_MODAL_CSS, unsafe_allow_html=True)
    logos = {"UFPI": institutional_logo_uri("UFPI"), "CEAD": institutional_logo_uri("CEAD")}
    st.markdown(build_academic_header_html(logos), unsafe_allow_html=True)

    identification, name, technologies, data = st.tabs(
        ["Identificação", "Por que Argos DataLab", "Tecnologias", "Bases de dados"]
    )
    with identification:
        st.markdown(build_identification_html(), unsafe_allow_html=True)
    with name:
        st.markdown(build_name_story_html(), unsafe_allow_html=True)
    with technologies:
        st.markdown(build_technologies_html(), unsafe_allow_html=True)
    with data:
        st.markdown(build_data_sources_html(catalog_stats(ASSETS)), unsafe_allow_html=True)

    st.caption(
        "Projeto com finalidade exclusivamente acadêmica, educacional e de desenvolvimento "
        "tecnológico. Os logotipos pertencem às respectivas instituições e identificam apenas "
        "o vínculo acadêmico."
    )
