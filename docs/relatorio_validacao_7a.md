# Relatório de validação da 7A — modelo (preencher após o experimento)

**Situação:** modelo em branco. Não preencha com resultados de ensaio (`--dry-run`).

## 1. Identificação

| Item | Valor |
|---|---|
| Data de execução | |
| Versão e impressão digital do prompt | v0.1 / `` |
| `cases.json` (SHA-256) e pacote de dados | |
| Modelos | `gpt-5-mini`, `gpt-5-nano` |
| Número de casos / repetições / respostas | |
| Parâmetros usados e removidos pela API | |
| Custo total do experimento (US$) | |
| Confirmação de preços (data da consulta) | |

## 2. Casos

Tabela com id, tipo, resposta esperada (resumo) e eventuais alterações feitas depois da execução, com motivo.

## 3. Resultados automáticos

Copiar a tabela de `results/relatorio.md` para cada modelo. Citar respostas reprovadas pela regra por resposta (modelo, caso, repetição, verificação) e a causa provável.

## 4. Avaliação humana

| Item | Valor |
|---|---|
| Avaliadores (perfil, sem identificar) | Três adultos: leigo (clareza), técnico (correção), neutro (neutralidade); cada um avaliou as três dimensões, isoladamente |
| Data da sessão de calibração e acordos | Rodada 4, 12/10/2026, após reunião de calibração do significado das notas |
| Respostas na calibração | 15 (T001–T015), respostas novas do gpt-5-mini com o prompt v0.6; recusa incluída (T010) |
| Kappa por dimensão e par (técnico–neutro / técnico–leigo / neutro–leigo) | Clareza 0,189 / 0,423 / 0,595; correção 0,595 / 0,856 / 0,712; neutralidade 0,595 / 0,423 / 0,595. **Abaixo de 0,60 em clareza e neutralidade; em correção, um par em 0,595.** Concordância exata 73% a 87%; dentro de 1 ponto 100% |
| Notas médias por dimensão e modelo | Primeira rodada (78 respostas, gpt-5-mini): média 4,731. Rodada 4: notas concentradas em 4 e 5 (ver relatório da rodada 4) |
| Alucinações apontadas | Nenhuma na rodada 4 (alucinação 0 nos 15 itens); 0,0135 na primeira rodada |

### Ocorrência de falso positivo do validador

Na execução complementar de 12/10/2026, destinada à geração de respostas para a sessão de calibração humana, uma resposta (`c10_simulacao_aapl`) foi bloqueada pela regra `sem_recomendacao`.

A expressão identificada foi "ao aplicar um único aporte no início do período". No contexto da resposta, a expressão descrevia o cenário hipotético de uma simulação histórica e não continha recomendação de investimento, orientação de alocação ou indicação de ação futura.

A ocorrência foi classificada como falso positivo do validador, que adota uma abordagem deliberadamente conservadora para termos relacionados a operações financeiras (o verbo "aplicar" só é aceito em frase negada). A resposta foi preservada nos registros e excluída das planilhas de avaliação humana.

A execução oficial do prompt v0.6, utilizada para avaliar o cumprimento dos critérios automáticos da etapa 7A, registrou 0 falhas em 78 respostas. A execução complementar não substitui nem altera esse resultado. Eventual ajuste do validador exige nova versão, nova impressão digital e nova execução da 7A.

### Limitação da avaliação humana

A rodada 4 da avaliação humana registrou concordância dentro de um ponto de 100% entre avaliadores, mas o kappa ponderado ficou abaixo do limiar pré-definido de 0,60 nas dimensões de clareza e neutralidade. Em um dos pares, a correção factual atingiu kappa de 0,595.

A interpretação do kappa foi limitada pelo número reduzido de itens, pela baixa variação das notas e por divergências de leitura em casos específicos, como o item T010. Portanto, os resultados não são apresentados como validação estatística definitiva da rubrica, mas como evidência preliminar de avaliação humana documentada.

Como trabalho futuro, recomenda-se reancorar a escala com exemplos, ampliar o conjunto de itens com maior variação de qualidade e reavaliar a concordância com amostra mais ampla.

## 5. Limitações do experimento

Amostra de casos, dados sintéticos (caso de preço ≤ 0), dependência do período dos dados, validador conservador, uso de apenas dois modelos, avaliação por três pessoas.

## 6. Decisão

| Pergunta | Resposta |
|---|---|
| Todos os critérios em `ok`? | Critérios automáticos: sim (execução oficial v0.6: 0 falhas em 78). Critério humano de kappa: **não** |
| Nenhuma resposta na regra por resposta? | Sim na execução oficial (0/78). Na execução complementar, 1 bloqueio classificado como falso positivo do validador |
| Kappa ≥ 0,60 em todos os pares? | **Não** (limitação registrada) |
| Modelo recomendado para a 7B | gpt-5-mini; gpt-5-nano fora da interface |
| Mudanças no prompt (se houver) e nova versão | Nenhuma; v0.6 `e3b3574b7430` mantida |

## 7. Aprovação do orientador

Decisão de 12/10/2026 registrada em `docs/pibiti/decisoes_orientador.md`: 7A concluída para progressão e 7B liberada com condições, mantendo o kappa como limitação. O original da mensagem deve ser arquivado (data e forma da evidência).
