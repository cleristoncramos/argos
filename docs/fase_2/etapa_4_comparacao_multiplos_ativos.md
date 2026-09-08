# Fase 2 — Etapa 4: Comparação de Múltiplos Ativos

## Objetivo

Permitir comparação exploratória entre ativos de diferentes classes usando desempenho relativo, risco e correlação histórica.

## Escopo

A página aceita de dois a cinco símbolos separados por vírgula.

Exemplo:

```text
BTC-USD,AAPL,USDBRL=X,SPY
```

## Fluxo por ativo

```text
coleta
→ preparação
→ agregação por frequência
→ Close como Value
→ retornos
→ drawdown
→ armazenamento da série tratada
```

A comparação só é produzida quando ao menos dois ativos possuem dados válidos. Símbolos sem dados são listados em aviso sem interromper comparações ainda viáveis.

## Recursos

- normalização em Base 100;
- tabela de preços alinhada por data;
- tabela de retornos;
- matriz de correlação;
- resumo individual;
- volatilidade, drawdown, percentual positivo e Sharpe por ativo;
- cartões de destaques;
- tabela de dados normalizados;
- download CSV.

## Alinhamento temporal

As séries usam união completa por data, preservando lacunas de negociação. A correlação considera somente pares de retornos válidos e coincidentes.

## Base 100

Cada ativo inicia em 100 em sua primeira observação válida:

```text
120 representa valorização acumulada de 20%
80 representa desvalorização acumulada de 20%
```

## Limitações

- correlação não implica causalidade;
- dados históricos não representam previsão;
- calendários de negociação distintos podem gerar lacunas;
- a anualização é configurada por frequência e pode exigir refinamento por classe de ativo.

## Arquivos relacionados

- `app/pages/2_Comparacao_de_Ativos.py`
- `core/comparison.py`
- `core/risk_metrics.py`
- `tests/test_comparison.py`
- `docs/evidencias/cenario_d_comparacao/comparacao_ativos_base_100.csv`

## Resultado

O Argos DataLab evoluiu de análise individual para comparação multiclasse, reunindo retorno, risco, drawdown e correlação.
