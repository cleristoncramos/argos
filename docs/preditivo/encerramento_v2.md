# Encerramento do piloto preditivo v2

**Situação:** v2 **encerrada sem abertura da avaliação final** (decisão DV2, 08/11/2026, sujeita à confirmação original do orientador) · nenhum sinal habilitado · período final sem avaliação preditiva

A v2 é uma investigação concluída. Os filtros e as limitações estão relatados de forma distinta e transparente.

---

## 1. Resultado oficial

> O piloto v2 investigou a ampliação da regularização da Ridge, mantendo os demais elementos da v1. A VALE3 não atingiu os filtros de desenvolvimento. A PETR4 atingiu os filtros contra retorno zero e média histórica expansiva, mas uma análise exploratória posterior identificou que uma previsão constante igual à média do treino também superava a referência expansiva, sem utilizar indicadores. Portanto, o atendimento desses filtros não isolou a contribuição das variáveis. Por decisão de orientação, a avaliação final não foi aberta e nenhum sinal foi habilitado.

**VALE3.SA (V2-7):**

> A v2 não atendeu aos critérios de desenvolvimento necessários para abertura da avaliação final da VALE3.SA. Não houve evidência suficiente, segundo o protocolo, para habilitar o sinal.

**Resultado metodológico.** A referência acrescentada na v2, a média histórica expansiva, não separou completamente o efeito da regularização do efeito do procedimento de atualização da média.

## 2. Situação de cada elemento

| Elemento | Situação |
| --- | --- |
| Filtros de desenvolvimento da PETR4 (critério 3: 6 de 8; critério 6: 5 de 8) | **Atendidos** |
| Filtros de desenvolvimento da VALE3 (critério 3: 4 de 8; critério 6: 3 de 8) | Não atendidos |
| Critérios dependentes do período final (1, 2, 4, 5 e a parte final do 6) | **Não avaliados** |
| Abertura final da PETR4 | Não autorizada por decisão de orientação (não progressão) |
| Habilitação de sinais | Não autorizada para nenhum ativo |

A PETR4 foi encerrada por decisão de não progressão, fundamentada na limitação interpretativa, e não por descumprimento dos filtros.

A DV2 não cria um critério 7 nem altera os critérios 1 a 6, e os critérios não avaliados não são marcados como reprovados.

## 3. Diagnóstico exploratório

A comparação com uma previsão constante igual à média do alvo no treino:
- não estava prevista no protocolo;
- foi calculada só sobre as dobras de desenvolvimento de 2014 a 2021;
- não tem efeito retroativo nos critérios;
- serve para interpretar os resultados e orientar uma possível investigação futura.

Ela está em `resultados/v2/diagnostico_exploratorio_constante_treino.json`.

| Ativo | Constante do treino supera a média histórica | Ridge supera a média histórica | Ridge supera a constante do treino |
| --- | ---: | ---: | ---: |
| PETR4.SA | 7 de 8 | 5 de 8 | 2 de 8 |
| VALE3.SA | 4 de 8 | 3 de 8 | 3 de 8 |

A comparação mistura dois efeitos:
- o uso dos indicadores na Ridge;
- a diferença entre a média do treino, mantida durante o ano, e a média histórica, atualizada a cada data.

Isso não demonstra que as variáveis sejam inúteis. O diagnóstico também não diz nada sobre o período final, que não foi avaliado; a conclusão se restringe ao mecanismo observado no desenvolvimento.

## 4. Marcos e correção de infraestrutura

| Commit | Marco |
| --- | --- |
| `378b0b9` | Congelamento do experimento: código, configuração v2 e protocolo |
| `cdf7eef` | **Correção de infraestrutura, anterior à produção dos resultados** (ver abaixo) |
| `cdf7eef` | Base da rodada oficial: dois eventos `desenvolvimento` em `registro_v2.jsonl` |
| `a762437` | Relatório do desenvolvimento |

**A correção.** A primeira tentativa de rodada depois do congelamento foi recusada pela própria trava de código congelado, antes de carregar qualquer dado. O defeito estava em `registro.arquivos_alterados`, que cortava o primeiro caractere do primeiro caminho listado. A correção:
- passou a usar `git diff --name-only HEAD` e `git ls-files --others`;
- veio com o teste `test_arquivos_alterados_le_caminhos_completos`;
- não mudou grade, variáveis, critérios, configuração nem protocolo, cujos hashes são os do congelamento.

O congelamento e a correção são marcos distintos.

**Reprodução da v1.** O único evento `reproducao_v1` no registro é a verificação anterior ao congelamento, ainda com o hash antigo do protocolo. A rodada oficial repetiu a reprodução internamente, e ela passou, com diferença máxima de cerca de 10⁻¹⁶. Isso está registrado em `desenvolvimento_resumo.json` (`_declaracoes.reproducao_v1`). A rodada também conferiu os erros internos dos `alpha` comuns com os da v1.

## 5. Estado do bloqueio

Gravado em `experiments/preditivo/encerramento_v2.json`:
- avaliação final não executada;
- marca de uso do final ausente;
- lista de datas do período final não gerada;
- 0 de 7 condições de abertura cumpridas;
- nenhum evento de avaliação final em `registro_v2.jsonl`.

Com o encerramento, o código recusa todos os comandos da v2: `reproduzir-v1`, `desenvolver`, `listar-datas` e `final`.

**Achado de implementação.** O código só liberaria a lista de datas e a avaliação final quando todos os ativos atendessem aos filtros, enquanto o protocolo avalia os critérios por ativo e não definiu a abertura parcial. O achado fica registrado e não é corrigido, porque não haverá abertura. Uma versão futura deve definir no protocolo e no código quais condições são globais e quais são por ativo.

## 6. Arquivamento

Itens versionados no Git:

| Item | Arquivo |
| --- | --- |
| Protocolo v2 | `docs/preditivo/protocolo_piloto_v2.md` (SHA-256 `767566481140bd748ec798a0d774b5ff17cc742d8cbd0d157c8d9b6f22d408a0`, inalterado desde a rodada) |
| Configuração v2 | `experiments/preditivo/config_v2.py` (`79a89c807f33962a78e801c79e0072ed883003a9e19388259aa4f56098a3f328`) |
| Configuração, nota, manifesto e política | Iguais aos da v1 |
| Proposta, relatório e encerramento | `proposta_piloto_v2.md`, `desenvolvimento_oficial_v2.md` e este documento |
| Registro de execuções | `experiments/preditivo/registro_v2.jsonl` |
| Estado do bloqueio | `experiments/preditivo/encerramento_v2.json` e `condicoes_abertura_v2.json` |
| Decisões | `docs/pibiti/decisoes_orientador.md` (V2, confirmação e DV2) |

Os resultados ficam em `experiments/preditivo/resultados/v2/`, que o Git ignora. Os hashes estão em `encerramento_v2.json`:

| Arquivo | SHA-256 |
| --- | --- |
| `desenvolvimento_PETR4_SA.csv` | `c4a5fd70f4a449bae221553823a54e2ba0f5d283ad2298e256163f23052646db` |
| `desenvolvimento_VALE3_SA.csv` | `9435a40b1106a20f1d337498700945d5a306cede1156002018b289490a11832b` |
| `desenvolvimento_resumo.json` | `7fbdc42d12aaaf534df524ad0fcc3128e8e80dcee79f7b2384587df12df87836` |
| `reproducao_v1.json` | `21fcee10717df97581178ac67e60c83b97e476fc5967cf2ce1d0ff8701e8b810` |
| `diagnostico_exploratorio_constante_treino.json` | `5f41f5190f5bcf63f39d6bf2dc3f1a6f3a435ca06fe74900964cfc072901861d` |

A cópia fora do Git, com lista de hashes, fica na pasta de cópias de segurança do piloto (`encerramento_v2`).

**Pendente:** arquivar as mensagens originais do orientador (V2, confirmação e DV2), com data e remetente.

## 7. Continuidade

Não há v3 imediata. Uma proposta futura poderá investigar se as variáveis acrescentam informação em comparação com uma referência sem variáveis que tenha:
- a mesma amostra de treino;
- o mesmo calendário de reestimação;
- as mesmas datas de previsão;
- as mesmas restrições de disponibilidade de alvos.

É só uma hipótese de pesquisa. Ela não autoriza novos experimentos nem mudança dos critérios atuais.
