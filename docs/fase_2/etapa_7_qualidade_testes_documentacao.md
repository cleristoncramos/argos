# Fase 2 — Etapa 7: Qualidade, Testes e Documentação

## Objetivo

Fortalecer a confiabilidade do Argos DataLab por meio de uma pirâmide de testes, configuração padronizada do pytest, cobertura mínima do núcleo analítico e documentação técnica das validações realizadas.

## Pirâmide de testes

A estratégia adotada prioriza testes automatizados rápidos e determinísticos no núcleo do projeto, complementados por validações de integração leve, interface e publicação.

| Nível | Objetivo | Aplicação no Argos DataLab |
|---|---|---|
| Testes unitários | Validar regras e funções isoladas | Processamento, análise, indicadores, risco, comparação, formatação e visualizações |
| Integração leve | Validar colaboração entre módulos sem dependência de rede | Carregamento simulado, DataFrame, retornos, drawdown e métricas |
| Testes manuais de interface | Validar widgets, estados, navegação, gráficos e downloads | Páginas Streamlit e persistência entre telas |
| Validação de publicação | Confirmar a versão disponibilizada | Aplicação publicada no Streamlit Community Cloud |

A estratégia reduz dependência de serviços externos nos testes automatizados e permite concentrar a maior cobertura nas regras de negócio.

## Configuração do pytest

Foi criado e configurado o arquivo:

```text
pytest.ini
```

A configuração define:

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
    backup_tests_2026-09-05
    backup_encoding_*
    backup_layout_*

addopts =
    -ra
    --strict-markers
    --strict-config
    --tb=short
    --cov=core
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
```

## Regras de qualidade

- Testes são descobertos somente em `tests/`.
- Arquivos de teste seguem o padrão `test_*.py`.
- Marcadores e configurações inválidas causam falha.
- A cobertura é medida sobre `core/`.
- O relatório exibe linhas não cobertas no terminal.
- Um relatório HTML é gerado em `htmlcov/`.
- A suíte falha automaticamente se a cobertura total de `core/` ficar abaixo de 80%.

## Cobertura por módulo

A suíte cobre os módulos:

```text
tests/test_analyzer.py
tests/test_comparison.py
tests/test_data_loader.py
tests/test_data_processor.py
tests/test_formatters.py
tests/test_indicators.py
tests/test_risk_metrics.py
tests/test_visualizations.py
```

Temas validados:

- estatísticas, variação percentual, retornos e sazonalidade;
- preparação e agregação OHLCV;
- símbolos, datas, colunas e qualidade da fonte;
- cache e carregamento com `yf.Ticker` simulado;
- indicadores técnicos;
- risco, drawdown, volatilidade e Sharpe;
- comparação, Base 100, correlação e resumo;
- formatação brasileira;
- criação de gráficos e validação de colunas obrigatórias.

## Resultado registrado

A execução registrada em 07/09/2026 informou:

```text
110 passed in 3.94s
Required test coverage of 80% reached.
Total coverage: 93.75%
```

Cobertura registrada por módulo:

| Módulo | Cobertura |
|---|---:|
| `core/analyzer.py` | 100% |
| `core/formatters.py` | 100% |
| `core/indicators.py` | 100% |
| `core/risk_metrics.py` | 100% |
| `core/visualizations.py` | 100% |
| `core/data_loader.py` | 98% |
| `core/data_processor.py` | 90% |
| `core/comparison.py` | 85% |
| `core/config.py` | 0% |
| **Total de `core/`** | **93,75%** |

`core/config.py` concentra constantes e configurações. Sua baixa cobertura não equivale a uma lacuna nos módulos de cálculo e processamento, que possuem cobertura elevada.

## Execução

Para executar a suíte:

```powershell
python -m pytest
```

Para abrir o relatório HTML:

```powershell
Start-Process ".\htmlcov\index.html"
```

Para verificação de sintaxe antes de commit ou publicação:

```powershell
python -m py_compile ".\app\main.py"
python -m py_compile ".\core\data_loader.py"
python -m py_compile ".\core\indicators.py"
python -m py_compile ".\core\risk_metrics.py"
python -m py_compile ".\core\comparison.py"
```

## Documentação produzida

A qualidade e a rastreabilidade foram documentadas em:

- `TESTES.md`;
- `pytest.ini`;
- `README.md`;
- `docs/README.md`;
- documentos das etapas das Fases 1 e 2;
- `docs/evidencias/`;
- `docs/etapa_8_validacao_academica.md`.

## Rastreabilidade

- Commit relacionado: `ff181c0` — `test: ampliar cobertura e documentar qualidade`.
- Configuração de qualidade: `pytest.ini`.
- Registro detalhado: `TESTES.md`.

## Resultado

A Fase 2 passou a contar com uma estratégia de qualidade reproduzível, cobertura mínima obrigatória e documentação que conecta testes, código, cenários manuais e evidências.
