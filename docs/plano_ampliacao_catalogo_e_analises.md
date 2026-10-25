# Plano de ampliação do catálogo e de novas análises

**Status:** **aprovado com delimitações pelo orientador em 24/10/2026** (registro em [`pibiti/decisoes_orientador.md`](pibiti/decisoes_orientador.md)); a seção 9 resume os limites e prevalece sobre o texto original · **Elaborado em:** 24/10/2026 · **Referência externa analisada:** Investidor10 (investidor10.com.br), consulta em 24/10/2026

Este plano responde a três perguntas: (1) o que plataformas de mercado, como o Investidor10, oferecem em análise de séries históricas; (2) se o catálogo do Argos deve crescer, inclusive com criptomoedas recentes; e (3) quais novas análises cabem no objetivo do projeto. A execução é gradual e segue o cronograma aprovado (seção 9).

---

## 1. Premissas que delimitam o plano

1. **Objetivo do Argos.** Apoiar a interpretação de séries históricas por pessoas sem formação em finanças (pergunta de pesquisa A). O sistema **descreve o passado**. Não prevê preços, não recomenda compra ou venda e não avalia se um ativo está "barato" ou "caro".
2. **Decisões já registradas.**
   - N02: recorte por anos só na Análise Individual.
   - N04: a simulação mantém as janelas móveis.
   - N06: no máximo 5 ativos na comparação.
   - N07: sem regressão de tendência nem detecção automática de cruzamentos.
   - Dividendos, câmbio, inflação, custos e impostos estão fora dos cálculos ([`fora_do_escopo.md`](fora_do_escopo.md)).
3. **Prioridades do orientador (12/10/2026).** Na ordem:
   1. 7B (integração controlada da API).
   2. Modo de demonstração com dados salvos.
   3. Preparação documental do O6.
   4. Só depois, novas funções.

   Este plano **não passa à frente** dessas prioridades. Ele indica o que pode entrar antes do congelamento (fev/2027) e o que fica para depois.
4. **Fonte de dados.** Yahoo Finance (via `yfinance`). Qualquer ampliação precisa ter histórico disponível nessa fonte. Uma nova fonte, como o Banco Central para inflação, é uma nova dependência e exige justificativa.

---

## 2. O que o Investidor10 oferece e como isso se relaciona com o Argos

Levantamento feito nas páginas de ranking de criptomoedas, de ranking de ações, da ação PETR4 e do Bitcoin.

| Recurso no Investidor10 | Existe no Argos? | Cabe no objetivo? | Observação |
| --- | --- | --- | --- |
| Gráfico de cotação com períodos (1 D a 15 A) | Sim | Sim | Seletor de período e frequência na barra lateral |
| "Se você tivesse investido há 1 ano, hoje você teria…" | Sim (24/10/2026) | Sim | Simulação de Aportes, só com variação de preço |
| Tabela de rentabilidade por janela (1 m, 3 m, 1 a, 2 a, 5 a, 10 a) | **Parcial** | Sim | O Argos mostra primeiro e último valor do período escolhido. Falta a tabela de janelas fixas (proposta **A1**) |
| Rentabilidade real (descontada a inflação) | Não | Condicionado | Exige série de inflação (IPCA/CPI) e muda a premissa "só preço" (proposta **A6**) |
| Cotação ajustada (reinvestimento de dividendos) | Não | Condicionado | O Yahoo fornece o preço ajustado. Muda a premissa de cálculo (proposta **A6**) |
| Cotação em reais, dólares ou euros | Não | Condicionado | O catálogo já tem pares de câmbio. O câmbio está fora do escopo hoje (proposta **A5**) |
| Comparação do ativo com índices (Ibovespa, CDI, IPCA) | Parcial | Sim | A Comparação aceita índices, mas o usuário precisa escolhê-los. Proposta **A2**: referência automática |
| Comparação com outras ações do setor | Parcial | Sim | A Comparação tem filtros de grupo e subclasse |
| Comparação de uma empresa com uma commodity (ex.: Petrobras × Brent) | Parcial | Sim | Já é possível na Comparação (ação + commodity) |
| Rankings (maiores altas em 24 h e 30 d, valor de mercado) | Não | **Com cuidado** | Proposta **A3**: panorama descritivo do catálogo, sem formato de "oportunidade" |
| Dados históricos em tabela e download | Sim | Sim | "Dados Processados" e botão "Baixar CSV" |
| Indicadores fundamentalistas (P/L, P/VP, ROE, margens) | Não | Não | Análise de balanço, fora da proposta de séries de preço |
| "Preço justo" de Graham e "preço teto" de Bazin, *upside* | Não | **Não** | Sugere valor-alvo e decisão de compra, o que conflita com a neutralidade do Argos |
| *Checklist* do investidor, carteira recomendada, "mais queridas" | Não | **Não** | Recomendação ou popularidade, fora do objetivo |
| Fórum de discussão | Não | Não | Fora do escopo |

**Síntese.** O Investidor10 é uma plataforma de decisão de investimento. O Argos é uma ferramenta educativa de leitura do passado. Três ideias são aproveitáveis sem ferir a neutralidade:

- rentabilidade por janelas;
- comparação automática com uma referência;
- um panorama descritivo do catálogo.

Dividendos, inflação e câmbio são úteis, mas dependem de rever premissas. Valuation e recomendações não entram.

---

## 3. Diagnóstico do catálogo atual

O catálogo tem **120 ativos em 13 grupos e 9 classes** (`core/assets.py`).

| Grupo | Ativos | Lacuna observada |
| --- | ---: | --- |
| Criptomoedas | 10 | Só as maiores (BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, TRX, LINK). Faltam as tradicionais (LTC, BCH) e as de infraestrutura (DOT, NEAR) |
| Ações Brasil | 12 | Faltam setores: saneamento, aeronáutica, saúde, siderurgia, telecomunicações, varejo, tecnologia e banco de investimento |
| FIIs Brasil | 5 | Faltam fundos de papel (recebíveis) e de shopping de outros gestores |
| ETFs de ações | 10 | **Nenhum ETF negociado na B3** (BOVA11, IVVB11, SMAL11, DIVO11) |
| ETFs de renda fixa | 6 | Todos dos EUA |
| Ações EUA, Europa e Ásia, REITs, índices, câmbio, commodities, juros | 51 | Cobertura adequada para fins educativos |

**Custo de ampliar.** O número 120 está fixo em vários pontos:

- a validação de `core/assets.py`;
- `tests/test_assets.py`;
- o texto de `core/catalog_notice.py`;
- `docs/catalogo-de-ativos.md`;
- o modal acadêmico e a página Sobre o Projeto.

Cada ativo novo também precisa de:

- logotipo (`core/asset_logos.py`);
- subclasse e mercado;
- descrição;
- **dados salvos no modo de demonstração**.

Por isso, a ampliação deve ser feita **uma vez, em lote, antes de gerar os dados do modo demo**, e não aos poucos.

---

## 4. Criptomoedas recentes com altas fortes: análise e posição proposta

O ranking de maiores altas em 30 dias do Investidor10 mostrava, em 24/10/2026, o token **DHN (Dohrnii) com +14.067%**.

- **Observação.** No Yahoo Finance, o fechamento mensal do DHN ficou entre US$ 3 e US$ 6 de outubro/2025 a setembro/2026 e foi de **US$ 479,63 em outubro/2026**, cerca de 145 vezes o mês anterior.
- **Hipóteses, não demonstradas.** Um salto dessa ordem pode ter várias explicações: baixa negociação, oferta concentrada, evento do próprio projeto ou falha da fonte. Os dados de preço, sozinhos, não permitem afirmar nenhuma delas. O ponto didático é a **necessidade de investigar** antes de interpretar, não a atribuição de uma causa.

**Riscos de incluir criptomoedas pelo desempenho recente:**

1. **Viés de seleção e de sobrevivência.** Escolher ativos *porque* subiram ensina a conclusão errada: que altas passadas indicam altas futuras. Os textos do Argos combatem exatamente essa leitura.
2. **Histórico curto.** Por exemplo, HYPE tem cerca de 2 anos de dados (694 observações). Sazonalidade, janelas móveis e volatilidade mensal ficam pouco confiáveis.
3. **Qualidade dos dados.** Saltos dessa ordem merecem atenção e verificação. O Argos hoje não sinaliza isso.
4. **Aparência de recomendação.** Uma lista curada com "as que mais subiram" lê-se como sugestão de compra.

**Posição proposta:**

- **Não** incluir no catálogo ativos escolhidos pelo desempenho recente.
- Ampliar as criptomoedas por **critérios fixos e documentados**:
  - pelo menos 3 anos de histórico no Yahoo;
  - estar entre as maiores por capitalização;
  - não ser *stablecoin*, cuja variação é quase nula;
  - representar um uso distinto: pagamento, contratos inteligentes, finanças descentralizadas ou infraestrutura.
- Criptomoedas recentes continuam acessíveis pelo modo **"Digitar ticker"**, que já existe. Ele passa a exibir **alertas automáticos** de histórico curto e de saltos atípicos (proposta **A4**).
- O caso DHN pode virar **material didático**: um exemplo, na página Sobre ou no glossário, de por que "maior alta do mês" não descreve risco.

---

## 5. Proposta de ampliação do catálogo (120 → 150)

Todos os tickers abaixo foram verificados no Yahoo Finance em 24/10/2026 (data do primeiro dado disponível). Os critérios são os da seção 2 de [`catalogo-de-ativos.md`](catalogo-de-ativos.md), acrescidos do mínimo de 3 anos de histórico.

| Grupo | Inclusões propostas (+30) | Histórico no Yahoo desde | Motivo |
| --- | --- | --- | --- |
| Criptomoedas (+8) | LTC-USD, BCH-USD, XLM-USD, DOT-USD, NEAR-USD, AAVE-USD, UNI7083-USD, HBAR-USD | 2014 a 2020 | Usos distintos (pagamento, infraestrutura, finanças descentralizadas), todas com mais de 5 anos de dados |
| Ações Brasil (+10) | PRIO3, SBSP3, EMBJ3, BPAC11, RDOR3, EQTL3, GGBR4, VIVT3, RADL3, TOTS3 | 2000 a 2020 | Cobre setores ausentes: petróleo independente, saneamento, aeronáutica, banco de investimento, saúde, energia, siderurgia, telecomunicações, farmácias e tecnologia |
| FIIs Brasil (+4) | KNCR11, CPTS11, HGRU11, VISC11 | 2014 a 2018 | Fundos de papel (recebíveis) e de renda urbana e shopping |
| ETFs da B3 (+6) | BOVA11, SMAL11, IVVB11, DIVO11, GOLD11, HASH11 | 2008 a 2021 | ETFs em reais: Ibovespa, small caps, S&P 500, dividendos, ouro e cesta de criptoativos. Classificar pela exposição (GOLD11 junto ao ouro, HASH11 junto a criptoativos), não só pela bolsa |
| Ações EUA (+2) | a definir (ex.: um nome de saúde e um de consumo) | — | Opcional, para equilibrar setores |

**Reserva** (atendem aos critérios e podem substituir alguma inclusão): **SUI20947-USD** (dados desde mai/2023) e **APT21794-USD** (desde out/2022).

**Ficam fora desta rodada:**

- **HYPE:** cerca de 2 anos de histórico.
- **TON:** TON11419-USD retorna só uma observação e TON-USD é outra série. O ticker precisa de verificação.
- **PEPE e SHIB:** moedas de meme, sem uso distinto; a categoria já é representada pelo DOGE.
- **CPLE6:** sem dados no Yahoo.
- **VGHF11:** cerca de 2,7 anos de histórico.

**Grupo "Criptomoedas recentes":** não será criado nesta rodada (parecer de 24/10/2026). Esses ativos seguem acessíveis pelo "Digitar ticker", com os alertas da A4.

---

## 6. Novas análises dentro do objetivo

Todas descrevem o passado, usam linguagem neutra (verificada por `core/disclaimers.py`) e seguem o padrão do projeto:

- cálculo puro em `core/`, com 100% de cobertura de testes;
- apresentação em `app/`;
- roteiro "Como ler este gráfico" para cada gráfico novo.

### A1. Tabela de variação por janelas (Análise Individual)

- **O quê.** Uma linha com a variação em 1 mês, 3 meses, 6 meses, no ano, em 1, 2, 5 e 10 anos, e a taxa equivalente ao ano para janelas de 1 ano ou mais. As janelas sem dado suficiente aparecem como "—".
- **Por quê.** Responde "quanto variou em cada prazo?" sem exigir que a pessoa troque o período na barra lateral. É o recurso mais usado no Investidor10.
- **Onde.** `core/periods.py` ou `core/returns_utils.py` (`window_returns_table`); seção nova em "Visão Geral do Ativo".
- **Esforço:** baixo. **Risco:** baixo.

### A2. Referência automática do mercado (Análise Individual e Risco e Retorno)

- **O quê.** Mostrar ao lado do ativo a variação, no mesmo período, de uma referência definida pelo mercado do ativo: Ibovespa para ações e FIIs brasileiros, S&P 500 para EUA, Bitcoin para criptomoedas e o índice local para Europa e Ásia. Um único gráfico em base 100, sem regressão nem beta.
- **Por quê.** "Subiu 20%" só faz sentido diante do mercado. Hoje isso exige montar a comparação manualmente.
- **Cuidado.** Não chamar a referência de "o mercado a bater". Texto obrigatório: "diferenças passadas não se repetem necessariamente".
- **Esforço:** médio. **Risco:** baixo. **Depende de:** aval do orientador (proximidade com a decisão N07).

### A3. Panorama do catálogo (página ou aba nova)

- **O quê.** Tabela de todos os ativos de um grupo, ordenável, com:
  - variação em 1 mês, 12 meses e 5 anos;
  - volatilidade anualizada;
  - queda máxima;
  - anos de histórico.

  É o equivalente descritivo dos rankings do Investidor10.
- **Neutralidade.**
  - Nenhum rótulo de "melhor", "oportunidade" ou "em alta".
  - Ordenação padrão por nome, não por desempenho.
  - Aviso fixo: "variação passada não indica variação futura; a ordem da tabela não é uma recomendação".
  - Volatilidade e queda máxima ficam sempre ao lado do retorno, para que alta e risco apareçam juntos.
- **Técnica.**
  - Download em lote (`yf.download` com vários tickers) e cache de 1 h.
  - No modo demo, usa os dados salvos.
  - É a função mais cara em rede: precisa de limite de tempo e mensagem de falha parcial.
- **Esforço:** médio a alto. **Risco:** médio, pela aparência de ranking. **Depende de:** aval do orientador.

### A4. Alertas de qualidade e de comportamento atípico dos dados

- **O quê.** Sinalizar, no bloco de disponibilidade e em "Detalhes do processamento":
  - histórico curto (menos de 3 anos);
  - variação diária atípica (por exemplo, mais de 50% em um dia ou mais de 10 desvios-padrão);
  - volume zero ou ausente em muitos dias;
  - preços repetidos por vários dias seguidos.
- **Por quê.** Protege a interpretação em ativos como o DHN e reforça o objetivo de qualidade de dados já existente (`core/data_availability.py`). Vale para o catálogo e para o modo "Digitar ticker".
- **Esforço:** baixo a médio. **Risco:** baixo. **Prioridade alta**, porque também melhora o que já existe.

### A5. Valores convertidos para reais (opcional)

- **O quê.** Opção de ver ativos cotados em dólar convertidos para reais pelo par USDBRL=X do catálogo, com o aviso de que o resultado passa a misturar ativo e câmbio.
- **Depende de:** rever a premissa "sem câmbio". **Situação:** condicionado (Plano 3).

### A6. Dividendos e inflação (opcional)

- **O quê.**
  - Alternar entre "só preço" e "preço com reinvestimento de proventos", usando o preço ajustado do Yahoo.
  - Mostrar a variação real, descontada a inflação: IPCA pela API SGS do Banco Central, série 433, ou CPI.
- **Depende de:**
  - rever as premissas de cálculo e dos textos;
  - aceitar uma nova fonte de dados (Banco Central);
  - revalidar o prompt da LLM, que hoje cita "sem dividendos".

  **Situação:** condicionado (Plano 3, depois do congelamento).

### A7. Tempo de recuperação das quedas (Risco e Retorno)

- **O quê.** Para as maiores quedas do período, mostrar quantos dias o preço levou para voltar ao pico anterior ou indicar que ainda não voltou. Pode aparecer como tabela das 3 maiores quedas, com início, fundo, recuperação e duração.
- **Por quê.** Traduz a queda máxima, que é abstrata, em tempo, algo mais fácil de entender para quem não é da área.
- **Esforço:** baixo, pois aproveita o `calculate_drawdown` existente. **Risco:** baixo.

### A8. Maiores altas e quedas do período, com datas (Análise Individual)

- **O quê.** As 5 maiores altas e as 5 maiores quedas na frequência escolhida, com data, e a proporção de períodos de alta e de baixa.
- **Por quê.** Mostra que poucos dias concentram grande parte do resultado. É descritivo e didático.
- **Esforço:** baixo. **Risco:** baixo.

**Itens analisados e descartados:**

- preço justo e preço teto;
- indicadores fundamentalistas;
- *checklist* de compra;
- rankings de popularidade;
- previsão de preços;
- qualquer pontuação ou nota de ativo.

---

## 7. Cronograma proposto

As fases respeitam as prioridades do orientador (seção 1, item 3). As fases 1 e 2 só começam com a 7B estabilizada. O catálogo precisa estar definido **antes** de gerar os dados do modo demo.

| Fase | Período sugerido | Conteúdo | Critério de aceite |
| --- | --- | --- | --- |
| 0 | nov/2026 (1 semana) | Levar este plano ao orientador e registrar as decisões em `pibiti/decisoes_orientador.md` | Decisões sobre A2, A3, A5, A6, a ampliação e o grupo opcional de recentes |
| 1 | nov/2026 (2 semanas) | **A4** (alertas de dados), **A1** (janelas), **A7** (recuperação) e **A8** (altas e quedas) | Funções em `core/` com 100% de cobertura, roteiros de leitura, linguagem neutra testada e conferência no navegador |
| 2 | nov–dez/2026 (2 semanas) | **Ampliação do catálogo** (120 → 150), com logotipos, subclasses, descrições, documentação e contagens atualizadas | `test_assets` com a nova contagem, todos os tickers com histórico verificado e documentação revisada |
| 3 | dez/2026 (2 a 3 semanas) | **A2** (referência automática) e **A3** (panorama), se aprovados | Avisos de neutralidade, tempo de carga aceitável com cache e funcionamento no modo demo |
| 4 | jan/2027 | Gerar os dados do modo demo com o catálogo final, revisar textos e preparar o congelamento | Demo funcionando sem internet com todos os ativos |
| Plano 3 | depois de fev/2027 | **A5** (reais), **A6** (dividendos e inflação) e grupo "Criptomoedas recentes" | Conforme novas decisões |

---

## 8. Decisões a levar ao orientador

1. Aprovar a ampliação do catálogo para cerca de 150 ativos com os critérios da seção 5, ou manter 120.
2. Aprovar o critério de 3 anos de histórico mínimo para criptomoedas e a recusa de inclusões pelo desempenho recente.
3. Aprovar o grupo opcional "Criptomoedas recentes", com aviso, ou deixar esses ativos só no modo "Digitar ticker".
4. Aprovar A2 (referência automática), avaliando a proximidade com a decisão N07.
5. Aprovar A3 (panorama do catálogo), avaliando o risco de leitura como ranking de recomendação.
6. Confirmar que A5 e A6 (câmbio, dividendos e inflação) ficam para depois do congelamento.
7. Confirmar o encaixe das fases 1 a 3 entre a 7B, o modo demo e o O6.

---

## 9. Parecer do orientador (24/10/2026): delimitações aprovadas

O texto completo da decisão está em [`pibiti/decisoes_orientador.md`](pibiti/decisoes_orientador.md). Em caso de divergência com as seções anteriores, valem estes limites.

**Não autorizado nesta rodada:** valuation, preço justo, preço teto, recomendação, pontuação de ativos, classificação de ativos como oportunidade e previsão.

| Item | Situação | Requisitos acrescentados pelo parecer |
| --- | --- | --- |
| Catálogo | Aprovado (cerca de 150) | 150 é referência, não meta. Conferência técnica de cada inclusão; classificação pela exposição; substituições justificadas no registro do catálogo |
| Criptomoedas | Critérios aprovados | 3 anos de histórico, capitalização com fonte e data, diversidade de usos, dados suficientes, nada motivado só por alta recente. Sem grupo "recentes" |
| A1 | Aprovada | Datas efetivamente usadas; "—" sem histórico; acumulada × taxa anual; base explícita (todo o histórico ou recorte da interface) |
| A2 | Aprovada | Referência de comparação, não meta; escolha explicada; desativável e, se viável, substituível; período comum; avisos de moeda e calendário; sem referência adequada, não mostrar |
| A3 | Aprovada, gradual | Por grupo; ordenação inicial por nome; retorno com volatilidade e queda máxima; período e histórico; aviso de não recomendação; falhas parciais sem zeros; cache e limites; sem destacar "vencedores" |
| A4 | Aprovada, prioridade alta | Sinalizar sem concluir erro ou manipulação; limiares como heurísticas documentadas e testadas; regras por classe; ausência de volume não reprova séries em que o campo não se aplica |
| A7 | Aprovada | Início, fundo, recuperação, duração e "não recuperado até a última observação disponível"; unidade da duração definida |
| A8 | Aprovada | Extremos com datas e frequência; sem afirmar que poucos dias explicam o resultado, salvo cálculo próprio |
| A5, A6 | Plano 3 | Especificação própria; preço ajustado descrito como a fonte o trata |

**Cronograma aprovado.** Substitui a seção 7.

| Período | Entrega |
| --- | --- |
| Antes das novas funções | Estabilidade da 7B, estrutura do modo demo e preparação documental do O6 |
| Novembro/2026 | A4, A1, A7 e A8 |
| Novembro a dezembro/2026 | Ampliação do catálogo |
| Dezembro/2026 | A2 e primeira versão da A3 |
| Janeiro/2027 | Atualização dos dados salvos, integração e revisão (testes sem internet) |
| Fevereiro/2027 | Congelamento |
| Depois do congelamento | A5, A6 e demais extensões |

**Ordem de preservação em caso de conflito:**

1. 7B;
2. modo demo;
3. O6;
4. alertas e análises simples;
5. catálogo;
6. referência automática;
7. panorama.

**Explicação assistida.** As novas funções nascem com "Como ler este gráfico". Os novos ativos não exigem mudar o prompt congelado. Um novo tipo de análise só entra no contexto da LLM após testes de compatibilidade, rastreabilidade e neutralidade. Até lá, a função usa apenas a explicação fixa.

**Registros a manter durante a execução:**

- critérios e lista final do catálogo;
- inclusões, substituições e exclusões justificadas;
- metodologia dos novos cálculos;
- testes e conferência das telas;
- atualização do modo demo;
- limitações;
- ajustes do cronograma.

---

## 10. Registro de execução

| Data | Item | Situação | Registro |
| --- | --- | --- | --- |
| 24/10/2026 | A4 — alertas de qualidade dos dados | **Implementado** | `core/data_quality.py` (100% de cobertura), quadro "Atenção aos dados" nas cinco páginas de análise e linha "Verificações de qualidade" nos detalhes. Metodologia, limiares, calibração e limitações em [`metodologia_de_calculo.md`](metodologia_de_calculo.md), seção 2.2. Conferido no navegador com XPML11.SA (aviso de mudança de patamar em 14/01/2026), DHN-USD pelo "Digitar ticker" e a Comparação XPML11 × MXRF11 |
| 24/10/2026 | A1 — variação por janelas | **Implementado** | `core/trailing_returns.py` e `app/ui/trailing_table.py` (100% de cobertura no `core`). Base explícita (período carregado, fechamentos diários), datas usadas, "—" sem histórico, início ajustado marcado, variação acumulada separada da taxa equivalente ao ano. Metodologia em [`metodologia_de_calculo.md`](metodologia_de_calculo.md), seção 2.3. Conferido no navegador com PETR4 (5 e 10 anos) e ^TNX (tabela não exibida para taxas) |
| 24/10/2026 | A7 — tempo de recuperação das quedas | **Implementado** | `core/drawdown_episodes.py` e `app/ui/drawdown_table.py` (100% de cobertura no `core`). Três maiores quedas com início (pico), fundo, recuperação do pico, duração de cada etapa em dias corridos (com aproximação em meses ou anos) e "não recuperado até a última observação disponível", sem estimativa. Metodologia em [`metodologia_de_calculo.md`](metodologia_de_calculo.md), seção 4.1. Conferido no navegador com PETR4 (10 anos, mensal) e BTC (5 anos, diário, com uma queda não recuperada) |
| 24/10/2026 | A8 — maiores altas e quedas | **Implementado** | `core/extreme_moves.py` e `app/ui/extremes_table.py` (100% de cobertura no `core`). Cinco maiores altas e cinco maiores quedas com período, datas e fechamentos comparados, contagem de variações positivas e negativas e marca "(em andamento)" no último período incompleto. A nota informa que a tabela não mede a contribuição desses períodos para o resultado total. Metodologia em [`metodologia_de_calculo.md`](metodologia_de_calculo.md), seção 2.4. Conferido no navegador com PETR4 (5 anos, mensal e diário) |
| 24/10/2026 | **Fase 1** (A4, A1, A7 e A8) | Publicação verificada em 25/10/2026 (commit `958b729`) | Próxima etapa do cronograma aprovado: ampliação do catálogo (fase 2) |
| 24/10/2026 | Fase 2 — ampliação do catálogo | **Implementada**; publicação verificada em 25/10/2026 (commit `958b729`) | 120 → 148 ativos: 29 inclusões (8 criptomoedas, 10 ações brasileiras, 2 dos EUA, 3 FIIs, 4 ETFs de ações da B3, `GOLD11` e `HASH11` classificados pela exposição) e 1 exclusão (`XPML11.SA`, por descontinuidade na fonte, substituído por `VISC11.SA`). `CPTS11.SA` não entrou por dados sem continuidade. Conferência técnica, capitalização com fonte e data, exclusões e logos em [`catalogo-de-ativos.md`](catalogo-de-ativos.md), seção 40. Logos sem fonte utilizável passaram a mostrar o ícone da classe (antes apareciam quebrados) |
| 24/10/2026 | A2 — referência automática | **Implementado** | `core/benchmark.py` (100% de cobertura): sugestão por ativo com motivo explicado, troca ou desativação pelo usuário, Base 100 só nas datas comuns, avisos de moeda, unidade e calendário, e nenhuma sugestão quando não há referência adequada (FIIs, Europa, Ásia, ETFs globais e de renda fixa e outros). Novo roteiro `referencia_base100`; contexto da LLM inalterado. Metodologia em [`metodologia_de_calculo.md`](metodologia_de_calculo.md), seção 2.5. Conferido no navegador com PETR4, IVVB11, ETH e MXRF11 |
| 25/10/2026 | A3 — panorama do catálogo (primeira versão) | **Implementado** | Página "Panorama do Catálogo" (módulo 06): consulta de um grupo por vez sob demanda, com cache e limite de 25 ativos; ordem inicial por nome; retorno ao lado de volatilidade e queda máxima; período e início dos dados indicados; aviso de que a ordem não é recomendação; falhas parciais vazias, nunca zero. `core/panorama.py` com 100% de cobertura. Metodologia em [`metodologia_de_calculo.md`](metodologia_de_calculo.md), seção 5.2. Conferido no navegador com Ações Brasil (22 ativos) e Treasury |
| 25/10/2026 | **Fase 3** (A2 e primeira versão da A3) | Publicação verificada em 25/10/2026 (commit `958b729`) | Próxima etapa do cronograma: atualização dos dados salvos do modo demo, integração e revisão (janeiro/2027) |
| 24/10/2026 | Achado da calibração | Registrado | XPML11.SA tem, na fonte, três pregões (14 a 16/01/2026) cotados a cerca de 1/100 do nível habitual. Retornos, volatilidade e queda máxima que incluem essas datas são afetados. A causa não foi verificada; o alerta informa o usuário. Decidir na revisão do catálogo (fase 2) se o ativo permanece ou se a série precisa de tratamento documentado |

---

## 11. Atualização de 25/10/2026 — Fases 1 a 3

Conforme registro do desenvolvedor, as fases 1, 2 e 3 foram implementadas
e publicadas, incluindo A4, A1, A7, A8, ampliação do catálogo para 148
ativos, A2 e a primeira versão de A3.

As entregas possuem testes, metodologia documentada e registro no plano.
Permanece pendente a conferência manual da versão publicada no Streamlit
Community Cloud.

A próxima atividade imediata é verificar o deploy e registrar os resultados
por funcionalidade, com identificação do commit publicado.

A regeneração preliminar dos dados do modo demo poderá ser antecipada.
Permanecem previstos para janeiro de 2027 a atualização final dos dados
salvos, os testes completos sem internet e a revisão geral preparatória
para o congelamento de fevereiro de 2027.

A preparação documental do O6 continuará em paralelo.

**Situação das fases 1 a 3:** implementação concluída; validação do deploy pendente.

**Conferência 1 da versão publicada (25/10/2026, commit `6ab02d1`):** registrada em [`verificacao_publicacao.md`](verificacao_publicacao.md). A4, A1, A7, A8, catálogo, A2 e A3 foram conferidos. A página inicial apresentou `IndexError`, já corrigido localmente, com um teste de fumaça novo. A correção ainda precisa ser publicada e reconferida. O modo demo completo não reproduz as respostas de IA salvas (período do pacote diferente), o que fica para o primeiro snapshot. Situação: conferida com pendência; ainda não "publicação verificada".

**Conferência 2 (25/10/2026, commit `958b729`):** a correção foi publicada e a versão foi reconferida por inteiro. As 7 páginas e a página inicial abrem sem erro, e todos os blocos repetem os resultados da conferência 1. **Situação das fases 1 a 3: publicação verificada.** As ressalvas (falha parcial do panorama coberta só por testes; ajustes do modo demo) estão em [`verificacao_publicacao.md`](verificacao_publicacao.md). Próximo passo: primeiro snapshot do catálogo ampliado no modo demo, resolvendo os achados 2 e 3.

**Primeiro snapshot do modo demo (25/10/2026):** 148 ativos, de 01/12/2020 a 23/10/2026 (versão `v1.1-demo-preliminar`). Os achados 2 e 3 foram resolvidos: as 5 telas com respostas de IA salvas as reproduzem no modo demo completo, e a referência Ibovespa funciona offline. Os recursos novos (A1, A2, A3, A7 e A8) foram conferidos no modo demo. Seguem para janeiro/2027 o snapshot final, o roteiro completo sem internet e o teste de memória (`docs/demonstracao.md`, seção 2.3.2).

**Organização sugerida pelo orientador (25/10/2026):**

| Momento | Atividade |
| --- | --- |
| Agora | Conferir o deploy e corrigir eventuais diferenças em relação à versão local |
| Após a conferência | Gerar um primeiro snapshot do catálogo ampliado e testar os novos recursos no modo demo |
| Novembro–dezembro/2026 | Corrigir falhas, preparar o O6 e manter documentação e dados organizados |
| Janeiro/2027 | Atualizar o snapshot final, executar o roteiro completo sem internet e revisar o pacote |
| Fevereiro/2027 | Congelar a versão identificada por commit/tag, com evidências dos testes |

Nenhuma funcionalidade nova será aberta neste ciclo: o objetivo é transformar
as entregas em uma versão verificada, reproduzível e pronta para avaliação e
demonstração.

---

## 12. Atualização de 25/10/2026 — Estabilização e preparação do congelamento

Conforme conferência registrada pelo desenvolvedor, as fases 1 a 3 estão
publicadas e verificadas no Streamlit Community Cloud.

O erro identificado na página inicial foi corrigido, com inclusão de teste de
regressão. O primeiro snapshot do modo de demonstração foi gerado e os dois
achados identificados nessa preparação foram resolvidos.

Novembro e dezembro de 2026 ficam destinados a eventuais correções e à
preparação documental do O6, em paralelo, sem previsão de novas ampliações
funcionais neste ciclo.

Em janeiro de 2027 serão realizados:
- geração do snapshot final;
- execução local do roteiro completo com internet desativada;
- teste de consumo de memória da aplicação no Streamlit Community Cloud;
- consolidação das evidências e revisão das pendências.

O congelamento permanece previsto para fevereiro de 2027, condicionado à
resolução das falhas críticas e à identificação da versão por commit/tag.

A conclusão do primeiro snapshot não equivale à conclusão da validação offline
final. A preparação do O6 não autoriza o início da coleta com participantes.

**Escopo dos dois testes de janeiro (orientação de 25/10/2026).** São verificações separadas:

- o **teste sem internet** é executado na **instalação local**, com `ARGOS_DEMO_MODE=true` e o pacote de dados salvos;
- o **teste de memória** verifica a **aplicação hospedada** no Streamlit Community Cloud, que roda com dados consultados na fonte e não usa o pacote do modo demo.

### 12.1 Registro atual: entregas, versão publicada e snapshot

| Entrega | Commit da implementação | Data |
| --- | --- | --- |
| A4 — alertas de qualidade dos dados | `b6c7657` | 24/10/2026 |
| A1 — variação por prazo | `91ad1b9` | 24/10/2026 |
| A7 — maiores quedas e recuperação | `d7885c4` | 24/10/2026 |
| A8 — maiores altas e quedas (fim da fase 1) | `ea31028` | 24/10/2026 |
| Fase 2 — catálogo com 148 ativos | `bddcceb` | 24/10/2026 |
| A2 — referência de mercado | `343e399` | 24/10/2026 |
| A3 — Panorama do Catálogo, primeira versão (fim da fase 3) | `6ab02d1` | 25/10/2026 |
| Correção da página inicial e teste de fumaça (regressão) | `958b729` | 25/10/2026 |

| Registro | Identificação |
| --- | --- |
| Conferência da versão publicada | 25/10/2026. Conferência 1 sobre o commit `6ab02d1` (encontrou o erro da página inicial); conferência 2 sobre o commit **`958b729`**, com **publicação verificada** das fases 1 a 3. Registro em [`verificacao_publicacao.md`](verificacao_publicacao.md) (commit `3d65056`) |
| Endereço e branch | https://argos-datalab.streamlit.app · `main` |
| Snapshot preliminar do modo demo | **`v1.1-demo-preliminar`**, coletado em 25/10/2026: 148 ativos, de 01/12/2020 a 23/10/2026; impressão SHA-256 do manifesto `56f2822f28f3d155…`. Gerado pela versão de `scripts/gerar_dados_demo.py` registrada no commit `60ce73b` (`--catalog --start 2020-12-01`). Dados em `data/demo/`, fora do Git. Descrição em [`demonstracao.md`](demonstracao.md), seção 2.3.2 |
| Pacote anterior do modo demo | `v1.0-demo`, coletado em 10/10/2026 (5 ativos), guardado em `data/demo_2026-10-10/`, fora do Git |
| Testes no momento do registro | 908 testes passando; cobertura de `core/` em 100% |
