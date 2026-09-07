# Registro de Testes — Argos DataLab

## Visão geral

Este documento registra a estratégia de qualidade, os testes automatizados, a cobertura de código, os cenários manuais e os critérios de validação do Argos DataLab.

A aplicação tem finalidade educacional e de pesquisa, utilizando dados históricos do Yahoo Finance por meio da biblioteca `yfinance`.

- URL publicada: [https://argos-datalab.streamlit.app](https://argos-datalab.streamlit.app)
- Ambiente principal: Windows com ambiente virtual `venv`
- Python: 3.13.15
- Streamlit: 1.63.0
- Pandas: 3.0.5
- Plotly: 7.0.0
- yfinance: 1.7.0
- pytest: 9.1.1
- pytest-cov: 7.1.0
- Última validação: 07/09/2026

## Estratégia de testes

O projeto utiliza uma pirâmide de testes para maximizar a confiabilidade sem tornar a suíte lenta ou dependente de serviços externos.

| Nível | Objetivo | Escopo no projeto |
|---|---|---|
| Testes unitários | Validar funções e regras isoladas | Módulos de `core/`, cálculos, indicadores, formatadores e validações |
| Integração leve | Validar colaboração entre módulos sem rede real | Carregador com `yf.Ticker` simulado, DataFrame → retornos → drawdown → métricas |
| Testes manuais de interface | Validar estado, widgets, navegação, gráficos e downloads | Páginas Streamlit e persistência entre páginas |
| Validação de publicação | Confirmar a versão publicada | Streamlit Community Cloud, branch `main` e URL pública |

## Execução dos testes

### Suíte completa

A configuração oficial está em `pytest.ini`. Para executar testes e cobertura:

```powershell
python -m pytest
```

A execução padrão:

- Descobre testes apenas em `tests/`.
- Exige configuração e marcadores válidos.
- Mede cobertura de `core/`.
- Mostra linhas não cobertas no terminal.
- Gera relatório HTML em `htmlcov/`.
- Falha se a cobertura total ficar abaixo de 80%.

### Relatório HTML de cobertura

Após executar a suíte:

```powershell
Start-Process ".\htmlcov\index.html"
```

### Verificação de sintaxe

Antes de um commit ou publicação, execute:

```powershell
python -m py_compile ".\core\data_loader.py"
python -m py_compile ".\core\risk_metrics.py"
python -m py_compile ".\app\main.py"
python -m py_compile ".\app\pages\2_Comparacao_de_Ativos.py"
python -m py_compile ".\app\pages\3_Indicadores_Tecnicos.py"
python -m py_compile ".\app\pages\4_Risco_e_Retorno.py"
```

## Configuração do pytest

O arquivo `pytest.ini` contém as regras de descoberta e qualidade:

```ini
[pytest]
minversion = 8.0

testpaths =
    tests

python_files =
    test_*.py

python_classes =
    Test*

python_functions =
    test_*

addopts =
    -ra
    --strict-markers
    --strict-config
    --tb=short
    --cov=core
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

## Resultado automatizado atual

**Data da execução:** 07/09/2026

**Comando:**

```powershell
python -m pytest
```

**Resultado:**

```text
110 passed in 3.94s
Required test coverage of 80% reached.
Total coverage: 93.75%
```

### Cobertura por módulo

| Módulo | Cobertura |
|---|---:|
| `core/analyzer.py` | 100% |
| `core/formatters.py` | 100% |
| `core/indicators.py` | 100% |
| `core/risk_metrics.py` | 100% |
| `core/visualizations.py` | 100% |
| `core/data_loader.py` | 98% |
| `core/data_processor.py` | 90% |
| `core/comparison.py` | 85% |
| `core/config.py` | 0% |
| **Total de `core/`** | **93.75%** |

`core/config.py` contém essencialmente configurações e constantes. Por isso, sua baixa cobertura não representa risco funcional equivalente aos módulos de cálculo, processamento e interface.

## Cobertura unitária

### Análise e processamento

Os testes validam:

- Variação percentual.
- Estatísticas descritivas.
- Retornos simples, logarítmicos e acumulados.
- Composição de retornos acumulados.
- Sazonalidade.
- Matriz ano × mês.
- Preparação de DataFrames.
- Agregação diária, semanal e mensal.
- Seleção da variável principal.
- Rejeição de colunas ausentes.

### Indicadores técnicos

Os testes validam:

- Médias móveis simples.
- Médias móveis exponenciais.
- RSI.
- MACD e histograma.
- Bandas de Bollinger.
- Ordem das bandas superior, média e inferior.

### Risco e retorno

Os testes validam:

- Conversão de taxa anual para taxa periódica.
- Rejeição de taxa anual e fator de anualização inválidos.
- Volatilidade anualizada.
- Índice de Sharpe com taxa livre de risco zero e positiva.
- Retornos insuficientes e retornos constantes.
- Drawdown, pico acumulado e maior drawdown.
- Percentual de períodos positivos.
- Resumo de risco e retorno.
- Rejeição de valores ausentes, não numéricos, zero e negativos.

### Comparação de ativos

Os testes validam:

- Normalização e deduplicação de símbolos.
- Limite mínimo e máximo de ativos.
- Normalização Base 100.
- União externa das séries por data.
- Tabela de retornos.
- Matriz de correlação.
- Resumo comparativo.
- Formatação de retorno percentual.

### Carregamento de dados

Os testes de `data_loader.py` utilizam mocks de `yf.Ticker`; portanto, não dependem de internet ou do Yahoo Finance.

São validados:

- Normalização de símbolo, datas e intervalo antes da chamada cacheada.
- Símbolo vazio.
- Ticker reconhecido.
- Ticker sem identidade.
- Falha no acesso a `ticker.info`.
- Histórico vazio.
- Colunas obrigatórias ausentes.
- Ausência de coluna `Date` ou `Datetime`.
- Falha simulada em `ticker.history`.
- Validação de linhas, ausências, datas duplicadas e fechamentos negativos.

### Formatação e visualizações

Os testes validam:

- Formatação numérica brasileira.
- Formatação monetária com prefixo.
- Formatação percentual.
- Valores nulos, inválidos e `NaN`.
- Contexto dos gráficos.
- Gráficos de preço, candles, volume, RSI, MACD, retorno acumulado, drawdown e histograma.
- Rejeição de colunas obrigatórias ausentes em gráficos.

## Testes manuais de interface

### Consulta individual

| Cenário | Parâmetros | Resultado esperado | Status |
|---|---|---|---|
| Criptoativo diário | `BTC-USD`; período válido; Diário | Dados, gráficos e indicadores exibidos | Aprovado |
| Criptoativo semanal | `BTC-USD`; período válido; Semanal | Série agregada semanalmente | Aprovado |
| Criptoativo mensal | `BTC-USD`; período válido; Mensal | Série agregada mensalmente e heatmap exibido | Aprovado |
| Ação | `AAPL`; período válido; Mensal | Dados alternativos carregados | Aprovado |
| Período inválido | Data inicial maior ou igual à final | Consulta bloqueada com mensagem de erro | Aprovado |
| Símbolo inválido | Símbolo inexistente | Erro controlado sem quebra da aplicação | Aprovado |
| Exportação | Consulta válida | Download de CSV disponível | Aprovado |

### Persistência entre páginas

| Cenário | Resultado esperado | Status |
|---|---|---|
| `main` → Sobre o Projeto → `main` | Ativo, datas e frequência permanecem preenchidos | Aprovado |
| Indicadores Técnicos → outra página → retorno | Controles técnicos, gráficos, tabela e download permanecem visíveis | Aprovado |
| Risco e Retorno com taxa de 10% → outra página → retorno | Taxa, Sharpe, gráficos e legenda permanecem coerentes | Aprovado |
| Alterar taxa sem recalcular | Resultados confirmados continuam usando a taxa anterior | Aprovado |
| Recalcular risco e retorno | Sharpe e legenda passam a refletir a nova taxa | Aprovado |
| Comparação → outra página → retorno | Símbolos, período, frequência, taxa, gráficos e tabelas permanecem | Aprovado |

### Comparação de ativos

| Cenário | Parâmetros | Resultado esperado | Status |
|---|---|---|---|
| Comparação válida | `BTC-USD,AAPL,USDBRL=X,SPY` | Base 100, tabela, correlação, métricas e CSV | Aprovado |
| Símbolo inválido entre ativos válidos | Pelo menos dois ativos válidos | Aviso exibido; comparação continua | Aprovado |
| Taxa livre de risco | Alteração seguida de novo cálculo | Sharpes atualizados com a taxa confirmada | Aprovado |

### Indicadores técnicos

| Cenário | Resultado esperado | Status |
|---|---|---|
| Candles em frequência diária ou semanal | Gráfico de candles exibido | Aprovado |
| Candles em frequência mensal | Aviso exibido e gráfico de linha usado | Aprovado |
| Médias móveis, RSI, MACD e Bollinger | Indicadores calculados e renderizados | Aprovado |

## Cache e desempenho

A coleta histórica utiliza:

```python
@st.cache_data(
    ttl=3600,
    show_spinner=False,
)
```

A função pública normaliza símbolo, período e intervalo antes de delegar a chamada à função cacheada. Assim, solicitações equivalentes como:

```text
aapl
 AAPL
AAPL
```

utilizam o símbolo normalizado `AAPL` na chave de cache.

O cache foi validado manualmente ao reutilizar consultas equivalentes entre as páginas `main`, Indicadores Técnicos e Risco e Retorno.

## Publicação

A aplicação é publicada no Streamlit Community Cloud a partir de:

```text
Repositório: cleristoncramos/argos
Branch: main
Arquivo de entrada: app/main.py
```

Fluxo de publicação:

```text
Alterar localmente
→ executar testes
→ commit
→ push para branch de trabalho
→ Pull Request
→ merge na main
→ deploy automático no Streamlit Community Cloud
```

## Conclusão

A Etapa 7 — Qualidade, Testes e Documentação foi concluída com 110 testes automatizados aprovados e 93.75% de cobertura em `core/`.

A suíte é rápida, determinística, não depende de rede para testar o carregamento de dados e mantém um limite mínimo obrigatório de 80% de cobertura.