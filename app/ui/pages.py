"""
Ordem oficial das páginas do sistema.

O menu principal (`app/main.py`) e os atalhos "Primeiros passos" da página
inicial são montados a partir desta lista, para nunca divergirem. As análises
vêm primeiro, na ordem do fluxo de estudo, e "Sobre o Projeto" fica no fim,
como informação institucional. O botão "Get Started" abre a primeira página.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PageSpec:
    path: str          # relativo a app/main.py
    title: str
    icon: str
    description: str   # texto do cartão "Primeiros passos"


HOME_PAGE = PageSpec("views/home.py", "Início", "🏠", "")

MENU_PAGES = (
    PageSpec("views/analise_individual.py", "Análise Individual", "📈",
             "Preço, volatilidade mensal e sazonalidade de um ativo ao longo do tempo."),
    PageSpec("views/comparacao_ativos.py", "Comparação de Ativos", "⚖️",
             "De 2 a 5 ativos em base 100, correlação e resumo de risco e retorno."),
    PageSpec("views/indicadores_tecnicos.py", "Indicadores Técnicos", "📉",
             "Médias móveis, Bandas de Bollinger, RSI e MACD com guias de leitura."),
    PageSpec("views/risco_retorno.py", "Risco e Retorno", "⚠️",
             "Volatilidade, Sharpe, drawdown máximo e distribuição dos retornos."),
    PageSpec("views/simulacao_aportes.py", "Simulação de Aportes", "🧪",
             "E se eu tivesse investido? Simulação histórica, sem custos nem impostos."),
    PageSpec("views/panorama_catalogo.py", "Panorama do Catálogo", "🗂️",
             "Todos os ativos de um grupo no mesmo período: variação, volatilidade e queda máxima."),
    PageSpec("views/sobre_projeto.py", "Sobre o Projeto", "📊",
             "Objetivos, metodologia de cálculo, fontes de dados e limitações."),
)

# Destino do botão "Get Started": a primeira página do menu.
START_PAGE = MENU_PAGES[0]
