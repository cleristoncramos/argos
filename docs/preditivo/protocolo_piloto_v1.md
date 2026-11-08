# Protocolo do piloto preditivo — v1 (minuta)

**Status:** minuta para revisão do orientador · **Criado em:** 07/11/2026
**Plano de origem:** [`../plano_reformulacao_preditiva.md`](../plano_reformulacao_preditiva.md), seções 6.2 a 6.4 e 7.1.

> **Nada aqui está aprovado.** As escolhas marcadas com **[R6]**, **[R7]** ou **[R8]** dependem das decisões pendentes do bloco B do plano. Os valores propostos servem para tornar o protocolo verificável e podem ser trocados antes do início. **Depois que a avaliação final começar, nenhum item deste protocolo pode mudar**; qualquer mudança gera uma nova versão (v2) e invalida o teste final já usado.

**Escopo.** Experimento local, fora do aplicativo, em `experiments/preditivo/`. Nenhuma previsão, sinal ou resultado deste piloto aparece na versão pública do Argos. As regras da camada descritiva (prompt v0.6, validador e testes de linguagem) não mudam.

---

## 1. Ativos e justificativa [R6]

| Proposta | Alternativa |
| --- | --- |
| `PETR4.SA` e `VALE3.SA` | `BOVA11.SA` e `SMAL11.SA` |

**Motivos da proposta:** mesma classe (ações brasileiras), alta liquidez, histórico diário longo na fonte e presença no catálogo do Argos. A alternativa troca ações por ETFs de índice, o que reduz o risco específico de uma empresa, mas tem histórico mais curto.

**Limitação registrada desde já:** os dois ativos foram escolhidos hoje e existem até hoje (viés de sobrevivência). Os resultados valem para esses ativos e esse período; **não serão generalizados** para o mercado nem para o catálogo.

## 2. Alvo e horizonte

| Item | Definição |
| --- | --- |
| Frequência | Diária (pregões da B3 presentes na série) |
| Horizonte | **h = 20 observações** (pregões), não dias corridos |
| Alvo | Retorno simples acumulado: `y_t = P_(t+20) / P_t − 1`, com `P` a série de retorno da seção 3 |
| Momento da decisão | Após o fechamento de `t`, usando só informação até `t` |
| Unidade | Decimal (0,05 = 5%) |

Datas sem fechamento são descartadas antes de montar a série, como já faz `core/data_processor.py`.

## 3. Série de preços e tratamento de eventos [R8]

| Uso | Série proposta | Motivo |
| --- | --- | --- |
| Alvo e variáveis de retorno | Fechamento ajustado por desdobramentos e proventos (`Adj Close` do Yahoo Finance) | Evita quedas artificiais na data ex e saltos em desdobramentos |
| Simulação da estratégia | A mesma série ajustada, como aproximação de retorno total **antes de impostos** | Os proventos entram como reinvestidos na data ex, conforme o ajuste da fonte |
| Variáveis de nível (médias, bandas) | Calculadas sobre a série ajustada | Coerência com o alvo |

**Rótulos obrigatórios nos resultados:** "retorno aproximado com proventos reinvestidos, antes de impostos e de custos não modelados". Não chamar de retorno total exato: o ajuste da fonte não reproduz datas de pagamento, impostos sobre proventos nem frações de ações.

**Verificação na coleta:** comparar o retorno acumulado ajustado com o não ajustado e registrar as datas com diferença diária acima de 1 ponto percentual (desdobramentos e proventos grandes), para conferência manual.

## 4. Variáveis disponíveis em cada data

Reaproveitar `core/features.py` (`build_feature_table`), que já usa apenas dados até `t` e tem testes de truncamento:

- `ret_1`, `close_over_sma_short` (20), `close_over_sma_long` (50), `ema_spread` (12/26), `rsi` (14), `macd_hist_over_close`, `bb_percent_b`, `atr_over_close` (14), `vol_rolling` (20);
- defasagens 1, 2 e 3 de cada uma.

Acréscimos propostos, calculados só com o passado: retorno acumulado dos últimos 20 e 60 pregões e distância ao pico dos últimos 252 pregões.

**Regras:**
- linhas sem todas as variáveis (aquecimento) são excluídas, nunca preenchidas;
- nenhuma janela centrada e nenhum preenchimento com valor posterior a `t`;
- padronização (média e desvio) ajustada **só no treino de cada divisão**.

## 5. Datas de desenvolvimento e de teste [R6]

| Período | Datas propostas | Uso |
| --- | --- | --- |
| Desenvolvimento | 02/01/2008 a 30/12/2021 | Treino e validação com origem móvel (seção 6) |
| Embargo | 20 pregões após o fim do desenvolvimento | Nenhuma linha usada |
| Teste final | Do 21º pregão de 2022 até a data de corte | Avaliado **uma única vez** |
| Data de corte | 30/10/2026 (último pregão coletado, registrado no manifesto) | Fixa para todo o piloto |

As últimas 20 datas antes da data de corte não têm alvo realizado e ficam fora da avaliação.

O conjunto de dados é coletado uma vez e congelado, com manifesto no formato do modo demo: data da coleta, fonte, série usada e hash SHA-256 de cada arquivo. Todas as rodadas usam o mesmo manifesto.

## 6. Validação e tratamento da sobreposição dos alvos

O alvo de `t` usa os preços até `t + 20`. Linhas vizinhas compartilham 19 dos 20 retornos, e um alvo perto de uma fronteira enxerga o período seguinte.

**Origem móvel no desenvolvimento.** Janela de treino expansível, com novo ajuste a cada 252 pregões:

| Dobra | Treino | Validação |
| --- | --- | --- |
| 1 | 2008 a 2013 | 2014 |
| 2 | 2008 a 2014 | 2015 |
| … | … | … |
| 8 | 2008 a 2020 | 2021 |

**Expurgo e embargo em toda fronteira:**
- remover do treino as linhas cujo alvo (`t + 1` a `t + 20`) entra no período de validação ou de teste;
- descartar os primeiros 20 pregões após cada fronteira;
- teste automático: para toda linha de treino, `data(t + 20) < início da validação`. Se falhar, o experimento para (seção 10).

**Teste final.** O mesmo procedimento de origem móvel continua no período de teste (novo ajuste a cada 252 pregões, com a escolha de hiperparâmetros feita pelo procedimento já fixado). Nada é escolhido olhando o teste.

## 7. Referência e modelo candidato

| Papel | Modelo | Detalhe |
| --- | --- | --- |
| Referência obrigatória | Retorno zero | `ŷ = 0` em toda data |
| Referência auxiliar | Média histórica expansível | Média dos alvos já realizados até `t − 20` |
| Candidato | Regressão regularizada (Ridge) | Variáveis padronizadas no treino; `alpha` escolhido em grade fixa (0,1; 1; 10; 100; 1000) por validação temporal interna ao treino |
| Expansão (após a primeira avaliação) | Um modelo de árvores (gradient boosting) | Só entra numa rodada nova, registrada, e não reabre o teste final |

**Bibliotecas:** scikit-learn só no ambiente de `experiments/preditivo/` (arquivo de dependências próprio). O `requirements.txt` do aplicativo não muda neste piloto.

## 8. Estratégia e custos [R7]

| Item | Proposta |
| --- | --- |
| Regra | Na data de decisão, ficar **exposto** ao ativo se `ŷ > c`; senão, ficar **em caixa** |
| Limiar `c` | Custo de ida e volta (seção abaixo); nenhum outro limiar é testado no teste final |
| Frequência de decisão | A cada 20 pregões, em datas fixas (sem sobreposição de posições) |
| Execução | No fechamento do pregão seguinte à decisão (`t + 1`), para não usar o preço de `t` duas vezes |
| Restrições | Sem venda a descoberto, sem alavancagem, um ativo por vez |
| Caixa | Remunerado pelo CDI diário (Banco Central, série SGS 12), coletado e congelado com o mesmo manifesto |
| Custo por operação | 0,05% de custos de negociação + 0,05% de slippage (premissa); sensibilidade com 0%, 0,1% e 0,3% |
| Comparações | Comprar e manter o ativo; ficar só em caixa; a mesma regra usando a referência de retorno zero (que equivale a ficar em caixa) |
| Impostos | Não modelados; resultados rotulados "antes de impostos" |

Os dois experimentos de aporte do plano (capital disponível desde o início e dinheiro recebido ao longo do tempo) ficam para a rodada seguinte, com especificação própria.

## 9. Métricas e condições de habilitação

### 9.1 Métricas registradas (todas, sempre)

| Objeto | Métricas |
| --- | --- |
| Previsão | MAE e RMSE do candidato e das referências; razão RMSE candidato / RMSE retorno zero; R² fora da amostra em relação ao retorno zero (`1 − SSE_candidato / SSE_zero`) |
| Comparação estatística | Teste de Diebold-Mariano com erro-padrão robusto (Newey-West, 19 defasagens), por causa da sobreposição dos alvos |
| Direção | Acurácia balanceada do sinal de `ŷ`, calculada só nas datas de decisão (sem sobreposição) |
| Estratégia | Retorno líquido acumulado e anualizado, volatilidade, drawdown máximo, número de trocas e percentual do tempo exposto |
| Estabilidade | R² fora da amostra em cada dobra do desenvolvimento |

### 9.2 Critérios de elegibilidade, definidos antes da avaliação final (proposta)

Avaliados **por ativo**, no teste final. O sinal só pode ser habilitado no ambiente experimental se **todos** forem atendidos:

1. R² fora da amostra maior que zero (o candidato erra menos que o retorno zero);
2. Diebold-Mariano com p < 0,10 a favor do candidato;
3. R² fora da amostra maior que zero em pelo menos 5 das 8 dobras do desenvolvimento;
4. com o custo da premissa, a estratégia tem retorno líquido maior que ficar em caixa **e** drawdown máximo menor que comprar e manter, ou retorno líquido maior que comprar e manter;
5. o resultado do critério 4 se mantém com o dobro do custo.

Se algum critério falhar, o sistema registra e, numa eventual tela experimental, informa: **"não houve evidência suficiente para habilitar o sinal"**, mostrando a comparação. Esse resultado conclui o experimento cientificamente (plano, seção 6.3).

## 10. Registro de experimentos e critérios de interrupção

**Registro.** Cada execução grava uma linha em `experiments/preditivo/registro.jsonl` com:
- data e hora (Brasília) e commit do código;
- hash do manifesto de dados e da configuração;
- ativo, modelo, hiperparâmetros e dobra;
- métricas e se a execução tocou o teste final.

Configurações rejeitadas ficam registradas e entram no relatório. O teste final é marcado como **usado** na primeira execução que o lê.

**Interromper e corrigir antes de seguir quando:**
- o teste de expurgo da seção 6 falhar;
- a coleta tiver lacunas não explicadas, ou a verificação de ajuste da seção 3 mostrar diferenças sem evento conhecido;
- o código de treino ler qualquer linha do período de teste.

**Se um vazamento for descoberto depois de usar o teste final:** registrar o ocorrido, corrigir e reportar os resultados como comprometidos. O teste final não é refeito com novos dados escolhidos depois.

---

## Pendências antes de executar

| Item | Depende de |
| --- | --- |
| Ativos e datas (seções 1 e 5) | R6 |
| Estratégia, custos e caixa (seção 8) | R7 |
| Série de preços (seção 3) | R8 |
| Limiares de elegibilidade (seção 9.2) | Orientador, antes do início |
| Coleta do CDI e conferência dos termos de uso das fontes | Desenvolvedor |
