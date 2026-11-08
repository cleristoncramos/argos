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
| `dados.py` | Coleta, triagem de eventos, inconsistências OHLC, manifesto com hashes e leitura conferida | 3, 5, 8.3 |
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

Coleta e congela os dados uma única vez (preços ajustados, série de triagem e CDI da SGS 12) em `experiments/preditivo/dados/`, com `manifest.json`. Não sobrescreve um manifesto existente. Os CSVs ficam fora do Git; o manifesto é versionado.

```bash
python -m experiments.preditivo.executar listar-datas
```

Gera `datas_elegiveis.json` (N1): datas do período final com alvo realizado, pelo calendário e pelo horizonte, sem consultar erros.

```bash
python -m experiments.preditivo.executar desenvolver
```

Roda as 8 dobras de 2014 a 2021. Usa só preços anteriores à primeira data do período final (o 21º pregão de 2022), então o período final não é lido. Um teste garante isso.

```bash
python -m experiments.preditivo.executar final --confirmo-abertura
```

**Travado.** Só roda com as 8 condições da seção 12 do protocolo marcadas em `condicoes_abertura.json`, com os hashes ali iguais aos atuais e sem uso anterior. Na primeira execução grava `avaliacao_final_usada.json`, que impede uma segunda.

## Testes

```bash
python -m pytest experiments/preditivo/tests --no-cov
```

Os testes ficam fora da suíte do `core/` (`tests/`), porque o scikit-learn não é dependência do aplicativo. Cobrem:
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
| Embargo nas reestimações do período final | Só no início de 2022 (o período final aprovado é contínuo "a partir do 21º pregão de 2022"); em 2023 a 2026, só expurgo | `config.EMBARGO_NAS_REESTIMACOES_FINAIS` |
| Triagem de eventos | No yfinance, o fechamento "sem ajuste" já vem corrigido por desdobramentos; a triagem aponta sobretudo proventos | `dados.triagem_eventos` |
| Início do treino | A coleta começa em 02/01/2008; o aquecimento das variáveis (até 252 pregões) consome o começo da série, e as datas efetivas saem no manifesto e no relatório | `amostras.construir_amostras` |
