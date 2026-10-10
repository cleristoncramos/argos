# Plano de Ajustes 2 — Argos DataLab

**Elaborado em:** 09/10/2026 · **Atualizado em:** 09/10/2026 (terceira rodada de respostas) · **Situação:** pronto para execução; a passagem à API (Bloco 7B) depende dos resultados da 7A · **Base:** `docs/ata_reuniao_2026-10-07.md`, `docs/checklist_pendencias.md` e `docs/llm_7b_especificacao.md`

**O que este plano cobre:** as melhorias funcionais decididas na reunião de 07/10/2026, na ordem em que devem ser feitas. **O que ele não cobre:** Fase 10 (nome e identidade visual), home, "Get Started", vídeo de abertura e a definição de autoria de trabalhos colaborativos. Esses itens formam o **Plano 3**.

Convenções: **[D]** decisão tomada · **[S]** sugestão deste plano, ainda sem aceite · **[?]** depende de resposta (seção 7).

---

## 1. Princípios que valem para todos os blocos

1. **Cálculo em `core/`, tela em `app/`.** `core/` não importa `app/`. Toda regra nova nasce em `core/`, com teste, antes de aparecer na página.
2. **Teste antes da tela.** Cada função nova tem teste com valor calculado à mão. `core/` permanece com 100% de cobertura.
3. **Consulta confirmada.** Filtros novos só recalculam ao clicar em "Aplicar", como nas demais páginas.
4. **Linguagem descritiva** [D N08]. Nada de "melhor", "pior", "compre", "invista", "vai subir". Todo texto novo passa no teste de linguagem neutra, que passa a cobrir também os textos de `app/`, não só `indicator_docs.py` [S].
5. **Todo recurso novo nasce com seu texto educativo** (o que mede, o que mostra, cuidado, o que não permite concluir) e com sua seção em `metodologia_de_calculo.md`.
6. **Unidades:** `analyzer` trabalha em percentual; `calculate_returns`, risco, comparação e simulação em decimal. Funções novas declaram a unidade na docstring e no teste.
7. **Documentação junto com o código,** não no fim.

---

## 2. Decisões incorporadas

### 2.1 Respostas de 09/10/2026 (primeira rodada)

| ID | Decisão | Efeito no plano |
| --- | --- | --- |
| N01 | **[D]** "Get Started" e vídeo ficam para depois das funcionalidades, junto com a Fase 10 | Plano 3 |
| N03 | **[D]** Sazonalidade: fechamento do mês de entrada → fechamento do mês de saída, como **janela de retorno composta** | Bloco 2 |
| N04 | **[D]** Simulação: manter apenas as janelas móveis históricas existentes | Bloco 4 só revisa |
| N07 | **[D]** Tendência: retorno móvel e razão de desempenho; sem regressão | Bloco 6 |
| N10 | **[D]** SBBD, trilha de demos | Seção 5 |

### 2.2 Respostas de 09/10/2026 (segunda rodada)

| ID | Decisão | Efeito no plano |
| --- | --- | --- |
| N02 | **[D]** O recorte por anos fica **só na Análise Individual** | Bloco 3 perde "anos selecionados comparados" (ver nota abaixo) |
| N04b | **[D]** Sim: a janela sazonal por ano atende ao exemplo "depositar em setembro e retirar em outubro" | Bloco 4 fecha sem nova modalidade |
| N05 | **[D]** Sim: exibir mediana e proporção de anos positivos por mês, além da média | Bloco 2 |
| N06 | **[D]** Não: sem tabela com mais de 5 ativos nesta rodada | Bloco 3 perde a tarefa de tabela maior |
| N08 | **[D]** Sim: linguagem descritiva em toda a interface | Princípio 4 |
| N09 | **[D]** A LLM entra no relatório da pergunta A como **componente de apoio à interpretação e à educação financeira**, não como núcleo metodológico; papel delimitado: explicar gráficos, filtros e métricas já calculados | Bloco 8.2 ajusta `validacao_academica.md` |
| N12 | **[D]** Não há defeitos de "seleção de ativos" ou "logos" | Tarefa removida do Bloco 1 |
| N13 | **[D]** Os relatórios do PIBITI registram a mudança de escopo: (1) cronograma original, (2) cronograma efetivamente executado, (3) alterações e justificativas, (4) conexão da nova etapa com o objetivo geral do plano aprovado | Bloco 8.4 |
| N14 | **[D]** A avaliação de compreensão e usabilidade (O6) será feita **só com adultos (18 anos ou mais)**, com TCLE; sem menores | Pesquisa; Bloco 8.2 |
| N15 | **[D]** Relatório Parcial até **31/03/2027**; Relatório Final e Resumo Expandido até **28/08/2027**; defesa do TCC até **31/10/2027** | Calendário (seção 5.3) |
| N16 | **[D]** O orientador apenas sugeriu um trabalho colaborativo; **nada está confirmado**. Não registrar nada sobre isso em `docs/contribuicoes.md`; tratar no próximo plano | Seção 5.2; Plano 3 |
| N17 | **[D]** Provedor OpenAI; `gpt-5-mini` como modelo principal e `gpt-5-nano` para comparação; limites de custo e uso; critérios de passagem da 7A | Bloco 7 e `docs/llm_7b_especificacao.md` |
| N18 | **[D]** Demonstração principal: **ao vivo, com dados salvos e em cache**. Reserva obrigatória: **screencast de até 5 min**. Reserva secundária: **versão online pública** da aplicação | Seção 5.1; Bloco 8 |
| LLM | **[D]** A transição da 7A para a 7B está aprovada pelo orientador **desde que** todas as condições, limites e critérios sejam cumpridos | Bloco 7: a 7B só começa depois que a 7A atingir todos os limiares |

### 2.3 Respostas de 09/10/2026 (terceira rodada)

| ID | Decisão | Efeito no plano |
| --- | --- | --- |
| N14b | **[D]** Para a avaliação O6 com adultos, o CEP exige **parecer favorável antes do início da coleta**. O TCLE é necessário, mas **não substitui** a apreciação ética | Novo **Bloco 9**; a coleta só começa depois do parecer; calendário (seção 5.3) |
| N16 | **[D]** Confirmado: trabalho colaborativo e autoria ficam para o próximo plano | Plano 3 |
| N19 | **[D]** Limites de uso em três camadas: por sessão (`st.session_state`), por navegador (cookie/localStorage) e global em contador persistente. O global não pode ficar só na memória do Streamlit | Bloco 7B; `services/llm_limits.py` |
| N20 | **[D]** Avaliação humana da 7A por **três avaliadores independentes** (leigo, técnico, neutralidade), com sessão de calibração e kappa ponderado ≥ 0,60 | 7A.6; `docs/llm_7b_especificacao.md`, seção 5 |
| N21 | **[D]** A evidência escrita das decisões do orientador fica em `docs/pibiti/decisoes_orientador.md` | Arquivo criado (modelo preenchido) |
| N22 | **[D por delegação]** Escolhi: **versão pública sem explicação assistida** (recurso desligado por configuração, com texto fixo); explicação assistida ativa só na demonstração ao vivo e no screencast | Bloco 8.6; seção 5.1 |
| N23 | **[D]** Revisão por pessoa da área de educação: **depois** (interpretado como depois do congelamento da versão da demonstração) | Seção 5.3; ver nota abaixo |
| N24 | **[D]** Streamlit Community Cloud como acesso público **complementar**, não como garantia da demonstração. Limites verificados em 10/10/2026 (valores aproximados de fev/2024: CPU 0,078 a 2 núcleos, memória 690 MB a 2,7 GB, armazenamento até 50 GB, hibernação após 12 h). Demo principal: **modo offline local com dados salvos** | Bloco 8.6 e 8.8; `docs/demonstracao.md` |

**Nota sobre N23.** Se a revisão pedagógica mudar textos depois do congelamento, a demonstração em cache e o screencast precisam ser refeitos. O plano trata a revisão como entrada de uma versão posterior (correção de textos), e não da versão congelada. Se "depois" significava apenas "decidir mais tarde", avise.

**Nota sobre N22 e N24.** São escolhas minhas, por delegação, e podem ser revistas. A versão pública sem a LLM evita custo e abuso de uma chave exposta, não exige contador global externo e deixa a avaliação dos revisores independente de limites de uso.

**Nota sobre N02.** Na reunião de 07/10 o orientador queria ver, para dois ativos, "o de 2025 e 2024 dos dois" (D12 do registro da reunião). Com N02, o recorte por anos não aparece na Comparação. A Comparação continua mostrando a sazonalidade geral (média de todos os anos) de cada ativo. Se o orientador sentir falta da comparação por anos, a lógica de `core/seasonality.py` já a comporta, e ela pode entrar no Plano 3.

**Nota sobre a aprovação da 7B.** A aprovação é **condicional**: não autoriza integrar a API antes de a 7A cumprir os limiares. O registro dessa aprovação é um dos entregáveis da 7B; convém guardar a evidência por escrito (mensagem ou ata) [S].

---

## 3. Visão geral dos blocos

| Bloco | Conteúdo | Demandas da ata | Depende de | Esforço relativo [S] |
| --- | --- | --- | --- | --- |
| 1 | Consolidação e contribuições | R01, R09 | — | P |
| 2 | Sazonalidade por anos, meses e janela de retorno | R02 | 1 | M |
| 3 | Comparação ampliada (lacunas) | R03 | 2 | P |
| 4 | Simulação histórica: revisão e texto | R04 | 1 | P |
| 5 | Educação: textos por gráfico | R06, R10 | 2, 3, 4 | M |
| 6 | Tendência: retorno móvel e razão de desempenho | R05 | 3, 5 | M |
| 7A | Validação de prompts (protocolo e experimento) | R07 | 2, 3, 5 | M |
| 7B | Camada de interpretação assistida (API) | R07 | 7A aprovada, 5 | G |
| 8 | Documentação, relatórios e congelamento de versão | — | todos | P |
| 9 | Protocolo ético e avaliação com usuários (O6) | pesquisa (N14, N14b) | 8 (versão congelada) para a coleta; o protocolo pode ser escrito antes | M, prazo externo |

P = pequeno, M = médio, G = grande. É estimativa relativa, não prazo. Os blocos 4 e 7A.1 a 7A.3 podem andar em paralelo com 2 e 3.

---

## 4. Blocos

### Bloco 1 — Consolidação e contribuições

**Objetivo:** fechar o que já foi entregue antes de acrescentar mais.

| ID | Tarefa |
| --- | --- |
| 1.1 | Executar o roteiro de conferência no navegador das 5 páginas alteradas em 07/10 e dos 4 downloads de CSV. Cenários mínimos: Análise Individual em frequência diária e mensal; Risco e Retorno com `CL=F` incluindo abril de 2020; Comparação com `CL=F` e outro ativo; Indicadores Técnicos (rótulo da moeda); Simulação de Aportes |
| 1.2 | Converter os itens `[~]` do checklist em `[x]` conforme o resultado de 1.1 |
| 1.3 | **Verificar a versão do pandas.** Em pandas < 3.0, `pct_change()` preenche lacunas por padrão (`fill_method='pad'`), o que pode transformar uma lacuna em retorno zero em `calculate_returns_table`. Se a versão for anterior, passar `fill_method=None` e acrescentar teste com lacuna [S] |
| 1.4 | Criar `docs/contribuicoes.md` **sem** registrar trabalho colaborativo com terceiros (N16): só as contribuições já existentes no Argos e a origem de ideias relevantes (ex.: a ideia da simulação atribuída ao Giovanni na reunião) |
| 1.5 | Commit das pendências de documentação: `git add core/ app/ tests/ docs/` |

**Critério de aceite:** nenhum item `[~]` das Fases 6 e 7 resta sem resultado de conferência; 1.3 resolvido com teste; `docs/contribuicoes.md` criado.

### Bloco 2 — Sazonalidade por anos, meses e janela de retorno

**Objetivo:** permitir que o usuário compare anos específicos com a média geral (caso do orientador: setembro→outubro no Bitcoin) e veja a janela de entrada e saída como retorno composto. **Onde fica:** só na Análise Individual [D N02].

**Novo módulo `core/seasonality.py`** [S] (nome provisório). Funções puras, em **percentual** (mesma unidade do `analyzer`):

| Função | Entrada | Saída |
| --- | --- | --- |
| `filter_monthly_matrix(matrix, years=None, months=None)` | matriz ano × mês (a de `create_monthly_return_matrix`), anos e meses escolhidos | submatriz; `None` significa todos |
| `seasonal_summary(matrix, years=None)` | matriz e anos do recorte | por mês: média geral, média do recorte, diferença em **pontos percentuais**, **mediana**, **proporção de anos com retorno positivo** [D N05], N geral e N do recorte |
| `window_returns(df, entry_month, exit_month, years=None)` | dados, mês de entrada e mês de saída | por ano: `P(fechamento de saída) / P(fechamento de entrada) − 1` |

**Regras:**

- **Janela [D N03]:** entrada no fechamento do mês `m1`, saída no fechamento do mês `m2`. "Setembro → outubro" é o fechamento de **setembro** até o de **outubro**, ou seja, o retorno de **outubro**. Janelas mais longas são **compostas**, `(1+r₁)(1+r₂)(1+r₃) − 1`, nunca somadas.
- **Janela que cruza a virada do ano** (entrada em novembro, saída em fevereiro): a saída pertence ao ano seguinte; o rótulo é o ano da entrada.
- **Fechamento do mês** é o último pregão do mês (mesmo critério da matriz mensal).
- **Dados ausentes:** se um dos dois fechamentos não existe, o ano fica fora da média e do N. Não há interpolação.
- **Mês em andamento:** fora da média, ou sinalizado; nunca entra como mês completo [S].
- **Média geral:** todos os anos disponíveis. A visão padrão continua sendo a geral; o recorte é escolha do usuário.
- **Diferença do ano contra a média:** em pontos percentuais.
- **N por mês** sempre exibido. A mediana e a proporção de anos positivos são calculadas sobre o mesmo N.

**Interface (Análise Individual, abaixo do mapa de calor):** bloco "Recorte por anos e meses", com seleção de anos (um ou mais), meses (opcional) e janela (mês de entrada → mês de saída, opcional), botão "Aplicar filtro". Mostra média geral × média do recorte, mediana, proporção de anos positivos, retorno por ano, diferença e N, com gráfico comparativo. Texto metodológico obrigatório [A]: *"A média histórica representa o comportamento agregado dos anos disponíveis. Um ano específico pode divergir significativamente dessa média. A sazonalidade deve ser interpretada como evidência histórica descritiva, não como padrão determinístico."*

**Testes (valores calculados à mão):**

1. Com todos os anos, a média do recorte é **igual** à média geral atual (regressão).
2. Com um subconjunto, a média de cada mês é a média manual das células da matriz.
3. N por mês igual ao número de células não vazias.
4. Janela de um mês é igual ao retorno mensal da matriz (coerência com o `analyzer`).
5. Janela de três meses é igual ao produto dos três retornos mensais menos 1.
6. Janela que cruza a virada do ano.
7. Ano com fechamento ausente é excluído do N.
8. Mês em andamento não entra na média.
9. Mediana e proporção de anos positivos conferem com cálculo manual (incluindo N par e N ímpar, e retorno exatamente zero, que não conta como positivo).
10. Linguagem neutra no texto novo.

**Critério de aceite:** testes 1 a 10 passando; texto metodológico presente; conferência no navegador com o Bitcoin, setembro→outubro [S].

### Bloco 3 — Comparação ampliada (apenas as lacunas)

**Já existe:** até 5 ativos (`MAX_COMPARED`), Base 100, retorno, volatilidade, drawdown, correlação, aviso de períodos divergentes, período comum, exclusão de preço ≤ 0. Este bloco acrescenta só o que falta, **sem recorte por anos** [D N02] e **sem tabela com mais de 5 ativos** [D N06].

| ID | Tarefa |
| --- | --- |
| 3.1 | **Sazonalidade comparada:** média por mês de cada ativo (todos os anos disponíveis) lado a lado, com N por ativo (reusa `core/seasonality.py`) |
| 3.2 | Conferir se a legenda do gráfico permite ocultar e exibir séries; se sim, avisar o usuário com uma linha de ajuda |
| 3.3 | Verificar como o `multiselect` de tickers é alimentado e se a hierarquia Classe → Subclasse → Mercado → Ativos está presente; propor ajuste se não estiver [?] |
| 3.4 | Textos de comparação em redação descritiva: "maior retorno acumulado no período analisado", "menor queda máxima observada"; nenhum ranking de "melhor" |

**Testes:** sazonalidade por ativo com séries sintéticas de resultado conhecido; ativos com históricos de tamanhos diferentes (N diferente por ativo); linguagem neutra.

**Critério de aceite:** comparação de 5 ativos de classes diferentes legível em tela padrão; N exibido por ativo; períodos não equivalentes sinalizados; nenhum texto de ranking prescritivo.

### Bloco 4 — Simulação histórica: revisão e ajuste de texto

**Decisões [D]:** só as janelas móveis existentes (N04); a janela sazonal por ano do Bloco 2 atende ao exemplo do orientador (N04b).

| ID | Tarefa |
| --- | --- |
| 4.1 | Conferir que o texto obrigatório está na página, palavra por palavra: *"Esta é uma simulação histórica hipotética. Ela mostra como um valor teria evoluído no período selecionado, sem representar previsão, recomendação ou garantia de resultado futuro."* |
| 4.2 | Conferir a redação "teria ocorrido" e a ausência de "vai ocorrer", "previsão", "quanto investir" |
| 4.3 | **Renomear "pior, mediana e melhor janela"** para rótulos descritivos ("menor retorno histórico", "mediana", "maior retorno histórico") [S]. "Melhor/pior" é o tipo de termo que a regra de neutralidade evita |
| 4.4 | Garantir que a página informa: preço de fechamento sem dividendos, custos e impostos não incluídos, moeda do ativo |
| 4.5 | Confirmar que ativos de taxa de juros (`^IRX`, `^FVX`, `^TNX`, `^TYX`) continuam fora |
| 4.6 | Estender o teste de linguagem neutra à página da simulação |

**Critério de aceite:** 4.1 a 4.6 conferidos e cobertos por teste.

### Bloco 5 — Educação: textos por gráfico

**Objetivo:** todo gráfico tem um texto curto e fixo. Esses textos também são o **conteúdo de reserva** (fallback) da camada de LLM.

| ID | Tarefa |
| --- | --- |
| 5.1 | Inventário: lista de todos os gráficos e blocos analíticos de cada página, com o texto explicativo existente |
| 5.2 | Para cada gráfico sem texto, escrever o roteiro padrão: **o que mede · o que mostra · principal cuidado · o que não permite concluir** |
| 5.3 | Textos dos recursos novos (Blocos 2, 3 e 6), escritos junto com cada um |
| 5.4 | Conferir a cobertura dos 10 termos da lista de [A] no glossário: retorno, volatilidade, Sharpe, drawdown, correlação, sazonalidade, RSI, MACD, médias móveis, Base 100 |
| 5.5 | Botão discreto "Como ler este gráfico" por gráfico, abrindo o texto fixo (a caixa "O que significa?" já cumpre parte disso) |
| 5.6 | Revisão dos textos por pessoa da área de educação, quando a ferramenta estiver pronta (registrar quem, quando, o que mudou) [?] |
| 5.7 | Teste de linguagem neutra cobrindo **todos** os textos de `app/ui/` |

**Critério de aceite:** nenhum gráfico sem texto; 10 termos no glossário; teste 5.7 passando.

### Bloco 6 — Tendência: retorno móvel e razão de desempenho

**Decisão [D N07]:** só estes dois. Sem regressão de tendência e sem detecção automática de cruzamentos.

**Novo módulo `core/trend.py`** [S], em **decimal**:

| Função | Definição |
| --- | --- |
| `rolling_return(close, window)` | `P_t / P_{t−window} − 1`, sobre fechamentos mensais; janelas de 3, 6 e 12 meses |
| `performance_ratio(base100_a, base100_b)` | `I_A,t / I_B,t − 1`; linha de referência em 0 |
| `rolling_return_gap(close_a, close_b, window)` | diferença de retorno móvel entre dois ativos, em pontos percentuais [S] |

**Cuidados:**

- **Janela sempre visível** no título e no texto ("retorno móvel de 12 meses").
- Rótulo **"tendência histórica"**, nunca "previsão" nem "tendência futura". O texto diz que a tendência passada pode mudar e que os dados não permitem concluir que um ativo continuará acima do outro.
- **A razão acumulada depende da data inicial**, porque todos partem de 100 na mesma data. Um cruzamento na razão (linha passando por 0) pode mudar se o período mudar. O texto avisa isso. O retorno móvel é menos sensível ao ponto de partida e acompanha a razão na mesma tela [S].
- Com mais de dois ativos, a razão é calculada **de cada ativo contra um ativo de referência escolhido pelo usuário** [S].
- Antes de haver observações suficientes para a janela, o valor é vazio, não zero.

**Testes:** retorno móvel de 12 meses de uma série que dobra em 12 meses é 1,0; razão de duas séries idênticas é 0 em todo ponto; ativos com históricos diferentes; janela maior que a série devolve vazio; linguagem neutra.

**Critério de aceite:** testes passando; janela e aviso de data inicial presentes; conferência no navegador com dois ativos.

### Bloco 7 — Camada de interpretação assistida (LLM)

Especificação completa, parâmetros, custos, limites, limiares e rubrica em **`docs/llm_7b_especificacao.md`**. Aqui ficam a estrutura e a ordem.

**Posicionamento [D]:** a LLM é uma **camada de linguagem natural sobre resultados calculados de forma determinística pelo Argos**. Não calcula métricas, não escolhe ativos nem filtros, não acessa internet, banco de dados, arquivos ou ferramentas, não recomenda, não prevê. Para a pesquisa, é um **componente de apoio à interpretação e à educação financeira**, não o núcleo metodológico [D N09].

**Configuração aprovada [D N17]:** OpenAI; `gpt-5-mini` (principal) e `gpt-5-nano` (comparação); saída em JSON Schema; máximo de 900 tokens de saída; timeout de 20 s; no máximo 2 retentativas; sem entrada livre do usuário na primeira versão; ferramentas, navegação e execução de código desabilitadas.

**Limites aprovados:** US$ 10,00 para a validação inicial; US$ 5,00 por mês em uso ou demonstração; 20 interpretações por usuário por dia; 50 por sessão; 200 globais por dia. Ao atingir qualquer limite: conteúdo educativo fixo e aviso de indisponibilidade temporária.

#### 7A — Validação de prompts (antes da API no aplicativo)

Os limiares de custo (≤ US$ 0,002 por explicação) e de tempo (≤ 8 s) **só podem ser medidos chamando a API**. Por isso a 7A inclui um **script de experimento fora do aplicativo** (por exemplo, `experiments/llm_7a/`), que usa os mesmos contextos e prompts. O que o orientador pediu ("testar prompts por fora, sem API dentro da ferramenta") continua valendo: nada da API entra no Argos antes da aprovação da 7A.

| ID | Tarefa |
| --- | --- |
| 7A.1 | Criar `docs/protocolo_prompts_llm.md` com o prompt de sistema e os prompts de usuário (análise individual, sazonalidade, comparação) como versão v0, versionados |
| 7A.2 | Implementar `core/llm_context.py` (monta o pacote de contexto a partir de resultados já calculados) e `core/llm_validation.py` (valida esquema, ticker, período, frequência, métricas citadas, valores rastreáveis, linguagem proibida, limitações). Ambos puros, sem rede, com testes. Servem à 7A e à 7B [S] |
| 7A.3 | Montar **no mínimo 12 casos**: análise individual, sazonalidade (incluindo poucos anos e mês incompleto), comparação de ativos, simulação histórica, dados insuficientes e pedidos de recomendação; mais o caso setembro→outubro e um ativo com preço ≤ 0 [S] |
| 7A.4 | Escrever a **resposta esperada** de cada caso antes de rodar |
| 7A.5 | Rodar com **pelo menos 2 modelos** (`gpt-5-mini` e `gpt-5-nano`), **3 repetições por caso** (no mínimo 72 respostas); registrar modelo, versão do prompt, tokens, custo e tempo de cada chamada |
| 7A.6 | **Avaliação humana por três avaliadores independentes** [D N20]: (1) **leigo**, sem formação em finanças: clareza, vocabulário e compreensibilidade; (2) **técnico**: completude, correção factual e aderência ao contexto; (3) **neutralidade**: linguagem prescritiva, recomendações implícitas, previsões e adequação das limitações. Antes, uma **sessão de calibração** com casos exemplares; concordância mínima por **kappa ponderado ≥ 0,60**. As verificações automáticas (formato, consistência, termos proibidos) ficam com o desenvolvedor, que **não** é o único avaliador humano das dimensões subjetivas. Regras de aprovação em `docs/llm_7b_especificacao.md`, seção 5 |
| 7A.7 | Incluir **casos negativos**, entre eles a frase falada na reunião ("seria bom investir em setembro") como saída que o validador deve rejeitar |
| 7A.8 | Escrever o **relatório de validação da 7A** (incluindo a calibração, o kappa e as decisões) e registrar a aprovação do orientador para a transição em `docs/pibiti/decisoes_orientador.md` [D N21] |

**Condição de passagem para a 7B [D N17]:** todos os limiares da tabela de `docs/llm_7b_especificacao.md` atingidos (100% em estrutura, consistência, ausência de recomendação, de previsão e de linguagem proibida, e na recusa correta; ≥ 95% em correção factual; ≥ 90% em limitações e em "o que não pode ser concluído"; ≥ 80% de estabilidade; ≤ 5% de alucinação; nota média ≥ 4,0; custo médio ≤ US$ 0,002; tempo médio ≤ 8 s). Uma única violação de recomendação, previsão ou linguagem proibida reprova o caso; ele só é reaprovado depois de ajuste do prompt, do validador ou do contexto.

#### 7B — Integração por API (somente após a condição de passagem)

**Arquitetura [S]:**

```
core/llm_context.py     → monta o pacote de contexto (puro, testado) — criado na 7A
core/llm_validation.py  → valida a resposta (puro, testado)        — criado na 7A
core/llm_prompts.py     → prompts versionados (texto, versão)
services/llm_client.py  → chama a API (timeout, retentativas, erro); fora de core/
services/llm_audit.py   → registro mínimo de auditoria
services/llm_limits.py  → contagem e limites de uso
app/ui/llm_panel.py     → botão "✨ Explicar esta análise" e bloco expansível
```

`core/` continua sem rede e sem importar `app/`. O cliente é testado com cliente falso.

**Entregáveis da 7B:** os 10 itens da especificação (contexto, prompt versionado, cliente, validador, auditoria, botão, fallback, testes, documentação de arquitetura/custo/limites/segurança, relatório da 7A com a aprovação do orientador).

**Validação antes de exibir:** 10 verificações (JSON válido; campos obrigatórios; ticker; período e frequência; métricas existentes no contexto; valores rastreáveis; sem recomendação; sem previsão determinística; sem termos proibidos; limitações e "o que não pode ser concluído" presentes). Se qualquer uma falhar, **a resposta não é exibida** e aparece: *"A explicação automática não pôde ser exibida porque não atendeu aos critérios de segurança e neutralidade do Argos DataLab."*

**Interface:** botão discreto "✨ Explicar esta análise", acionado só por ação explícita. Nunca gerar ao carregar a página. A resposta aparece em bloco expansível (resumo, filtros aplicados, o que o gráfico mostra, interpretação das métricas, limitações, o que não pode ser concluído, nota educativa). O usuário pode ver o contexto enviado [S].

**Segredos:** chave em `.streamlit/secrets.toml` (local) e no segredo do ambiente de deploy; `.streamlit/secrets.toml` no `.gitignore`; `.streamlit/secrets.toml.example` sem chave real.

**Auditoria mínima:** data e hora, tipo de análise, modelo, versão do prompt, tokens de entrada e saída, custo estimado, resultado da validação, motivo de rejeição. Sem dados pessoais, sem chave, sem prompt completo com segredos.

**Pontos técnicos a resolver antes de implementar [S]** (detalhes em `docs/llm_7b_especificacao.md`):

1. **Temperatura 0 a 0,2 pode não ser aceita.** Pelo que conheço, os modelos de raciocínio da família GPT-5 não aceitam temperatura diferente do padrão, e os tokens de raciocínio contam no limite de saída, o que pode esgotar os 900 tokens antes da resposta. **Não consegui confirmar isso na documentação oficial** (a busca devolveu só páginas de terceiros). Conferir a documentação atual da OpenAI na primeira chamada de teste e, se for o caso, omitir a temperatura, usar o menor esforço de raciocínio e ajustar o limite.
2. **Limites de uso sem login** [D N19]: (a) **por sessão**, em `st.session_state` (perde-se ao fechar ou recarregar a aba e ao reiniciar o servidor); (b) **por navegador**, com cookie ou localStorage (é contornável pelo usuário e, até onde sei, o Streamlit não oferece escrita nativa desses dados, o que exigiria componente de terceiros; tratar como camada auxiliar) [S]; (c) **global**, em contador **persistente** (arquivo ou SQLite no computador da demonstração; serviço externo se a explicação for ativada na versão pública), nunca só em memória. Configurar também o teto de gasto **no painel do provedor** como trava independente do código.
3. **Entrada livre não é permitida**, então a "recusa correta a pedido de recomendação" é testada no experimento da 7A (com perguntas injetadas no contexto de teste), não na interface.

**Testes da 7B:** contexto com valores conhecidos; validador rejeita JSON inválido, número fora do contexto, ticker/período errados, cada termo proibido e ausência de limitação obrigatória; fallback em timeout, erro de API, limite atingido e resposta inválida; contagem de limites; auditoria sem dados pessoais. Cobertura de `core/` mantida em 100%.

**Ligação com a pesquisa:** os resultados da 7A e da 7B alimentam a **auditoria de neutralidade** (frente 4 de `validacao_academica.md`).

### Bloco 8 — Documentação, relatórios e congelamento de versão

| ID | Tarefa |
| --- | --- |
| 8.1 | Atualizar `metodologia_de_calculo.md` (recorte por anos, janela composta, mediana, N por mês, retorno móvel, razão, unidades), `arquitetura.md` (novos módulos), `checkpoint_qualidade.md` e `checklist_pendencias.md` |
| 8.2 | Atualizar `validacao_academica.md`: camada educativa e LLM como **componente de apoio** (N09); O6 só com adultos e TCLE (N14); protocolo de prompts na frente 4; casos de referência do recorte por anos na frente 1 |
| 8.3 | Rodar `python -m pytest` com cobertura; registrar a contagem |
| 8.4 | **Registro de escopo para os relatórios do PIBITI** (N13): preparar o quadro com (1) cronograma original, (2) cronograma efetivamente executado, (3) alterações e justificativas, (4) conexão com o objetivo geral do plano aprovado. Primeira entrega: Relatório Parcial |
| 8.5 | Registrar **a versão do sistema** (tag no Git) e a data; é a versão usada em qualquer demonstração |
| 8.6 | Preparar a estratégia de demonstração (seção 5.1): camadas, roteiro, screencast e **versão pública no Streamlit Community Cloud em modo de demonstração**, sem chamadas ao modelo [D N22, N24] |
| 8.8 | **Modo de demonstração com dados salvos** (`ARGOS_DEMO_MODE`): requisito **obrigatório** do congelamento. Requisitos, comportamento e critério de aceite em `docs/demonstracao.md`, seção 2 [D 10/10/2026] |
| 8.7 | Registrar o que ficou fora, com motivo |

---

### Bloco 9 — Protocolo ético e avaliação com usuários (O6)

**Decisões [D]:** a avaliação O6 será só com **adultos (18 anos ou mais)**, com TCLE (N14). O CEP exige **parecer favorável antes de qualquer coleta**; o TCLE não substitui a apreciação ética (N14b).

| ID | Tarefa |
| --- | --- |
| 9.1 | Confirmar com o orientador e com a secretaria do CEP da UFPI o procedimento, os documentos exigidos e o prazo de apreciação, e quem é o pesquisador responsável [?] |
| 9.2 | Escrever o **protocolo de pesquisa** da avaliação: objetivo (O6), participantes (adultos), recrutamento, procedimento, instrumentos (questionário de interpretação, escala SUS, versões com e sem camada educativa), riscos e benefícios, tratamento e guarda dos dados, critérios de inclusão e exclusão (base: `docs/validacao_academica.md`, frente 3) |
| 9.3 | Escrever o **TCLE** e os instrumentos |
| 9.4 | Submeter ao CEP o quanto antes; **nenhuma coleta antes do parecer favorável** |
| 9.5 | Definir se a avaliação humana da 7A (três avaliadores) exige tratamento ético próprio (N25) |
| 9.6 | Aplicar a avaliação sobre a **versão congelada**; registrar versão e data |
| 9.7 | Implementar o **interruptor da condição "sem camada educativa"** (variável `ARGOS_EDU_LAYER`) e seu teste automatizado, mantendo os avisos obrigatórios nas duas condições; antes do congelamento [D 10/10/2026] |
| 9.8 | Pré-teste dos instrumentos com 2 a 3 adultos, **somente após o parecer**, descrito no protocolo [D 10/10/2026] |

**Estado (10/10/2026).** Tarefas 9.2, 9.3 e 9.5 com minutas em `docs/pibiti/cep/`: `protocolo_pesquisa.md`, `tcle_participantes.md`, `tcle_avaliadores.md`, `instrumentos.md`, `roteiro_aplicacao.md` e `checklist_submissao_cep.md` (perguntas ao orientador e ao CEP, documentos, datas-alvo). Decisões de delineamento [D, por delegação]: dois grupos independentes, 20 participantes (10 por grupo), sessão presencial individual de cerca de 60 minutos no modo demo, alocação em blocos de 4, análise exploratória (Mann-Whitney com tamanho de efeito e intervalos). Pendentes: 9.1 (confirmar procedimento com o orientador e o CEP/UFPI), revisão do orientador, documentos institucionais e a submissão (meta: **15/12/2026**).
**Critério de aceite:** protocolo e TCLE prontos e submetidos; parecer registrado em `docs/pibiti/decisoes_orientador.md` antes da coleta.

---

## 5. Publicação, demonstração e calendário

### 5.1 SBBD — informações e consequências

**Informações recebidas em 09/10/2026** (conferir na chamada oficial quando for publicada; o cronograma ainda não está definido):

| Item | Informação |
| --- | --- |
| Evento | SBBD, trilha de demos e aplicações; evento previsto para setembro/2027, Porto Alegre/RS |
| Chamada | Prevista até abril/2027 |
| Tamanho | Máximo de 6 páginas, **contando** tabelas, ilustrações, agradecimentos e referências |
| Formato | Modelo oficial da SBC (LaTeX ou Word); entrega em PDF |
| Avaliação | Não é duplo-cega: nomes, e-mails e afiliações na primeira página; agências financiadoras nos agradecimentos |
| Idioma | Português ou inglês |
| Vídeo | Link público para um screencast de **até 5 minutos**, de preferência em nota de rodapé na primeira página |
| Submissão | Somente eletrônica, pelo sistema JEMS |
| Publicação | Anais Estendidos do SBBD, na plataforma SBC Open Lib |

**Estratégia de demonstração [D N18]:**

1. **Principal:** ao vivo, com **dados salvos e em cache**, para não depender do Yahoo Finance na hora.
2. **Reserva obrigatória:** screencast de até 5 minutos.
3. **Reserva secundária:** versão online pública da aplicação.

**Consequências [S]:**

1. **Duas gravações diferentes.** O vídeo curto da home (30 a 90 s, Plano 3) e o screencast de até 5 min do artigo.
2. **Congelar a versão** (Bloco 8.5) antes de gravar o screencast e de preparar os dados em cache.
3. **Conjunto de dados salvos:** definir quais ativos e períodos, de modo que a demonstração cubra análise individual, sazonalidade, comparação, simulação e (se aprovada) a explicação assistida. Documentar a data da coleta.
4. **Versão pública** [D N22, N24]: hospedada no Streamlit Community Cloud como acesso **complementar**, em modo de demonstração, **sem chamadas ao modelo** (respostas salvas e validadas, ou o texto fixo no lugar). A explicação assistida ao vivo roda só na demonstração local e aparece no screencast. Se a LLM for ativada publicamente no futuro, será preciso contador global externo, teto no provedor e política de dados.
5. **Modo de demonstração com dados salvos** [D 10/10/2026]: requisito obrigatório do congelamento (seção 5.1.1).
5. **Enquadramento:** o SBBD é de **bancos de dados**. O artigo deve destacar coleta, catálogo, tratamento, validação de qualidade e disponibilidade, métricas reprodutíveis e a camada de interpretação auditável, além da análise financeira.
6. **Espaço:** os recursos dos Blocos 2 a 7 competem por 6 páginas. Decidir cedo o que o artigo mostra.

### 5.1.1 Modo de demonstração com dados salvos

Antes do congelamento da versão para demonstração, será implementado o modo de demonstração com dados salvos previsto em `demonstracao.md`, seção 2.

Nesse modo, a aplicação utilizará datasets locais previamente preparados, sem depender de conexão com fontes externas de dados. As análises, gráficos, filtros, indicadores, métricas e simulações previstos para a demonstração deverão funcionar integralmente nesse modo.

As explicações assistidas por modelo de linguagem utilizarão respostas previamente geradas e validadas, quando disponíveis. Caso não haja resposta salva ou a funcionalidade não esteja disponível, o sistema exibirá textos educativos fixos.

O modo de demonstração será ativado por variável de ambiente (`ARGOS_DEMO_MODE`) e impedirá chamadas externas desnecessárias. A versão congelada somente será considerada pronta após validação com a internet desativada.

**Critério de aceite:** modo implementado; todas as análises da demo rodando sem internet; nenhuma chamada externa nos fluxos principais; datasets versionados ou no pacote da demo; respostas de LLM salvas validadas; texto fixo de reserva funcionando; aviso de versão congelada na interface; teste automatizado; demonstração executada uma vez sem internet. Detalhes em `docs/demonstracao.md`, seção 2.4.

### 5.2 Autoria e contribuições

- **Nada está confirmado** sobre trabalho colaborativo com outra pessoa; o orientador apenas deu uma sugestão [D N16]. **Não se registra nada sobre isso** em `docs/contribuicoes.md` agora. O tema volta no **próximo plano**.
- `docs/contribuicoes.md` registra apenas o que já existe no Argos (papéis de implementação, análise, escrita e revisão, e a origem de ideias).
- Princípios que valem para qualquer artigo: definir autoria antes da submissão; todos os autores revisam e aprovam a versão final; evitar incluir autor sem contribuição substancial e evitar excluir quem contribuiu; definir quem responde pela integridade do código, dos dados e dos resultados.
- O trecho do documento de deliberações que atribui ao CNPq a recomendação sobre autoria **não foi verificado**. Conferir o texto oficial (CNPq, UFPI/PIBITI ou SBC) antes de citar.

### 5.3 Calendário-âncora e proposta de ordem

**Datas [D N15 e N10]:**

| Marco | Data |
| --- | --- |
| Relatório Parcial | até 31/03/2027 |
| Chamada de demos do SBBD | até abril/2027 (data exata a definir) |
| Relatório Final e Resumo Expandido | até 28/08/2027 |
| SBBD | setembro/2027 |
| Defesa do TCC | até 31/10/2027 |

**Proposta de distribuição [S]** (não conheço a sua disponibilidade semanal; ajustar):

| Período | Foco |
| --- | --- |
| Out–nov/2026 | Blocos 1 a 4; 7A.1 a 7A.3 em paralelo; **9.1 e 9.2 (protocolo para o CEP) começam já** |
| Dez/2026 | Blocos 5 e 6; experimento da 7A e avaliação humana; 9.3 e submissão ao CEP |
| Jan/2027 | 7B (se a 7A passar); **implementar e validar o modo de demonstração com dados salvos** (8.8); início do Plano 3 (Fase 10, home, vídeo curto) |
| Fev/2027 | **Congelar a versão** (somente com o modo demo validado sem internet); dados salvos; screencast; rascunho do artigo |
| Mar/2027 | Relatório Parcial (até 31/03) |
| Abr/2027 | Submissão ao SBBD |
| Mai–jul/2027 | Coleta da O6, **somente se houver parecer favorável do CEP**; análise |
| Até 28/08/2027 | Relatório Final e Resumo Expandido |
| Set/2027 | SBBD |
| Após o congelamento | Revisão pela pessoa da área de educação, em versão de correção de textos [D N23] |
| Até 31/10/2027 | Defesa do TCC |

**Atenção a três gargalos:** (a) março e abril de 2027 concentram o Relatório Parcial e a submissão ao SBBD; (b) o **parecer do CEP é prazo externo**: se a submissão atrasar, a coleta da O6 invade agosto e comprime a análise e o Relatório Final; (c) a coleta só pode ocorrer sobre a versão congelada, então qualquer alteração depois de fevereiro precisa ser pequena.

---

## 6. Plano 3 (fora deste plano)

Fase 10 (nome e identidade visual), home com frase de efeito e botão "Começar", tutorial curto, vídeo de 30 a 90 s, cards de acesso, página "Como usar", ajustes de tema e revisões visuais; **definição de autoria e do trabalho colaborativo** (N16); eventual recorte por anos na Comparação, se o orientador quiser. Depende de o Plano 2 estar estável.

---

## 7. Perguntas ainda abertas

| ID | Pergunta | Bloco |
| --- | --- | --- |
| N16 | Trabalho colaborativo e autoria: adiado, confirmado para o próximo plano | Plano 3 |
| N25 | ~~Os três avaliadores humanos da 7A exigem tratamento ético próprio?~~ **[D por delegação, 10/10/2026]** Serão incluídos no mesmo protocolo, como avaliadores especialistas, com TCLE próprio (`tcle_avaliadores.md`); o CEP confirma na apreciação | 7A, 9 |
| N26 | Quem são os três avaliadores? O avaliador técnico pode ser o próprio desenvolvedor? (recomendação: não, para evitar autoavaliação) | 7A |
| N27 | Qual é o procedimento, o prazo e o pesquisador responsável no CEP da UFPI? Perguntas prontas em `docs/pibiti/cep/checklist_submissao_cep.md` | 9 |
| N28 | Como obter o kappa ponderado se cada avaliador pontua dimensões diferentes? Proposta [S]: subconjunto de calibração (por exemplo, 20% dos casos) avaliado por **todos** em **todas** as dimensões; o kappa é calculado sobre ele, aos pares | 7A |
| N29 | A regra por resposta (100% de correção factual) e o limiar agregado (≥ 95% das métricas citadas) coexistem? Proposta [S]: vale o mais rígido na aprovação da resposta; o agregado é indicador | 7A |
| N30 | Confirmar que "depois" (N23) significa depois do congelamento da versão | 5, 8 |

## 8. Riscos

| Risco | Efeito | Mitigação |
| --- | --- | --- |
| Bloco 7B toma o tempo das funcionalidades analíticas | Atrasa 2, 3, 5 | 7B só depois da 7A aprovada e dos blocos 2 a 5 |
| LLM produz texto prescritivo ou número errado | Contradiz a ata de 06/10 | Validador com 10 verificações, texto fixo de reserva, casos negativos na 7A |
| Parâmetros da API diferentes do especificado (temperatura, tokens de raciocínio) | Respostas vazias ou erro de chamada | Teste de primeira chamada; ajustar parâmetros; registrar no relatório da 7A |
| Resposta da LLM não reprodutível | Dificulta validação e descrição no artigo | Registrar modelo, versão do prompt e parâmetros; 3 repetições por caso |
| Custo ou vazamento de chave | Gasto inesperado, segurança | Teto no provedor, limites no código, segredos fora do Git, auditoria mínima |
| 72 respostas para avaliar manualmente | Gargalo de tempo | Verificações objetivas automáticas; avaliação humana só de clareza e completude |
| Média com poucos anos interpretada como regra | Conclusão enganosa | N por mês sempre visível; mediana e proporção de anos positivos |
| Dependência do Yahoo Finance na demonstração | Falha ao vivo | Dados salvos e em cache; screencast; versão pública |
| Março–abril/2027 sobrecarregados | Atraso em relatório ou submissão | Congelar a versão em fevereiro/2027 |
| Parecer do CEP tardio (prazo externo) | A coleta da O6 não ocorre a tempo | Escrever o protocolo já em out–nov/2026; submeter em dez/2026 (Bloco 9); alternativa por especialistas (`validacao_academica.md`) se o parecer não sair |
| Avaliadores humanos da 7A sem concordância | Resultado da 7A inválido | Calibração com casos exemplares; kappa ponderado ≥ 0,60 em subconjunto comum; reavaliar após ajuste |
| Regras de aprovação divergentes (por resposta × agregado) | Dúvida sobre a passagem à 7B | Registrar a regra mais rígida como vigente (N29) |
| Seis páginas para tudo | Artigo disperso | Decidir cedo o recorte do artigo |

---

## 9. Critérios de aceite do Plano 2

1. Aplicação estável: testes verdes, `core/` com 100% de cobertura, conferência no navegador registrada.
2. Usuário compara anos específicos e a janela de entrada e saída na Análise Individual, com N, mediana e proporção de anos positivos e texto metodológico.
3. Comparação de até 5 ativos legível, com sazonalidade geral por ativo.
4. Simulação com texto obrigatório e rótulos descritivos.
5. Todo gráfico com texto educativo; glossário com os 10 termos.
6. Tendência (retorno móvel e razão) com janela visível e aviso de data inicial.
7. 7A concluída, com relatório e avaliação por três avaliadores independentes (kappa ponderado ≥ 0,60 na calibração); 7B concluída **somente** se todos os limiares da 7A foram atingidos e a aprovação do orientador está registrada em `docs/pibiti/decisoes_orientador.md`.
8. Nenhuma recomendação direta em qualquer página, coberto por teste.
9. Documentação atualizada, quadro de escopo para o Relatório Parcial pronto, versão registrada.
10. `docs/contribuicoes.md` criado, sem registro de trabalho colaborativo não confirmado.
11. Protocolo e TCLE da O6 prontos e submetidos ao CEP; nenhuma coleta antes do parecer favorável.