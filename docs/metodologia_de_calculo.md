# Metodologia de Cálculo — Argos DataLab

**Atualizado em:** 10/10/2026 (Plano 2, blocos 1 a 6) · Módulos: `core/analyzer.py`, `core/returns_utils.py`, `core/seasonality.py`, `core/trend.py`, `core/indicators.py`, `core/indicators_extra.py`, `core/risk_metrics.py`, `core/comparison.py`, `core/simulation.py`, `core/features.py`

Este documento descreve **o que cada número significa e como é calculado**. Os parâmetros que o usuário pode alterar estão indicados. Os dados de entrada e seu tratamento estão em `docs/fontes_e_tratamento_de_dados.md`.

> **Aviso.** Todos os resultados descrevem o comportamento histórico dos dados no período e na frequência escolhidos. Não são previsões, não são recomendação de compra ou venda e não consideram o perfil de quem usa a ferramenta.

---

## 1. Notação e convenções

| Símbolo | Significado |
| --- | --- |
| `C_t` (ou `V_t`) | Preço de fechamento do período `t` (coluna `Value`) |
| `r_t` | Retorno simples: `r_t = V_t / V_{t-1} − 1` |
| `k` | Fator de anualização: 252 (diário), 52 (semanal), 12 (mensal) |
| `N` | Janela do indicador, em períodos da frequência escolhida |

**Unidades.** `analyzer.py` e `seasonality.py` trabalham em **percentual** (5,0 = 5%); `risk_metrics.py`, `comparison.py`, `simulation.py` e `trend.py` em **decimal** (0,05 = 5%). A conversão para texto ocorre somente na interface.

**Retorno simples e lacunas de calendário.** Todo retorno percentual é calculado por `simple_returns(x) = x / x.shift(1) − 1` (`core/returns_utils.py`). Um valor ausente produz retorno **vazio** (NaN) naquele ponto e no seguinte; ele **não** é preenchido com o valor anterior. Essa fórmula não depende do parâmetro `fill_method` do pandas, cujo comportamento padrão mudou entre as versões 2.x e 3.x (a versão 2.x preenchia lacunas; a 3.x não). Testes em `tests/test_returns_gap.py`.

**Sem informação futura.** Cada indicador, em cada data `t`, usa apenas dados até `t`. Isso é verificado por testes automatizados.

---

## 2. Retorno e estatísticas da análise individual (`analyzer.py`)

| Medida | Definição | Unidade |
| --- | --- | --- |
| Primeiro / último valor | Primeiro e último `Value` do período agregado | Unidade do ativo |
| Variação percentual (`Pct_Change`) | `(V_t / V_{t-1} − 1) × 100` | % |
| Retorno total | `(V_último / V_primeiro − 1) × 100`. Se o primeiro valor for zero ou ausente, o resultado é vazio | % |
| Períodos analisados | Número de observações do período agregado | contagem |

**Retorno acumulado.** O retorno total é a valorização acumulada entre o início e o fim do período. É diferente do retorno de cada período, exibido no gráfico de variação percentual.

**Volatilidade mensal anualizada (Análise Individual).** Para cada mês do calendário, calcula-se o desvio-padrão amostral (`ddof = 1`) dos retornos diários do mês e multiplica-se por `√252 × 100`. Meses com uma única observação não têm desvio-padrão e ficam de fora. Barras acima do percentil 95 da série são destacadas.

**Matriz de retorno mensal (mapa de calor).** Para cada mês, `retorno = último valor do mês / último valor do mês anterior − 1`, em %. Usa o último fechamento de cada mês, **independentemente da frequência escolhida**, de modo que dados diários e mensais produzem o mesmo resultado. Ficam vazios: o primeiro mês da série, meses sem dados e o mês seguinte a uma lacuna.

**Média por mês do calendário.** Média, por mês (janeiro a dezembro), dos retornos mensais da matriz. Com poucos anos de histórico, a média é instável e não indica padrão que se repetirá.

---

## 2.1 Sazonalidade por anos, meses e janela de retorno (`seasonality.py`)

Todas as funções trabalham em **percentual** e usam o **último fechamento de cada mês** (independente da frequência escolhida), como a matriz de retorno mensal da seção 2.

| Medida | Definição |
| --- | --- |
| Média por mês do calendário | Média, nos anos disponíveis, do retorno daquele mês. É a visão padrão ("todos os anos") |
| Média do recorte | A mesma média, restrita aos anos escolhidos pelo usuário (só na Análise Individual) |
| Diferença | `média do recorte − média de todos os anos`, em **pontos percentuais** |
| Mediana | Mediana dos retornos do mês (N par: média dos dois valores centrais), nos anos considerados |
| Anos positivos (%) | `anos com retorno > 0 / anos com dado × 100`. Retorno exatamente zero **não** conta como positivo |
| N | Número de anos com dado naquele mês. Sempre exibido; mediana e % de anos positivos usam o mesmo N |
| Janela de retorno | `P(fechamento do mês de saída) / P(fechamento do mês de entrada) − 1`, por ano |

Regras da janela:

- **Setembro → outubro** é o fechamento de setembro até o de outubro, isto é, o **retorno de outubro**. Janelas mais longas são **compostas**, `(1+r₁)(1+r₂)(1+r₃) − 1`, nunca somadas (exemplo de teste: +10%, −10% e +20% compõem +18,8%, e não +20%).
- **Virada de ano** (entrada em novembro, saída em fevereiro): a saída pertence ao ano seguinte; o rótulo é o **ano da entrada**.
- **Dados ausentes:** se um dos dois fechamentos não existe, o ano fica fora da média e do N. Não há interpolação. Fechamento menor ou igual a zero também exclui o ano.
- **Mês em andamento:** o mês do calendário corrente não entra nas médias nem nas janelas, porque ainda não está completo. Ele continua visível no mapa de calor.
- Meses de entrada e de saída devem ser diferentes.

A média histórica representa o comportamento agregado dos anos disponíveis; um ano específico pode divergir significativamente dela, e a sazonalidade é evidência histórica descritiva, não padrão determinístico (texto obrigatório exibido na interface).

---

## 3. Indicadores técnicos (`indicators.py`, `indicators_extra.py`)

Os indicadores são **transformações matemáticas do histórico**. O Argos os usa para descrever tendência, momentum e dispersão, e **não** os converte em sinais de compra ou venda. As descrições exibidas na interface vêm de `core/indicator_docs.py`.

| Indicador | Categoria | Fórmula | Parâmetros (padrão) |
| --- | --- | --- | --- |
| SMA | Tendência | `SMA_t = (C_t + C_{t-1} + … + C_{t-N+1}) / N` | curta 20, longa 50 |
| EMA | Tendência | `EMA_t = α·C_t + (1 − α)·EMA_{t-1}`, `α = 2/(N+1)` | curta 12, longa 26 |
| Bandas de Bollinger | Volatilidade | Central = `SMA_N`; bandas = `SMA_N ± k·s_N`, com `s_N` desvio-padrão **amostral** (`ddof = 1`) | janela 20, `k` = 2,0 |
| RSI | Momentum | `RSI = 100 − 100/(1 + RS)`, `RS` = média de ganhos / média de perdas, ambas com suavização de Wilder (`α = 1/N`) | janela 14; níveis 30 e 70 |
| MACD | Momentum | `MACD = EMA_curta − EMA_longa`; `Sinal = EMA_9(MACD)`; `Histograma = MACD − Sinal` | EMAs 12 e 26 (usa os controles de EMA da página); sinal 9 |
| ATR | Volatilidade | `TR_t = max(H−L, |H−C_{t-1}|, |L−C_{t-1}|)`; `ATR_t` = suavização de Wilder (`α = 1/N`) de `TR` | janela 14 |
| Volatilidade móvel | Volatilidade | `Vol_t = desvio-padrão(r_{t-N+1..t}) × √k`, `r` = retorno simples (fração) | janela 20; `k` conforme a frequência |
| Volume | Volume | Soma das quantidades negociadas no período agregado | — |

**Decisões de implementação (aprovação do orientador pendente):**

- **RSI de Wilder**, com média inicializada no primeiro valor; por isso os primeiros pontos podem diferir levemente de outras plataformas.
- **Bollinger com `ddof = 1`** (desvio-padrão amostral). Algumas plataformas usam `ddof = 0`.
- **RSI de série sem variação** é indefinido (vazio), e não 50 nem 100.
- **ATR** e **volatilidade móvel** só aparecem depois de completada a janela (`min_periods = N`). No primeiro período, `TR = H − L`, pois não há fechamento anterior.
- **Aquecimento.** Os primeiros valores de EMAs e MACD dependem do ponto inicial da série e são menos confiáveis.
- A janela mínima de ATR e volatilidade móvel é 2; valores menores levantam erro.

**Limitações gerais.** Os parâmetros são convenções ajustáveis e os resultados mudam com eles; cruzamentos, faixas e níveis de referência descrevem o passado e **não** indicam resultado futuro; em frequência semanal ou mensal há menos observações, o que torna janelas longas menos estáveis.

**Camada de features (`features.py`).** Separada da visualização e da geração de sinais, reúne as variáveis que poderão alimentar modelos futuros. Cada indicador documentado informa se é candidato a feature (`feature_candidate`); o volume, por exemplo, não é. A ata prevê variáveis defasadas e a verificação de que nenhuma usa informação posterior ao instante `t`.

---

## 4. Métricas de risco e retorno (`risk_metrics.py`)

Todas são calculadas sobre a série `Value` da frequência escolhida, em formato **decimal**.

| Métrica | Definição | Leitura (descritiva) |
| --- | --- | --- |
| Retorno total | `V_último / V_primeiro − 1` | Valorização acumulada no período |
| Retorno médio | Média aritmética dos retornos simples `r_t` | Retorno típico por período; não é o retorno composto |
| Volatilidade anualizada | `desvio-padrão(r_t, ddof=1) × √k` | Dispersão histórica dos retornos; maior valor indica maior oscilação, sem dizer se o ativo é bom ou ruim |
| Percentual de períodos positivos | `proporção de r_t > 0` (retorno zero não conta como positivo) | Frequência de ganhos; não mede o tamanho de ganhos e perdas |
| Pico acumulado | `Running_Peak_t = max(V_1, …, V_t)` | Maior valor já alcançado até `t` |
| Drawdown | `Drawdown_t = V_t / Running_Peak_t − 1` (sempre ≤ 0) | Queda em relação ao maior pico anterior |
| Drawdown máximo | Menor valor da série de drawdown | Maior perda observada entre um pico e o fundo seguinte |
| Data do pior drawdown | Data do menor drawdown (a primeira, em caso de empate) | Data do **fundo** da queda, não a do pico |
| Índice de Sharpe | Ver abaixo | Relação histórica entre retorno excedente e risco |

**Índice de Sharpe anualizado.**

```text
taxa_periódica = (1 + taxa_livre_de_risco_anual) ^ (1/k) − 1
excesso_t      = r_t − taxa_periódica
Sharpe         = média(excesso) / desvio-padrão(excesso, ddof=1) × √k
```

- A taxa livre de risco é informada pelo usuário em % ao ano (padrão 0%); o fator `k` e a taxa usados aparecem na página.
- O resultado é **vazio** quando há menos de 2 retornos ou quando o desvio-padrão é zero.
- Depende diretamente do período, da frequência, da taxa e do fator `k`; alterar qualquer um altera o resultado.

**Entradas inválidas.** `calculate_drawdown` e `build_risk_summary` exigem valores numéricos maiores que zero e levantam `ValueError` caso contrário. As páginas capturam o erro e explicam o motivo (por exemplo, o petróleo WTI fechou negativo em 20/04/2020).

**Volatilidade sem dados.** Para série vazia ou constante, a função devolve 0,0. Na interface, isso significa "sem dados suficientes ou série constante", e não ausência de risco.

**Anualização.** O mesmo `k` vale para todas as classes de ativos. Para criptoativos, que negociam todos os dias, 365 poderia ser usado; o projeto mantém 252 por comparabilidade.

**Distribuição de retornos.** Histograma dos retornos por período em faixas de 5 pontos percentuais (de "abaixo de −30%" a "acima de 30%"). Descreve o passado, não projeta resultados.

---

## 5. Comparação de ativos (`comparison.py`, `comparison_checks.py`)

- **Base 100.** Cada série é dividida pelo seu **primeiro valor válido** e multiplicada por 100. Exige primeiro valor maior que zero. Compara trajetórias, não preços, e **não incorpora variação cambial**.
- **Tabela de preços.** Junção externa por data (ou por fim de período, ver `docs/fontes_e_tratamento_de_dados.md`), de modo que ativos com calendários diferentes permanecem na mesma tabela.
- **Retornos e correlação.** Retornos simples de cada ativo; correlação de Pearson entre os retornos. A matriz exibida é triangular (sem diagonal nem pares repetidos). A correlação mede associação linear no período, **não causalidade** e não garante comportamento futuro.
- **Resumo comparativo.** Observações, primeiro e último valor, retorno total e retorno médio por ativo, somados às métricas de risco da seção 4.
- **Destaques.** "Maior/menor retorno acumulado no período analisado", "menor queda máxima observada" e "maior Sharpe no período analisado" **descrevem o período analisado**; não indicam qual ativo é melhor.
- **Sazonalidade comparada.** Média do retorno mensal de cada mês do calendário, por ativo, com todos os anos disponíveis de cada um (`compare_monthly_averages`). Sem recorte por anos na Comparação. Ativos com históricos de tamanhos diferentes têm N diferentes, sempre exibidos.
- **Períodos divergentes.** Quando os ativos têm históricos de tamanhos diferentes, as métricas de cada um valem para o período dele, a menos que a opção "Comparar apenas o período comum" esteja ativa.
- **Taxas de juros.** Variações de nível de taxa não equivalem a retornos de preço e vêm com nota explicativa.

---

### 5.1 Tendência histórica: retorno móvel e razão de desempenho (`trend.py`)

Em **decimal**. Só estes dois recursos: sem regressão de tendência e sem detecção automática de cruzamentos. Os rótulos dizem "tendência histórica", e a interface avisa que a tendência passada pode mudar.

| Medida | Definição |
| --- | --- |
| Fechamento mensal | Último valor de cada mês, em calendário mensal contínuo; mês sem dado e mês em andamento são vazios |
| Retorno móvel de `w` meses | `P_t / P_{t−w} − 1`, com `w` = 3, 6 ou 12. Antes de haver `w` meses de histórico, o valor é **vazio**, não zero. Base menor ou igual a zero também dá vazio |
| Base 100 comum | Para cada par de ativos, ambas as séries são recolocadas em 100 na **primeira data em que as duas têm dado** |
| Razão de desempenho | `I_A,t / I_B,t − 1`, com `I` em base 100 comum. Zero significa desempenho igual desde o início comum. Com mais de dois ativos, cada ativo é comparado com um ativo de referência escolhido pelo usuário |
| Diferença de retorno móvel | `retorno móvel de A − retorno móvel de B` (em decimal; 0,05 = 5 pontos percentuais) |

Cuidados: a janela fica visível no título; a razão acumulada **depende da data inicial**, e um cruzamento da linha por zero pode mudar se o período mudar; o retorno móvel é menos sensível ao ponto de partida e deve ser lido junto com a razão; os dados não permitem concluir que um ativo continuará acima do outro.

---

## 6. Simulação histórica de aportes (`simulation.py`)

Simulação **educacional**, com valor hipotético informado pelo usuário. Não usa o perfil, a renda nem os objetivos do usuário.

| Item | Regra |
| --- | --- |
| Preço usado | Fechamento do período (`Value`) |
| Aporte único | Todo o valor no primeiro preço da série |
| Aportes periódicos | Valor igual a cada `every` observações, começando na primeira |
| Comparação | O aporte único usa o **mesmo total investido** dos aportes periódicos |
| Quantidade | Frações são permitidas |
| Resultado | Total investido, valor final, resultado, retorno sobre o investido e menor retorno ao longo do caminho |
| Janelas históricas | Para cada data inicial possível, o resultado de um horizonte fixo; resumo com menor retorno histórico, mediana, maior retorno histórico e proporção de janelas positivas (rótulos descritivos; não há "melhor" nem "pior" janela) |
| Não simuláveis | `^IRX`, `^FVX`, `^TNX`, `^TYX`, `^VIX` (taxas e indicadores, não ativos negociáveis) |
| Não considerado | Dividendos, taxas, impostos, câmbio e inflação |

O resumo das janelas não classifica nenhuma como "boa" ou "ruim" para investir; apenas descreve o que ocorreu. O texto obrigatório no topo da página é `SIMULATION_MANDATORY_TEXT`, e as premissas (fechamento sem ajuste por dividendos, sem custos, taxas ou impostos, valores na moeda do ativo) vêm de `SIMULATION_ASSUMPTIONS` (`core/simulation_texts.py`). O aviso completo continua em `SIMULATION_DISCLAIMER`.

---

## 7. Hipóteses para futura previsão (rascunho para discussão com o orientador)

> Esta seção registra **hipóteses a testar**, não resultados. Nenhuma capacidade preditiva foi demonstrada.

O que o Argos faz hoje é descritivo. A ata de 06/10/2026 prevê, numa etapa posterior, avaliar se os indicadores técnicos servem como variáveis de entrada de modelos simples. Pontos já definidos pela ata:

- **Modelos:** começar por benchmarks e modelos simples (regressão, classificação, ARIMA, Random Forest) antes de redes neurais.
- **Alvos candidatos:** retorno futuro, direção do retorno ou volatilidade futura (a definir).
- **Horizontes candidatos:** próximo dia, próxima semana, próximo mês (a definir).
- **Validação:** temporal, com separação entre treino, validação e teste e avaliação fora da amostra.

Hipóteses de trabalho (formulação final depende da pergunta de pesquisa):

1. **H0:** os indicadores técnicos, em variáveis defasadas, não melhoram a previsão fora da amostra em relação a benchmarks simples (por exemplo, "repetir o último valor" ou média histórica).
2. **H1:** indicadores de volatilidade (ATR, volatilidade móvel) ajudam a prever volatilidade futura melhor do que indicadores de tendência ou momentum.
3. **H2:** diferenças de desempenho entre modelos só são relevantes se persistirem em vários ativos e períodos, após comparação com benchmarks adequados.

Regras que o projeto adota para não afirmar mais do que os dados permitem:

- Não afirmar capacidade preditiva sem teste fora da amostra.
- Não afirmar superioridade de um modelo sem comparação com benchmarks.
- Não interpretar acurácia estatística como rentabilidade; separar resultado estatístico de utilidade econômica.
- Registrar limitações e resultados negativos.

O protocolo de validação temporal e o relatório metodológico fazem parte da etapa de validação acadêmica (`docs/checklist_pendencias.md`, seção 14).

---

## 8. Os resultados históricos não são previsões

Retornos, volatilidade, drawdown, Sharpe, correlação, indicadores e simulações descrevem **como os preços se comportaram** nos dados baixados. Padrões passados não garantem repetição futura. A ferramenta não avalia renda, dívidas, objetivos nem tolerância individual a risco e não deve ser usada como consultoria de investimentos.