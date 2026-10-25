# Arquitetura do Sistema — Argos

**Status:** protótipo evolutivo · **Atualizado em:** 24/10/2026 · **Testes:** 899 passando, cobertura de `core/` em 100% (2.695 instruções)

Este documento descreve como o Argos é organizado: camadas, módulos, páginas, fluxo de dados, configuração e convenções. Os cálculos estão detalhados em `docs/metodologia_de_calculo.md`; as fontes e o tratamento dos dados, em `docs/fontes_e_tratamento_de_dados.md`; o catálogo de ativos, em `docs/catalogo-de-ativos.md`; a explicação assistida, em `docs/llm_7b_implementacao.md`.

---

## 1. Posicionamento

O Argos é uma **ferramenta de pesquisa, educação financeira e apoio à interpretação de dados históricos**. Não é uma ferramenta de recomendação de investimentos: não indica compra ou venda, não avalia o perfil do usuário e não faz previsões. Essa delimitação (ata de 06/10/2026) orienta a arquitetura em quatro pontos:

1. **Separação entre visualização, métrica e sinal.** Indicadores são exibidos e documentados, mas nenhuma camada transforma um indicador em ordem de compra ou venda.
2. **Camada educativa.** Cada métrica tem texto de apoio (`app/ui/education.py`, `app/ui/indicator_docs.py`, `app/ui/chart_guide.py`) e as páginas exibem avisos metodológicos (`app/ui/disclaimers.py`). A camada pode ser desligada para a avaliação experimental (seção 9); os avisos obrigatórios, não.
3. **Linguagem neutra verificada por teste.** `core/disclaimers.py` mantém a lista de expressões proibidas e os testes verificam os textos exibíveis.
4. **IA apenas descritiva e controlada.** A explicação assistida recebe somente métricas já calculadas, passa por validação antes de ser exibida e fica desligada por padrão (seção 8).

## 2. Tecnologias

| Componente | Uso |
| --- | --- |
| Python 3 | Linguagem do projeto |
| Streamlit | Interface multipágina (`st.navigation` / `st.Page`), estado de sessão, cache e modal (`st.dialog`) |
| Plotly | Gráficos interativos |
| pandas / NumPy | Manipulação de séries e cálculos |
| yfinance | Obtenção de dados históricos (Yahoo Finance) |
| pytest + pytest-cov | Testes automatizados (cobertura mínima de 80%, medida em `core/`) |
| GitHub Actions | Rotina que mantém o app publicado ativo (`.github/workflows/keep-alive.yml`) |
| Streamlit Community Cloud | Hospedagem pública (`app/main.py`, branch `main`) |
| Biblioteca padrão (`urllib`) | Cliente da API de modelo de linguagem, sem dependência externa |

As versões usadas em produção estão fixadas em `app/requirements.txt`; o `requirements.txt` da raiz lista as versões mínimas para desenvolvimento local.

## 3. Estrutura de pastas

```text
argos/
├── app/                         # Interface (Streamlit): só renderização e interação
│   ├── main.py                  # Navegação, estilo comum e aviso do modo de demonstração
│   ├── reload_guard.py          # Recarga dos módulos de core/ e app/ depois de um deploy
│   ├── requirements.txt         # Dependências fixadas para o Streamlit Community Cloud
│   ├── views/                   # Uma página por arquivo
│   │   ├── home.py                  # Página inicial
│   │   ├── sobre_projeto.py
│   │   ├── analise_individual.py
│   │   ├── comparacao_ativos.py
│   │   ├── indicadores_tecnicos.py
│   │   ├── risco_retorno.py
│   │   ├── simulacao_aportes.py
│   │   └── panorama_catalogo.py
│   ├── ui/                      # Componentes reutilizáveis
│   │   ├── about.py                 # Conteúdo da página Sobre o Projeto (testável)
│   │   ├── academic_dialog.py       # Modal "Informações acadêmicas"
│   │   ├── asset_cards.py           # Cards e logos dos ativos (com fallback)
│   │   ├── chart_guide.py           # Botão "Como ler este gráfico"
│   │   ├── charts.py                # Layout base dos gráficos Plotly das páginas de análise
│   │   ├── colors.py                # Cores e ícones de retorno positivo/negativo
│   │   ├── comparison_info.py       # Avisos de comparabilidade
│   │   ├── data_cache.py            # Cache dos downloads (st.cache_data sobre core/data_loader)
│   │   ├── data_info.py             # Fonte, disponibilidade, resumo da análise e aviso de catálogo
│   │   ├── demo_banner.py           # Aviso de versão congelada (modo de demonstração)
│   │   ├── design.py                # CSS comum a todas as páginas (identidade visual)
│   │   ├── disclaimers.py           # Avisos legais e metodológicos
│   │   ├── drawdown_table.py        # Tabela "Maiores quedas e recuperação" (Risco e Retorno)
│   │   ├── education.py             # Caixas "O que significa?" e glossário
│   │   ├── extremes_table.py        # Bloco "Maiores altas e quedas" da Análise Individual
│   │   ├── indicator_docs.py        # Notas e glossário dos indicadores técnicos
│   │   ├── landing.py               # Blocos HTML da página inicial e do modal (testáveis)
│   │   ├── llm_explain.py           # Botão e exibição da explicação assistida
│   │   ├── metric_card.py           # Card de métrica
│   │   ├── page_header.py           # Cabeçalho padrão das páginas de análise (sem ícones)
│   │   ├── pages.py                 # Ordem oficial das páginas (menu, home e Get Started)
│   │   ├── panorama_table.py        # Textos e tabela da página Panorama do Catálogo
│   │   ├── season_explorer.py       # Frases e células do bloco "Explorar anos e meses"
│   │   ├── sidebar.py               # Seleção de ativo, período e frequência
│   │   ├── state.py                 # Estado inicial da sessão
│   │   ├── tables.py                # Tabelas padronizadas
│   │   ├── trailing_table.py        # Tabela "Variação por prazo" da Análise Individual
│   │   └── what_if.py               # Bloco "Se você tivesse investido" da Simulação de Aportes
│   └── assets/                  # Arquivos estáticos
│       ├── institucional/           # Logotipos da UFPI e do CEAD (origem em FONTES.md)
│       └── video/                   # Vídeo animado da página inicial
├── core/                        # Cálculos, regras e textos de domínio, sem dependência de interface
├── data/                        # Respostas salvas da explicação assistida e pacote da demonstração
├── experiments/                 # Experimento 7A (avaliação da explicação assistida)
├── scripts/                     # Dados da demonstração, vídeo da página inicial e keep-alive
├── tests/                       # Testes automatizados
├── docs/                        # Documentação técnica e acadêmica
├── .streamlit/config.toml       # Tema visual base
├── .github/workflows/           # Keep-alive do app publicado
└── pytest.ini                   # Configuração de testes e cobertura
```

## 4. Camadas e regra de dependência

```text
        app/views  ──usa──►  app/ui  ──usa──►  core
            │                                   ▲
            └───────────────usa─────────────────┘
```

- **`core/`** contém cálculos, validações, regras de negócio e textos de domínio. Recebe e devolve `DataFrame`, dicionários e tipos simples.
- **`app/`** contém apenas renderização e interação: widgets, gráficos, tabelas, mensagens e estilo.
- **Regra:** `core/` nunca importa de `app/`. Cálculos não ficam nas páginas; quando uma página precisa de um cálculo novo, ele é criado em `core/` e testado.
- **Módulos puros.** Os módulos da explicação assistida, do modo de demonstração e da camada educativa em `core/` não importam o Streamlit nem acessam a rede por conta própria; a chamada à API passa por uma função de transporte injetável, substituída por um cliente simulado nos testes.

**Nenhum módulo de `core/` importa o Streamlit** (verificado por `tests/test_data_cache.py`). O cache dos downloads fica na camada de interface: `app/ui/data_cache.py` aplica `st.cache_data` às funções puras `core.data_loader.fetch_history` e `core.demo_mode.load_demo_frame` e as injeta em `core.data_loader.download_active_data`. As páginas chamam a versão de `app/ui/data_cache.py`.

## 5. Módulos de `core/`

### 5.1 Dados e catálogo

| Módulo | Responsabilidade |
| --- | --- |
| `assets.py` | Catálogo de 148 ativos (`CATALOG_SIZE`; 13 grupos, 9 classes; ver "Termos do catálogo" na seção 11), busca, filtros encadeados (`filter_assets`, `facet_values`), hierarquia e validação automática do catálogo |
| `asset_logos.py` | Resolução do logo do ativo (CoinCap e Financial Modeling Prep), com fallback para emoji; sem logos remotos no modo de demonstração |
| `catalog_notice.py` | Aviso de que o catálogo é uma amostra inicial |
| `config.py` | Frequências suportadas (diária, semanal, mensal, semestral e anual) e fatores de anualização |
| `periods.py` | Atalhos de período (1, 3, 5 e 10 anos, personalizado) e cálculo da data inicial |
| `date_validation.py` | Validação do intervalo de datas do período personalizado |
| `ticker_input.py` | Normalização e validação do ticker digitado livremente |
| `data_loader.py` | Download no Yahoo Finance com repetições (`fetch_history`), normalização dos parâmetros e checagem básica de qualidade; desvia para os dados salvos no modo de demonstração. Puro: recebe por parâmetro as versões cacheadas da interface |
| `demo_mode.py` | Modo de demonstração: leitura dos CSVs salvos, manifesto com hash SHA-256 e reamostragem por frequência |
| `data_processor.py` | Preparação dos dados, agregação por frequência e seleção da variável principal |
| `data_availability.py` | Período solicitado × período disponível, número de observações e avisos |
| `data_quality.py` | Alertas de qualidade da série diária (mudança de patamar desfeita, variação atípica, preço repetido, volume ausente, intervalos sem dados, histórico curto), com limiares por tipo de série |
| `drawdown_episodes.py` | Episódios de queda (pico, fundo, recuperação) e durações; quedas não recuperadas sem estimativa |
| `benchmark.py` | Referência de comparação sugerida por ativo (Ibovespa, S&P 500, Bitcoin, ouro), alinhamento em Base 100 nas datas comuns e avisos de moeda e calendário |
| `extreme_moves.py` | Variações entre fechamentos consecutivos, maiores altas e quedas, contagem por direção e marca de período em andamento |
| `panorama.py` | Panorama de um grupo: métricas por ativo, ordenação com vazios no fim e período coberto |
| `trailing_returns.py` | Variação por prazo (1 mês a 10 anos) até a última observação, com datas efetivas e taxa equivalente ao ano |
| `currency.py` | Unidade de cotação de cada ativo (moeda, taxa em %, pontos) |
| `formatters.py` | Formatação numérica no padrão brasileiro |
| `exports.py` | Geração de CSV para download e nomes de arquivo seguros |

### 5.2 Análises e métricas

| Módulo | Responsabilidade |
| --- | --- |
| `analyzer.py` | Estatísticas da análise individual, variação percentual, sazonalidade e retorno mensal |
| `returns_utils.py` | `simple_returns`: retorno simples sem preenchimento de lacunas, independente da versão do pandas |
| `seasonality.py` | Sazonalidade por anos, meses e janela de retorno composta; mediana, % de anos positivos e N; comparação entre ativos |
| `indicators.py` | SMA, EMA, Bandas de Bollinger, RSI e MACD |
| `indicators_extra.py` | ATR e volatilidade móvel |
| `features.py` | Camada de variáveis (features) para modelos futuros, separada da visualização |
| `risk_metrics.py` | Retorno, volatilidade, drawdown, percentual positivo e Sharpe |
| `comparison.py` | Base 100, tabelas de preços e retornos, correlação e resumo comparativo |
| `comparison_checks.py` | Períodos divergentes entre ativos e notas de comparabilidade |
| `trend.py` | Tendência histórica: retorno móvel, razão de desempenho e diferença de retorno móvel |
| `simulation.py` | Simulação histórica de aportes ("Se você tivesse investido", aporte único × periódico, janelas móveis) |
| `visualizations.py` | Construção dos gráficos Plotly (formato numérico brasileiro, rótulos de contexto) |

### 5.3 Textos educativos e avisos

| Módulo | Responsabilidade |
| --- | --- |
| `indicator_docs.py` | Documentação estruturada de cada indicador (o que mede, fórmula, parâmetros, limitações) |
| `chart_guides.py` | Roteiro fixo por gráfico (o que mede, mostra, cuidado, o que não permite concluir); também é o conteúdo de reserva da explicação assistida |
| `glossary.py` | Definições do glossário educativo |
| `comparison_texts.py` | Rótulos descritivos dos destaques e dicas da página de Comparação |
| `simulation_texts.py` | Texto obrigatório, premissas e rótulos descritivos da simulação |
| `disclaimers.py` | Avisos e lista de expressões proibidas (linguagem de recomendação) |
| `edu_layer.py` | Interruptor da camada educativa (`ARGOS_EDU_LAYER`) para a avaliação experimental |

### 5.4 Explicação assistida (etapas 7A e 7B)

| Módulo | Responsabilidade |
| --- | --- |
| `llm_context.py` | Pacote de contexto enviado ao modelo, montado a partir de resultados já calculados (o modelo não recebe imagens nem calcula nada) |
| `llm_builders.py` | Contextos de cada tela (análise individual, janela sazonal, risco e retorno, comparação de 2 ativos e simulação de aportes) |
| `llm_prompts.py` | Prompts versionados (v0.6 congelado) e esquema JSON da saída |
| `llm_client.py` | Cliente da API: modelo, teto de tokens, timeout e retentativas |
| `llm_validation.py` | Validação da resposta: JSON e campos obrigatórios, ativo, período e frequência coerentes com o contexto, números rastreáveis às métricas, ausência de recomendação e de previsão; qualquer falha bloqueia a exibição |
| `llm_service.py` | Fluxo fechado: contexto → modelo ou resposta salva → validação → exibição ou texto de reserva; limite de uso e custo por sessão e registro de uso |
| `llm_mode.py` | Resolução do modo (`off`, `demo`, `live`) conforme a configuração e o modo de demonstração |
| `llm_render.py` | Conversão da resposta aprovada em texto seguro para exibir (com escape de Markdown) |
| `llm_eval.py` | Métricas e critérios de aprovação do experimento 7A |

## 6. Páginas e navegação

A navegação é registrada em `app/main.py` com `st.navigation`, a partir da lista única de `app/ui/pages.py`, que também define a ordem dos atalhos "Primeiros passos" da página inicial e o destino do botão **Get Started** (a primeira página). A ordem segue o fluxo de estudo: análises primeiro e "Sobre o Projeto" por último, como informação institucional. A página inicial é a padrão; nas demais, o item "Início" fica oculto no menu e um ícone de casa leva de volta a ela.

| Página | Arquivo | O que faz |
| --- | --- | --- |
| Início | `views/home.py` | Apresentação, botão **Get Started**, vídeo dos recursos, mosaico animado do catálogo, tutorial em 3 passos, atalhos para os módulos e botão do modal acadêmico; sem barra lateral |
| Análise Individual | `views/analise_individual.py` | Série temporal, estatísticas, volatilidade mensal anualizada, variação por período, padrões sazonais e o bloco "Explorar anos e meses" (anos × média e variação entre dois meses) |
| Comparação de Ativos | `views/comparacao_ativos.py` | De 2 a 5 ativos, escolhidos por grupo com filtros opcionais de subclasse e mercado: base 100, período comum opcional, risco, correlação, sazonalidade comparada, tendência histórica (retorno móvel e razão) e dados tabulares |
| Indicadores Técnicos | `views/indicadores_tecnicos.py` | Linha ou candles, médias móveis, Bollinger, RSI, MACD, ATR, volatilidade móvel e volume |
| Risco e Retorno | `views/risco_retorno.py` | Retorno, volatilidade, Sharpe, drawdown (com data), melhor e pior período, distribuição de retornos |
| Simulação de Aportes | `views/simulacao_aportes.py` | Simulação histórica com valor hipotético; não é recomendação nem previsão |
| Panorama do Catálogo | `views/panorama_catalogo.py` | Todos os ativos de um grupo no mesmo período: variação no período e em 12 meses, volatilidade, queda máxima, início dos dados e alertas; consulta por grupo sob demanda, ordem inicial por nome |
| Sobre o Projeto | `views/sobre_projeto.py` | Contexto, pergunta de pesquisa e objetivos (com situação), módulos na ordem do menu, metodologia, dados e catálogo, qualidade e escopo, contexto acadêmico e aviso legal. Conteúdo em `app/ui/about.py` |

**Modal acadêmico.** O botão "Informações acadêmicas" da página inicial abre `app/ui/academic_dialog.py` (`st.dialog`), com três abas: identificação do trabalho, tecnologias e bases de dados. O conteúdo é montado por funções puras de `app/ui/landing.py`, cobertas por `tests/test_landing.py`.

Todas as páginas de análise exibem, ao final, o aviso de catálogo e o rodapé legal, e cada gráfico tem o botão "Como ler este gráfico" (`app/ui/chart_guide.py`). Nas telas que têm explicação assistida, o botão correspondente só aparece quando o recurso está ligado.

## 7. Fluxo de dados

Exemplo (página de Risco e Retorno); as demais páginas de análise seguem o mesmo esqueleto:

```text
sidebar.render_asset_controls()      escolha de ativo, período, frequência
        │  (botão habilitado só com ativo válido e datas válidas)
        ▼
data_cache.download_active_data()    app/ui: cache de 1 h sobre core/data_loader
        │                             dados diários do Yahoo Finance
        │                             ou CSVs salvos, no modo de demonstração
        ▼
data_processor.prepare_dataframe()   OHLCV ordenado, datas válidas
        ▼
data_processor.aggregate_by_frequency() + select_primary_variable("Close")
        ▼                             coluna Value = fechamento do período
data_availability.assess_availability()   solicitado × disponível; barra se insuficiente
data_quality.assess_data_quality()        alertas da série diária (não altera os dados)
        ▼
analyzer.calculate_returns() → risk_metrics.calculate_drawdown() → build_risk_summary()
        ▼
st.session_state                      resultado guardado ("consulta confirmada")
        ▼
tabelas, cards e gráficos             renderização (app/ui + core/visualizations)
```

Os dados diários são baixados uma única vez; as frequências semanal, mensal, semestral e anual são derivadas localmente por agregação (`data_processor.aggregate_by_frequency`, com a chave `PeriodEnd` calculada por `period_end`) (ver `docs/fontes_e_tratamento_de_dados.md`). Falhas temporárias da fonte levantam `DataUnavailable` dentro da função cacheada, para que não fiquem guardadas em cache.

**Estado da sessão: "consulta confirmada".** Cada página só recalcula quando o usuário clica no botão de análise. O resultado fica em `st.session_state` (`*_loaded`, `*_query`, `*_df` e afins) junto com os parâmetros usados. Alterar um controle na barra lateral **não muda a análise exibida** até um novo clique, e os textos da página usam os parâmetros da consulta confirmada, não os do widget. Falhas limpam o estado para evitar exibir resultados de uma consulta anterior.

## 8. Explicação assistida

Implementada na etapa 7B, depois da validação experimental da 7A:

```text
llm_builders (contexto da tela) ──► llm_service ──► modo live: llm_client (API)
                                         │          modo demo: data/llm_demo.json
                                         ▼
                                  llm_validation ──► aprovada: llm_render ──► app/ui/llm_explain
                                         │
                                         └─► reprovada ou indisponível: texto de reserva (chart_guides)
```

- **Desligada por padrão** (`ARGOS_LLM_MODE=off`): o botão não aparece.
- **Modo `demo`:** reproduz respostas gravadas e validadas para contextos fixos, sem rede e sem custo; é o padrão quando o modo de demonstração está ativo.
- **Modo `live`:** chama a API por clique explícito, com limite de 20 chamadas e US$ 0,50 por sessão; a chave vem de variável de ambiente ou dos segredos do Streamlit e nunca é gravada.
- Toda resposta é revalidada antes de aparecer, inclusive as salvas, e o uso é registrado em `logs/llm_uso.jsonl` (fora do repositório).

## 9. Configuração

| Variável | Valores | Efeito |
| --- | --- | --- |
| `ARGOS_DEMO_MODE` | `true` / `false` (padrão) | Usa apenas os dados salvos em `data/demo/` e exibe o aviso de versão congelada |
| `ARGOS_DEMO_DIR` | caminho | Pasta alternativa do pacote de demonstração |
| `ARGOS_EDU_LAYER` | `on` (padrão) / `off` | Oculta os componentes educativos para a condição experimental da avaliação; os avisos obrigatórios continuam visíveis |
| `ARGOS_LLM_MODE` | `off` (padrão), `demo`, `live` | Modo da explicação assistida |
| `OPENAI_API_KEY` | chave | Necessária apenas no modo `live` |
| `ARGOS_LLM_RECORD` | `1` | No modo `live`, grava as respostas aprovadas em `data/llm_demo.json` |

As variáveis podem vir do ambiente ou de `.streamlit/secrets.toml` (ignorado pelo Git).

## 10. Identidade visual

| Arquivo | Papel |
| --- | --- |
| `.streamlit/config.toml` | Tema base: claro, fundo levemente quente, cor principal vermelha, bordas finas escuras e raio zero |
| `app/ui/design.py` | CSS comum aplicado por `app/main.py` em todas as páginas: cantos retos, painéis brancos com sombra suave, botão principal com texto branco |
| `app/views/home.py` | Estilo próprio da página inicial |
| `app/ui/landing.py` | Estilo do mosaico de ativos e do modal acadêmico |
| `scripts/video_recursos/animacao.html` | Animação do vídeo da página inicial, gravada em MP4 por `scripts/gravar_video_recursos.py` |

## 11. Convenções

**Unidades.** São a principal fonte de erro no projeto:

| Módulo | Unidade dos retornos |
| --- | --- |
| `analyzer.py` (`Pct_Change`, `total_return`, sazonalidade, matriz mensal) | **Percentual** (5,0 = 5%) |
| `calculate_returns`, `cumulative`, `risk_metrics.py`, `comparison.py`, `simulation.py`, `trend.py` | **Decimal** (0,05 = 5%) |
| `format_return_pct` | Recebe **decimal** e devolve texto em % |

**Colunas.** `Date`, `Open`, `High`, `Low`, `Close`, `Volume`; `Value` é a cópia da variável principal; `Simple_Return`, `Log_Return`, `Running_Peak` e `Drawdown` são criadas pelo `core/`.

**Anualização.** √252 (diário), √52 (semanal), √12 (mensal), √2 (semestral) e √1 (anual), aplicada a todas as classes de ativos. Nas frequências semestral e anual, `data_availability` sinaliza o último período ainda em andamento (retorno parcial).

**Termos do catálogo.** Interface e código usam os mesmos termos:

| Termo na interface | Campo em `core/assets.py` | Quantidade | Exemplos |
| --- | --- | ---: | --- |
| **Grupo** | `group` | 13 | Criptomoedas, Ações Brasil, ETFs de renda fixa, FIIs Brasil |
| **Classe** | `class` | 9 | Criptomoeda, Ação, ETF, REIT, FII, Índice, Forex, Commodity, Renda Fixa |
| **Subclasse** | `subcategory` | — | Energia, Bancos, Smart contracts |
| **Mercado** | `market` | — | Brasil/B3, EUA, Global |

**Nomes.** Código em inglês; textos exibidos ao usuário em português do Brasil, com separador decimal vírgula e milhar ponto.

**HTML próprio.** Todo texto vindo do catálogo, do usuário ou do modelo de linguagem é escapado antes de entrar em HTML ou Markdown.

## 12. Decisões de projeto

| Decisão | Justificativa |
| --- | --- |
| Manter Python, Streamlit, Plotly e yfinance | Aprovado na reunião de 06/10/2026; adequado a protótipo e a gráficos interativos |
| Catálogo hierárquico como fluxo principal; digitação livre de ticker opcional | Acessível a iniciantes, sem impedir usuários avançados (que passam por validação) |
| Apenas preço de fechamento como variável principal | Simplicidade e comparabilidade; dividendos, taxas, impostos, câmbio e inflação ficam fora do escopo |
| Valores ≤ 0 não entram em retorno percentual, drawdown e base 100 | Esses cálculos exigem preço positivo (ex.: petróleo WTI fechou negativo em 20/04/2020); as páginas exibem mensagem clara |
| Simulação com valor hipotético, sem perfil do usuário | Evita configurar recomendação individual |
| Features separadas da visualização | Impede que um gráfico vire sinal de negociação e prepara o uso futuro em modelos |
| Retorno por `x / x.shift(1) − 1`, sem `pct_change()` | O padrão do pandas para lacunas mudou entre as versões 2.x e 3.x; a fórmula explícita dá o mesmo resultado em ambas |
| Janela de sazonalidade como retorno composto fechamento a fechamento | "Setembro → outubro" é o retorno de outubro; janelas longas compõem, não somam (decisão de 09/10/2026) |
| Recorte por anos só na Análise Individual | Decisão do orientador (N02); a Comparação mostra a média de todos os anos |
| Tendência limitada a retorno móvel e razão de desempenho | Decisão N07: sem regressão e sem detecção automática de cruzamentos |
| Texto fixo por gráfico em `core/chart_guides.py` | Garante explicação sem depender de modelo de linguagem; serve de conteúdo de reserva |
| Explicação assistida em módulos puros de `core/`, desligada por padrão | Testável sem rede; a versão pública não chama o modelo, e o modo `demo` usa respostas validadas |
| Modo de demonstração com dados congelados e hash | Apresentações e avaliação com usuários reproduzíveis e sem depender da internet |
| Recarga dos módulos do projeto quando o código muda (`app/reload_guard.py`) | O Streamlit só recarrega módulos da pasta do script (`app/`); depois de um push, o Streamlit Cloud continuava com a versão antiga de `core/` na memória, o que causou um `TypeError` em 24/10/2026 |
| Cache dos downloads em `app/ui/data_cache.py`, por injeção no `core` | Mantém `core/` livre do Streamlit e testável sem o runtime; falhas da fonte continuam fora do cache |
| Nome provisório "Argos — Plataforma de Análise Histórica de Ativos Financeiros" (24/10/2026), sem a analogia mitológica | O orientador considerou que "Argos DataLab" e a mitologia não transmitiam a seriedade de um sistema acadêmico; a denominação definitiva será decidida com ele. O prompt congelado v0.6 mantém o nome antigo, pois é texto interno validado na 7A e alterá-lo exigiria nova versão e nova validação |
| Modal acadêmico em vez de página no menu | Mantém o menu focado nas análises; as informações acadêmicas ficam a um clique da página inicial |

## 13. Testes e qualidade

- **899 testes**, cobertura de `core/` em **100%** (2.695 instruções; meta mínima de 80% no `pytest.ini` e de 95% para a versão congelada).
- `app/` **não** tem testes de renderização: páginas e componentes são conferidos manualmente no navegador (roteiro em `docs/roteiro_conferencia_navegador.md`). Há, porém:
  - **testes de componentes** que montam o HTML e o layout dos gráficos de `app/ui` sem o Streamlit (`test_ui_components.py`, `test_landing.py`), verificando escape de texto, conteúdo do modal, layout base dos gráficos e ausência de cantos arredondados no CSS próprio;
  - **testes estruturais** que leem o código-fonte das páginas (`test_chart_guides.py`, `test_simulation_texts.py`): todo gráfico tem roteiro de leitura, os textos novos usam linguagem neutra e o texto obrigatório da simulação está presente.
- Testes verificam, entre outros: ausência de informação futura nos indicadores, linguagem neutra nos textos, catálogo (148 ativos, tickers únicos, campos obrigatórios, lista igual à do documento do catálogo), disponibilidade de dados, bordas de agregação, modo de demonstração e todo o fluxo da explicação assistida com cliente simulado.
- Não há pipeline de integração contínua: os testes são executados localmente antes de cada commit.
- O acompanhamento por fase está em `docs/checkpoint_qualidade.md`; as pendências, em `docs/checklist_pendencias.md`.

### Limitações conhecidas da arquitetura

