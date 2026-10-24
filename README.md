# Argos

**Plataforma de Análise Histórica de Ativos Financeiros: análise exploratória de ativos, comparação de desempenho, indicadores técnicos e métricas de risco, com finalidade educacional e de pesquisa.**

[![Aplicação online](https://img.shields.io/badge/app-argos--datalab.streamlit.app-C8102E)](https://argos-datalab.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.63-FF4B4B?logo=streamlit&logoColor=white)
![Testes](https://img.shields.io/badge/testes-806%20aprovados-2E7D32)
![Cobertura](https://img.shields.io/badge/cobertura%20do%20core-100%25-2E7D32)
![PIBITI UFPI](https://img.shields.io/badge/PIBITI-UFPI%202026%E2%80%932027-1F1F1F)

O **Argos** reúne em uma única plataforma o histórico de **120 ativos em 13 grupos** (ações, criptomoedas, FIIs, REITs, ETFs, commodities, câmbio, índices e taxas de juros) e transforma esses dados em gráficos interativos, métricas quantitativas e textos explicativos em linguagem simples. Foi desenvolvido no **Programa Institucional de Bolsas de Iniciação em Desenvolvimento Tecnológico e Inovação (PIBITI) da Universidade Federal do Piauí**, ciclo 2026–2027.

> [!IMPORTANT]
> O Argos tem finalidade **exclusivamente acadêmica, educacional e de desenvolvimento tecnológico**. As informações, métricas e visualizações descrevem dados históricos e **não constituem recomendação, indicação ou aconselhamento de investimento**.

> [!NOTE]
> **Nome provisório.** Até 23/10/2026 o sistema se chamava **Argos DataLab**. Em 24/10/2026 o nome passou a ser **Argos — Plataforma de Análise Histórica de Ativos Financeiros**, sem a analogia mitológica, enquanto a denominação definitiva é discutida com o orientador. Documentos históricos (atas, relatórios e o prompt congelado da explicação assistida) mantêm o nome original.

---

## Sumário

1. [Sobre o projeto](#sobre-o-projeto)
2. [Funcionalidades](#funcionalidades)
3. [Catálogo de ativos](#catálogo-de-ativos)
4. [Metodologia de cálculo](#metodologia-de-cálculo)
5. [Fonte e tratamento dos dados](#fonte-e-tratamento-dos-dados)
6. [Arquitetura](#arquitetura)
7. [Tecnologias](#tecnologias)
8. [Instalação e execução](#instalação-e-execução)
9. [Configuração](#configuração)
10. [Modo de demonstração](#modo-de-demonstração)
11. [Testes e qualidade](#testes-e-qualidade)
12. [Publicação](#publicação)
13. [Identidade visual](#identidade-visual)
14. [Documentação complementar](#documentação-complementar)
15. [Como contribuir](#como-contribuir)
16. [Contexto acadêmico](#contexto-acadêmico)
17. [Aviso legal e metodológico](#aviso-legal-e-metodológico)
18. [Licença](#licença)

---

## Sobre o projeto

Dados de mercado estão amplamente disponíveis, mas interpretá-los exige ferramentas e conhecimento que nem sempre estão ao alcance de estudantes e pesquisadores. O Argos aproxima esses dois lados: cada análise vem acompanhada da fórmula usada, das premissas adotadas e de uma leitura em linguagem simples do que o resultado significa (e do que ele **não** permite concluir).

**Público-alvo:** estudantes, pesquisadores e interessados em mercado financeiro que desejam estudar o comportamento histórico de ativos com rigor e transparência.

**Perguntas que a plataforma ajuda a responder:**

| Pergunta | Onde |
| --- | --- |
| Como um ativo se comportou ao longo do tempo? Há meses historicamente melhores ou piores? | Análise Individual |
| Qual ativo foi mais longe no mesmo período? Eles se movem juntos? | Comparação de Ativos |
| O que dizem as médias móveis, as Bandas de Bollinger, o RSI e o MACD? | Indicadores Técnicos |
| Quanto o ativo oscilou e qual foi a maior queda desde um pico? | Risco e Retorno |
| E se eu tivesse investido um valor fixo todo mês? | Simulação de Aportes |

**Princípios do projeto:**

- **Transparência:** fórmulas, parâmetros e convenções documentados e visíveis na interface.
- **Neutralidade:** os textos descrevem o passado; nenhum ativo é apontado como "melhor" ou "pior" para investir.
- **Reprodutibilidade:** cálculos isolados em `core/`, cobertos por testes, e um modo de demonstração com dados congelados.
- **Separação de responsabilidades:** interface em `app/`, regras analíticas em `core/`.

---

## Funcionalidades

### Página inicial

- Nome, frase de efeito e botão **Get Started**, que abre a Análise Individual.
- Vídeo animado e ilustrativo com um tour pelos recursos do sistema, com os logotipos reais dos ativos do catálogo.
- Mosaico animado e lento com os 120 ativos do catálogo: logotipo, ticker e nome.
- Tutorial em três passos e atalhos de "primeiros passos" para cada módulo.
- Botão **Informações acadêmicas**, que abre um modal com os logotipos da UFPI e do CEAD, a identificação do trabalho, as tecnologias e as bases de dados.

### Análise Individual

- Seleção guiada por grupo de ativos ou digitação livre do ticker, com validação de formato e de existência na fonte.
- Atalhos de período (1, 3, 5 e 10 anos) ou intervalo personalizado; frequência diária, semanal, mensal, semestral ou anual.
- Visão geral (primeiro e último valor, retorno total, observações) e evolução temporal do preço.
- Volatilidade anualizada mês a mês, com destaque para os meses de maior oscilação.
- Mapa de calor de retornos mensais (mês × ano), média por mês do calendário, recorte por anos e **janela sazonal** (por exemplo, de setembro a outubro em cada ano).
- Painel de disponibilidade de dados (período solicitado × disponível) e exportação em CSV.

### Comparação de Ativos

- De **2 a 5 ativos**, inclusive de grupos diferentes, com evolução em **base 100**.
- Seleção por **grupo de ativos**, com filtros opcionais de **subclasse** (setor ou tipo) e **mercado** (país ou bolsa) que restringem a lista.
- Opção de comparar apenas o **período comum** a todos os ativos.
- Matriz de correlação dos retornos, resumo comparativo e destaques descritivos do período.
- Tendência histórica com **retorno móvel** (3, 6 ou 12 meses) e **razão de desempenho** em relação a um ativo de referência.
- Sazonalidade comparada entre os ativos.

### Indicadores Técnicos

- Gráfico de linha de fechamento ou de **candles**.
- **SMA** e **EMA** (curta e longa), **Bandas de Bollinger**, **RSI**, **MACD**, **ATR**, volatilidade móvel e volume.
- Parâmetros ajustáveis e um guia de leitura ("como ler este gráfico") para cada indicador.

### Risco e Retorno

- Retorno acumulado, retorno médio, **volatilidade anualizada**, **Índice de Sharpe** (com taxa livre de risco configurável), **drawdown máximo** e a data do fundo da maior queda.
- Percentual de períodos positivos, melhor e pior período.
- Curva de drawdown e distribuição dos retornos por faixas.

### Simulação de Aportes

- Aporte único versus aportes periódicos com o mesmo total investido.
- Janelas históricas de horizonte fixo, com menor, mediano e maior resultado e a proporção de janelas positivas.
- Premissas explícitas: preço de fechamento, sem dividendos, taxas, impostos ou inflação.

### Sobre o Projeto

- Contexto e público, pergunta de pesquisa e objetivos com a situação de cada um, módulos, metodologia, dados e catálogo, qualidade, escopo e contexto acadêmico.

### Explicação assistida por IA (opcional, desligada por padrão)

Recurso experimental, resultado da etapa de pesquisa 7B, que gera um texto educativo a partir das métricas exibidas em uma tela. Usa um prompt congelado e versionado, resposta em JSON validada antes de ser exibida, limites de uso e de custo por sessão e um texto fixo de reserva em caso de falha. Fica **desligado por padrão**; no modo de demonstração usa apenas respostas previamente gravadas e validadas. Detalhes em [`docs/llm_7b_implementacao.md`](docs/llm_7b_implementacao.md).

---

## Catálogo de ativos

O catálogo fica em [`core/assets.py`](core/assets.py) e reúne **120 ativos em 13 grupos e 9 classes**:

| Grupo | Classe | Ativos | Exemplos |
| --- | --- | ---: | --- |
| Criptomoedas | Criptomoeda | 10 | BTC-USD, ETH-USD, SOL-USD |
| Ações Brasil | Ação | 12 | PETR4.SA, VALE3.SA, ITUB4.SA |
| Ações EUA | Ação | 15 | AAPL, MSFT, NVDA |
| Ações Europa | Ação | 8 | ASML, SAP, NESN.SW |
| Ações Ásia | Ação | 8 | TSM, SONY, 005930.KS |
| ETFs de ações | ETF | 10 | SPY, QQQ, VTI |
| ETFs de renda fixa | ETF | 6 | BND, AGG, TLT |
| REITs / mercado imobiliário | REIT | 5 | VNQ, O, PLD |
| FIIs Brasil | FII | 5 | MXRF11.SA, HGLG11.SA, KNRI11.SA |
| Índices de mercado | Índice | 12 | ^BVSP, ^GSPC, ^IXIC |
| Forex | Forex | 8 | USDBRL=X, EURUSD=X, USDJPY=X |
| Commodities | Commodity | 14 | GC=F, SI=F, CL=F |
| Treasury / taxas de juros | Renda Fixa | 7 | ^IRX, ^TNX, ^TYX |

Além do catálogo, qualquer ticker disponível no Yahoo Finance pode ser digitado diretamente (por exemplo, `PETR4.SA`, `BRK-B`, `^BVSP`, `GC=F`). A lista completa, com critérios de inclusão, está em [`docs/catalogo-de-ativos.md`](docs/catalogo-de-ativos.md).

---

## Metodologia de cálculo

Resumo das principais convenções. A descrição completa, com fórmulas, unidades e casos-limite, está em [`docs/metodologia_de_calculo.md`](docs/metodologia_de_calculo.md).

| Tema | Convenção adotada |
| --- | --- |
| Variável principal | Preço de **fechamento** (`Close`) da frequência escolhida |
| Retorno simples | `r_t = V_t / V_{t-1} − 1`; lacunas viram vazio e **não** são preenchidas com o valor anterior |
| Anualização | Fator `k` = 252 (diário), 52 (semanal), 12 (mensal), 2 (semestral) e 1 (anual), igual para todas as classes |
| Volatilidade | `desvio-padrão(r, ddof=1) × √k` |
| Índice de Sharpe | `média(r − r_f) / desvio-padrão(r − r_f) × √k`, com a taxa anual `r_f` convertida para a frequência |
| Drawdown | `V_t / máximo(V_1..V_t) − 1`; o drawdown máximo é o menor valor da série |
| Base 100 | Cada série dividida pelo seu primeiro valor válido e multiplicada por 100 |
| Correlação | Pearson entre retornos simples coincidentes |
| SMA / EMA | Janelas padrão 20 e 50 (SMA) e 12 e 26 (EMA) |
| Bandas de Bollinger | `SMA_20 ± 2 × desvio-padrão amostral` |
| RSI | Janela 14, suavização de Wilder, níveis de referência 30 e 70 |
| MACD | `EMA_12 − EMA_26`, linha de sinal `EMA_9` |
| Sem informação futura | Cada indicador em uma data usa apenas dados até essa data (verificado por testes) |

---

## Fonte e tratamento dos dados

| Fonte | Conteúdo | Uso |
| --- | --- | --- |
| **Yahoo Finance** (via `yfinance`) | Séries diárias de abertura, máxima, mínima, fechamento e volume | Base de todas as análises; consulta sob demanda com cache de 1 hora |
| **Catálogo interno** | Ticker, nome, classe, mercado e descrição dos ativos | Seleção guiada e organização da interface |
| **Pacote de demonstração** | CSVs congelados com manifesto e hash SHA-256 | Apresentações e avaliação sem depender da internet |
| **CoinCap** e **Financial Modeling Prep** | Logotipos públicos de criptomoedas, ações, ETFs, REITs e FIIs | Identificação visual dos ativos |

**Tratamento:** os dados diários são baixados uma única vez; as frequências semanal, mensal, semestral e anual são derivadas localmente por agregação (abertura, máxima, mínima, fechamento e volume somado). Datas inválidas são descartadas, e falhas temporárias da fonte não ficam guardadas em cache.

**Limitações conhecidas:**

- Os retornos são **de preço**: dividendos e proventos não são incorporados, o que subestima o retorno total de ações pagadoras e FIIs.
- O mesmo fator de anualização (252) é usado para criptoativos, que negociam todos os dias, por comparabilidade entre classes.
- Valores em moedas diferentes não são convertidos; a base 100 compara trajetórias, não preços.
- A fonte pode apresentar atrasos, ajustes históricos, mudanças de ticker e indisponibilidade temporária.

Detalhes em [`docs/fontes_e_tratamento_de_dados.md`](docs/fontes_e_tratamento_de_dados.md) e [`docs/fora_do_escopo.md`](docs/fora_do_escopo.md).

---

## Arquitetura

A aplicação segue uma separação em camadas: as páginas em `app/` cuidam apenas da interface e delegam todos os cálculos ao pacote `core/`, que não depende do Streamlit e é integralmente testado.

```text
Barra lateral (ativo, período, frequência)
        │  botão habilitado só com ativo e datas válidos
        ▼
app/ui/data_cache       cache de 1 h sobre core/data_loader (dados diários do Yahoo Finance)
        ▼
core/data_processor     limpeza, ordenação e agregação por frequência
        ▼
core/data_availability  período solicitado × disponível
        ▼
core/analyzer, risk_metrics, indicators, comparison, seasonality, simulation, trend
        ▼
st.session_state        resultado da "consulta confirmada"
        ▼
app/ui + core/visualizations   cartões, tabelas e gráficos Plotly
```

### Estrutura de pastas

```text
argos/
├── app/
│   ├── main.py                  # Ponto de entrada: navegação e estilo comum
│   ├── requirements.txt         # Dependências fixadas para o Streamlit Community Cloud
│   ├── views/                   # Páginas (home, análises, simulação, sobre)
│   ├── ui/                      # Componentes de interface (barra lateral, cartões, tabelas, modal, estilo)
│   └── assets/                  # Logotipos institucionais e vídeo da página inicial
├── core/                        # Regras analíticas, dados, métricas, indicadores e textos educativos
├── tests/                       # Suíte de testes automatizados (pytest)
├── data/                        # Respostas salvas da explicação assistida e pacote da demonstração
├── docs/                        # Documentação técnica, metodológica e acadêmica
├── experiments/                 # Experimentos de pesquisa (avaliação da explicação assistida)
├── scripts/                     # Geração dos dados de demonstração e do vídeo da página inicial
├── .streamlit/config.toml       # Tema visual da aplicação
├── .github/workflows/           # Rotina que mantém o app publicado ativo
├── requirements.txt             # Dependências para desenvolvimento local
└── pytest.ini                   # Configuração dos testes e da cobertura mínima
```

Descrição de cada módulo em [`docs/arquitetura.md`](docs/arquitetura.md).

---

## Tecnologias

| Camada | Tecnologia | Papel |
| --- | --- | --- |
| Linguagem | Python 3 | Lógica de dados, cálculos e interface |
| Dados | pandas e NumPy | Séries temporais, agregação, retornos e estatísticas |
| Interface | Streamlit | Aplicação web multipágina, estado de sessão e cache |
| Visualização | Plotly | Gráficos interativos (linhas, candles, mapas de calor) |
| Coleta | yfinance | Acesso às séries históricas do Yahoo Finance |
| Qualidade | pytest e pytest-cov | Testes automatizados e medição de cobertura |
| Publicação | GitHub, GitHub Actions e Streamlit Community Cloud | Versionamento, rotina de keep-alive e hospedagem |
| IA (opcional) | API de modelo de linguagem | Explicação assistida dos gráficos, desligada por padrão |

Versões usadas em produção (fixadas em [`app/requirements.txt`](app/requirements.txt)): Streamlit 1.63, pandas 3.0, NumPy 2.5, Plotly 7.0 e yfinance 1.7.

---

## Instalação e execução

### Pré-requisitos

- Python 3.10 ou superior
- Git

### Passo a passo

Clone o repositório:

```bash
git clone https://github.com/cleristoncramos/argos.git
```

Entre na pasta do projeto:

```bash
cd argos
```

Crie o ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente virtual no Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, libere scripts apenas para o terminal atual e ative de novo:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Ative o ambiente virtual no macOS ou Linux:

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

Inicie a aplicação, a partir da raiz do projeto:

```bash
streamlit run app/main.py
```

A aplicação abre em `http://localhost:8501`. Para encerrar o servidor, use `Ctrl + C` no terminal.

> [!NOTE]
> O `requirements.txt` da raiz lista as versões mínimas para desenvolvimento local. O `app/requirements.txt` fixa as versões exatas usadas pelo Streamlit Community Cloud.

---

## Configuração

A aplicação funciona sem nenhuma configuração adicional. Os recursos opcionais são controlados por variáveis de ambiente ou pelo arquivo `.streamlit/secrets.toml` (que nunca vai para o repositório):

| Variável | Valores | Efeito |
| --- | --- | --- |
| `ARGOS_DEMO_MODE` | `true` / `false` (padrão) | Usa apenas os dados salvos em `data/demo/`, sem acessar a internet |
| `ARGOS_DEMO_DIR` | caminho | Pasta alternativa para o pacote de demonstração |
| `ARGOS_EDU_LAYER` | `on` (padrão) / `off` | Oculta os textos educativos para a condição experimental da avaliação com usuários; os avisos obrigatórios continuam visíveis |
| `ARGOS_LLM_MODE` | `off` (padrão), `demo`, `live` | Controla a explicação assistida: desligada, respostas salvas ou chamadas à API |
| `OPENAI_API_KEY` | chave da API | Necessária apenas no modo `live` da explicação assistida |
| `ARGOS_LLM_RECORD` | `1` | No modo `live`, grava as respostas aprovadas para uso posterior no modo `demo` |

---

## Modo de demonstração

Para apresentações e avaliações com usuários, o Argos pode rodar **sem internet**, a partir de um pacote de dados congelado (CSVs e manifesto com data da coleta e hash SHA-256 de cada arquivo).

Gere o pacote uma vez, com internet:

```bash
python scripts/gerar_dados_demo.py
```

Confira a integridade dos arquivos pelos hashes:

```bash
python scripts/gerar_dados_demo.py --verify
```

Depois, inicie a aplicação com `ARGOS_DEMO_MODE=true`. Um aviso na interface indica que os dados são salvos. Estratégia completa em [`docs/demonstracao.md`](docs/demonstracao.md) e [`docs/versao_congelada.md`](docs/versao_congelada.md).

---

## Testes e qualidade

A suíte possui **806 testes automatizados**, com **100% de cobertura no pacote `core/`**. Ela verifica, entre outros pontos:

- integridade do catálogo e validação de tickers e datas;
- tratamento de dados, lacunas de calendário e agregação por frequência;
- retornos, volatilidade, Sharpe, drawdown, base 100 e correlação;
- indicadores técnicos, inclusive a ausência de informação futura;
- sazonalidade, janelas de retorno e simulação de aportes;
- modo de demonstração, explicação assistida e componentes de interface.

Execute os testes:

```bash
python -m pytest
```

Gere o relatório de cobertura em HTML:

```bash
python -m pytest --cov=core --cov-report=term-missing --cov-report=html
```

O relatório fica em `htmlcov/index.html`. O `pytest.ini` exige cobertura mínima de **80%**; para a versão congelada, a meta é de **95% no `core/`**.

> [!NOTE]
> O projeto ainda não tem pipeline de integração contínua: os testes devem ser executados localmente antes de cada commit. Registro detalhado em [`TESTES.md`](TESTES.md) e [`docs/checkpoint_qualidade.md`](docs/checkpoint_qualidade.md).

---

## Publicação

A aplicação é publicada no **Streamlit Community Cloud**, integrado ao GitHub:

| Configuração | Valor |
| --- | --- |
| Repositório | `cleristoncramos/argos` |
| Branch de produção | `main` |
| Arquivo de entrada | `app/main.py` |
| Endereço | [argos-datalab.streamlit.app](https://argos-datalab.streamlit.app) |

Cada push na `main` dispara uma nova publicação. O Streamlit só recarrega sozinho os módulos da pasta `app/`; por isso, a cada execução, [`app/reload_guard.py`](app/reload_guard.py) verifica se os arquivos de `core/` e `app/` mudaram e, se mudaram, descarta da memória os módulos antigos. Alterações em `.streamlit/config.toml` ainda podem exigir **Reboot app** no painel do Streamlit Cloud.

**Rotina de keep-alive.** O Community Cloud hiberna apps sem visitas por cerca de 12 horas. O workflow [`.github/workflows/keep-alive.yml`](.github/workflows/keep-alive.yml) roda a cada 3 horas e abre o app em um navegador real ([`scripts/manter_app_ativo.py`](scripts/manter_app_ativo.py)); se o app estiver hibernando, clica no botão para acordá-lo. Em repositórios públicos, o GitHub desativa workflows agendados após 60 dias sem atividade; nesse caso, reative-o na aba **Actions**.

---

## Identidade visual

O sistema usa tema claro com profundidade: fundo levemente quente, painéis brancos com sombra suave, detalhes em vermelho, **cantos retos** e **linhas finas escuras** delimitando elementos e seções.

| Arquivo | Conteúdo |
| --- | --- |
| [`.streamlit/config.toml`](.streamlit/config.toml) | Tema base (cores, bordas e raio zero) |
| [`app/ui/design.py`](app/ui/design.py) | CSS comum a todas as páginas |
| [`app/ui/landing.py`](app/ui/landing.py) | Blocos da página inicial e do modal acadêmico |
| [`scripts/video_recursos/animacao.html`](scripts/video_recursos/animacao.html) | Animação do vídeo da página inicial |
| [`scripts/gravar_video_recursos.py`](scripts/gravar_video_recursos.py) | Grava a animação em MP4 |

Os logotipos institucionais ficam em `app/assets/institucional/`, com a origem registrada em `FONTES.md`.

---

## Documentação complementar

| Documento | Conteúdo |
| --- | --- |
| [`docs/arquitetura.md`](docs/arquitetura.md) | Camadas, módulos, fluxo de dados e decisões de projeto |
| [`docs/metodologia_de_calculo.md`](docs/metodologia_de_calculo.md) | Fórmulas, unidades e convenções de todas as métricas |
| [`docs/fontes_e_tratamento_de_dados.md`](docs/fontes_e_tratamento_de_dados.md) | Coleta, preparação, frequências e limitações da fonte |
| [`docs/catalogo-de-ativos.md`](docs/catalogo-de-ativos.md) | Catálogo completo e critérios de inclusão |
| [`docs/fora_do_escopo.md`](docs/fora_do_escopo.md) | O que a plataforma deliberadamente não faz |
| [`docs/demonstracao.md`](docs/demonstracao.md) | Estratégia de demonstração e modo offline |
| [`docs/versao_congelada.md`](docs/versao_congelada.md) | Procedimento de congelamento da versão de avaliação |
| [`docs/validacao_academica.md`](docs/validacao_academica.md) | Cenários de validação e evidências |
| [`docs/llm_7b_implementacao.md`](docs/llm_7b_implementacao.md) | Implementação da explicação assistida |
| [`docs/relatorio_validacao_7a.md`](docs/relatorio_validacao_7a.md) | Avaliação experimental da explicação assistida |
| [`docs/README.md`](docs/README.md) | Índice das fases e etapas de desenvolvimento |
| [`TESTES.md`](TESTES.md) | Registro da estratégia de testes |

---

## Como contribuir

1. Crie uma branch para cada funcionalidade ou correção.
2. Mantenha cálculos e regras de negócio em `core/`; as páginas em `app/` devem apenas exibir resultados.
3. Adicione ou atualize testes para toda alteração em cálculos, tratamento de dados ou regras críticas.
4. Documente em `docs/` qualquer decisão metodológica que altere métricas ou indicadores.
5. Execute `python -m pytest` e confira a interface localmente antes de enviar.
6. Nunca envie chaves de API, arquivos `.env`, ambientes virtuais ou relatórios temporários.

Crie uma branch para a sua alteração:

```bash
git checkout -b feature/nome-da-funcionalidade
```

As mensagens de commit seguem o padrão [Conventional Commits](https://www.conventionalcommits.org/pt-br/) em português (`feat:`, `fix:`, `docs:`, `chore:`, `style:`).

---

## Contexto acadêmico

| Informação | Detalhes |
| --- | --- |
| Instituição | Universidade Federal do Piauí (UFPI) |
| Centro | Centro de Educação Aberta e a Distância (CEAD) |
| Curso | Curso Superior de Tecnologia em Gestão de Dados |
| Programa | Programa Institucional de Bolsas de Iniciação em Desenvolvimento Tecnológico e Inovação (PIBITI UFPI 2026–2027) |
| Plano de trabalho | Análise de Dados para Apoio à Tomada de Decisão em Investimentos no Mercado Financeiro |
| Pesquisador discente | Clériston de Castro Ramos |
| Orientador | Prof. Dr. Arlino Henrique Magalhães de Araújo |

---

## Aviso legal e metodológico

O Argos é um projeto de **pesquisa, ensino e desenvolvimento tecnológico**. Dados históricos e indicadores quantitativos são instrumentos de estudo, não previsões ou garantias.

- Resultados passados não garantem resultados futuros.
- A plataforma não oferece recomendação de compra, venda ou manutenção de ativos.
- Nenhuma informação exibida substitui análise profissional, avaliação de perfil de risco ou orientação de especialista habilitado.
- A disponibilidade e a precisão dos dados dependem de fontes externas.

> [!WARNING]
> O Argos **não deve ser utilizado como ferramenta de recomendação de investimentos**.

---

## Licença

Projeto desenvolvido para fins educacionais e de pesquisa no âmbito do PIBITI UFPI. **Todos os direitos reservados.** As marcas e logotipos da UFPI e do CEAD pertencem às respectivas instituições e são usados apenas para identificar o vínculo acadêmico.
