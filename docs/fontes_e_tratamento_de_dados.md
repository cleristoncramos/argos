# Fontes e Tratamento de Dados — Argos DataLab

**Atualizado em:** 07/10/2026 · Módulos: `core/data_loader.py`, `core/data_processor.py`, `core/data_availability.py`, `core/ticker_input.py`, `core/periods.py`, `core/date_validation.py`

Este documento responde a quatro perguntas: de onde vêm os dados, o que o sistema faz com eles antes de calcular qualquer métrica, o que acontece quando os dados estão incompletos e quais são os limites da fonte.

---

## 1. Fonte de dados

- **Fonte única:** Yahoo Finance, acessado pela biblioteca `yfinance` (`Ticker.history`).
- **Natureza:** fonte pública e **não oficial**. O Yahoo Finance não fornece garantia contratual de disponibilidade, exatidão ou continuidade, e o `yfinance` não é um produto do Yahoo. A tela exibe a fonte e o horário da consulta.
- **Granularidade baixada:** apenas diária (`interval="1d"`). Séries semanais e mensais são **derivadas localmente** por agregação (seção 4).
- **Preços usados:** `Open`, `High`, `Low`, `Close` e `Volume`, com `auto_adjust=False`. A variável principal das análises é `Close`. O sistema **não usa** `Adj Close` e, portanto, não incorpora dividendos ao retorno: os retornos são de preço, não de retorno total.
- **Catálogo:** 120 ativos em 13 grupos (`docs/catalogo-de-ativos.md`). O catálogo é uma **amostra inicial**, não o universo do mercado. O usuário avançado pode digitar outro ticker do Yahoo Finance (seção 6).

## 2. Download

`download_active_data(symbol, start_date, end_date, interval)` normaliza os parâmetros e delega a `_download_active_data_cached`.

| Etapa | Regra |
| --- | --- |
| Normalização | Ticker em maiúsculas e sem espaços; intervalo em minúsculas |
| Data final | Soma 1 dia à data final pedida, porque o Yahoo trata o fim como exclusivo; sem isso o último pregão ficaria de fora |
| Repetições | Até 3 tentativas, com espera de 1,5 s, quando a resposta vem vazia, sem as colunas obrigatórias ou com erro de rede |
| Colunas | Se o `yfinance` devolver colunas em MultiIndex, mantém só o primeiro nível |
| Colunas obrigatórias | `Open`, `High`, `Low`, `Close`, `Volume`; a data pode vir como `Date` ou `Datetime` e é renomeada para `Date` |
| Fuso horário | Removido (`tz_localize(None)`); a data permanece a do horário local da bolsa |
| Ordenação | Crescente por data |
| Cache | 1 hora (`st.cache_data`, `ttl=3600`) |
| Falha | Levanta `DataUnavailable` dentro da função cacheada, de modo que **falhas temporárias não ficam em cache**; o chamador público recebe `None` |

Consequência do cache: uma consulta repetida dentro de 1 hora reaproveita os dados anteriores. A hora real da consulta aparece na página.

## 3. Preparação

`prepare_dataframe` mantém apenas as colunas `Date`, `Open`, `High`, `Low`, `Close` e `Volume` disponíveis, converte `Date` (descartando linhas com data inválida), ordena e cria `Year`, `Month` e `YearMonth`.

`validate_data` produz indicadores simples de qualidade, exibidos na página de Análise Individual: total de linhas, valores ausentes por coluna, datas duplicadas e fechamentos negativos.

## 4. Decisões sobre frequência

| Frequência | Fator de anualização | Como é obtida |
| --- | --- | --- |
| Diária | 252 | Dados como baixados |
| Semanal | 52 | Agrupamento por semana do calendário |
| Mensal | 12 | Agrupamento por mês do calendário |

**Regras de agregação OHLCV** (`aggregate_by_frequency`): `Open` = primeiro valor do período; `High` = máximo; `Low` = mínimo; `Close` = último valor; `Volume` = soma.

**Alinhamento na comparação.** Em frequência semanal ou mensal, a página de comparação alinha os ativos pelo **fim do período do calendário** (coluna `PeriodEnd`), e não pelo último pregão de cada ativo. Assim, ativos com calendários de negociação diferentes (feriados distintos, mercados 24 horas) caem na mesma linha. Se algum ativo não tiver `PeriodEnd`, o alinhamento volta a usar `Date`.

**Fator de anualização.** O mesmo fator (252, 52 ou 12) é aplicado a todas as classes para manter as métricas comparáveis. É uma convenção do projeto, não uma verdade universal: criptoativos negociam todos os dias, e 365 seria uma alternativa defensável. O fator usado aparece nas páginas de risco e comparação.

**Por que não há frequência semestral ou anual.** Com um período de 10 anos, haveria apenas 20 observações semestrais ou 10 anuais, o que torna volatilidade, Sharpe e correlação pouco estáveis. A inclusão depende de decisão do orientador.

**Observação sobre Indicadores Técnicos.** Essa página agrega semanal e mensal por reamostragem do calendário (`W` e `ME`), então as datas exibidas são os rótulos de fim de semana e de fim de mês, e não o último pregão.

## 5. Disponibilidade e dados insuficientes

O sistema separa **período solicitado** de **período disponível** (`assess_availability`). Pedir "10 anos" não garante 10 anos de dados.

| Situação | Regra | Mensagem |
| --- | --- | --- |
| Histórico menor que o pedido | Primeiro dado disponível mais de 10 dias depois do início pedido | Aviso: comum em criptomoedas e ativos recentes; as métricas valem para o período efetivamente disponível |
| Dados terminando antes do fim | Último dado mais de 7 dias antes do fim pedido | Aviso: pode indicar ativo sem negociação recente, descontinuado ou indisponibilidade da fonte |
| Dados insuficientes | Menos de 2 observações no período agregado | **Erro**: a análise não é gerada |
| Poucas observações | Menos de 12 observações no período agregado | Informação: estatísticas de amostras curtas são pouco estáveis |

As tolerâncias de 10 e 7 dias evitam falsos avisos causados por fins de semana e feriados nas pontas do período. Cada página exibe o período solicitado, o período disponível e a contagem de observações diárias e agregadas.

**Ativos com datas de início diferentes** (página de comparação):

- Cada ativo é analisado no seu próprio período disponível, e a página avisa quando os históricos divergem (`comparison_checks`).
- A opção **"Comparar apenas o período comum"** corta todos os ativos para o intervalo em que todos têm dados. Torna as métricas diretamente comparáveis, mas usa menos histórico. Sem período em comum, a comparação não é gerada.
- Ativos em moedas diferentes não têm variação cambial incorporada na Base 100 nem nos retornos.

## 6. Datas e tickers informados pelo usuário

- **Período personalizado** (`validate_date_range`): as duas datas são obrigatórias, a inicial deve ser anterior à final, e a final não pode estar no futuro. Com intervalo inválido, o botão de análise fica desabilitado e a mensagem de erro é exibida.
- **Ticker digitado:** é normalizado e validado por uma consulta curta (cerca de 15 dias) ao Yahoo Finance. Ticker inexistente gera mensagem clara. Tickers fora do catálogo funcionam, mas sem metadados do catálogo, e a tela informa isso.

## 7. Dados ausentes e valores inválidos

| Caso | Tratamento |
| --- | --- |
| Linha com data inválida | Descartada na preparação |
| Resposta vazia ou sem colunas obrigatórias | Repetição; depois, ativo tratado como indisponível |
| Primeira observação do período em retorno | Não existe retorno; a primeira linha de `Pct_Change` e de `Simple_Return` fica vazia |
| Mês sem dados na matriz mensal | Célula vazia; o mês seguinte a uma lacuna também fica vazio, pois não há valor anterior para comparar |
| Indicador sem janela completa | Valor vazio nos primeiros períodos (ATR e volatilidade móvel exigem a janela inteira) |
| RSI de série sem variação | Indefinido (vazio) |
| Preço ≤ 0 | `calculate_drawdown` e `build_risk_summary` levantam `ValueError`; as páginas exibem mensagem clara. Na comparação, o ativo é excluído e listado em aviso |
| Ativo com menos de 2 pontos na comparação | Excluído e listado em aviso |
| Volatilidade sem retornos ou série constante | Devolve 0,0; a interface deve explicar que isso significa "sem dados suficientes ou série constante", e não ausência de risco |

O sistema **não preenche lacunas por interpolação** nem inventa observações. Para a análise individual e o risco, retorno e drawdown são calculados sobre a sequência de observações disponíveis.

## 8. Limitações do yfinance e do Yahoo Finance

1. **Não oficial e sem garantia.** Estrutura, limites e disponibilidade podem mudar sem aviso, e a biblioteca pode quebrar entre versões (por exemplo, o formato das colunas).
2. **Falhas intermitentes.** O serviço pode devolver respostas vazias, limitar o número de requisições ou bloquear temporariamente. Por isso há repetições e o cache não guarda falhas.
3. **Profundidade de histórico variável.** Criptomoedas, IPOs, ETFs e FIIs recentes têm menos dados; alguns contratos futuros e índices têm lacunas.
4. **Dados revisáveis.** O Yahoo pode corrigir ou reajustar séries passadas (desdobramentos, eventos corporativos), de modo que duas consultas em datas diferentes podem não coincidir.
5. **Sem dividendos no retorno.** Os retornos são de preço de fechamento.
6. **Contratos futuros (`=F`).** São séries contínuas, sujeitas a efeitos de troca de contrato; podem assumir valores zero ou negativos (WTI em 20/04/2020).
7. **Taxas de juros (`^IRX`, `^FVX`, `^TNX`, `^TYX`).** São níveis de taxa (em %), não preços. O "retorno" dessas séries mede a variação do nível da taxa, e não o retorno de um título. Por isso não entram na simulação de aportes.
8. **Volume.** Índices e câmbio frequentemente não têm volume confiável; fontes e mercados diferem.
9. **Horário e calendário.** Cada mercado tem pregões e fusos próprios; o sistema remove o fuso e não converte horários entre mercados.
10. **Moedas.** Cada ativo é cotado na sua moeda de origem; o sistema não converte câmbio.

## 9. Resultados históricos não são previsões

Todos os números e gráficos do Argos descrevem o comportamento **passado** dos dados baixados, no período e na frequência escolhidos. Eles não projetam resultados futuros, não indicam o momento de comprar ou vender e não consideram renda, objetivos, dívidas ou tolerância individual a risco. Esse aviso aparece nas páginas e é parte do critério de aceite do projeto.