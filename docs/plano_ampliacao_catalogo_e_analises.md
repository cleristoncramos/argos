# Plano de ampliação do catálogo e de novas análises

**Status:** proposta para discussão com o orientador · **Elaborado em:** 24/10/2026 · **Referência externa analisada:** Investidor10 (investidor10.com.br), consulta em 24/10/2026

Este plano responde a três perguntas: (1) o que plataformas de mercado, como o Investidor10, oferecem em análise de séries históricas; (2) se o catálogo do Argos deve crescer, inclusive com criptomoedas recentes; e (3) quais novas análises cabem no objetivo do projeto. Nada aqui altera o sistema por enquanto: cada item depende de aprovação.

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

O ranking de maiores altas em 30 dias do Investidor10 mostrava, em 24/10/2026, o token **DHN (Dohrnii) com +14.067%**. No Yahoo Finance, o fechamento mensal do DHN ficou entre US$ 3 e US$ 6 de outubro/2025 a setembro/2026 e saltou para **US$ 479,63 em outubro/2026**, cerca de 145 vezes em um mês. Esse padrão é típico de token com **baixa liquidez e oferta concentrada**, e não de crescimento sustentado.

**Riscos de incluir criptomoedas pelo desempenho recente:**

1. **Viés de seleção e de sobrevivência.** Escolher ativos *porque* subiram ensina a conclusão errada: que altas passadas indicam altas futuras. Os textos do Argos combatem exatamente essa leitura.
2. **Histórico curto.** Por exemplo, HYPE tem cerca de 2 anos de dados (694 observações). Sazonalidade, janelas móveis e volatilidade mensal ficam pouco confiáveis.
3. **Qualidade dos dados.** Saltos de 100 vezes podem combinar movimento real, baixa negociação e falhas da fonte. O Argos hoje não sinaliza isso.
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
| ETFs de ações (+6) | BOVA11, SMAL11, IVVB11, DIVO11, GOLD11, HASH11 | 2008 a 2021 | ETFs da B3 em reais: Ibovespa, small caps, S&P 500, dividendos, ouro e cesta de criptoativos |
| Ações EUA (+2) | a definir (ex.: um nome de saúde e um de consumo) | — | Opcional, para equilibrar setores |

**Reserva** (atendem aos critérios e podem substituir alguma inclusão): **SUI20947-USD** (dados desde mai/2023) e **APT21794-USD** (desde out/2022).

**Ficam fora desta rodada:**

- **HYPE:** cerca de 2 anos de histórico.
- **TON:** TON11419-USD retorna só uma observação e TON-USD é outra série. O ticker precisa de verificação.
- **PEPE e SHIB:** moedas de meme, sem uso distinto; a categoria já é representada pelo DOGE.
- **CPLE6:** sem dados no Yahoo.
- **VGHF11:** cerca de 2,7 anos de histórico.

**Grupo novo opcional, "Criptomoedas recentes":** só se o orientador aprovar. Ficaria com um aviso fixo de histórico curto e sem entrar nas análises que exigem muitos anos (sazonalidade e janelas longas).

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
