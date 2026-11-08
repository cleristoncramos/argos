# Snapshot do piloto — `snap-20261108-01`

**Situação:** snapshot coletado e congelado · verificação de integridade **com pendência** · elegibilidade para a modelagem **aguarda a decisão P1** (seção 6) · cópia de segurança feita e conferida
**Avaliação final:** bloqueada. Este relatório não contém nenhum resultado de modelo nem do período final.

O congelamento do snapshot não equivale à aprovação de integridade para a modelagem, ao congelamento da configuração nem à autorização de abertura da avaliação final ([plano](../plano_reformulacao_preditiva.md), seção 7.3).

---

## 1. Identificação

| Item | Valor |
| --- | --- |
| Snapshot | `snap-20261108-01` (primeira tentativa; nenhuma anterior) |
| Coletado em | 08/11/2026, 11:49:21 (horário de Brasília) |
| Data de corte dos preços | 30/10/2026 |
| Implementação | commit `47642c7ed233c07ba23539ec14b6e63c38a5fbf6` |
| Árvore de trabalho | Registrada como alterada: a única alteração local era `docs/versao_congelada.md`, um documento sem relação com o código do piloto |
| Protocolo no momento da coleta | `docs/preditivo/protocolo_piloto_v1.md`, SHA-256 `3e71eff9f944beae91deecee32ee13bd793ee31b09b72c03843746ffa15ce997` |
| Versões | Python 3.13.15 · pandas 3.0.5 · NumPy 2.5.2 · yfinance 1.7.0 · scikit-learn 1.9.1 |
| Manifesto | `experiments/preditivo/dados/snap-20261108-01/manifest.json`, SHA-256 `6985328407ba456ada6c92872382e00f0109a772a904bbf477e3b5a006dd272c` |
| Ponteiro | `experiments/preditivo/snapshot.json` (snapshot vigente) |

## 2. Parâmetros da coleta

| Série | Parâmetros |
| --- | --- |
| Preços ajustados | Yahoo Finance via yfinance; `interval=1d`, `auto_adjust=True`, `actions=False`, `start=2008-01-02`, `end=2026-10-31` (exclusivo) |
| Preços brutos e eventos | Yahoo Finance via yfinance; `interval=1d`, `auto_adjust=False`, `actions=True`, mesmo intervalo |
| CDI | Banco Central do Brasil, SGS 12, em blocos de até 5 anos; resposta original em % ao dia, preservada, e tabela convertida para decimal |

## 3. Arquivos, cobertura e conferência das séries

| Arquivo | Linhas | Início | Fim | Ordenada | Datas repetidas | Não finitos | SHA-256 |
| --- | ---: | --- | --- | --- | ---: | ---: | --- |
| `PETR4_SA_ajustado.csv` | 4.679 | 02/01/2008 | 30/10/2026 | sim | 0 | 0 | `b50067b2a8f7648bf21ce90f270da14a7a5d46b264b0cd56734e03736cfa68c6` |
| `PETR4_SA_bruto.csv` | 4.679 | 02/01/2008 | 30/10/2026 | sim | 0 | 0 | `d9a63afba0e681d0dc8795dbb3bc9ab9f9cb32de6edb02f70b5974fd8e77a269` |
| `VALE3_SA_ajustado.csv` | 4.679 | 02/01/2008 | 30/10/2026 | sim | 0 | 0 | `92baa5a7583eabf148b004deee2ae5ddc327aedfc1aecd5bac7859b73e652fdf` |
| `VALE3_SA_bruto.csv` | 4.679 | 02/01/2008 | 30/10/2026 | sim | 0 | 0 | `587cb2d741c46aa3f73af459bc9d4debbe87b59645102a858eb47a2c6638e426` |
| `cdi_sgs12.csv` | 4.731 | 02/01/2008 | 30/10/2026 | sim | 0 | 0 | `ed6eb932eafc494aa9478c028feb410f7b2bd1ea6aa1c4a15e32d8f533109a88` |
| `cdi_sgs12_resposta.json` | — | — | — | — | — | — | `a06afbe28e8a5b31f153a4413b5168c8db3dfd3b214fe87a03c644a7139ffbf6` |

Os arquivos de dados ficam fora do Git. Os hashes permitem conferir os arquivos, mas não reconstruí-los: é preciso manter uma cópia de segurança em armazenamento controlado.

## 4. Verificações e pendências de integridade

### 4.1 Faixa mínima ≤ abertura, fechamento ≤ máxima (bases comparáveis)

A série ajustada usada no piloto coincide com a reconstrução da base bruta pelo fator `a_t = Adj Close / Close` (maior diferença relativa: 0, nos dois ativos). As ocorrências abaixo violam a faixa **na base bruta e na ajustada**, ou seja, na mesma base de ajuste.

| Ativo | Data | Abertura | Máxima | Mínima | Fechamento | O que está fora da faixa | Situação |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| PETR4.SA | 02/04/2014 | 15,71 | 16,60 | 15,70 | 15,56 | Fechamento abaixo da mínima | Em investigação |
| VALE3.SA | 14/08/2012 | 38,36 | 37,75 | 36,84 | 37,05 | Abertura acima da máxima | Em investigação |
| VALE3.SA | 05/09/2012 | 32,70 | 33,89 | 32,77 | 33,00 | Abertura abaixo da mínima | Em investigação |

Os valores de PETR4 em 02/04/2014 são idênticos aos observados no ensaio preliminar. Nenhuma linha foi removida ou alterada. A identificação do campo divergente veio depois, pela conferência externa (seção 6.2).

### 4.2 Variações do fator de ajuste sem evento registrado

Nenhuma, nos dois ativos.

**Correção de um registro anterior.** A sequência foi esta:
1. no ensaio, levantou-se a hipótese de uma variação do fator de PETR4 entre 02/04 e 03/04/2014 sem evento;
2. a coleta oficial identificou o provento de 0,99757 em **03/04/2014**;
3. esse provento explica exatamente a mudança do fator: `1 − 0,99757 / 15,56 = 0,9359`, e `0,2505 × 0,9359 = 0,2344`;
4. a afirmação anterior foi corrigida. No ensaio, a coluna de proventos não foi exibida na conferência, e a afirmação foi feita sem essa informação.

Essa questão está esclarecida. Ela é distinta da violação OHLC de 02/04/2014, que segue na seção 6.

### 4.3 Triagem de diferenças entre retorno de preço e retorno ajustado por proventos

| Ativo | Datas acima de 1 ponto percentual | Com provento informado na mesma data |
| --- | ---: | ---: |
| PETR4.SA | 30 | 30 |
| VALE3.SA | 32 | 32 |

Todas as datas marcadas coincidem com proventos informados pela fonte. Cada uma segue registrada no manifesto com investigação "pendente", para documentação.

### 4.4 Desdobramentos e grupamentos informados pela fonte

| Ativo | Data | Fator |
| --- | --- | ---: |
| PETR4.SA | 28/04/2008 | 2 |

Nenhum na VALE3.

## 5. O que fica pendente antes do desenvolvimento oficial

1. Investigar as três ocorrências da seção 4.1 e decidir, de forma documentada, se cada observação é mantida, corrigida ou excluída, e quais amostras isso afeta. Os arquivos originais não são sobrescritos: um tratamento, se houver, é registrado à parte.
2. Documentar a conferência das datas da triagem de proventos (seção 4.3).
3. Confirmar com o orientador a formalização do embargo nas reestimações (protocolo, seção 6.3).
4. Fazer a cópia de segurança dos arquivos do snapshot fora do Git.

Só depois: configuração consolidada → desenvolvimento oficial → decisão sobre encerrar a v1 ou abrir o período final.

---

## 6. Tratamento das ocorrências (manifestação do orientador de 08/11/2026)

### 6.1 Cópia de segurança e evidências

| Item | Registro |
| --- | --- |
| Cópia de segurança | `C:\Users\User\argos_backup_snapshots\snap-20261108-01` (disco local, fora do OneDrive e do Git); os 6 arquivos e o manifesto conferidos contra os hashes, sem divergência |
| Árvore alterada na coleta | Desvio documental justificado; evidência em [`evidencias/arvore_coleta_snap-20261108-01.md`](evidencias/arvore_coleta_snap-20261108-01.md). O registro "árvore alterada" permanece no manifesto |

### 6.2 Conferência externa pontual (B3)

Fonte: série histórica oficial de cotações da B3 (COTAHIST), mercado à vista, valores nominais, consultada em 08/11/2026 às 12:02. Arquivos guardados junto à cópia de segurança, com hash em [`politica_qualidade.json`](../../experiments/preditivo/politica_qualidade.json): `COTAHIST_D02042014.ZIP` (SHA-256 `c351731f…`) e `COTAHIST_A2012.ZIP` (SHA-256 `98771b12…`). Nos períodos conferidos não há desdobramento, então a base bruta do snapshot e os valores nominais da B3 são comparáveis.

| Ativo e data | Campo | Snapshot (base bruta) | B3 | Situação |
| --- | --- | ---: | ---: | --- |
| PETR4, 02/04/2014 | Abertura / máxima / mínima | 15,71 / 16,60 / 15,70 | 15,71 / 16,60 / 15,70 | Conferem |
| PETR4, 02/04/2014 | **Fechamento** | 15,56 | **16,56** | Diverge (diferença de 1,00) |
| VALE3, 14/08/2012 | Abertura / mínima / fechamento | 38,36 / 36,84 / 37,05 | 38,36 / 36,84 / 37,05 | Conferem |
| VALE3, 14/08/2012 | **Máxima** | 37,75 | **38,64** | Diverge |
| VALE3, 05/09/2012 | Abertura / fechamento | 32,70 / 33,00 | 32,70 / 33,00 | Conferem |
| VALE3, 05/09/2012 | **Máxima** / **mínima** | 33,89 / 32,77 | **33,19** / **32,47** | Divergem |

**O que muda em relação ao que se supunha:** nas duas datas da VALE3, a abertura, apontada pela relação entre os campos, confere com a B3; os campos divergentes são a máxima e a mínima. Eles entram no ATR, então a VALE3 também é afetada. As aberturas continuam marcadas como questionadas, por cautela; a abertura não entra em nenhum cálculo deste piloto (confirmado por código e por teste).

### 6.3 Política implementada

`experiments/preditivo/qualidade.py`, com a política em [`politica_qualidade.json`](../../experiments/preditivo/politica_qualidade.json). Os arquivos do snapshot não são alterados: a política é aplicada na memória, e o calendário original é preservado.

| Item | Regra |
| --- | --- |
| Dependências | Fechamento: todas as variáveis, o alvo e o preço de execução. Máxima e mínima: só o ATR. Abertura: nenhum cálculo |
| Invalidar | O campo passa a ser ausente. Nenhum cálculo o usa, e nada é estimado no lugar dele. Janelas finitas que o incluiriam ficam inválidas. Variáveis recursivas (médias exponenciais, MACD, RSI e ATR de Wilder) seguem sem a observação e ficam inválidas por 78 pregões de reaquecimento, a mesma convenção do aquecimento inicial. Depois disso, a influência residual é tratada como desprezível, pela mesma convenção. Alvos cuja entrada ou saída dependa do fechamento invalidado ficam ausentes e não entram no treino |
| Substituir pela fonte verificada | O valor da B3 é convertido para a base ajustada pelo fator `Adj Close / Close` da própria data e usado só na visão derivada |
| Trava | A rodada oficial do desenvolvimento, a lista de datas elegíveis e a avaliação final recusam a política enquanto houver entrada com decisão pendente |

### 6.4 Impacto de cada opção (sem nenhum modelo)

Medido com `executar qualidade` sobre o período de desenvolvimento, só com contagens de amostras e variáveis.

| Ativo | Opção | Amostras perdidas | Por variáveis | Por alvo | Células de variáveis | Datas afetadas | Nas validações de 2014 a 2021 | Calendário preservado |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| PETR4 | Invalidar | 254 | 252 | 2 | 9.828 | 28/02/2014 a 08/04/2015 | 254 | Sim |
| PETR4 | Substituir pela B3 | 0 | 0 | 0 | 0 | — | 0 | Sim |
| VALE3 | Invalidar | 95 | 95 | 0 | 3.705 | 14/08/2012 a 04/01/2013 | 0 | Sim |
| VALE3 | Substituir pela B3 | 0 | 0 | 0 | 0 | — | 0 | Sim |

Na PETR4, a invalidação retira cerca de 252 pregões de amostras porque a distância ao pico de 252 pregões não pode ser calculada em nenhuma janela que inclua o fechamento ausente.

### 6.5 Decisão pendente antes do desenvolvimento oficial

A política conservadora foi aprovada para o caso **sem** fonte verificável. A conferência encontrou fonte verificável para as três datas, então a escolha do tratamento (P1, em [`../pibiti/decisoes_orientador.md`](../pibiti/decisoes_orientador.md)) precisa ser decidida e registrada antes do desenvolvimento oficial, sem considerar desempenho de modelo:

- **(a) invalidar** os campos divergentes: perde 254 amostras na PETR4 e 95 na VALE3, sem usar nenhum valor externo;
- **(b) substituir** na visão derivada pelos valores da B3: não perde amostras, mas introduz valores de outra fonte, convertidos pelo fator de ajuste.

Nenhum modelo foi ajustado para produzir esta comparação.
