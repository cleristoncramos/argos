# Argos DataLab

Aplicação web para análise exploratória de dados históricos do mercado financeiro.

O projeto foi desenvolvido no contexto do PIBITI UFPI 2026–2027, no plano de
trabalho **Análise de Dados para Apoio à Tomada de Decisão em Investimentos no
Mercado Financeiro**.

## Funcionalidades

- Consulta de dados históricos por símbolo de ativo.
- Seleção de data inicial, data final e frequência.
- Agregação diária, semanal e mensal.
- Estatísticas descritivas.
- Cálculo de variação percentual e retorno acumulado.
- Gráfico de evolução temporal.
- Gráfico de variação percentual.
- Mapa de calor de sazonalidade por ano e mês.
- Exportação de dados tratados em CSV.
- Validação básica da estrutura dos dados.

## Tecnologias

- Python
- Streamlit
- Pandas
- Plotly
- yfinance
- Pytest

## Estrutura do projeto

```text
argos/
├── app/
│   ├── main.py
│   └── pages/
│       └── 1_Sobre_o_Projeto.py
├── core/
│   ├── analyzer.py
│   ├── config.py
│   ├── data_loader.py
│   └── data_processor.py
├── notebooks/
├── tests/
├── requirements.txt
└── README.md
```

## Como executar localmente

Clone o repositório e crie um ambiente virtual:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Execute a aplicação pela raiz do projeto:

```powershell
streamlit run app/main.py
```

## Testes

Para executar os testes automatizados:

```powershell
pytest -v
```

## Aviso

Esta aplicação tem finalidade educacional e de pesquisa. Dados históricos não
garantem desempenho futuro e o sistema não constitui recomendação de investimento.