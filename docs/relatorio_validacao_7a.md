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
| Avaliadores (perfil, sem identificar) | |
| Data da sessão de calibração e acordos | |
| Respostas na calibração | |
| Kappa por dimensão e par | |
| Notas médias por dimensão e modelo | |
| Alucinações apontadas | |

## 5. Limitações do experimento

Amostra de casos, dados sintéticos (caso de preço ≤ 0), dependência do período dos dados, validador conservador, uso de apenas dois modelos, avaliação por três pessoas.

## 6. Decisão

| Pergunta | Resposta |
|---|---|
| Todos os critérios em `ok`? | |
| Nenhuma resposta na regra por resposta? | |
| Kappa ≥ 0,60 em todos os pares? | |
| Modelo recomendado para a 7B | |
| Mudanças no prompt (se houver) e nova versão | |

## 7. Aprovação do orientador

Registrar em `docs/pibiti/decisoes_orientador.md` (data, forma — mensagem ou ata — e texto da autorização para iniciar a 7B).
