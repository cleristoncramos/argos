"""
Roteiro fixo "Como ler este gráfico" (Plano 2, Bloco 5).

Cada gráfico ou bloco analítico tem quatro partes curtas: o que mede, o que
mostra, o principal cuidado e o que não permite concluir. Os textos são
descritivos (sem recomendação, previsão ou ranking) e servem também como
conteúdo de reserva da camada de explicação assistida (Bloco 7).
"""

from typing import Dict

GUIDE_FIELDS = ("mede", "mostra", "cuidado", "nao_permite")

GUIDE_LABELS = {
    "mede": "O que mede",
    "mostra": "O que mostra",
    "cuidado": "Principal cuidado",
    "nao_permite": "O que não permite concluir",
}

CHART_GUIDES: Dict[str, Dict[str, str]] = {
    # ---------------------------------------------------------------- Análise Individual
    "evolucao_temporal": {
        "mede": "O valor de fechamento do ativo em cada data do período, na moeda do ativo.",
        "mostra": "A trajetória do valor ao longo do tempo, com seus trechos de alta e de queda.",
        "cuidado": "A escala do eixo e o período escolhido mudam a impressão visual. Os valores não incluem dividendos.",
        "nao_permite": "Concluir o que ocorrerá depois nem se o valor atual está alto ou baixo.",
    },
    "volatilidade_mensal": {
        "mede": "A intensidade das oscilações dos retornos em cada mês, anualizada.",
        "mostra": "Quais meses tiveram oscilação maior ou menor; as barras em destaque são os meses de maior oscilação do período.",
        "cuidado": "Volatilidade mede o tamanho das oscilações, não a direção. Meses com poucos dados são menos representativos.",
        "nao_permite": "Dizer se houve ganho ou perda no mês, nem estimar a oscilação futura.",
    },
    "variacao_percentual": {
        "mede": "A variação de cada período em relação ao período imediatamente anterior.",
        "mostra": "A sequência de variações, com os períodos de alta e de queda lado a lado.",
        "cuidado": "Não é o retorno acumulado. A frequência escolhida (diária, semanal ou mensal) muda o tamanho das barras.",
        "nao_permite": "Concluir que uma sequência de altas ou quedas continuará.",
    },
    "mapa_sazonal": {
        "mede": "O retorno de cada mês em cada ano, pelo último fechamento do mês em relação ao mês anterior.",
        "mostra": "Como cada mês se comportou em cada ano; células vazias indicam meses sem dados.",
        "cuidado": "Cada célula vem de um único ano. O mês em andamento aparece no mapa, mas não entra nas médias.",
        "nao_permite": "Concluir que um mês do calendário tende a se repetir.",
    },
    "media_mensal": {
        "mede": "A média dos retornos de cada mês do calendário, nos anos disponíveis.",
        "mostra": "O comportamento agregado de cada mês ao longo do histórico.",
        "cuidado": "A média esconde a dispersão entre anos e usa poucos anos de histórico, o que a torna instável.",
        "nao_permite": "Tratar a média como padrão fixo ou como projeção.",
    },
    "recorte_anos": {
        "mede": "A média do retorno mensal nos anos escolhidos, comparada com a média de todos os anos, em pontos percentuais.",
        "mostra": "Em quais meses os anos escolhidos ficaram acima ou abaixo da média geral, com mediana, proporção de anos positivos e número de anos (N).",
        "cuidado": "Recortes com poucos anos geram médias instáveis. Observe o N de cada mês.",
        "nao_permite": "Explicar a causa da diferença nem concluir que ela se repetirá.",
    },
    "janela_retorno": {
        "mede": "O retorno composto do fechamento do mês de entrada ao fechamento do mês de saída, em cada ano.",
        "mostra": "Como a janela terminou em cada ano e qual foi a média e a mediana entre os anos.",
        "cuidado": "Anos sem os dois fechamentos ficam de fora. O cálculo não inclui custos, impostos nem dividendos.",
        "nao_permite": "Concluir que repetir essas datas de entrada e saída produzirá resultado semelhante.",
    },
    # ---------------------------------------------------------------- Comparação
    "base_100": {
        "mede": "A evolução de cada ativo normalizada para 100 na data inicial.",
        "mostra": "O crescimento relativo dos ativos, comparável mesmo quando os preços têm escalas diferentes.",
        "cuidado": "O resultado depende da data inicial. Ativos em moedas diferentes não têm variação cambial incorporada.",
        "nao_permite": "Ordenar ativos por qualidade nem supor que a posição relativa se manterá.",
    },
    "correlacao": {
        "mede": "O grau em que os retornos de dois ativos variaram juntos, de -1 a 1, usando apenas retornos coincidentes.",
        "mostra": "Quais pares de ativos se moveram no mesmo sentido ou em sentidos opostos no período.",
        "cuidado": "O valor muda com o período e com a frequência escolhidos.",
        "nao_permite": "Concluir que um ativo causa o movimento do outro ou que a relação continuará.",
    },
    "sazonalidade_comparada": {
        "mede": "A média do retorno mensal de cada mês do calendário, para cada ativo, usando todos os anos disponíveis.",
        "mostra": "O comportamento médio de cada mês, lado a lado entre os ativos, com o número de anos (N) de cada um.",
        "cuidado": "Ativos com históricos de tamanhos diferentes têm N diferentes, e médias com poucos anos variam muito.",
        "nao_permite": "Indicar qual ativo terá maior retorno em um mês nem prever o comportamento futuro.",
    },
    # ---------------------------------------------------------------- Risco e Retorno
    "retorno_acumulado": {
        "mede": "O ganho ou a perda acumulados desde a data inicial do período.",
        "mostra": "A trajetória do retorno acumulado, com o maior e o menor valor marcados.",
        "cuidado": "O resultado depende da data inicial escolhida.",
        "nao_permite": "Concluir qual será o retorno em períodos seguintes.",
    },
    "drawdown": {
        "mede": "A queda do valor em relação ao maior valor atingido anteriormente.",
        "mostra": "A profundidade e a duração das quedas ocorridas no período.",
        "cuidado": "A maior queda observada vale só para o período analisado e não é um limite.",
        "nao_permite": "Estimar a queda máxima futura nem o tempo de recuperação.",
    },
    "distribuicao_retornos": {
        "mede": "A frequência dos retornos do período em cada faixa percentual.",
        "mostra": "Como os retornos se distribuíram: onde se concentraram e quão extremos foram os casos raros.",
        "cuidado": "O formato depende da frequência escolhida. As barras mostram contagens, não probabilidades futuras.",
        "nao_permite": "Calcular a chance de um resultado ocorrer daqui para frente.",
    },
    # ---------------------------------------------------------------- Indicadores Técnicos
    "candles": {
        "mede": "A abertura, a máxima, a mínima e o fechamento de cada período.",
        "mostra": "A amplitude e a direção do movimento de cada período.",
        "cuidado": "A cor indica apenas se o fechamento ficou acima ou abaixo da abertura.",
        "nao_permite": "Identificar sinais de compra ou venda.",
    },
    "preco_indicadores": {
        "mede": "O valor de fechamento junto com médias móveis e Bandas de Bollinger calculadas a partir do próprio histórico.",
        "mostra": "A suavização do preço pelas médias e a faixa de oscilação em torno da média.",
        "cuidado": "Os indicadores reagem com atraso e mudam conforme a janela escolhida.",
        "nao_permite": "Tratar cruzamentos de médias ou toques nas bandas como sinais de compra ou venda.",
    },
    "volume": {
        "mede": "A quantidade negociada em cada período.",
        "mostra": "Os períodos de maior e de menor atividade de negociação.",
        "cuidado": "O volume não é comparável entre ativos ou mercados diferentes e pode não existir para índices e câmbio.",
        "nao_permite": "Concluir a direção do preço a partir do volume.",
    },
    "rsi": {
        "mede": "A relação entre as altas e as quedas recentes, em uma escala de 0 a 100.",
        "mostra": "A intensidade dos movimentos recentes.",
        "cuidado": "As linhas de 30 e 70 são convenções, não limites; o indicador pode permanecer fora delas por muito tempo.",
        "nao_permite": "Tratar o valor como sinal automático de compra ou venda.",
    },
    "macd": {
        "mede": "A diferença entre duas médias móveis exponenciais e a sua linha de sinal.",
        "mostra": "Quando as médias se aproximam ou se afastam uma da outra.",
        "cuidado": "Por ser derivado de médias, reage com atraso aos movimentos do preço.",
        "nao_permite": "Tratar cruzamentos como sinal automático de compra ou venda.",
    },
    "atr": {
        "mede": "A amplitude média das variações de preço em uma janela, na unidade do preço.",
        "mostra": "Se a amplitude das variações aumentou ou diminuiu ao longo do tempo.",
        "cuidado": "Está na unidade do preço, então não é comparável entre ativos de preços diferentes.",
        "nao_permite": "Indicar a direção do preço.",
    },
    "volatilidade_movel": {
        "mede": "A oscilação dos retornos em uma janela móvel, anualizada.",
        "mostra": "Como a intensidade das oscilações variou ao longo do período.",
        "cuidado": "O resultado depende do tamanho da janela escolhida.",
        "nao_permite": "Prever a oscilação futura.",
    },
    # ---------------------------------------------------------------- Simulação histórica
    "simulacao_caminho": {
        "mede": "O valor hipotético da carteira ao longo do tempo, para aporte único e para aportes periódicos.",
        "mostra": "O que teria ocorrido com o valor investido em cada estratégia no período selecionado.",
        "cuidado": "A data de início e a frequência dos aportes mudam o resultado. Não há custos, impostos nem dividendos.",
        "nao_permite": "Concluir que uma estratégia terá resultado maior no futuro.",
    },
    "simulacao_janelas": {
        "mede": "O retorno de cada janela histórica, de acordo com a data em que ela começou.",
        "mostra": "A dispersão de resultados que já ocorreram para a duração escolhida.",
        "cuidado": "As janelas se sobrepõem, então não são observações independentes.",
        "nao_permite": "Tratar os extremos como limites do que pode ocorrer.",
    },
    # ---------------------------------------------------------------- Tendência histórica (Comparação)
    "tendencia_retorno_movel": {
        "mede": "O quanto cada ativo variou nos últimos meses da janela escolhida, a cada mês, pelo último fechamento mensal.",
        "mostra": "Como o retorno de curto, médio ou longo prazo de cada ativo evoluiu e quando ficou positivo ou negativo.",
        "cuidado": "O resultado depende do tamanho da janela, e meses sem observações suficientes ficam vazios.",
        "nao_permite": "Concluir que a tendência observada continuará ou que um ativo seguirá acima do outro.",
    },
    "tendencia_razao": {
        "mede": "A razão entre o desempenho de um ativo e o do ativo de referência desde a data inicial comum (0 indica desempenho igual).",
        "mostra": "Se, desde o início, o ativo acumulou mais ou menos que a referência, e como essa diferença mudou.",
        "cuidado": "A razão depende da data inicial, e um cruzamento por zero pode mudar se o período mudar.",
        "nao_permite": "Concluir que a diferença vista continuará ou prever quando ela se inverterá.",
    },
}


def chart_guide(chart_id: str) -> Dict[str, str]:
    """Roteiro de um gráfico. KeyError se o identificador não existir."""
    if chart_id not in CHART_GUIDES:
        raise KeyError(f"Gráfico sem roteiro de leitura: {chart_id!r}")
    return CHART_GUIDES[chart_id]


def guide_text(chart_id: str) -> str:
    """Roteiro em texto corrido (usado também como conteúdo de reserva)."""
    guide = chart_guide(chart_id)
    return "\n".join(f"{GUIDE_LABELS[field]}: {guide[field]}" for field in GUIDE_FIELDS)