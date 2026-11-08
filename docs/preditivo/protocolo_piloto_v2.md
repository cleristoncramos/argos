# Protocolo do piloto preditivo — v2

**Status:** consolidado e **confirmado** pelo orientador em 08/11/2026 (V2-1 a V2-7, com as condições da confirmação) · **Congelamento:** no commit que antecede o desenvolvimento oficial (seção 12) · **Criado em:** 08/11/2026
**Origem:** [`proposta_piloto_v2.md`](proposta_piloto_v2.md) e [`../pibiti/decisoes_orientador.md`](../pibiti/decisoes_orientador.md), entrada "Autorização do piloto v2". **Versão anterior:** [`protocolo_piloto_v1.md`](protocolo_piloto_v1.md), v1 encerrada por não elegibilidade ([encerramento](encerramento_v1.md)).

> **Alcance da autorização.** A decisão autoriza consolidar este protocolo e, depois da confirmação real, implementar, testar e executar o desenvolvimento da v2. Ela não autoriza:
> - abrir o período final;
> - publicar previsões;
> - habilitar sinais no aplicativo;
> - alterar o prompt histórico v0.6.
>
> A ampliação da grade é uma investigação justificada, não uma promessa de melhora.

---

## 1. Hipótese

> Investigar se uma grade mais ampla de regularização permite à Ridge obter ganho preditivo estável em relação ao retorno zero e à média histórica, mantendo os demais elementos do piloto.

**Motivação, a partir do desenvolvimento da v1:**
- O melhor valor da grade anterior esteve na fronteira em 14 dos 16 ajustes: `alpha` = 1000, escolhido 7 vezes em cada ativo.
- Nesses 14 ajustes, o erro das validações internas em `alpha` = 1000 foi menor que em `alpha` = 100.

Isso justifica investigar a grade além do antigo limite, mas não demonstra que o limite tenha causado a não elegibilidade da v1. O comportamento além dele é justamente o que a v2 investiga.

## 2. Elementos preservados

Ficam incorporadas sem alteração as seções abaixo do protocolo v1 (SHA-256 `e7f2d5e4456b6c77a6c1f23efe1828ab5680c91f0cfcd11afc8ffae102153a30`) e a nota metodológica (SHA-256 `be0747afd0671f2ef09ec602730be9568802d6d85540aec9b0d1a72d0f4c6e94`):

| Protocolo v1 | Conteúdo |
| --- | --- |
| 1 | Ativos: PETR4.SA e VALE3.SA, avaliados separadamente |
| 2 | Alvo `y_t = P_(t+21)/P_(t+1) − 1`, horizonte de 20 intervalos, datas de cada amostra |
| 3 | Série ajustada e consistência de ajuste. Dados: **o mesmo snapshot `snap-20261108-01`** (manifesto `6985328407ba456ada6c92872382e00f0109a772a904bbf477e3b5a006dd272c`) e **a mesma política de qualidade 1.0** (`f75598b06fa9a1100fecc5783b78c1874642686223ecb5b60e05096cf8e88975`), sem nova coleta |
| 4 | As 12 variáveis, com defasagens e padronização só no treino |
| 5 | Períodos: desenvolvimento de 2008 a 2021; período final do 21º pregão de 2022 até o corte de 30/10/2026 |
| 6 | Dobras anuais de 2014 a 2021, regra de fronteira (embargo de 20 pregões e expurgo por datas), período final sequencial e embargo só na fronteira de 2022 |
| 7 | Referências e modelo Ridge, **exceto a grade de `alpha`** (seção 3 deste protocolo). Escolha por 3 validações internas anuais; empate vai para o maior `alpha` |
| 8 | Estratégia `ŷ > c` com `c` = 0,002, custos de 0,10% por lado, sensibilidade de 0 a 0,30% e caixa no CDI |
| 9.1 e 9.2 | Métricas e teste Diebold-Mariano contra o retorno zero (nota N1 a N5) |
| 10 e 11 | Interrupção e regras de versão; o registro passa a ser próprio da v2 (seção 11 deste protocolo) |

Nenhuma outra mudança de modelagem é introduzida.

## 3. Mudança principal: grade de `alpha`

| Versão | Grade |
| --- | --- |
| v1 | 0,1 · 1 · 10 · 100 · 1000 |
| **v2** | 0,1 · 1 · 10 · 100 · 1000 · 10⁴ · 10⁵ · 10⁶ |

**Limite fixo (V2-2).** Se 10⁶ for selecionado, o fato é registrado como escolha no limite superior. Isso não permite:
- acrescentar valores durante a execução oficial;
- repetir a seleção com outra grade e substituir o resultado;
- escolher uma configuração depois de consultar o período final.

Uma pergunta adicional pode ser proposta depois, sem modificar a v2.

**Encolhimento, só como ilustração.** Com variáveis padronizadas e de 1.234 a 2.973 amostras de treino, uma ordem de grandeza aproximada do fator de encolhimento é 0,1 em 10⁴ e 0,001 em 10⁶. Isso não é propriedade garantida para todos os coeficientes, porque o encolhimento de cada direção depende dos autovalores da matriz das variáveis. Se as previsões ficarem "praticamente iguais à média", isso precisa ser verificado nos registros da seção 4, não presumido a partir do valor de `alpha`.

## 4. Registro por ajuste

Além do que a v1 já registra (`alpha`, erros internos por `alpha`, número de amostras de treino e de avaliação, embargo, intercepto e indicação de escolha no limite), cada ajuste registra:

| Campo | Definição |
| --- | --- |
| `previsoes_media`, `previsoes_desvio` | Média e desvio-padrão das previsões da Ridge nas datas avaliadas do ano |
| `media_alvo_treino` | Média do alvo nas amostras de treino daquele ajuste |
| `afastamento_media_historica` | Nas mesmas datas: média de `|ŷ_Ridge − ŷ_média|` e raiz da média de `(ŷ_Ridge − ŷ_média)²`, em que `ŷ_média` é a referência da seção 5 |
| `norma_coeficientes` | Norma euclidiana dos coeficientes na escala padronizada, sem o intercepto |
| `alpha_no_limite_da_grade` | Verdadeiro se o `alpha` escolhido for 10⁶ |

## 5. Referência de média histórica e R² contra a média

**Média histórica (definição causal da v1, preservada):** em cada data de decisão `t`, a média dos alvos com `label_end_date ≤ t`, isto é, só alvos integralmente realizados e disponíveis naquele momento (`modelos.prever_media_historica`).

Ela **não** é a média do alvo no treino do último ajuste. As duas séries são registradas e tratadas separadamente:
- a média do treino é constante dentro do ano e exclui as amostras removidas por embargo e expurgo;
- a média histórica é atualizada a cada data.

**R² fora da amostra em relação à média histórica:**

```
R²_média = 1 − Σ_t (y_t − ŷ_Ridge,t)² / Σ_t (y_t − ŷ_média,t)²
```

- Ridge e referência são avaliadas **nas mesmas datas**: no período final, a lista de datas elegíveis do critério 1; em cada dobra, as datas avaliadas do ano com alvo realizado.
- O resultado é **não calculável**, e não atende ao critério, quando:
  - o denominador for zero;
  - houver valor não finito;
  - faltar alguma previsão, da Ridge ou da referência, em qualquer data da amostra.
- Nenhum arredondamento converte resultado nulo, negativo ou não calculável em aprovação.

Superar a média é uma condição operacional de ganho incremental neste protocolo. Não demonstra relação causal entre indicadores e retornos.

## 6. Critérios de elegibilidade

Avaliados por ativo. O sinal só é elegível se **todos** forem atendidos:

| # | Critério | Situação |
| --- | --- | --- |
| 1 | R² fora da amostra estritamente maior que zero em relação ao retorno zero, no período final | Igual à v1 |
| 2 | Diebold-Mariano contra o retorno zero, com `p` < 0,10 estrito | Igual à v1 e à nota |
| 3 | R² > 0 em relação ao retorno zero em pelo menos 5 das 8 dobras | Igual à v1 (filtro de desenvolvimento) |
| 4 | Condição econômica (A∧B)∨C com o custo-base | Igual à v1 |
| 5 | Critério 4 mantido com o dobro do custo | Igual à v1 |
| **6** | **`R²_média` estritamente maior que zero no período final e em pelo menos 5 das 8 dobras** | **Novo, obrigatório e cumulativo (V2-3)** |

O critério 6 impede que a aproximação da Ridge a uma previsão quase constante conte como evidência de contribuição das variáveis.

**Filtros de desenvolvimento.** A parte de dobras dos critérios 3 e 6 é verificada antes de qualquer abertura. Se algum deles falhar, aplica-se a seção 10.

## 7. Diebold-Mariano contra a média (V2-4): só diagnóstico

O teste usa a mesma especificação da nota, com diferencial `d_t = (y_t − ŷ_média,t)² − (y_t − ŷ_Ridge,t)²`, unilateral a favor da Ridge, Newey-West com 19 defasagens e as mesmas datas. Regras:
- não substitui o critério 2;
- não oferece uma segunda oportunidade de aprovação;
- não pode ser escolhido como resultado principal por ser mais favorável;
- é reportado sempre, inclusive quando não favorece a Ridge;
- é interpretado com as limitações da nota para comparação de previsões estimadas.

## 8. Não independência do desenvolvimento (V2-5)

Todo relatório da v2 deve conter:

> A configuração da v2 foi proposta a partir dos resultados de desenvolvimento da v1. As mesmas dobras foram reutilizadas para seleção e avaliação de desenvolvimento. Seus resultados não constituem evidência independente de generalização.

O atendimento dos critérios 3 e 6 não é descrito como confirmação independente da hipótese.

## 9. Período reservado e abertura (V2-6)

**Designação:** "Período ainda não utilizado para avaliação preditiva ou seleção de modelos." Os arquivos foram acessados na coleta, nas verificações de integridade e na reconstrução de ajustes, conforme o [encerramento da v1](encerramento_v1.md), seção 3.

**Condições de abertura**, todas obrigatórias:
1. protocolo v2 confirmado;
2. configuração e dados identificados por hashes;
3. implementação e testes concluídos;
4. desenvolvimento oficial concluído;
5. critérios 3 e 6 atendidos no desenvolvimento;
6. relatório de desenvolvimento emitido;
7. nova decisão escrita de abertura.

Depois dessa decisão, gera-se a lista de datas elegíveis pelas regras da nota (N1), antes de calcular qualquer previsão ou métrica final. Uma vez conhecidos os resultados finais, não é permitido modificar grade, critérios ou estratégia e reutilizar o mesmo resultado como nova confirmação independente.

## 10. Encerramento sem abertura (V2-7)

Se os critérios 3 ou 6 falharem no desenvolvimento oficial, a v2 é encerrada sem avaliação final, com a redação:

> A v2 não atendeu aos critérios de desenvolvimento necessários para abertura da avaliação final. Não houve evidência suficiente, segundo o protocolo, para habilitar o sinal.

Não há obrigação de abrir o período final para completar tabelas nem de criar uma v3.

Se a Ridge se aproximar da média e superar o retorno zero, mas não atender ao critério 6, o resultado é informativo: a ampliação da regularização não demonstrou o ganho incremental exigido para esta configuração.

## 11. Separação técnica e preservação da v1

- **Configuração, registro e travas próprios da v2:**
  - configuração em arquivo distinto;
  - registro em `registro_v2.jsonl`;
  - condições de abertura, marca de uso e lista de datas elegíveis com arquivos próprios;
  - resultados identificados pela versão.
- **Funções compartilhadas:** a v2 pode usar as funções testadas da v1.
- **v1 preservada:**
  - `config.py`, `registro.jsonl`, `encerramento_v1.json`, os resultados e os hashes arquivados da v1 não mudam;
  - a trava de encerramento da v1 continua valendo;
  - nenhum comando da v2 sobrescreve resultados oficiais de qualquer versão.
- **Equivalência nos valores comuns das grades.** Com a mesma configuração numérica, a v2 restrita à grade da v1 deve reproduzir:
  - os erros internos;
  - os `alpha` escolhidos;
  - as previsões e as métricas oficiais da v1 por dobra.

  A tolerância documentada é de 10⁻¹⁰ de diferença relativa e 10⁻¹² absoluta. Diferenças acima dela precisam de justificativa numérica explícita, ou o desenvolvimento da v2 não prossegue.

## 12. Condições antes do desenvolvimento oficial

| # | Condição | Situação |
| --- | --- | --- |
| 1 | Protocolo v2 consolidado | **Feito** (esta versão) |
| 2 | Confirmação real da decisão do orientador | **Feito** (08/11/2026) |
| 3 | Separação por versão implementada, com testes da v1 inalterada e da equivalência | **Feito**: `config_v2.py`, `executar_v2.py`, `registro_v2.jsonl`, `condicoes_abertura_v2.json`; a reprodução da v1 com dados reais passou (diferença máxima de cerca de 10⁻¹⁶) |
| 4 | Testes com dados sintéticos: grade, limite fixo, critério 6, registros da seção 4, casos não calculáveis | **Feito**: `experiments/preditivo/tests/test_v2.py` |
| 5 | Configuração e código congelados, com hashes deste protocolo, da nota, da configuração v2, do manifesto e da política | No commit de congelamento; os hashes entram em cada linha de `registro_v2.jsonl` |

**Rodada única e sem ensaio.** O desenvolvimento oficial da v2 roda uma única vez: o comando recusa código não commitado (só são aceitos `docs/versao_congelada.md` e o próprio `registro_v2.jsonl`), repete a reprodução da v1 antes de começar, confere os erros internos dos `alpha` comuns com os da v1 e não sobrescreve resultados oficiais. Não há ensaio da v2 com dados reais antes da rodada oficial; o único teste com dados reais é a reprodução da v1, que não produz nenhum resultado da grade ampliada.

**Sequência autorizada:**
1. consolidar o protocolo v2;
2. obter a confirmação real;
3. implementar a separação por versão;
4. executar testes com dados sintéticos e de desenvolvimento;
5. congelar configuração e código;
6. executar o desenvolvimento oficial;
7. emitir o relatório;
8. decidir sobre encerramento ou abertura do período final.

## 13. Custo previsto

É uma previsão de esforço, não uma medida.
- **Implementação:** de 1 a 2 dias de trabalho, com testes.
- **Processamento:** cerca de 1,6 vez o desenvolvimento da v1, que levou poucos segundos por ativo, por causa dos 8 valores de `alpha` em vez de 5.
- **Dados:** sem coleta, conferência ou mudança de política.

---

## Histórico

| Data | Versão | Mudança |
| --- | --- | --- |
| 08/11/2026 | v2, confirmada | Confirmação do orientador; seção 12 atualizada com a implementação, os testes e a reprodução da v1 (sem mudança no experimento) |
| 08/11/2026 | v2, consolidada | Criação a partir da proposta e da decisão V2-1 a V2-7: grade ampliada até 10⁶ com limite fixo; critério 6 contra a média histórica causal; Diebold-Mariano contra a média só como diagnóstico; não independência declarada; período reservado com abertura condicionada; encerramento sem abertura; separação por versão |
