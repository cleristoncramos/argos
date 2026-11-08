# Piloto preditivo — implementação local

Implementa o [protocolo do piloto](../../docs/preditivo/protocolo_piloto_v1.md) e a [nota metodológica](../../docs/preditivo/nota_teste_estatistico.md). É um experimento **local**: nada daqui é importado pelo aplicativo, e nenhum resultado aparece na versão pública do Argos.

## Módulos

| Arquivo | Papel | Seção do protocolo |
| --- | --- | --- |
| `config.py` | Parâmetros aprovados (ativos, datas, horizonte, custos, limiares) | 1, 2, 5, 7, 8, 9 |
| `amostras.py` | Variáveis disponíveis em `t` e alvo `P_(t+21) / P_(t+1) − 1`, com `decision_date`, `entry_date` e `label_end_date` | 2, 3, 4 |
| `divisoes.py` | Dobras anuais, embargo de 20 pregões e expurgo pelas datas, inclusive nas divisões internas | 6 |
| `modelos.py` | Retorno zero, média histórica e Ridge com escolha do `alpha` nas validações internas | 7 |
| `avaliacao.py` | Reestimação no início de cada ano, com o modelo vigente registrado em cada previsão | 6.1, 6.3 |
| `estrategia.py` | Exposto ou caixa, custos por lado, CDI realizado, comprar e manter | 8 |
| `estatistica.py` | R² fora da amostra, Diebold-Mariano, Clark-West (diagnóstico) e casos não calculáveis | 9.1, 9.2; nota |
| `elegibilidade.py` | Os cinco critérios, com a condição econômica (A ∧ B) ∨ C | 9.3, 9.4 |
| `dados.py` | Coleta; triagem de retorno de preço × ajustado por proventos; desdobramentos da fonte; conferência OHLC em bases comparáveis; variações do fator sem evento; manifesto com hashes e leitura conferida | 3, 5, 8.3 |
| `qualidade.py` | Política de qualidade por campo e por dependência (invalidar ou substituir pela fonte verificada), na memória, com o calendário preservado; trava enquanto houver decisão pendente | 3, 10 |
| `registro.py` | Uma linha por execução em `registro.jsonl`, com commit e hashes | 10 |
| `abertura.py` | Trava da avaliação final | 6.3, 11, 12 |
| `executar.py` | Comandos | — |

## Instalação

```bash
pip install -r requirements.txt
pip install -r experiments/preditivo/requirements.txt
```

## Comandos (a partir da raiz do repositório)

```bash
python -m experiments.preditivo.executar coletar
```

Cria um **snapshot** com identificador próprio (`snap-AAAAMMDD-NN`) em `experiments/preditivo/dados/<snapshot>/`, com os preços ajustados, a série bruta com os eventos, a resposta original do BCB (SGS 12, em % ao dia) e a tabela convertida para decimal. O que as fontes retornaram é preservado sem correções. `snapshot.json` (versionado) aponta o snapshot vigente e guarda as tentativas anteriores. Uma nova coleta só ocorre com motivo registrado (`--nova-tentativa "motivo"`) e recebe outro identificador, sem apagar a anterior.

O manifesto (versionado) registra o commit da implementação, as versões das dependências, os parâmetros explícitos da coleta, os hashes, a conferência de cada série (cobertura, contagem, ordenação, datas repetidas e valores não finitos) e a situação, com três estados separados: snapshot (coletado e congelado), verificação de integridade (com ou sem pendência) e elegibilidade para a modelagem. Os CSVs e a resposta do BCB ficam fora do Git.

**Guarda dos dados brutos:** os hashes do manifesto permitem conferir os arquivos, mas não reconstruí-los. Depois da coleta, guardar uma cópia dos CSVs em armazenamento controlado, fora do Git.

O manifesto registra, para investigação e documentação (nada é corrigido automaticamente):
- triagem de diferenças entre retorno de preço e retorno ajustado por proventos (não detecta desdobramentos);
- desdobramentos e grupamentos informados pela fonte;
- conferência da faixa mínima ≤ abertura, fechamento ≤ máxima na base bruta e na base ajustada reconstruída com `a_t = Adj Close / Close`, e a diferença entre essa reconstrução e a série usada;
- datas em que o fator de ajuste muda sem provento nem desdobramento registrado.

```bash
python -m experiments.preditivo.executar listar-datas
```

Gera `datas_elegiveis.json` (N1): datas do período final com alvo realizado, pelo calendário e pelo horizonte, sem consultar erros.

```bash
python -m experiments.preditivo.executar qualidade
```

Compara os tratamentos possíveis das ocorrências de integridade sem ajustar nenhum modelo: amostras e variáveis invalidadas, datas afetadas e preservação do calendário.

```bash
python -m experiments.preditivo.executar desenvolver
```

Roda as 8 dobras de 2014 a 2021, com a política de qualidade de `politica_qualidade.json`. Recusa rodar enquanto a política tiver decisão pendente; `--ensaio` roda sem essa exigência e é registrado como ensaio, não como rodada oficial. Usa só preços anteriores à primeira data do período final (o 21º pregão de 2022), então o período final não é lido. Um teste garante isso.

```bash
python -m experiments.preditivo.executar final --confirmo-abertura
```

**Travado.** Só roda com as 8 condições da seção 12 do protocolo marcadas em `condicoes_abertura.json`, com os hashes ali iguais aos atuais e sem uso anterior. Na primeira execução grava `avaliacao_final_usada.json`, que impede uma segunda.

## Testes

```bash
python -m pytest experiments/preditivo/tests --no-cov
```

Os testes ficam fora da suíte do `core/` (`tests/`), porque o scikit-learn não é dependência do aplicativo. Cobrem:
- as verificações da coleta (OHLC em bases comparáveis, fator sem evento, desdobramentos);
- alinhamento das datas e fórmula do alvo (condição 4);
- ausência de informação futura nas variáveis;
- embargo e expurgo nas divisões externas e internas (condição 5);
- custos, caixa e referências do backtest (condição 6);
- a rotina do Diebold-Mariano com exemplo conferido à mão e todos os casos não calculáveis da nota;
- os critérios de elegibilidade;
- a trava da avaliação final;
- a separação entre desenvolvimento e período final.

## Interpretações a confirmar antes do congelamento

| Ponto | Implementação | Onde |
| --- | --- | --- |
| Embargo nas reestimações do período final | Embargo nas fronteiras dos blocos (dobras e início de 2022); nas reestimações de 2023 a 2026, sem nova interrupção, só expurgo. Formalização proposta no protocolo, seção 6.3 | `config.EMBARGO_NAS_REESTIMACOES_FINAIS`, `executar.embargos_periodo_final` |
| Tolerância da variância nula | Série constante se a amplitude for no máximo 10⁻¹² vezes o maior valor absoluto; entradas não finitas são verificadas antes | `estatistica.serie_constante` |
| Início do treino | A coleta começa em 02/01/2008; o aquecimento das variáveis (até 252 pregões) consome o começo da série, e as datas efetivas saem no manifesto e no relatório | `amostras.construir_amostras` |

## Registro de cada ajuste

Além do `alpha` e dos erros das validações internas, cada ajuste registra a média do alvo no treino, a média e o desvio das previsões, o uso de intercepto e se o `alpha` ficou no limite da grade. O resumo do desenvolvimento traz a frequência de seleção de cada `alpha`. Um `alpha` alto encolhe os coeficientes; com intercepto, as previsões tendem a uma constante ligada à média do alvo no treino, não necessariamente a zero.
