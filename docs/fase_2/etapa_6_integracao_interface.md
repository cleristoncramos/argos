# Fase 2 — Etapa 6: Integração com a Interface

## Objetivo

Integrar os recursos analíticos desenvolvidos nas etapas anteriores à interface multipágina do Argos DataLab, mantendo consistência entre parâmetros, processamento, resultados exibidos e navegação.

## Escopo

Esta etapa trata exclusivamente da integração da camada analítica com a interface Streamlit. A qualidade e os testes são documentados na Etapa 7. A validação acadêmica e a publicação são documentadas na Etapa 8.

## Páginas integradas

A aplicação foi organizada nas seguintes telas:

| Arquivo | Responsabilidade |
|---|---|
| `app/main.py` | Análise individual, estatísticas, evolução temporal, variação percentual, sazonalidade, tabela, download e qualidade |
| `app/pages/1_Sobre_o_Projeto.py` | Propósito, escopo, contexto acadêmico e limitações |
| `app/pages/2_Comparacao_de_Ativos.py` | Comparação de 2 a 5 ativos, Base 100, correlação e métricas |
| `app/pages/3_Indicadores_Tecnicos.py` | SMA, EMA, Bollinger, RSI, MACD, candles, volume e exportação |
| `app/pages/4_Risco_e_Retorno.py` | Retorno, volatilidade, drawdown, Sharpe, histograma e exportação |

## Componentes compartilhados

A interface utiliza componentes reutilizáveis:

```text
app/ui/sidebar.py
app/ui/state.py
```

`app/ui/sidebar.py` concentra os controles comuns de ativo, datas e frequência. `app/ui/state.py` inicializa e sincroniza o estado persistente da análise individual.

## Integração do fluxo

O fluxo de uma consulta confirmada é:

```text
widget da interface
→ validação dos parâmetros
→ persistência dos controles
→ clique no botão de análise
→ chamada ao núcleo analítico
→ armazenamento do resultado
→ renderização dos gráficos e tabelas
→ exportação dos dados
```

A interface não realiza diretamente os cálculos principais. Ela chama funções de `core/`, recebe DataFrames e métricas e apresenta os resultados ao usuário.

## Estado persistente

As páginas utilizam `st.session_state` para manter:

- ativo selecionado;
- data inicial;
- data final;
- frequência;
- parâmetros específicos de cada análise;
- consulta confirmada;
- DataFrames processados;
- métricas calculadas;
- tabelas e matrizes de comparação.

As chaves persistentes são separadas das chaves temporárias dos widgets. Essa separação evita perda de parâmetros durante reruns do Streamlit e durante a navegação entre páginas.

## Regras de integração

- A consulta só é considerada confirmada após o botão correspondente ser acionado.
- Os resultados exibidos pertencem aos parâmetros armazenados na consulta confirmada.
- Alterar um widget não modifica retroativamente os resultados já calculados.
- Períodos inválidos são bloqueados antes da consulta.
- Dados vazios invalidam o resultado da página.
- Parâmetros específicos, como taxa livre de risco, são armazenados junto das métricas que produziram.

## Integração com o núcleo

A interface utiliza os módulos:

```text
core/data_loader.py
core/data_processor.py
core/analyzer.py
core/indicators.py
core/risk_metrics.py
core/comparison.py
core/visualizations.py
core/formatters.py
```

Essa divisão permite que a camada visual permaneça responsável pela interação e apresentação, enquanto as regras de coleta, transformação, cálculo e geração de gráficos ficam centralizadas no núcleo.

## Resultado

As funcionalidades da plataforma analítica passaram a estar disponíveis em uma interface multipágina coerente, com controles reutilizáveis, estado persistente, resultados confirmados, gráficos, tabelas e downloads.

## Documentos relacionados

- Registro original: `docs/etapa_6_integracao_interface.md`
- Etapa 7: `etapa_7_qualidade_testes_documentacao.md`
- Etapa 8: `etapa_8_validacao_academica_publicacao.md`
