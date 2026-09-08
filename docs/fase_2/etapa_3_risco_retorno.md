# Fase 2 — Etapa 3: Métricas de Risco e Retorno

## Objetivo

Permitir análise histórica de desempenho considerando retorno, volatilidade, perdas máximas e retorno ajustado ao risco.

## Fluxo analítico

```text
coleta
→ preparação
→ agregação por frequência
→ seleção de Close como Value
→ retornos simples e logarítmicos
→ pico acumulado e drawdown
→ fator de anualização
→ resumo de risco e retorno
```

## Métricas apresentadas

- retorno total;
- retorno médio por período;
- volatilidade anualizada;
- drawdown máximo;
- percentual de períodos positivos;
- índice de Sharpe.

## Fatores de anualização

| Frequência | Fator |
|---|---:|
| Diário | 252 |
| Semanal | 52 |
| Mensal | 12 |

A configuração registra que 252 é aproximação comum para mercados tradicionais; criptoativos podem demandar refinamento futuro para 365 dias.

## Taxa livre de risco

A taxa anual é configurável pela interface e convertida para taxa periódica equivalente:

\[
r_p = (1+r_a)^{1/N} - 1
\]

O valor confirmado fica armazenado junto com a consulta, os dados e as métricas. Assim, alterar o widget após o cálculo não altera retroativamente o Sharpe exibido.

## Visualizações e dados

A página apresenta:

- cartões de métricas;
- curva de retorno acumulado;
- curva de drawdown;
- histograma de retornos;
- tabela explicativa;
- tabela detalhada;
- download CSV.

## Arquivos relacionados

- `app/pages/4_Risco_e_Retorno.py`
- `core/risk_metrics.py`
- `core/analyzer.py`
- `core/data_processor.py`
- `core/config.py`
- `core/visualizations.py`
- `tests/test_risk_metrics.py`
- `docs/evidencias/cenario_e_risco_retorno/BTC-USD_risco_retorno.csv`

## Resultado

A plataforma passou a disponibilizar métricas de risco e retorno com parâmetros explícitos, gráficos e dados exportáveis.
