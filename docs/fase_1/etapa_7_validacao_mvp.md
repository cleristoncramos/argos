# Fase 1 — Etapa 7: Validação do MVP

## Objetivo

Validar o fluxo mínimo da aplicação desde a entrada de parâmetros até a apresentação e exportação dos resultados.

## Fluxo validado

```text
seleção do ativo, período e frequência
→ validação de entradas
→ coleta histórica
→ preparação e agregação
→ cálculo de estatísticas e variação percentual
→ gráficos e tabela
→ exportação CSV
→ painel de qualidade
```

## Cenários manuais registrados

- `BTC-USD` em frequência diária;
- `BTC-USD` em frequência semanal;
- `BTC-USD` em frequência mensal;
- `AAPL` em período válido;
- período inválido;
- símbolo inválido;
- exportação de CSV;
- navegação entre páginas com persistência de filtros.

## Interface de validação

A página principal apresenta:

- total de linhas;
- datas duplicadas;
- fechamentos negativos;
- valores ausentes;
- tabela de dados tratados;
- mapa de calor de sazonalidade;
- variações destacadas visualmente;
- download de CSV em UTF-8.

## Arquivos relacionados

- `app/main.py`
- `app/ui/sidebar.py`
- `app/ui/state.py`
- `core/data_loader.py`
- `core/data_processor.py`
- `core/analyzer.py`
- `core/formatters.py`
- `TESTES.md`

## Resultado

O MVP foi validado como ferramenta exploratória de análise histórica de ativo individual, com conferência de qualidade e exportação de dados.
