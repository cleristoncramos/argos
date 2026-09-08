# Fase 2 — Etapa 2: Indicadores Técnicos

## Objetivo

Ampliar o Argos DataLab com análise técnica exploratória baseada em indicadores configuráveis e visualizações associadas.

## Implementação realizada

A página `app/pages/3_Indicadores_Tecnicos.py` integra coleta, preparação, agregação, cálculo, gráficos, tabela e exportação.

Foram implementados:

- médias móveis simples;
- médias móveis exponenciais;
- Bandas de Bollinger;
- RSI;
- MACD, linha de sinal e histograma;
- volume;
- gráfico de candles;
- gráfico de preço com indicadores;
- exportação CSV.

## Regras de cálculo

As funções de `core/indicators.py` operam sobre uma cópia do DataFrame e retornam colunas adicionais.

- SMA: média móvel de janela configurável.
- EMA: média móvel exponencial com `adjust=False`.
- RSI: calculado por ganhos e perdas médios; ausência de perdas resulta em RSI 100 e ausência de ganhos resulta em RSI 0.
- MACD: EMA curta menos EMA longa, com linha de sinal e histograma.
- Bollinger: média móvel com limites formados por múltiplos do desvio-padrão.

## Frequência

A série é agregada antes dos cálculos quando a frequência é semanal ou mensal. Para cada período:

- abertura: primeiro valor;
- máxima: maior valor;
- mínima: menor valor;
- fechamento: último valor;
- volume: soma.

Em frequência mensal, candles são substituídos por linha de fechamento.

## Arquivos relacionados

- `app/pages/3_Indicadores_Tecnicos.py`
- `core/indicators.py`
- `core/visualizations.py`
- `tests/test_indicators.py`
- `tests/test_visualizations.py`
- `docs/evidencias/cenario_f_indicadores/BTC-USD_indicadores.csv`

## Resultado

O Argos DataLab passou a permitir análise técnica configurável, visualização de indicadores e exportação de resultados.
