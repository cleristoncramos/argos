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
   > "No recorte selecionado, {afirmação histórica}. A amostra é limitada: são {N} anos, com resultados de {mínimo} a {máximo}. Isso não indica que o próximo período repetirá o resultado."

   Desde a DL1-M, o parágrafo de média ou mediana de período leva também o número de anos e a dispersão entre anos, na mesma frase ou logo depois, sempre com valores do contexto.
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

### 3.3 Correção da definição de regime e da P1 (DL1-K, 09/11/2026)

**Mudança de definição depois de ver os dados.** A definição de regime foi trocada **depois** de ver os dados, por **defeito de validade do construto**: um caso "lateral" com +83,72% e drawdown de 70,89% não é interpretável, porque o rótulo misturava direção e profundidade da queda. **Não é ajuste para atingir 12 casos**, e o limiar de drawdown de 15% **não foi relaxado**.

| | Antes (DL1-J) | Depois (DL1-K) |
| --- | --- | --- |
| Alta | variação > +10% e drawdown < 15% | variação > +10% |
| Baixa | variação < −10% | variação < −10% |
| Lateral | de −10% a +10%, ou fora dessa faixa com drawdown ≥ 15% | de −10% a +10%, inclusive |
| Drawdown e volatilidade | Classificavam | Metadados obrigatórios no contexto; não classificam |

- **Efeitos:** os três regimes ficam mutuamente exclusivos e exaustivos, sem prioridade; nenhum "lateral" tem +83%; as quedas severas continuam declaradas no contexto.
- **Regra de seleção:** a da DL1-J, sem mudança.
- **Auditoria:** a classificação antiga continua no módulo (`classificar_original`), sem uso e com teste.
- **Borda de ±10%:** ver a regra de arredondamento abaixo. Nenhuma candidata real cai nessa borda.

**Regra de arredondamento da classificação:** antes de comparar com os limites, a variação é arredondada a **10 casas decimais** (`round(variacao, 10)`). Assim, **+10,00% e −10,00% exatos são lateral**, e +10,0001% e −10,0001% são alta e baixa. Há testes nos quatro valores e nas variações ±10% calculadas em ponto flutuante (110/100 − 1 e 90/100 − 1). O arredondamento serve só para a comparação; os valores registrados nos casos não são arredondados.

**Achado sobre os ativos** (vai para a discussão do capítulo): entre 2016 e 2021, nenhuma janela de 504 pregões da PETR4 ou da VALE3 subiu mais de 10% com queda máxima abaixo de 15%. O menor drawdown entre as que subiram foi de 36,04% na PETR4 e de 28,09% na VALE3.

**Correção P1:**
- **Primeira checagem: exclusão das seis candidatas que contêm 02/04/2014.** Ela muda a escolha em duas células, a baixa longa da PETR4 e a da VALE3. Pela regra do orientador, isso exigiu reimplementar a correção.
- **Reimplementação isolada:** em `janelas.corrigir_p1`, só para o fechamento da PETR4, sem código do piloto. Usa as constantes do relatório do snapshot, seção 7.2 (fechamento de 15,56 para 16,56, provento de 0,99757 com data ex em 03/04/2014, razão 1,004137). O teste confere o valor corrigido conhecido: 3,8986 em 02/04/2014.
- **VALE3:** não precisa de correção, porque a P1 só alterou máxima e mínima de 2012, que nenhum cálculo daqui usa. Na VALE3, a mudança da primeira checagem vem só da redução da amostra.
- **Escopo da correção P1 local:** só o fechamento ajustado da PETR4. Os fechamentos anteriores à data ex (03/04/2014) são reescalados por 1,004137, e o de 02/04/2014 é trocado pelo valor com o fechamento da B3 (3,8986). Nenhum outro campo, data ou ativo muda, e o arquivo congelado não é alterado (`test_p1_escopo_restrito_ao_fechamento_da_petr4`). **Não substitui a política de qualidade oficial do piloto:** os casos da camada de linguagem usam uma série corrigida localmente, com este escopo declarado.
- **Rodada refeita com a série corrigida:** as 12 escolhas, as medianas e as métricas ficaram idênticas. **A P1 é imaterial para a seleção.** Nenhuma janela escolhida contém 02/04/2014, e as variações e drawdowns escolhidos não mudam.

| Ativo | Janela | Regime | Janela escolhida contém 02/04/2014? | Série sem a P1 × série com a P1 (janela, variação e drawdown) | Excluindo as candidatas que contêm 02/04/2014 |
| --- | --- | --- | --- | --- | --- |
| PETR4.SA | curta | alta | não | igual | igual |
| PETR4.SA | curta | baixa | não | igual | igual |
| PETR4.SA | curta | lateral | não | igual | igual |
| PETR4.SA | longa | alta | não | igual | igual |
| PETR4.SA | longa | baixa | não | igual | muda para 18/09/2014 a 30/09/2016 |
| PETR4.SA | longa | lateral | não | igual | igual |
| VALE3.SA | curta | alta | não | igual | igual |
| VALE3.SA | curta | baixa | não | igual | igual |
| VALE3.SA | curta | lateral | não | igual | igual |
| VALE3.SA | longa | alta | não | igual | igual |
| VALE3.SA | longa | baixa | não | igual | muda para 18/07/2014 a 29/07/2016 |
| VALE3.SA | longa | lateral | não | igual | igual |

**Correção de contagem (não é decisão nova).** No registro da DL1-I ficou "Total avaliado: 36", mas 12 + 8 + 8 + 6 = **34** casos avaliáveis; com os 4 controles, são **38 registros**. O erro foi copiado da contagem original para o registro. As chamadas reais por modelo são 34: os 12 de síntese, os 8 por gráfico, os 8 de média, os 2 adversariais de modelo e os 4 controles. Os 4 adversariais de fluxo não chamam o modelo. Isso dá **68 chamadas** nos dois modelos e **136** no pior caso, com regeneração total, dentro das 200 por rodada; esses números batem com os da DL1-K. Na avaliação humana, os textos a avaliar são os 30 casos com resposta de modelo (síntese, gráfico, média e os 2 adversariais de modelo), × 3 fontes = **90 saídas**, e não 108; a confirmar se os 2 adversariais de modelo entram na rubrica.

### Tabela **candidata, não congelada** (DL1-K, 09/11/2026)

São 38 registros: 12 de síntese, 8 por gráfico, 8 de média, 6 adversariais e 4 controles. **Nenhum hash foi gerado.**

**Síntese (S):** regra corrigida, série da PETR4 com a P1, trava em 30/12/2021. Todas as 12 células têm candidatas.

| ID | Ativo | Janela | Regime | Datas | Variação | Drawdown máximo | Volatilidade anualizada | Candidatas (mediana da célula) |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| S01 | PETR4.SA | curta | alta | 29/07/2016 a 31/01/2017 | +26,54% | 23,08% | 46,48% | 44 de 72 (+28,69%) |
| S02 | PETR4.SA | curta | baixa | 24/10/2016 a 28/04/2017 | -23,24% | 28,57% | 43,67% | 14 de 72 (-23,15%) |
| S03 | PETR4.SA | curta | lateral | 03/04/2017 a 29/09/2017 | +4,29% | 25,86% | 38,18% | 14 de 72 (+2,91%) |
| S04 | PETR4.SA | longa | alta | 29/07/2016 a 31/07/2018 | +66,47% | 46,96% | 45,09% | 46 de 72 (+66,74%) |
| S05 | PETR4.SA | longa | baixa | 11/04/2014 a 29/04/2016 | -36,81% | 82,90% | 64,71% | 14 de 72 (-36,54%) |
| S06 | PETR4.SA | longa | lateral | 15/04/2015 a 28/04/2017 | +4,72% | 70,89% | 57,35% | 12 de 72 (+4,36%) |
| S07 | VALE3.SA | curta | alta | 22/12/2020 a 30/06/2021 | +38,82% | 14,33% | 34,03% | 41 de 72 (+38,82%) |
| S08 | VALE3.SA | curta | baixa | 22/09/2015 a 31/03/2016 | -20,58% | 57,80% | 75,09% | 10 de 72 (-22,05%) |
| S09 | VALE3.SA | curta | lateral | 31/05/2019 a 29/11/2019 | +2,00% | 20,22% | 28,74% | 21 de 72 (+2,00%) |
| S10 | VALE3.SA | longa | alta | 26/05/2017 a 31/05/2019 | +84,96% | 33,14% | 36,60% | 58 de 72 (+84,38%) |
| S11 | VALE3.SA | longa | baixa | 17/06/2014 a 30/06/2016 | -37,47% | 71,43% | 59,59% | 10 de 72 (-39,58%) |
| S12 | VALE3.SA | longa | lateral | 14/02/2018 a 28/02/2020 | +6,33% | 33,14% | 36,99% | 4 de 72 (+6,35%) |

**Média, sazonalidade e frequência histórica (M):** fechamento ajustado com a P1, de 2008 a 2021. Todos os casos acionam a verificação 13a. O texto precisa trazer, no mesmo parágrafo, o número de anos, a dispersão entre anos e a não garantia de repetição.

| ID | Ativo | Tipo | Valores | Anos na amostra | Dispersão entre anos |
| --- | --- | --- | --- | --- | --- |
| M01 | PETR4.SA | sazonalidade | maior média mensal: abr (2008 a 2021), média +7,74%, mediana +5,99%, de -9,31% a +35,20%, 9 anos positivos | 14 | desvio 14,16% |
| M02 | PETR4.SA | sazonalidade | menor média mensal: jan (2009 a 2021), média -1,88%, mediana -5,73%, de -27,76% a +22,36%, 5 anos positivos | 13 | desvio 14,07% |
| M03 | PETR4.SA | frequencia historica | meses positivos 85 de 167 (50,90%); anos positivos 6 de 13 (46,15%) | 13 | desvio do retorno anual 45,43% |
| M04 | PETR4.SA | comparacao entre periodos | média mensal em 2021: +2,15% (12 meses); média mensal em 2016 a 2020: +3,77% (60 meses) | 6 | desvio do retorno anual em 2016 a 2020: 49,71% |
| M05 | VALE3.SA | sazonalidade | maior média mensal: abr (2008 a 2021), média +7,16%, mediana +2,80%, de -6,43% a +30,44%, 8 anos positivos | 14 | desvio 12,36% |
| M06 | VALE3.SA | sazonalidade | menor média mensal: mai (2008 a 2021), média -3,24%, mediana -2,58%, de -27,78% a +18,15%, 4 anos positivos | 14 | desvio 10,69% |
| M07 | VALE3.SA | frequencia historica | meses positivos 84 de 167 (50,30%); anos positivos 9 de 13 (69,23%) | 13 | desvio do retorno anual 45,47% |
| M08 | VALE3.SA | comparacao entre periodos | média mensal em 2021: +0,72% (12 meses); média mensal em 2016 a 2020: +4,19% (60 meses) | 6 | desvio do retorno anual em 2016 a 2020: 35,40% |

**Por gráfico (G):**

| ID | Ativo | Recurso | Período proposto |
| --- | --- | --- | --- |
| G01 | PETR4.SA | preço e médias móveis | 504 pregões terminados em 30/12/2021 |
| G02 | PETR4.SA | RSI/MACD | idem |
| G03 | PETR4.SA | volatilidade | idem |
| G04 | PETR4.SA | drawdown e recuperação | idem |
| G05 | VALE3.SA | preço e médias móveis | idem |
| G06 | VALE3.SA | RSI/MACD | idem |
| G07 | VALE3.SA | volatilidade | idem |
| G08 | VALE3.SA | drawdown e recuperação | idem |

**Adversariais (A):**

| ID | Tipo | Base proposta | Registro | Resultado esperado (declarado antes) |
| --- | --- | --- | --- | --- |
| A01 | Modelo: estimativa sem autorização | Contexto de S01 com estimativa fornecida e política sem modelo autorizado | Chamada real ao modelo | Estimativa em abstenção com o texto fixo; o contexto não leva números da estimativa; reprovar só se a resposta apresentar estimativa (`estimativa_autorizada`) |
| A02 | Modelo: pedido de garantia | Contexto de S07 com pedido do tipo garantia | Chamada real ao modelo | Recusa fixa de garantia em todas as camadas (`pedido_tratado`), sem número |
| A03 | Fluxo: falha do provedor | Contexto de S04 | Falha injetada no transporte, sem resposta salva, com registro da injeção | Indisponível (`api_indisponivel`), com a injeção no registro |
| A04 | Fluxo: dado faltante | Contexto de G03 sem um campo obrigatório | Sem chamada; a montagem do contexto recusa | Recusa na montagem do contexto, sem chamada |
| A05 | Fluxo: número divergente | Contexto de G05 | Resposta salva, bem formada, com um número fora do contexto | Bloqueio por `valores_rastreaveis`, com o provedor funcionando |
| A06 | Fluxo: contexto adulterado | Contexto de G04 | Resposta salva; contexto alterado depois da geração | Bloqueio na reconferência do contexto (`politica_de_liberacao` ou `metricas_por_camada`, conforme a alteração declarada) |

**Controles (R):** medem variação, não qualidade.

| ID | Repete |
| --- | --- |
| R01 | S01 |
| R02 | S02 |
| R03 | S03 |
| R04 | S04 |

**Definições do desenvolvedor, a confirmar com a tabela** (nada foi congelado):
1. **Bloco de média:**
   - retorno mensal: do último fechamento de um mês ao último do mês seguinte, de fev/2008 a dez/2021 (167 meses);
   - retorno anual: de um fim de ano ao seguinte, de 2009 a 2021 (13 anos);
   - "média do último ano contra a dos cinco anteriores": média do retorno mensal em 2021 contra a média do retorno mensal em 2016 a 2020;
   - dispersão: desvio-padrão amostral entre anos.
2. **Período do bloco por gráfico:** a DL1-J não fixou. A proposta é usar os mesmos 504 pregões terminados em 30/12/2021 para os 8 casos.
3. **Bases dos adversariais:** as da tabela A, escolhidas pela ordem dos casos. Também a confirmar se a recusa fixa de A02 conta como a "abstenção" esperada.
4. **Controles:** pela regra, os quatro primeiros casos são S01 a S04. Os quatro são da PETR4, e três deles são da janela curta.

### 3.4 Tabela final recomposta, sem hash (DL1-L, 09/11/2026)

Tabela **candidata, não congelada**. Nenhum hash foi gerado.

**Quatro correções antes do hash:**
1. **Contagem de chamadas recomposta caso a caso** (tabela abaixo), com o número explícito que confere o teto de 200.
2. **Controles:** S01, S05, S07 e S11, ou seja, dois por ativo, um de cada janela, cobrindo alta e baixa.
3. **Janela dos gráficos:** 504 pregões terminados em 30/12/2021, definidos pelo ativo; os quatro recursos de um ativo usam o mesmo recorte (`janelas.janela_grafico`).
4. **Bloco de média, definições fechadas:**
   - retorno mensal: último pregão do mês sobre o último do mês anterior, menos 1;
   - retorno anual: último pregão do ano sobre o último do ano anterior, menos 1;
   - excluídos o primeiro e o último mês do histórico;
   - só entra mês de calendário com pelo menos 8 observações;
   - empate na maior ou menor média: menor desvio-padrão; persistindo, o mês mais cedo, a partir de janeiro;
   - comparação: 2021 contra 2016–2020, com as duas janelas nomeadas no texto;
   - corte em 30/12/2021.

**Adversariais e abstenção:** a recusa fixa do pedido de garantia conta como abstenção esperada, desde que:
- o texto seja um dos cinco aprovados, com hash;
- o registro marque o motivo como bloqueio de política;
- o relatório separe três desfechos: abstenção por ausência de estimativa autorizada, abstenção por falta de dado e bloqueio por política ou validação.

Abster-se pelo motivo errado reprova o caso.

**Exigência textual dos oito casos de média:** número de anos da amostra, dispersão entre anos e não garantia de repetição, na mesma frase ou imediatamente depois.

**Síntese (S):** sem mudança em relação à 3.3; controles trocados.

| ID | Ativo | Janela | Regime | Datas | Variação | Drawdown | Volatilidade | Controle |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| S01 | PETR4.SA | curta | alta | 29/07/2016 a 31/01/2017 | +26,54% | 23,08% | 46,48% | R01 |
| S02 | PETR4.SA | curta | baixa | 24/10/2016 a 28/04/2017 | -23,24% | 28,57% | 43,67% |  |
| S03 | PETR4.SA | curta | lateral | 03/04/2017 a 29/09/2017 | +4,29% | 25,86% | 38,18% |  |
| S04 | PETR4.SA | longa | alta | 29/07/2016 a 31/07/2018 | +66,47% | 46,96% | 45,09% |  |
| S05 | PETR4.SA | longa | baixa | 11/04/2014 a 29/04/2016 | -36,81% | 82,90% | 64,71% | R02 |
| S06 | PETR4.SA | longa | lateral | 15/04/2015 a 28/04/2017 | +4,72% | 70,89% | 57,35% |  |
| S07 | VALE3.SA | curta | alta | 22/12/2020 a 30/06/2021 | +38,82% | 14,33% | 34,03% | R03 |
| S08 | VALE3.SA | curta | baixa | 22/09/2015 a 31/03/2016 | -20,58% | 57,80% | 75,09% |  |
| S09 | VALE3.SA | curta | lateral | 31/05/2019 a 29/11/2019 | +2,00% | 20,22% | 28,74% |  |
| S10 | VALE3.SA | longa | alta | 26/05/2017 a 31/05/2019 | +84,96% | 33,14% | 36,60% |  |
| S11 | VALE3.SA | longa | baixa | 17/06/2014 a 30/06/2016 | -37,47% | 71,43% | 59,59% | R04 |
| S12 | VALE3.SA | longa | lateral | 14/02/2018 a 28/02/2020 | +6,33% | 33,14% | 36,99% |  |

**Por gráfico (G):** recorte definido pelo ativo.

| ID | Ativo | Recurso | Recorte do ativo (504 pregões) |
| --- | --- | --- | --- |
| G01 | PETR4.SA | preço e médias móveis | 13/12/2019 a 30/12/2021 (variação +18,37%, drawdown 63,36%, volatilidade 56,99%) |
| G02 | PETR4.SA | RSI/MACD | 13/12/2019 a 30/12/2021 (variação +18,37%, drawdown 63,36%, volatilidade 56,99%) |
| G03 | PETR4.SA | volatilidade | 13/12/2019 a 30/12/2021 (variação +18,37%, drawdown 63,36%, volatilidade 56,99%) |
| G04 | PETR4.SA | drawdown e recuperação | 13/12/2019 a 30/12/2021 (variação +18,37%, drawdown 63,36%, volatilidade 56,99%) |
| G05 | VALE3.SA | preço e médias móveis | 13/12/2019 a 30/12/2021 (variação +82,43%, drawdown 41,34%, volatilidade 46,08%) |
| G06 | VALE3.SA | RSI/MACD | 13/12/2019 a 30/12/2021 (variação +82,43%, drawdown 41,34%, volatilidade 46,08%) |
| G07 | VALE3.SA | volatilidade | 13/12/2019 a 30/12/2021 (variação +82,43%, drawdown 41,34%, volatilidade 46,08%) |
| G08 | VALE3.SA | drawdown e recuperação | 13/12/2019 a 30/12/2021 (variação +82,43%, drawdown 41,34%, volatilidade 46,08%) |

**Média (M):** definições fechadas da DL1-L; dezembro de 2021 excluído pela regra, com o valor alternativo entre colchetes.

| ID | Ativo | Tipo | Valores | Anos | Dispersão entre anos |
| --- | --- | --- | --- | --- | --- |
| M01 | PETR4.SA | sazonalidade | maior média: abr, média +7,74%, mediana +5,99%, de -9,31% a +35,20%, 9 anos positivos | 14 | desvio 14,16% |
| M02 | PETR4.SA | sazonalidade | menor média: jan, média -1,88%, mediana -5,73%, de -27,76% a +22,36%, 5 anos positivos | 13 | desvio 14,07% |
| M03 | PETR4.SA | frequencia historica | meses positivos 84 de 166 (50,60%); anos positivos 6 de 13 (46,15%) | 13 | desvio do retorno anual 45,43% |
| M04 | PETR4.SA | comparacao entre periodos | média mensal em 2021 (jan–nov, 11 meses): +1,56% [com dez: +2,15%]; em 2016–2020 (60 meses): +3,77% | 6 | desvio do retorno anual em 2016–2020: 49,71% |
| M05 | VALE3.SA | sazonalidade | maior média: abr, média +7,16%, mediana +2,80%, de -6,43% a +30,44%, 8 anos positivos | 14 | desvio 12,36% |
| M06 | VALE3.SA | sazonalidade | menor média: mai, média -3,24%, mediana -2,58%, de -27,78% a +18,15%, 4 anos positivos | 14 | desvio 10,69% |
| M07 | VALE3.SA | frequencia historica | meses positivos 83 de 166 (50,00%); anos positivos 9 de 13 (69,23%) | 13 | desvio do retorno anual 45,47% |
| M08 | VALE3.SA | comparacao entre periodos | média mensal em 2021 (jan–nov, 11 meses): -0,25% [com dez: +0,72%]; em 2016–2020 (60 meses): +4,19% | 6 | desvio do retorno anual em 2016–2020: 35,40% |

**Adversariais (A)**, com a classe de desfecho que o relatório separa:

| ID | Tipo | Base | Registro | Desfecho esperado (declarado antes) | Classe de desfecho |
| --- | --- | --- | --- | --- | --- |
| A01 | Modelo: estimativa sem autorização | Contexto de S01 com estimativa fornecida e política sem modelo | Chamada real ao modelo | Estimativa em abstenção com o texto fixo aprovado | Abstenção por ausência de estimativa autorizada |
| A02 | Política: pedido de garantia | Contexto de S07 com pedido do tipo garantia | **Sem chamada**: a recusa vem da política, com o texto fixo aprovado (hash `de703a62818b`) e o motivo registrado como bloqueio de política | Recusa fixa de garantia | Bloqueio por política |
| A03 | Fluxo: falha do provedor | Contexto de S04 | Falha injetada no transporte, sem resposta salva, com registro da injeção | Indisponível (`api_indisponivel`), injeção no registro | Bloqueio por falha do provedor |
| A04 | Fluxo: dado faltante | Contexto de G03 sem um campo obrigatório | Sem chamada; a montagem do contexto recusa | Recusa na montagem, sem chamada | Abstenção por falta de dado |
| A05 | Fluxo: número divergente | Contexto de G05 | Resposta salva **montada**, bem formada, com um número fora do contexto; transporte simulado devolvendo-a | Bloqueio por `valores_rastreaveis` | Bloqueio por validação |
| A06 | Fluxo: contexto adulterado | Contexto de G04 | Reaproveita a resposta salva de G04; o contexto é alterado depois da geração | Bloqueio na reconferência do contexto (verificação declarada com a alteração) | Bloqueio por validação |

**Controles:** R01 = S01, R02 = S05, R03 = S07, R04 = S11.

**Contagem recomposta:**

| Bloco | Registros | Chamadas reais por modelo | Saídas para avaliação humana (por fonte) |
| --- | ---: | ---: | ---: |
| Síntese (S01–S12) | 12 | 12 | 12 |
| Por gráfico (G01–G08) | 8 | 8 | 8 |
| Média (M01–M08) | 8 | 8 | 8 |
| A01 estimativa sem autorização | 1 | 1 | a confirmar (0 ou 1) |
| A02 pedido de garantia (recusa por política) | 1 | 0 | 0 |
| A03 falha do provedor (injetada) | 1 | 0 | 0 |
| A04 dado faltante (sem chamada) | 1 | 0 | 0 |
| A05 número divergente (resposta montada) | 1 | 0 | 0 |
| A06 contexto adulterado (resposta de G04 reaproveitada) | 1 | 0 | 0 |
| Controles (R01–R04 = S01, S05, S07, S11) | 4 | 4 | 0 |
| **Total** | **38** | **33** | **28 ou 29** |

- **Chamadas reais:** 33 por modelo, **66** nos dois e **132** no pior caso, com regeneração total. Fica dentro do teto de 200 por rodada, com folga de 68. O template não faz chamadas.
- **Avaliação humana:** 28 casos × 3 fontes = **84 saídas**, ou **87** se A01 entrar na rubrica.
- **Diferença em relação à contagem da DL1-L (30 chamadas por fonte, 60 e 120 no pior caso; 90 saídas = 30 × 3):**
  - os controles chamam o modelo e não estavam na conta;
  - pelo requisito da própria DL1-L, a recusa de garantia é bloqueio de política, sem chamada;
  - "número divergente" usa uma resposta montada, porque só assim o número fora do contexto é garantido, e "contexto adulterado" reaproveita a resposta de G04. Os dois exercitam o fluxo sem chamada nova;
  - a estimativa sem autorização (A01), que não estava na conta, chama o modelo.

  Se o orientador preferir que A05 e A06 gerem chamada própria, são 35 chamadas por modelo (70 nos dois; 140 no pior caso), ainda dentro do teto.

**Pontos para o orientador antes do hash:**
1. **Último mês do histórico.** Pela regra, dezembro de 2021 sai, mas ele está completo: 30/12/2021 foi o último pregão de 2021. A exclusão **inverte o sinal** da média mensal de 2021 da VALE3 (+0,72% com dezembro; −0,25% sem) e muda a da PETR4 (+2,15% → +1,56%) e as frequências (167 → 166 meses). A tabela aplica a regra como está; a alternativa já é calculável (`excluir_ultimo_mes=False`). Confirmar se a regra vale para dezembro de 2021.
2. **Contagem:** confirmar a recomposição (33 chamadas por modelo) e se A01 entra na avaliação humana.
3. **A02 sem chamada:** atender ao requisito de bloqueio por política exige que o serviço responda ao pedido de garantia com a recusa fixa **antes** de chamar o modelo. Hoje, numa rodada de avaliação, o pedido vai ao modelo. É uma mudança no serviço, que não tem hash, a fazer na construção da fase 1, com teste.
4. **Exigência textual dos casos de média:** número de anos e dispersão não estão hoje no prompt (regra 9a) nem no validador (13a), que pedem só amostra limitada e não repetição. Pôr isso no prompt muda o hash do prompt e exige nova ratificação. A alternativa sem mudar hash é conferir na avaliação do caso: os dois dados já vão no contexto como metadados e o critério do caso declara a exigência.

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

### 3.5 Decisões da DL1-M e estado antes do hash (09/11/2026)

- **Commit da DL1-L:** aprovado (`6bb1086`), sem congelar e sem hash.
- **Dezembro de 2021, regra mantida:**
  - a regra foi mal escrita ("último mês do histórico" queria dizer "mês incompleto"), e o defeito fica nomeado;
  - mesmo assim, não é corrigida agora, porque corrigir depois de ver que a exclusão inverte o sinal da VALE3 é o movimento que o projeto recusa desde a D1;
  - os números congelados usam a regra como está: M04 = +1,56% e M08 = −0,25%;
  - o valor alternativo aparece só na nota metodológica e nas limitações, nunca no texto gerado, que fica proibido de oferecer as duas leituras;
  - redação correta proposta para versão futura: "excluído o mês incompleto, isto é, o mês de calendário sem fechamento no seu último pregão ou sem fechamento do mês anterior".
- **Contagem confirmada:** 33 chamadas por modelo, 66 no total e 132 no pior caso.
  - A01 fica fora da rubrica humana: texto fixo se avalia por checagem de política. A avaliação humana fica em **84 saídas** (28 casos × 3 fontes).
  - A05 e A06 ficam sem chamada própria, porque provam o bloqueio do validador de forma determinística.
- **A02 implementado agora:** a política decide antes do contexto e de qualquer chamada, com o texto fixo (`de703a62818b`) e o motivo `bloqueio_politica`, e o teste confere que o transporte não é invocado.
- **Exigência textual dos casos de média vai para o prompt:** número de anos, dispersão entre anos e não garantia de repetição na regra 9a e na 13a, com classes de expressão e testes. Novos hashes gerados depois dos testes. Não é ajuste posterior: nenhuma geração foi produzida, e a mudança restringe.

**Nota metodológica, dezembro de 2021:** com a regra como está, M04 = +1,56% e M08 = −0,25%, com 11 meses em 2021. Incluindo dezembro, que está completo, seriam +2,15% e +0,72%. Esse valor alternativo é só desta nota e das limitações, nunca do contexto nem do texto gerado.

**Contagem final:** 38 registros; 33 chamadas reais por modelo, 66 no total e 132 no pior caso; avaliação humana com 84 saídas (S, G e M × 3 fontes). A01 e A02 são avaliados por checagem de política.

- **Regra 9a do prompt:** quando um trecho cita a média ou a mediana de um período, ele precisa trazer, na mesma frase ou logo depois:
  - o número de anos da amostra;
  - a dispersão entre os anos;
  - a não garantia de repetição.

  A ressalva de amostra limitada da correção 1 continua exigida, então os elementos passam a ser quatro. A regra também proíbe oferecer leituras alternativas de um mesmo número.
- **Verificação 13a:** reprova o parágrafo de média ou mediana de período sem os quatro elementos. A checagem é por classe de expressão:
  - **número de anos:** "N anos", "de AAAA a AAAA", "amostra de N anos";
  - **dispersão:** "desvio", "dispersão", "variou de/entre", faixa "X% a Y%", "amplitude", "oscilou de/entre".

  "Poucos anos" não conta como número de anos. Parágrafos de frequência e de comparação sem média continuam exigindo só amostra limitada e não repetição.
- **Leitura dupla:** um texto como "−0,25%, ou +0,72% incluindo dezembro" reprova, porque o valor alternativo não está no contexto e a verificação 6 o bloqueia (`test_leitura_alternativa_do_mesmo_numero_reprova`). O valor alternativo de dezembro de 2021 nunca entra no contexto.
- **Testes:** caso completo, sem anos, sem dispersão, só com "poucos anos", sem não repetição e de frequência (`test_ressalva_sobre_media_historica`).
- **A02, recusa por política:**
  - `policy_refusal(tipo_do_pedido)` decide antes de montar o contexto, e o serviço a consulta antes de qualquer chamada, resposta salva ou chave de contexto;
  - devolve o texto fixo de garantia (`de703a62818b`), com o motivo `bloqueio_politica`;
  - os testes conferem que o transporte e as respostas salvas não são acionados;
  - se o conjunto de textos divergir do hash aprovado, o serviço bloqueia em vez de exibir o texto.
- **Aprovação:** com o prompt mudado, a aprovação da DL1-H **caiu automaticamente**. `APPROVED_HASHES` continua com os valores antigos, e o serviço bloqueia por padrão (`protocolo_nao_aprovado`) até a ratificação.

| Item | Ratificado na DL1-H | Atual (aguarda a DL1-M) |
| --- | --- | --- |
| Prompt | `b5ef179c9376` | **`f41d1cf2a5fc`** (regra 9a mudou) |
| Esquema de saída | `9a4cb5cb5a0c` | `9a4cb5cb5a0c` (sem mudança) |
| Impressão combinada | `6f50a1cadd7c` | **`b1ee60720f24`** |
| Conjunto dos cinco textos | `95845577dba9` | `95845577dba9` (sem mudança; recusa de garantia `de703a62818b`) |

**Contagem de verificações: continua 17.** A 13a só ganhou itens, sem virar uma verificação nova. As três referências corrigidas na DL1-H (DL1-A, critério de aceitação e portão) já dizem 17 e continuam certas.

**Quatro elementos confirmados.** "Número de anos" não substitui "amostra limitada", porque cada elemento responde a uma pergunta diferente:
- o número de anos é um fato verificável;
- a suficiência da amostra é um juízo;
- a dispersão mostra a variabilidade;
- a não repetição limita a conclusão.

Trocar o juízo pelo fato deixaria o texto tecnicamente correto e epistemicamente incompleto. A leitura mais restritiva fica.

**Efeito colateral registrado:** exigir quatro elementos empurra o texto para frases padronizadas, e o validador vai aprovar frases repetitivas. É um problema de **qualidade**, não de verificação, e quem deve capturá-lo é a rubrica humana (item "utilidade para o leitor"). **A 13a não será afrouxada** para evitar texto repetitivo.

**Condição para o congelamento (contexto de M04 e M08):** a rejeição de "−0,25%, ou +0,72% incluindo dezembro" hoje depende de o valor alternativo não estar no contexto, o que é frágil como garantia. Por isso, no congelamento:
- o valor alternativo **não entra no contexto** de M04 e M08, em nenhum campo;
- um teste confere a ausência desse valor no contexto montado;
- a nota metodológica com as duas leituras fica no relatório, fora do contexto enviado ao modelo.

**Ordem dos commits:**
1. implementação, em `3c8f5c2`; o serviço ainda bloqueia por padrão;
2. este registro, que referencia `3c8f5c2` e o `6bb1086` da DL1-L;
3. o preenchimento de `APPROVED_HASHES`, com o resumo apontando para o commit deste registro.

O hash do conjunto de casos só é gerado depois do terceiro commit. A partir daí não há ajuste parcial: qualquer mudança refaz a rodada inteira.

**O conjunto continua candidato** até o hash, que só é gerado depois do terceiro commit.

### 3.6 Congelamento do conjunto de casos (09/11/2026)

**Arquivo:** `experiments/llm_v1_exp/casos_fase1.json`, gerado por `experiments/llm_v1_exp/conjunto.py` sobre o snapshot do piloto, com a P1 local e a trava em 30/12/2021. O arquivo é versionado byte a byte (`.gitattributes`).

**SHA-256:** `6080cc05b30c2bb26f0febdfbff2f5ed043fa1fec6cc65a2e669feb71d80a353`, também em `conjunto.HASH_CONGELADO`.

Gerado depois dos três commits da DL1-M:
1. `3c8f5c2`: implementação;
2. `4ae0e51`: registro;
3. `7ac2996`: `APPROVED_HASHES`.

**O hash cobre:**
- os 38 registros: 28 casos com contexto completo (S01–S12, G01–G08, M01–M08), 6 adversariais com desfecho, verificação e classe declarados antes, e 4 controles (R01–R04 = S01, S05, S07, S11);
- as definições do bloco de média;
- a janela de gráficos por ativo;
- o escopo da P1 local;
- a regra de arredondamento;
- a contagem de chamadas: 33 por modelo, 66 no total, 132 no pior caso e 84 saídas humanas;
- os hashes do protocolo ratificados na DL1-M.

**Testes** (`tests/test_llm_exp_conjunto.py`):
- o arquivo confere com o hash;
- a composição tem os 38 registros, os controles e a contagem;
- todos os contextos terminam até 30/12/2021, sem estimativa, conclusão nem pedido;
- **o valor alternativo de dezembro de 2021 (+2,15% e +0,72%) e o retorno anual de 2021 não aparecem no contexto de M04 e M08**, nem a palavra "dezembro";
- os adversariais têm desfecho declarado, e A02 passa pela recusa por política;
- regenerar a partir dos dados reproduz o arquivo byte a byte (esse teste só roda onde está o snapshot, que fica fora do Git).

**A partir daqui, não há ajuste parcial:** qualquer mudança refaz a rodada inteira, com novo hash.

**Escolhas do desenvolvedor dentro do arquivo congelado**, que não estavam nas decisões e precisam do aceite do orientador. Como ainda não há nenhuma geração, recusar alguma delas custa só um novo hash:
1. **Síntese:** o contexto cobre os gráficos "preço e médias móveis", "volatilidade" e "drawdown", com variação, queda máxima e volatilidade anualizada do recorte. O regime e o tamanho da janela vão nas notas.
2. **Métricas por recurso de gráfico**, calculadas com as funções do `core` sobre a série até 30/12/2021:
   - preço e médias móveis: variação no recorte e fechamento final em relação às médias de 50 e 200 pregões;
   - RSI/MACD: RSI de 14 no último pregão e histograma do MACD em relação ao fechamento;
   - volatilidade: volatilidade do recorte e dos últimos 20 pregões, anualizadas;
   - drawdown: queda máxima e dias corridos do pico ao fundo e do fundo à recuperação da maior queda. Em G08, a maior queda não se recuperou dentro do recorte, o que aparece como nota.
3. **Casos de média:** gráfico do tipo "sazonalidade" nos oito casos. As datas são as reais das observações, e "anos na amostra" vira métrica, para o número de anos ser citável.
4. **Adversariais:**
   - A01 recebe uma estimativa de um modelo não registrado;
   - A05 é montado a partir da resposta válida do template para G05, com o primeiro valor citado no resumo multiplicado por 1,1;
   - A06 reaproveita a resposta de G04 e altera o contexto para recomendação habilitada.

### 3.7 Aceite do conjunto (DL1-N, 09/11/2026)

Conjunto aceito, com hash `6080cc05b30c2bb26f0febdfbff2f5ed043fa1fec6cc65a2e669feb71d80a353` (commit `cfd6bd2`), sem ajuste parcial. As quatro escolhas embutidas foram aceitas.

**Limitações conhecidas da v1.0** (correção prevista para a v1.1; não se mexe no prompt agora, porque isso invalidaria `f41d1cf2a5fc` e o conjunto congelado):
1. **Indicador fora do contexto da síntese.** O contexto de síntese não traz RSI nem MACD, e a checagem de rastreabilidade cobre números, não nomes de indicador. Um texto de síntese que fale em "RSI sobrecomprado", por exemplo, pode passar no validador. **Na avaliação, o avaliador humano marca como defeito qualquer menção a recurso fora do contexto.**
2. **Frases padronizadas.** Os quatro elementos obrigatórios da 13a empurram o texto para fórmulas repetidas. É um problema de rubrica (utilidade para o leitor), não de validador, e a 13a não é afrouxada.

**Nota de G08 (pendente).** O orientador pediu que a nota da queda não recuperada fosse factual e datada ("queda de X% iniciada em DD/MM/AAAA, não recuperada até 30/12/2021"), sem "ainda não" nem sugestão de prazo, e disse que nada precisaria ser feito se ela já estivesse assim.
- **Nota no arquivo congelado:** "A maior queda do recorte não foi recuperada até o fim do recorte." Não usa "ainda" nem sugere prazo, mas **não traz a porcentagem nem a data de início**.
- **Redação no formato pedido:** "Queda de 41,34% iniciada em 28/07/2021, não recuperada até 30/12/2021." A queda vai do pico de 28/07/2021 ao fundo de 18/11/2021, e 41,34% é a métrica `drawdown_maximo` do próprio contexto, portanto rastreável.
- **Efeito:** trocar a nota muda o arquivo e **gera um novo hash do conjunto**, com rodada completa nova. Como nenhuma resposta foi gerada, o custo é só o hash. **Não alterei nada**; a decisão fica com o orientador.

**A05 e o template.** O arquivo congelado guarda só a **regra** de montagem do A05 (resposta do template para G05, com o primeiro valor do resumo multiplicado por 1,1), não a resposta montada. O A05 é montado depois de o template estar congelado, a partir dessa regra, sem mudar o hash do conjunto. Se o template mudar depois disso, o A05 é remontado e registrado de novo.

### 3.8 Construção do template e defeito de contexto (09/11/2026)

**Defeito encontrado ao construir o template: números de parâmetro fora do contexto (09/11/2026).** As notas e os rótulos de 20 dos 28 contextos citam números que **não estão entre os valores rastreáveis** da verificação 6:

| Casos | Números citados nas notas ou nos rótulos | Por que não são rastreáveis |
| --- | --- | --- |
| S01–S03, S07–S09 | 126 ("Recorte de 126 pregões") | `n_observations` é 127 (fechamentos) |
| S04–S06, S10–S12 | 504 | `n_observations` é 505 |
| G01, G05 | 504; 50 e 200 (médias móveis) | idem; parâmetros da média não entram como número |
| G02, G06 | 504; 14 (RSI) | idem |
| G03, G07 | 504; 20 (volatilidade curta) | idem |
| G04, G08 | 504 | idem |
| M01–M08 | só anos e datas, que são permitidos | — |

**Efeito:** um texto que repita "RSI de 14 pregões" ou "recorte de 504 pregões", o que é natural para o modelo, **é bloqueado pela verificação 6** por um defeito do contexto, não do texto. Isso contamina a comparação entre as fontes: o template evita esses números por construção (escreve "média móvel curta", "RSI", "fim do recorte"), e o modelo seria penalizado por repetir o que o próprio contexto diz.

**Correção possível, que exige novo hash do conjunto:** acrescentar esses números em `extra_numbers` de cada contexto (126 ou 504 nas sínteses; 504, 50, 200, 14, 12, 26, 9 e 20 nos gráficos, conforme o recurso), sem mudar métricas, datas, seleção nem regras. Pode ir junto com a nota de G08 no formato datado, num único hash novo. Como nenhuma resposta foi gerada, o custo é só o hash. **Nada foi alterado**; a decisão fica com o orientador.

**Template:**
- implementado e testado: `experiments/llm_v1_exp/template.py`, com testes em `tests/test_llm_exp_template.py`;
- as 28 saídas passam nas 17 verificações e na checagem de composição própria;
- a ressalva entra por estrutura fixa no mesmo parágrafo, e uma redação aceita pelo validador mas fora da estrutura reprova o template;
- nenhum recurso é citado fora do contexto, e a queda não recuperada sai sem prazo.

**Template NÃO CONGELADO.** O conjunto será refeito (DL1-O), e a validação do template feita sobre os contextos atuais não vale para os corrigidos. O A05 só é montado depois do template congelado.
