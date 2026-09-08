# Fase 2 — Etapa 0: Preparação

## Objetivo

Preparar o projeto para evoluir do MVP de análise individual para uma plataforma analítica modular, preservando a estabilidade da aplicação existente.

## Preparação realizada

A expansão partiu de uma base já estruturada em interface, núcleo analítico e testes. Foram mantidos:

- separação entre `app/`, `core/` e `tests/`;
- ambiente virtual e dependências declaradas;
- configuração de testes e cobertura mínima;
- fluxo de branches, Pull Requests e merge na `main`;
- documentação de execução, testes e publicação;
- evidências tabulares em CSV.

Também foi incluída a configuração de Dev Container, registrada no commit:

```text
4d0b62e — Added Dev Container Folder
```

## Critérios adotados

- preservar o MVP funcional;
- adicionar funcionalidades de forma modular;
- evitar dependência de rede na suíte de testes;
- registrar resultados em CSV;
- manter capturas visuais locais fora do Git;
- validar cada incremento por cenários funcionais.

## Resultado

Foi estabelecida uma base técnica e de qualidade para adicionar fundamentos analíticos, indicadores, métricas de risco, comparação de ativos e visualizações sem romper o fluxo do MVP.
