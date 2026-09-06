import streamlit as st


st.set_page_config(
    page_title="Sobre o Projeto | Argos DataLab",
    page_icon="📊",
    layout="wide",
)


st.title("📊 Sobre o Argos DataLab")


st.header("Propósito")

st.write(
    "O Argos DataLab é uma ferramenta educacional e de pesquisa para "
    "análise exploratória de dados históricos do mercado financeiro."
)

st.write(
    "A aplicação permite consultar ativos, explorar séries temporais, "
    "visualizar variações entre períodos e observar padrões sazonais."
)


st.header("Funcionalidades do MVP")

st.markdown(
    """
- Consulta de dados históricos por símbolo de ativo.
- Seleção de período e frequência de análise.
- Estatísticas descritivas e retorno acumulado.
- Gráficos de evolução temporal e variação percentual.
- Mapa de calor anual e mensal.
- Exportação dos dados processados em CSV.
- Validação básica da qualidade dos dados.
"""
)


st.header("Limitações")

st.write(
    "Os resultados representam análises de dados históricos e não "
    "constituem recomendação, aconselhamento ou garantia de investimento. "
    "O desempenho passado não garante resultados futuros."
)


st.header("Contexto acadêmico")

st.write(
    "Projeto de Iniciação em Desenvolvimento Tecnológico e Inovação "
    "(PIBITI UFPI 2026–2027)."
)

st.write(
    "Título: Análise de Dados para Apoio à Tomada de Decisão em "
    "Investimentos no Mercado Financeiro."
)

st.write(
    "Orientador: Arlino Henrique Magalhães de Araújo."
)