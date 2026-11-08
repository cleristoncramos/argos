# Protocolo do piloto preditivo — v1 (minuta)

**Status:** minuta para revisão do orientador · **Criado em:** 07/11/2026 · **Revisão 1:** 08/11/2026 (ajustes de alinhamento, reestimação, expurgo, preços, caixa, custos, teste estatístico, condição econômica e regra de versões; ver o histórico no fim)
**Plano de origem:** [`../plano_reformulacao_preditiva.md`](../plano_reformulacao_preditiva.md), seções 6.2 a 6.4 e 7.1.

> **Nada aqui está aprovado.** As escolhas marcadas com **[R6]**, **[R7]** ou **[R8]** dependem das decisões pendentes do bloco B do plano, e os limiares da seção 9 dependem do orientador. Os valores propostos servem para tornar o protocolo verificável e podem ser trocados antes do congelamento. As regras de mudança depois do congelamento estão na seção 11.

**Escopo.** Experimento local, fora do aplicativo, em `experiments/preditivo/`. Nenhuma previsão, sinal ou resultado deste piloto aparece na versão pública do Argos, e nenhum resultado libera recomendação pública automaticamente. As regras da camada descritiva (prompt v0.6, validador e testes de linguagem) não mudam.

---

## 1. Ativos e justificativa [R6]

| Proposta | Alternativa |
| --- | --- |
| `PETR4.SA` e `VALE3.SA`, **avaliados separadamente** | `BOVA11.SA` e `SMAL11.SA` |

**Motivos da proposta:** mesma classe (ações brasileiras), alta liquidez, histórico diário longo na fonte e presença no catálogo do Argos. A alternativa troca ações por ETFs de índice, o que reduz o risco específico de uma empresa, mas tem histórico mais curto.

**Limitação registrada desde já:** os dois ativos foram escolhidos hoje e existem até hoje (viés de sobrevivência). Os resultados valem para esses ativos e esse período; **não serão generalizados** para o mercado nem para o catálogo.

## 2. Alvo, horizonte e datas de cada amostra

O alvo é alinhado à entrada efetiva da estratégia: o modelo prevê o retorno que a posição de fato obteria.

| Evento | Data | Campo registrado |
| --- | --- | --- |
| Informação disponível e decisão | Após o fechamento de `t` | `decision_date` |
| Entrada | Fechamento de `t + 1` | `entry_date` |
| Saída ou rebalanceamento seguinte | Fechamento de `t + 21` | `label_end_date` |

| Item | Definição |
| --- | --- |
| Frequência | Diária (pregões da B3 presentes na série) |
| Horizonte | **20 intervalos entre observações** (pregões), não dias corridos |
| Alvo | `y_t = P(entry_date + 20 pregões) / P(entry_date) − 1 = P_(t+21) / P_(t+1) − 1`, com `P` a série da seção 3 |
| Unidade | Decimal (0,05 = 5%) |

**Regra de implementação.** Cada amostra guarda `decision_date`, `entry_date` e `label_end_date`, calculadas pelo calendário da própria série. Disponibilidade dos alvos, expurgo, referência de média histórica e testes usam essas datas, nunca constantes como 20 ou 21 espalhadas pelo código.

Um alvo só está **realizado** em uma data `d` se `label_end_date ≤ d`. Datas sem fechamento são descartadas antes de montar a série, como já faz `core/data_processor.py`.

## 3. Série de preços e tratamento de eventos [R8]

| Uso | Série proposta |
| --- | --- |
| Alvo, variáveis e simulação | Série com **abertura, máxima, mínima e fechamento ajustados pelo mesmo fator** (coleta com ajuste por desdobramentos e proventos aplicado a todas as colunas de preço) |
| Volume | Não usado nas variáveis deste piloto |

**Consistência obrigatória.** Todas as variáveis que combinam preços de abertura, máxima, mínima e fechamento usam a mesma base de ajuste. É vedado combinar máxima e mínima não ajustadas com fechamento ajustado sem tratamento explícito e teste correspondente. Isso afeta em especial o ATR (`core/indicators_extra.py`), que usa máxima, mínima e fechamento anterior.

**Rótulo obrigatório nos resultados:** "retorno aproximado com proventos reinvestidos, antes de impostos e de custos não modelados". Não chamar de retorno total exato: o ajuste da fonte não reproduz datas de pagamento, impostos sobre proventos nem frações de ações.

**Natureza do snapshot.** A série baixada é uma reconstrução feita pela fonte na data da coleta, com os ajustes conhecidos naquele momento. Não é uma base histórica ponto a ponto com as versões que estiveram disponíveis no passado.

**Triagem de eventos.** Na coleta, comparar o retorno diário ajustado com o não ajustado e listar as datas com diferença acima de 1 ponto percentual. A lista é só triagem: cada data é conferida manualmente contra um evento conhecido (desdobramento, grupamento ou provento). Diferença sem evento identificado interrompe o experimento (seção 10).

## 4. Variáveis disponíveis em cada data

Reaproveitar `core/features.py` (`build_feature_table`), que usa apenas dados até `t` e tem testes de truncamento, aplicado à série da seção 3:

- `ret_1`, `close_over_sma_short` (20), `close_over_sma_long` (50), `ema_spread` (12/26), `rsi` (14), `macd_hist_over_close`, `bb_percent_b`, `atr_over_close` (14), `vol_rolling` (20);
- defasagens 1, 2 e 3 de cada uma.

Acréscimos propostos, calculados só com o passado: retorno acumulado dos últimos 20 e 60 pregões e distância ao pico dos últimos 252 pregões.

**Regras:**
- antes do uso, conferir e registrar quais colunas de preço cada variável usa e se todas estão na mesma base de ajuste;
- linhas sem todas as variáveis (aquecimento) são excluídas, nunca preenchidas;
- nenhuma janela centrada e nenhum preenchimento com valor posterior a `t`;
- padronização (média e desvio) ajustada **só no treino de cada ajuste**.

## 5. Períodos [R6]

| Período | Datas propostas | Uso |
| --- | --- | --- |
| Desenvolvimento | 02/01/2008 a 30/12/2021 | Treino e validação com origem móvel (seção 6) |
| Teste final | Pregões de 2022 até a data de corte, com o embargo da seção 6 | Avaliação final do procedimento congelado |
| Data de corte | 30/10/2026 (último pregão coletado, registrado no manifesto) | Fixa para todo o piloto |

As amostras cujo `label_end_date` passa da data de corte não têm alvo realizado e ficam fora da avaliação. As datas efetivas de início de cada período, depois do aquecimento das variáveis e do embargo, são registradas no manifesto antes da execução.

O conjunto de dados é coletado uma vez e congelado, com manifesto no formato do modo demo: data da coleta, fonte, série usada e hash SHA-256 de cada arquivo. Todas as rodadas usam o mesmo manifesto.

## 6. Validação, expurgo e embargo

### 6.1 Origem móvel no desenvolvimento

Janela de treino expansível, com **reestimação no início de cada ano de avaliação**, em datas fixadas pelo calendário da série e registradas antes da execução:

| Dobra | Treino | Validação |
| --- | --- | --- |
| 1 | 2008 a 2013 | 2014 |
| 2 | 2008 a 2014 | 2015 |
| … | … | … |
| 8 | 2008 a 2020 | 2021 |

### 6.2 Regra de fronteira (vale para toda divisão)

Em cada dobra, nesta ordem:

1. definir as datas inicialmente destinadas à validação (o ano da dobra);
2. excluir os primeiros 20 pregões desse intervalo (**embargo**, regra conservadora adicional);
3. remover do treino toda amostra cujo `label_end_date` alcance ou ultrapasse a primeira data efetivamente avaliada (**expurgo**);
4. aplicar os mesmos passos às divisões internas usadas para escolher a regularização (seção 7).

O embargo **complementa** o expurgo; não o substitui.

**Teste automático obrigatório:** em todo ajuste, para toda amostra de treino, `label_end_date < primeira data avaliada`. Se falhar, o experimento para (seção 10).

### 6.3 Teste final com avaliação sequencial

O teste final segue o mesmo procedimento: ajuste inicial no começo de 2022, com todo o desenvolvimento como treino, e reestimação no início de 2023, 2024, 2025 e 2026, com o procedimento de escolha de hiperparâmetros já fixado.

Durante o teste final, a reestimação pode usar observações anteriores à data do ajuste, inclusive do período de teste já transcorrido, **desde que seus alvos estejam integralmente realizados** (`label_end_date` antes da data do ajuste, com a regra de fronteira da seção 6.2).

É proibido usar dados futuros, alvos ainda não realizados ou resultados agregados do teste final para modificar o procedimento, selecionar variáveis, escolher estratégias ou alterar hiperparâmetros fora do procedimento fixado.

**"O teste final é usado uma única vez"** significa uma execução final do procedimento congelado, não um único ajuste de modelo.

## 7. Referências e modelo candidato

| Papel | Modelo | Detalhe |
| --- | --- | --- |
| Referência obrigatória | Retorno zero | `ŷ = 0` em toda data |
| Referência auxiliar | Média histórica expansível | Média dos alvos com `label_end_date ≤ decision_date` |
| Candidato | Regressão regularizada (Ridge) | Variáveis padronizadas no treino; `alpha` na grade fixa 0,1; 1; 10; 100; 1000 |

**Escolha do `alpha` em cada ajuste:** três divisões internas sequenciais, com os três últimos anos completos do treino como validações internas anuais. Aplica-se a regra de fronteira da seção 6.2 (embargo e expurgo pelas datas). O critério de escolha é o menor erro quadrático médio nas três validações internas. Empate: o maior `alpha`.

**Expansão:** um modelo de árvores (gradient boosting) só entra numa rodada nova, registrada como tal, e não reabre o teste final (seção 11).

**Bibliotecas:** scikit-learn só no ambiente de `experiments/preditivo/` (arquivo de dependências próprio). O `requirements.txt` do aplicativo não muda neste piloto.

## 8. Estratégia, caixa e custos [R7]

### 8.1 Regra

| Item | Proposta |
| --- | --- |
| Regra de entrada | Ficar **exposto** se `ŷ > r̂_caixa + c`; senão, ficar **em caixa** |
| `r̂_caixa` | Estimativa do retorno do caixa no horizonte, só com informação disponível na decisão: o CDI diário da `decision_date`, mantido constante por 20 pregões, `(1 + CDI_d)^20 − 1` |
| `c` | Custo de ida e volta da premissa-base (seção 8.3) |
| Frequência de decisão | A cada 20 pregões, em datas fixas, com execução no fechamento seguinte (`entry_date`) |
| Restrições | Sem venda a descoberto, sem alavancagem, um ativo por vez |

### 8.2 Caixa

- O **CDI efetivamente realizado** remunera o caixa no cálculo retrospectivo do patrimônio. O CDI futuro nunca entra na decisão.
- Fonte: Banco Central, série SGS 12 (CDI diário, em **% ao dia**). Converter para decimal (dividir por 100) antes de compor.
- O CDI é uma referência hipotética de remuneração do caixa, não a promessa de um produto sem custos que entregaria exatamente essa taxa.
- A série é coletada e congelada com o mesmo manifesto dos preços.

### 8.3 Custos

| Item | Definição |
| --- | --- |
| Custo por lado executado (base) | 0,05% de negociação + 0,05% de slippage = **0,10%** |
| Custo aproximado de ida e volta | **0,20%**, antes dos efeitos de composição |
| Permanecer exposto entre decisões | Não gera venda e recompra fictícias |
| Entrar | Custo de compra |
| Sair | Custo de venda |
| Comprar e manter | Custo de compra na entrada e de venda no encerramento |
| Encerramento final | Todas as estratégias encerram na data de corte com custo de venda, se expostas |
| Sensibilidade (por lado) | 0%; 0,05%; **0,10% (base)**; **0,20% (dobro da base)**; 0,30% |

### 8.4 Comparações

Comprar e manter o ativo; ficar só em caixa; a mesma regra usando a referência de retorno zero (que fica em caixa sempre que o CDI estimado mais o custo for positivo). Impostos não são modelados; os resultados são rotulados "antes de impostos".

Os dois experimentos de aporte do plano (capital disponível desde o início e dinheiro recebido ao longo do tempo) ficam para a rodada seguinte, com especificação própria.

## 9. Métricas e condições de habilitação

### 9.1 Métricas registradas (todas, sempre)

| Objeto | Métricas |
| --- | --- |
| Previsão | MAE e RMSE do candidato e das referências; razão RMSE candidato / RMSE retorno zero; R² fora da amostra em relação ao retorno zero (`1 − SSE_candidato / SSE_zero`) |
| Direção | Acurácia balanceada do sinal de `ŷ`, calculada só nas datas de decisão (sem sobreposição) |
| Estratégia | Retorno líquido acumulado e anualizado, volatilidade, **magnitude** do drawdown máximo (valor positivo), número de trocas e percentual do tempo exposto |
| Estabilidade | R² fora da amostra em cada dobra do desenvolvimento |

### 9.2 Teste estatístico (pendente de nota metodológica)

A comparação entre o candidato e o retorno zero é de **modelos aninhados**: o retorno zero corresponde ao candidato com todos os coeficientes nulos. Para esse caso, a literatura distingue o teste de Diebold-Mariano do procedimento de Clark-West, que corrige o viés do erro quadrático do modelo maior sob a hipótese nula.

Antes de congelar o protocolo, uma nota metodológica curta (`docs/preditivo/nota_teste_estatistico.md`) fixará:

| Item | Proposta inicial a justificar na nota |
| --- | --- |
| Teste | Clark-West, por se tratar de comparação aninhada |
| Perda | Erro quadrático |
| Diferencial | Perda do retorno zero menos perda ajustada do candidato |
| Hipótese | Unilateral: o candidato tem menor erro quadrático esperado |
| Variância | HAC de Newey-West com 19 defasagens, por causa da sobreposição dos alvos |
| Casos não calculáveis | Variância nula ou amostra insuficiente: critério registrado como "não calculável" e tratado como não atendido |

O limiar **p < 0,10** é exploratório, escolhido para este piloto, e não é garantia de que a estratégia funcionará no futuro. Enquanto a nota não for aprovada, o critério 2 da seção 9.3 não pode ser usado.

### 9.3 Critérios de elegibilidade, definidos antes da avaliação final (proposta)

Avaliados **por ativo**, no teste final. O sinal só pode ser habilitado no ambiente experimental se **todos** forem atendidos:

1. R² fora da amostra maior que zero (o candidato erra menos que o retorno zero);
2. teste da seção 9.2 com p < 0,10 a favor do candidato;
3. R² fora da amostra maior que zero em pelo menos 5 das 8 dobras do desenvolvimento;
4. **condição econômica**, com o custo-base:
   - **(A)** retorno líquido da estratégia > retorno do caixa **E** magnitude do drawdown máximo da estratégia < magnitude do drawdown máximo de comprar e manter;
   - **OU (B)** retorno líquido da estratégia > retorno de comprar e manter **E** magnitude do drawdown máximo da estratégia ≤ magnitude do drawdown máximo de comprar e manter + 5 pontos percentuais (limite de risco proposto para este ramo);
5. a condição 4 continua atendida com o custo por lado de 0,20% (dobro da base).

São critérios de pesquisa propostos para este piloto, não padrões universais de investimento.

Se algum critério falhar, o sistema registra e, numa eventual tela experimental, informa: **"não houve evidência suficiente para habilitar o sinal"**, mostrando a comparação. Esse resultado conclui o experimento cientificamente (plano, seção 6.3).

## 10. Registro de experimentos e critérios de interrupção

**Registro.** Cada execução grava uma linha em `experiments/preditivo/registro.jsonl` com:
- data e hora (Brasília) e commit do código;
- hash do manifesto de dados e da configuração;
- ativo, modelo, hiperparâmetros e ajuste;
- métricas e se a execução foi a avaliação final.

Configurações rejeitadas ficam registradas e entram no relatório. A primeira execução da avaliação final marca o teste final como **usado**.

**Interromper e corrigir antes de seguir quando:**
- o teste de fronteira da seção 6.2 falhar;
- a coleta tiver lacunas não explicadas, ou a triagem da seção 3 mostrar diferença sem evento identificado;
- alguma variável combinar preços de bases de ajuste diferentes;
- algum ajuste usar amostra com alvo não realizado na data do ajuste, ou dados posteriores a ela.

**Se um vazamento for descoberto depois da avaliação final:** registrar o ocorrido, corrigir e reportar os resultados como comprometidos. O teste final não é refeito com novos dados escolhidos depois.

## 11. Versões e mudanças

- **Mudanças substantivas** em dados, alvos, variáveis, divisões temporais, modelos, estratégia, métricas ou critérios de elegibilidade exigem nova versão do protocolo.
- Depois de consultados os resultados finais, uma mudança substantiva **não permite reutilizar o mesmo teste** como evidência confirmatória independente. Os resultados anteriores permanecem registrados.
- Pesquisas feitas depois do primeiro teste são identificadas como **exploratórias** ou avaliadas prospectivamente em dados novos, posteriores à data de corte.
- **Correções editoriais ou documentais** que não alterem o experimento entram no histórico abaixo, sem invalidar a execução.

---

## Pendências antes de congelar

| Item | Depende de |
| --- | --- |
| Ativos, horizonte e datas (seções 1, 2 e 5) | R6 |
| Estratégia, caixa e custos (seção 8) | R7 |
| Série de preços e consistência das colunas (seções 3 e 4) | R8 |
| Nota metodológica do teste estatístico (seção 9.2) | Desenvolvedor, com aprovação do orientador |
| Limiares de elegibilidade, inclusive o limite de risco do ramo B (seção 9.3) | Orientador |
| Coleta do CDI e conferência dos termos de uso das fontes | Desenvolvedor |

## Histórico

| Data | Versão | Mudança |
| --- | --- | --- |
| 07/11/2026 | v1, minuta | Primeira redação |
| 08/11/2026 | v1, minuta, revisão 1 | Alvo alinhado à entrada em `t + 1` e datas por amostra; reestimação sequencial no teste final com alvos realizados; embargo e expurgo separados e aplicados também às divisões internas; reestimação no início de cada ano; preços de abertura, máxima, mínima e fechamento na mesma base de ajuste e natureza do snapshot; regra de entrada contra o caixa estimado sem usar o CDI futuro; custos por lado; teste estatístico condicionado a nota metodológica (comparação aninhada); condição econômica com parênteses, magnitude do drawdown e limite de risco no ramo B; regra de versões substantivas e editoriais |
