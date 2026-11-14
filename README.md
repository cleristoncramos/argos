# Argos — Plataforma de Análise Histórica de Ativos Financeiros

**Análise exploratória de ativos, comparação de desempenho, indicadores técnicos, métricas de risco, sazonalidade, eventos históricos e simulação de aportes, com finalidade educacional e de pesquisa.**

[![Aplicação online](https://img.shields.io/badge/app-online-C8102E)](https://argos-datalab.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.63-FF4B4B?logo=streamlit&logoColor=white)
![Testes](https://img.shields.io/badge/testes-1.258%20aprovados-2E7D32)
![Cobertura](https://img.shields.io/badge/cobertura%20do%20core-100%25-2E7D32)
![PIBITI UFPI](https://img.shields.io/badge/PIBITI-UFPI%202026%E2%80%932027-1F1F1F)

O **Argos** permite analisar milhares de ativos financeiros com dados do Yahoo Finance. Ele parte de um catálogo curado de **148 ativos em 13 grupos** (ações brasileiras, americanas, europeias e asiáticas, ETFs, FIIs, REITs, criptomoedas, moedas, commodities, índices e taxas de juros) e aceita qualquer outro código disponível na fonte. Os dados viram gráficos interativos, métricas quantitativas e textos explicativos em linguagem simples, que dizem o que cada número mostra e o que ele **não** permite concluir.

O projeto foi desenvolvido no **Programa Institucional de Bolsas de Iniciação em Desenvolvimento Tecnológico e Inovação (PIBITI) da Universidade Federal do Piauí**, ciclo 2026–2027.

> [!IMPORTANT]
> O Argos tem finalidade **exclusivamente acadêmica, educacional e de desenvolvimento tecnológico**. As informações, métricas e visualizações descrevem dados históricos e **não constituem recomendação, indicação ou aconselhamento de investimento**. Os resultados podem variar entre execuções, e o padrão histórico não garante repetição.

**Aplicação publicada:** [argos-datalab.streamlit.app](https://argos-datalab.streamlit.app)

---

## Sumário

1. [Sobre o projeto](#sobre-o-projeto)
2. [Sobre o nome](#sobre-o-nome)
3. [Funcionalidades](#funcionalidades)
4. [Camada educativa](#camada-educativa)
5. [Eventos históricos](#eventos-históricos)
6. [Explicação assistida e pesquisa com modelos de linguagem](#explicação-assistida-e-pesquisa-com-modelos-de-linguagem)
7. [Catálogo de ativos](#catálogo-de-ativos)
8. [Metodologia de cálculo](#metodologia-de-cálculo)
9. [Fonte e tratamento dos dados](#fonte-e-tratamento-dos-dados)
10. [Arquitetura](#arquitetura)
11. [Tecnologias](#tecnologias)
12. [Instalação e execução](#instalação-e-execução)
13. [Configuração](#configuração)
14. [Modo de demonstração](#modo-de-demonstração)
15. [Testes e qualidade](#testes-e-qualidade)
16. [Publicação](#publicação)
17. [Identidade visual](#identidade-visual)
18. [Situação do projeto](#situação-do-projeto)
19. [Documentação complementar](#documentação-complementar)
20. [Como contribuir](#como-contribuir)
21. [Contexto acadêmico](#contexto-acadêmico)
22. [Aviso legal e metodológico](#aviso-legal-e-metodológico)
23. [Licença](#licença)

---

## Sobre o projeto

Dados de mercado estão amplamente disponíveis, mas interpretá-los exige conhecimento técnico. Gráficos e indicadores costumam aparecer sem a fórmula, sem as premissas e misturados a sugestões de compra e venda, o que dificulta o estudo crítico. O Argos aproxima esses dois lados: cada análise vem com a fórmula usada, as premissas adotadas e uma leitura em linguagem simples do resultado e dos seus limites.

**Público:** estudantes, pesquisadores e pessoas interessadas em mercado financeiro que desejam examinar dados históricos com rigor, inclusive sem formação prévia na área.

**Perguntas que a plataforma ajuda a responder:**

| Pergunta | Onde |
| --- | --- |
| Como um ativo se comportou ao longo do tempo? O que acontecia no mundo naquele período? | Análise Individual |
| Há meses historicamente melhores ou piores? Em quais anos o padrão não se repetiu? | Análise Individual (sazonalidade) |
| Qual ativo foi mais longe no mesmo período? Eles se movem juntos? | Comparação de Ativos |
| O que mostram as médias móveis, as Bandas de Bollinger, o RSI e o MACD? | Indicadores Técnicos |
| Quanto o ativo oscilou e qual foi a maior queda desde um pico? Quanto tempo levou para se recuperar? | Risco e Retorno |
| Se eu tivesse investido R$ 1.000 há um ano, quanto teria hoje? E com um valor fixo todo mês? | Simulação de Aportes |
| Como os ativos de um mesmo grupo se comportaram no mesmo período? | Panorama do Catálogo |

**Princípios do projeto:**

- **Transparência:** fórmulas, parâmetros e convenções documentados e visíveis na interface.
- **Neutralidade:** os textos descrevem o passado; nenhum ativo é apontado como "melhor" ou "pior" para investir, e nenhuma tela faz previsão.
- **Honestidade sobre os limites:** todo resultado vem acompanhado do que ele não permite concluir, e eventos históricos são apresentados como contexto, nunca como causa.
- **Reprodutibilidade:** cálculos isolados em `core/`, cobertos por testes, e um modo de demonstração com dados congelados e verificados por hash.
- **Separação de responsabilidades:** interface em `app/`, regras analíticas em `core/`.

---

## Sobre o nome

O nome vem da mitologia grega. Jasão recebeu a missão de buscar o velocino de ouro, guardado na Cólquida por um dragão que nunca dormia. Para a viagem, o construtor **Argos** ergueu, com a ajuda de Atena, o navio que levou o seu nome, o **Argo**, e Jasão reuniu os argonautas, heróis de talentos diferentes. A plataforma retoma essa viagem como analogia:

| Na viagem | No Argos |
| --- | --- |
| O navio | A plataforma, que organiza dados de vários mercados e descreve o caminho já percorrido, sem prever o próximo trecho |
| A tripulação | As classes de ativos, cada uma com comportamento próprio |
| O mar e as rochas | As crises, quedas e períodos de volatilidade registrados no histórico |
| O velocino | O entendimento dos dados, não um lucro: nenhum dado histórico oferece garantia de resultado |

O nome completo, **Argos — Plataforma de Análise Histórica de Ativos Financeiros**, é o nome definitivo do sistema. A história completa está na página **Sobre o Projeto**, na seção "Por que Argos".

---

## Funcionalidades

O menu principal tem oito páginas: seis módulos de análise, a página Configurações e a página Sobre o Projeto. Nos módulos de análise, a barra lateral **Parâmetros** reúne a escolha do ativo, o período e a frequência.

### Escolha do ativo e do período (barra lateral "Parâmetros")

- Escolha guiada por **grupo de ativos** ou digitação livre do **ticker**, com validação do formato e da existência na fonte.
- Assim que o ativo é escolhido, a barra mostra o **período disponível** ("Dados disponíveis de … a …"), e o seletor de datas fica limitado a esse período.
- Atalhos de período (1, 3, 5 e 10 anos) ou intervalo personalizado. Se um atalho começa antes do primeiro dado do ativo, o início é ajustado automaticamente e um aviso explica o ajuste.
- Frequência diária, semanal, mensal, semestral ou anual.
- A análise só é refeita quando o usuário clica no botão de carregar ("consulta confirmada"); mudar um controle não altera a análise que está na tela.

### Página inicial

- Nome, subtítulo e o botão **Get Started**, que abre a Análise Individual.
- Texto de apresentação, quadro com os números do catálogo e cartões de "Primeiros passos" para os seis módulos de análise.
- Vídeo com um tour pelos recursos e mosaico animado com os logotipos dos ativos do catálogo.
- Botão **Informações acadêmicas**, que abre um quadro com a identificação do trabalho, as instituições, as tecnologias e as bases de dados.

### Análise Individual

- Cartão do ativo ao lado do resumo de disponibilidade (período solicitado × disponível, destacado em vermelho quando o histórico é menor que o pedido) e dos **alertas de qualidade dos dados**: mudança de patamar que se desfaz em poucos dias, variações diárias atípicas, preço sem variação, dias sem volume, intervalos sem dados e histórico curto. Os alertas indicam o que merece atenção, sem afirmar erro.
- Visão geral: primeiro e último valor, retorno total e número de observações.
- **Variação por prazo** (1, 3 e 6 meses, neste ano, 1, 2, 3, 5 e 10 anos), com as datas usadas, a variação acumulada e a taxa equivalente ao ano, e um rodapé com os termos da tabela explicados em linguagem simples.
- **Evolução temporal** do preço com os **eventos históricos** marcados como linhas pontilhadas (ver [Eventos históricos](#eventos-históricos)).
- **Comparação com uma referência de mercado** em Base 100 (Ibovespa, S&P 500, Bitcoin, ouro ou a referência escolhida em Configurações), com o motivo da sugestão, datas comuns, avisos de moeda e calendário e opção de trocar ou desativar.
- **Volatilidade anualizada mês a mês**, também com os eventos históricos.
- Variação percentual por período e **maiores altas e quedas**, com datas, fechamentos comparados e contagem de variações positivas e negativas.
- **Sazonalidade:**
  - mapa de calor de retornos mensais (mês × ano) e média por mês do calendário;
  - **anos comparados à média**: por padrão, uma barra por mês com a diferença em relação à média de todos os anos; opcionalmente, os valores lado a lado;
  - **variação entre dois meses** do calendário em cada ano (setembro → outubro como padrão), com o aviso de quais anos **não seguiram o sentido da maioria**, inclusive entre os mais recentes;
  - aviso fixo: "Os resultados podem variar entre execuções. O padrão histórico não garante repetição.";
  - dica de leitura ("Como ler") embaixo de cada gráfico.
- Dados processados em tabela e exportação em CSV.

### Comparação de Ativos

- De **2 a 5 ativos**, inclusive de grupos diferentes, com evolução em **Base 100**.
- Seleção por grupo, com filtros opcionais de **subclasse** (setor ou tipo) e **mercado** (país ou bolsa).
- Opção de comparar apenas o **período comum** a todos os ativos.
- Matriz de correlação dos retornos, resumo comparativo e destaques descritivos do período.
- Tendência histórica com **retorno móvel** (3, 6 ou 12 meses) e **razão de desempenho** em relação a um ativo de referência.
- Sazonalidade comparada entre os ativos, com o aviso de que o padrão histórico não garante repetição.
- Alertas de qualidade dos dados agrupados por ativo.

### Indicadores Técnicos

- Gráfico de linha de fechamento ou de **candles**.
- **SMA** e **EMA** (curta e longa), **Bandas de Bollinger**, **RSI**, **MACD**, **ATR**, volatilidade móvel e volume.
- Parâmetros ajustáveis e um guia de leitura para cada indicador.

### Risco e Retorno

- Retorno acumulado, retorno médio, **volatilidade anualizada**, **Índice de Sharpe** (com taxa livre de risco configurável), **drawdown máximo** e a data do fundo da maior queda.
- Percentual de períodos positivos, melhor e pior período.
- Curva de drawdown e distribuição dos retornos por faixas.
- **Maiores quedas e tempo de recuperação:** pico, fundo, data em que o preço voltou ao pico e duração de cada etapa. Quedas ainda não recuperadas aparecem como tal, sem estimativa.

### Simulação de Aportes

- Calculadora "Se você tivesse investido": valor e prazo (1, 2, 3, 5 ou 10 anos, todo o período ou uma data), com valor final, ganho ou perda, variação total e anual, pior e melhor momento do caminho e gráfico da trajetória.
- Aporte único versus aportes periódicos com o mesmo total investido.
- Janelas históricas de horizonte fixo, com menor, mediano e maior resultado e a proporção de janelas positivas.
- Premissas explícitas: preço de fechamento, sem dividendos, taxas, impostos ou inflação.

### Panorama do Catálogo

- Todos os ativos de um grupo no mesmo período (1, 3 ou 5 anos), um grupo por vez.
- Variação no período e em 12 meses ao lado da volatilidade anualizada e da queda máxima, com a data de início dos dados e os alertas de qualidade.
- Ordem inicial por nome e aviso de que a ordenação não é recomendação; dados indisponíveis aparecem vazios, nunca como zero.

### Configurações

- **Referência de comparação padrão:** automática pela classe do ativo (o padrão), uma das quatro referências fixas, qualquer ativo do catálogo ou um ticker digitado, conferido na fonte. Na versão pública, a escolha vale até fechar o navegador; numa instalação local com o catálogo editável, fica salva.
- **Catálogo de ativos:** na versão pública, fixo e somente leitura, com a lista de grupos e quantidades. Numa **instalação local**, com `ARGOS_CATALOGO_EDITAVEL=on`, é possível criar grupos e acrescentar ativos, sempre conferidos na fonte antes de salvar. Os acréscimos ficam numa camada em SQLite por cima do catálogo base, que não muda, e aparecem na barra lateral e na Comparação de Ativos.

### Sobre o Projeto

- Contexto e público, objetivos da pesquisa, os seis módulos de análise, metodologia, dados e catálogo, qualidade, escopo, equipe, a origem do nome ("Por que Argos") e o aviso legal.

---

## Camada educativa

Os textos educativos acompanham cada análise e podem ser desligados para a condição experimental da avaliação com usuários (`ARGOS_EDU_LAYER=off`); os avisos obrigatórios aparecem sempre.

- **"Como ler este gráfico":** roteiro fixo de cada gráfico, com o que ele mede, o que mostra, os cuidados e o que ele não permite concluir. O inventário completo está em [`docs/inventario_graficos.md`](docs/inventario_graficos.md).
- **Dicas de leitura** curtas, sempre visíveis, embaixo dos gráficos de sazonalidade.
- **"O que significa?"** e **glossário** com os termos de cada página.
- **Rodapé de termos** da tabela de variação por prazo.
- **Avisos obrigatórios:** natureza histórica dos dados, ausência de recomendação, premissas da simulação e o aviso de que o padrão histórico não garante repetição.

---

## Eventos históricos

Os gráficos de preço e de volatilidade da Análise Individual marcam, como linhas pontilhadas, acontecimentos que mexeram com o mercado no período carregado. Ao passar o mouse, aparecem o título, a data, a descrição e a fonte do evento.

- **Base do sistema:** [`data/eventos_historicos.csv`](data/eventos_historicos.csv), com **39 eventos de 2016 a 2026**. **Todo evento tem fonte e endereço**, conferidos, com preferência por fontes oficiais ou públicas (TSE, Agência Senado, Agência Brasil, Anvisa, OMS e OPAS, Nações Unidas, Federal Reserve, FDIC, entre outras).
- **Categorias**, que ligam e desligam pela legenda e pelo filtro: Mercado e crises, Saúde, Política, Mundo e **Do ativo**.
- **Eventos de um ativo:** a categoria "Do ativo" só aparece na análise dos ativos indicados na coluna `ativos` (por exemplo, Brumadinho para VALE3.SA, a falência da FTX para BTC-USD e ETH-USD, e o DeepSeek e o caso de espionagem para NVDA).
- **Quadro "Eventos no período e fontes":** lista os eventos do período com o link de cada fonte.
- **Eventos do usuário:** o botão "Adicionar evento próprio" inclui eventos na sessão do navegador, que podem ser baixados em CSV e carregados de novo numa próxima visita.
- **Contexto, não causa:** a tela avisa que as linhas não indicam que o evento causou a variação do ativo.

Para acrescentar um evento à base, inclua uma linha no CSV com `data`, `categoria`, `titulo`, `descricao`, `fonte`, `url` e, se for de um ativo específico, os tickers em `ativos`, separados por espaço. Os testes exigem fonte e endereço `https://` em todo evento do sistema.

---

## Explicação assistida e pesquisa com modelos de linguagem

O Argos tem duas camadas de explicação por modelo de linguagem, com protocolos separados e congelados por hash. **Nenhuma delas faz recomendação.**

| Camada | Situação | Uso |
| --- | --- | --- |
| **v0.6** (etapa 7B) | Implementada e **desligada por padrão** (`ARGOS_LLM_MODE=off`) | Texto educativo a partir das métricas de uma tela, com prompt congelado (impressão `e3b3574b7430`), resposta em JSON validada antes de exibir, limites de uso e custo e texto fixo de reserva. No modo de demonstração, usa só respostas gravadas e validadas. Detalhes em [`docs/llm_7b_implementacao.md`](docs/llm_7b_implementacao.md) |
| **v1.0-experimental** | Em **avaliação de pesquisa**; **não aparece na versão pública** | Explica separadamente a observação histórica, a estimativa de um modelo autorizado e a conclusão de um motor de decisão. Como nenhum modelo preditivo nem motor de decisão está autorizado pela política, toda estimativa sai como abstenção. Protocolo em [`docs/protocolo_llm_v1.0-experimental.md`](docs/protocolo_llm_v1.0-experimental.md) |

**Rodada de avaliação da v1.0-experimental (fase 1):**

- conjunto congelado de casos (fase1-v2), comparado a um template determinístico, sem modelo de linguagem, que serve de referência;
- provedor `grok-4.3` (xAI), pela Responses API, com temperatura 0 e esforço de raciocínio `low`;
- cada chamada passa pela política, pelas 17 verificações do validador e por um contador de custo, que reserva o custo antes de cada tentativa e recusa a chamada antes de passar de US$ 16 ou de 200 tentativas;
- rodada de 66 chamadas concluída em 13/11/2026; a avaliação cega com dois avaliadores começa em 15/11/2026.

O registro completo está em [`docs/llm_v1_exp_fase1.md`](docs/llm_v1_exp_fase1.md) e em [`docs/pibiti/decisoes_orientador.md`](docs/pibiti/decisoes_orientador.md) (DL2-I).

A **linha preditiva** é pesquisa à parte, com pilotos encerrados sem modelo elegível ([`docs/plano_reformulacao_preditiva.md`](docs/plano_reformulacao_preditiva.md)). Nenhuma previsão é exibida na plataforma.

---

## Catálogo de ativos

O catálogo base fica em [`core/assets.py`](core/assets.py) e reúne **148 ativos em 13 grupos e 9 classes**:

| Grupo | Classe | Ativos | Exemplos |
| --- | --- | ---: | --- |
| Criptomoedas | Criptomoeda | 19 | BTC-USD, ETH-USD, LTC-USD, HASH11.SA (ETF da B3) |
| Ações Brasil | Ação | 22 | PETR4.SA, VALE3.SA, SBSP3.SA |
| Ações EUA | Ação | 17 | AAPL, MSFT, NVDA |
| Ações Europa | Ação | 8 | ASML, SAP, NESN.SW |
| Ações Ásia | Ação | 8 | TSM, SONY, 005930.KS |
| ETFs de ações | ETF | 14 | SPY, QQQ, BOVA11.SA |
| ETFs de renda fixa | ETF | 6 | BND, AGG, TLT |
| REITs / mercado imobiliário | REIT | 5 | VNQ, O, PLD |
| FIIs Brasil | FII | 7 | MXRF11.SA, HGLG11.SA, KNCR11.SA |
| Índices de mercado | Índice | 12 | ^BVSP, ^GSPC, ^IXIC |
| Forex | Forex | 8 | USDBRL=X, EURUSD=X, USDJPY=X |
| Commodities | Commodity | 15 | GC=F, CL=F, GOLD11.SA (ETF da B3) |
| Treasury / taxas de juros | Renda Fixa | 7 | ^IRX, ^TNX, ^TYX |

Além do catálogo, **qualquer ticker disponível no Yahoo Finance** pode ser digitado na barra lateral (por exemplo, `AMD`, `EMBR3.SA`, `BRK-B`, `^STOXX50E`). Numa instalação local, o catálogo também pode ser ampliado pela página Configurações. A lista completa, com critérios de inclusão e o registro da ampliação, está em [`docs/catalogo-de-ativos.md`](docs/catalogo-de-ativos.md).

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
| Variação por prazo | `valor final / valor no início da janela − 1`; taxa anual `(1 + variação)^(1/anos) − 1` só para prazos de 1 ano ou mais; "Neste ano" vai do último dia do ano anterior à última data disponível |
| Sazonalidade | Fechamento de cada mês = último valor do mês; variação entre dois meses = composta; o mês em andamento não entra nas médias; "anos fora do padrão" = anos com sentido contrário ao da maioria |
| Quedas e recuperação | Episódio do pico ao fundo e à volta ao pico; durações em dias corridos; queda não recuperada sem estimativa |
| Referência de mercado | Ativo e referência em Base 100 só nas datas comuns, sem beta nem regressão |
| Alertas de qualidade | Heurísticas por tipo de série (por exemplo, variação diária acima de 25% em ações e de 50% em criptomoedas, e atípica para o próprio ativo), calibradas no catálogo e documentadas |

---

## Fonte e tratamento dos dados

| Fonte | Conteúdo | Uso |
| --- | --- | --- |
| **Yahoo Finance** (via `yfinance`) | Séries diárias de abertura, máxima, mínima, fechamento e volume | Base de todas as análises; consulta sob demanda com cache de 1 hora |
| **Catálogo interno** | Ticker, nome, classe, mercado e descrição dos ativos | Seleção guiada e organização da interface |
| **Base de eventos históricos** | Data, categoria, título, descrição, fonte, endereço e ativos de cada evento | Contexto nos gráficos de preço e de volatilidade |
| **Pacote de demonstração** | CSVs congelados dos 148 ativos, com manifesto e hash SHA-256 | Apresentações e avaliação sem depender da internet |
| **CoinCap** e **Financial Modeling Prep** | Logotipos públicos de criptomoedas, ações, ETFs, REITs e FIIs | Identificação visual dos ativos |

**Tratamento:** os dados diários são baixados uma única vez; as frequências semanal, mensal, semestral e anual são derivadas localmente por agregação (abertura, máxima, mínima, fechamento e volume somado). Datas inválidas são descartadas, e falhas temporárias da fonte não ficam guardadas em cache. A série diária passa por verificações automáticas de qualidade, que geram alertas na tela sem alterar nem remover dados. O período disponível de cada ativo é consultado com buscas pequenas (uma mensal e duas diárias) e guardado em cache por 1 hora.

**Limitações conhecidas:**

- Os retornos são **de preço**: dividendos e proventos não são incorporados, o que subestima o retorno total de ações pagadoras e FIIs.
- O mesmo fator de anualização (252) é usado para criptoativos, que negociam todos os dias, por comparabilidade entre classes.
- Valores em moedas diferentes não são convertidos; a Base 100 compara trajetórias, não preços.
- A fonte pode apresentar atrasos, ajustes históricos, mudanças de ticker e indisponibilidade temporária.

Detalhes em [`docs/fontes_e_tratamento_de_dados.md`](docs/fontes_e_tratamento_de_dados.md) e [`docs/fora_do_escopo.md`](docs/fora_do_escopo.md).

---

## Arquitetura

A aplicação segue uma separação em camadas: as páginas em `app/` cuidam apenas da interface e delegam todos os cálculos ao pacote `core/`, que não depende do Streamlit e é integralmente testado.

```text
Barra lateral "Parâmetros" (ativo, período limitado ao histórico, frequência)
        │  botão habilitado só com ativo e datas válidos
        ▼
app/ui/data_cache       cache de 1 h sobre core/data_loader (dados diários do Yahoo Finance)
        ▼
core/data_processor     limpeza, ordenação e agregação por frequência
        ▼
core/data_availability  período solicitado × disponível
core/data_quality       alertas de qualidade da série diária
        ▼
core/analyzer, risk_metrics, indicators, comparison, seasonality, simulation, trend,
     trailing_returns, extreme_moves, drawdown_episodes, benchmark, panorama,
     historical_events
        ▼
st.session_state        resultado da "consulta confirmada"
        ▼
app/ui + core/visualizations   cartões, tabelas e gráficos Plotly
```

### Estrutura de pastas

```text
argos/
├── app/
│   ├── main.py                  # Ponto de entrada: navegação, estilo comum e recarga de módulos após deploy
│   ├── reload_guard.py          # Recarrega core/ e app/ depois de um deploy, sem quebrar sessões em andamento
│   ├── requirements.txt         # Dependências fixadas para o Streamlit Community Cloud
│   ├── views/                   # Páginas: início, seis análises, configurações e sobre
│   ├── ui/                      # Componentes: barra lateral, cartões, tabelas, eventos, catálogo, estilo
│   └── assets/                  # Logotipos institucionais e vídeo da página inicial
├── core/                        # Regras analíticas, dados, métricas, indicadores, eventos, catálogo local e LLM
├── data/
│   ├── eventos_historicos.csv   # Base de eventos históricos com fonte (versionada)
│   ├── llm_demo.json            # Respostas salvas da explicação assistida (versionadas)
│   └── demo/                    # Pacote da demonstração (fora do Git)
├── tests/                       # Suíte de testes automatizados (pytest)
├── docs/                        # Documentação técnica, metodológica e acadêmica
├── experiments/                 # Pesquisa: avaliação da explicação assistida e linha preditiva
├── scripts/                     # Dados de demonstração, vídeo da página inicial e keep-alive
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
| Linguagem | Python 3.12+ | Lógica de dados, cálculos e interface |
| Dados | pandas e NumPy | Séries temporais, agregação, retornos e estatísticas |
| Interface | Streamlit | Aplicação web multipágina, estado de sessão e cache |
| Visualização | Plotly | Gráficos interativos (linhas, candles, barras e mapas de calor) |
| Coleta | yfinance | Acesso às séries históricas do Yahoo Finance |
| Persistência local | SQLite (biblioteca padrão) | Catálogo editável e preferências numa instalação local |
| Qualidade | pytest e pytest-cov | Testes automatizados e medição de cobertura |
| Publicação | GitHub, GitHub Actions e Streamlit Community Cloud | Versionamento, rotina de keep-alive e hospedagem |
| Pesquisa com LLM | APIs de modelos de linguagem (OpenAI e xAI) | Explicação assistida, desligada por padrão, e rodadas de avaliação |

Versões usadas em produção (fixadas em [`app/requirements.txt`](app/requirements.txt)): Streamlit 1.63, pandas 3.0, NumPy 2.5, Plotly 7.0 e yfinance 1.7.

---

## Instalação e execução

### Pré-requisitos

- Python 3.12 ou superior (exigido pelo NumPy 2.5; testado no 3.13 e no 3.14)
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

Para usar o catálogo editável numa instalação local, inicie com a variável ligada (PowerShell):

```powershell
$env:ARGOS_CATALOGO_EDITAVEL = "on"; streamlit run app/main.py
```

> [!NOTE]
> O `requirements.txt` da raiz lista as versões mínimas para desenvolvimento local. O `app/requirements.txt` fixa as versões exatas usadas pelo Streamlit Community Cloud.

---

## Configuração

A aplicação funciona sem nenhuma configuração adicional. Os recursos opcionais são controlados por variáveis de ambiente ou pelo arquivo `.streamlit/secrets.toml`, que nunca vai para o repositório:

| Variável | Valores | Efeito |
| --- | --- | --- |
| `ARGOS_DEMO_MODE` | `true` / `false` (padrão) | Usa apenas os dados salvos em `data/demo/`, sem acessar a internet |
| `ARGOS_DEMO_DIR` | caminho | Pasta alternativa para o pacote de demonstração |
| `ARGOS_CATALOGO_EDITAVEL` | `on` / desligado (padrão) | Só em instalação local: libera a edição do catálogo na página Configurações (grupos novos e ativos acrescentados, guardados em `data/catalogo_local.sqlite`). Na versão pública fica desligado, e o catálogo é somente leitura |
| `ARGOS_CATALOGO_ARQUIVO` | caminho | Arquivo SQLite alternativo para o catálogo local |
| `ARGOS_EDU_LAYER` | `on` (padrão) / `off` | Oculta os textos educativos para a condição experimental da avaliação com usuários; os avisos obrigatórios continuam visíveis |
| `ARGOS_LLM_MODE` | `off` (padrão), `demo`, `live` | Controla a explicação assistida v0.6: desligada, respostas salvas ou chamadas à API |
| `OPENAI_API_KEY` | chave da API | Necessária apenas no modo `live` da explicação assistida v0.6 |
| `ARGOS_LLM_RECORD` | `1` | No modo `live`, grava as respostas aprovadas para uso posterior no modo `demo` |
| `XAI_API_KEY` | chave da API da xAI | Só para a rodada de avaliação da camada v1.0-experimental; fica no ambiente de quem executa a rodada, nunca no repositório, em log ou no navegador |

---

## Modo de demonstração

Para apresentações e avaliações com usuários, o Argos pode rodar **sem internet**, a partir de um pacote de dados congelado (CSVs e manifesto com data da coleta e hash SHA-256 de cada arquivo).

Gere o pacote uma vez, com internet, para o catálogo inteiro e a partir de uma data fixa:

```bash
python scripts/gerar_dados_demo.py --catalog --start 2020-12-01
```

O início em 01/12/2020 cobre o período das respostas de IA salvas em `data/llm_demo.json` (04/01/2021 a 31/12/2025), para que elas também apareçam no modo de dados salvos. Sem `--catalog`, o gerador usa só cinco ativos de referência.

Confira a integridade dos arquivos pelos hashes:

```bash
python scripts/gerar_dados_demo.py --verify
```

Depois, inicie a aplicação com `ARGOS_DEMO_MODE=true`. Um aviso na interface indica a versão do pacote e a data dos dados salvos. No modo de demonstração, a digitação livre de tickers e a edição do catálogo ficam desligadas.

- **Snapshot atual:** `v1.1-demo-preliminar`, de 25/10/2026, com 148 ativos de 01/12/2020 a 23/10/2026. O pacote fica fora do Git, por causa dos termos de uso da fonte.
- **Validação:** o teste completo sem internet é feito na **instalação local**. O teste de memória verifica, separadamente, a aplicação hospedada no Streamlit Community Cloud.

Estratégia completa em [`docs/demonstracao.md`](docs/demonstracao.md) e [`docs/versao_congelada.md`](docs/versao_congelada.md).

---

## Testes e qualidade

A suíte possui **1.258 testes automatizados**, com **100% de cobertura no pacote `core/`**. Ela verifica, entre outros pontos:

- integridade do catálogo, do catálogo local e da base de eventos (inclusive a fonte de cada evento);
- validação de tickers, datas e do período disponível de cada ativo;
- tratamento de dados, lacunas de calendário e agregação por frequência;
- retornos, volatilidade, Sharpe, drawdown, Base 100 e correlação;
- indicadores técnicos, inclusive a ausência de informação futura;
- sazonalidade, anos fora do padrão, janelas de retorno e simulação de aportes;
- alertas de qualidade dos dados, variação por prazo, quedas e recuperação, maiores altas e quedas, referência de mercado e panorama do catálogo;
- modo de demonstração, explicação assistida, protocolo da camada experimental (hashes, política e as 17 verificações) e contador de custo;
- **teste de fumaça** (Streamlit AppTest): a página inicial e o estado inicial de cada página abrem sem exceção.

Execute os testes:

```bash
python -m pytest
```

Gere o relatório de cobertura em HTML:

```bash
python -m pytest --cov=core --cov-report=term-missing --cov-report=html
```

O relatório fica em `htmlcov/index.html`. O `pytest.ini` exige cobertura mínima de **95% no `core/`**; a suíte falha abaixo disso.

> [!NOTE]
> O projeto não tem pipeline de integração contínua: os testes devem ser executados localmente antes de cada commit. Depois de cada publicação relevante, a versão no ar é conferida por funcionalidade, com data, commit e evidências, em [`docs/verificacao_publicacao.md`](docs/verificacao_publicacao.md). Registro detalhado em [`TESTES.md`](TESTES.md) e [`docs/checkpoint_qualidade.md`](docs/checkpoint_qualidade.md).

---

## Publicação

A aplicação é publicada no **Streamlit Community Cloud**, integrado ao GitHub:

| Configuração | Valor |
| --- | --- |
| Repositório | `cleristoncramos/argos` |
| Branch de produção | `main` |
| Arquivo de entrada | `app/main.py` |
| Endereço | [argos-datalab.streamlit.app](https://argos-datalab.streamlit.app) |

O endereço mantém o identificador técnico criado na primeira publicação do app; o nome do sistema é **Argos — Plataforma de Análise Histórica de Ativos Financeiros**.

Cada push na `main` dispara uma nova publicação. O Streamlit só recarrega sozinho os módulos da pasta `app/`; por isso, a cada execução, [`app/reload_guard.py`](app/reload_guard.py) verifica se os arquivos de `core/` e `app/` mudaram e, se mudaram, descarta da memória os módulos antigos. Essa limpeza é feita por uma sessão de cada vez e preserva os módulos que outra sessão ainda está importando. Alterações em `.streamlit/config.toml` podem exigir **Reboot app** no painel do Streamlit Cloud.

**Rotina de keep-alive.** O Community Cloud hiberna apps sem visitas por cerca de 12 horas. O workflow [`.github/workflows/keep-alive.yml`](.github/workflows/keep-alive.yml) roda a cada 3 horas e abre o app em um navegador real ([`scripts/manter_app_ativo.py`](scripts/manter_app_ativo.py)); se o app estiver hibernando, clica no botão para acordá-lo. Em repositórios públicos, o GitHub desativa workflows agendados após 60 dias sem atividade; nesse caso, reative-o na aba **Actions**.

---

## Identidade visual

O sistema usa tema claro com profundidade: fundo papel levemente quente (`#F7F6F2`), tinta quase preta (`#111111`), carmim (`#C8102E`) como cor de destaque, o degradê carmim-laranja do título da página inicial, **cantos retos** e **linhas finas escuras** delimitando elementos e seções. A tipografia combina Source Sans 3 nos textos e JetBrains Mono nos números.

| Arquivo | Conteúdo |
| --- | --- |
| [`.streamlit/config.toml`](.streamlit/config.toml) | Tema base (cores, bordas e raio zero) |
| [`app/ui/design.py`](app/ui/design.py) | CSS comum a todas as páginas |
| [`app/ui/landing.py`](app/ui/landing.py) | Blocos da página inicial e do quadro acadêmico |
| [`scripts/video_recursos/animacao.html`](scripts/video_recursos/animacao.html) | Animação do vídeo da página inicial |
| [`scripts/gravar_video_recursos.py`](scripts/gravar_video_recursos.py) | Grava a animação em MP4 |

Os logotipos institucionais ficam em `app/assets/institucional/`, com a origem registrada em `FONTES.md`. A logomarca do sistema está em definição, a partir de um conjunto de propostas na paleta acima.

---

## Situação do projeto

| Etapa | Situação |
| --- | --- |
| Plano de ampliação do catálogo e das análises (fases 1 a 3) | Concluído e verificado na publicação em 25/10/2026 |
| Modo de demonstração | Snapshot do catálogo ampliado gerado e conferido em 25/10/2026 |
| Camada de linguagem v1.0-experimental | Protocolo aprovado e hashes ratificados (DL1, 09/11/2026) |
| Plano da reunião de 10/11/2026 (DL2), etapas 1 a 5 | Concluídas em 13/11/2026: ajustes de interface, período por ativo, aviso de não determinismo e destaques da sazonalidade, página Configurações e eventos históricos com fonte |
| DL2, etapa 6: explicação por LLM com o `grok-4.3` | Rodada de 66 chamadas concluída em 13/11/2026; avaliação cega com dois avaliadores a partir de 15/11/2026 |
| Janeiro de 2027 | Snapshot final, roteiro completo sem internet (local), teste de memória no Streamlit Cloud e consolidação das evidências |
| Fevereiro de 2027 | Congelamento da versão de avaliação, identificada por commit e tag |

A coleta de dados com participantes (O6) depende de parecer favorável do Comitê de Ética em Pesquisa e não começa antes disso. O plano detalhado da DL2 está em [`docs/plano_reuniao_2026-11-10.md`](docs/plano_reuniao_2026-11-10.md), e as pendências em [`docs/checklist_pendencias.md`](docs/checklist_pendencias.md).

---

## Documentação complementar

| Documento | Conteúdo |
| --- | --- |
| [`docs/arquitetura.md`](docs/arquitetura.md) | Camadas, módulos, fluxo de dados e decisões de projeto |
| [`docs/metodologia_de_calculo.md`](docs/metodologia_de_calculo.md) | Fórmulas, unidades e convenções de todas as métricas |
| [`docs/fontes_e_tratamento_de_dados.md`](docs/fontes_e_tratamento_de_dados.md) | Coleta, preparação, frequências e limitações da fonte |
| [`docs/catalogo-de-ativos.md`](docs/catalogo-de-ativos.md) | Catálogo completo, critérios de inclusão e registro da ampliação |
| [`docs/inventario_graficos.md`](docs/inventario_graficos.md) | Gráficos do sistema e seus roteiros "Como ler este gráfico" |
| [`docs/fora_do_escopo.md`](docs/fora_do_escopo.md) | O que a plataforma deliberadamente não faz |
| [`docs/plano_ampliacao_catalogo_e_analises.md`](docs/plano_ampliacao_catalogo_e_analises.md) | Plano de ampliação, registro de execução e cronograma |
| [`docs/plano_reuniao_2026-11-10.md`](docs/plano_reuniao_2026-11-10.md) | Plano da reunião de 10/11/2026 (DL2) e execução de cada etapa |
| [`docs/plano_reformulacao_preditiva.md`](docs/plano_reformulacao_preditiva.md) | Proposta de reformulação com as camadas preditiva e decisória |
| [`docs/protocolo_prompts_llm.md`](docs/protocolo_prompts_llm.md) | Protocolo da explicação assistida v0.6 |
| [`docs/protocolo_llm_v1.0-experimental.md`](docs/protocolo_llm_v1.0-experimental.md) | Protocolo da camada de linguagem v1.0-experimental |
| [`docs/llm_v1_exp_fase1.md`](docs/llm_v1_exp_fase1.md) | Fase 1 da avaliação da v1.0-experimental: conjunto, template e rodada |
| [`docs/llm_7b_implementacao.md`](docs/llm_7b_implementacao.md) | Implementação da explicação assistida v0.6 |
| [`docs/relatorio_validacao_7a.md`](docs/relatorio_validacao_7a.md) | Avaliação experimental da explicação assistida v0.6 |
| [`docs/pibiti/decisoes_orientador.md`](docs/pibiti/decisoes_orientador.md) | Registro das decisões do orientador |
| [`docs/checklist_pendencias.md`](docs/checklist_pendencias.md) | Pendências e situação de cada frente de trabalho |
| [`docs/verificacao_publicacao.md`](docs/verificacao_publicacao.md) | Conferência da versão publicada, com commits e evidências |
| [`docs/demonstracao.md`](docs/demonstracao.md) | Estratégia de demonstração e modo sem internet |
| [`docs/versao_congelada.md`](docs/versao_congelada.md) | Procedimento de congelamento da versão de avaliação |
| [`docs/validacao_academica.md`](docs/validacao_academica.md) | Cenários de validação e evidências |
| [`docs/README.md`](docs/README.md) | Índice das fases e etapas de desenvolvimento |
| [`TESTES.md`](TESTES.md) | Registro da estratégia de testes |

---

## Como contribuir

1. Crie uma branch para cada funcionalidade ou correção.
2. Mantenha cálculos e regras de negócio em `core/`; as páginas em `app/` devem apenas exibir resultados.
3. Adicione ou atualize testes para toda alteração em cálculos, tratamento de dados ou regras críticas; o `core/` deve continuar com 100% de cobertura.
4. Documente em `docs/` qualquer decisão metodológica que altere métricas, indicadores ou textos educativos.
5. Não altere arquivos protegidos por hash (protocolos de LLM, conjunto de casos e template congelados) sem nova ratificação registrada.
6. Ao acrescentar um evento histórico, informe a fonte e o endereço.
7. Execute `python -m pytest` e confira a interface localmente antes de enviar.
8. Nunca envie chaves de API, arquivos `.env`, ambientes virtuais, bancos locais ou relatórios temporários.

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
- Os resultados podem variar entre execuções, e o padrão histórico não garante repetição.
- A plataforma não oferece recomendação de compra, venda ou manutenção de ativos.
- Eventos históricos são contexto: a plataforma não afirma que um evento causou a variação de um ativo.
- Nenhuma informação exibida substitui análise profissional, avaliação de perfil de risco ou orientação de especialista habilitado.
- A disponibilidade e a precisão dos dados dependem de fontes externas.

> [!WARNING]
> O Argos **não deve ser utilizado como ferramenta de recomendação de investimentos**.

---

## Licença

Projeto desenvolvido para fins educacionais e de pesquisa no âmbito do PIBITI UFPI. **Todos os direitos reservados.** As marcas e logotipos da UFPI e do CEAD pertencem às respectivas instituições e são usados apenas para identificar o vínculo acadêmico.
