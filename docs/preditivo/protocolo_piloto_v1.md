# Protocolo do piloto preditivo — v1 (consolidado)

**Status:** consolidado com a decisão do orientador de 08/11/2026 sobre R6, R7, R8 e os critérios de elegibilidade · **Congelamento:** só depois das condições da seção 12 · **Criado em:** 07/11/2026 · **Revisões:** 08/11/2026 (ver o histórico no fim)
**Plano de origem:** [`../plano_reformulacao_preditiva.md`](../plano_reformulacao_preditiva.md), seções 6.2 a 6.4 e 7.1. **Decisão:** [`../pibiti/decisoes_orientador.md`](../pibiti/decisoes_orientador.md), entrada de 08/11/2026.

> **Alcance da aprovação.** A decisão de 08/11/2026 autoriza a preparação, a implementação e a execução do piloto quantitativo **local**. Ela não autoriza a integração ao aplicativo público e não significa que modelos ou sinais estão validados. A avaliação final só pode ser aberta depois das condições da seção 12, entre elas registrar a confirmação original da decisão.

**Escopo.** Experimento local, fora do aplicativo, em `experiments/preditivo/`. Nenhuma previsão, sinal ou resultado deste piloto aparece na versão pública do Argos, e nenhum resultado libera recomendação pública. As regras da camada descritiva (prompt v0.6, validador e testes de linguagem) não mudam.

---

## 1. Ativos (R6, aprovado)

| Ativo | Avaliação |
| --- | --- |
| `PETR4.SA` | Treinamento, previsões, métricas, backtest e elegibilidade próprios |
| `VALE3.SA` | Treinamento, previsões, métricas, backtest e elegibilidade próprios |

- A elegibilidade de um ativo não autoriza o sinal do outro.
- Os resultados não serão generalizados para o catálogo do Argos nem para o mercado. Os dois ativos foram escolhidos hoje e existem até hoje (viés de sobrevivência).
- A alternativa `BOVA11.SA` e `SMAL11.SA` fica reservada para uma rodada futura. Trocar os ativos depois de conhecidos os resultados finais exige outro experimento, sem apagar o resultado deste piloto.

## 2. Alvo, horizonte e datas de cada amostra (R6, aprovado)

O alvo é alinhado à entrada simulada: o modelo é avaliado sobre o retorno que a posição de fato obteria.

| Evento | Definição | Campo registrado |
| --- | --- | --- |
| Informação disponível | Dados conhecidos até o fechamento de `t` | — |
| Decisão | Após o fechamento de `t` | `decision_date` |
| Entrada simulada | Fechamento de `t + 1` | `entry_date` |
| Saída ou próximo rebalanceamento | Fechamento de `t + 21` | `label_end_date` |

| Item | Definição |
| --- | --- |
| Frequência | Diária, com as observações válidas da série e o calendário registrado no conjunto de dados |
| Horizonte | **20 intervalos entre observações**, não 20 dias corridos |
| Alvo | `y_t = P_(t+21) / P_(t+1) − 1` (retorno entre a entrada e a saída), com `P` o fechamento ajustado da seção 3 |
| Unidade | Decimal (0,05 = 5%) |

Esta definição substitui a fórmula original `P_(t+20) / P_t − 1`.

**Regra de implementação.** Cada amostra guarda `decision_date`, `entry_date` e `label_end_date`, calculadas pelo calendário da própria série. Disponibilidade dos alvos, exclusão das últimas amostras, expurgo, referência de média histórica e testes usam essas datas, não uma quantidade fixa de linhas.

Um alvo só está **realizado** em uma data `d` se `label_end_date ≤ d`. Datas sem fechamento são descartadas antes de montar a série, como já faz `core/data_processor.py`.

## 3. Série de preços e tratamento de eventos (R8, aprovado)

**Fechamento ajustado** (desdobramentos e proventos, conforme a fonte) para:
- construção do alvo;
- variáveis de retorno;
- variáveis de nível;
- aproximação do desempenho da estratégia.

**Consistência de ajuste.** Variáveis que usam abertura, máxima ou mínima precisam de todos os preços na mesma base de ajuste do fechamento. É vedado combinar, mesmo por descuido, máxima e mínima não ajustadas com fechamento ajustado. Isso afeta em especial o ATR (`core/indicators_extra.py`), que usa máxima, mínima e fechamento anterior. O volume não é usado nas variáveis deste piloto.

**Descrição obrigatória dos resultados:**

> "Retorno aproximado com ajustes da fonte para proventos e desdobramentos, antes de impostos e de custos não modelados."

O resultado não é apresentado como reprodução exata dos fluxos financeiros de uma carteira real.

**Natureza do snapshot.** A série baixada é uma reconstrução feita pela fonte na data da coleta, com os ajustes conhecidos naquele momento, não uma base histórica ponto a ponto. Essa limitação e qualquer revisão posterior da fonte constam no relatório.

**Triagem de diferenças entre retorno de preço e retorno ajustado por proventos.** Na coleta, comparar o retorno diário ajustado com o de preço e listar as datas com diferença acima de 1 ponto percentual. Na fonte, os preços "sem ajuste" já vêm corrigidos por desdobramentos, então essa triagem aponta proventos e **não** é detector de desdobramentos; os desdobramentos e grupamentos informados pela fonte são registrados separadamente. Cada diferença relevante é investigada e documentada, sem atribuir causa apenas pelo tamanho da variação.

**Conferência de abertura, máxima, mínima e fechamento.** A faixa mínima ≤ abertura, fechamento ≤ máxima é conferida em bases comparáveis: na base bruta da fonte e na base ajustada reconstruída com o fator `a_t = Adj Close / Close` aplicado às quatro colunas, que também é comparada com a série usada no piloto. Também são listadas as datas em que o fator muda sem provento nem desdobramento registrado. Ocorrências ficam "em investigação" e não são corrigidas automaticamente.

**Congelamento.** A coleta é congelada com manifesto (data, fonte, série usada e hash SHA-256 de cada arquivo), no formato do modo demo. Todas as rodadas usam o mesmo manifesto.

## 4. Variáveis disponíveis em cada data

Reaproveitar `core/features.py` (`build_feature_table`), que usa apenas dados até `t` e tem testes de truncamento, aplicado à série da seção 3:

- `ret_1`, `close_over_sma_short` (20), `close_over_sma_long` (50), `ema_spread` (12/26), `rsi` (14), `macd_hist_over_close`, `bb_percent_b`, `atr_over_close` (14), `vol_rolling` (20);
- defasagens 1, 2 e 3 de cada uma.

Acréscimos, calculados só com o passado: retorno acumulado dos últimos 20 e 60 pregões e distância ao pico dos últimos 252 pregões.

**Regras:**
- antes do uso, conferir e registrar quais colunas de preço cada variável usa e se todas estão na mesma base de ajuste;
- linhas sem todas as variáveis (aquecimento) são excluídas, nunca preenchidas;
- nenhuma janela centrada e nenhum preenchimento com valor posterior a `t`;
- padronização (média e desvio) ajustada **só no treino de cada ajuste**.

## 5. Períodos (R6, aprovado)

| Período | Datas |
| --- | --- |
| Desenvolvimento | 02/01/2008 a 30/12/2021 |
| Separação conservadora | 20 pregões após o desenvolvimento |
| Período final | A partir do 21º pregão de 2022 |
| Data de corte | 30/10/2026 |

As amostras cujo `label_end_date` passa da data de corte não têm alvo realizado e ficam fora da avaliação. As datas efetivamente usadas, depois de aquecimento, limpeza, embargo e disponibilidade do alvo, constam no manifesto e no relatório.

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

### 6.3 Período final com avaliação sequencial (aprovado)

Ajuste inicial no começo de 2022, com todo o desenvolvimento como treino, e reestimação no início de 2023, 2024, 2025 e 2026, com o procedimento de escolha do `alpha` já fixado.

O treinamento pode incorporar observações do período final já transcorrido, **desde que seus alvos estejam completamente realizados na data do ajuste** (com a regra de fronteira da seção 6.2). Isso não autoriza consultar o futuro.

É proibido usar dados futuros, alvos não realizados ou resultados agregados do período final para modificar o procedimento, selecionar variáveis, escolher estratégias ou alterar hiperparâmetros fora do procedimento fixado.

**"Teste final usado uma única vez"** significa executar uma única avaliação final do procedimento congelado, sem alterar escolhas com base nos resultados agregados encontrados.

**Embargo nas reestimações (confirmado pelo orientador em 08/11/2026).** O embargo de 20 pregões é aplicado nas fronteiras dos blocos de avaliação definidos neste protocolo (cada ano das dobras de desenvolvimento e o início do período final, em 2022). Nas reestimações anuais dentro de um bloco sequencial já iniciado (2023 a 2026), não há nova interrupção das previsões; o treino usa somente amostras com alvos integralmente realizados na data do ajuste (expurgo). Implementação: `EMBARGO_NAS_REESTIMACOES_FINAIS = False` em `experiments/preditivo/config.py`, coberta por teste.

## 7. Referências e modelo candidato

| Papel | Modelo | Detalhe |
| --- | --- | --- |
| Referência obrigatória | Retorno zero | `ŷ = 0` em toda data |
| Referência auxiliar | Média histórica expansível | Média dos alvos com `label_end_date ≤ decision_date` |
| Candidato | Regressão regularizada (Ridge) | Variáveis padronizadas no treino; `alpha` na grade fixa 0,1; 1; 10; 100; 1000 |

**Escolha do `alpha` em cada ajuste:** três divisões internas sequenciais, com os três últimos anos completos do treino como validações internas anuais, sob a regra de fronteira da seção 6.2 (embargo e expurgo pelas datas). Critério: menor erro quadrático médio nas três validações internas. Empate: o maior `alpha`.

**Expansão:** um modelo de árvores (gradient boosting) só entra numa rodada nova, registrada como tal, e não reabre o período final (seção 11).

**Bibliotecas:** scikit-learn só no ambiente de `experiments/preditivo/` (arquivo de dependências próprio). O `requirements.txt` do aplicativo não muda neste piloto.

## 8. Estratégia, custos e caixa (R7, aprovado)

### 8.1 Regra

| Item | Definição |
| --- | --- |
| Regra | Ficar **exposto** ao ativo se `ŷ_t > c`; senão, ficar **em caixa** |
| Limiar | `c = 0,002` (custo aproximado de ida e volta, em decimal) |
| Frequência de decisão | A cada 20 pregões, com execução no fechamento seguinte (`entry_date`) |
| Restrições | Sem venda a descoberto, sem alavancagem, cada ativo avaliado separadamente, sem sobreposição de posições dentro de cada simulação |

É uma regra de **retorno absoluto acima do custo**. Ela não afirma antecipadamente superar o CDI e não deve ser descrita como otimização do retorno excedente ao CDI. A comparação com o caixa é feita no backtest e nos critérios de elegibilidade. Uma regra que compare a previsão com uma estimativa do caixa pode ser pesquisada em versão posterior.

### 8.2 Custos

| Componente | Valor por lado executado |
| --- | --- |
| Negociação | 0,05% |
| Slippage | 0,05% |
| **Total** | **0,10%** |
| Ida e volta aproximada | 0,20% |

- Os custos incidem sobre o valor negociado.
- Permanecer exposto entre duas decisões não gera venda e recompra artificiais.
- Entrar gera custo de compra; sair gera custo de venda.
- Comprar e manter tem custo de entrada e de encerramento pela mesma convenção.
- Encerramento final: todas as estratégias encerram na data de corte com custo de venda, se expostas.

**Sensibilidade** (custo total por lado): 0%; **0,10% (cenário-base)**; **0,20% (dobro do custo-base)**; 0,30%. Os cenários são todos apresentados e não podem ser usados para escolher retrospectivamente qual resultado divulgar.

### 8.3 Caixa

- Série SGS 12 do Banco Central (CDI diário), coletada e congelada com o mesmo manifesto dos preços.
- **Unidade:** % ao dia. **Conversão:** dividir por 100. **Acumulação:** produto de `(1 + CDI_d)` nos dias em caixa.
- O CDI realizado é usado só na contabilização retrospectiva do caixa, nunca como informação futura para decidir a exposição.
- O CDI é uma referência hipotética de remuneração do caixa, não a promessa de um produto sem custos com exatamente essa taxa.
- Resultados antes de impostos, com essa limitação visível.

### 8.4 Comparações

Comprar e manter o ativo; ficar só em caixa; a mesma regra usando a referência de retorno zero (como `0 > 0,002` é falso, ela fica sempre em caixa).

Os experimentos de aporte único e aportes periódicos ficam para uma rodada posterior, com especificação própria.

## 9. Métricas e critérios de elegibilidade

### 9.1 Métricas registradas (todas, sempre)

| Objeto | Métricas |
| --- | --- |
| Previsão | MAE e RMSE do candidato e das referências; razão RMSE candidato / RMSE retorno zero; R² fora da amostra em relação ao retorno zero (`1 − SSE_candidato / SSE_zero`) |
| Direção | Acurácia balanceada do sinal de `ŷ`, calculada só nas datas de decisão (sem sobreposição) |
| Estratégia | Retorno líquido acumulado e anualizado, volatilidade, **magnitude** do drawdown máximo (valor positivo), número de trocas e percentual do tempo exposto |
| Estabilidade | R² fora da amostra em cada dobra do desenvolvimento, todas reportadas, inclusive as negativas |

### 9.2 Teste estatístico (aprovado; especificação na nota metodológica)

**Teste:** Diebold-Mariano unilateral, com `p < 0,10` **estrito** a favor do candidato, calculado em precisão completa. A especificação completa está na [nota metodológica](nota_teste_estatistico.md) (decisões N1 a N5 de 08/11/2026):
- amostra: todas as datas elegíveis do período final com alvo realizado, por ativo, fixadas em lista antes da avaliação (a mesma do R² do critério 1);
- perda quadrática e diferencial `d_t = y_t² − (y_t − ŷ_t)²`;
- p-valor pela normal padrão, sem correção de amostra pequena;
- variância de Newey-West (Bartlett) com 19 defasagens, centrada e dividida por `T`;
- mínimo operacional de 200 datas e casos "não calculáveis" (que não atendem ao critério).

O teste é um **filtro exploratório previamente especificado**. Em comparação aninhada, com Ridge, seleção temporal da regularização e reestimação sequencial, não se assume que o nível nominal de 10% corresponda exatamente à taxa efetiva de falso positivo. Não há troca de teste depois da abertura dos resultados finais. O Clark-West é apresentado só como diagnóstico complementar, sem efeito sobre a elegibilidade.

### 9.3 Critérios de elegibilidade (aprovados)

Avaliados **por ativo**, no período final. O sinal só é elegível se **todos** forem atendidos:

1. **Ganho preditivo:** R² fora da amostra **estritamente maior que zero** em relação ao retorno zero. Zero não satisfaz, e não se aplica arredondamento para converter resultado nulo ou negativo em aprovação. Se a perda total da referência for zero, o R² é "não calculável" e o critério não é atendido.
2. **Comparação estatística:** teste da seção 9.2 com `p < 0,10` (estrito, em precisão completa) a favor do candidato; "não calculável" não atende.
3. **Estabilidade:** R² fora da amostra maior que zero em pelo menos 5 das 8 dobras do desenvolvimento.
4. **Resultado econômico,** com o custo-base: **(A ∧ B) ∨ C**, onde
   - **A:** retorno líquido da estratégia superior ao do caixa;
   - **B:** magnitude do drawdown máximo da estratégia inferior à de comprar e manter;
   - **C:** retorno líquido da estratégia superior ao de comprar e manter.

   O ramo C não comprova menor risco. Se a estratégia for elegível por esse ramo com drawdown maior, essa condição é destacada no relatório, e ela não pode ser descrita como superior em todas as dimensões. Não há limite adicional de drawdown neste piloto; a elegibilidade permite apenas investigação no ambiente experimental.
5. **Robustez ao custo:** o critério 4 continua atendido com o dobro do custo-base (0,20% por lado), executando a mesma estratégia com os mesmos sinais e calendário e alterando só o custo contabilizado. Sem novo ajuste do modelo nem seleção de limiar.

São regras internas deste piloto, não padrões universais de investimento.

### 9.4 Resultado e alcance

- Se qualquer critério falhar: **"Não houve evidência suficiente para habilitar o sinal."** Isso não é fracasso do projeto: o experimento está cientificamente concluído se executado conforme o protocolo e relatado integralmente.
- Se todos os critérios forem atendidos: o sinal pode ser considerado elegível para **integração experimental restrita**, depois da conferência do relatório e dos testes. Não há liberação automática ao público nem transferência da elegibilidade para outros ativos, modelos ou horizontes.

## 10. Registro de experimentos e critérios de interrupção

**Registro.** Cada execução grava uma linha em `experiments/preditivo/registro.jsonl` com:
- data e hora (Brasília) e commit do código;
- hash do manifesto de dados, do protocolo e da configuração;
- ativo, modelo, hiperparâmetros e ajuste;
- métricas e se a execução foi a avaliação final.

Configurações rejeitadas ficam registradas e entram no relatório. A primeira execução da avaliação final marca o período final como **usado**.

**Interromper e corrigir antes de seguir quando:**
- o teste de fronteira da seção 6.2 falhar;
- a coleta tiver lacunas não explicadas, ou a triagem da seção 3 tiver diferença relevante ainda não investigada;
- alguma variável combinar preços de bases de ajuste diferentes;
- algum ajuste usar amostra com alvo não realizado na data do ajuste, ou dados posteriores a ela.

**Se um vazamento for descoberto depois da avaliação final:** registrar o ocorrido, corrigir e reportar os resultados como comprometidos. O período final não é refeito com novos dados escolhidos depois.

## 11. Versões e mudanças

- **Mudanças substantivas** em dados, alvos, variáveis, divisões temporais, modelos, estratégia, métricas ou critérios de elegibilidade exigem nova versão do protocolo.
- Depois de consultados os resultados finais, uma mudança substantiva **não permite reutilizar o mesmo período** como evidência confirmatória independente. Os resultados anteriores permanecem registrados.
- Pesquisas feitas depois da avaliação final são identificadas como **exploratórias** ou avaliadas prospectivamente em dados novos, posteriores à data de corte.
- **Correções editoriais ou documentais** que não alterem o experimento entram no histórico abaixo, sem invalidar a execução.

## 12. Condições para abrir a avaliação final

A implementação local pode avançar enquanto estes itens são preparados. O período final só é aberto com todos atendidos:

| # | Condição | Situação |
| --- | --- | --- |
| 1 | Incorporar as decisões de 08/11/2026 ao protocolo | **Feito** (esta versão) |
| 2 | Registrar a versão consolidada e seu hash SHA-256 | Pendente: no congelamento, em `experiments/preditivo/` e no registro de decisões |
| 3 | Congelar os dados (manifesto com hashes) e a configuração | Pendente |
| 4 | Testar o alinhamento entre `decision_date`, `entry_date` e `label_end_date` | Testes implementados e aprovados em 08/11/2026 (`experiments/preditivo/tests`); confirmar com os dados congelados |
| 5 | Testar o expurgo nas divisões externas e internas | Testes implementados e aprovados em 08/11/2026; o teste de fronteira também roda em cada ajuste |
| 6 | Conferir custos, caixa e referências | Testes do backtest implementados e aprovados em 08/11/2026; conferência com os dados congelados pendente |
| 7 | Fechar a nota metodológica do teste estatístico (seção 9.2) | Decisões N1 a N5 aprovadas e ajustes incorporados (08/11/2026); cumprida quando a confirmação original for arquivada |
| 8 | Registrar a confirmação original da decisão (mensagem do orientador com data e remetente) | Pendente |

---

## Histórico

| Data | Versão | Mudança |
| --- | --- | --- |
| 07/11/2026 | v1, minuta | Primeira redação |
| 08/11/2026 | v1, minuta, revisão 1 | Alvo alinhado à entrada e datas por amostra; reestimação sequencial; embargo e expurgo separados, inclusive nas divisões internas; preços na mesma base de ajuste; caixa estimado na regra; custos por lado; teste estatístico condicionado a nota; condição econômica explícita; regra de versões |
| 08/11/2026 | v1, consolidada | Decisão do orientador sobre R6, R7, R8 e critérios. Regra de entrada volta a `ŷ > c` com `c = 0,002`, sem estimativa do caixa; sensibilidade em 0%, 0,10%, 0,20% e 0,30% por lado; teste de Diebold-Mariano com revisão de adequação antes da execução; ramo C sem limite adicional de drawdown, com destaque obrigatório; descrição obrigatória do resultado; condições para abrir a avaliação final (seção 12) |
| 08/11/2026 | v1, consolidada (nota) | Seção 9.2 alinhada à nota metodológica aprovada (N1 a N5): amostra em lista fixada antes, limiar estrito em precisão completa, filtro exploratório com limitação inferencial, Clark-West só diagnóstico; R² com denominador nulo "não calculável" no critério 1 |
| 08/11/2026 | v1, consolidada (implementação) | Seção 12 atualizada com os testes implementados em `experiments/preditivo/` (sem mudança no experimento) |
| 08/11/2026 | v1, consolidada (verificações) | Triagem renomeada para retorno de preço × ajustado por proventos, com desdobramentos à parte; conferência OHLC em bases comparáveis e variações do fator sem evento; formalização proposta do embargo nas reestimações do período final (a confirmar) |
| 08/11/2026 | v1, consolidada (embargo) | Formalização do embargo nas reestimações confirmada pelo orientador; política de qualidade por campo e por dependência em `experiments/preditivo/qualidade.py` e `politica_qualidade.json` (tratamento das ocorrências pendente de decisão) |
