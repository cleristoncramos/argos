# Argos DataLab

Aplicação web para análise exploratória de dados históricos do mercado financeiro.

O projeto foi desenvolvido no contexto do PIBITI UFPI 2026–2027, no plano de trabalho **Análise de Dados para Apoio à Tomada de Decisão em Investimentos no Mercado Financeiro**.

> Aviso: esta aplicação possui finalidade educacional e de pesquisa. Dados históricos, indicadores técnicos e métricas de risco não garantem desempenho futuro e não constituem recomendação de investimento.

## Aplicação publicada

A versão publicada está disponível em:

[https://argos-datalab.streamlit.app](https://argos-datalab.streamlit.app)

## Funcionalidades

### Análise individual

- Consulta de dados históricos por símbolo de ativo.
- Seleção de data inicial, data final e frequência.
- Frequências diária, semanal e mensal.
- Agregação e tratamento dos dados.
- Estatísticas descritivas.
- Variação percentual, retornos simples e retorno acumulado.
- Série temporal e mapa de calor de sazonalidade.
- Exportação dos dados tratados em CSV.
- Validação de símbolos, períodos e estrutura dos dados.

### Indicadores técnicos

- Gráfico de preço de fechamento e gráfico de candles.
- Médias móveis simples e exponenciais.
- Bandas de Bollinger.
- RSI.
- MACD.
- Volume.
- Exportação em CSV com os indicadores calculados.
- Regra de segurança: candles são substituídos por linha de fechamento na frequência mensal.

### Risco e retorno

- Retorno acumulado.
- Retorno médio por período.
- Volatilidade anualizada.
- Drawdown máximo.
- Percentual de períodos positivos.
- Índice de Sharpe.
- Taxa livre de risco anual configurável.
- Gráficos de retorno acumulado, drawdown e distribuição de retornos.
- Exportação em CSV.

### Comparação de ativos

- Comparação de 2 a 5 símbolos.
- Normalização de desempenho em Base 100.
- Tabela comparativa de retorno, volatilidade, drawdown e Sharpe.
- Matriz de correlação de retornos.
- Métricas individuais por ativo.
- Taxa livre de risco anual configurável.
- Exportação da série normalizada em CSV.
- Exemplo de símbolos: `BTC-USD,AAPL,USDBRL=X,SPY`.

### Persistência e desempenho

- Persistência de filtros e resultados ao navegar entre páginas.
- Estados isolados para análise individual, indicadores, risco e retorno e comparação.
- Consistência entre parâmetros exibidos e resultados confirmados.
- Cache de dados históricos com `st.cache_data` e TTL de uma hora.
- Normalização de símbolos antes da chave de cache.

## Tecnologias

- Python 3.13
- Streamlit
- Pandas
- NumPy
- Plotly
- yfinance
- pytest
- pytest-cov

## Estrutura do projeto

```text
argos/
├── app/
│   ├── main.py
│   ├── pages/
│   │   ├── 1_Sobre_o_Projeto.py
│   │   ├── 2_Comparacao_de_Ativos.py
│   │   ├── 3_Indicadores_Tecnicos.py
│   │   └── 4_Risco_e_Retorno.py
│   └── ui/
│       ├── sidebar.py
│       └── state.py
├── core/
│   ├── analyzer.py
│   ├── comparison.py
│   ├── config.py
│   ├── data_loader.py
│   ├── data_processor.py
│   ├── formatters.py
│   ├── indicators.py
│   ├── risk_metrics.py
│   └── visualizations.py
├── tests/
├── notebooks/
├── requirements.txt
├── pytest.ini
├── TESTES.md
└── README.md
```

## Instalação

Clone o repositório:

```powershell
git clone [https://github.com/cleristoncramos/argos.git](https://github.com/cleristoncramos/argos.git)
cd argos
```

Crie e ative o ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Execução local

Na raiz do projeto, execute:

```powershell
streamlit run app/main.py
```

A aplicação será aberta no navegador pelo endereço informado pelo Streamlit, geralmente:

```text
http://localhost:8501
```

## Testes e cobertura

A suíte de testes está configurada em `pytest.ini`.

Para executar todos os testes com cobertura:

```powershell
python -m pytest
```

Resultado de referência da Etapa 7:

```text
110 passed
Cobertura de core/: 93.75%
Cobertura mínima exigida: 80%
```

A execução gera um relatório HTML em `htmlcov/`. Para abri-lo:

```powershell
Start-Process ".\htmlcov\index.html"
```

A cobertura é medida em `core/`, com falha automática se o total ficar abaixo de 80%.

Consulte [TESTES.md](TESTES.md) para a estratégia completa, cobertura por módulo e cenários manuais.

## Fonte de dados

Os dados históricos são obtidos do Yahoo Finance por meio da biblioteca `yfinance`.

Exemplos de símbolos:

```text
BTC-USD
AAPL
SPY
USDBRL=X
BRL=X
```

A disponibilidade e a nomenclatura dos símbolos dependem do Yahoo Finance.

## Publicação

A aplicação é publicada no Streamlit Community Cloud usando:

```text
Repositório: cleristoncramos/argos
Branch: main
Arquivo principal: app/main.py
```

Fluxo recomendado:

```text
Criar ou atualizar branch de trabalho
→ implementar alterações
→ executar python -m pytest
→ validar manualmente
→ commit e push
→ abrir Pull Request
→ merge na main
→ deploy automático no Streamlit Community Cloud
```

## Qualidade

O projeto utiliza:

- Testes unitários para funções de cálculo, processamento e formatação.
- Mocks para chamadas ao Yahoo Finance nos testes de carregamento.
- Testes de integração leve para fluxos de processamento.
- Testes manuais para navegação Streamlit, widgets, gráficos, downloads e publicação.
- Cobertura mínima obrigatória de 80% em `core/`.

## Licença e uso

Projeto acadêmico de pesquisa e educação. O uso dos resultados é de responsabilidade do usuário.