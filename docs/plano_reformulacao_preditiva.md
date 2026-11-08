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
| N07: sem regressão nem detecção de cruzamentos | Permanece vigente na camada histórica. Na camada experimental, propõe-se autorizar regressão como método preditivo, quando prevista no protocolo do piloto. Detecção de cruzamentos não fica automaticamente autorizada: só entra se houver uma estratégia específica, definida e avaliada antes | A confirmar |
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
| R4 | Congelar em fevereiro de 2027 apenas a versão histórica, e se o O6 avaliará a versão histórica, a experimental ou ambas (decidir em novembro de 2026) | Orientador |
| R5 | Texto final da pergunta e dos objetivos, e como o Relatório Parcial registra a mudança de escopo | Orientador |
| R6 | Piloto: ativos, horizonte (ex.: 20 pregões), alvo (retorno acumulado simples ou logarítmico) e modelos | Orientador |
| R7 | Estratégia do piloto (ex.: exposto ou fora do mercado), custos e remuneração do caixa (ex.: CDI) | Orientador |
| R8 | Usar preço ajustado por proventos no piloto | Orientador |
| R9 | CEP: submeter o protocolo atual e emendar depois, ou revisar antes da submissão | Orientador e CEP |
| R10 | LLM no ambiente experimental: chamadas ao modelo ou só respostas salvas, e orçamento | Orientador |
| R11 | API separada (o documento a considera opcional) | Orientador |
| R12 | Relação com o TCC "Previsão de Riscos Financeiros" (Lorrana Evelyn de Araújo Pereira), que prevê volatilidade; o piloto proposto prevê retorno | Orientador e autora |
| R13 | Confirmar quais registros de [`pibiti/decisoes_orientador.md`](pibiti/decisoes_orientador.md) têm evidência original (seção "Auditoria de 07/11/2026" daquele arquivo) | Orientador |

**Atualização de 08/11/2026:** R6, R7 e R8 foram decididos pelo orientador, junto com os critérios de elegibilidade do piloto. Detalhes em [`pibiti/decisoes_orientador.md`](pibiti/decisoes_orientador.md) (entrada de 08/11/2026) e no protocolo consolidado. A confirmação original ainda precisa ser arquivada.

As decisões não precisam bloquear todas as atividades ao mesmo tempo:

| Bloco | Decisões | O que libera |
| --- | --- | --- |
| A — Direção e governança | R1, R2, R3, R4, R5, R9 e R13 | Formalização do escopo, preservação da versão histórica e encaminhamento ético e regulatório |
| B — Piloto quantitativo | R6, R7 e R8 | Conjunto de dados, alvos, modelos e backtest local |
| C — Integração e colaboração | R10, R11 e R12 | LLM experimental, implantação e divisão entre trabalhos |

As decisões do bloco C podem amadurecer enquanto o experimento local avança, desde que não haja publicação nem coleta antecipadas.

---

## 6. Plano de execução por etapas

"Documento" resume a sugestão do documento de 07/11/2026; "Complemento" são acréscimos propostos pelo desenvolvedor, também sujeitos a confirmação.

| Etapa | Documento | Complemento | Condição de passagem |
| --- | --- | --- | --- |
| 0. Revisão de escopo | Nova pergunta, arquitetura confirmada, estratégia de publicação | Este plano; auditoria das decisões; tag da versão histórica; revisão das minutas do CEP; atualização de `validacao_academica.md` e `fora_do_escopo.md`; regras por camada (seção 4) | Confirmação escrita do orientador e encaminhamento da revisão regulatória |
| 1. Experimento local | Poucos ativos, alvo e referência definidos | Em `experiments/`, fora do app. Usar a série de preços definida em R8, documentando o tratamento de desdobramentos e proventos e sua compatibilidade com o cálculo de retorno e o backtest; distinguir a série usada para estimar retornos dos preços e fluxos usados para simular operações. Manifesto com data de corte e hash; teste automático de que nenhum rótulo cruza a fronteira entre treino e teste | Conjunto de dados reproduzível e divisões temporais verificadas |
| 2. Modelagem | Referência ingênua (retorno zero ou preço constante), ARIMA, regressão regularizada e gradient boosting ou Random Forest; LSTM só depois, se justificado | Começar pelo escopo reduzido da seção 6.2: retorno zero e regressão regularizada. Um modelo de árvores entra após a primeira avaliação; ARIMA e outros modelos depois, sem bloquear o piloto. Validação com origem móvel e intervalo entre treino e teste de pelo menos o horizonte; teste final usado uma única vez; registro dos modelos que não funcionaram; intervalo preditivo avaliado por cobertura; probabilidade só com modelo calibrado (Brier) | Relatório fora da amostra, com limitações (ver seção 6.3) |
| 3. Estratégia | Regra transparente, custos, comparação; backtest sem vazamento nem seleção retroativa | Os dois experimentos de aporte; caixa remunerado; custos e slippage configuráveis. Controle de múltiplos testes conforme a seção 6.4 | Backtest documentado, inclusive regras rejeitadas (ver seção 6.3) |
| 4. LLM | Novo contexto, prompt e validação | Família `v1.0-experimental`; validador de autorização e fidelidade; rubrica com comunicação da incerteza; v0.6 intacta | Explicações fiéis, sem números ou sinais inventados |
| 5. Integração | Inferência por API e interface experimental | Começar sem API: inferência no app a partir do modelo registrado, atrás de um interruptor; histórico e futuro visualmente distintos; medir memória | Testes de falha, custo, segurança e atualização |
| 6. Avaliação | Compreensão e comunicação de risco | O6 com as condições definidas em R4; medir confiança excessiva | Procedimentos éticos aplicáveis e protocolo revisado |
| 7. Publicação | Liberação gradual | Público só com o que o enquadramento permitir | Governança, evidências e monitoramento |

### 6.1 Calendário indicativo

A tag de referência de novembro não equivale ao congelamento final da entrega histórica.

| Período | Marco ou etapa |
| --- | --- |
| nov/2026 | Etapa 0; tag de referência da versão histórica atual; decisão sobre qual versão o O6 avaliará (R4) |
| nov–dez/2026 | Correções da versão histórica; documentos éticos preparados conforme a decisão do O6 |
| jan/2027 | Snapshot final e testes sem internet da versão histórica |
| fev/2027 | Congelamento formal da entrega histórica |
| até 31/03/2027 | Etapas 1 a 3 (Relatório Parcial) |
| abr–jun/2027 | Etapas 4 e 5; coleta do O6, se aprovada, com meta de conclusão até junho ou início de julho |
| jul/2027 | Análise dos resultados do O6 |
| ago/2027 | Consolidação e redação (Relatório Final e Resumo Expandido até 28/08/2027) |
| depois | Etapa 7, conforme o enquadramento regulatório |

Se a versão experimental não estiver pronta a tempo da coleta, o O6 pode avaliar a versão histórica, sem apresentar os resultados como validação da função preditiva.

A recomendação pública não integra a entrega mínima deste ciclo. Sua eventual disponibilização dependerá dos resultados quantitativos, da avaliação de riscos e do enquadramento institucional e regulatório, sem compromisso de prazo neste plano.

### 6.2 Escopo inicial do piloto (R6, R7 e R8 decididos em 08/11/2026)

Um recorte pequeno permite verificar primeiro a integridade dos dados, dos alvos e da avaliação.

| Elemento | Escopo inicial |
| --- | --- |
| Ativos | `PETR4.SA` e `VALE3.SA`, avaliados separadamente |
| Frequência | Diária |
| Horizonte | 20 observações futuras (pregões) |
| Alvo | Retorno simples entre a entrada (fechamento de `t + 1`) e o fechamento de `t + 21` |
| Referência | Retorno zero |
| Modelo candidato | Regressão regularizada |
| Expansão | Um modelo de árvores após a primeira avaliação |
| Estratégia | Exposto se a previsão superar o custo de ida e volta (0,20%), senão em caixa (CDI); sem venda a descoberto e sem alavancagem |

### 6.3 Conclusão científica e habilitação operacional

**Conclusão científica.** O experimento é considerado concluído quando seu protocolo, resultados e limitações estão documentados, inclusive quando o modelo não supera a referência.

**Habilitação operacional.** Previsões ou sinais só serão disponibilizados no ambiente experimental quando atenderem aos critérios de elegibilidade definidos **antes** da avaliação final. Os limiares ficam no protocolo do piloto e não podem ser escolhidos depois de conhecidos os resultados.

Se o modelo não atender aos critérios, o sistema exibirá a comparação experimental e informará a ausência de evidência suficiente para habilitar o sinal.

### 6.4 Controle de múltiplos testes no piloto

- Registrar previamente a estratégia, os limiares e as variantes permitidas.
- Manter um registro de todas as configurações testadas.
- Selecionar configurações apenas no conjunto de desenvolvimento.
- Não escolher a estratégia com base no teste final.
- Métodos adicionais de ajuste para múltiplos testes serão especificados se houver exploração de muitas regras ou configurações.

---

## 7. Andamento da etapa 0

| Item | Situação |
| --- | --- |
| Este plano | Criado em 07/11/2026 |
| Auditoria de [`pibiti/decisoes_orientador.md`](pibiti/decisoes_orientador.md) | Registrada em 07/11/2026; aguarda o orientador (R13) |
| Reformulação registrada em [`validacao_academica.md`](validacao_academica.md) e [`fora_do_escopo.md`](fora_do_escopo.md) | Registrada como proposta; textos vigentes preservados |
| Impacto no CEP ([`pibiti/cep/checklist_submissao_cep.md`](pibiti/cep/checklist_submissao_cep.md), seção 6) | Registrado; a revisão das minutas depende de R9 |
| Impacto nos relatórios ([`pibiti/escopo_relatorios.md`](pibiti/escopo_relatorios.md)) | Registrado como alteração em avaliação |
| Tag de referência da versão histórica atual | A fazer em novembro de 2026 (não equivale ao congelamento de fevereiro) |
| Página "Sobre o Projeto" | Sem mudança até a confirmação (R5) |
| Consulta regulatória | A encaminhar (R2) |
| Ajustes da revisão de 07/11/2026 (N07, piloto reduzido, habilitação, preços, múltiplos testes, calendário, blocos de decisão) | Incorporados |
| Protocolo do piloto | Consolidado em 08/11/2026 com a decisão sobre R6, R7, R8 e critérios; a avaliação final depende das condições da seção 12 do protocolo |

### 7.1 Próximo artefato

Antes de mudar o prompt v0.6 ou os testes que impedem recomendação na aplicação histórica, redigir uma especificação curta do piloto. **Minuta redigida em 07/11/2026:** [`preditivo/protocolo_piloto_v1.md`](preditivo/protocolo_piloto_v1.md), com:

1. ativos e justificativa;
2. alvo e horizonte;
3. série de preços e tratamento de eventos;
4. variáveis disponíveis em cada data;
5. datas de treino, validação e teste;
6. tratamento da sobreposição dos alvos;
7. referência e modelo candidato;
8. estratégia e custos;
9. métricas e condições de habilitação (seção 6.3);
10. registro de experimentos e critérios de interrupção.

A nova LLM entra depois, para explicar resultados efetivamente produzidos, inclusive a conclusão "não houve evidência suficiente". O projeto não depende de encontrar uma estratégia vencedora para ser bem-sucedido.

### 7.2 Atualização — 08/11/2026

O piloto foi implementado em `experiments/preditivo/`, com dependências próprias e a avaliação final bloqueada. Os testes do piloto e os 929 testes do aplicativo foram aprovados; os resultados ficam vinculados ao commit correspondente.

O ensaio preliminar usou dados reais, sem constituir coleta oficial nem abertura da avaliação final.

No desenvolvimento preliminar, os dois ativos tiveram R² positivo em três das oito dobras. Se confirmado na rodada oficial, o resultado não atende ao critério 3 de elegibilidade. Nesse caso, nenhum dos ativos pode ser declarado elegível pela regra atual, e um bom resultado no período final não compensa essa falha. A orientação é manter a v1, concluir a rodada oficial do desenvolvimento e registrar o resultado, sem alterar grade, variáveis ou limiares para buscar elegibilidade.

O `alpha` selecionado atingiu com frequência o limite superior da grade (1000). Isso indica regularização forte, não necessariamente previsões próximas de zero: com intercepto, a redução dos coeficientes aproxima as previsões de uma constante ligada à média do alvo no treino. O registro de cada ajuste passou a incluir a frequência de seleção de cada `alpha`, a média e o desvio das previsões, a média do alvo no treino e a configuração do intercepto. A grade não é ampliada nesta versão.

A ocorrência de PETR4 em 02/04/2014 permanece **em investigação**. A conferência na mesma base de ajuste mostrou que a faixa também é violada na base bruta da fonte (fechamento 15,56 abaixo da mínima 15,70) e que a série ajustada usada no piloto coincide com a reconstrução pelo fator `a_t = Adj Close / Close`. Também foi citada uma variação do fator entre 02/04 e 03/04/2014 sem provento registrado; **essa afirmação foi corrigida** no relatório do snapshot oficial: há provento de 0,99757 em 03/04/2014 na fonte, que explica a variação exatamente. Antes de classificar a ocorrência da faixa, investigar a integridade desse registro.

Permanecem pendentes: a confirmação da formalização do embargo nas reestimações, a coleta oficial, a investigação das ocorrências e a decisão sobre a finalidade do período final (seção 12 do protocolo).

Nenhum resultado preliminar autoriza habilitação de sinais ou abertura automática da avaliação final.

### 7.3 Coleta oficial — snapshot do piloto

A coleta oficial do piloto usa a data de corte de 30/10/2026 e preserva os dados retornados pelas fontes, sem correções automáticas. A data da coleta é a data real de execução, distinta da data de corte dos preços.

O congelamento do snapshot não equivale à aprovação de integridade para a modelagem, ao congelamento da configuração nem à autorização de abertura da avaliação final.

A ocorrência de PETR4 em 02/04/2014 e as demais verificações são registradas no manifesto. Qualquer tratamento posterior é documentado sem sobrescrever os arquivos originais. A decisão sobre manter, corrigir ou excluir a observação, e quais amostras isso afeta, é tomada antes da rodada oficial do desenvolvimento. Se a coleta oficial retornar valores diferentes dos observados no ensaio, a diferença é registrada; não se escolhe a versão mais conveniente.

Sequência a partir daqui: snapshot congelado → investigação e decisão sobre integridade → confirmação do embargo → configuração consolidada → desenvolvimento oficial → decisão sobre encerrar a v1 ou abrir o período final.

A avaliação final permanece bloqueada.

**Resultado (08/11/2026):** snapshot `snap-20261108-01` coletado e congelado, com verificação de integridade com pendência. Identificação, hashes, cobertura, contagens e pendências em [`preditivo/snapshot_snap-20261108-01.md`](preditivo/snapshot_snap-20261108-01.md).

**Atualização (08/11/2026, tarde):** cópia de segurança feita e conferida; árvore alterada aceita como desvio documental, com evidência arquivada; embargo nas reestimações confirmado pelo orientador. A conferência externa pela B3 encontrou fonte verificável para as três ocorrências e identificou os campos divergentes (fechamento na PETR4; máxima e mínima na VALE3). A política foi implementada com os dois tratamentos possíveis, e a escolha entre eles (decisão P1) precede o desenvolvimento oficial. Detalhes no [relatório do snapshot](preditivo/snapshot_snap-20261108-01.md), seção 6.

**Atualização (08/11/2026, P1):** o orientador aprovou a substituição pontual pelos valores da B3, na visão derivada. As condições foram cumpridas: registros exatos identificados, base de cotação compatível, método de ajuste reproduzível e fator da PETR4 recalculado com o fechamento corrigido. O impacto final é de zero amostras perdidas. Política versão 1.0 com hash registrado. O desenvolvimento oficial está autorizado; a avaliação final segue bloqueada.

**Desenvolvimento oficial (08/11/2026):** concluído com a política 1.0 e o snapshot congelado. Os dois ativos tiveram R² positivo em 3 das 8 dobras (PETR4: 2015, 2020 e 2021; VALE3: 2018, 2019 e 2020); o critério 3 não é atendido, e a v1 não pode habilitar sinal. Relatório em [`preditivo/desenvolvimento_oficial_v1.md`](preditivo/desenvolvimento_oficial_v1.md). Próxima decisão: encerrar a v1 ou abrir o período final só para completar o estudo. A avaliação final segue bloqueada.

**Encerramento da v1 (08/11/2026, D1):** o orientador encerrou a v1 por não elegibilidade, sem executar a avaliação final. Resultado oficial: não houve evidência suficiente, segundo os critérios do protocolo v1, para habilitar o sinal; a conclusão vale para essa configuração e não se generaliza. O período final fica reservado para uma eventual v2, sob protocolo fechado antes da avaliação. A linha preditiva continua: a próxima atividade é uma proposta documental e delimitada de v2. Detalhes em [`preditivo/encerramento_v1.md`](preditivo/encerramento_v1.md).

**Proposta da v2 (08/11/2026):** documento em [`preditivo/proposta_piloto_v2.md`](preditivo/proposta_piloto_v2.md). A mudança principal é a grade de `alpha` ampliada até 10⁶, porque a v1 escolheu o limite superior em 14 de 16 ajustes. Como a média histórica superou o retorno zero em 6 de 8 dobras da v1, a proposta acrescenta o critério 6, de ganho sobre a média histórica, para impedir uma aprovação só por convergência à média. Aguarda as decisões V2-1 a V2-7; nada da v2 foi implementado ou executado.

**Protocolo v2 (08/11/2026):** o orientador aprovou a v2 (V2-1 a V2-7): grade até 10⁶ com limite fixo, critério 6 obrigatório contra a média histórica causal, Diebold-Mariano contra a média só como diagnóstico e declaração de não independência do desenvolvimento. Protocolo consolidado em [`preditivo/protocolo_piloto_v2.md`](preditivo/protocolo_piloto_v2.md). A implementação começa só depois da confirmação real; o período final continua sem uso para avaliação preditiva ou seleção de modelos.
