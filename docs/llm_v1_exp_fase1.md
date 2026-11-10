# Fase 1 da camada de linguagem v1.0-experimental — especificação

**Situação:** especificação do desenvolvedor, redigida em 09/11/2026 por determinação da DL1-H · nada desta fase foi construído ainda · protocolo de referência: [`protocolo_llm_v1.0-experimental.md`](protocolo_llm_v1.0-experimental.md), com os hashes ratificados (impressão `6f50a1cadd7c`)
**Decisões de origem:** DL1-D (fase 1 obrigatória, só respostas salvas) e DL1-E (avaliação cega), em [`pibiti/decisoes_orientador.md`](pibiti/decisoes_orientador.md).

---

## 1. Entregas

A fase 1 só termina com as quatro entregas. A avaliação humana só começa quando as três primeiras existirem com hash.

| # | Entrega | Hash registrado |
| --- | --- | --- |
| 1 | Conjunto de casos congelado: contextos v1.0-experimental, os mesmos para o template, o modelo primário e o secundário | Hash do conjunto |
| 2 | Template determinístico: texto montado por regras fixas, sem modelo de linguagem, com as mesmas três camadas e os mesmos textos fixos | Hash do código do template e das saídas sobre o conjunto |
| 3 | Respostas salvas: geradas em lote, no job offline, pelo modelo primário (Gemini Flash, versão fixada) e, se houver, pelo secundário (GPT-5 mini); versionadas e validadas pelas 17 verificações | Hash de cada arquivo de respostas |
| 4 | Primeiro relatório de avaliação cega (DL1-E) | — |

Nada é chamado durante a navegação. Os limites valem para o job: no máximo 200 chamadas por rodada e US$ 16 na rodada de avaliação, dentro do teto mensal de US$ 20. O contador próprio do job é a autoridade: reserva o custo antes da chamada e conta também as que falharem.

## 2. Regra da correção 1 no template (escrita antes da construção)

O template aplica a regra da média histórica **por composição fixa, sem depender do validador**:

1. **Estrutura fixa, não geração.** O template compõe a ressalva por estrutura fixa: toda frase de média histórica, comparação entre períodos ou frequência histórica sai de um modelo de parágrafo que já contém as duas ressalvas. Exemplo de modelo:
   > "No recorte selecionado, {afirmação histórica}. A amostra é limitada e houve variação entre os anos. Isso não indica que o próximo período repetirá o resultado."
2. **Mesmo parágrafo.** A ressalva entra no mesmo parágrafo da afirmação histórica, no mesmo campo de texto do bloco, nunca em outro bloco ou em item de lista separado.
3. **Defeito de composição.** Parágrafo do template que cite média, comparação entre períodos ou frequência histórica sem as duas ressalvas é defeito de composição, e o caso **falha no teste do template**. Esse teste é independente do validador: confere a estrutura do parágrafo montado. Além dele, as saídas do template também passam pelas 17 verificações.

O mesmo vale para as demais regras da camada: o template copia os textos fixos, o rótulo de cada bloco e os limites por gráfico; não fala de futuro fora da estimativa; e não atribui aprovação a indicador, estratégia ou modelo.

## 3. Conjunto de casos (decisão DL1-I, 09/11/2026)

São 36 casos congelados, mais quatro repetições de controle:

| Bloco | Casos | Função |
| --- | ---: | --- |
| Síntese por ativo: 3 regimes × 2 janelas × 2 ativos | 12 | Núcleo da avaliação |
| Explicação por gráfico: 2 ativos × 4 recursos | 8 | Tabela A.3 e limites por gráfico |
| Média, sazonalidade ou frequência histórica | 8 | Verificação 13a e ressalva |
| Adversariais com abstenção esperada | 6 | Estimativa sem autorização, contexto adulterado, pedido de garantia, dado faltante, número divergente, falha do provedor |
| **Total avaliado** | **36** | |
| Repetições de controle (mesmo contexto dos quatro primeiros casos) | 4 | Medem variação, sobretudo no GPT-5 mini; não entram na avaliação de qualidade |

**Regras de composição:**
- os 12 casos de síntese cobrem os dois ativos e os três regimes, sem concentração em cenário favorável;
- os 6 adversariais têm o resultado esperado declarado antes da execução, e acertar é abster-se, não produzir texto;
- as 4 repetições usam o mesmo contexto dos quatro primeiros casos e servem para medir variação, não qualidade;
- nenhum caso é acrescentado nem removido depois do congelamento. Se algum se mostrar malformado, o conjunto é refeito com novo hash e nova rodada completa.

**Política vigente:** zero modelos e zero motores. Toda estimativa é abstenção e toda conclusão é "não disponível".

**Orçamento** (contas da DL1-I):
- 40 execuções por modelo, ou 80 chamadas nos dois modelos;
- no pior caso, com regeneração total, 160 chamadas, dentro das 200 por rodada e com margem para 40 retentativas;
- custo estimado abaixo de US$ 0,50, longe do teto de US$ 16;
- o template não faz chamadas.

### 3.1 Definições da DL1-J (09/11/2026)

**Janelas:** duas, fixas, em pregões: curta = 126 (cerca de 6 meses) e longa = 504 (cerca de 24 meses).

**Regimes** (regra única sobre o fechamento ajustado, sem julgamento visual):
- alta: variação no fim da janela > +10% e drawdown máximo < 15%;
- baixa: variação < −10%;
- lateral: variação entre −10% e +10%, ou fora dessa faixa com drawdown ≥ 15%. A terceira condição é intencional e captura a alta com queda severa no meio.

**Escolha da janela:** enumeram-se as candidatas que terminam no último pregão de cada mês, de jan/2016 a dez/2021, para cada ativo, regime e comprimento. Em cada célula, escolhe-se a de retorno acumulado mais próximo da mediana; em empate, a mais antiga.

**Ativos e trava temporal:**
- PETR4.SA e VALE3.SA;
- todas as janelas terminam até 30/12/2021, sem dado do bloco reservado, nem para fins descritivos;
- o arquivo de casos grava início, fim, retorno acumulado, drawdown e regime de cada caso.

**Recursos do bloco por gráfico:** preço e médias móveis, RSI/MACD, volatilidade, drawdown e recuperação. Ficam fora:
- sazonalidade, já exercitada no bloco próprio;
- aportes, que exigem premissas de custo;
- referência de mercado, que pede índice externo ao snapshot;
- previsão, que daria abstenção garantida.

**Adversariais de fluxo:** caso que testa o modelo leva resposta salva; caso que testa o fluxo leva falha injetada ou ausência de chamada.

| Caso | Registro | O que deve reprovar |
| --- | --- | --- |
| Falha do provedor | Falha injetada, sem resposta salva, com registro da injeção | O tratamento de erro |
| Dado faltante | Sem chamada; contexto montado com campo ausente | A montagem do contexto |
| Número divergente | Resposta salva, bem formada, com número fora do contexto | A verificação de número |
| Contexto adulterado | Resposta salva e contexto alterado depois da geração | A reconferência de contexto |

Cada caso declara antes o resultado esperado e a verificação que deve disparar. O registro mostra a injeção ou a ausência de chamada. Acerto é abstenção pela verificação correta; abstenção por outro motivo conta como falha do caso.

**Congelamento:** 12 + 8 + 8 + 6 + 4 = 38 registros, dos quais 36 casos avaliáveis, num único arquivo com hash: parâmetros das janelas, função de regime e limiares, datas e métricas, resultado esperado dos adversariais e lista das repetições. Qualquer alteração posterior invalida o hash e exige rodada completa nova; não há ajuste parcial.

### 3.2 **Aplicação da regra (09/11/2026, sem congelamento).** Módulo `experiments/llm_v1_exp/janelas.py`, com testes em `tests/test_llm_exp_janelas.py`.
- **Fonte:** CSV ajustado do snapshot `snap-20261108-01`, com o hash conferido pelo manifesto.
- **Trava:** o CSV é cortado em 30/12/2021 logo depois da leitura, antes de qualquer cálculo.
- **Pipeline:** nenhum código do pipeline preditivo é executado.
- **Janela de N pregões:** N retornos, ou seja, N + 1 fechamentos.

| Ativo | Janela | Regime | Datas | Variação | Drawdown máximo | Candidatas na célula |
| --- | --- | --- | --- | ---: | ---: | --- |
| PETR4.SA | curta | alta | 06/07/2017 a 29/12/2017 | +32,29% | 14,23% | 12 de 72 (mediana +28,02%) |
| PETR4.SA | curta | baixa | 24/10/2016 a 28/04/2017 | -23,24% | 28,57% | 14 de 72 (mediana -23,15%) |
| PETR4.SA | curta | lateral | 22/09/2015 a 31/03/2016 | +19,23% | 52,27% | 46 de 72 (mediana +19,17%) |
| PETR4.SA | longa | alta | **célula vazia** (0 de 72 candidatas) | — | — | — |
| PETR4.SA | longa | baixa | 11/04/2014 a 29/04/2016 | -36,81% | 82,90% | 14 de 72 (mediana -36,54%) |
| PETR4.SA | longa | lateral | 19/01/2015 a 31/01/2017 | +63,79% | 70,89% | 58 de 72 (mediana +63,12%) |
| VALE3.SA | curta | alta | 28/11/2017 a 30/05/2018 | +42,76% | 12,82% | 22 de 72 (mediana +42,62%) |
| VALE3.SA | curta | baixa | 22/09/2015 a 31/03/2016 | -20,58% | 57,80% | 10 de 72 (mediana -22,05%) |
| VALE3.SA | curta | lateral | 21/10/2015 a 29/04/2016 | +8,84% | 53,76% | 40 de 72 (mediana +8,79%) |
| VALE3.SA | longa | alta | **célula vazia** (0 de 72 candidatas) | — | — | — |
| VALE3.SA | longa | baixa | 17/06/2014 a 30/06/2016 | -37,47% | 71,43% | 10 de 72 (mediana -39,58%) |
| VALE3.SA | longa | lateral | 12/11/2019 a 30/11/2021 | +83,72% | 41,34% | 62 de 72 (mediana +83,08%) |

Composição das células laterais e alcance da correção P1:

| Ativo | Janela | Laterais | Na faixa de ±10% | Variação > +10% com drawdown ≥ 15% | Menor drawdown entre as janelas com variação > +10% | Candidatas que contêm 02/04/2014 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| PETR4.SA | curta | 46 | 14 | 32 | 9,13% | 0 |
| PETR4.SA | longa | 58 | 12 | 46 | 36,04% | 3 |
| VALE3.SA | curta | 40 | 21 | 19 | 7,18% | 0 |
| VALE3.SA | longa | 62 | 4 | 58 | 28,09% | 3 |

**Pontos que voltam ao orientador** (nada foi ajustado; o conjunto não foi congelado):
1. **A célula "alta" da janela longa fica vazia nos dois ativos.** Nenhuma janela de 504 pregões terminada entre 2016 e 2021 teve variação > +10% com drawdown < 15%; o menor drawdown entre essas janelas foi de 36,04% na PETR4 e de 28,09% na VALE3. A regra produz **10 casos de síntese, não 12**, e o total muda.
2. **"Lateral" reúne sobretudo altas com queda severa.** Na janela longa, isso vale para 46 de 58 laterais na PETR4 e 58 de 62 na VALE3. Pela mediana, os laterais escolhidos têm variação de +19,23%, +63,79%, +8,84% e +83,72%. Um avaliador pode ler "lateral com +83,72%" como contradição. Fica a confirmar se é esse o efeito desejado da terceira condição.
3. **Precedência entre baixa e lateral.** Variação < −10% com drawdown ≥ 15% satisfaz as duas regras. Foi aplicado "baixa", porque a terceira condição foi justificada pela alta com queda. A confirmar.
4. **Correção P1.** O CSV lido é o snapshot original, sem a visão derivada da política de qualidade, cuja aplicação exigiria código do piloto. Seis candidatas longas (três por ativo) contêm 02/04/2014, data corrigida pela P1; **nenhuma janela escolhida contém essa data**. Mesmo assim, as medianas das células com essas candidatas usam o valor original. A confirmar se isso é aceitável.
5. **Bloco de média, sazonalidade ou frequência histórica (8 casos):** ainda sem composição definida (ativos, meses ou comparações e janelas).

## 4. Respostas salvas (a detalhar)

- **Cliente Gemini:** separado, usado só no job offline, com a chave só no ambiente do job; o `llm_client` da v0.6 não é tocado.
- **Registro por chamada:** tokens, custo, tipo (primeira ou regeneração) e resultado das 17 verificações.
- **Respostas reprovadas:** guardadas como resultado. Não entram na tela experimental, que mostra abstenção.
- **Temperatura:**
  - modelo primário: baixa, fixa e registrada;
  - secundário: a restrição do provedor fica registrada; usa seed quando houver; sem seed, roda cada caso duas vezes e registra a variação.

## 5. Avaliação cega (DL1-I)

- **Volume:** 36 casos × 3 fontes (template, Gemini e GPT-5 mini) = 108 saídas. Com dois avaliadores e a rubrica de cinco itens, são cerca de duas horas por avaliador.
- **Corte, se o tempo apertar:** sai o modelo secundário da avaliação humana, que fica só na checagem automática. **Nenhum caso é cortado**: reduzir a amostra enfraquece a conclusão; reduzir uma fonte só diminui a comparação.
- **Distribuição:** as saídas vão embaralhadas, sem a proporção entre fontes e sem dizer qual modelo é o primário. A semente do embaralhamento é registrada.
- **Avaliadores:** no mínimo dois, sem saber qual saída é do template.
- **Rubrica:** fidelidade aos números, aderência às três camadas, calibração da incerteza, ausência de promessa e utilidade para o leitor.
- **Desacordo:** resolvido por um terceiro designado e registrado.
- **Aceitação:** zero violação das 17 verificações; nenhuma saída com promessa, urgência ou persuasão; LLM igual ou superior ao template em pelo menos 70% dos casos, com o desempenho do template publicado junto. Empate ou vitória do template é resultado legítimo.

## 6. Conclusão da fase 1

A fase 1 termina quando existirem, com hash registrado:
1. o conjunto de 36 casos congelado, com o resultado esperado dos 6 adversariais;
2. o template com ressalva estrutural, aprovado nos testes de composição;
3. as respostas salvas das três fontes para os 36 casos;
4. o relatório de avaliação, com rubrica, discordâncias e desempenho do template ao lado.

A ativação da tela experimental só é discutida depois disso.
