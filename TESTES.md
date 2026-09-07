# Registro de Testes — Argos DataLab

## Ambiente

- Sistema operacional: Windows
- Ambiente Python: venv
- Python: 3.13.15
- Streamlit: 1.63.0
- Pandas: 3.0.5
- Plotly: 7.0.0
- yfinance: 1.7.0
- Fonte de dados: Yahoo Finance, via yfinance
- Data da validação: 05/09/2026
- URL publicada: https://argos-datalab.streamlit.app

## Testes automatizados

Comando:

```powershell
pytest -v
```

Resultado:

```text
14 testes aprovados em 4.02s
```

Quantidade de testes aprovados: 14
Data da execução: 05/09/2026

## Testes manuais

| Cenário | Parâmetros | Resultado esperado | Resultado obtido | Status |
|---|---|---|---|---|
| BTC diário | BTC-USD; 01/01/2020–31/01/2020; Diário | Dados e gráficos carregados | Dados carregados com sucesso; linha e indicadores exibidos | Aprovado |
| BTC mensal | BTC-USD; 01/01/2020–31/12/2020; Mensal | Agregação mensal e heatmap | Dados agregados por mês e heatmap gerado corretamente | Aprovado |
| BTC semanal | BTC-USD; 01/01/2020–31/03/2020; Semanal | Agregação semanal | Série semanal processada sem erro | Aprovado |
| Ação | AAPL; 01/01/2020–31/12/2020; Mensal | Dados alternativos carregados | Dados de AAPL carregados e exibidos normalmente | Aprovado |
| Intervalo inválido | Data inicial >= data final | Consulta bloqueada | Botão de carregamento bloqueado com mensagem de erro | Aprovado |
| Símbolo inválido | ATIVO-INVALIDO-XYZ | Erro controlado | Mensagem de erro exibida e app não quebra | Aprovado |
| Exportação | Consulta válida | CSV baixado | Botão de download disponível e exportação em CSV funcional | Aprovado |

Cenários manuais testados:
- BTC diário
- BTC mensal
- BTC semanal
- Ação AAPL
- Intervalo inválido
- Símbolo inválido
- Exportação em CSV

## Conclusão

O MVP está apto a avançar para a Fase 2. Os testes automatizados passaram e os cenários principais da interface e do processamento de dados foram validados com sucesso.

URL atual publicada: https://argos-datalab.streamlit.app

## Métricas de risco — Drawdown

Arquivo testado:

```text
core/risk_metrics.py
```

Comando executado:

```powershell
pytest .\tests\test_risk_metrics.py -v
```

Cenários cobertos:

- Cálculo do pico acumulado.
- Cálculo do drawdown em relação ao pico anterior.
- Identificação do maior drawdown.
- Série com crescimento contínuo.
- Rejeição de preços iguais a zero ou negativos.
- Rejeição de coluna inexistente.
- DataFrame vazio.

## Validação automatizada — Fase 2

**Data:** 05/09/2026  
**Comando executado:**

```powershell
pytest -v
```

**Resultado:**

```text
56 passed in 5.08s
```

**Ambiente:**

```text
Python 3.13.15
pytest 9.1.1
Windows
```

## Etapa 6 — Persistência de estado e cache

**Data:** 07/09/2026

### Objetivo

Garantir a persistência dos parâmetros e resultados das análises ao navegar entre as páginas do Streamlit, evitando perda de filtros, reinicialização de widgets e inconsistência entre valores exibidos e métricas calculadas.

Também foi validado o cache de dados históricos obtidos pelo Yahoo Finance.

### Implementações concluídas

- Centralização do estado da análise individual com chaves `asset_*`.
- Reutilização de controles compartilhados de ativo, período e frequência nas páginas:
  - `main.py`
  - `3_Indicadores_Tecnicos.py`
  - `4_Risco_e_Retorno.py`
- Isolamento da análise de comparação com chaves `comparison_*`.
- Isolamento dos controles técnicos com chaves `indicators_*`.
- Isolamento dos controles de risco e retorno com chaves `risk_return_*`.
- Persistência dos resultados confirmados de cada página no `st.session_state`.
- Separação entre o estado persistente e o estado temporário dos widgets quando necessário.
- Correção da persistência da taxa livre de risco nas páginas Risco e Retorno e Comparação de Ativos.
- Garantia de que índices de Sharpe, gráficos e legendas usam os mesmos parâmetros confirmados no cálculo.
- Substituição do ticker inválido `USD=BRL` por `USDBRL=X` na comparação de ativos.
- Normalização de símbolos antes da função cacheada, para evitar entradas duplicadas como `aapl`, `AAPL` e ` AAPL `.
- Cache aplicado à coleta de dados históricos com `@st.cache_data(ttl=3600, show_spinner=False)`.

### Estados implementados

#### Análise individual

```text
asset_symbol
asset_start_date
asset_end_date
asset_frequency
asset_query
asset_loaded
asset_df
asset_stats
asset_validation
```

#### Indicadores técnicos

```text
indicators_loaded
indicators_query
indicators_df
indicators_chart_type
indicators_show_sma_short
indicators_sma_short_window
indicators_show_sma_long
indicators_sma_long_window
indicators_show_ema_short
indicators_ema_short_window
indicators_show_ema_long
indicators_ema_long_window
indicators_show_bollinger
indicators_bollinger_window
indicators_bollinger_std
indicators_show_rsi
indicators_rsi_window
indicators_rsi_upper
indicators_rsi_lower
indicators_show_macd
indicators_show_volume
```

#### Risco e retorno

```text
risk_return_loaded
risk_return_query
risk_return_df
risk_return_metrics
risk_return_risk_free_rate_pct
risk_return_risk_free_rate_pct_widget
risk_return_load_button
```

#### Comparação de ativos

```text
comparison_loaded
comparison_query
comparison_asset_data
comparison_failed_symbols
comparison_base_100_table
comparison_price_table
comparison_returns_table
comparison_correlation_matrix
comparison_summary
comparison_symbols_input
comparison_start_date
comparison_end_date
comparison_frequency
comparison_risk_free_rate_pct
comparison_symbols_input_widget
comparison_start_date_widget
comparison_end_date_widget
comparison_frequency_widget
comparison_risk_free_rate_pct_widget
comparison_load_button
```

### Testes manuais executados

- A análise individual mantém ativo, período e frequência após navegar para Sobre o Projeto e retornar.
- Indicadores Técnicos mantém os parâmetros compartilhados, controles próprios, gráficos, tabela e download após navegação.
- Risco e Retorno mantém a taxa livre de risco após navegação.
- Risco e Retorno mantém coerência entre a taxa mostrada, a legenda e o índice de Sharpe calculado.
- Alterar a taxa livre de risco sem clicar no botão não altera os resultados já confirmados.
- Ao clicar em Analisar risco e retorno, as métricas são recalculadas com a taxa informada.
- Comparação de Ativos mantém símbolos, período, frequência, taxa livre de risco, tabelas, gráficos, correlação e métricas após navegação.
- Comparação de Ativos funciona com os símbolos:
  - `BTC-USD`
  - `AAPL`
  - `USDBRL=X`
  - `SPY`
- O aviso para símbolos inválidos é exibido sem interromper a comparação quando pelo menos dois ativos válidos são obtidos.
- A regra de candle mensal em Indicadores Técnicos exibe linha de fechamento em vez de candles.
- O cache foi validado ao reutilizar consultas equivalentes entre páginas.

### Validação técnica

```powershell
python -m py_compile ".\core\data_loader.py"
python -m py_compile ".\app\main.py"
python -m py_compile ".\app\pages\2_Comparacao_de_Ativos.py"
python -m py_compile ".\app\pages\3_Indicadores_Tecnicos.py"
python -m py_compile ".\app\pages\4_Risco_e_Retorno.py"
pytest -v
```

### Resultado

Etapa concluída e validada manualmente.