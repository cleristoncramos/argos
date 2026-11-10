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

**Pontos a definir antes do congelamento** (o desenvolvedor não decide sozinho):
1. **Regimes e janelas da síntese.** Quais são os três regimes (por exemplo, alta, queda e lateral) e por qual critério, declarado antes, as duas janelas de cada ativo são escolhidas, para evitar escolha favorável. Também quais são os dois ativos.
2. **Quatro recursos do bloco por gráfico**, entre os oito tipos da tabela A.3.
3. **Natureza dos seis adversariais.** Dois são casos de contexto e podem ir ao modelo: estimativa sem autorização e pedido de garantia. Os outros quatro testam o fluxo:
   - **Contexto adulterado:** o serviço ou o validador bloqueia.
   - **Número divergente:** é uma propriedade da resposta, não do contexto. Para garantir a ocorrência, a resposta precisa ser injetada, o que testa o validador, não o modelo.
   - **Falha do provedor:** é simulada no transporte.
   - **Dado faltante:** pelo protocolo atual, dados insuficientes geram um texto válido ("Os dados são insuficientes para a análise"), não abstenção. Para o acerto ser abster-se, o caso precisa ser de dado obrigatório ausente, recusado pelo Argos antes da chamada.

   Proposta: registrar os quatro como testes do fluxo, com resposta ou falha injetada e resultado esperado declarado, e não como avaliação do modelo.

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
