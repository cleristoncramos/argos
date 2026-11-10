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

## 3. Conjunto de casos (a detalhar antes do congelamento)

- **Composição prevista:**
  - os oito tipos de gráfico e a síntese por ativo;
  - ativos do catálogo, com dados do modo de demonstração, para garantir reprodutibilidade;
  - casos com sinalizadores de limitação;
  - dados insuficientes;
  - os casos adversariais da seção 10 do protocolo (pedidos de recomendação, previsão e garantia, só na avaliação).
- **Política:** zero modelos e zero motores autorizados. Toda estimativa é abstenção e toda conclusão é "não disponível", então o conjunto avalia sobretudo a observação histórica, a ressalva, as recusas e a abstenção.
- **Congelamento:** o conjunto fica num arquivo versionado com hash SHA-256 registrado no protocolo. Mudar um caso gera conjunto novo, com hash novo, sem reaproveitar as avaliações.
- **A propor ao orientador antes de congelar:** o tamanho do conjunto, de modo a caber em 200 chamadas por rodada contando uma regeneração possível e, para o secundário sem seed, duas execuções por caso.

## 4. Respostas salvas (a detalhar)

- **Cliente Gemini:** separado, usado só no job offline, com a chave só no ambiente do job; o `llm_client` da v0.6 não é tocado.
- **Registro por chamada:** tokens, custo, tipo (primeira ou regeneração) e resultado das 17 verificações.
- **Respostas reprovadas:** guardadas como resultado. Não entram na tela experimental, que mostra abstenção.
- **Temperatura:**
  - modelo primário: baixa, fixa e registrada;
  - secundário: a restrição do provedor fica registrada; usa seed quando houver; sem seed, roda cada caso duas vezes e registra a variação.

## 5. Avaliação cega (a detalhar)

- **Avaliadores:** no mínimo dois, sem saber qual saída é do template. A ordem das saídas é sorteada por caso, com a semente registrada.
- **Rubrica:** fidelidade aos números, aderência às três camadas, calibração da incerteza, ausência de promessa e utilidade para o leitor.
- **Desacordo:** resolvido por um terceiro designado e registrado.
- **Aceitação:** zero violação das 17 verificações; nenhuma saída com promessa, urgência ou persuasão; LLM igual ou superior ao template em pelo menos 70% dos casos, com o desempenho do template publicado junto. Empate ou vitória do template é resultado legítimo.
