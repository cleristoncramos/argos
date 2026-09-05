# Requisitos — Fase 2 do Argos DataLab

## Objetivo

Evoluir o MVP para oferecer indicadores técnicos, métricas de risco,
comparação entre ativos e visualizações analíticas.

## Requisitos funcionais

- RF01: Permitir informar e analisar múltiplos símbolos.
- RF02: Comparar retornos normalizados entre ativos.
- RF03: Calcular médias móveis simples e exponenciais.
- RF04: Calcular RSI.
- RF05: Calcular MACD e linha de sinal.
- RF06: Calcular retorno acumulado.
- RF07: Calcular retorno médio por período.
- RF08: Calcular volatilidade anualizada.
- RF09: Calcular máximo drawdown.
- RF10: Calcular índice de Sharpe com taxa livre de risco configurável.
- RF11: Exibir gráficos e tabelas comparativas.
- RF12: Exportar dados e métricas da análise.
- RF13: Validar símbolos, períodos e frequência antes do cálculo.
- RF14: Informar que indicadores são descritivos e não recomendação.

## Requisitos não funcionais

- RNF01: Cálculos devem estar isolados em módulos testáveis.
- RNF02: Funções de dados e cálculos devem usar cache quando adequado.
- RNF03: O sistema deve tratar falhas de consulta sem exibir traceback.
- RNF04: Gráficos devem ter título, unidade, período e legenda claros.
- RNF05: A interface deve funcionar em tela desktop e permanecer legível.
- RNF06: Mudanças não podem quebrar o MVP já publicado.