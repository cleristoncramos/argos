# Registro de Testes — Argos

## Visão geral

Este documento registra a estratégia de qualidade, os testes automatizados, a cobertura de código, as verificações manuais e os critérios de validação do Argos.

A aplicação tem finalidade educacional e de pesquisa, com dados históricos do Yahoo Finance obtidos pela biblioteca `yfinance`.

| Item | Valor |
| --- | --- |
| URL publicada | [https://argos-datalab.streamlit.app](https://argos-datalab.streamlit.app) |
| Ambiente local | Windows, com ambiente virtual `venv` |
| Python | 3.13.15 local e 3.14 no Streamlit Community Cloud (mínimo: 3.12, exigido pelo NumPy 2.5) |
| Bibliotecas | Streamlit 1.63.0 · pandas 3.0.5 · NumPy 2.5.2 · Plotly 7.0.0 · yfinance 1.7.0 |
| Testes | pytest 9.1.1 · pytest-cov 7.1.0 |
| Última execução registrada | 25/10/2026 |

## Estratégia de testes

| Nível | Objetivo | Escopo no projeto |
| --- | --- | --- |
| Testes unitários | Validar funções e regras isoladas | Todo o pacote `core/`: cálculos, indicadores, métricas, catálogo, formatação e validações |
| Integração leve | Validar a colaboração entre módulos sem rede | Carregador com `yf.Ticker` simulado; dados → retornos → drawdown → métricas; modo de demonstração com pacote temporário |
| Testes estruturais | Ler o código-fonte das páginas | Todo gráfico tem roteiro "Como ler este gráfico"; textos sem linguagem prescritiva; cabeçalho padrão sem ícones; `core/` sem importar Streamlit; sem acesso à rede fora dos módulos autorizados |
| Teste de fumaça da interface | Abrir as páginas de verdade | Streamlit AppTest: página inicial e estado inicial de cada página do menu, sem exceção (`tests/test_app_smoke.py`) |
| Conferência manual no navegador | Validar interações, gráficos e downloads | Roteiros em [`docs/roteiro_conferencia_navegador.md`](docs/roteiro_conferencia_navegador.md) e [`docs/checklists/verificacao_manual_telas.md`](docs/checklists/verificacao_manual_telas.md) |
| Conferência da versão publicada | Confirmar o que está no ar | Por funcionalidade, com data, commit e evidências, em [`docs/verificacao_publicacao.md`](docs/verificacao_publicacao.md) |

O teste de fumaça foi incluído em 25/10/2026. A inclusão da sétima página tinha quebrado a grade da página inicial, e o erro só apareceu na conferência da versão publicada. Agora ele é detectado localmente.

## Execução dos testes

A configuração oficial está em `pytest.ini`. Para executar os testes e medir a cobertura:

```powershell
python -m pytest
```

A execução padrão:

- descobre testes apenas em `tests/`;
- exige configuração e marcadores válidos (`--strict-config`, `--strict-markers`);
- mede a cobertura de `core/`, mostra as linhas não cobertas e gera o relatório HTML em `htmlcov/`;
- **falha se a cobertura de `core/` ficar abaixo de 95%**, a meta da versão congelada.

Para abrir o relatório HTML de cobertura:

```powershell
Start-Process ".\htmlcov\index.html"
```

Para uma execução rápida, sem medir cobertura:

```powershell
python -m pytest --no-cov -q
```

## Configuração do pytest

```ini
[pytest]
minversion = 8.0

testpaths =
    tests

python_files =
    test_*.py

python_classes =
    Test*

python_functions =
    test_*

norecursedirs =
    .git
    .pytest_cache
    __pycache__
    venv
    htmlcov

addopts =
    -ra
    --strict-markers
    --strict-config
    --tb=short
    --cov=core
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=95
```

Até 25/10/2026, a cobertura mínima era de 80%. Ela foi elevada para 95% porque o `core/` já estava em 100% e essa é a meta da versão congelada; uma queda passa a falhar a suíte. Os marcadores `unit`, `integration` e `manual`, que nenhum teste usava, foram retirados.

## Resultado automatizado atual

**Data da execução:** 25/10/2026 · **Comando:** `python -m pytest`

```text
908 passed
Required test coverage of 95% reached. Total coverage: 100.00%
```

**Cobertura:** 100% das 2.695 instruções dos 49 módulos de `core/`. As páginas (`app/`) não entram na medição de cobertura. Elas são verificadas pelos testes estruturais, pelo teste de fumaça e pela conferência no navegador.

### Testes por área

| Área | Testes | Arquivos principais |
| --- | ---: | --- |
| Catálogo, seleção e unidades | 103 | `test_assets`, `test_asset_logos`, `test_catalog_doc`, `test_catalog_notice`, `test_ticker_input`, `test_date_validation`, `test_periods_glossary`, `test_currency` |
| Dados: carga, cache, preparação e qualidade | 94 | `test_data_loader`, `test_data_cache`, `test_data_processor`, `test_data_processor_edges`, `test_long_frequencies`, `test_data_availability`, `test_data_quality`, `test_returns_gap`, `test_exports` |
| Análises e métricas | 211 | `test_analyzer`, `test_risk_metrics`, `test_indicators`, `test_indicators_extra`, `test_indicators_validation`, `test_features`, `test_seasonality`, `test_seasonality_compare`, `test_trailing_returns`, `test_extreme_moves`, `test_drawdown_episodes`, `test_benchmark`, `test_simulation`, `test_panorama`, `test_trend` |
| Comparação de ativos | 43 | `test_comparison`, `test_comparison_align`, `test_comparison_checks`, `test_comparison_edges` |
| Textos educativos e neutralidade | 76 | `test_chart_guides`, `test_disclaimers`, `test_edu_layer`, `test_simulation_texts`, `test_review_adjustments` |
| Interface: componentes e páginas | 112 | `test_ui_components`, `test_formatters`, `test_visualizations`, `test_visualizations_br`, `test_landing`, `test_about`, `test_page_header`, `test_pages`, `test_reload_guard`, `test_app_smoke`, `test_what_if`, `test_season_explorer`, `test_trailing_table`, `test_drawdown_table`, `test_extremes_table`, `test_panorama_table` |
| Explicação assistida por IA | 218 | `test_llm_builders`, `test_llm_context`, `test_llm_eval`, `test_llm_experiment`, `test_llm_mode`, `test_llm_prompts`, `test_llm_service`, `test_llm_validation` |
| Modo de demonstração, configuração e casos-limite | 51 | `test_demo_mode`, `test_config`, `test_coverage_gaps` |
| **Total** | **908** | 69 arquivos |

### O que os testes garantem, em resumo

- **Cálculos:** retornos, volatilidade, Sharpe, drawdown, base 100, correlação, indicadores técnicos sem informação futura, sazonalidade, simulação de aportes, variação por prazo, quedas e recuperação, extremos do período, referência de mercado e panorama.
- **Dados:** normalização de tickers, datas e frequências; agregação semanal, mensal, semestral e anual; lacunas de calendário; disponibilidade do período; alertas de qualidade, inclusive os casos usados na calibração.
- **Carregamento sem rede:** `yf.Ticker` simulado; nenhum módulo acessa a rede fora dos autorizados.
- **Catálogo:** 148 ativos, tickers únicos, campos obrigatórios, lista igual à do documento do catálogo e número exibido no vídeo da página inicial.
- **Linguagem:** os textos não usam frases prescritivas ("momento de comprar", "ativo barato" etc.), e todo gráfico tem roteiro de leitura.
- **Explicação assistida:** prompt congelado, contexto, validador de respostas, limites de uso, modo demonstração e texto de reserva.
- **Modo de demonstração:** manifesto, hashes, leitura offline, gerador do pacote (inclusive `--catalog` e `--start`) e aviso de versão congelada.

## Conferências manuais e da versão publicada

As verificações que dependem do navegador estão em documentos próprios:

| Documento | Conteúdo |
| --- | --- |
| [`docs/roteiro_conferencia_navegador.md`](docs/roteiro_conferencia_navegador.md) | Cenários de conferência por página e por bloco funcional |
| [`docs/checklists/verificacao_manual_telas.md`](docs/checklists/verificacao_manual_telas.md) | Verificação das telas nos modos offline, demonstração e live da explicação assistida |
| [`docs/verificacao_publicacao.md`](docs/verificacao_publicacao.md) | Conferência da versão publicada em 25/10/2026: commit `958b729` verificado, com evidências |
| [`docs/demonstracao.md`](docs/demonstracao.md), seção 2.3.2 | Conferência do modo de demonstração com o snapshot do catálogo ampliado |

### Cenários manuais registrados em 07/09/2026 (histórico)

Registro da primeira rodada de testes manuais, mantido como histórico. As conferências posteriores estão nos documentos acima.

| Cenário | Resultado esperado | Status em 07/09/2026 |
| --- | --- | --- |
| `BTC-USD` em frequência diária, semanal e mensal | Dados, gráficos, indicadores e mapa de calor exibidos | Aprovado |
| `AAPL` mensal | Dados alternativos carregados | Aprovado |
| Data inicial maior ou igual à final | Consulta bloqueada com mensagem de erro | Aprovado |
| Símbolo inexistente | Erro controlado, sem quebra da aplicação | Aprovado |
| Exportação | Download de CSV disponível | Aprovado |
| Persistência entre páginas | Ativo, datas, frequência, taxa e resultados mantidos ao trocar de página | Aprovado |
| Comparação `BTC-USD,AAPL,USDBRL=X,SPY` | Base 100, tabela, correlação, métricas e CSV | Aprovado |
| Candles em frequência mensal | Aviso exibido e gráfico de linha usado | Aprovado |

## Cache e desempenho

O `core/` não depende do Streamlit. O cache das consultas fica na camada de interface, em `app/ui/data_cache.py`, com `st.cache_data` (validade de 1 hora). Ele envolve as funções de `core/data_loader.py`, que recebem por parâmetro as versões cacheadas.

Antes da consulta, o símbolo, as datas e o intervalo são normalizados. Assim, pedidos equivalentes (`aapl`, ` AAPL`, `AAPL`) usam a mesma chave de cache. Falhas temporárias da fonte não ficam guardadas em cache.

O teste `test_core_does_not_import_streamlit` garante que nenhum módulo de `core/` importa o Streamlit.

## Publicação

A aplicação é publicada no Streamlit Community Cloud:

```text
Repositório: cleristoncramos/argos
Branch: main
Arquivo de entrada: app/main.py
```

Fluxo praticado:

```text
Alterar localmente
→ executar python -m pytest (cobertura mínima de 95% no core/)
→ conferir a interface no navegador
→ commit e push na main
→ publicação automática no Streamlit Community Cloud
→ conferência da versão publicada nas entregas relevantes (docs/verificacao_publicacao.md)
```

## Conclusão

Em 25/10/2026, a suíte tem **908 testes aprovados** e **100% de cobertura** em `core/`, com mínimo obrigatório de 95%. Ela é determinística e não depende de rede. Os testes estruturais e de fumaça cobrem a camada de interface. A versão publicada foi conferida por funcionalidade (commit `958b729`).
