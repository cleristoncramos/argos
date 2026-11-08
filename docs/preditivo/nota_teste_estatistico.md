# Nota metodológica — teste estatístico do piloto preditivo

**Status:** decisões N1 a N5 aprovadas pelo orientador em 08/11/2026 e incorporadas · confirmação original a arquivar · faz parte do procedimento a congelar
**Protocolo:** [`protocolo_piloto_v1.md`](protocolo_piloto_v1.md), seções 9.2 e 9.3 (critérios 1 e 2) e condição 7 da seção 12.
**Decisão:** [`../pibiti/decisoes_orientador.md`](../pibiti/decisoes_orientador.md), entrada "Nota metodológica do teste estatístico (08/11/2026)".

Esta nota especifica o teste aprovado (Diebold-Mariano, `p < 0,10` a favor do candidato) e registra a revisão de adequação. Ela foi escrita **antes** de qualquer resultado do período final. O procedimento é um **critério exploratório de elegibilidade** do piloto local; não equivale a certificação estatística de uma recomendação de investimento.

---

## 1. Amostra (N1, aprovada)

| Item | Definição |
| --- | --- |
| Modelos comparados | Candidato (Ridge) contra a referência de retorno zero (`ŷ_zero = 0`). A média histórica não entra no teste; é só referência descritiva |
| Unidade | Cada ativo separadamente (`PETR4.SA` e `VALE3.SA`); **nunca** um teste agregado |
| Amostra | **Todas as datas previstas para avaliação no período final com alvo integralmente realizado**, uma previsão por pregão. É a mesma amostra do R² fora da amostra do critério 1 |
| Previsão de cada data | A do ajuste vigente naquela data (avaliação sequencial, seção 6.3 do protocolo), com a identificação do modelo vigente registrada |

As datas de decisão da estratégia, a cada 20 pregões, servem ao backtest e à acurácia de direção. Elas não substituem a amostra diária do teste.

**Lista de datas elegíveis.** Antes da avaliação final, a lista é gerada a partir do calendário, do horizonte e da disponibilidade do alvo (`label_end_date ≤ data de corte`), e fixada **sem consultar erros nem desempenho do candidato**. A lista e seu hash entram no manifesto da configuração.

**Regras:**
- não selecionar datas favoráveis;
- não excluir observações por terem erros elevados;
- não agregar PETR4 e VALE3 num único teste;
- registrar o modelo vigente em cada previsão;
- distinguir data sem alvo realizado (fora da lista) de falha na geração da previsão (data da lista sem previsão).

Se faltar a previsão em uma data da lista, ela **não** é descartada para calcular o teste numa amostra mais conveniente: a falha é registrada e tratada pela seção 4.

## 2. Função de perda e diferencial

Para cada data `t` da lista, com `y_t` o alvo realizado e `ŷ_t` a previsão do candidato:

| Grandeza | Fórmula |
| --- | --- |
| Perda da referência | `L_zero,t = y_t²` |
| Perda do candidato | `L_cand,t = (y_t − ŷ_t)²` |
| Diferencial | `d_t = y_t² − (y_t − ŷ_t)²` |

**Convenção de sinal:** `d_t > 0` significa que o candidato errou menos naquela data; média positiva favorece o candidato.

**Relação com o critério 1.** O R² fora da amostra é `1 − Σ L_cand / Σ L_zero = d̄ / média(L_zero)`. Quando a perda média da referência é positiva, o R² tem o mesmo sinal de `d̄`, e essa coerência é verificada por teste. **Se `Σ L_zero = 0`, o R² é "não calculável"**, e o critério 1 não é atendido.

## 3. Hipóteses e estatística (N2, aprovada)

| Item | Definição |
| --- | --- |
| Hipótese nula | `E[d_t] ≤ 0`: o candidato não tem perda esperada menor que a referência |
| Hipótese alternativa | `E[d_t] > 0`: o candidato tem perda esperada menor (unilateral) |
| Estatística | `DM = d̄ / √(V̂ / T)`, com `T` o número de datas da lista e `d̄` a média de `d_t` |
| Variância de longo prazo | `V̂ = γ̂_0 + 2 Σ_(j=1..L) w_j γ̂_j`, com `γ̂_j` a autocovariância amostral de `d_t` na defasagem `j`, **centrada em `d̄` e dividida por `T`** |
| Defasagens | `L = 19` |
| Pesos | Bartlett (Newey-West): `w_j = 1 − j / (L + 1)` |
| p-valor | `p = 1 − Φ(DM)`, com `Φ` a distribuição normal padrão |
| Decisão | Critério 2 atendido **somente se `p < 0,10`** (estrito). `p = 0,10` não atende. A decisão usa o valor em precisão completa, nunca o arredondado das tabelas |

**Justificativas, como escolhas operacionais fixadas para este piloto:**
- **19 defasagens** correspondem à sobreposição mecânica do horizonte de 20 intervalos. Não se afirma que essa escolha capture toda a dependência temporal possível dos diferenciais de perda.
- **Pesos de Bartlett** mantêm a variância estimada não negativa. Os pesos uniformes da formulação original podem produzir variância negativa em amostras finitas.
- **Normal padrão, sem correção de Harvey-Leybourne-Newbold** no p-valor de decisão, para não abrir uma escolha a mais. Isso não garante que o tamanho da amostra elimine os problemas de aproximação. A versão corrigida pode ser apresentada só como informação complementar.

## 4. Casos não calculáveis (N3, aprovada)

O critério 2 é registrado como **"não calculável"** e tratado como **não atendido** quando:

| Caso | Registro |
| --- | --- |
| `T < 200` | `Status: não calculável. Motivo: amostra inferior ao mínimo previsto. Critério 2: não atendido.` |
| Variância de longo prazo nula | Motivo: variância nula. Série constante quando a amplitude (máximo − mínimo) é no máximo 10⁻¹² vezes o maior valor absoluto (tolerância relativa à escala, fixada antes de qualquer resultado); absorve resíduos de arredondamento sem apagar variações pequenas e reais |
| Variância não finita, ou erro numérico no cálculo | Motivo: erro numérico, registrado separadamente da variância nula |
| Entradas não finitas (`y_t` ou `ŷ_t`) | Motivo: entrada não finita |
| Previsão ausente em data da lista | Motivo: previsão ausente, com as datas |
| Desalinhamento entre alvo e previsão (datas diferentes ou fora da lista) | Motivo: desalinhamento, com as datas |

O mínimo de 200 datas é um **requisito operacional** do piloto. Não é prova de suficiência estatística, de independência das observações nem de poder adequado.

É proibido ajustar a variância ou remover datas para obter um p-valor utilizável.

## 5. Revisão de adequação: comparação aninhada (N4, aprovada)

**O ponto.** O retorno zero é um caso particular do candidato (a Ridge com todos os coeficientes nulos), uma comparação **aninhada**. Nesse caso, mesmo quando as variáveis não ajudam a prever, o candidato estima coeficientes, e esse ruído de estimação aumenta seu erro.

**Limitação registrada (texto aprovado):**

> A literatura sobre comparações aninhadas identifica problemas de distribuição e possível conservadorismo de testes baseados no diferencial não ajustado de perdas (Clark e McCracken, 2001; Clark e West, 2007).
>
> No presente piloto, que utiliza Ridge, seleção temporal de regularização e reestimação sequencial, não se assume que o nível nominal de 10% corresponda exatamente à taxa efetiva de falso positivo.
>
> O teste será utilizado como filtro exploratório previamente especificado, em conjunto com os demais critérios, com essa limitação registrada.

A aprovação autoriza o uso experimental do procedimento; não declara validade inferencial exata para toda configuração da Ridge. Um estudo de simulação do tamanho e do poder do teste fica como extensão metodológica possível, não exigida neste piloto.

**Também considerado:** o arcabouço de Giacomini e White (2006) valida testes do tipo Diebold-Mariano para comparar métodos de previsão, estimação incluída, mas pressupõe janela de estimação móvel de tamanho fixo. O piloto usa janela expansível (protocolo, seção 6.1), então esse arcabouço não se aplica diretamente.

**Não há troca de teste** depois da abertura dos resultados finais.

## 6. Clark-West como diagnóstico complementar (N5, aprovada)

Diferencial ajustado, que soma de volta o quadrado da distância entre as duas previsões (a referência prevê zero):

`f_t = y_t² − (y_t − ŷ_t)² + ŷ_t²`

Mesma estatística, variância, defasagens, hipótese unilateral e casos não calculáveis das seções 3 e 4, aplicadas a `f_t`.

O resultado:
- não substitui o Diebold-Mariano;
- não altera a elegibilidade;
- não oferece uma segunda chance de aprovação;
- é apresentado independentemente de favorecer ou não o candidato;
- vem com as limitações de aplicação ao procedimento regularizado explicitadas.

Se o Clark-West for significativo e o Diebold-Mariano não, o relatório registra a **divergência entre os diagnósticos**. Ele não conclui que foi comprovado um ganho real encoberto pelo primeiro teste: o ajuste de Clark-West trata o ruído adicional de estimação em comparações aninhadas, mas sua interpretação depende das condições de aplicação.

## 7. Implementação e testes

A função fica em `experiments/preditivo/` e é pura. Recebe `datas`, `y`, `ŷ`, a lista de datas elegíveis e `L`, e devolve `d̄`, `V̂`, `DM`, `p` e o status (`ok` ou `não calculável`, com o motivo).

**Testes da rotina matemática**, com amostras pequenas e independentes do mínimo operacional (o mínimo de 200 é um parâmetro, desligável nesses testes):
- exemplo numérico conferido à mão: `γ̂_j`, pesos, `V̂`, `DM` e `p`;
- convenção de sinal: `ŷ = y` dá `d̄ > 0`; `ŷ = 0` dá `d̄ = 0` e variância nula;
- `d_t` constante dá variância nula, registrada como tal (e não como erro numérico);
- `V̂` nunca negativa em séries aleatórias (propriedade dos pesos de Bartlett);
- coerência de sinal entre `d̄` e R² quando a perda média da referência é positiva; denominador nulo dá R² "não calculável";
- limiar estrito: `p = 0,10` exato não atende;
- Clark-West calculado com a mesma rotina sobre `f_t`.

**Testes do requisito operacional:**
- amostra com menos de 200 datas dá "não calculável" por amostra insuficiente;
- entradas não finitas (`NaN`, infinito) dão "não calculável" por entrada não finita;
- previsão ausente em data da lista dá "não calculável" por previsão ausente, sem recalcular numa amostra menor;
- datas de previsão diferentes das da lista dão "não calculável" por desalinhamento.

**Registro:** o commit da implementação e o hash da configuração final (incluindo a lista de datas elegíveis) entram no manifesto antes da avaliação final.

## 8. Decisões aprovadas

| ID | Decisão |
| --- | --- |
| N1 | Amostra diária completa previamente elegível, por ativo, igual à do R² |
| N2 | p-valor unilateral pela normal padrão, com `p < 0,10` estrito, HAC com pesos de Bartlett e 19 defasagens |
| N3 | Mínimo operacional de 200 datas; casos não calculáveis não atendem ao critério |
| N4 | Diebold-Mariano mantido como filtro exploratório, com a limitação inferencial explícita |
| N5 | Clark-West só como diagnóstico, sem efeito sobre a elegibilidade |

A implementação que reproduzir exatamente estas definições não exige novas decisões sobre N1 a N5. Qualquer mudança substantiva é resolvida antes da abertura dos resultados finais.

## Referências

- Clark, T. E.; McCracken, M. W. Tests of equal forecast accuracy and encompassing for nested models. *Journal of Econometrics*, v. 105, n. 1, p. 85–110, 2001.
- Clark, T. E.; West, K. D. Approximately normal tests for equal predictive accuracy in nested models. *Journal of Econometrics*, v. 138, n. 1, p. 291–311, 2007.
- Diebold, F. X.; Mariano, R. S. Comparing predictive accuracy. *Journal of Business & Economic Statistics*, v. 13, n. 3, p. 253–263, 1995.
- Giacomini, R.; White, H. Tests of conditional predictive ability. *Econometrica*, v. 74, n. 6, p. 1545–1578, 2006.
- Harvey, D.; Leybourne, S.; Newbold, P. Testing the equality of prediction mean squared errors. *International Journal of Forecasting*, v. 13, n. 2, p. 281–291, 1997.
- Newey, W. K.; West, K. D. A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, v. 55, n. 3, p. 703–708, 1987.

As referências bibliográficas devem ser conferidas nas fontes originais antes de entrarem no relatório.

## Histórico

| Data | Mudança |
| --- | --- |
| 08/11/2026 | Primeira redação, com as propostas N1 a N5 |
| 08/11/2026 | Decisões N1 a N5 aprovadas e incorporadas: lista de datas elegíveis fixada antes da avaliação; limiar estrito em precisão completa; justificativas como escolhas operacionais; casos não calculáveis ampliados (entradas não finitas, desalinhamento, erro numérico distinto de variância nula); denominador nulo do R²; ressalva aprovada no lugar da afirmação sobre falso positivo; Clark-West sem conclusão automática de ganho encoberto; testes matemáticos separados do mínimo operacional |
| 08/11/2026 | Implementação: tolerância relativa de 10⁻¹² para série constante, com testes de série exatamente constante, constante com resíduo de arredondamento, baixa amplitude com variação real e entradas não finitas (verificadas antes da tolerância) |
