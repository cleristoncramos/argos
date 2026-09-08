# Fase 2 — Etapa 5: Melhoria das Visualizações

## Objetivo

Aprimorar a interpretação dos resultados por meio de gráficos consistentes, contexto explícito, validação de dados e padrões visuais reutilizáveis.

## Implementação realizada

O módulo `core/visualizations.py` centraliza gráficos e regras visuais reutilizáveis para as páginas analíticas.

## Padronização visual

A implementação define uma paleta centralizada para:

- preços;
- médias móveis;
- Bandas de Bollinger;
- volume;
- RSI;
- MACD e sinal;
- valores positivos, negativos e neutros.

Os gráficos usam tema claro, fundos padronizados, grade leve, margens consistentes, títulos, eixos identificados e contexto de ativo, período e frequência.

## Validação antes dos gráficos

A função `validate_columns()` verifica se todas as colunas necessárias existem antes de criar cada visualização. Dados estruturais incompletos não geram gráficos enganosos.

## Gráficos implementados

- linha de preço com indicadores;
- candles OHLC;
- volume;
- RSI;
- MACD;
- retorno acumulado;
- drawdown;
- histograma de retornos;
- evolução normalizada Base 100;
- heatmap de correlação;
- gráfico de variação percentual;
- mapa sazonal Ano × Mês.

## Decisões de leitura

- candles usam verde para alta e vermelho para baixa;
- RSI possui referências superior, inferior e neutra;
- MACD diferencia valores positivos e negativos;
- retorno acumulado e drawdown usam preenchimento até zero;
- `hovertemplate` informa data e valor;
- o candle oculta o seletor temporal inferior para reduzir ruído;
- o mapa sazonal apresenta valores percentuais em cada célula.

## Arquivos relacionados

- `core/visualizations.py`
- `app/main.py`
- `app/pages/2_Comparacao_de_Ativos.py`
- `app/pages/3_Indicadores_Tecnicos.py`
- `app/pages/4_Risco_e_Retorno.py`
- `tests/test_visualizations.py`
- `docs/etapa_6_integracao_interface.md`
- `docs/etapa_8_validacao_academica.md`

## Resultado

A plataforma passou a apresentar resultados analíticos com consistência visual, contexto explícito e proteção contra dados incompletos.
