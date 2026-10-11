# Checkpoint de Qualidade e Testes — Fase 8

Referência: ata de 30/09/2026, item 15 ("Qualidade e testes").
Última execução registrada (10/10/2026, fim do Bloco 6 do Plano 2): **487 testes passando; cobertura de `core/` em 100% (1251 instruções)**; pandas 3.0.5, Python 3.13.15, Windows.
(mínimo exigido: 80%; meta do projeto: manter próximo ou acima de 95%).

> Este documento é um checkpoint, não um relatório automático. Reexecute
> `python -m pytest` a cada fase e atualize a coluna "Situação".

## 1. Itens da ata × testes

| Item da ata | Onde está coberto | Situação |
| --- | --- | --- |
| Manter todos os testes existentes | suíte completa | Atendido (487 passando no fim do Bloco 6) |
| Testes para novos indicadores | `test_indicators_extra.py`, `test_indicators_validation.py`, `test_features.py` | Atendido |
| Textos e componentes críticos | `test_disclaimers.py`, `test_ui_components.py`, `test_periods_glossary.py` | Atendido |
| Catálogo de ativos | `test_assets.py`, `test_catalog_doc.py`, `test_catalog_notice.py` | Atendido |
| Logos e fallbacks | `test_asset_logos.py` | Atendido |
| Dados insuficientes | `test_data_availability.py`, `test_comparison_checks.py` | Atendido |
| Ativos sem histórico completo / períodos diferentes | `test_data_availability.py`, `test_comparison_checks.py` | Atendido |
| Cálculos com valores ausentes | `test_indicators_validation.py`, `test_risk_metrics.py`, `test_comparison_edges.py`, `test_review_adjustments.py` | Atendido |
| Filtros sem resultado | `test_assets.py::test_get_assets_with_no_match_returns_empty_list` | Atendido |
| Exportação CSV | `test_exports.py` (função em `core/exports.py`, usada nas 4 páginas com download) | Atendido |
| Validação de datas | `test_date_validation.py` (regra em `core/date_validation.py`, usada na barra lateral); `test_data_loader.py` cobre a normalização da data final | Atendido |
| Cobertura mínima de 80% | 100% | Atendido |
| Cobertura próxima ou acima de 95% | 100% | Atendido |

## 2. Lacunas de cobertura (última execução)

| Módulo | Cobertura | Linhas sem teste | Tratamento |
| --- | ---: | --- | --- |
| `comparison.py` | 100% | — | Fechado por `test_comparison_edges.py` |
| `data_processor.py` | 100% | — | Fechado por `test_data_processor_edges.py` |
| `assets.py` | 100% | — | Fechado por `test_coverage_gaps.py` |
| `data_loader.py` | 100% | — | Fechado por `test_coverage_gaps.py` |
| `indicator_docs.py` | 100% | — | Fechado por `test_coverage_gaps.py` |
| `indicators_extra.py` | 100% | — | Fechado por `test_coverage_gaps.py` |
| `data_availability.py` | 100% | — | Fechado por `test_coverage_gaps.py` |

Novos módulos de 07/10 (`simulation.py`, `risk_metrics.py`, `analyzer.py`, `visualizations.py`) estão em 100%.

## 2.1 Evolução durante o Plano 2

| Bloco | Conteúdo | Testes após o bloco | Instruções em `core/` | Observação |
| --- | --- | ---: | ---: | --- |
| 1 | Retornos sem preenchimento de lacunas; alinhamento por fim de período | 405 | 1081 | Executado pelo autor |
| 2 | Sazonalidade por anos, meses e janela | 425 (previsto) | — | Sem registro da execução isolada |
| 3 | Comparação ampliada (sazonalidade comparada, textos) | 429 | — | Executado pelo autor |
| 4 | Textos da simulação | 435 | 1197 | Executado pelo autor |
| 5 | Roteiros "Como ler este gráfico" | 465 | 1208 | Executado pelo autor |
| 6 | Tendência histórica | 487 | 1251 | Executado pelo autor |

Todos os módulos novos de `core/` (`returns_utils.py`, `seasonality.py`, `trend.py`, `chart_guides.py`, `comparison_texts.py`, `simulation_texts.py`) estão em 100%.

## 3. Limitações conhecidas desta medição

- A cobertura mede apenas `core/`. Páginas (`app/views/`) e componentes
  (`app/ui/`) não entram na porcentagem; sua verificação visual é manual
  (`docs/roteiro_conferencia_navegador.md`). Testes estruturais leem o código
  das páginas e de `app/ui/` (roteiro por gráfico, linguagem neutra, texto
  obrigatório da simulação), mas não renderizam a interface.
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