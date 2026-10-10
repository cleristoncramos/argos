# Registro da Reunião de 07/10/2026 — Argos DataLab

**Data da reunião:** 07/10/2026 · **Orientador:** Prof. Dr. Arlino Henrique Magalhães de Araújo · **Elaborado em:** 07/10/2026

**Finalidade deste documento:** registrar o que foi dito e deliberado, separar decisão de sugestão, confrontar com o que o Argos já tem e reunir os insumos para o **novo plano de ajustes** (Plano 2). Este documento **não é o plano**: ele alimenta o plano. A Fase 10 (nome e identidade visual) e tudo o que for visual entram no plano seguinte, conforme combinado.

**Relação com outros documentos:** complementa `docs/ata_reuniao_2026-10-06.md`, `docs/checklist_pendencias.md` e `docs/validacao_academica.md`. Nada dito em 07/10 revoga o posicionamento de 06/10; a reunião o reforça.

**Atualização de 09/10/2026:** as perguntas N01 a N24 foram respondidas em três rodadas; ver as seções 12, 13 e 14. O plano resultante está em `docs/plano_de_ajustes_2.md`. Onde este registro diz o contrário das seções 12 a 14, valem as seções 12 a 14.

---

## 0. Fontes e como ler este registro

| Código | Fonte | Natureza | Cuidados |
| --- | --- | --- | --- |
| **[A]** | Documento de deliberações | Texto estruturado e organizado por seções | Parece uma redação posterior à reunião, e não a fala. Tem seções duplicadas (3 e 10 tratam da mesma home), traz referências externas (CNPq, documentação do Streamlit, RAG) que **não aparecem na transcrição** e inclui itens sem origem na fala (ver seção 5). Contém fórmulas em formato quebrado (`𝑉 𝑓 = …`); neste registro elas foram reescritas. |
| **[B]** | Transcrição da reunião | Fala bruta, com erros de transcrição | Frases incompletas e termos trocados (lista na seção 9). O tom é de conversa: muita coisa é "ideia", não decisão. |
| **[S]** | Sugestão deste registro | Proposta minha, **não dita na reunião** | Marcada sempre com [S]. Serve para o plano, mas precisa de aceite. |

**Regra de precedência adotada:** para **prioridade e tempo** ("é para agora", "fica para depois"), vale o que o orientador disse em [B]. Para **estrutura e detalhamento**, vale [A], desde que não contradiga [B]. Onde as fontes divergem, a divergência está listada na seção 5 e vira pergunta na seção 8.

---

## 1. Síntese

1. O Argos deve ser apresentado como ferramenta de pesquisa aplicada, análise exploratória, educação financeira, apoio à interpretação e desenvolvimento tecnológico. Sobre ser pesquisa **ou** educação, o orientador disse "é os dois" [B]; a pergunta a que isso responde não aparece na transcrição, então a leitura é provável, não certa. A pergunta de pesquisa continua sendo a opção A.
2. Não deve ser apresentado como recomendador, previsor, definidor de valor a investir ou substituto de análise profissional [A]. É o mesmo posicionamento de 06/10.
3. A evolução proposta é em camadas: **consolidar → anos/períodos na sazonalidade → comparação ampliada → simulação histórica → educação → LLM experimental** [A].
4. **Home no estilo do Streamlit, "Get Started" e vídeo curto:** o orientador gostou da ideia, mas disse que "não é para agora" e "por enquanto, deixa lá" [B]. [A] classifica como prioridade média.
5. **Filtro por anos na sazonalidade** foi a demanda com maior valor de pesquisa [A: alta para pesquisa]. Nasceu de um caso concreto: setembro→outubro no Bitcoin, em que a média histórica aponta um sentido e um ano específico divergiu [B].
6. **Comparação de vários ativos:** o orientador quer ver todos os gráficos para mais de um ativo, inclusive os de sazonalidade e os de anos específicos [B]. Parte disso já existe (seção 3).
7. **Simulação histórica** ("e se eu tivesse investido X em uma data e retirado em outra?"): a ideia foi atribuída ao Giovanni na fala [B]. Há limites obrigatórios de linguagem [A].
8. **Gráficos de tendência** (o retorno está crescendo, caindo, convergindo, foi ultrapassado?): é uma ideia aberta, sem método definido. O orientador disse que são "gráficos difíceis" e que "dá tempo" [B].
9. **Educação:** textos fixos agora, em linguagem simples. **LLM:** só testar prompts em ferramentas externas, **sem API e sem integração** por enquanto [A+B].
10. **Publicação:** o orientador pretende **sugerir** dois trabalhos/demos com a colega, "se ela quiser" [B]. A divisão de autoria precisa ser formalizada antes de começar [A].

---

## 2. Registro de decisões e sugestões

Legenda de força: **Decidido** (afirmado como direção) · **Sugerido** (proposta do orientador, sujeita a teste/aceite) · **Ideia** (explorar depois) · **Condicional** (depende de terceiros).

| ID | Item | Força | Fonte | Observação |
| --- | --- | --- | --- | --- |
| D01 | Posicionamento: pesquisa aplicada, análise exploratória, educação financeira, apoio à interpretação, desenvolvimento tecnológico | Decidido | A (+B "é os dois", leitura provável) | Reforça a ata de 06/10 |
| D02 | Não ser recomendador, previsão garantida, definidor de valor a investir ou substituto de análise profissional | Decidido | A | Obriga a revisar textos da interface |
| D03 | Evolução em camadas (consolidar → anos → comparação → simulação → educação → LLM) | Decidido | A (síntese) | Ordem de [A]; a fala segue ordem diferente (seção 5) |
| D04 | Home inspirada na do Streamlit (nome, frase, "Get Started", vídeo, passos) | Sugerido | A+B | [B]: "não é para agora" |
| D05 | Tutorial curto (3 a 5 passos), sem tutorial longo, sem LLM no onboarding, sem muitas telas | Decidido | A+B | |
| D06 | Manter "Sobre o Projeto" como página secundária | Sugerido | A | Não aparece na fala; [B] diz apenas "ao invés de abrir no Sobre" |
| D07 | Vídeo de 30 a 90 s mostrando só a primeira interação | Sugerido | A (+B: "videozinho") | O limite de 30–90 s é de [A] |
| D08 | Simulação histórica hipotética: valor inicial, data de entrada, data de saída, ativo, valor final, retorno, gráfico | Sugerido | A+B | Ideia atribuída ao Giovanni em [B] |
| D09 | Limites da simulação: "simulação histórica", "teria ocorrido", sem previsão, sem recomendação, sem patrimônio/renda pessoal | Decidido | A | Texto obrigatório na seção R04 |
| D10 | Filtro de sazonalidade por ano(s) e meses, comparando com a média geral | Sugerido (alta para pesquisa) | A+B | Gatilho: caso setembro→outubro do Bitcoin |
| D11 | Comparação de 2 a 5 ativos no gráfico, mais ativos só em tabela | Sugerido | A (+B: "os caras gostam de ver muito") | O limite de 5 já existe no código |
| D12 | Levar para vários ativos todos os gráficos da análise individual (sazonalidade, anos específicos) | Sugerido | B (+A 7.2) | |
| D13 | Gráficos de tendência (retorno móvel, inclinação, cruzamento, diferença de desempenho) | Ideia | A+B | [A]: prioridade baixa/média. [B]: "tá longe ainda" |
| D14 | Textos fixos revisados para indicadores e gráficos | Decidido | A+B | [B]: "pode ser fixo" |
| D15 | Botão/ícone por gráfico que abre uma explicação curta ("o que este gráfico está dizendo") | Sugerido | B | Nesta fase com texto fixo; LLM só depois |
| D16 | LLM: apenas testar prompts em ferramentas externas; sem API agora | Decidido | A+B | [B]: "não precisa nem botar API dentro da tua ferramenta por enquanto" |
| D17 | Só considerar API depois de prompts estáveis, com dados estruturados, proibição de recomendar, linguagem probabilística e origem dos dados | Decidido (como condição) | A | RAG citado em [A]; em [B] aparece como "reg" |
| D18 | Revisão da parte educativa por pessoa da área de educação (pedagoga), quando a ferramenta estiver pronta | Condicional | A+B | Convite só depois da ferramenta pronta [B] |
| D19 | Possível artigo separado para evento de educação | Ideia | B | "talvez... na medida do possível" |
| D20 | Dois trabalhos/demos: (1) Argos, com o Clériston como primeiro autor; (2) trabalho da colega, com apoio técnico dele | **Condicional** | A+B | [B]: "vou sugerir para ela, se ela quiser". **Ainda não aceito pela colega** |
| D21 | Formalizar divisão, responsabilidades e autoria **antes** de começar | Decidido | A | |
| D22 | O cronograma do plano de trabalho do PIBITI é formal; durante a execução pode ser alterado | Informativo | B | O orientador chamou o cronograma de "fake, pode-se dizer", ou seja, cumpre exigência de avaliação |
| D23 | Cronograma de implementação em 7 etapas (consolidação, sazonalidade, comparação, simulação, educação, LLM, publicação) | Sugerido | A | Sem datas |
| D24 | Critérios de aceite da rodada (12 itens) | Sugerido | A | Versão verificável na seção 7 |

---

## 3. Demandas detalhadas

Cada demanda traz: o que foi pedido, **o que o Argos já tem** (conferido no que tenho em mãos; o que não pude conferir está dito), a lacuna, os cuidados metodológicos e os critérios de aceite propostos.

> **Limite da conferência:** conferi `MAX_COMPARED`, as abas e funções da página de comparação, o heatmap/gráfico sazonal da análise individual, `indicator_docs.py`, o checklist e a `arquitetura.md`. **Não** tenho em mãos `core/simulation.py` nem `views/simulacao_aportes.py`; o que digo sobre a simulação vem do checklist e da `arquitetura.md`.

### R01 — Consolidação da aplicação atual (Etapa 1)

- **Pedido [A]:** corrigir e estabilizar a análise individual; corrigir seleção de ativos; validar dados, logos e mensagens; garantir testes passando; documentar o estado atual.
- **Situação:** 393 testes passando, `core/` com 100% de cobertura, documentação técnica da Fase 9 entregue. **Pendente:** conferência no navegador das 5 páginas alteradas (itens `[~]` do checklist).
- **Lacuna:** "corrigir seleção de ativos" e "logos" **não aparecem na fala [B]**. Não sei a que defeito se referem. Precisam ser descritos (qual ativo, qual tela, o que acontece) para virar tarefa.
- **Critério de aceite [S]:** itens `[~]` do checklist convertidos em `[x]` após roteiro de conferência no navegador; lista de defeitos de seleção/logo registrada com passos para reproduzir.

### R02 — Sazonalidade por ano e por período (Etapa 2) — **alta para pesquisa**

- **Pedido:** na análise de sazonalidade, o usuário escolhe um ou mais anos (ex.: 2024 e 2025) e opcionalmente meses (ex.: setembro e outubro) e vê o mesmo gráfico da média, mas só para esse recorte, ao lado da média geral. **A visão padrão continua sendo a geral**; o recorte é uma escolha do usuário ("não apareceria direto").
- **Exibir [A]:** média geral; média do período escolhido; retorno mensal por ano; diferença entre o ano selecionado e a média; quantidade de observações; gráfico comparativo.
- **Já existe:** gráfico de barras com a média por mês e heatmap ano × mês na Análise Individual (`create_monthly_return_matrix`, `Year`/`Month` no `data_processor`). A matriz mensal já contém o retorno de cada ano e mês; **a base de dados do filtro existe**.
- **Lacuna:** não há seleção de anos/meses, média do recorte, diferença contra a média geral nem contagem de observações por mês.
- **Cuidados metodológicos:**
  - Mensagem obrigatória [A]: a média representa o comportamento agregado; um ano pode divergir; sazonalidade é evidência histórica descritiva, não padrão determinístico. Não gerar conclusões automáticas.
  - Mostrar sempre **N por mês** (quantos anos entram em cada média). Com poucos anos selecionados o N é pequeno e a média é instável.
  - A diferença entre ano e média deve ser em **pontos percentuais**, não em "%" sobre "%".
  - Meses sem dados (lacuna) ficam fora da média e do N; a documentação já diz que a célula é vazia.
  - O ano corrente tem mês incompleto. [S] Excluir o mês em andamento da média ou sinalizá-lo; hoje não verifiquei o tratamento.
  - Unidade: o `analyzer` trabalha em **percentual**, enquanto o restante trabalha em decimal. O filtro deve ficar no lado do `analyzer` e nos mesmos termos, para não misturar escalas.
  - [S] Definir se "média geral" inclui os anos selecionados (padrão: sim, é a média de todos os anos disponíveis) e oferecer, se aceito, "média dos demais anos".
  - [S] Considerar exibir também a **mediana** e a **proporção de anos com retorno positivo** naquele mês. A média é sensível a valores extremos (criptoativos) e o exemplo do Bitcoin trata exatamente de quantos anos confirmaram o padrão. Não foi pedido na reunião.
- **Ambiguidade a resolver (pergunta N03):** "depositar em setembro e retirar em outubro" é o retorno do **mês de outubro** (fechamento de setembro → fechamento de outubro) ou a soma de **setembro e outubro**? Os dois são legítimos e dão números diferentes.
- **Critérios de aceite [S]:**
  1. Com todos os anos selecionados, a média do recorte é **igual** à média geral atual (teste de regressão).
  2. Com um subconjunto, a média de cada mês é igual à média manual das células da matriz mensal para aqueles anos (teste com valores calculados à mão).
  3. N por mês exibido e consistente com as células não vazias.
  4. Texto metodológico presente e sem linguagem prescritiva (teste de linguagem neutra).
  5. Anos sem dados no ativo não aparecem como opção, ou aparecem desabilitados.
- **Onde fica a interface (decisão aberta, [A] pede avaliar):** na Análise Individual (recorte de um ativo) ou em página própria. Como a comparação também precisa do recorte (R03), [S] construir a lógica em `core/` independente da página.

### R03 — Comparação ampliada de ativos (Etapa 3) — **alta**

- **Pedido:** comparar 2 a 5 ativos; seleção hierárquica; Base 100; retorno, volatilidade, drawdown, sazonalidade, anos selecionados, matriz de correlação; evitar poluição visual; permitir remover ativos; avisar quando os períodos históricos não são equivalentes; mais de 5 apenas em tabela; ocultar/exibir séries.
- **Já existe:** `MAX_COMPARED = 5` com `max_selections`; Base 100; retorno, risco (volatilidade, drawdown); matriz e heatmap de correlação; abas Desempenho/Risco/Correlação/Dados; aviso de períodos divergentes (`comparison_checks`); opção de período comum; exclusão com aviso de ativos com preço ≤ 0.
- **Lacunas:**
  - sazonalidade comparada entre ativos (média por mês de cada ativo lado a lado) e **anos selecionados comparados** (depende de R02);
  - ocultar/exibir séries no gráfico (o Plotly já permite clicar na legenda; conferir se está habilitado e se o usuário sabe disso);
  - tabela com mais de 5 ativos (decisão aberta, pergunta N06);
  - seleção hierárquica por ativo **dentro** da comparação (Classe → Subclasse → Mercado → Ativos, como em [A] 7.3). Hoje a seleção é um `multiselect` de tickers; não conferi como ele é alimentado.
- **Cuidados:**
  - A pergunta-guia do orientador é "qual ativo teve melhor comportamento histórico?". Na interface, evitar ranking de "melhor/pior". [S] Usar redação descritiva ("maior retorno acumulado no período", "menor queda máxima"), sempre com período e frequência.
  - Em [B] aparecem formulações como "historicamente, do próximo mês, é melhor de investir" e "vou apostar nele". São o modelo mental do usuário, **não texto de interface**. Ver D02 e a seção 5.
  - Ativos em moedas diferentes: sem câmbio incorporado (já documentado).
  - Muitas linhas poluem o gráfico: o limite de 5 é de legibilidade, não de cálculo.
- **Critérios de aceite [S]:** comparação de 5 ativos legível em tela padrão; sazonalidade comparada com N exibido por ativo; períodos não equivalentes sempre sinalizados; nenhum texto de ranking prescritivo.

### R04 — Simulação histórica (Etapa 4) — **média**

- **Pedido:** "Se eu tivesse investido determinado valor em uma data e retirado em outra, o que teria acontecido historicamente?" Entradas: valor inicial hipotético, data de entrada, data de saída, ativo. Saídas: valor final, retorno percentual, gráfico da evolução; custos opcionais, se implementados.
- **Fórmula [A]:** **V_f = V_0 × (P_f / P_0)**, onde V_0 é o valor inicial hipotético, P_0 o preço na entrada e P_f o preço na saída. O retorno é (P_f / P_0) − 1.
- **Já existe (segundo checklist e `arquitetura.md`):** página `simulacao_aportes.py` e `core/simulation.py`, com aporte único × periódico e janelas móveis (pior, mediana e melhor janela histórica), disclaimer e a regra de nunca declarar ativo "barato" ou "caro". Taxas de juros (`^IRX`, `^FVX`, `^TNX`, `^TYX`) ficam fora da simulação.
- **Lacuna a verificar (pergunta N04):** a simulação atual trabalha com **janelas móveis**, não necessariamente com **data de entrada e data de saída escolhidas pelo usuário** para um ativo. A demanda da reunião é a segunda. Se o código já aceita datas livres, a lacuna é só de texto e de gráfico; se não aceita, é uma nova modalidade.
- **Cuidados:**
  - Texto obrigatório [A], palavra por palavra: *"Esta é uma simulação histórica hipotética. Ela mostra como um valor teria evoluído no período selecionado, sem representar previsão, recomendação ou garantia de resultado futuro."*
  - Usar "teria ocorrido", nunca "vai ocorrer". Não chamar de previsão. Não calcular quanto o usuário **deve** investir. Não pedir patrimônio ou renda.
  - Datas de entrada/saída que não são pregão: usar o primeiro pregão em ou após a entrada e o último em ou antes da saída, **exibindo as datas efetivamente usadas** [S].
  - Os dados são de preço de fechamento, sem dividendos (`auto_adjust=False`, sem `Adj Close`); o resultado **não é retorno total**. Custos, impostos e taxas não estão incluídos. Esses avisos entram na tela [A].
  - O valor inicial padrão pode funcionar como âncora. [S] Usar um valor neutro e rotulado como exemplo.
  - Moeda: o resultado fica na moeda de cotação do ativo (R$ ou US$), sem conversão.
- **Critério de aceite [S]:** V_f confere com cálculo manual em três casos (ganho, perda, preço igual); datas efetivas exibidas; texto obrigatório presente; teste de linguagem neutra cobre a página.

### R05 — Gráficos de tendência (sem etapa no cronograma [A]) — **baixa/média**

- **Pedido:** observar se o retorno de um ativo está crescendo, caindo, convergindo, sendo superado por outro ou mudou de comportamento. Exemplo da fala: dois ativos que se cruzam em 2020 e, depois disso, um cresce mais rápido que o outro.
- **Visualizações listadas [A]:** retorno acumulado (Base 100, já existe); retorno móvel em 3, 6 e 12 meses; média móvel do retorno ou do preço; inclinação por regressão linear em janela móvel; cruzamento de séries; diferença de desempenho **D_t = I_A,t − I_B,t** ou **D_t = I_A,t / I_B,t − 1**.
- **Cuidados metodológicos:**
  - Não chamar de previsão. Rotular "tendência histórica", mostrar a **janela** usada e dizer que a tendência passada pode mudar. Não concluir que o ativo continuará superior [A].
  - [S] **Cruzamento em Base 100 depende da data inicial escolhida**: todos partem de 100 na mesma data, então o ponto em que as linhas se cruzam muda se o período mudar. Isso não invalida o gráfico, mas precisa de aviso. A razão A/B (ou D_t em forma de razão, linha de referência em 0) e o retorno móvel são menos sensíveis à data de partida.
  - [S] A diferença D_t = I_A − I_B em pontos de Base 100 e a razão I_A/I_B − 1 respondem a perguntas diferentes (diferença absoluta × desempenho relativo). A escolha precisa ser registrada em `metodologia_de_calculo.md`.
  - [S] A inclinação por regressão em janela móvel é sensível ao tamanho da janela. [A] pede "avaliar estabilidade em diferentes janelas", então a primeira versão pode mostrar mais de uma janela.
  - Desenvolver também alimenta a tentação de previsão, que a pergunta A deixou como trabalho futuro. Manter a linguagem descritiva.
- **Observação:** a seção 8 de [A] não aparece nos critérios de aceite nem no cronograma de [A]. [S] Tratar como "se houver tempo", com a versão mínima: retorno móvel (3/6/12 meses) e D_t em forma de razão para pares de ativos.
- **Critério de aceite [S]:** janela exibida; rótulo "tendência histórica"; teste com série sintética em que o cruzamento e a razão são conhecidos.

### R06 — Educação financeira: textos fixos (Etapa 5)

- **Pedido:** explicar gráficos e indicadores para leigos. Lista [A]: retorno, volatilidade, Sharpe, drawdown, correlação, sazonalidade, RSI, MACD, médias móveis, Base 100. Mais: tooltips, glossário, explicação por gráfico, e o "botãozinho" por gráfico que abre uma explicação curta [B].
- **Já existe:** `app/ui/education.py` (caixas "O que significa?" e glossário), `core/glossary.py` (10 termos no checklist) e `indicator_docs.py` (8 indicadores: SMA, EMA, Bollinger, RSI, MACD, ATR, volatilidade móvel e volume), com teste de linguagem neutra.
- **Lacuna:** cobrir **por gráfico** (não só por indicador), no estilo "o que o gráfico mede / o que indica / cuidado / o que não permite concluir", o mesmo roteiro do prompt-base de [A] 9.5. Para os recursos novos (R02, R04, R05) os textos devem nascer junto com a funcionalidade.
- **Texto-exemplo da reunião [A]:** *"Este gráfico mostra a média histórica do retorno de cada mês. O valor não representa uma regra fixa: um determinado ano pode apresentar comportamento diferente da média."*
- **Cuidados:**
  - O orientador deixou claro que ninguém na equipe é da área de educação ("eu não sou bom de educação"). Há uma pedagoga como possível revisora; ela só entra "quando a ferramenta estiver pronta" [B].
  - [S] A revisão por pessoa da educação serve também como **revisão de conteúdo** (frente 2 de `validacao_academica.md`) e pode alimentar a avaliação de compreensão (O6).
  - Em [B] o orientador cita adolescentes (cerca de 15 anos) como possível público de ensino. **Para a pesquisa, o público definido é "usuários sem formação em finanças" (opção A)**. [S] Não incluir menores de idade como participantes de avaliação sem decisão específica (envolve CEP e TCLE).
  - O uso didático por professores/pais ("ensinar investimento para os filhos") aproxima o projeto da opção B da pergunta de pesquisa, que **não foi a escolhida**. Pode seguir como motivação de extensão, sem mudar objetivos.
- **Critério de aceite [S]:** todo gráfico exibido tem texto explicativo; todos os textos passam no teste de linguagem neutra; os 10 termos da lista de [A] estão no glossário; revisão registrada (por quem, quando).

### R07 — LLM experimental, por fora da ferramenta (Etapa 6) — **não é para agora**

- **Pedido:** nenhuma integração. Apenas **testar prompts** em ferramenta externa (ChatGPT, Gemini ou outra). Só com prompts estáveis considerar API [B]. O orientador indicou um curso (RAG, n8n, Groq, modelos locais) para estudo "com o tempo" e mencionou uma máquina do CEAD para eventual execução local [B].
- **Etapas [A]:** (1) exportar ou capturar dados do gráfico; (2) criar prompts padronizados; (3) testar vários modelos; (4) comparar respostas; (5) identificar alucinações; (6) criar respostas esperadas; (7) manter revisão humana; (8) registrar limitações. Integração (endpoint separado, dados estruturados, contexto do gráfico, proibição de recomendar, linguagem probabilística, origem dos dados) só depois.
- **Prompt-base [A]:** quatro partes (o que o gráfico mede; o que os dados históricos indicam; principal cuidado de interpretação; o que o gráfico não permite concluir), com proibições (sem previsão determinística, sem "barato/caro", sem pontos de compra e venda, sem quanto investir; dizer explicitamente quando os dados são insuficientes).
- **Ponto de atenção:** o exemplo falado de saída da LLM foi *"seria bom você investir em setembro, porque tem uma alta significativa em outubro"* [B]. Essa saída **falharia** no critério de neutralidade de 06/10 e no prompt-base do próprio [A]. [S] Usá-la como **exemplo negativo** no conjunto de teste: o protocolo deve detectá-la.
- **Protocolo mínimo [S] (documento, sem código):**
  - conjunto fixo de casos: 5 a 8 gráficos × 3 ativos de classes diferentes, incluindo casos de dados insuficientes e o caso setembro→outubro;
  - mesmo prompt em pelo menos 2 modelos; cada caso repetido algumas vezes para medir **estabilidade**;
  - para cada caso, uma resposta esperada (escrita antes) e uma lista de verificação: fatos conferem com os dados? alguma recomendação? alguma previsão determinística? algum "barato/caro"? linguagem probabilística?;
  - os dados enviados são só séries públicas e agregadas (sem dados pessoais).
- **Ligação com a pesquisa:** o resultado serve à frente 4 (auditoria de neutralidade) de `validacao_academica.md`. A LLM é **trabalho futuro/experimental** e não deve entrar como objetivo específico do relatório da pergunta A sem decisão (pergunta N09).

### R08 — Home, "Get Started" e vídeo — **média; fica para o plano seguinte**

- **Pedido:** substituir a abertura centrada em "Sobre o Projeto" por uma home com nome, frase de efeito, botão "Começar", vídeo curto e instruções rápidas; cards de acesso a Análise Individual, Comparação, Indicadores e Risco e Retorno; manter "Sobre" como página secundária [A].
- **Estrutura proposta [A]:** nome e frase → botão "Começar agora" → vídeo → "Como usar" em 5 passos (escolha o ativo, defina o período, selecione a frequência, gere a análise, consulte as explicações).
- **Por que o plano seguinte:** [B] diz "não é para agora" e [A] diz que a mudança "não deve preceder a consolidação das funcionalidades principais". Além disso, a home depende de **nome** e **frase de efeito**, que pertencem à Fase 10. [S] Tratar R08 e a Fase 10 como um único bloco, depois das funcionalidades.
- **Não fazer agora [A]:** tutorial complexo antes de validar a navegação; LLM no onboarding; muitas telas; interromper a análise com mensagens demais.
- **Insumo desde já [S]:** o vídeo precisa de uma versão estável e congelada. Registrar a versão do sistema usada na gravação (ver R09).

### R09 — Publicação, autoria e contribuições (Etapa 7)

- **Proposta [B]:** dois demos (artigos curtos). **Trabalho 1:** Argos, com o Clériston como primeiro autor e dono do projeto; a colega ajudaria na escrita. **Trabalho 2:** o trabalho da colega, com ela como primeira autora e escrita, e o Clériston ajudando na implementação. Um apresentaria um e outra apresentaria os dois, se ambos fossem aceitos.
- **Estado:** **condicional**. O orientador disse que vai sugerir à colega "se ela quiser". Não há aceite registrado.
- **[A] adiciona:** nenhum item deve ser decidido sem formalização; documento de contribuições; autoria definida antes da submissão; todos os autores revisam e aprovam a versão final; evitar autores sem contribuição substancial e evitar excluir quem contribuiu; definir quem responde pela integridade do código, dos dados e dos resultados.
- **Ambiguidades:** em [B], o Trabalho 1 teria o Clériston como primeiro autor **e** a colega "atende a escrita"; em [A], o Trabalho 1 tem "primeiro autor: estudante responsável pela implementação" e o Trabalho 2 tem "outra pessoa responsável pela maior parte da escrita". Quem escreve o Trabalho 1, quem apresenta e a ordem completa de autoria não estão definidos (pergunta N11).
- **Cuidado:** [A] afirma que "o CNPq recomenda..." autoria por contribuição significativa. Isso **não aparece na fala** e não foi verificado por mim. [S] Conferir o texto oficial (CNPq e/ou UFPI/PIBITI) antes de citar em qualquer documento.
- **Entregáveis [A]:** definir evento ou chamada; verificar formato (demo, artigo curto, completo); separar resultados da plataforma dos resultados do outro projeto; versão demonstrável; slides e roteiro; registrar versões do sistema usadas na demo.
- **[S] Documento de contribuições:** criar `docs/contribuicoes.md` agora, em formato de tabela (pessoa × implementação, análise, escrita, revisão, responsabilidade por código e dados), com datas. Pode seguir a taxonomia CRediT, se o orientador concordar. Registrar também a origem de ideias (ex.: a ideia da simulação foi atribuída ao Giovanni em [B]); isso protege todos na definição de autoria.
- **Aviso:** o cronograma formal do PIBITI pode ser alterado na execução [B], mas [S] confirmar com o orientador se os relatórios parcial e final devem registrar a mudança de escopo.

### R10 — Revisão transversal de linguagem (decorre de D02)

- **Pedido [A]:** revisar textos da interface para evitar linguagem prescritiva; diferenciar análise histórica, simulação e recomendação; preservar avisos metodológicos.
- **Já existe:** teste automático de linguagem neutra nos textos de `indicator_docs.py`; disclaimers por página.
- **Lacuna [S]:** estender o mesmo teste a **todos os textos novos** (sazonalidade por ano, simulação, tendência, educação, home) e a qualquer saída de LLM no protocolo de R07. Mantém uma lista única de termos proibidos e de padrões a vigiar (compre, venda, melhor momento, barato, caro, "vai subir", "deve investir").

---

## 4. Ideias citadas e itens de reserva (não entram no plano agora)

- Executar LLM **localmente** em máquina do CEAD (se for necessário processar localmente) [B].
- Fluxo "no-code" com n8n e uso de Groq como alternativa simples [B] (a transcrição grafa "SN8N" e "Grok").
- Arquitetura **RAG** para fundamentar respostas em documentos e regras do sistema; [A] ressalva que RAG não elimina alucinações e exige avaliação de recuperação e de geração.
- Segundo artigo, voltado a evento de educação, com a parte educativa [B]: "na medida do possível".
- Convidar a colega pedagoga para pensar a vertente educativa quando a ferramenta estiver pronta [B].
- Possível uso didático por professores e famílias [B] (ver R06, sobre o escopo).
- Dividir a comparação em pares quando houver muitos ativos [B: "dividir pra dois"].
- Frequências semestral/anual (aberto desde antes; ver `fontes_e_tratamento_de_dados.md`, seção 4).

---

## 5. Divergências e ambiguidades entre as fontes

| # | Tema | [A] diz | [B] diz | Tratamento proposto |
| --- | --- | --- | --- | --- |
| 1 | Home | Prioridade média; o critério de aceite exige "home com acesso inicial simples" | "Não é para agora", "por enquanto, deixa lá" | Ir para o plano seguinte, junto com a Fase 10. Remover o critério de aceite da home **desta** rodada, ou marcá-lo como pertencente ao Plano 3 |
| 2 | Seções 3 e 10 de [A] | Descrevem a mesma home duas vezes, com textos ligeiramente diferentes (frases de efeito e passos) | — | Tratar como uma única demanda (R08). A frase de efeito é provisória até a Fase 10 |
| 3 | Ordem de trabalho | Simulação (Etapa 4) depois da comparação (Etapa 3) | A fala percorre: home, simulação, sazonalidade, comparação, tendência, educação, LLM | Adotar a ordem de [A], por ser a organizada, mas confirmar (N01) |
| 4 | Tendência | Seção própria, prioridade baixa/média, **fora do cronograma e dos critérios de aceite** | "Gráficos difíceis, mas possíveis", "tá longe ainda" | Versão mínima opcional (R05). Perguntar se entra nesta rodada |
| 5 | Itens da Etapa 1 | "Corrigir seleção de ativos", "validar logos" | Não aparecem | Pedir a descrição dos defeitos (R01) |
| 6 | Linguagem do orientador × neutralidade | Proíbe linguagem prescritiva e recomendação | Usa exemplos como "seria bom investir em setembro", "vou apostar nele", "melhor de investir" | O exemplo expressa a lógica de uso, não o texto da interface. Registrar a linguagem neutra como regra e confirmar com o orientador (N08) |
| 7 | Autoria | Trabalho 1: primeiro autor é o estudante da implementação; Trabalho 2: outra pessoa escreve | Dois cenários cruzados (cada um primeiro autor de um, ajudando no outro), **condicionado ao aceite da colega** | Formalizar por escrito (R09). Não tratar como decidido |
| 8 | Instituição de apoio | "O CNPq recomenda…" | Não aparece | Verificar fonte oficial antes de citar |
| 9 | LLM | "Somente depois" de prompts, com proibição de recomendação | O orientador descreve uma LLM que "explica o gráfico" e diz se seria bom investir | Aplicar [A] (proibir recomendação). O "botão que explica" entra agora **com texto fixo** (R06) |
| 10 | Número de ativos | 2 a 5 no gráfico; mais só em tabela | "Os caras gostam de ver muito"; "bota dois, três, quatro" | Manter 5 no gráfico (já existe). Decidir a tabela com mais ativos (N06) |
| 11 | Cronograma | Sete etapas, sem datas | O cronograma do plano de trabalho é "fake"; pode alterar na execução; TCC e prazos "estão longe" | O plano precisa de datas reais (N10) |
| 12 | Evento | "Definir possível evento ou chamada" | Menciona uma chamada de demos com termo ininteligível na transcrição ("demo semanal de jantar") | Perguntar o nome do evento e o prazo (N10) |

---

## 6. Impactos nos documentos existentes

| Documento | O que precisa mudar |
| --- | --- |
| `checklist_pendencias.md` | Novo adendo ("Adendo de 07/10/2026 — segunda reunião") com R01 a R10; atualizar a seção "9. Simulação de aportes" com a distinção entre janelas móveis e datas livres (R04); atualizar "10. Comparação" com sazonalidade e anos; incluir as novas perguntas na seção C |
| `validacao_academica.md` | (a) **Escopo:** sazonalidade por ano, simulação, comparação ampliada e tendência não estão entre os quatro grupos de indicadores da pergunta A (tendência, momentum, volatilidade, volume). Decidir se são "organização para interpretação" (dentro da pergunta) ou extensões fora do objetivo principal. (b) A **camada educativa** passa a ser entrega explícita: reforça O6 e a comparação "com × sem camada educativa". (c) O protocolo de prompts (R07) alimenta a **auditoria de neutralidade** (frente 4). (d) A revisão pela pedagoga entra na **frente 2** (conteúdo). (e) Adicionar o recurso de anos específicos como caso de **teste de valores de referência** (média do recorte) na frente 1 |
| `metodologia_de_calculo.md` | Documentar, quando implementados: média do recorte por anos e N por mês; diferença em pontos percentuais; tratamento do mês em andamento; V_f = V_0 × P_f/P_0 e o uso de preços de fechamento sem dividendos; retorno móvel; D_t (diferença e razão) e a escolha adotada; janela de qualquer regressão |
| `arquitetura.md` | Novos módulos de `core/` (filtro sazonal por anos, simulação com datas livres, tendência) e, se houver, a página inicial. Reforçar a regra de que `core/` não importa `app/` |
| `fontes_e_tratamento_de_dados.md` | Sem mudança necessária agora. Se a simulação aceitar datas livres, acrescentar a regra de pregão efetivo |
| `docs/contribuicoes.md` (novo) | Criar (R09) |
| `docs/protocolo_prompts_llm.md` (novo, [S]) | Criar quando a Etapa 6 começar (R07) |

**Testes novos esperados [S]:** filtro sazonal (regressão com todos os anos; subconjunto; N por mês; meses com lacuna; ano corrente); simulação (três casos manuais; datas fora de pregão; ativos excluídos); comparação (sazonalidade por ativo); retorno móvel e D_t com séries sintéticas; linguagem neutra para todos os textos novos.

---

## 7. Critérios de aceite da rodada, em forma verificável

Os 12 critérios de [A] (seção 12) reescritos para poderem ser conferidos:

| # | Critério de [A] | Como verificar [S] |
| --- | --- | --- |
| 1 | Aplicação inicial estável | Suíte de testes verde; roteiro de navegador executado nas 5 páginas, com registro |
| 2 | Análise individual compreensível | Cada gráfico com texto explicativo; teste de leitura por pessoa leiga (informal, antes da avaliação formal) |
| 3 | Comparação funciona sem poluição visual | Conferência com 5 ativos de classes diferentes em tela padrão |
| 4 | Comparar anos específicos | R02 aceito pelos critérios próprios |
| 5 | Simulação claramente delimitada | Texto obrigatório presente; cálculo conferido; datas efetivas exibidas |
| 6 | Indicadores com textos explicativos | Cobertura da lista da seção 9.2 de [A] no glossário e nas caixas |
| 7 | Sistema sem recomendações diretas | Teste de linguagem neutra em todas as páginas novas |
| 8 | Home com acesso inicial simples | **Fora desta rodada** (Plano 3, com a Fase 10) — depende da confirmação do orientador (N01) |
| 9 | Código testado | Cobertura de `core/` mantida em 100% para os módulos novos |
| 10 | Documentação atualizada | Documentos da seção 6 revisados |
| 11 | Contribuições registradas | `docs/contribuicoes.md` criado e preenchido |
| 12 | (síntese de [A]) Ordem em camadas respeitada | Plano 2 cumprido na ordem aprovada |

---

## 8. Perguntas para o orientador

Numeração própria (N), para não colidir com as da seção C do checklist.

| ID | Pergunta | Por que importa |
| --- | --- | --- |
| N01 | Confirma que home, "Get Started" e vídeo ficam para depois das funcionalidades e junto com a Fase 10? | [A] e [B] divergem (seção 5, item 1) |
| N02 | O filtro por anos fica na Análise Individual, em página própria ou nas duas (reaproveitando a lógica na Comparação)? | Define estrutura de `core/` e de páginas |
| N03 | "Depositar em setembro e retirar em outubro" significa o retorno do mês de outubro ou setembro + outubro? Vale também para a simulação (R04)? | Dois números diferentes |
| N04 | A simulação deve aceitar **data de entrada e saída livres** para um ativo (além das janelas móveis que já existem)? | Verificar a lacuna de R04 |
| N05 | Aceita exibir, além da média, a **mediana** e a proporção de anos positivos por mês? | Medidas mais robustas para o caso do orientador |
| N06 | O limite de 5 ativos vale só para o gráfico? Tabela com mais ativos entra nesta rodada? | Seção 7.4 de [A] |
| N07 | Os gráficos de tendência (R05) entram nesta rodada ou ficam para depois? Em caso afirmativo, qual versão mínima? | Estão fora do cronograma de [A] |
| N08 | Confirma que os textos da interface seguirão linguagem descritiva ("maior retorno no período"), mesmo quando a pergunta do usuário for "qual é melhor?" | Coerência com D02 e com a ata de 06/10 |
| N09 | A LLM experimental é parte do relatório da pergunta A ou trabalho futuro e extensão? | Evita ampliar o escopo da pergunta |
| N10 | Qual é o evento/chamada de demo, o formato e o prazo? Quais são as datas do TCC e dos relatórios parcial e final do PIBITI? | O plano precisa de datas reais |
| N11 | Autoria: quem escreve o Trabalho 1, quem apresenta e qual a ordem de autoria nos dois? A colega aceitou a proposta? | R09 está condicional |
| N12 | Quais são os defeitos de "seleção de ativos" e "logos" citados na Etapa 1 de [A]? | Sem descrição, não vira tarefa |
| N13 | Os relatórios do PIBITI devem registrar a mudança do escopo em relação ao cronograma formal? | D22 |
| N14 | A avaliação com pessoas (O6) terá apenas adultos? Qual o caminho de CEP/TCLE? | Segue da seção C do checklist; menores exigem decisão à parte |

---

## 9. Termos ininteligíveis da transcrição e como foram lidos

| Trecho | Leitura adotada | Confiança |
| --- | --- | --- |
| "demo semanal de jantar" | Termo de uma chamada de demos; não identificado | Baixa — perguntar (N10) |
| "Paris" ("bota de Paris") | "pares" (comparação em pares) | Média |
| "L&M" | LLM | Alta |
| "reg", "as regs" | RAG | Alta |
| "SN8N" | n8n | Alta |
| "Grok" | Groq (nome provável da ferramenta citada; a transcrição pode estar trocando por "Grok") | Média |
| "CEAD" | Unidade da UFPI mencionada como detentora de máquina potente | Alta (como nome); conteúdo não verificado |
| "Giovanni" | Participante da reunião, a quem se atribui a ideia da simulação | Alta |
| "ela" (trabalho da colega) | Colega citada sem nome; não identificada | — |
| "Tu já está com a conta baixa" | Trecho sem sentido claro (talvez "carga baixa"); não usado | Baixa |

---

## 10. Insumos para elaborar o Plano 2

### 10.1 Dependências

```
R01 consolidação ──┬─> R02 sazonalidade por anos ──┬─> R03 comparação (sazonalidade e anos)
                   │                                └─> R06 textos (novos gráficos)
                   ├─> R04 simulação (verificar o que existe)
                   ├─> R10 linguagem neutra (acompanha todos)
                   └─> R09 contribuições (paralelo, sem código)

R05 tendência (opcional) ── depende de R03 (pares de ativos) e de R06 (texto)
R07 protocolo de prompts ── paralelo, só documento; depende de R02/R03 para ter gráficos de teste
R08 home + vídeo + Fase 10 ── Plano 3, depois de tudo acima estável
```

### 10.2 Ordem proposta para o Plano 2 [S]

Proposta para discussão, não decisão:

1. **Bloco 1 — Consolidação:** conferência no navegador, defeitos de seleção/logo (R01), `docs/contribuicoes.md` (R09, começo).
2. **Bloco 2 — Sazonalidade por anos** em `core/` + página + testes (R02).
3. **Bloco 3 — Comparação ampliada:** apenas as lacunas (sazonalidade comparada, anos, tabela maior, legenda interativa) (R03).
4. **Bloco 4 — Simulação:** verificar o código existente e fechar a diferença para datas livres (R04).
5. **Bloco 5 — Educação:** textos por gráfico, botão "como ler este gráfico" com texto fixo, ampliação do glossário (R06) e extensão do teste de linguagem neutra (R10).
6. **Bloco 6 — Tendência mínima**, se aprovada (R05).
7. **Bloco 7 — Protocolo de prompts externos** (R07), documento apenas.
8. **Bloco 8 — Fechamento:** documentação (seção 6), revisão do checklist, registro de versão para demo.

**Plano 3 (fora desta rodada):** Fase 10 (nome e identidade visual) + home + onboarding + vídeo (R08); eventual integração de LLM, só após prompts estáveis.

### 10.3 Riscos

| Risco | Efeito | Mitigação |
| --- | --- | --- |
| Escopo cresce além da pergunta A | Dispersão; relatório sem foco | N09 e a revisão de escopo de `validacao_academica.md` |
| Datas desconhecidas (TCC, relatórios, evento) | Plano sem prazo realista | N10 |
| Linguagem prescritiva escapar (textos novos ou saída de LLM) | Contradiz D02 e a ata de 06/10 | Teste de linguagem neutra obrigatório (R10) |
| Interpretação errada de "média" com poucos anos | Conclusão enganosa pelo usuário | N por mês sempre visível; mediana e % de anos positivos (N05) |
| Autoria indefinida | Conflito depois | Documento de contribuições desde já; N11 |
| Cálculo de simulação parecer retorno total | Erro de interpretação | Aviso de preço de fechamento sem dividendos e sem custos |
| Dependência de uma fonte não oficial (Yahoo Finance) na demo | Falha ao vivo | Registrar versão e, se aprovado, preparar dados salvos para a demo [S] |

### 10.4 O que **não** fazer nesta rodada (reunião)

- Integrar API de LLM ou RAG; colocar LLM no onboarding [A+B].
- Construir tutorial longo ou com muitas telas [A+B].
- Mudanças visuais e de identidade (Fase 10) [decisão de hoje].
- Qualquer texto que sugira previsão, recomendação ou valor a investir [A].

---

## 11. Próximos passos imediatos

1. Enviar este registro ao orientador (ou usar como roteiro da próxima conversa) e obter as respostas da seção 8, em especial N01, N03, N04, N07, N10 e N11.
2. Atualizar `checklist_pendencias.md` com o adendo desta reunião.
3. Com as respostas, escrever o **Plano 2** (blocos, ordem, datas e critérios de aceite).
4. Em paralelo, sem depender de respostas: conferir as 5 páginas no navegador (R01) e criar `docs/contribuicoes.md` (R09).

---

## 12. Respostas recebidas em 09/10/2026

| ID | Resposta | Efeito sobre este registro |
| --- | --- | --- |
| N01 | Confirmado: "Get Started" e vídeo ficam para depois das funcionalidades, junto com a Fase 10 | R08 sai do Plano 2 e vai para o Plano 3. O critério de aceite 8 da seção 7 fica fora desta rodada |
| N03 | Fechamento de setembro → fechamento de outubro, apresentado como **janela de retorno** (composta), não como soma de dois percentuais mensais | Resolve a ambiguidade de R02: "setembro→outubro" é o retorno de outubro. Janelas maiores são compostas |
| N04 | **Não**: manter apenas as janelas móveis históricas já existentes | R04 deixa de ter a lacuna "datas livres". O trabalho se reduz a revisar texto e rótulos. Permanece a pergunta N04b (a janela sazonal por ano atende ao exemplo do orientador?) |
| N07 | Começar por retorno móvel e razão de desempenho, sem regressão de tendência | R05 restrito a esses dois. Regressão e detecção de cruzamentos saem da primeira versão |
| N10 | Evento: SBBD (trilha de demos). Chamada prevista até abril/2027; evento em setembro/2027, Porto Alegre/RS. Regras de submissão informadas (6 páginas, modelo SBC, PDF, avaliação não duplo-cega, screencast de até 5 min, JEMS, Anais Estendidos na SOL) | R09 ganha evento e prazo-âncora. Faltam as datas do TCC e dos relatórios do PIBITI (N15). As regras do evento foram informadas pelo usuário e devem ser conferidas na chamada oficial |
| N11 | O orientador sugeriu um trabalho colaborativo com outra orientanda, mas **nada está confirmado**. Em 09/10 (N16): não registrar nada sobre isso em `docs/contribuicoes.md`; tratar no próximo plano | R09 fica limitada ao que já existe no Argos. Autoria e trabalho colaborativo vão para o Plano 3 |
| LLM | A integração de API e LLM pode entrar no Plano 2, como camada de interpretação assistida, contextual e auditável: recebe dados estruturados já calculados, descreve filtros e limites, não calcula, não escolhe dados, não recomenda. Esquema JSON na saída; prompts, interface e gestão de segredos especificados | R07 passa de "não é para agora" a Bloco 7 do Plano 2, em duas etapas: 7A (protocolo de prompts externos) e 7B (API), com condição de passagem. Mantém a ordem pedida pelo orientador em 07/10 |

**Ponto de atenção registrado:** em 07/10 o orientador disse que a API não deve entrar "por enquanto" e que primeiro se testam prompts estáveis. A inclusão no Plano 2 só é compatível com isso se o protocolo de prompts vier antes e o orientador aprovar a passagem à API (N17).

**Perguntas ainda abertas após a segunda rodada:** ver a seção 13 e o Plano 2, seção 7.

---

## 13. Respostas recebidas em 09/10/2026 (segunda rodada)

| ID | Resposta | Efeito sobre este registro |
| --- | --- | --- |
| N02 | O recorte por anos fica **só na Análise Individual** | A Comparação não terá anos selecionados comparados; mantém a sazonalidade geral por ativo. Reduz o que o orientador pediu em D12; revisitar no Plano 3 se ele quiser |
| N04b | Sim: a janela sazonal por ano atende ao exemplo "depositar em setembro e retirar em outubro" | Fecha R04 sem nova modalidade de simulação |
| N05 | Sim: exibir mediana e proporção de anos positivos por mês, além da média | Incorporado a R02 |
| N06 | Não: sem tabela com mais de 5 ativos nesta rodada | R03 perde essa lacuna |
| N08 | Sim: linguagem descritiva em toda a interface | Regra transversal confirmada (R10, D02) |
| N09 | A LLM entra no relatório da pergunta A como **componente de apoio à interpretação e à educação financeira**, com papel delimitado, não como núcleo metodológico | R07 deixa de ser "extensão externa" e passa a integrar o escopo; `validacao_academica.md` deve refletir isso |
| N12 | Desconsiderar: não existem defeitos de seleção de ativos ou logos | Resolve a divergência 5 da seção 5. R01 sem essa tarefa |
| N13 | Sim: os relatórios do PIBITI devem registrar a mudança de escopo (cronograma original, cronograma executado, alterações com justificativas e conexão com o objetivo geral), sobretudo no Relatório Parcial e no Final | Resolve D22. Vira tarefa do Bloco 8 |
| N14 | A avaliação O6 será só com adultos (18 anos ou mais), com TCLE; sem menores nesta etapa | Fecha a ressalva de R06 sobre adolescentes. Permanece a dúvida sobre parecer do CEP (N14b) |
| N15 | Relatório Parcial até 31/03/2027; Relatório Final e Resumo Expandido até 28/08/2027; defesa do TCC até 31/10/2027 | Fornece as datas pedidas na seção 8; entram no calendário do Plano 2 |
| N16 | O orientador apenas sugeriu; nada confirmado sobre o trabalho colaborativo. Não registrar em contribuições; deixar para o próximo plano | Ver N11 acima |
| N17 | OpenAI, `gpt-5-mini` (principal) e `gpt-5-nano` (comparação); saída em JSON Schema; limites de custo e uso; limiares de passagem da 7A; rubrica de 0 a 5. Foi informado que a transição da 7A para a 7B está aprovada pelo orientador, condicionada ao cumprimento de todos os critérios | Detalhado em `docs/llm_7b_especificacao.md`. A 7B não começa antes de a 7A atingir todos os limiares |
| N18 | Demonstração principal ao vivo, com dados salvos e em cache. Reserva obrigatória: screencast de até 5 min. Reserva secundária: versão online pública | Registrado no Plano 2, seção 5.1 |

**Ressalvas registradas sobre N17** (detalhes em `docs/llm_7b_especificacao.md`, seção 7): a temperatura de 0 a 0,2 e o limite de 900 tokens podem não funcionar com modelos de raciocínio, e isso não foi confirmado na documentação oficial; o limite "por usuário por dia" não é aplicável sem login; 200 interpretações por dia com `gpt-5-mini` custam ≈ US$ 7,80 em 30 dias, acima do teto mensal de US$ 5,00; o preço do `gpt-5-nano` não foi verificado.

**Perguntas que continuam abertas:** N14b (CEP), N19 a N24 (Plano 2, seção 7). N16 fica para o Plano 3.

---

## 14. Respostas recebidas em 09/10/2026 (terceira rodada)

| ID | Resposta | Efeito sobre este registro |
| --- | --- | --- |
| N14b | O CEP exige parecer favorável antes do início da coleta da avaliação O6 com adultos; o TCLE é necessário, mas não substitui a apreciação ética | Fecha a pergunta pendente de R06 e da seção C do checklist. Cria o Bloco 9 do Plano 2 e um prazo externo |
| N16 | Sim (adiar para o próximo plano) | Confirma o tratamento de N11 e N16 |
| N19 | Limites em três camadas: sessão (`st.session_state`), navegador (cookie/localStorage) e global em contador persistente | Registrado na especificação da LLM |
| N20 | Três avaliadores humanos independentes (leigo, técnico, neutralidade); sessão de calibração; kappa ponderado ≥ 0,60; regras de aprovação por resposta | Registrado na especificação da LLM. Ressalvas: o kappa exige itens comuns entre avaliadores; a regra por resposta (100% de correção factual) e o limiar agregado (≥ 95%) precisam de reconciliação |
| N21 | A evidência escrita fica em `docs/pibiti/decisoes_orientador.md` | Arquivo criado com modelo preenchido; as evidências a anexar são suas |
| N22 | "Faça o que achar mais recomendado" | Decidido por delegação: versão pública sem explicação assistida; ativa só na demonstração ao vivo e no screencast |
| N23 | "Depois" | Interpretado como depois do congelamento da versão; confirmar (N30) |
| N24 | "Faça o que achar mais recomendado" | Decidido por delegação: Streamlit Community Cloud |

**Perguntas que continuam abertas:** N25 a N30 (Plano 2, seção 7). N16 fica para o Plano 3.