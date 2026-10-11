"""
Textos da página de Simulação Histórica (Plano 2, Bloco 4).

Linguagem descritiva: diz o que teria ocorrido no passado, sem previsão,
recomendação ou ranking de "melhor" e "pior".
"""

# Texto obrigatório, palavra por palavra (item 4.1 do Plano 2).
SIMULATION_MANDATORY_TEXT = (
    "Esta é uma simulação histórica hipotética. Ela mostra como um valor teria "
    "evoluído no período selecionado, sem representar previsão, recomendação "
    "ou garantia de resultado futuro."
)

# Premissas exibidas na página (item 4.4).
SIMULATION_ASSUMPTIONS = (
    "compra ao preço de fechamento da observação, sem ajuste por dividendos, "
    "com frações permitidas, sem custos de corretagem, taxas ou impostos, e com "
    "valores na moeda do ativo (sem conversão cambial)."
)

# Rótulos descritivos da tabela de janelas (item 4.3). As chaves são as do
# resumo calculado em core/simulation.py.
SIMULATION_WINDOW_LABELS = {
    "Pior janela": "Menor retorno histórico",
    "Início da pior janela": "Início da janela de menor retorno",
    "Mediana": "Mediana",
    "Melhor janela": "Maior retorno histórico",
    "Início da melhor janela": "Início da janela de maior retorno",
    "Janelas com retorno positivo": "Janelas com retorno positivo",
}

SIMULATION_STRATEGY_CAPTION = (
    "Os dois cenários investem o mesmo total. No aporte único, todo o valor "
    "entra na primeira data; nos periódicos, ele é dividido ao longo do "
    "tempo. Qual deles terminou com maior valor final depende do período "
    "escolhido e não indica o que ocorrerá no futuro."
)