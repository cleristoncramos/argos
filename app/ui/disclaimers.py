"""
Componentes de UI reutilizáveis para avisos, disclaimers e explicações
educativas padronizadas, usados em todas as páginas do Argos DataLab.
"""

import streamlit as st

from core.disclaimers import (
    INVESTMENT_DISCLAIMER,
    METHODOLOGY_LIMITATIONS_INTRO,
    PROFILE_LIMITATION_DISCLAIMER,
    SIMULATION_DISCLAIMER_TEMPLATE,
    MetricExplanation,
    get_metric_explanation,
)


def render_footer_disclaimer() -> None:
    """
    Renderiza o aviso padrão de rodapé, já usado em todas as páginas
    (substitui os textos de rodapé escritos manualmente em cada view).
    """
    st.markdown("---")
    st.caption(f"⚠️ {INVESTMENT_DISCLAIMER}")


def render_profile_limitation_notice() -> None:
    """
    Renderiza o aviso de que a ferramenta não avalia perfil individual
    do usuário (renda, objetivos, dívidas, tolerância a risco).
    Usar em páginas que apresentem simulações ou análises de risco.
    """
    st.info(f"ℹ️ {PROFILE_LIMITATION_DISCLAIMER}")


def render_methodology_limitations(bullet_points: list[str]) -> None:
    """
    Renderiza uma seção padronizada de "Limitações metodológicas" como
    um expander, para ser incluída ao final de páginas analíticas.

    `bullet_points` deve conter as limitações específicas daquela
    página (ex: "O cálculo do Sharpe depende da taxa livre de risco
    informada pelo usuário").
    """
    with st.expander("📐 Limitações metodológicas desta análise", expanded=False):
        st.markdown(METHODOLOGY_LIMITATIONS_INTRO)
        st.markdown("")
        for point in bullet_points:
            st.markdown(f"- {point}")


def render_simulation_disclaimer(formatted_value: str) -> None:
    """
    Renderiza o disclaimer específico de simulações históricas de
    aporte (Fase 7), com o valor hipotético já formatado em texto
    (ex: "R$ 1.000,00").
    """
    text = SIMULATION_DISCLAIMER_TEMPLATE.format(valor=formatted_value)
    st.info(f"💡 {text}")


def render_metric_tooltip_icon(metric_key: str) -> str:
    """
    Retorna o HTML de um ícone de informação com tooltip nativo (atributo
    `title`), pronto para ser embutido dentro de um card de métrica
    já renderizado via st.markdown(..., unsafe_allow_html=True).

    Se a métrica não tiver explicação cadastrada, retorna string vazia
    (fail-safe: nunca quebra a renderização do card por falta de texto).
    """
    explanation = get_metric_explanation(metric_key)
    if explanation is None:
        return ""

    tooltip_text = (
        f"{explanation.description} "
        f"Unidade: {explanation.unit}. "
        f"{explanation.limitation}"
    )
    # Normaliza aspas para não quebrar o atributo HTML title="..."
    tooltip_text = tooltip_text.replace('"', "'")

    return (
        f'<span title="{tooltip_text}" '
        'style="cursor: help; color: #94a3b8; margin-left: 6px; '
        'font-size: 0.95rem;">&#9432;</span>'
    )


def render_metric_explanation_block(metric_key: str) -> None:
    """
    Renderiza o bloco completo de explicação de uma métrica (nome,
    unidade, descrição, se maior/menor é desejável e limitação), em
    formato de texto corrido -- para uso em expanders educativos ou
    em uma futura página de glossário (Fase 4).
    """
    explanation = get_metric_explanation(metric_key)
    if explanation is None:
        return

    st.markdown(f"**{explanation.name}** · {explanation.unit}")
    st.markdown(explanation.description)
    st.caption(f"Valores mais altos: {explanation.higher_is}.")
    st.caption(f"Limitação: {explanation.limitation}")