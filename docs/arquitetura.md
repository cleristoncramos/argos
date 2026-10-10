# Arquitetura do Sistema — Argos DataLab

**Status:** protótipo evolutivo · **Atualizado em:** 10/10/2026 (Plano 2, blocos 1 a 6) · **Testes:** 487 passando, cobertura de `core/` em 100% (1251 instruções)

Este documento descreve como o Argos DataLab é organizado: camadas, módulos, fluxo de dados e convenções. Os cálculos estão detalhados em `docs/metodologia_de_calculo.md`; as fontes e o tratamento dos dados, em `docs/fontes_e_tratamento_de_dados.md`; o catálogo de ativos, em `docs/catalogo-de-ativos.md`.

---

## 1. Posicionamento

O Argos é uma **ferramenta de pesquisa, educação financeira e apoio à interpretação de dados históricos**. Não é uma ferramenta de recomendação de investimentos: não indica compra ou venda, não avalia o perfil do usuário e não faz previsões. Essa delimitação (ata de 06/10/2026) orienta a arquitetura em três pontos:

1. **Separação entre visualização, métrica e sinal.** Indicadores são exibidos e documentados, mas nenhuma camada transforma um indicador em ordem de compra ou venda.
2. **Camada educativa obrigatória.** Cada métrica tem texto de apoio (`app/ui/education.py`, `app/ui/indicator_docs.py`) e as páginas exibem avisos metodológicos (`app/ui/disclaimers.py`).
3. **Linguagem neutra verificada por teste.** `core/disclaimers.py` mantém a lista de expressões proibidas e os testes verificam os textos exibíveis.

## 2. Tecnologias

| Componente | Uso |
| --- | --- |
| Python | Linguagem do projeto |
| Streamlit | Interface multipágina (`st.navigation` / `st.Page`) |
| Plotly | Gráficos interativos |
| pandas / NumPy | Manipulação de séries e cálculos |
| yfinance | Obtenção de dados históricos (Yahoo Finance) |
| pytest + pytest-cov | Testes automatizados (meta mínima de 80% de cobertura em `core/`) |

## 3. Estrutura de pastas

```text
argos/
├── app/                    # Interface (Streamlit) — só renderização
│   ├── main.py             # Registro das páginas e navegação
│   ├── views/              # Uma página por arquivo
│   │   ├── analise_individual.py
│   │   ├── indicadores_tecnicos.py
│   │   ├── risco_retorno.py
│   │   ├── comparacao_ativos.py
│   │   └── simulacao_aportes.py
│   └── ui/                 # Componentes reutilizáveis
│       ├── asset_cards.py      # Cards e logos dos ativos (com fallback)
│       ├── chart_guide.py      # Botão "Como ler este gráfico"
│       ├── colors.py           # Cores e ícones de retorno positivo/negativo
│       ├── comparison_info.py  # Avisos de comparabilidade
│       ├── data_info.py        # Fonte, disponibilidade e aviso de catálogo
│       ├── disclaimers.py      # Avisos legais e metodológicos
│       ├── education.py        # Caixas "O que significa?" e glossário
│       ├── indicator_docs.py   # Notas e glossário dos indicadores técnicos
│       ├── metric_card.py      # Card de métrica
│       ├── sidebar.py          # Seleção de ativo, período e frequência
│       ├── state.py            # Estado inicial da sessão
│       └── tables.py           # Tabelas padronizadas
├── core/                   # Cálculos e regras — sem dependência de interface
├── tests/                  # Testes automatizados de core/
├── docs/                   # Documentação técnica e acadêmica
└── pytest.ini              # Configuração de testes e cobertura
```

## 4. Camadas e regra de dependência

```text
        app/views  ──usa──►  app/ui  ──usa──►  core
            │                                   ▲
            └───────────────usa─────────────────┘
```

- **`core/`** contém cálculos, validações, regras de negócio e textos de domínio. Recebe e devolve `DataFrame`, dicionários e tipos simples.
- **`app/`** contém apenas renderização e interação: widgets, gráficos, tabelas, mensagens.
- **Regra:** `core/` nunca importa de `app/`. Cálculos não ficam nas páginas; quando uma página precisa de um cálculo novo, ele é criado em `core/` e testado.

Exceção conhecida: `core/data_loader.py` importa `streamlit` apenas para usar `st.cache_data` no download (ver seção 11).

## 5. Módulos de `core/`

| Módulo | Responsabilidade |
| --- | --- |
| `assets.py` | Catálogo de 120 ativos (13 grupos), busca, filtros, hierarquia e validação automática do catálogo |
| `asset_logos.py` | Resolução de logo do ativo, com fallback para emoji |
| `catalog_notice.py` | Texto de aviso de que o catálogo é uma amostra inicial |
| `config.py` | Frequências suportadas e fatores de anualização |
| `periods.py` | Atalhos de período (1, 3, 5 e 10 anos, personalizado) e cálculo da data inicial |
| `date_validation.py` | Validação do intervalo de datas do período personalizado |
| `ticker_input.py` | Normalização e validação do ticker digitado livremente |
| `data_loader.py` | Download no Yahoo Finance, repetições, cache e checagem básica de qualidade |
| `data_processor.py` | Preparação dos dados, agregação por frequência e seleção da variável principal |
| `data_availability.py` | Período solicitado × período disponível, número de observações e avisos |
| `currency.py` | Unidade de cotação de cada ativo (moeda, taxa em %, pontos) |
| `formatters.py` | Formatação numérica no padrão brasileiro |
| `analyzer.py` | Estatísticas da análise individual, variação percentual, sazonalidade e retorno mensal |
| `indicators.py` | SMA, EMA, Bandas de Bollinger, RSI e MACD |
| `indicators_extra.py` | ATR e volatilidade móvel |
| `indicator_docs.py` | Documentação estruturada de cada indicador (o que mede, fórmula, parâmetros, limitações) |
| `features.py` | Camada de variáveis (features) para modelos futuros, separada da visualização |
| `risk_metrics.py` | Retorno, volatilidade, drawdown, percentual positivo e Sharpe |
| `comparison.py` | Base 100, tabelas de preços e retornos, correlação e resumo comparativo |
| `comparison_checks.py` | Períodos divergentes entre ativos e notas de comparabilidade |
| `simulation.py` | Simulação histórica de aportes (aporte único × periódico, janelas móveis) |
| `simulation_texts.py` | Texto obrigatório, premissas e rótulos descritivos da simulação |
| `returns_utils.py` | `simple_returns`: retorno simples sem preenchimento de lacunas, independente da versão do pandas |
| `seasonality.py` | Sazonalidade por anos, meses e janela de retorno composta; mediana, % de anos positivos e N; comparação entre ativos |
| `trend.py` | Tendência histórica: retorno móvel, razão de desempenho e diferença de retorno móvel |
| `comparison_texts.py` | Rótulos descritivos dos destaques e dicas da página de Comparação |
| `chart_guides.py` | Roteiro fixo por gráfico (o que mede, mostra, cuidado, o que não permite concluir); também é o conteúdo de reserva da explicação assistida |
| `visualizations.py` | Construção dos gráficos Plotly (formato numérico brasileiro, rótulos de contexto) |
| `exports.py` | Geração de CSV para download e nomes de arquivo seguros |
| `glossary.py` | Definições do glossário educativo |
| `disclaimers.py` | Avisos e lista de expressões proibidas (linguagem de recomendação) |

## 6. Páginas

| Página | Arquivo | O que faz |
| --- | --- | --- |
| Análise Individual | `views/analise_individual.py` | Série temporal, estatísticas, volatilidade mensal anualizada, variação por período, padrões sazonais e recorte por anos, meses e janela de retorno |
| Indicadores Técnicos | `views/indicadores_tecnicos.py` | Médias móveis, Bollinger, RSI, MACD, ATR, volatilidade móvel e volume |
| Risco e Retorno | `views/risco_retorno.py` | Retorno, volatilidade, Sharpe, drawdown (com data), distribuição de retornos |
| Comparação de Ativos | `views/comparacao_ativos.py` | Até 5 ativos: Base 100, risco, correlação, sazonalidade comparada, tendência histórica (retorno móvel e razão) e dados tabulares |
| Simulação de Aportes | `views/simulacao_aportes.py` | Simulação histórica com valor hipotético; não é recomendação nem previsão |

Todas as páginas exibem, ao final, o aviso de catálogo e o rodapé legal, e cada gráfico tem o botão "Como ler este gráfico" (`app/ui/chart_guide.py`).

## 7. Fluxo de dados

Exemplo (página de Risco e Retorno); as demais seguem o mesmo esqueleto:

```text
sidebar.render_asset_controls()      escolha de ativo, período, frequência
        │  (botão habilitado só com ativo válido e datas válidas)
        ▼
data_loader.download_active_data()   dados diários do Yahoo Finance (cache de 1 h)
        ▼
data_processor.prepare_dataframe()   OHLCV ordenado, datas válidas
        ▼
data_processor.aggregate_by_frequency() + select_primary_variable("Close")
        ▼                             coluna Value = fechamento do período
data_availability.assess_availability()   solicitado × disponível; barra se insuficiente
        ▼
analyzer.calculate_returns() → risk_metrics.calculate_drawdown() → build_risk_summary()
        ▼
st.session_state                      resultado guardado ("consulta confirmada")
        ▼
tabelas, cards e gráficos             renderização (app/ui + core/visualizations)
```

Os dados diários são baixados uma única vez; semanal e mensal são derivados localmente por agregação (ver `docs/fontes_e_tratamento_de_dados.md`).

## 8. Estado da sessão: "consulta confirmada"

Cada página só recalcula quando o usuário clica no botão de análise. O resultado fica em `st.session_state` (`*_loaded`, `*_query`, `*_df` e afins) junto com os parâmetros usados. Alterar um controle na barra lateral **não muda a análise exibida** até um novo clique, e os textos da página usam os parâmetros da consulta confirmada, não os do widget. Falhas limpam o estado para evitar exibir resultados de uma consulta anterior.

## 9. Convenções

**Unidades.** São a principal fonte de erro no projeto:

| Módulo | Unidade dos retornos |
| --- | --- |
| `analyzer.py` (`Pct_Change`, `total_return`, sazonalidade, matriz mensal) | **Percentual** (5,0 = 5%) |
| `calculate_returns`, `cumulative`, `risk_metrics.py`, `comparison.py`, `simulation.py` | **Decimal** (0,05 = 5%) |
| `format_return_pct` | Recebe **decimal** e devolve texto em % |

**Colunas.** `Date`, `Open`, `High`, `Low`, `Close`, `Volume`; `Value` é a cópia da variável principal; `Simple_Return`, `Log_Return`, `Running_Peak` e `Drawdown` são criadas pelo `core/`.

**Anualização.** √252 (diário), √52 (semanal), √12 (mensal), aplicada a todas as classes de ativos.

**Nomes.** Código em inglês; textos exibidos ao usuário em português do Brasil, com separador decimal vírgula e milhar ponto.

## 10. Decisões de projeto

| Decisão | Justificativa |
| --- | --- |
| Manter Python, Streamlit, Plotly e yfinance | Aprovado na reunião de 06/10/2026; adequado a protótipo e a gráficos interativos |
| Catálogo hierárquico como fluxo principal; digitação livre de ticker opcional | Acessível a iniciantes, sem impedir usuários avançados (que passam por validação) |
| Apenas preço de fechamento como variável principal | Simplicidade e comparabilidade; dividendos, taxas, impostos, câmbio e inflação ficam fora do escopo |
| Valores ≤ 0 não entram em retorno percentual, drawdown e Base 100 | Esses cálculos exigem preço positivo (ex.: petróleo WTI fechou negativo em 20/04/2020); as páginas exibem mensagem clara |
| Simulação com valor hipotético, sem perfil do usuário | Evita configurar recomendação individual |
| Features separadas da visualização | Impede que um gráfico vire sinal de negociação e prepara o uso futuro em modelos |
| Retorno por `x / x.shift(1) − 1`, sem `pct_change()` | O padrão do pandas para lacunas mudou entre as versões 2.x e 3.x; a fórmula explícita dá o mesmo resultado em ambas |
| Janela de sazonalidade como retorno composto fechamento a fechamento | "Setembro → outubro" é o retorno de outubro; janelas longas compõem, não somam (decisão de 09/10/2026) |
| Recorte por anos só na Análise Individual | Decisão do orientador (N02); a Comparação mostra a média de todos os anos |
| Tendência limitada a retorno móvel e razão de desempenho | Decisão N07: sem regressão e sem detecção automática de cruzamentos |
| Texto fixo por gráfico em `core/chart_guides.py` | Garante explicação sem depender de modelo de linguagem; serve de conteúdo de reserva |

## 11. Testes e qualidade

- **487 testes**, cobertura de `core/` em **100%** (1251 instruções; meta mínima de 80%).
- `app/` **não** tem testes de renderização: páginas e componentes são conferidos manualmente no navegador (roteiro em `docs/roteiro_conferencia_navegador.md`). Há, porém, **testes estruturais** que leem o código-fonte das páginas e de `app/ui/` (`test_chart_guides.py`, `test_simulation_texts.py`): todo gráfico tem roteiro de leitura, os textos novos usam linguagem neutra e o texto obrigatório da simulação está presente. A cobertura mede apenas `core/`.
- Testes verificam, entre outros: ausência de informação futura nos indicadores, linguagem neutra nos textos, catálogo (120 ativos, tickers únicos, campos obrigatórios), disponibilidade de dados e bordas de agregação.
- O acompanhamento por fase está em `docs/checkpoint_qualidade.md`; as pendências, em `docs/checklist_pendencias.md`.

### Camada planejada: interpretação assistida (Bloco 7)

Ainda **não implementada**. Se a validação da 7A cumprir todos os limiares e o orientador aprovar a 7B, a camada ficará **fora de `core/`** (módulo `services/`), com o provedor, o modelo, a chave e os limites em configuração; o botão "✨ Explicar esta análise" só chama o modelo por clique explícito; toda resposta passa por validações antes de ser exibida, e há texto fixo de reserva (`core/chart_guides.py`). A versão pública não terá a explicação assistida (`LLM_ENABLED=false`). Detalhes em `docs/llm_7b_especificacao.md`.

### Limitações conhecidas da arquitetura

- `core/data_loader.py` depende de `streamlit` (cache). Para isolar totalmente `core/`, o cache poderia ser movido para a camada `app/`.
- Cada página repete o helper `apply_custom_layout` e parte do CSS do tema; há oportunidade de centralizar em `app/ui`.
- A terminologia "grupos" (código) × "classes" (interface) ainda não está padronizada.
- O seletor da Comparação oferece Classe → Ativos; os campos `subcategory` e `market` do catálogo existem, mas ainda não são filtros (candidato ao Plano 3).
- Frequências semestral e anual não estão implementadas (decisão pendente com o orientador).