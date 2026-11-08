# Proposta do piloto preditivo v2

**Situação:** proposta aprovada com ajustes pelo orientador (V2-1 a V2-7, 08/11/2026, sujeita à confirmação original) e consolidada no [protocolo v2](protocolo_piloto_v2.md), que prevalece em caso de divergência · nenhum experimento novo executado · período final ainda não utilizado para avaliação preditiva ou seleção de modelos
**Base:** v1 encerrada por não elegibilidade (decisão D1, [encerramento](encerramento_v1.md)). Esta proposta usa só os resultados do desenvolvimento oficial da v1 (dobras de 2014 a 2021), já registrados em `experiments/preditivo/resultados/`. Todas as mudanças motivadas por esses resultados estão registradas aqui.

---

## 1. Hipótese

**Limitação investigada: o melhor valor da grade de `alpha` da v1 esteve frequentemente na fronteira.**

Evidências do desenvolvimento da v1:

- `alpha` = 1000, o limite superior da grade, foi escolhido em 14 dos 16 ajustes (7 de 8 em cada ativo).
- Nesses 14 ajustes, o erro das validações internas com `alpha` = 1000 foi menor que com `alpha` = 100, de 0,6% a 7,9%. O erro ainda caía no limite da grade; o comportamento além dele não é conhecido e é o que a v2 investiga.
- Nos dois ajustes em que a escolha foi `alpha` = 100 (PETR4 em 2014 e VALE3 em 2021), o erro interno não era monótono na grade.

Por isso, a v1 não distingue duas explicações para a falta de estabilidade:
- (a) as variáveis não trazem informação útil para o retorno dos 20 pregões seguintes;
- (b) há informação, mas a v1 não permitiu regularização suficiente para separá-la do ruído.

**Hipótese da v2:** "Investigar se uma grade mais ampla de regularização permite à Ridge obter ganho preditivo estável em relação ao retorno zero e à média histórica, mantendo os demais elementos do piloto." A fronteira da grade anterior justifica a investigação, mas não demonstra que o limite tenha causado a não elegibilidade da v1.

A hipótese é formulada para poder ser refutada. Se a v2 também não for elegível, a explicação (b) fica enfraquecida para esta configuração.

## 2. Mudança principal

**Ampliar a grade de `alpha` para cima, sem mexer no restante do modelo:**

| | Grade |
| --- | --- |
| v1 | 0,1 · 1 · 10 · 100 · 1000 |
| v2 (proposta) | 0,1 · 1 · 10 · 100 · 1000 · **10⁴ · 10⁵ · 10⁶** |

- **Por que até 10⁶:** a intenção é cobrir o caminho entre o modelo da v1 e uma previsão quase constante. Como ilustração, e não como propriedade garantida para todos os coeficientes: com variáveis padronizadas e de 1.234 a 2.973 amostras de treino, uma ordem de grandeza do encolhimento é 0,1 em 10⁴ e 0,001 em 10⁶. O encolhimento de cada direção depende dos autovalores das variáveis. Se as previsões ficarem próximas da média, isso será verificado nos registros (protocolo v2, seção 4), não presumido.
- **Regras mantidas:** a escolha continua por 3 validações internas anuais, e o empate continua indo para o maior `alpha`.
- **Regra fixada antes:** se a escolha atingir 10⁶, o fato é registrado, mas a grade **não** é ampliada outra vez na v2.

### Risco de aprovação degenerada e salvaguarda

No desenvolvimento da v1, a média histórica teve erro menor que o retorno zero em 6 das 8 dobras, nos dois ativos (PETR4: 2015 e 2017 a 2021; VALE3: 2015 a 2020). Já o Ridge teve erro menor que a média histórica em só 2 das 8 dobras em cada ativo (PETR4: 2015 e 2020; VALE3: 2019 e 2021).

Com a grade ampliada, a Ridge pode se aproximar de uma previsão quase constante, próxima da média do alvo no treino, e passar no critério 3, que compara com o retorno zero, sem nenhuma contribuição das variáveis. A média do treino não é a mesma série que a média histórica expansiva usada como referência (protocolo v2, seção 5). Nesse caso, a estratégia `ŷ > c` viraria uma regra quase constante: sempre exposto ou sempre no caixa, conforme a média do treino fique acima ou abaixo de `c`. Isso não é um sinal preditivo.

Por isso, a ampliação da grade só é interpretável junto com um critério que exija ganho sobre a média histórica (seção 4, critério 6). Esse critério não aumenta as chances de aprovação; ele as reduz. Ele não altera nenhum limiar da v1.

### Alternativas consideradas e não escolhidas

| Alternativa | Motivo para não escolher agora |
| --- | --- |
| Trocar ou ampliar variáveis | Abre muitos graus de liberdade. Sem resolver a regularização, não se sabe se as variáveis atuais já trazem informação |
| Trocar o modelo (não linear) | Mais parâmetros e mais risco de sobreajuste, e mudaria mais de um elemento ao mesmo tempo. A preferência por regularização forte na v1 é compatível com excesso de variância, mas essa é uma interpretação possível, não uma conclusão |
| Mudar o horizonte | Muda a pergunta, e os resultados deixariam de ser comparáveis aos da v1 |
| Trocar ativos | Não responde à limitação observada e quebra a comparação |
| Relaxar o critério 3 (menos de 5 de 8) | Mudaria o limiar só para aprovar, o que a D1 veda |

## 3. Elementos preservados

| Elemento | v2 |
| --- | --- |
| Ativos | PETR4.SA e VALE3.SA, avaliados separadamente |
| Dados | Mesmo snapshot `snap-20261108-01` (manifesto `6985328407ba…`), sem nova coleta |
| Política de qualidade | 1.0 (`f75598b06fa9…`), mesma visão derivada |
| Variáveis | As 12 da v1, com os mesmos cálculos e defasagens |
| Alvo e horizonte | `y_t = P(t+21)/P(t+1) − 1`, 20 pregões |
| Modelo | Ridge com `StandardScaler` e intercepto |
| Seleção do `alpha` | 3 validações internas anuais; empate vai para o maior |
| Dobras, embargo e expurgo | 8 dobras anuais de 2014 a 2021; embargo de 20 pregões; expurgo por datas |
| Período final e reestimações | Do 21º pregão de 2022 a 30/10/2026; reestimação anual, com embargo só na fronteira de 2022 |
| Referências | Retorno zero e média histórica expansiva |
| Estratégia e custos | Exposto se `ŷ > c`, com `c` = 0,002; caixa no CDI; custo de 0,10% por lado; sensibilidade de 0 a 0,30% |
| Testes | Diebold-Mariano unilateral com Newey-West (19 defasagens), `p` < 0,10 estrito, T ≥ 200; Clark-West só como diagnóstico |

A única diferença de modelagem é a grade. A v2 é comparável dobra a dobra com a v1: nos valores comuns às duas grades, os ajustes são idênticos.

## 4. Critérios

Definidos antes de qualquer teste da v2:

| Critério | v2 |
| --- | --- |
| 1. R² fora da amostra > 0 no período final, em relação ao retorno zero | Mantido |
| 2. Diebold-Mariano contra o retorno zero | Mantido |
| 3. R² > 0 em pelo menos 5 das 8 dobras | Mantido, com a ressalva sobre independência (seção 5) |
| 4. Condição econômica (A∧B)∨C | Mantido |
| 5. Robustez com custo em dobro | Mantido |
| **6. Ganho sobre a média histórica (novo, proposto)** | R² fora da amostra > 0 no período final **em relação à média histórica expansiva**, e o mesmo em pelo menos 5 das 8 dobras |

O critério 6 segue a forma dos critérios 1 e 3, com a média no lugar do retorno zero. Ele é cumulativo como os outros. Diebold-Mariano contra a média fica como diagnóstico, salvo decisão em contrário (seção 8).

Sem o critério 6, um resultado elegível poderia vir só da convergência para a média, e a hipótese da seção 1 não seria testada.

## 5. Avaliação: separação entre desenvolvimento e período final

- **O desenvolvimento da v2 não é independente.** As dobras de 2014 a 2021 são as mesmas da v1, e a mudança principal foi motivada pelos resultados dessas dobras. Os critérios 3 e 6 continuam obrigatórios, mas atendê-los no desenvolvimento não é evidência independente.
- **A única evidência independente da v2 é o período final reservado**: "período ainda não utilizado para avaliação preditiva ou seleção de modelos". Os arquivos foram acessados na coleta, na integridade e nos ajustes (seção 6).
- **Ordem obrigatória:**
  1. Protocolo v2 redigido, com esta proposta incorporada e hash registrado.
  2. Confirmação do orientador.
  3. Implementação e testes.
  4. Desenvolvimento oficial da v2.
  5. Relatório do desenvolvimento.
  6. Decisão do orientador sobre abrir o período final.
  7. Lista de datas elegíveis.
  8. Avaliação final, executada uma única vez.
- **Se a v2 não atender aos critérios 3 ou 6 no desenvolvimento,** ela é encerrada como a v1, sem abrir o período final.
- **Separação técnica:** a v2 tem configuração, registro e trava próprios. A configuração, a trava e o `encerramento_v1.json` da v1 continuam como estão, e os hashes da v1 não mudam.

## 6. Período reservado: acessos e finalidades

Do 21º pregão de 2022 a 30/10/2026:

| Acesso | Finalidade | Resultado preditivo produzido? |
| --- | --- | --- |
| Coleta da v1 | Baixar e congelar as séries; calcular hashes, contagens e cobertura | Não |
| Verificações de integridade da coleta | Triagem de proventos, desdobramentos, faixa OHLC e variações do fator, na série inteira | Não |
| Reconstrução do fator de ajuste (política 1.0) | O fator de cada data depende de proventos e fechamentos posteriores, inclusive do período final | Não |
| `qualidade` e `desenvolver` da v1 | Carregar o arquivo inteiro e truncá-lo antes do 21º pregão de 2022 | Não |
| Esta proposta | Usou só os resultados das dobras de 2014 a 2021 | Não |
| `listar-datas` e `final` | Nunca executados | — |

Não há previsões, alvos avaliados nem métricas do período final, e nenhuma decisão da v2 foi tomada com base nele. Estado registrado em `experiments/preditivo/encerramento_v1.json`.

## 7. Custo esperado

Previsão de esforço, não compromisso medido.

- **Implementação** (de 1 a 2 dias de trabalho, com testes):
  - parametrizar a versão (configuração, registro e trava por versão), sem mudar os arquivos com hash da v1;
  - grade ampliada na configuração da v2;
  - critério 6 em `elegibilidade.py`, com o cálculo do R² estendido a uma referência informada (hoje ele usa só o retorno zero), sem mudar o resultado da v1;
  - registro, em cada ajuste, do fator de encolhimento efetivo e do quanto a previsão se afasta da média do treino;
  - testes: v1 inalterada nos valores comuns da grade, regra de não ampliar a grade de novo, critério 6 e separação por versão.
- **Documentação:** protocolo v2, que deriva do v1 e muda só as seções da grade e dos critérios; o relatório de desenvolvimento segue o modelo da v1.
- **Computação:** desprezível. São 8 valores de `alpha` em vez de 5 (cerca de 1,6 vez o custo da v1), e o desenvolvimento da v1 levou poucos segundos por ativo. A avaliação final, se autorizada, também leva segundos.
- **Dados:** nenhuma coleta nova, nenhuma nova conferência na B3 e nenhuma mudança na política de qualidade.

## 8. O que depende de confirmação real do orientador

| # | Decisão | Proposta |
| --- | --- | --- |
| V2-1 | Hipótese e mudança principal | Grade de `alpha` ampliada até 10⁶, sem outra mudança de modelagem |
| V2-2 | Regra para o limite da nova grade | Registrar e não ampliar outra vez na v2 |
| V2-3 | Critério 6 (ganho sobre a média histórica) | Adotar como critério obrigatório, nos moldes dos critérios 1 e 3. Alternativa: só diagnóstico, com a restrição de que um resultado elegível por convergência à média não habilita sinal |
| V2-4 | Diebold-Mariano contra a média | Só diagnóstico |
| V2-5 | Desenvolvimento não independente | Manter os critérios 3 e 6 obrigatórios e declarar a ressalva no relatório |
| V2-6 | Uso do período reservado pela v2 | Só depois do protocolo v2 fechado, do desenvolvimento elegível e de nova decisão de abertura |
| V2-7 | Encerramento sem abertura | Se os critérios 3 ou 6 falharem no desenvolvimento, encerrar a v2 sem abrir o período final |

**Decisão (08/11/2026):** as sete propostas foram aprovadas, com o critério 6 obrigatório (a alternativa de diagnóstico não foi adotada) e com as correções de redação já incorporadas acima. Até a confirmação original, nada da v2 é implementado ou executado.
