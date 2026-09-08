# Fase 1 — Etapa 8: Registro de Testes

## Objetivo

Formalizar a estratégia de qualidade, a execução dos testes automatizados, a cobertura e os cenários manuais de validação.

## Estratégia

O projeto utiliza:

- testes unitários para regras de cálculo, processamento, indicadores e formatação;
- integração leve entre módulos sem acesso real à rede;
- mocks de `yf.Ticker` no carregamento de dados;
- testes manuais das páginas Streamlit, widgets, gráficos e downloads;
- validação da publicação.

## Configuração

O `pytest.ini` define:

```ini
testpaths = tests
--cov=core
--cov-report=term-missing
--cov-report=html
--cov-fail-under=80
```

A cobertura é calculada sobre `core/` e a execução falha se ficar abaixo de 80%.

## Resultado registrado

Em 07/09/2026, a execução registrada em `TESTES.md` informou:

```text
110 passed in 3.94s
Required test coverage of 80% reached.
Total coverage: 93.75%
```

## Cobertura por tema

- análise, estatísticas, retornos e sazonalidade;
- carregamento e validação da fonte;
- preparação e agregação de dados;
- indicadores técnicos;
- risco e retorno;
- comparação de ativos;
- formatação;
- visualizações.

## Arquivos relacionados

- `TESTES.md`
- `pytest.ini`
- `tests/`
- commit `ff181c0` — `test: ampliar cobertura e documentar qualidade`

## Resultado

A qualidade do núcleo analítico passou a ser acompanhada por testes repetíveis e cobertura mínima obrigatória.
