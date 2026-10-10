"""
Textos descritivos da página de Comparação (Plano 2, Bloco 3).

Linguagem descritiva: dizem o que aconteceu no período analisado, sem
ranking de "melhor" ou "pior" e sem recomendação.
"""

HIGHLIGHT_LABELS = {
    "max_return": "Maior retorno acumulado no período analisado",
    "min_return": "Menor retorno acumulado no período analisado",
    "min_drawdown": "Menor queda máxima observada",
    "max_sharpe": "Maior Sharpe no período analisado",
}

LEGEND_HINT = (
    "Dica: clique no nome de um ativo na legenda para ocultá-lo ou exibi-lo; "
    "dois cliques isolam esse ativo."
)

SEASONALITY_COMPARISON_NOTE = (
    "Cada barra é a média do retorno mensal daquele mês do calendário, usando "
    "todos os anos disponíveis de cada ativo. Ativos com históricos de tamanhos "
    "diferentes têm quantidades de anos (N) diferentes, indicadas na tabela. "
    "Médias calculadas com poucos anos variam bastante. O mês em andamento "
    "não entra nas médias."
)