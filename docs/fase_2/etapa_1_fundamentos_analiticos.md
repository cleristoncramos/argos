# Fase 2 — Etapa 1: Fundamentos Analíticos

## Objetivo

Criar uma base reutilizável para preparar séries financeiras, agregá-las por frequência, calcular retornos, estatísticas e padrões sazonais.

## Preparação de dados

`prepare_dataframe()`:

- exige a coluna `Date`;
- converte datas inválidas para nulo e as remove;
- mantém colunas OHLCV disponíveis;
- ordena cronologicamente;
- adiciona `Year`, `Month` e `YearMonth`.

`aggregate_by_frequency()` suporta:

- Diário;
- Semanal;
- Mensal.

Para períodos semanal e mensal, aplica as regras financeiras:

| Campo | Regra |
|---|---|
| Open | primeiro preço |
| High | maior preço |
| Low | menor preço |
| Close | último preço |
| Volume | soma do volume |
| Date | última data do período |

## Variável analítica

`select_primary_variable()` cria `Value` como cópia de `Close`, preservando as colunas OHLCV para análises e visualizações posteriores.

## Cálculos implementados

- estatísticas descritivas;
- variação percentual;
- retorno simples;
- retorno logarítmico;
- retorno acumulado;
- análise de sazonalidade por mês;
- percentual de meses positivos;
- matriz Ano × Mês de variação percentual.

## Fórmulas

Variação percentual:

\[
\text{Pct\_Change}_t =
\left(\frac{Value_t}{Value_{t-1}} - 1\right) \times 100
\]

Retorno simples:

\[
r_t = \frac{Value_t}{Value_{t-1}} - 1
\]

Retorno logarítmico:

\[
\ell_t = \ln\left(\frac{Value_t}{Value_{t-1}}\right)
\]

Retorno acumulado:

\[
R_t = \prod_{i=1}^{t}(1 + r_i) - 1
\]

## Arquivos relacionados

- `core/data_processor.py`
- `core/analyzer.py`
- `app/main.py`
- `tests/test_data_processor.py`
- `tests/test_analyzer.py`
- `docs/evidencias/cenario_a_aapl/AAPL_dados_tratados.csv`
- `docs/evidencias/cenario_b_btc/BTC-USD_dados_tratados.csv`
- `docs/evidencias/cenario_c_usdbrl/USDBRL=X_dados_tratados.csv`

## Resultado

A aplicação passou a oferecer uma base analítica consistente para séries financeiras em diferentes frequências.
