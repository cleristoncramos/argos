# Desenvolvimento oficial do piloto — v1

**Situação:** rodada oficial concluída em 08/11/2026 · **critério 3 não atendido nos dois ativos** · avaliação final bloqueada
Este relatório cobre só o período de desenvolvimento (dobras de 2014 a 2021). Nenhum preço do período final foi lido: o desenvolvimento usa apenas datas anteriores ao 21º pregão de 2022 (teste automático em `experiments/preditivo/tests`).

---

## 1. Identificação

| Item | Valor |
| --- | --- |
| Data e hora | 08/11/2026, 12:18:50 (Brasília) |
| Commit da implementação | `1f2e167` |
| Árvore de trabalho | Registrada como alterada: a única alteração local era `docs/versao_congelada.md`, o mesmo documento sem relação com o piloto da coleta ([evidência](evidencias/arvore_coleta_snap-20261108-01.md)) |
| Snapshot | `snap-20261108-01` (manifesto SHA-256 `6985328407ba…`) |
| Política de qualidade | Versão 1.0 (decisão P1), SHA-256 `f75598b06fa9…`, aplicada na visão derivada |
| Protocolo e nota | Hashes no `registro.jsonl` (eventos `desenvolvimento`) |
| Configuração | Sem alteração: ativos, horizonte, variáveis, grade de `alpha` (0,1 a 1000), embargo e expurgo conforme o protocolo consolidado |

## 2. R² fora da amostra por dobra

R² em relação ao retorno zero, na amostra diária de cada ano de validação (depois do embargo de 20 pregões). Erros na escala do retorno acumulado em 20 pregões.

### PETR4.SA

| Validação | R² | RMSE Ridge | RMSE retorno zero | RMSE média histórica | `alpha` | Datas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2014 | −0,6590 | 0,2098 | 0,1629 | 0,1640 | 100 | 228 |
| 2015 | **+0,0381** | 0,1756 | 0,1791 | 0,1791 | 1000 | 226 |
| 2016 | −0,1706 | 0,2641 | 0,2441 | 0,2463 | 1000 | 229 |
| 2017 | −0,0120 | 0,0909 | 0,0904 | 0,0898 | 1000 | 234 |
| 2018 | −0,0657 | 0,1793 | 0,1737 | 0,1723 | 1000 | 226 |
| 2019 | −0,0931 | 0,0660 | 0,0631 | 0,0615 | 1000 | 228 |
| 2020 | **+0,1315** | 0,1922 | 0,2063 | 0,2058 | 1000 | 228 |
| 2021 | **+0,0010** | 0,1092 | 0,1093 | 0,1055 | 1000 | 226 |

### VALE3.SA

| Validação | R² | RMSE Ridge | RMSE retorno zero | RMSE média histórica | `alpha` | Datas |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2014 | −0,1092 | 0,0888 | 0,0843 | 0,0864 | 1000 | 228 |
| 2015 | −0,2195 | 0,1671 | 0,1514 | 0,1513 | 1000 | 226 |
| 2016 | −0,1510 | 0,2288 | 0,2133 | 0,2131 | 1000 | 229 |
| 2017 | −0,1031 | 0,0955 | 0,0909 | 0,0884 | 1000 | 234 |
| 2018 | **+0,0305** | 0,0843 | 0,0856 | 0,0838 | 1000 | 226 |
| 2019 | **+0,1326** | 0,0723 | 0,0776 | 0,0754 | 1000 | 228 |
| 2020 | **+0,0756** | 0,1351 | 0,1406 | 0,1349 | 1000 | 228 |
| 2021 | −0,0080 | 0,0995 | 0,0992 | 0,0997 | 100 | 226 |

## 3. Critério 3 (estabilidade)

| Ativo | Dobras com R² > 0 | Exigido | Critério 3 |
| --- | ---: | ---: | --- |
| PETR4.SA | 3 de 8 (2015, 2020, 2021) | 5 | **Não atendido** |
| VALE3.SA | 3 de 8 (2018, 2019, 2020) | 5 | **Não atendido** |

Os critérios de elegibilidade são todos obrigatórios (protocolo, seção 9.3). Com o critério 3 não atendido, **nenhum dos dois ativos pode ser declarado elegível pela regra da v1**, qualquer que seja o resultado no período final. Os critérios 1, 2, 4 e 5 dependem do período final e não foram calculados. Pelo protocolo, o resultado da v1 é: **"Não houve evidência suficiente para habilitar o sinal."** Isso conclui o experimento cientificamente, desde que relatado integralmente.

Nenhum parâmetro, variável, grade ou limiar foi alterado depois de conhecidos estes resultados.

## 4. Seleção do `alpha` e comportamento das previsões

| Ativo | `alpha` = 1000 | `alpha` = 100 | Demais valores |
| --- | ---: | ---: | ---: |
| PETR4.SA | 7 ajustes | 1 (2014) | 0 |
| VALE3.SA | 7 ajustes | 1 (2021) | 0 |

A escolha atingiu com frequência o limite superior da grade. Isso indica regularização forte, não previsões nulas. Com intercepto (`fit_intercept` verdadeiro em todos os ajustes), as previsões ficam próximas de uma constante ligada à média do alvo no treino, mas ainda variam. O desvio-padrão das previsões em cada validação foi de 0,008 a 0,080 na PETR4 e de 0,010 a 0,038 na VALE3. Os valores por ajuste (média e desvio das previsões e média do alvo no treino) estão no `registro.jsonl`. A grade não foi ampliada nesta versão.

A acurácia balanceada de direção, nas datas de decisão (a cada 20 pregões), ficou entre 0,33 e 0,75 na PETR4 e entre 0,39 e 0,63 na VALE3, com poucas decisões por ano. Ela é informativa e não entra nos critérios.

## 5. Comparação com o ensaio preliminar

O ensaio local sem a política de qualidade (verificação de funcionamento sobre o mesmo snapshot, sem evento no `registro.jsonl` e sem valor de decisão) também teve 3 de 8 dobras positivas nos dois ativos, nos mesmos anos. As diferenças de R² entre o ensaio e a rodada oficial são pequenas (por exemplo, PETR4 em 2014: −0,6533 no ensaio e −0,6590 na oficial) e vêm da visão derivada da P1, que alterou valores na PETR4 em 2014 e 2015 e o ATR da VALE3 em 2012 e 2013.

## 6. Decisão pendente

Conforme o plano (seção 7.3), cabe agora ao orientador decidir, e registrar antes de qualquer abertura:

| Caminho | Consequência |
| --- | --- |
| Encerrar a v1 por não elegibilidade | Preserva o período final sem uso nesta avaliação, disponível para uma versão futura |
| Abrir o período final para completar o estudo da v1 | Produz o relatório completo (critérios 1, 2, 4 e 5 e o diagnóstico Clark-West), mas não pode habilitar o sinal, porque o critério 3 falhou |

A avaliação final permanece bloqueada até essa decisão e até o cumprimento das demais condições da seção 12 do protocolo.
