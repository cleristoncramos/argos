# Desenvolvimento oficial do piloto — v2

**Situação:** rodada oficial concluída em 08/11/2026 · **PETR4.SA: filtros dos critérios 3 e 6 atendidos** · **VALE3.SA: critérios 3 e 6 não atendidos** · avaliação final bloqueada; a abertura depende de nova decisão escrita do orientador

> A configuração da v2 foi proposta a partir dos resultados de desenvolvimento da v1. As mesmas dobras foram reutilizadas para seleção e avaliação de desenvolvimento. Seus resultados não constituem evidência independente de generalização.

O período final segue como "período ainda não utilizado para avaliação preditiva ou seleção de modelos". O comando de desenvolvimento não usou preços, alvos, previsões ou métricas do bloco final para treinamento, seleção ou avaliação.

---

## 1. Identificação

| Item | Valor |
| --- | --- |
| Data | 08/11/2026 (eventos `desenvolvimento` em `experiments/preditivo/registro_v2.jsonl`) |
| Commit | `cdf7eef`: congelamento em `378b0b9` mais a correção abaixo |
| Alterações locais na rodada | Só `docs/versao_congelada.md` (desvio já registrado) e `registro_v2.jsonl`, as duas aceitas pelo protocolo v2 (seção 12) |
| Protocolo v2 | SHA-256 `767566481140bd748ec798a0d774b5ff17cc742d8cbd0d157c8d9b6f22d408a0` |
| Configuração v1 / v2 | `90986a8c…` (inalterada) / `79a89c807f33962a78e801c79e0072ed883003a9e19388259aa4f56098a3f328` |
| Nota, manifesto e política | Iguais aos da v1 (`be0747af…`, `6985328407ba…`, `f75598b06fa9…`) |

**Tentativa recusada antes da rodada.** A primeira execução depois do congelamento foi recusada pela trava de código congelado antes de carregar qualquer dado. A causa foi um defeito na leitura dos caminhos alterados: o primeiro caractere de `docs/versao_congelada.md` era cortado. O defeito foi corrigido com teste no commit `cdf7eef`, sem mudança no experimento. Nenhum resultado da v2 existia antes da rodada registrada.

**Verificações antes dos resultados.**
- **Reprodução da v1:** a v2 restrita à grade antiga reproduziu as previsões e as métricas oficiais da v1. A diferença máxima foi de 9,99 × 10⁻¹⁷ (tolerância de 10⁻¹⁰ relativa e 10⁻¹² absoluta).
- **`alpha` comuns às duas grades:** os erros internos são iguais aos da v1 em todos os 16 ajustes.

## 2. Resultados por dobra

R² fora da amostra contra o retorno zero (critério 3) e contra a média histórica expansiva causal (critério 6, `R²_média`), nas datas avaliadas de cada ano.

### PETR4.SA

| Validação | `alpha` | R² contra zero | `R²_média` | RMSE Ridge / zero / média | Desvio das previsões | Média do treino | Norma dos coeficientes |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 2014 | 100 | −0,6590 | −0,6361 | 0,2098 / 0,1629 / 0,1640 | 0,0802 | −0,0009 | 0,0342 |
| 2015 | 10⁶ (limite) | **+0,0123** | **+0,0123** | 0,1780 / 0,1791 / 0,1791 | 0,0005 | −0,0048 | 0,0001 |
| 2016 | 10⁶ (limite) | −0,0391 | −0,0211 | 0,2488 / 0,2441 / 0,2463 | 0,0007 | −0,0086 | 0,0001 |
| 2017 | 10⁶ (limite) | **+0,0212** | **+0,0071** | 0,0894 / 0,0904 / 0,0898 | 0,0003 | 0,0065 | 0,0002 |
| 2018 | 10⁶ (limite) | **+0,0163** | **+0,0005** | 0,1723 / 0,1737 / 0,1723 | 0,0005 | 0,0074 | 0,0002 |
| 2019 | 10⁶ (limite) | **+0,0541** | **+0,0031** | 0,0614 / 0,0631 / 0,0615 | 0,0001 | 0,0112 | 0,0001 |
| 2020 | 10⁶ (limite) | **+0,0154** | **+0,0104** | 0,2047 / 0,2063 / 0,2058 | 0,0008 | 0,0119 | 0,0001 |
| 2021 | 10⁴ | **+0,0462** | −0,0237 | 0,1067 / 0,1093 / 0,1055 | 0,0136 | 0,0127 | 0,0081 |

### VALE3.SA

| Validação | `alpha` | R² contra zero | `R²_média` | RMSE Ridge / zero / média | Desvio das previsões | Média do treino | Norma dos coeficientes |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 2014 | 10⁵ | −0,0654 | −0,0142 | 0,0870 / 0,0843 / 0,0864 | 0,0032 | 0,0066 | 0,0008 |
| 2015 | 10⁴ | −0,1335 | −0,1341 | 0,1611 / 0,1514 / 0,1513 | 0,0122 | 0,0012 | 0,0037 |
| 2016 | 10⁶ (limite) | −0,0278 | −0,0292 | 0,2162 / 0,2133 / 0,2131 | 0,0005 | −0,0056 | 0,0001 |
| 2017 | 10⁶ (limite) | **+0,0508** | −0,0027 | 0,0886 / 0,0909 / 0,0884 | 0,0004 | 0,0090 | 0,0002 |
| 2018 | 10⁶ (limite) | **+0,0485** | **+0,0060** | 0,0835 / 0,0856 / 0,0838 | 0,0003 | 0,0120 | 0,0001 |
| 2019 | 10⁶ (limite) | **+0,0686** | **+0,0119** | 0,0749 / 0,0776 / 0,0754 | 0,0005 | 0,0131 | 0,0001 |
| 2020 | 10⁶ (limite) | **+0,0782** | −0,0015 | 0,1350 / 0,1406 / 0,1349 | 0,0010 | 0,0128 | 0,0002 |
| 2021 | 100 | −0,0080 | **+0,0023** | 0,0995 / 0,0992 / 0,0997 | 0,0128 | 0,0165 | 0,0339 |

Na v1, o maior desvio das previsões por ano foi de 0,008 a 0,080 na PETR4 e de 0,010 a 0,038 na VALE3, e a grade parava em 1000.

## 3. Filtros de desenvolvimento

| Ativo | Critério 3 (contra zero) | Critério 6 nas dobras (contra a média) | Resultado |
| --- | --- | --- | --- |
| PETR4.SA | 6 de 8 (mínimo 5): **atendido** | 5 de 8 (mínimo 5): **atendido** | Filtros atendidos; a abertura depende de nova decisão escrita (protocolo v2, seção 9) |
| VALE3.SA | 4 de 8: não atendido | 3 de 8: não atendido | Encerramento sem avaliação final (V2-7) |

**VALE3.SA.** Pela V2-7, o resultado deste ativo é: "A v2 não atendeu aos critérios de desenvolvimento necessários para abertura da avaliação final. Não houve evidência suficiente, segundo o protocolo, para habilitar o sinal." A Ridge superou o retorno zero em quatro dobras, mas a média histórica só em três. A ampliação da regularização não demonstrou o ganho incremental exigido para esta configuração.

## 4. `alpha` no limite e "praticamente a média"

- **Escolha no limite superior:** 10⁶ foi escolhido em 6 de 8 dobras da PETR4 e em 5 de 8 da VALE3. Pela V2-2, isso fica registrado e a grade não é ampliada. Nessas 11 escolhas, o erro interno em 10⁶ ainda era de 0,1% a 2,2% menor que em 10⁵.
- **Verificação nos resultados** (pedida na V2-1): nas dobras com `alpha` = 10⁶, as previsões ficaram praticamente constantes dentro do ano.
  - O desvio-padrão das previsões ficou entre 0,0001 e 0,0010, e a norma dos coeficientes perto de 10⁻⁴.
  - A média das previsões ficou a no máximo 0,0004 da média do alvo no treino.
  - Ou seja: com `alpha` = 10⁶, a Ridge virou, na prática, a média do treino, e não a média histórica expansiva. O afastamento médio em relação a esta última ficou entre 0,0006 e 0,0097.

## 5. Diagnóstico posterior: de onde vem o ganho contra a média

Este diagnóstico **não é critério** e não estava no protocolo. Foi calculado depois da rodada, só com os dados do desenvolvimento, para interpretar o critério 6. Ele compara a média histórica com uma previsão **constante igual à média do alvo no treino**, sem nenhuma variável:

| Ativo | Dobras em que a constante do treino supera a média histórica | Dobras em que a Ridge supera a média histórica | Dobras em que a Ridge supera a constante do treino, no `R²_média` |
| --- | ---: | ---: | --- |
| PETR4.SA | 7 de 8 (todas, menos 2016) | 5 de 8 | 2 de 8 (2015 e 2020) |
| VALE3.SA | 4 de 8 (2017, 2018, 2019 e 2021) | 3 de 8 | 3 de 8 (2014, 2018 e 2019) |

**Leitura.** Na PETR4, a previsão constante da média do treino, sem variáveis, atende à parte do critério 6 nas dobras com folga maior que a Ridge (7 de 8 contra 5 de 8). Portanto, o atendimento do critério 6 pela PETR4 no desenvolvimento **não pode ser atribuído às variáveis**. Ele resulta, em grande parte, da diferença entre duas médias:
- a do treino, constante dentro do ano e calculada sobre as amostras que sobram depois do embargo e do expurgo;
- a histórica expansiva, atualizada a cada data.

É o caso que o critério 6 pretendia excluir (proposta, seção 2): a referência escolhida, a média expansiva causal, não o exclui quando a Ridge converge para a média do treino.

**Consequência para a estratégia** (só datas de decisão do desenvolvimento): nas dobras com `alpha` = 10⁶, a regra `ŷ > 0,002` ficou 100% exposta ou 100% em caixa durante o ano inteiro. Na PETR4, isso aconteceu de 2015 a 2020, conforme a média do treino estivesse acima ou abaixo de `c`. É uma regra praticamente constante, não um sinal que mude com as variáveis.

## 6. Decisão necessária

Pelas regras do protocolo v2, os critérios foram fixados antes e não mudam. A PETR4 atendeu aos filtros dos critérios 3 e 6. O período final só pode ser aberto com nova decisão escrita e com as sete condições da seção 9 cumpridas. Cabe ao orientador decidir:

| Caminho | Consequência |
| --- | --- |
| (a) Não abrir o período final e encerrar a v2 | Preserva o período reservado. O relatório registra que a PETR4 atendeu formalmente aos filtros, mas por um mecanismo atribuível à média do treino, conforme o diagnóstico da seção 5. Essa limitação da referência do critério 6 fica como pergunta para uma versão futura |
| (b) Abrir o período final só para a PETR4 | Aplica os critérios 1 a 6 como fixados. Mesmo uma aprovação formal teria de ser lida à luz da seção 5: o ganho provavelmente viria da média do treino, não das variáveis. O período reservado seria consumido |

**Observação de implementação.** O código congelado só libera a lista de datas e a avaliação final quando **todos** os ativos atendem aos filtros (`executar_v2._desenvolvimento_v2_atende`). O protocolo avalia os critérios por ativo, mas não definiu a abertura parcial. O caminho (b) exigiria uma alteração registrada do código, com novo commit e teste, antes de qualquer abertura.

**Recomendação do desenvolvedor:** caminho (a). A finalidade do critério 6, confirmada na decisão do orientador, era verificar se as variáveis acrescentam informação útil, e o diagnóstico mostra que, na PETR4, o ganho nas dobras também aparece sem as variáveis. Abrir o período agora consumiria a reserva para testar um mecanismo que a própria hipótese da v2 não pretendia validar. A decisão é do orientador.

## 7. Arquivos

Os arquivos ficam em `experiments/preditivo/resultados/v2/`, que o Git ignora, e numa cópia fora do Git com lista de hashes:

| Arquivo | SHA-256 |
| --- | --- |
| `desenvolvimento_PETR4_SA.csv` | `c4a5fd70f4a449bae221553823a54e2ba0f5d283ad2298e256163f23052646db` |
| `desenvolvimento_VALE3_SA.csv` | `9435a40b1106a20f1d337498700945d5a306cede1156002018b289490a11832b` |
| `desenvolvimento_resumo.json` | `7fbdc42d12aaaf534df524ad0fcc3128e8e80dcee79f7b2384587df12df87836` |
| `reproducao_v1.json` | `21fcee10717df97581178ac67e60c83b97e476fc5967cf2ce1d0ff8701e8b810` |
