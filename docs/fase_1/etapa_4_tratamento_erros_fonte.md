# Fase 1 — Etapa 4: Tratamento de Erros da Fonte de Dados

## Objetivo

Tratar falhas do Yahoo Finance e respostas inválidas sem expor exceções técnicas ao usuário ou apresentar resultados anteriores como se fossem atuais.

## Implementação realizada

A função de coleta utiliza `yfinance.Ticker` e executa validações progressivas:

1. normaliza os parâmetros de consulta;
2. rejeita símbolo vazio;
3. tenta obter dados de identidade do ativo;
4. verifica se existe ao menos um campo de identidade;
5. consulta o histórico com `auto_adjust=False`;
6. exige as colunas `Open`, `High`, `Low`, `Close` e `Volume`;
7. aceita `Date` ou `Datetime`, normalizando para `Date`;
8. converte datas, remove timezone quando necessário e ordena a série;
9. retorna `None` em caso de falha.

As páginas consumidoras verificam se a resposta é nula ou vazia. Quando isso ocorre, invalidam o estado da consulta, removem resultados aplicáveis, exibem mensagem orientativa e interrompem o fluxo com `st.stop()`.

## Qualidade da resposta

A função `validate_data()` registra:

- total de linhas;
- valores ausentes por coluna;
- datas duplicadas;
- fechamentos negativos;
- indicação de existência de dados.

## Cenários cobertos

- símbolo vazio;
- ticker sem identidade;
- falha em `ticker.info`;
- falha em `ticker.history`;
- histórico vazio;
- colunas obrigatórias ausentes;
- ausência de `Date` ou `Datetime`;
- datas duplicadas;
- valores ausentes;
- fechamentos negativos.

## Arquivos relacionados

- `core/data_loader.py`
- `app/main.py`
- `app/pages/2_Comparacao_de_Ativos.py`
- `app/pages/3_Indicadores_Tecnicos.py`
- `app/pages/4_Risco_e_Retorno.py`
- `tests/test_data_loader.py`

## Resultado

Falhas externas e dados incompletos passaram a produzir respostas controladas e compreensíveis, preservando a integridade das análises exibidas.
