import streamlit as st

st.set_page_config(
    page_title="Sobre o Projeto | Argos DataLab",
    page_icon="ℹ️",
    layout="wide",
)

st.title("ℹ️ Sobre o Argos DataLab")

st.markdown(
    """
    ## Propósito

    O **Argos DataLab** é uma ferramenta educacional e de pesquisa para
    análise exploratória de dados históricos do mercado financeiro.

    A aplicação permite consultar ativos, explorar séries temporais,
    visualizar variações entre períodos e observar padrões sazonais.

    ## Funcionalidades do MVP

    - Consulta de dados históricos por símbolo de ativo.
    - Seleção de período e frequência de análise.
    - Estatísticas descritivas e retorno acumulado.
    - Gráficos de evolução temporal e variação percentual.
    - Mapa de calor anual e mensal.
    - Exportação dos dados processados em CSV.
    - Validação básica da qualidade dos dados.

    ## Limitações

    Os resultados representam análises de dados históricos e não constituem
    recomendação, aconselhamento ou garantia de investimento. O desempenho
    passado não garante resultados futuros.

    ## Contexto acadêmico

    Projeto de Iniciação Tecnológica — PIBITI UFPI 2026–2027.

    Título do plano de trabalho: *Análise de Dados para Apoio à Tomada de
    Decisão em Investimentos no Mercado Financeiro*.

    Orientador: Arlino Henrique Magalhães de Araújo.
    """
)