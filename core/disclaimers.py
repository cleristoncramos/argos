"""
Textos padronizados e funções de formatação neutra para a camada de
educação financeira do Argos DataLab.

Este módulo é deliberadamente livre de dependências de UI (sem Streamlit).
Ele define O QUE dizer; o módulo app/ui/disclaimers.py define COMO exibir.

Princípio orientador (reunião de 30/09/2026 com o orientador):
o sistema é uma ferramenta de pesquisa, educação financeira e apoio à
interpretação de dados -- nunca uma recomendação de investimento.
"""

from dataclasses import dataclass


# ==========================================================
# Avisos padrão (texto fixo, reutilizado em várias páginas)
# ==========================================================

INVESTMENT_DISCLAIMER = (
    "Esta ferramenta possui finalidade educacional e de pesquisa. "
    "Dados históricos, indicadores técnicos e métricas de risco não "
    "constituem recomendação, indicação ou aconselhamento formal de "
    "investimento. Resultados passados não garantem rentabilidade ou "
    "desempenho futuro."
)

PROFILE_LIMITATION_DISCLAIMER = (
    "Esta ferramenta não avalia renda, objetivos financeiros, dívidas, "
    "horizonte de tempo ou tolerância individual a risco. As informações "
    "apresentadas são de caráter geral e histórico, e não substituem a "
    "orientação de um profissional habilitado."
)

METHODOLOGY_LIMITATIONS_INTRO = (
    "As limitações abaixo fazem parte da metodologia do projeto e devem "
    "ser consideradas na interpretação de qualquer resultado exibido "
    "nesta página."
)

SIMULATION_DISCLAIMER_TEMPLATE = (
    "Simulação histórica: se um aporte hipotético de {valor} tivesse sido "
    "realizado no período selecionado, o valor teria evoluído conforme os "
    "dados históricos apresentados. Essa simulação não representa "
    "recomendação nem previsão de resultados futuros."
)


# ==========================================================
# Vocabulário proibido e substituições neutras
# ==========================================================
# Usado tanto como referência de revisão manual quanto, futuramente,
# como checagem automatizada em testes de conteúdo (Fase 8).

FORBIDDEN_PHRASES = [
    "compre aqui",
    "venda aqui",
    "momento de comprar",
    "momento de vender",
    "ativo barato",
    "ativo caro",
    "oportunidade de compra",
    "recomendamos",
    "recomendação de compra",
    "recomendação de venda",
    "sinal de compra",
    "sinal de venda",
]

NEUTRAL_PHRASING_EXAMPLES = {
    "ponto_alta_historica": "Este período apresentou retorno histórico positivo.",
    "ponto_queda_historica": "Este ponto coincidiu com uma queda histórica.",
    "padrao_sem_garantia": "Esse padrão observado no histórico não garante repetição futura.",
    "melhor_retorno_comparacao": "Maior retorno histórico no período analisado.",
    "menor_retorno_comparacao": "Menor retorno histórico no período analisado.",
    "menor_drawdown_comparacao": "Menor queda máxima histórica registrada no período.",
}


def contains_forbidden_phrase(text: str) -> str | None:
    """
    Verifica se um texto contém alguma expressão que soe como
    recomendação de investimento. Retorna a frase encontrada (em
    minúsculas) ou None se o texto estiver limpo.

    Uso pretendido: testes de conteúdo (Fase 8) e revisão manual ao
    escrever novos textos de interface.
    """
    normalized = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in normalized:
            return phrase
    return None


# ==========================================================
# Metadados de métrica: usados para gerar tooltips/textos
# educativos de forma consistente entre páginas.
# ==========================================================

@dataclass(frozen=True)
class MetricExplanation:
    """Explicação educativa padronizada de uma métrica financeira."""
    name: str
    unit: str
    description: str
    higher_is: str  # "geralmente desejável", "geralmente indesejável", "depende do contexto"
    limitation: str


METRIC_EXPLANATIONS: dict[str, MetricExplanation] = {
    "retorno_total": MetricExplanation(
        name="Retorno Total",
        unit="Percentual (%)",
        description=(
            "Mede a variação acumulada do ativo entre o início e o fim "
            "do período analisado."
        ),
        higher_is="depende do contexto",
        limitation=(
            "Um retorno positivo indica valorização no intervalo "
            "observado, mas não representa garantia de resultado futuro. "
            "O valor depende fortemente do período escolhido."
        ),
    ),
    "retorno_medio": MetricExplanation(
        name="Retorno Médio por Período",
        unit="Percentual (%)",
        description=(
            "Média aritmética dos retornos simples na frequência "
            "selecionada (diária, semanal ou mensal)."
        ),
        higher_is="depende do contexto",
        limitation=(
            "Médias são sensíveis a valores extremos (outliers) e não "
            "capturam a ordem em que os retornos ocorreram."
        ),
    ),
    "volatilidade": MetricExplanation(
        name="Volatilidade Anualizada",
        unit="Percentual (%)",
        description=(
            "Mede a dispersão dos retornos em torno da média, anualizada "
            "a partir da frequência escolhida."
        ),
        higher_is="geralmente indesejável",
        limitation=(
            "Volatilidade mais alta indica maior oscilação histórica, "
            "mas não determina sozinha se o ativo é bom ou ruim -- "
            "depende do objetivo e do horizonte do investidor."
        ),
    ),
    "drawdown_maximo": MetricExplanation(
        name="Drawdown Máximo",
        unit="Percentual (%)",
        description=(
            "Representa a maior perda observada entre um pico histórico "
            "e o menor valor posterior, antes de uma recuperação."
        ),
        higher_is="geralmente indesejável",
        limitation=(
            "É uma medida importante de risco de perda, mas reflete um "
            "único evento histórico -- não indica a frequência com que "
            "perdas dessa magnitude ocorrem."
        ),
    ),
    "sharpe": MetricExplanation(
        name="Índice de Sharpe",
        unit="Índice (adimensional)",
        description=(
            "Relaciona o retorno obtido ao risco assumido, considerando "
            "a taxa livre de risco informada pelo usuário."
        ),
        higher_is="geralmente desejável",
        limitation=(
            "Quanto maior o índice, melhor foi a relação histórica entre "
            "retorno e volatilidade -- mas o resultado depende do "
            "período analisado, da taxa livre de risco escolhida e do "
            "fator de anualização usado no cálculo."
        ),
    ),
    "win_rate": MetricExplanation(
        name="Win Rate (Períodos Positivos)",
        unit="Percentual (%)",
        description=(
            "Indica a proporção de períodos com retorno positivo dentro "
            "da frequência selecionada."
        ),
        higher_is="depende do contexto",
        limitation=(
            "Um win rate alto não garante maior retorno total, pois "
            "perdas eventuais podem ser maiores que os ganhos acumulados."
        ),
    ),
}


def get_metric_explanation(key: str) -> MetricExplanation | None:
    """Busca a explicação educativa de uma métrica pelo identificador interno."""
    return METRIC_EXPLANATIONS.get(key)