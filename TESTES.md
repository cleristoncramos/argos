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