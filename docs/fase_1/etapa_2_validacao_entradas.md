# Fase 1 — Etapa 2: Fortalecimento da Validação de Entradas

## Objetivo

Evitar consultas inválidas, resultados inconsistentes e falhas previsíveis antes ou durante o processamento de dados financeiros.

## Implementação realizada

A validação foi distribuída entre interface, coleta, processamento, cálculos de risco e visualizações.

### Interface

A barra lateral compartilhada valida o período antes de permitir a execução:

- a data inicial deve ser anterior à data final;
- o botão de consulta é desabilitado para período inválido;
- símbolo vazio é bloqueado antes do carregamento;
- o símbolo é normalizado com remoção de espaços externos e conversão para maiúsculas.

### Coleta e processamento

A coleta rejeita símbolos vazios e dados sem identidade reconhecível. O processamento exige a coluna `Date`, preserva somente colunas OHLCV disponíveis e impede frequências não suportadas.

### Métricas e gráficos

As métricas de risco rejeitam valores vazios, não numéricos, zero ou negativos quando a operação exige preços positivos. As funções de visualização verificam as colunas obrigatórias antes de gerar cada gráfico.

## Arquivos relacionados

- `app/ui/sidebar.py`
- `app/ui/state.py`
- `app/main.py`
- `core/data_loader.py`
- `core/data_processor.py`
- `core/risk_metrics.py`
- `core/visualizations.py`
- `tests/test_data_loader.py`
- `tests/test_data_processor.py`
- `tests/test_risk_metrics.py`
- `tests/test_visualizations.py`

## Resultado

Consultas temporalmente inválidas, símbolos vazios, dados estruturais incompletos e valores inadequados para métricas financeiras passaram a ser tratados de maneira controlada.
