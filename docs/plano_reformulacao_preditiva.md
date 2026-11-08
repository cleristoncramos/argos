# Plano de reformulação: previsão, estratégias e apoio à decisão

**Status:** proposta em revisão (etapa 0) · **Criado em:** 07/11/2026
**Origem:** reunião com o orientador em 07/11/2026 e documento de sugestões de reformulação apresentado nela (arquivo `reunião 07.11.2026.docx`, guardado fora do repositório).

> **Nada neste documento está aprovado.** O documento de sugestões é uma proposta. Cada decisão abaixo só passa a valer depois de confirmada por escrito pelo orientador e registrada em [`pibiti/decisoes_orientador.md`](pibiti/decisoes_orientador.md), com a evidência arquivada. Até lá, continuam valendo as regras atuais do projeto.

---

## 1. O que muda na proposta

Até 07/11/2026, o Argos foi delimitado como plataforma de análise histórica, comparação de ativos, indicadores técnicos, métricas de risco, simulação de aportes e interpretação textual **sem previsão nem recomendação** (pergunta de pesquisa A, 07/10/2026).

A proposta organiza o sistema em três camadas:

| Camada | Pergunta respondida | Evidência necessária |
| --- | --- | --- |
| Descritiva | O que aconteceu? | Cálculos corretos e interpretação fiel |
| Preditiva | O que o modelo estima para um horizonte futuro? | Avaliação temporal fora da amostra e medida de incerteza |
| Decisória | Que estratégia apresenta a relação entre retorno, risco e custos mais favorável neste cenário? | Backtest, comparação com referências e regras explícitas |

A LLM pode comunicar as três camadas, mas não substitui a validação de nenhuma delas. Ela explica evidências, estimativas e conclusões produzidas por uma camada quantitativa validada; não escolhe por conta própria o "melhor momento para investir".

### 1.1 Pergunta de pesquisa proposta

> **Como integrar análise histórica, modelos preditivos e explicações por modelos de linguagem em uma plataforma compreensível para pessoas sem formação em finanças, avaliando desempenho fora da amostra, incerteza, utilidade decisória e compreensão dos resultados?**

Duas avaliações separadas:

- **quantitativa:** os modelos e as estratégias acrescentam informação útil em relação a referências simples?
- **com pessoas:** os usuários entendem resultados, riscos e incerteza sem interpretar a ferramenta como garantia de retorno?

Um modelo que não supere a referência também é resultado científico válido, desde que documentado.

### 1.2 Recomendação de investimento e enquadramento regulatório

A CVM distingue consultoria (orientação profissional e individualizada) e análise (relatórios capazes de influenciar decisões de investimento), e a orientação sobre robôs de investimento cita sistemas que indicam oportunidades e momentos de entrada ou saída. Por isso, a proposta prevê:

| Ambiente | Uso |
| --- | --- |
| Público | Análises históricas e recursos estabilizados; previsões e sinais apenas conforme o enquadramento revisado |
| Experimental restrito | Desenvolvimento e avaliação de previsões e estratégias, antes de qualquer liberação pública |

A aprovação acadêmica não substitui a análise institucional ou jurídica, e um aviso "não é recomendação" não resolve uma função que de fato recomenda. **Até a consulta regulatória, nenhuma recomendação ("compre", "não invista", "entre neste mês") é oferecida ao público.**

---

## 2. Diagnóstico do estado atual

### 2.1 Arquitetura

| Item | Estado em 07/11/2026 | O que a proposta exige |
| --- | --- | --- |
| Separação `core/` (puro) e `app/` (Streamlit) | Implementada; `core/` com 100% de cobertura | Manter |
| Coleta | Sob demanda, a cada consulta, pelo yfinance, com cache de 1 h | Para os modelos: dados versionados com data de corte |
| Versionamento de dados | Só no modo demo (manifesto com data e hash SHA-256) | Reaproveitar o manifesto como base do conjunto de treino |
| Camada de variáveis | `core/features.py`, sem alvo e sem informação futura (testado) | Acrescentar o alvo, sempre fora do app de consulta |
| Modelos | Não existem | Treino em rotina separada; registro com `model_id`, datas de treino e de corte, métricas |
| Inferência | Não existe | No app, só carregar o modelo aprovado e calcular a estimativa |
| Motor de decisão e backtest | Não existem | Regras simples e transparentes; simulação com a informação disponível em cada data |
| Pacote de evidências para a LLM | Contexto só histórico (`core/llm_builders.py`) | Pacote com histórico, previsão, validação, decisão e política de liberação |
| Dependências | Sem scikit-learn ou statsmodels; limite de 1 GB no Streamlit Cloud, Python 3.14 | Conferir compatibilidade e memória antes de escolher bibliotecas |

### 2.2 Cálculos

- **Preço sem ajuste.** O Argos baixa com `auto_adjust=False` e calcula retorno de preço. Para comparar estratégias, a proposta pede custos e slippage configuráveis, tratamento de proventos e desdobramentos, moeda explícita e resultado "antes de impostos". Retorno de preço não pode ser rotulado como retorno total.
- **Simulação de aportes.** `core/simulation.py` compara aportes periódicos com um aporte único de mesmo total no início. Falta tratar o saldo não aplicado e falta o segundo experimento (dinheiro recebido ao longo do tempo, sem antecipar capital).
- **Sazonalidade.** As médias mensais são calculadas sobre todo o histórico. Usá-las como estratégia exigiria teste fora da amostra; escolher a "melhor sazonalidade" e testá-la no mesmo histórico é vazamento.
- **Unidade de tempo.** Variação por prazo e quedas usam dias corridos; o alvo proposto usa observações (pregões). O contrato de cada cálculo precisa dizer qual unidade usa.

### 2.3 LLM, prompts e validador

- O prompt v0.6 congelado (`core/llm_prompts.py`, impressão digital `e3b3574b7430`) proíbe falar do futuro, usar "previsão" e qualquer linguagem de decisão, e recusa pedidos de previsão com frase fixa.
- O validador (`core/llm_validation.py`) bloqueia por vocabulário (`sem_previsao`, `sem_recomendacao`, termos proibidos). Ele não verifica **autorização**: não sabe se uma estimativa veio de um modelo validado.
- A aprovação da 7A vale para a finalidade anterior e **não valida** a função nova. Fica preservada como histórico.

### 2.4 Testes de linguagem

Cerca de dez arquivos de teste garantem que os textos do app não sugerem previsão nem recomendação (por exemplo `test_chart_guides`, `test_simulation_texts`, `test_disclaimers` e os das tabelas). Eles continuam corretos para a camada descritiva. A camada experimental precisa de regras próprias (seção 4), não da retirada dessas.

### 2.5 Avaliação

Não há protocolo de aprendizado de máquina (previsão está registrada como trabalho futuro em [`validacao_academica.md`](validacao_academica.md), seção 8). As minutas do O6 ([`pibiti/cep/`](pibiti/cep/)) descrevem uma ferramenta só descritiva.

---

## 3. Incompatibilidades com as regras vigentes

| Regra ou decisão vigente | Efeito da proposta | Situação |
| --- | --- | --- |
| Pergunta de pesquisa A (07/10/2026) | Substituída pela pergunta da seção 1.1 | A confirmar |
| Previsão, modelos e validação temporal fora do escopo | Reabrir | A confirmar |
| Dividendos, custos e impostos fora dos cálculos; A5 e A6 no Plano 3 | Reabrir para o backtest de estratégias | A confirmar |
| Parecer de 24/10/2026: sem previsão, recomendação, pontuação ou oportunidade | Substituir, na camada experimental, por regras de autorização | A confirmar |
| N07: sem regressão nem detecção de cruzamentos | Não se aplica à camada preditiva | A confirmar |
| N04: simulação só com janelas móveis | Ampliar com os dois experimentos de aporte | A confirmar |
| Prompt v0.6 congelado; mudança exige nova versão e nova 7A | Mantida: a v0.6 segue nas telas descritivas; nova família v1.0-experimental com avaliação própria | Compatível |
| N22: versão pública sem chamadas ao modelo | Decidir para o ambiente experimental | A decidir |
| 25/10/2026: sem novas funcionalidades neste ciclo | Compatível se a versão histórica for congelada e a experimental seguir como incremento separado | A decidir |
| Congelamento em fevereiro de 2027 | Proposta: congelar só a versão histórica | A decidir |
| Minutas do CEP e do TCLE (submissão prevista para 15/12/2026) | Revisar antes ou emendar depois | A decidir |

---

## 4. Regras por camada (proposta)

Separar as regras evita que a camada experimental afrouxe as garantias da camada descritiva.

| Regra | Camada descritiva (atual) | Camada experimental (proposta) |
| --- | --- | --- |
| Futuro | Não mencionar | Mencionar só estimativas fornecidas por modelo autorizado, com horizonte, data de corte e incerteza |
| Previsão | Recusar | Explicar a previsão disponível; abster-se quando não houver modelo válido |
| Linguagem decisória | Bloquear | Permitir só a conclusão emitida pelo motor de decisão, com a regra que a produziu |
| Organização do texto | Só passado | Separar observação histórica, estimativa e implicação para a estratégia avaliada |
| Neutralidade | Ausência de orientação | Ausência de persuasão, promessa, urgência, conflito oculto e falsa certeza |
| Recomendação ao público | Nunca | Desligada (`recommendation_enabled: false`) até o parecer regulatório |
| Testes de linguagem | Os atuais, inalterados | Conjunto próprio, aplicado só aos textos experimentais |

A família de protocolo da LLM para a camada experimental será nova (por exemplo `v1.0-experimental`), com contexto, esquema, prompt e validador próprios e uma avaliação humana nova. A v0.6 não é alterada.

---

## 5. Decisões pendentes

| # | Decisão | Com quem |
| --- | --- | --- |
| R1 | Quais sugestões do documento de 07/11/2026 foram adotadas, confirmadas por escrito | Orientador |
| R2 | Quem faz a consulta institucional ou jurídica sobre recomendação (UFPI, procuradoria, núcleo de inovação) | Orientador |
| R3 | Como restringir o ambiente experimental (só local ou app separado com acesso por convite) | Orientador |
| R4 | Congelar em fevereiro de 2027 apenas a versão histórica, e sobre qual versão aplicar o O6 | Orientador |
| R5 | Texto final da pergunta e dos objetivos, e como o Relatório Parcial registra a mudança de escopo | Orientador |
| R6 | Piloto: ativos, horizonte (ex.: 20 pregões), alvo (retorno acumulado simples ou logarítmico) e modelos | Orientador |
| R7 | Estratégia do piloto (ex.: exposto ou fora do mercado), custos e remuneração do caixa (ex.: CDI) | Orientador |
| R8 | Usar preço ajustado por proventos no piloto | Orientador |
| R9 | CEP: submeter o protocolo atual e emendar depois, ou revisar antes da submissão | Orientador e CEP |
| R10 | LLM no ambiente experimental: chamadas ao modelo ou só respostas salvas, e orçamento | Orientador |
| R11 | API separada (o documento a considera opcional) | Orientador |
| R12 | Relação com o TCC "Previsão de Riscos Financeiros" (Lorrana Evelyn de Araújo Pereira), que prevê volatilidade; o piloto proposto prevê retorno | Orientador e autora |
| R13 | Confirmar quais registros de [`pibiti/decisoes_orientador.md`](pibiti/decisoes_orientador.md) têm evidência original (seção "Auditoria de 07/11/2026" daquele arquivo) | Orientador |

---

## 6. Plano de execução por etapas

"Documento" resume a sugestão do documento de 07/11/2026; "Complemento" são acréscimos propostos pelo desenvolvedor, também sujeitos a confirmação.

| Etapa | Documento | Complemento | Condição de passagem |
| --- | --- | --- | --- |
| 0. Revisão de escopo | Nova pergunta, arquitetura confirmada, estratégia de publicação | Este plano; auditoria das decisões; tag da versão histórica; revisão das minutas do CEP; atualização de `validacao_academica.md` e `fora_do_escopo.md`; regras por camada (seção 4) | Confirmação escrita do orientador e encaminhamento da revisão regulatória |
| 1. Experimento local | Poucos ativos, alvo e referência definidos | Em `experiments/`, fora do app; dados ajustados; manifesto com data de corte e hash; teste automático de que nenhum rótulo cruza a fronteira entre treino e teste | Conjunto de dados reproduzível e divisões temporais verificadas |
| 2. Modelagem | Referência ingênua (retorno zero ou preço constante), ARIMA, regressão regularizada e gradient boosting ou Random Forest; LSTM só depois, se justificado | Validação com origem móvel e intervalo entre treino e teste de pelo menos o horizonte; teste final usado uma única vez; registro dos modelos que não funcionaram; intervalo preditivo avaliado por cobertura; probabilidade só com modelo calibrado (Brier) | Relatório fora da amostra, com limitações |
| 3. Estratégia | Regra transparente, custos, comparação; backtest sem vazamento nem seleção retroativa | Os dois experimentos de aporte; caixa remunerado; custos e slippage configuráveis; correção pelo número de regras testadas | Backtest documentado, inclusive regras rejeitadas |
| 4. LLM | Novo contexto, prompt e validação | Família `v1.0-experimental`; validador de autorização e fidelidade; rubrica com comunicação da incerteza; v0.6 intacta | Explicações fiéis, sem números ou sinais inventados |
| 5. Integração | Inferência por API e interface experimental | Começar sem API: inferência no app a partir do modelo registrado, atrás de um interruptor; histórico e futuro visualmente distintos; medir memória | Testes de falha, custo, segurança e atualização |
| 6. Avaliação | Compreensão e comunicação de risco | O6 com as condições definidas em R4; medir confiança excessiva | Procedimentos éticos aplicáveis e protocolo revisado |
| 7. Publicação | Liberação gradual | Público só com o que o enquadramento permitir | Governança, evidências e monitoramento |

### 6.1 Calendário indicativo

| Período | Etapas |
| --- | --- |
| nov–dez/2026 | Etapa 0; congelamento da versão histórica mantido como entrega segura |
| até 31/03/2027 | Etapas 1 a 3 (Relatório Parcial) |
| abr–jun/2027 | Etapas 4 e 5 |
| jul–ago/2027 | Etapa 6 (Relatório Final e Resumo Expandido até 28/08/2027) |
| depois | Etapa 7, conforme o enquadramento regulatório |

A recomendação pública provavelmente não cabe neste ciclo do PIBITI.

---

## 7. Andamento da etapa 0

| Item | Situação |
| --- | --- |
| Este plano | Criado em 07/11/2026 |
| Auditoria de [`pibiti/decisoes_orientador.md`](pibiti/decisoes_orientador.md) | Registrada em 07/11/2026; aguarda o orientador (R13) |
| Reformulação registrada em [`validacao_academica.md`](validacao_academica.md) e [`fora_do_escopo.md`](fora_do_escopo.md) | Registrada como proposta; textos vigentes preservados |
| Impacto no CEP ([`pibiti/cep/checklist_submissao_cep.md`](pibiti/cep/checklist_submissao_cep.md), seção 6) | Registrado; a revisão das minutas depende de R9 |
| Impacto nos relatórios ([`pibiti/escopo_relatorios.md`](pibiti/escopo_relatorios.md)) | Registrado como alteração em avaliação |
| Tag da versão histórica | A fazer, após R4 |
| Página "Sobre o Projeto" | Sem mudança até a confirmação (R5) |
| Consulta regulatória | A encaminhar (R2) |
