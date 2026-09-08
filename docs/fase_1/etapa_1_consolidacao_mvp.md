# Fase 1 — Etapa 1: Consolidação do MVP

## Objetivo

Consolidar uma versão mínima viável do Argos DataLab, com estrutura de código organizada, interface funcional, processamento de dados históricos e base para testes automatizados.

## Implementação realizada

O projeto foi estruturado em camadas com responsabilidades separadas:

```text
app/      Interface Streamlit, páginas e componentes de estado
core/     Coleta, processamento, análise, formatação e visualização
tests/    Testes automatizados por módulo
docs/     Registros, evidências e documentação
```

A aplicação principal ficou centralizada em `app/main.py`. A lógica de negócio foi isolada em módulos de `core/`, permitindo validar cálculos e tratamento de dados independentemente da camada visual.

## Fluxo do MVP

```text
Parâmetros do usuário
→ coleta de dados históricos
→ preparação da série OHLCV
→ agregação por frequência
→ seleção do fechamento como Value
→ estatísticas e variação percentual
→ gráficos, tabela, download e validação
```

## Arquivos relacionados

- `app/main.py`
- `app/ui/sidebar.py`
- `app/ui/state.py`
- `core/data_loader.py`
- `core/data_processor.py`
- `core/analyzer.py`
- `core/formatters.py`
- `tests/`

## Resultado

Foi estabelecido um MVP funcional para análise exploratória de um ativo, com dados históricos, gráficos, estatísticas, sazonalidade, exportação e verificações básicas de qualidade.
