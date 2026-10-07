# Checkpoint de Qualidade e Testes — Fase 8

Referência: ata de 30/09/2026, item 15 ("Qualidade e testes").
Última execução registrada: **276 testes passando; cobertura de `core/` em 96,87%**
(mínimo exigido: 80%; meta do projeto: manter próximo ou acima de 95%).

> Este documento é um checkpoint, não um relatório automático. Reexecute
> `python -m pytest` a cada fase e atualize a coluna "Situação".

## 1. Itens da ata × testes

| Item da ata | Onde está coberto | Situação |
| --- | --- | --- |
| Manter todos os testes existentes | suíte completa | Atendido (276 passando) |
| Testes para novos indicadores | `test_indicators_extra.py`, `test_indicators_validation.py`, `test_features.py` | Atendido |
| Textos e componentes críticos | `test_disclaimers.py`, `test_ui_components.py`, `test_periods_glossary.py` | Atendido |
| Catálogo de ativos | `test_assets.py`, `test_catalog_doc.py`, `test_catalog_notice.py` | Atendido |
| Logos e fallbacks | `test_asset_logos.py` | Atendido |
| Dados insuficientes | `test_data_availability.py`, `test_comparison_checks.py` | Atendido |
| Ativos sem histórico completo / períodos diferentes | `test_data_availability.py`, `test_comparison_checks.py` | Atendido |
| Cálculos com valores ausentes | `test_indicators_validation.py`, `test_risk_metrics.py`, `test_comparison_edges.py` | Atendido (revisar após a Fase 6 final) |
| Filtros sem resultado | `test_assets.py` (confirmar se há caso de filtro vazio) | **A confirmar** |
| Exportação CSV | — (a exportação é feita dentro das páginas, sem função em `core/`) | **Pendente** |
| Validação de datas | `test_data_loader.py` cobre a normalização da data final; regras de intervalo na barra lateral não têm teste | **Parcial** |
| Cobertura mínima de 80% | 96,87% | Atendido |
| Cobertura próxima ou acima de 95% | 96,87% | Atendido |

## 2. Lacunas de cobertura (última execução)

| Módulo | Cobertura | Linhas sem teste | Tratamento |
| --- | ---: | --- | --- |
| `comparison.py` | 86% | 43, 51, 58, 80, 85, 92, 117, 129, 157, 180, 189, 205, 210 | Coberto por `test_comparison_edges.py` |
| `data_processor.py` | 90% | 29, 34, 90, 93, 127, 192 | Coberto por `test_data_processor_edges.py` |
| `assets.py` | 93% | 331, 343, 351 | Pendente (ramos de erro de `validate_catalog`) |
| `data_loader.py` | 95% | 96, 119, 157 | Pendente |
| `indicator_docs.py` | 95% | 114 | Pendente |
| `indicators_extra.py` | 95% | 43 | Pendente |
| `data_availability.py` | 98% | 107 | Pendente |

## 3. Limitações conhecidas desta medição

- A cobertura mede apenas `core/`. Páginas (`app/views/`) e componentes
  (`app/ui/`) não entram na porcentagem; sua verificação é manual.
- Testes que dependem de rede (yfinance) usam objetos simulados e não
  garantem a disponibilidade real do Yahoo Finance.
- Cobertura alta não prova que a regra de negócio esteja correta; os
  valores esperados dos testes foram calculados à mão.

## 4. Checklist por fase

Antes de cada commit:

```text
[ ] python -m pytest sem falhas
[ ] cobertura total >= 95%
[ ] novos módulos de core/ com testes
[ ] textos de interface sem linguagem de recomendação
[ ] este checkpoint atualizado
```