# Encerramento do piloto preditivo v1

**Situação:** v1 **encerrada por não elegibilidade** (decisão D1, 08/11/2026, sujeita à confirmação original do orientador) · avaliação final **não executada** · período final reservado

A v1 é um experimento concluído com resultado de não elegibilidade. Não é uma tarefa incompleta que precise ser repetida até produzir aprovação.

---

## 1. Resultado oficial

> O piloto v1 foi encerrado após o desenvolvimento oficial. PETR4.SA e VALE3.SA não atenderam ao critério de estabilidade entre dobras: cada ativo apresentou R² positivo em três das oito dobras, abaixo do mínimo de cinco. Não houve evidência suficiente, segundo os critérios deste protocolo, para habilitar o sinal. A avaliação final não foi executada.

**Alcance da conclusão.** O experimento avaliou uma configuração específica:
- dados: snapshot `snap-20261108-01` com a política de qualidade 1.0;
- variáveis: as 12 variáveis do protocolo;
- modelo: Ridge com a grade de `alpha` fixada;
- horizonte: 20 pregões;
- critérios: os do protocolo v1.

O resultado não autoriza afirmações como:
- "não é possível prever esses ativos";
- "Ridge não funciona em finanças";
- "nenhum modelo pode superar a referência";
- "o período final confirmou a ausência de ganho".

O período final não forneceu resultado preditivo porque não foi avaliado.

Detalhes por dobra estão em [`desenvolvimento_oficial_v1.md`](desenvolvimento_oficial_v1.md).

## 2. `alpha`

`alpha` = 1000 foi selecionado em 7 das 8 dobras de cada ativo. A exceção foi `alpha` = 100: na PETR4 em 2014 e na VALE3 em 2021.

A grade não foi ampliada nesta versão, e a escolha não é interpretada como previsão nula: o desvio-padrão das previsões por ano foi de 0,008 a 0,080 na PETR4 e de 0,010 a 0,038 na VALE3. Esse comportamento pode motivar uma pergunta para a v2, mas não uma alteração retroativa da v1.

## 3. Alcance efetivo do bloqueio do período final

O comando de desenvolvimento não utilizou preços, alvos, previsões ou métricas do bloco final para treinamento, seleção ou avaliação.

O arquivo completo, que inclui as datas do bloco final, foi acessado para outras finalidades:

| Acesso | Finalidade | Uso de dados do bloco final |
| --- | --- | --- |
| Coleta (`coletar`) | Baixar e congelar as séries até o corte de 30/10/2026 | Cálculo de hashes; contagem de linhas, início e fim; datas repetidas; valores não finitos |
| Verificações de integridade na coleta | Triagem de retorno de preço × ajustado por proventos, desdobramentos, faixa OHLC e variações do fator | Percorreram a série inteira, incluindo o bloco final; produzem ocorrências de dados, não métricas preditivas |
| Reconstrução do fator de ajuste (política 1.0) | Conferir o método multiplicativo e recalcular o fator da PETR4 | O fator de cada data depende dos proventos e fechamentos posteriores a ela, inclusive os do bloco final. Ver nota abaixo |
| `qualidade` e `desenvolver` | Carregar o snapshot | Leem o arquivo inteiro; usam só o calendário de 2022 para localizar o 21º pregão e truncam a série antes dele (teste automático `test_desenvolvimento_nao_le_o_periodo_final`) |
| Comando `listar-datas` | Lista N1 de datas elegíveis do período final | **Nunca executado**: `datas_elegiveis.json` não existe |
| Comando `final` | Avaliação final | **Nunca executado**: sem marca de uso e sem evento de avaliação final no registro |

**Nota sobre a base ajustada.** Os preços ajustados por proventos são reescalados para trás a cada data ex. Por isso, o nível ajustado de uma data do desenvolvimento reflete proventos pagos depois, inclusive no bloco final. A reescala é multiplicativa e constante antes de cada data ex, então não altera retornos nem razões entre preços dentro do desenvolvimento. As variáveis e o alvo usam só essas grandezas. É uma propriedade da base de dados, não um uso preditivo do bloco final.

**Estado da trava no encerramento** (gravado em `experiments/preditivo/encerramento_v1.json`):
- marca de uso do final: ausente;
- lista de datas do período final: não gerada;
- condições da seção 12 cumpridas: 0 de 8;
- eventos com avaliação final no registro: 0.

Antes do encerramento, a trava recusava a abertura por condições pendentes e hashes ausentes. Depois dele, o código recusa também pela versão encerrada (`abertura.exigir_versao_aberta` e `verificar_abertura`), mesmo que todas as condições fossem cumpridas. Ficam recusados nesta versão:
- nova coleta;
- `listar-datas`;
- desenvolvimento oficial;
- `final`.

Para reproduzir o desenvolvimento, resta `desenvolver --ensaio`, que é registrado como ensaio.

**Reserva para uma v2.** O período só pode ser usado por uma futura v2 se:
- os resultados preditivos dele não forem consultados para escolher a nova configuração;
- o protocolo da v2 for fechado antes da avaliação;
- forem registradas todas as mudanças motivadas pelo desenvolvimento da v1;
- a v2 não for apresentada como repetição independente de uma hipótese que não mudou.

## 4. Dados recebidos, tratamento aplicado e visão derivada

| Camada | O que é | Onde está |
| --- | --- | --- |
| Dado recebido | Snapshot original, intacto, com as ocorrências preservadas | `experiments/preditivo/dados/snap-20261108-01/` (manifesto SHA-256 `6985328407ba456ada6c92872382e00f0109a772a904bbf477e3b5a006dd272c`) e cópia fora do Git |
| Tratamento | Política de qualidade 1.0: substituição pontual pela B3 de quatro campos em três datas (decisão P1) | `experiments/preditivo/politica_qualidade.json`, SHA-256 `f75598b06fa9a1100fecc5783b78c1874642686223ecb5b60e05096cf8e88975`; registros da B3 arquivados fora do Git |
| Visão derivada | Série em memória usada no desenvolvimento oficial | Gerada por `qualidade.aplicar_aos_precos`; impacto em `resultados/qualidade_impacto.json` ([relatório do snapshot](snapshot_snap-20261108-01.md), seção 7.3) |

**Limitações que continuam registradas:**

- **VALE3 em 2008–2009:** o método multiplicativo não reproduz o ajuste da fonte nesse período (diferença de até 6,7%). De 2010 em diante, reproduz com precisão de cerca de 10⁻⁷. A divergência segue sem explicação e fica para investigação futura.
- **Fator usado nas correções de máxima e mínima da VALE3 em 2012:** os valores da B3 foram convertidos para a base ajustada pelo fator da fonte na própria data (0,407471), sem recálculo. A justificativa:
  - o fator depende só de fechamentos e proventos, e as substituições de máxima e mínima não mudam nenhum dos dois, então o fator correto é o mesmo de antes;
  - nas datas afetadas, o método reconstruído reproduz o fator da fonte com diferença relativa de no máximo 5,6 × 10⁻⁷, e o código recusaria a substituição acima de 10⁻⁵;
  - a divergência de 2008–2009 está em datas anteriores. O fator de 2012 depende só de eventos posteriores a 2012, então essa divergência não entra nele.
- **Ensaio sem a política:** a verificação local de funcionamento rodada antes da P1 não tem evento no `registro.jsonl` e não é o desenvolvimento oficial. O único desenvolvimento oficial são os dois eventos `desenvolvimento` de 08/11/2026, às 12:18.
- **Árvore de trabalho alterada:** a coleta e o desenvolvimento foram registrados com a árvore alterada, e a única alteração era `docs/versao_congelada.md`, sem relação com o piloto. É um desvio documentado e aceito, não uma "árvore limpa" ([evidência](evidencias/arvore_coleta_snap-20261108-01.md)).

## 5. Arquivamento

Itens versionados no Git, com os hashes de protocolo, nota, configuração, manifesto e política gravados em cada linha do `registro.jsonl`:

| Item | Arquivo |
| --- | --- |
| Protocolo utilizado | `docs/preditivo/protocolo_piloto_v1.md` (inalterado desde o desenvolvimento; hash igual ao registrado) |
| Nota estatística | `docs/preditivo/nota_teste_estatistico.md` (idem) |
| Configuração | `experiments/preditivo/config.py` (idem) |
| Manifesto do snapshot | `experiments/preditivo/dados/snap-20261108-01/manifest.json` |
| Política de qualidade | `experiments/preditivo/politica_qualidade.json` |
| Relatório do snapshot e do impacto | `docs/preditivo/snapshot_snap-20261108-01.md` |
| Relatório do desenvolvimento | `docs/preditivo/desenvolvimento_oficial_v1.md` |
| Registro de execuções | `experiments/preditivo/registro.jsonl` |
| Estado do bloqueio | `experiments/preditivo/encerramento_v1.json` e `condicoes_abertura.json` |
| Decisões | `docs/pibiti/decisoes_orientador.md` (R6–R8, N1–N5, snapshot, P1, D1) |

O commit da implementação do desenvolvimento oficial é `1f2e167`.

As métricas e as previsões do desenvolvimento ficam em `experiments/preditivo/resultados/`, que é ignorado pelo Git. Os hashes estão em `encerramento_v1.json`:

| Arquivo | SHA-256 |
| --- | --- |
| `desenvolvimento_PETR4_SA.csv` | `ebbaed1064fcb13740ec9ebaca88084bb3b99e80f19e997e3c4d46d07c7af23a` |
| `desenvolvimento_VALE3_SA.csv` | `0c520d201c434d76e2c89fe0dffdd546e12bd0d15a1f7dc3bb630194ebe54c39` |
| `desenvolvimento_resumo.json` | `84fa66b6583a81e5edbe5ad7fa56df76e937f575d61218a708b2a50199df4891` |
| `qualidade_impacto.json` | `1414dc87f0a9cbf167034be22807c74fe0dba5ccb033b12c05de86449cb3f3ed` |

Uma cópia desses arquivos e dos itens acima fica fora do Git, na pasta de cópias de segurança do piloto (`encerramento_v1`), com lista de hashes.

**Pendente:** arquivar as mensagens originais do orientador, de R6–R8 até D1, com data e remetente.

## 6. Próxima atividade

A proposta de v2 começa documental, a partir dos resultados de desenvolvimento da v1. Ela deve selecionar poucas mudanças justificadas e não pode alterar o limiar só para tornar o resultado aprovado. Antes de novos experimentos, a proposta apresenta:
- a hipótese investigada;
- a diferença em relação à v1;
- os critérios mantidos ou revisados, com justificativa;
- o custo de implementação;
- o plano de avaliação;
- a situação do período reservado.

Não há busca ampla por modelos nesta etapa.
