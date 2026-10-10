# Validação Acadêmica — Argos DataLab

**Status:** rascunho para revisão do orientador · **Atualizado em:** 10/10/2026 (Plano 2)
**Decisão registrada:** pergunta de pesquisa **A** escolhida em 07/10/2026.

Este documento traduz a pergunta de pesquisa em objetivos, hipóteses, critérios verificáveis e um protocolo de validação, e indica o que já está feito no projeto e o que falta. Ele cumpre a seção 14 da ata de 06/10/2026. Os cálculos estão em `docs/metodologia_de_calculo.md`; as fontes e o tratamento de dados, em `docs/fontes_e_tratamento_de_dados.md`; a arquitetura, em `docs/arquitetura.md`.

> **Ponto de atenção.** Com a escolha da pergunta A, o eixo da validação passa a ser a **interpretação por pessoas sem formação em finanças** e o **rigor dos cálculos**, e não a **capacidade preditiva**. O que a ata chama de modelos de previsão, benchmarks e validação temporal fora da amostra continua registrado, mas passa a ser **trabalho futuro** (seção 8). O orientador deve confirmar essa leitura.

---

## 1. Pergunta de pesquisa

> **Em que medida indicadores técnicos clássicos (tendência, momentum, volatilidade e volume), calculados sobre dados históricos de múltiplas classes de ativos, podem ser organizados em uma ferramenta de apoio à interpretação de dados financeiros que seja compreensível para usuários sem formação em finanças, preservando rigor metodológico e sem configurar recomendação de investimento?**

### 1.1 Componentes e como cada um será verificado

A pergunta reúne cinco conceitos. Para poder respondê-la, cada um precisa de uma definição operacional.

| Conceito | Definição operacional proposta | Como verificar | Situação |
| --- | --- | --- | --- |
| Indicadores técnicos clássicos | SMA, EMA, Bollinger, RSI, MACD, ATR, volatilidade móvel e volume, com fórmulas, parâmetros e limitações documentados | Revisão de `core/indicator_docs.py` e dos testes de cada indicador | Implementado e testado |
| Múltiplas classes de ativos | 120 ativos em 13 grupos do catálogo | `docs/catalogo-de-ativos.md`, `validate_catalog` | Implementado |
| Apoio à interpretação | Cada métrica tem definição em linguagem simples, unidade, leitura (descritiva) e limitação | Auditoria de conteúdo (seção 5.2) | Implementado; falta auditoria formal |
| Compreensível para usuários sem formação em finanças | Pessoas sem formação em finanças, economia, contabilidade ou áreas afins interpretam corretamente as métricas e os gráficos | Avaliação com usuários (seção 5.3) | **Não realizada** |
| Rigor metodológico | Fórmulas documentadas, cálculos testados, ausência de informação futura, parâmetros e limitações visíveis, resultados reproduzíveis | Lista de critérios (seção 5.1) | Em grande parte atendido |
| Sem recomendação de investimento | Nenhum texto indica compra, venda ou adequação ao perfil; avisos visíveis | Teste automático de linguagem e auditoria (seção 5.4) | Implementado; falta auditoria formal |

### 1.2 Objetivo geral

Desenvolver e avaliar uma ferramenta de apoio à interpretação de dados históricos do mercado financeiro que organize indicadores técnicos clássicos de forma compreensível para pessoas sem formação em finanças, com rigor metodológico e sem configurar recomendação de investimento.

### 1.3 Objetivos específicos

| # | Objetivo | Evidência no projeto |
| --- | --- | --- |
| O1 | Selecionar e documentar um conjunto inicial de indicadores, com fórmula, parâmetros e limitações | `core/indicator_docs.py`, `docs/metodologia_de_calculo.md`, seção 3 |
| O2 | Implementar os cálculos de forma reprodutível e verificada, sem informação futura | `core/`, 487 testes, 100% de cobertura de `core/` |
| O3 | Construir uma camada educativa (explicações, glossário, avisos, roteiro "Como ler este gráfico") para usuários leigos | `app/ui/education.py`, `app/ui/indicator_docs.py`, `app/ui/chart_guide.py`, `core/glossary.py`, `core/chart_guides.py` |
| O4 | Garantir linguagem neutra e separação entre informação histórica, interpretação estatística, simulação e recomendação | `core/disclaimers.py`, testes de linguagem, avisos nas páginas |
| O5 | Documentar fontes, tratamento de dados e limitações | `docs/fontes_e_tratamento_de_dados.md` |
| O6 | **Avaliar a compreensão da ferramenta por usuários sem formação em finanças** | **A fazer** (seção 5.3) |

O objetivo O6 é o que falta para responder ao "em que medida" da pergunta.

---

## 2. Hipóteses

Hipóteses de trabalho, a serem refinadas com o orientador. Cada uma é verificável.

| # | Hipótese | Tipo de evidência |
| --- | --- | --- |
| H1 | Usuários sem formação em finanças interpretam corretamente mais métricas e gráficos com a camada educativa do que sem ela | Questionário de interpretação (seção 5.3) |
| H2 | Os cálculos do Argos reproduzem valores de referência obtidos de forma independente (cálculo manual, planilha ou outra biblioteca) dentro de tolerância numérica definida | Testes de referência (seção 5.1) |
| H3 | Nenhum texto exibível ao usuário contém linguagem de recomendação, e os usuários não percebem a ferramenta como recomendação de compra ou venda | Teste automático + item do questionário |
| H4 | Os indicadores mais fáceis de interpretar são os que descrevem o passado de forma direta (retorno, drawdown), e os mais difíceis são os que dependem de parâmetros (RSI, MACD, Bollinger) | Erros por item do questionário |

Hipótese nula de referência para H1: a camada educativa não altera a proporção de acertos. Resultados negativos ou inconclusivos serão registrados (seção 6).

---

## 3. Revisão teórica sobre análise técnica (pendência 1)

**Entregável:** capítulo de 8 a 15 páginas com referências.

### 3.1 Estrutura sugerida

1. **Análise técnica: conceitos e fundamentos.** Origem, premissas (preço incorpora informação; padrões se repetem), categorias de indicadores (tendência, momentum, volatilidade, volume).
2. **Indicadores adotados no Argos.** Para cada um: origem, fórmula, parâmetros convencionais, uso descritivo e limitações. Base: `docs/metodologia_de_calculo.md`, seção 3.
3. **Evidências sobre o valor da análise técnica.** Hipótese dos mercados eficientes e estudos empíricos favoráveis e desfavoráveis, com os cuidados de teste (viés de seleção de parâmetros, custos, amostra).
4. **Medidas de risco e retorno.** Retorno, volatilidade, drawdown, Sharpe e suas limitações.
5. **Educação financeira e compreensão de dados.** Letramento financeiro, comunicação de risco, letramento em visualização de dados.
6. **Regulação e posicionamento.** Diferença entre educação financeira e recomendação/adequação ao perfil do investidor (tema levantado na ata).
7. **Lacuna e posicionamento do Argos.** O que a literatura não resolve e onde o Argos se encaixa.

### 3.2 Relação entre indicadores e métodos de análise de dados

| Indicador | Natureza estatística | Método de análise de dados relacionado |
| --- | --- | --- |
| SMA | Média móvel (filtro passa-baixa) | Suavização de séries temporais |
| EMA | Média ponderada com decaimento exponencial | Suavização exponencial |
| Bollinger | Média e desvio-padrão móveis | Intervalos de dispersão, controle estatístico de processos |
| RSI | Razão entre médias de ganhos e perdas | Razão de médias suavizadas, normalização para [0, 100] |
| MACD | Diferença de duas médias exponenciais | Filtro de tendência de dois sinais |
| ATR | Média suavizada da amplitude verdadeira | Estimador de dispersão com lacunas |
| Volatilidade móvel | Desvio-padrão móvel de retornos | Estimação de volatilidade histórica |

Essa relação é o ponto de ligação entre a análise técnica e o curso de Tecnologia em Gestão de Dados.

### 3.3 Plano de busca

- **Bases:** Google Acadêmico, Portal de Periódicos CAPES, SciELO, Scopus ou Web of Science (conforme acesso institucional da UFPI).
- **Termos (português e inglês):** "análise técnica" / "technical analysis"; "indicadores técnicos" / "technical indicators"; "educação financeira" / "financial literacy"; "letramento em visualização" / "visualization literacy"; "ferramenta de apoio à decisão" / "decision support"; "comunicação de risco" / "risk communication".
- **Critérios de inclusão:** pesquisa revisada por pares ou obra de referência; relação direta com um dos sete tópicos da seção 3.1; texto acessível. **Exclusão:** material comercial sem método, sem autoria identificável ou sem acesso ao texto.
- **Registro:** cada trabalho vira uma linha da matriz de literatura (seção 3.4).

### 3.4 Matriz de literatura (pendência 3)

Meta: 20 a 30 trabalhos. Colunas sugeridas:

| Coluna | Conteúdo |
| --- | --- |
| ID | Número sequencial |
| Referência | Autor, ano, título, veículo |
| Tópico | Um dos sete tópicos da seção 3.1 |
| Pergunta ou objetivo | O que o trabalho investiga |
| Método e dados | Delineamento, amostra, ativos e período |
| Principais resultados | Em uma ou duas frases |
| Limitações | Declaradas ou observadas |
| Relevância para o Argos | Alta, média ou baixa, com justificativa |
| Como será usado | Fundamentação, comparação, método ou contraponto |

### 3.5 Pontos de partida para a busca

> **Atenção.** Esta lista é um **ponto de partida de busca**, escrita sem acesso às bases. Os dados bibliográficos (ano, veículo, título exato) precisam ser **conferidos na fonte antes de citar**. Ela não substitui a revisão.

| Tópico | Obra ou autor | Para que serve |
| --- | --- | --- |
| Análise técnica | Murphy, J. J. *Technical Analysis of the Financial Markets* | Referência geral sobre indicadores |
| Análise técnica | Wilder, J. W. *New Concepts in Technical Trading Systems* | Origem de RSI e ATR (suavização de Wilder) |
| Análise técnica | Bollinger, J. *Bollinger on Bollinger Bands* | Origem e uso das bandas |
| Análise técnica | Appel, G. (MACD) | Origem do MACD |
| Evidências | Fama, E. F. "Efficient Capital Markets: A Review of Theory and Empirical Work" (1970) | Hipótese dos mercados eficientes |
| Evidências | Brock, W.; Lakonishok, J.; LeBaron, B. "Simple Technical Trading Rules and the Stochastic Properties of Stock Returns" (1992) | Teste empírico de regras técnicas |
| Evidências | Lo, A.; Mamaysky, H.; Wang, J. "Foundations of Technical Analysis" (2000) | Abordagem estatística da análise técnica |
| Evidências | Park, C.-H.; Irwin, S. "What Do We Know About the Profitability of Technical Analysis?" (2007) | Revisão de estudos |
| Risco e retorno | Sharpe, W. F. "The Sharpe Ratio" (1994) | Definição e uso do índice de Sharpe |
| Risco e retorno | Markowitz, H. "Portfolio Selection" (1952) | Fundamento de risco e retorno |
| Educação financeira | Lusardi, A.; Mitchell, O. "The Economic Importance of Financial Literacy" (2014) | Letramento financeiro |
| Educação financeira | Estratégia Nacional de Educação Financeira (ENEF) | Política pública brasileira |
| Regulação | CVM, normas e materiais sobre educação financeira e adequação ao perfil do investidor (suitability) | Distinção entre educar e recomendar |
| Visualização | Lee, S. et al. "VLAT: Development of a Visualization Literacy Assessment Test" (2017) | Instrumento de letramento em visualização |
| Usabilidade | Brooke, J. "SUS: A Quick and Dirty Usability Scale" (1996) | Escala de usabilidade |
| Usabilidade | Nielsen, J. heurísticas de usabilidade | Avaliação heurística da interface |
| Séries temporais | Hyndman, R. J.; Athanasopoulos, G. *Forecasting: Principles and Practice* | Base para o trabalho futuro de previsão |
| Finanças e ML | López de Prado, M. *Advances in Financial Machine Learning* (2018) | Cuidados de validação (trabalho futuro) |

---

## 4. Como cada pendência acadêmica muda com a pergunta A

| # | Pendência | Situação após a decisão |
| --- | --- | --- |
| 1 | Revisão teórica | **Mantida**, ampliada com educação financeira e compreensão de dados (seção 3) |
| 2 | Pergunta de pesquisa | **Decidida:** opção A |
| 3 | Matriz de literatura | **Mantida** (seção 3.4) |
| 4 | Hipóteses, variáveis-alvo e horizontes de previsão | **Reformulada:** hipóteses H1 a H4 (seção 2); variáveis-alvo e horizontes passam a trabalho futuro |
| 5 | Benchmarks e modelos simples | **Trabalho futuro** (seção 8) |
| 6 | Protocolo de validação temporal | **Reformulada:** protocolo de validação técnica, de conteúdo e com usuários (seção 5); validação temporal mantida como trabalho futuro |
| 7 | Relatório metodológico | **Mantida** (seção 7) |

---

## 5. Protocolo de validação

A validação tem quatro frentes. As três primeiras podem ser feitas sem participantes externos; a quarta depende de avaliação com usuários.

### 5.1 Validação técnica: rigor dos cálculos

| Critério | Como verificar | Situação |
| --- | --- | --- |
| Fórmulas documentadas | `docs/metodologia_de_calculo.md` | Atendido |
| Cálculos cobertos por testes | `pytest`: 487 testes, 100% de `core/` | Atendido |
| Sem informação futura | Testes que alteram dados posteriores a `t` e verificam que o valor em `t` não muda | Atendido (confirmar escopo dos testes) |
| Valores de referência independentes | Comparar saídas do Argos com cálculo manual, planilha ou biblioteca de referência para uma série fixa; registrar a tolerância | **A fazer** |
| Casos de referência do recorte por anos, janela composta e tendência | Testes com valores calculados à mão: setembro → outubro é o retorno de outubro; janela de três meses é o produto dos retornos mensais; virada de ano; mediana e % de anos positivos (N par e ímpar, retorno zero); série que dobra em 12 meses tem retorno móvel 1,0; razão de séries idênticas é 0 (`test_seasonality*.py`, `test_trend.py`) | Atendido; conferir no navegador com o Bitcoin (setembro → outubro) |
| Casos de borda | Série vazia, constante, com lacunas, com valores ≤ 0, histórico curto | Atendido (`test_*_edges.py`) |
| Parâmetros e limitações visíveis | Fator de anualização, taxa livre de risco, janelas e avisos exibidos nas páginas | Atendido |
| Reprodutibilidade | Versões das bibliotecas fixadas (`requirements`); data da coleta registrada; **CSV exportado como instantâneo dos dados usados**, já que o Yahoo Finance pode revisar séries passadas | Parcial |

**Teste de referência sugerido.** Criar uma série pequena e fixa (por exemplo, 60 fechamentos), calcular à mão ou em planilha SMA, EMA, RSI, retorno, drawdown e Sharpe e registrar os valores esperados em um teste. Qualquer diferença deve ser explicada pelas convenções (RSI de Wilder, `ddof = 1`).

### 5.2 Validação de conteúdo: textos e explicações

- **Revisão por especialista.** O orientador (ou outro profissional de finanças/estatística) revisa os textos de `core/glossary.py`, `core/indicator_docs.py` e `app/ui/education.py`, registrando correções.
- **Checklist por métrica.** Cada métrica deve ter: definição em linguagem simples, unidade, leitura descritiva (o que valores maiores ou menores indicam, sem juízo de valor), limitação e aviso de que nenhuma métrica deve ser interpretada isoladamente.
- **Convenções a aprovar:** RSI de Wilder, Bollinger com `ddof = 1`, RSI plano = vazio, √252 na anualização diária, taxa livre de risco informada pelo usuário.

### 5.3 Avaliação com usuários: compreensão (objetivo O6, hipótese H1)

**Delineamento proposto (exploratório).**

- **Participantes:** pessoas sem formação em finanças, economia, contabilidade ou áreas afins (critério de inclusão: **adultos, 18 anos ou mais** [N14]; sem menores). Amostra pequena (por exemplo, 8 a 20 pessoas), adequada a estudo exploratório.
- **Condições:** versão **com** a camada educativa × versão **sem** (textos explicativos, "O que significa?" e glossário ocultos). Distribuição entre grupos ou medidas repetidas, a definir.
- **Tarefas:** após breve contexto, o participante usa as páginas Análise Individual, Risco e Retorno e Indicadores Técnicos com um ativo definido e responde a questões de interpretação.
- **Instrumentos:**
  1. **Questionário de interpretação** (cerca de 10 questões de múltipla escolha, com gabarito), cobrindo retorno total × retorno do período, volatilidade, drawdown, Sharpe, leitura do mapa de calor, RSI e Bollinger, e a diferença entre "histórico" e "previsão".
  2. **Item de neutralidade:** "A ferramenta está me dizendo que devo comprar ou vender?", com resposta esperada "não".
  3. **Escala de usabilidade (SUS)** e itens de clareza em escala Likert.
  4. **Comentário aberto** sobre o que não ficou claro.
- **Medidas:** proporção de acertos por item e total, tempo, avaliação de clareza e usabilidade, comentários.
- **Análise:** descritiva, com gráficos por item; testes não paramétricos com a ressalva de amostra pequena. Sem afirmar generalização.
- **Aspectos éticos [N14, N14b]:** pesquisa com participantes humanos, **somente adultos (18 anos ou mais)**, com termo de consentimento livre e esclarecido (TCLE). O CEP exige **parecer favorável antes do início da coleta**; o TCLE não substitui a apreciação ética. Nenhum dado de participante é coletado antes do parecer. Não coletar dados pessoais além do necessário. Protocolo e cronograma no Bloco 9 do Plano 2 (`docs/plano_de_ajustes_2.md`).

> Se o orientador preferir uma avaliação sem participantes nesta etapa, a alternativa é uma **avaliação heurística** por especialistas (heurísticas de Nielsen) e uma **revisão de conteúdo** (seção 5.2), registrando que a compreensão por leigos ainda não foi medida. O texto do relatório deve, nesse caso, reduzir a pergunta de "em que medida é compreensível" para "como a ferramenta foi projetada para ser compreensível".

### 5.4 Auditoria de neutralidade (sem recomendação)

- **Automática:** `core/disclaimers.py` mantém a lista de expressões proibidas e os testes verificam os textos exibíveis (indicadores, glossário, avisos).
- **Manual:** varredura das páginas em busca de frases como "compre", "venda", "ponto de entrada", "barato", "caro", "oportunidade". Registrar o resultado.
- **Separação visível** entre informação histórica, interpretação estatística, simulação educacional e recomendação (esta última inexistente).
- **Avisos:** a ferramenta não avalia renda, dívidas, objetivos nem tolerância individual a risco.

---

### 5.5 Camada de interpretação assistida (LLM) como componente de apoio

Decisão do orientador (N09): a explicação assistida entra no relatório da pergunta A como **componente de apoio à interpretação e à educação financeira**, **não como núcleo metodológico**. Seu papel é explicar gráficos, filtros e métricas **já calculados** pelo `core/`; ela não calcula, não recomenda e não prevê.

- **Condição de entrada.** A integração com a API (7B) só acontece se a validação de prompts (7A) cumprir **todos** os limiares e o orientador aprovar. A 7A é um experimento fora do aplicativo: no mínimo 12 casos, 2 modelos, 3 repetições, 3 avaliadores humanos independentes (leigo, técnico, neutralidade) com sessão de calibração e kappa ponderado ≥ 0,60. Limiares, rubrica e custos: `docs/llm_7b_especificacao.md`.
- **Protocolo de prompts na frente 4 (neutralidade).** Os prompts de sistema e de usuário, as respostas do experimento e as notas dos avaliadores alimentam a auditoria de neutralidade (seção 5.4). Toda saída é verificada contra a lista de expressões proibidas e contra os padrões a vigiar antes de ser exibida; se falhar, aparece o texto fixo de reserva.
- **Texto fixo de reserva.** Cada gráfico tem roteiro próprio em `core/chart_guides.py`, de modo que a ferramenta continua educativa sem o modelo.
- **Comparação para a pergunta A.** A hipótese H1 compara "com × sem camada educativa". A explicação assistida só entra nessa comparação se a 7B existir; caso contrário, a camada educativa avaliada é a de textos fixos.
- **Versão pública.** Sem explicação assistida (`LLM_ENABLED=false`), com texto fixo no lugar.

---

## 6. Limitações e resultados negativos

Para não afirmar mais do que os dados permitem, o relatório deve incluir:

- **Limitações dos dados:** fonte não oficial (Yahoo Finance), histórico variável, retorno de preço sem dividendos, revisões de séries, ausência de câmbio e inflação (`docs/fontes_e_tratamento_de_dados.md`, seção 8).
- **Limitações das métricas:** dependência de período, frequência, janelas e parâmetros; convenção única de anualização para todas as classes.
- **Limitações da avaliação:** amostra pequena e não probabilística, participantes voluntários, possível efeito de conveniência, ausência de acompanhamento ao longo do tempo.
- **Escopo:** o catálogo é amostra inicial, não o universo do mercado; não há previsão.
- **Resultados negativos ou inconclusivos:** se a camada educativa não melhorar a compreensão, ou se alguma métrica continuar sendo mal interpretada, isso será relatado como achado e levará a revisão dos textos, não será omitido.
- **Regra geral:** nenhum resultado histórico será apresentado como previsão, e nenhum resultado estatístico como utilidade econômica.

---

## 7. Relatório metodológico para o orientador (pendência 7)

Critério de aceite da ata: o orientador consegue reproduzir uma análise básica sem ajuda técnica.

| Capítulo | Conteúdo | Origem |
| --- | --- | --- |
| 1. Introdução | Contexto, justificativa, posicionamento (pesquisa e educação, não recomendação) | Ata de 06/10/2026 |
| 2. Pergunta, objetivos e hipóteses | Seções 1 e 2 deste documento | Este documento |
| 3. Revisão teórica | Seção 3 | A produzir |
| 4. Materiais e métodos | Arquitetura, dados, tratamento, indicadores, risco, simulação | `docs/arquitetura.md`, `docs/fontes_e_tratamento_de_dados.md`, `docs/metodologia_de_calculo.md` |
| 5. Validação | Protocolo da seção 5 e resultados obtidos | A produzir |
| 6. Roteiro de reprodução | Passo a passo: instalar, abrir, escolher um ativo, gerar análise, exportar CSV, conferir um valor | A produzir |
| 7. Limitações e resultados negativos | Seção 6 | Este documento |
| 8. Trabalho futuro | Seção 8 | Este documento |
| 9. Declaração | Resultados históricos não são previsões; a ferramenta não é consultoria de investimentos | Já presente nas páginas |
| Anexos | Catálogo de ativos, glossário, instrumento de avaliação, checklist de testes | `docs/`, `tests/` |

---

## 8. Trabalho futuro: previsão e validação temporal

Registrado para não se perder, mas **fora do escopo da pergunta A**. Só será tratado se o orientador reabrir o escopo (por exemplo, incorporando a opção C como objetivo específico).

**Princípios já definidos pela ata:** começar por benchmarks e modelos simples (regressão, classificação, ARIMA, Random Forest) antes de redes neurais; validação temporal com treino, validação e teste; avaliação fora da amostra; não interpretar acurácia como rentabilidade; não afirmar superioridade de modelos sem comparação adequada.

**Protocolo mínimo, se for retomado:**

1. **Alvo e horizonte** definidos antes de olhar os resultados (retorno, direção ou volatilidade; dia, semana ou mês).
2. **Variáveis (features)** construídas somente com dados até `t`, em `core/features.py`, com defasagens.
3. **Divisão temporal** sem embaralhar: treino → validação → teste em ordem cronológica, com validação em janela expansível (walk-forward) e intervalo de segurança entre treino e teste quando o alvo usar horizonte à frente.
4. **Benchmarks obrigatórios:** repetir o último valor, média histórica e modelo autorregressivo simples.
5. **Métricas:** erro (RMSE ou MAE) para retorno e volatilidade; acurácia balanceada e comparação com a classe majoritária para direção. Medir a utilidade econômica separadamente, se for o caso, com custos.
6. **Cuidados:** não ajustar parâmetros no conjunto de teste; registrar todas as tentativas, para evitar viés de seleção; repetir em vários ativos e períodos.
7. **Relato:** incluir resultados negativos.

---

## 9. Próximos passos

1. O orientador revisa este documento e confirma: (a) o texto da pergunta A; (b) que previsão e validação temporal ficam como trabalho futuro; (c) o formato da avaliação com usuários (ou a alternativa por especialistas); (d) o protocolo do CEP (Bloco 9); a necessidade de parecer favorável antes da coleta, de TCLE e de participantes adultos já está decidida (N14, N14b).
2. Iniciar a busca bibliográfica e preencher a matriz de literatura (meta: 20 a 30 trabalhos).
3. Implementar os testes de valores de referência (seção 5.1).
4. Preparar o questionário de interpretação e o roteiro da avaliação (seção 5.3).
5. Montar o relatório metodológico (seção 7) à medida que cada parte for concluída.