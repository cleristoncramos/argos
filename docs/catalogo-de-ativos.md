# 📚 Catálogo de Ativos — Argos DataLab

> Catálogo dos ativos financeiros disponibilizados pelo **Argos DataLab** para consulta, análise exploratória, comparação de desempenho, indicadores técnicos e métricas de risco.

---

## 1. Visão geral

O **Argos DataLab** mantém um catálogo centralizado de ativos para padronizar a seleção, a organização e a identificação dos instrumentos usados pela aplicação.

O catálogo é implementado em:

```text
core/assets.py
```

Cada registro separa: classe, subclasse, mercado, ticker, nome de exibição, descrição, grupo de interface, tipo de dado, ícone e cor de categoria.

O catálogo contém **120 ativos**, distribuídos em **13 grupos**.

> [!IMPORTANT]
> O catálogo é uma estrutura de **metadados editoriais** para seleção e organização da interface. A existência de um ticker no catálogo **não garante** que o Yahoo Finance disponibilize a mesma profundidade de histórico para todos os ativos.

> [!NOTE]
> **Terminologia.** Na interface, os 13 grupos aparecem no campo "Classe do Ativo". No código, porém, o campo `class` possui 9 valores (Criptomoeda, Ação, ETF, REIT, FII, Índice, Forex, Commodity e Renda Fixa), e os 13 valores do campo `group` organizam o menu. Neste documento, **grupo** se refere aos 13 itens do menu e **classe** aos 9 valores técnicos.

---

## 2. Natureza e critério de seleção

A seleção de ativos adotada no Argos DataLab possui natureza intencional e não probabilística. O catálogo inicial é composto por 120 instrumentos financeiros organizados em 13 classes, incluindo criptomoedas, ações brasileiras e internacionais, ETFs, FIIs, REITs, índices, pares cambiais, commodities e taxas de juros. A escolha considerou critérios combinados de representatividade por classe, diversidade geográfica, cobertura setorial, relevância econômica, liquidez ou notoriedade, disponibilidade de séries históricas, compatibilidade com os tickers utilizados pelo Yahoo Finance e valor educacional para a análise de risco, retorno, correlação e sazonalidade.

A inclusão de um ativo no catálogo não representa recomendação de investimento, ranking de qualidade, indicação de compra ou venda, nem avaliação de adequação ao perfil do investidor. O catálogo funciona como uma amostra operacional para demonstração, análise exploratória e pesquisa aplicada. A disponibilidade e a profundidade dos dados podem variar conforme o ativo e a fonte externa utilizada.

**Decisões de escopo (reunião de orientação de 06/10/2026):**

- Os 13 grupos são mantidos na primeira versão.
- O catálogo é uma **amostra inicial**, não o universo do mercado.
- A seleção hierárquica é o fluxo principal para usuários iniciantes. A digitação livre de ticker existe como modo alternativo (ver seção 27).

---

## 3. Objetivos do catálogo

1. Centralizar os ativos disponíveis na aplicação.
2. Evitar a duplicação de definições de ativos entre módulos.
3. Padronizar nomes, classes, subclasses e mercados.
4. Facilitar a construção dos menus da interface.
5. Permitir filtros por diferentes dimensões.
6. Fornecer a lista de tickers para consulta no `yfinance`.
7. Permitir uma hierarquia navegável.
8. Facilitar a manutenção e a expansão futura.
9. Garantir a validação estrutural do catálogo.
10. Manter uma referência documental dos ativos suportados.

---

## 4. Quantidade de ativos

| Indicador                        | Quantidade |
| -------------------------------- | ---------: |
| **Total de ativos**              |    **120** |
| Grupos (menu da interface)       |     **13** |
| Classes técnicas (campo `class`) |      **9** |
| Registros com ticker único       |    **120** |
| Campos obrigatórios por ativo    |     **10** |

A quantidade total é validada pelo código:

```python
if len(ASSETS) != 120:
    raise ValueError(...)
```

> [!NOTE]
> Como o valor 120 está fixo na validação, qualquer inclusão ou remoção exige atualizá-lo (ver seção 32). Os números exibidos na página "Sobre o Projeto" também devem acompanhar essa mudança (ver seção 38).

---

## 5. Estrutura hierárquica

```text
Classe
└── Subclasse
    └── Mercado
        └── Ativos
```

Exemplo:

```text
Ação
└── Tecnologia
    └── EUA
        ├── Apple
        ├── Microsoft
        ├── Alphabet
        └── Meta Platforms
```

A hierarquia é gerada por `get_hierarchy()`.

---

## 6. Classes de ativos

| Classe      | Ícone | Tipo de dado |
| ----------- | ----- | ------------ |
| Criptomoeda | ₿     | `crypto`     |
| Ação        | 📈    | `stock`      |
| ETF         | 📊    | `etf`        |
| REIT        | 🏢    | `reit`       |
| FII         | 🏠    | `fii`        |
| Índice      | 📐    | `index`      |
| Forex       | 💱    | `forex`      |
| Commodity   | 🛢️   | `future`     |
| Renda Fixa  | 💵    | `bond_yield` |

---

## 7. Grupos do catálogo

A ordem é mantida no código para garantir estabilidade do menu.

| Ordem | Chave               | Grupo                          | Classe      |
| ----: | ------------------- | ------------------------------ | ----------- |
|     1 | `crypto`            | ₿ Criptomoedas                 | Criptomoeda |
|     2 | `br_stocks`         | 🇧🇷 Ações Brasil              | Ação        |
|     3 | `us_stocks`         | 🇺🇸 Ações EUA                 | Ação        |
|     4 | `europe_stocks`     | 🇪🇺 Ações Europa              | Ação        |
|     5 | `asia_stocks`       | 🌏 Ações Ásia                  | Ação        |
|     6 | `equity_etfs`       | 📈 ETFs de ações               | ETF         |
|     7 | `fixed_income_etfs` | 💵 ETFs de renda fixa          | ETF         |
|     8 | `reits`             | 🏢 REITs / Mercado imobiliário | REIT        |
|     9 | `brazil_fiis`       | 🏠 FIIs Brasil                 | FII         |
|    10 | `indexes`           | 📊 Índices de mercado          | Índice      |
|    11 | `forex`             | 💱 Forex                       | Forex       |
|    12 | `commodities`       | 🛢️ Commodities                | Commodity   |
|    13 | `treasury`          | 💵 Treasury / taxas de juros   | Renda Fixa  |

---

## 8. Campos dos registros

| Campo            | Descrição                                              |
| ---------------- | ------------------------------------------------------ |
| `ticker`         | Símbolo usado para identificação/consulta do ativo     |
| `name`           | Nome de exibição                                       |
| `class`          | Classe principal                                       |
| `subcategory`    | Subclasse ou segmento                                  |
| `market`         | Mercado, país ou região associado                      |
| `description`    | Descrição resumida                                     |
| `group`          | Grupo usado na organização do menu                     |
| `icon`           | Ícone visual associado à classe                        |
| `category_color` | Cor visual associada à classe                          |
| `data_type`      | Tipo técnico usado pela aplicação                      |

---

## 9. ₿ Criptomoedas

**Total: 10 ativos**

|  # | Ticker     | Nome      | Subclasse           | Mercado | Descrição                                             |
| -: | ---------- | --------- | ------------------- | ------- | ----------------------------------------------------- |
|  1 | `BTC-USD`  | Bitcoin   | Cripto principal    | Global  | Principal criptomoeda por capitalização               |
|  2 | `ETH-USD`  | Ethereum  | Smart contracts     | Global  | Principal plataforma de contratos inteligentes        |
|  3 | `BNB-USD`  | BNB       | Exchange/Blockchain | Global  | Token associado ao ecossistema BNB                    |
|  4 | `SOL-USD`  | Solana    | Smart contracts     | Global  | Blockchain de alta capacidade                         |
|  5 | `XRP-USD`  | XRP       | Pagamentos          | Global  | Ativo voltado a pagamentos e liquidação               |
|  6 | `ADA-USD`  | Cardano   | Smart contracts     | Global  | Blockchain de contratos inteligentes                  |
|  7 | `DOGE-USD` | Dogecoin  | Meme coin           | Global  | Criptomoeda originada como meme                       |
|  8 | `AVAX-USD` | Avalanche | Smart contracts     | Global  | Plataforma blockchain                                 |
|  9 | `TRX-USD`  | TRON      | Blockchain          | Global  | Rede blockchain focada em aplicações descentralizadas |
| 10 | `LINK-USD` | Chainlink | Oracle              | Global  | Rede de oráculos para aplicações blockchain           |

---

## 10. 🇧🇷 Ações Brasil

**Total: 12 ativos**

|  # | Ticker     | Nome                             | Subclasse                 | Mercado   | Descrição                          |
| -: | ---------- | -------------------------------- | ------------------------- | --------- | ---------------------------------- |
| 11 | `PETR4.SA` | Petrobras PN                     | Energia                   | Brasil/B3 | Petróleo e gás                     |
| 12 | `VALE3.SA` | Vale                             | Mineração                 | Brasil/B3 | Mineração e metais                 |
| 13 | `ITUB4.SA` | Itaú Unibanco PN                 | Bancos                    | Brasil/B3 | Banco privado                      |
| 14 | `BBAS3.SA` | Banco do Brasil                  | Bancos                    | Brasil/B3 | Banco de controle estatal          |
| 15 | `BBDC4.SA` | Bradesco PN                      | Bancos                    | Brasil/B3 | Banco privado                      |
| 16 | `ITSA4.SA` | Itaúsa                           | Holding financeira        | Brasil/B3 | Holding de participações           |
| 17 | `WEGE3.SA` | WEG                              | Indústria                 | Brasil/B3 | Equipamentos elétricos e automação |
| 18 | `ABEV3.SA` | Ambev                            | Consumo                   | Brasil/B3 | Bebidas                            |
| 19 | `B3SA3.SA` | B3                               | Infraestrutura financeira | Brasil/B3 | Bolsa e infraestrutura de mercado  |
| 20 | `RENT3.SA` | Localiza                         | Serviços                  | Brasil/B3 | Locação de veículos                |
| 21 | `AXIA3.SA` | Axia Energia (Antiga Eletrobras) | Energia elétrica          | Brasil/B3 | Geração e transmissão de energia   |
| 22 | `SUZB3.SA` | Suzano                           | Papel e celulose          | Brasil/B3 | Celulose e papel                   |

> [!NOTE]
> O catálogo usa `AXIA3.SA` para a **Axia Energia (Antiga Eletrobras)**. Esse registro é a referência do projeto para essa posição.

---

## 11. 🇺🇸 Ações EUA

**Total: 15 ativos**

|  # | Ticker  | Nome               | Subclasse         | Mercado | Descrição                                   |
| -: | ------- | ------------------ | ----------------- | ------- | ------------------------------------------- |
| 23 | `AAPL`  | Apple              | Tecnologia        | EUA     | Eletrônicos e serviços                      |
| 24 | `MSFT`  | Microsoft          | Tecnologia        | EUA     | Software e computação em nuvem              |
| 25 | `NVDA`  | Nvidia             | Semicondutores    | EUA     | Chips e computação para IA                  |
| 26 | `AMZN`  | Amazon             | Tecnologia/Varejo | EUA     | E-commerce e cloud                          |
| 27 | `GOOGL` | Alphabet           | Tecnologia        | EUA     | Google, publicidade e cloud                 |
| 28 | `META`  | Meta Platforms     | Tecnologia        | EUA     | Redes sociais e publicidade digital         |
| 29 | `TSLA`  | Tesla              | Automóveis        | EUA     | Veículos elétricos e energia                |
| 30 | `AVGO`  | Broadcom           | Semicondutores    | EUA     | Semicondutores e infraestrutura tecnológica |
| 31 | `BRK-B` | Berkshire Hathaway | Holding           | EUA     | Conglomerado de investimentos               |
| 32 | `JPM`   | JPMorgan Chase     | Bancos            | EUA     | Serviços financeiros                        |
| 33 | `V`     | Visa               | Pagamentos        | EUA     | Rede global de pagamentos                   |
| 34 | `MA`    | Mastercard         | Pagamentos        | EUA     | Rede global de pagamentos                   |
| 35 | `LLY`   | Eli Lilly          | Farmacêutica      | EUA     | Medicamentos                                |
| 36 | `WMT`   | Walmart            | Varejo            | EUA     | Varejo e supermercados                      |
| 37 | `XOM`   | Exxon Mobil        | Energia           | EUA     | Petróleo e gás                              |

---

## 12. 🇪🇺 Ações Europa

**Total: 8 ativos**

|  # | Ticker      | Nome         | Subclasse      | Mercado     | Descrição                             |
| -: | ----------- | ------------ | -------------- | ----------- | ------------------------------------- |
| 38 | `ASML`      | ASML Holding | Semicondutores | Holanda     | Equipamentos para fabricação de chips |
| 39 | `SAP`       | SAP          | Software       | Alemanha    | Software empresarial                  |
| 40 | `NESN.SW`   | Nestlé       | Consumo        | Suíça       | Alimentos e bebidas                   |
| 41 | `MC.PA`     | LVMH         | Luxo           | França      | Bens de luxo                          |
| 42 | `SHEL`      | Shell        | Energia        | Reino Unido | Petróleo e gás                        |
| 43 | `NOVO-B.CO` | Novo Nordisk | Farmacêutica   | Dinamarca   | Produtos farmacêuticos                |
| 44 | `SIE.DE`    | Siemens      | Indústria      | Alemanha    | Automação e tecnologia industrial     |
| 45 | `AIR.PA`    | Airbus       | Aeroespacial   | França      | Aviação e defesa                      |

> [!NOTE]
> A coluna **Mercado** indica o país de origem da empresa. Tickers sem sufixo de bolsa (`ASML`, `SAP`, `SHEL`) correspondem, em geral, a listagens nos EUA, e não à bolsa do país de origem. Ver seção 24.

---

## 13. 🌏 Ações Ásia

**Total: 8 ativos**

|  # | Ticker      | Nome                 | Subclasse                  | Mercado        | Descrição                           |
| -: | ----------- | -------------------- | -------------------------- | -------------- | ----------------------------------- |
| 46 | `TSM`       | Taiwan Semiconductor | Semicondutores             | Taiwan/EUA ADR | Fabricação de chips                 |
| 47 | `BABA`      | Alibaba              | Tecnologia/E-commerce      | China/EUA ADR  | E-commerce e cloud                  |
| 48 | `SONY`      | Sony                 | Eletrônicos/Entretenimento | Japão          | Eletrônicos e entretenimento        |
| 49 | `005930.KS` | Samsung Electronics  | Tecnologia                 | Coreia do Sul  | Eletrônicos e semicondutores        |
| 50 | `0700.HK`   | Tencent              | Tecnologia                 | Hong Kong      | Internet, games e serviços digitais |
| 51 | `7203.T`    | Toyota               | Automóveis                 | Japão          | Automóveis                          |
| 52 | `000660.KS` | SK Hynix             | Semicondutores             | Coreia do Sul  | Memórias e semicondutores           |
| 53 | `9988.HK`   | Alibaba Group        | Tecnologia/E-commerce      | Hong Kong      | E-commerce e tecnologia             |

> [!NOTE]
> `BABA` e `9988.HK` são duas listagens da mesma empresa e são tratadas como **tickers distintos**. Em comparações entre elas, espera-se correlação muito alta, o que reflete a duplicidade de listagem e não diversificação.

---

## 14. 📈 ETFs de ações

**Total: 10 ativos**

|  # | Ticker | Nome                              | Subclasse     | Mercado    | Descrição                                  |
| -: | ------ | --------------------------------- | ------------- | ---------- | ------------------------------------------ |
| 54 | `SPY`  | SPDR S&P 500 ETF                  | Large Cap EUA | EUA        | Replica o S&P 500                          |
| 55 | `QQQ`  | Invesco QQQ                       | Nasdaq-100    | EUA        | Grandes empresas não financeiras do Nasdaq |
| 56 | `VTI`  | Vanguard Total Stock Market       | Mercado EUA   | EUA        | Mercado acionário americano amplo          |
| 57 | `VT`   | Vanguard Total World Stock        | Global        | Global     | Ações de mercados mundiais                 |
| 58 | `EEM`  | iShares MSCI Emerging Markets     | Emergentes    | Global     | Mercados emergentes                        |
| 59 | `EWZ`  | iShares MSCI Brazil               | Brasil        | EUA/Brasil | Ações brasileiras                          |
| 60 | `IWM`  | iShares Russell 2000              | Small Caps    | EUA        | Pequenas empresas americanas               |
| 61 | `DIA`  | SPDR Dow Jones Industrial Average | Large Cap     | EUA        | Replica o Dow Jones                        |
| 62 | `VEA`  | Vanguard FTSE Developed Markets   | Internacional | Global     | Mercados desenvolvidos fora dos EUA        |
| 63 | `VOO`  | Vanguard S&P 500                  | Large Cap EUA | EUA        | Replica o S&P 500                          |

> [!NOTE]
> `SPY` e `VOO` replicam o mesmo índice (S&P 500), e `VOO` e `VTI` têm forte sobreposição. Comparações entre eles mostram correlação próxima de 1 por construção.

---

## 15. 💵 ETFs de renda fixa

**Total: 6 ativos**

|  # | Ticker | Nome                             | Subclasse      | Mercado | Descrição                           |
| -: | ------ | -------------------------------- | -------------- | ------- | ----------------------------------- |
| 64 | `BND`  | Vanguard Total Bond Market       | Bonds EUA      | EUA     | Mercado amplo de títulos americanos |
| 65 | `AGG`  | iShares Core U.S. Aggregate Bond | Bonds EUA      | EUA     | Renda fixa americana ampla          |
| 66 | `TLT`  | iShares 20+ Year Treasury Bond   | Treasury longo | EUA     | Treasuries de longo prazo           |
| 67 | `IEF`  | iShares 7-10 Year Treasury Bond  | Treasury médio | EUA     | Treasuries de prazo intermediário   |
| 68 | `SHY`  | iShares 1-3 Year Treasury Bond   | Treasury curto | EUA     | Treasuries de curto prazo           |
| 69 | `TIP`  | iShares TIPS Bond                | Inflação       | EUA     | Títulos protegidos contra inflação  |

---

## 16. 🏢 REITs / Mercado imobiliário

**Total: 5 ativos**

|  # | Ticker | Nome                     | Subclasse        | Mercado | Descrição                       |
| -: | ------ | ------------------------ | ---------------- | ------- | ------------------------------- |
| 70 | `VNQ`  | Vanguard Real Estate ETF | Imobiliário      | EUA     | Carteira diversificada de REITs |
| 71 | `O`    | Realty Income            | Imobiliário      | EUA     | Imóveis comerciais              |
| 72 | `PLD`  | Prologis                 | Logística        | EUA     | Galpões e imóveis logísticos    |
| 73 | `AMT`  | American Tower           | Infraestrutura   | EUA     | Torres de telecomunicações      |
| 74 | `SPG`  | Simon Property Group     | Shopping centers | EUA     | Centros comerciais              |

> [!NOTE]
> `VNQ` é um ETF, mas está classificado deliberadamente na classe `REIT`, no grupo `reits`, para representar o segmento imobiliário.

---

## 17. 🏠 FIIs Brasil

**Total: 5 ativos**

|  # | Ticker      | Nome                    | Subclasse | Mercado   | Descrição                        |
| -: | ----------- | ----------------------- | --------- | --------- | -------------------------------- |
| 75 | `MXRF11.SA` | Maxi Renda              | Papel     | Brasil/B3 | Fundo imobiliário de recebíveis  |
| 76 | `HGLG11.SA` | Pátria Log              | Logística | Brasil/B3 | Imóveis logísticos               |
| 77 | `KNRI11.SA` | Kinea Renda Imobiliária | Híbrido   | Brasil/B3 | Escritórios e imóveis logísticos |
| 78 | `XPML11.SA` | XP Malls                | Shopping  | Brasil/B3 | Shopping centers                 |
| 79 | `BTLG11.SA` | BTG Logística           | Logística | Brasil/B3 | Galpões logísticos               |

---

## 18. 📊 Índices de mercado

**Total: 12 ativos**

|  # | Ticker      | Nome                  | Subclasse          | Mercado     | Descrição                              |
| -: | ----------- | --------------------- | ------------------ | ----------- | -------------------------------------- |
| 80 | `^BVSP`     | Ibovespa              | Ações              | Brasil      | Principal índice da B3                 |
| 81 | `^GSPC`     | S&P 500               | Large Cap          | EUA         | 500 grandes empresas americanas        |
| 82 | `^IXIC`     | Nasdaq Composite      | Tecnologia/Mercado | EUA         | Empresas listadas no Nasdaq            |
| 83 | `^DJI`      | Dow Jones             | Large Cap          | EUA         | 30 grandes empresas americanas         |
| 84 | `^RUT`      | Russell 2000          | Small Caps         | EUA         | Pequenas empresas americanas           |
| 85 | `^VIX`      | CBOE Volatility Index | Volatilidade       | EUA         | Expectativa de volatilidade do S&P 500 |
| 86 | `^FTSE`     | FTSE 100              | Large Cap          | Reino Unido | Principais empresas britânicas         |
| 87 | `^GDAXI`    | DAX                   | Large Cap          | Alemanha    | Principais empresas alemãs             |
| 88 | `^FCHI`     | CAC 40                | Large Cap          | França      | Principais empresas francesas          |
| 89 | `^N225`     | Nikkei 225            | Large Cap          | Japão       | Principais empresas japonesas          |
| 90 | `^HSI`      | Hang Seng             | Large Cap          | Hong Kong   | Principais empresas de Hong Kong       |
| 91 | `000001.SS` | Shanghai Composite    | Mercado amplo      | China       | Mercado acionário de Xangai            |

> [!NOTE]
> Índices não são negociáveis diretamente. Seus valores são expressos em **pontos**, e `^VIX` mede volatilidade esperada, não o preço de um ativo. Ver seção 24.

---

## 19. 💱 Forex

**Total: 8 ativos**

|  # | Ticker     | Nome    | Subclasse | Mercado | Descrição                      |
| -: | ---------- | ------- | --------- | ------- | ------------------------------ |
| 92 | `USDBRL=X` | USD/BRL | Major/EM  | Global  | Dólar americano contra real    |
| 93 | `EURUSD=X` | EUR/USD | Major     | Global  | Euro contra dólar              |
| 94 | `GBPUSD=X` | GBP/USD | Major     | Global  | Libra contra dólar             |
| 95 | `USDJPY=X` | USD/JPY | Major     | Global  | Dólar contra iene              |
| 96 | `USDCHF=X` | USD/CHF | Major     | Global  | Dólar contra franco suíço      |
| 97 | `AUDUSD=X` | AUD/USD | Major     | Global  | Dólar australiano contra dólar |
| 98 | `USDCAD=X` | USD/CAD | Major     | Global  | Dólar contra dólar canadense   |
| 99 | `USDCNY=X` | USD/CNY | China     | Global  | Dólar contra yuan              |

---

## 20. 🛢️ Commodities

**Total: 14 ativos**

### 20.1 Metais

|   # | Ticker | Nome    | Mercado   | Descrição                  |
| --: | ------ | ------- | --------- | -------------------------- |
| 100 | `GC=F` | Ouro    | EUA/COMEX | Contrato futuro de ouro    |
| 101 | `SI=F` | Prata   | EUA/COMEX | Contrato futuro de prata   |
| 102 | `HG=F` | Cobre   | EUA/COMEX | Contrato futuro de cobre   |
| 103 | `PL=F` | Platina | EUA/NYMEX | Contrato futuro de platina |

### 20.2 Energia

|   # | Ticker | Nome           | Mercado    | Descrição      |
| --: | ------ | -------------- | ---------- | -------------- |
| 104 | `CL=F` | Petróleo WTI   | EUA/NYMEX  | Petróleo WTI   |
| 105 | `BZ=F` | Petróleo Brent | Global/ICE | Petróleo Brent |
| 106 | `NG=F` | Gás Natural    | EUA/NYMEX  | Gás natural    |

### 20.3 Agrícolas

|   # | Ticker | Nome    | Mercado  | Descrição |
| --: | ------ | ------- | -------- | --------- |
| 107 | `ZS=F` | Soja    | EUA/CBOT | Soja      |
| 108 | `ZC=F` | Milho   | EUA/CBOT | Milho     |
| 109 | `ZW=F` | Trigo   | EUA/CBOT | Trigo     |
| 110 | `KC=F` | Café    | EUA/ICE  | Café      |
| 111 | `CC=F` | Cacau   | EUA/ICE  | Cacau     |
| 112 | `SB=F` | Açúcar  | EUA/ICE  | Açúcar    |
| 113 | `CT=F` | Algodão | EUA/ICE  | Algodão   |

> [!NOTE]
> Os ativos desta classe usam `data_type = "future"`: os registros representam **contratos futuros**, não o preço à vista da mercadoria. Ver seção 24.

---

## 21. 💵 Treasury / taxas de juros

**Total: 7 ativos**

Este grupo combina **indicadores de rendimento (yield)** e **ETFs de Treasuries**, que são tipos de série diferentes.

### 21.1 Indicadores de yield

|   # | Ticker | Nome                | Subclasse   | Mercado | Descrição                       |
| --: | ------ | ------------------- | ----------- | ------- | ------------------------------- |
| 114 | `^IRX` | Treasury 13 Semanas | Curto prazo | EUA     | Yield de Treasury de 13 semanas |
| 115 | `^FVX` | Treasury 5 Anos     | Médio prazo | EUA     | Yield de Treasury de 5 anos     |
| 116 | `^TNX` | Treasury 10 Anos    | Longo prazo | EUA     | Yield de Treasury de 10 anos    |
| 117 | `^TYX` | Treasury 30 Anos    | Longo prazo | EUA     | Yield de Treasury de 30 anos    |

### 21.2 ETFs de Treasuries

|   # | Ticker | Nome                     | Subclasse         | Mercado | Descrição                       |
| --: | ------ | ------------------------ | ----------------- | ------- | ------------------------------- |
| 118 | `BIL`  | Treasury 1-3 Meses (BIL) | Curto prazo       | EUA     | ETF de T-Bills de 1 a 3 meses   |
| 119 | `SHV`  | Treasury < 1 Ano (SHV)   | Curto prazo       | EUA     | ETF de Treasuries de até 1 ano  |
| 120 | `VGSH` | Treasury 1-3 Anos (VGSH) | Curto/médio prazo | EUA     | ETF de Treasuries de 1 a 3 anos |

> [!IMPORTANT]
> `^IRX`, `^FVX`, `^TNX` e `^TYX` são **taxas** (nível de rendimento), e não preços de um título. `BIL`, `SHV` e `VGSH` são **ETFs negociados**, com preço em US$. Ver seção 24 para as implicações nas métricas.

---

## 22. Resumo quantitativo

| Grupo                          | Quantidade |
| ------------------------------ | ---------: |
| ₿ Criptomoedas                 |         10 |
| 🇧🇷 Ações Brasil              |         12 |
| 🇺🇸 Ações EUA                 |         15 |
| 🇪🇺 Ações Europa              |          8 |
| 🌏 Ações Ásia                  |          8 |
| 📈 ETFs de ações               |         10 |
| 💵 ETFs de renda fixa          |          6 |
| 🏢 REITs / Mercado imobiliário |          5 |
| 🏠 FIIs Brasil                 |          5 |
| 📊 Índices de mercado          |         12 |
| 💱 Forex                       |          8 |
| 🛢️ Commodities                |         14 |
| 💵 Treasury / taxas de juros   |          7 |
| **TOTAL**                      |    **120** |

---

## 23. Classes técnicas e `data_type`

| Classe      | Grupos associados                | `data_type`  |
| ----------- | -------------------------------- | ------------ |
| Criptomoeda | Criptomoedas                     | `crypto`     |
| Ação        | Ações Brasil, EUA, Europa e Ásia | `stock`      |
| ETF         | ETFs de ações e renda fixa       | `etf`        |
| REIT        | REITs / Mercado imobiliário      | `reit`       |
| FII         | FIIs Brasil                      | `fii`        |
| Índice      | Índices de mercado               | `index`      |
| Forex       | Forex                            | `forex`      |
| Commodity   | Commodities                      | `future`     |
| Renda Fixa  | Treasury / taxas de juros        | `bond_yield` |

O campo `data_type` identifica tecnicamente a natureza do ativo (exemplos: `crypto` → `BTC-USD`; `stock` → `PETR4.SA`; `etf` → `SPY`; `reit` → `O`; `fii` → `MXRF11.SA`; `index` → `^BVSP`; `forex` → `USDBRL=X`; `future` → `GC=F`; `bond_yield` → `^TNX`, `BIL`).

---

## 24. Particularidades por tipo de ativo

Estas particularidades afetam a **interpretação** das métricas e devem ser consideradas ao comparar ativos de tipos diferentes.

### 24.1 Moeda de cotação

| Sufixo / padrão                 | Moeda ou unidade típica       |
| ------------------------------- | ----------------------------- |
| `.SA`                           | Real (R$)                     |
| Sem sufixo (EUA, ADRs)          | Dólar (US$)                   |
| `.SW`                           | Franco suíço                  |
| `.PA`, `.DE`                    | Euro                          |
| `.CO`                           | Coroa dinamarquesa            |
| `.KS`                           | Won sul-coreano               |
| `.HK`                           | Dólar de Hong Kong            |
| `.T`                            | Iene                          |
| `-USD` (cripto)                 | Dólar (US$)                   |
| `=F` (futuros)                  | Dólar (US$)                   |
| `=X` (câmbio)                   | Taxa de câmbio (sem moeda)    |
| `^...` e `.SS` (índices)        | Pontos                        |

> [!WARNING]
> Os valores de ativos de moedas diferentes **não são diretamente comparáveis em nível**. A comparação em **Base 100** e os retornos percentuais contornam isso, mas **não** incorporam variação cambial.

### 24.2 Tickers sem sufixo da Europa e da Ásia

`ASML`, `SAP`, `SHEL`, `SONY`, `TSM` e `BABA` correspondem, em geral, a listagens nos EUA (ADRs ou ações listadas), cotadas em dólar, embora a coluna **Mercado** indique o país de origem. A convenção de listagem é definida pela fonte (Yahoo Finance) e deve ser verificada ao adicionar novos ativos.

### 24.3 Contratos futuros (commodities)

Os registros de commodities são **contratos futuros** (`=F`), não preços à vista. Séries longas de futuros dependem de como a fonte encadeia contratos sucessivos, e a troca de vencimento pode introduzir saltos que não correspondem a retorno real.

### 24.4 Taxas de juros (yields)

`^IRX`, `^FVX`, `^TNX` e `^TYX` são **níveis de taxa**, normalmente expressos em pontos percentuais. Calcular "retorno" sobre uma taxa mede a variação do nível da taxa, e **não** o retorno de um título. Assim, métricas como retorno total, Sharpe e drawdown têm interpretação diferente para esses ativos e para os ETFs de Treasury (`BIL`, `SHV`, `VGSH`), que são preços.

### 24.5 Índice de volatilidade

`^VIX` mede a volatilidade esperada do S&P 500. Não é um ativo negociável diretamente, e retornos calculados sobre ele descrevem a variação do indicador.

### 24.6 Calendário de negociação

Criptomoedas negociam todos os dias. Ações, ETFs e índices seguem calendários de bolsa (cerca de 252 dias por ano). Por isso, o número de observações diárias de um mesmo período difere entre classes.

### 24.7 Volume

Nem todos os tipos de ativo possuem volume confiável (por exemplo, índices e câmbio). Os gráficos de volume dependem dessa disponibilidade na fonte.

---

## 25. Disponibilidade e período dos dados

O catálogo define **o que a aplicação oferece**; a fonte define **quais dados existem**. Para deixar essa diferença explícita ao usuário, as páginas de análise exibem:

- **Período solicitado** × **período disponível** (primeira e última observação efetivamente recebidas);
- quantidade de **observações diárias** e **no período agregado** pela frequência escolhida;
- **fonte** (Yahoo Finance via `yfinance`) e **data/hora da consulta**.

Avisos gerados automaticamente (`core/data_availability.py`):

| Situação                     | Critério                                               | Nível |
| ---------------------------- | ------------------------------------------------------ | ----- |
| Dados insuficientes          | menos de 2 períodos agregados                          | erro  |
| Histórico menor que o pedido | primeiro dado mais de 10 dias depois da data inicial   | aviso |
| Dados terminam antes         | último dado mais de 7 dias antes da data final         | aviso |
| Poucas observações           | menos de 12 períodos agregados                         | info  |

> Selecionar "10 anos" **não garante** dez anos de dados. Ativos recentes (criptomoedas novas, IPOs) e fontes com histórico incompleto podem oferecer períodos menores, e as métricas valem para o período efetivamente disponível.

Falhas temporárias da fonte não ficam em cache: uma nova consulta tenta baixar os dados novamente.

---

## 26. Convenção de anualização

A volatilidade é anualizada de acordo com a frequência dos retornos utilizados no cálculo.

| Frequência dos retornos | Fator de anualização |
| ----------------------- | -------------------- |
| Diária                  | √252                 |
| Semanal                 | √52                  |
| Mensal                  | √12                  |
| Semestral               | √2                   |
| Anual                   | 1                    |

Para retornos diários, utiliza-se convencionalmente o fator √252, correspondente a aproximadamente 252 dias de negociação por ano.

Quando a frequência mensal é selecionada, a volatilidade anualizada é calculada pela multiplicação do desvio-padrão dos retornos mensais por √12. Essa convenção é aplicada independentemente da classe do ativo, pois a série já foi agregada em 12 períodos por ano.

Em análises individuais de criptoativos com dados diários, pode-se adotar futuramente o fator √365, considerando que esses mercados operam continuamente. Na versão comparativa do sistema, a convenção padronizada de √252 pode ser mantida para preservar comparabilidade entre ativos negociados em calendários distintos.

O mesmo fator de anualização é usado no Índice de Sharpe, junto com a taxa livre de risco anual informada pelo usuário.

---

## 27. Ativos fora do catálogo (ticker digitado)

Usuários avançados podem digitar um ticker diretamente na barra lateral, como alternativa ao menu hierárquico.

- O ticker é **normalizado** (maiúsculas, sem espaços) e tem o **formato validado**.
- A existência é confirmada com uma consulta curta à fonte. Se o ticker não existir ou não tiver dados recentes, a aplicação exibe uma mensagem clara e **não** habilita a análise.
- Tickers válidos fora do catálogo **não possuem metadados** (classe, subclasse, descrição, ícone). Nesse caso, a interface usa o ticker como identificação e o ícone padrão.
- A seleção hierárquica continua sendo o **fluxo principal**, indicado para iniciantes.
- O ticker digitado não entra no catálogo, e a validação não equivale a inclusão.

---

## 28. Logos, ícones e cores

Cada ativo é exibido com um logo quando disponível, e **sempre com um ícone (emoji) de reserva**, para que imagens indisponíveis não quebrem a página.

| Grupo                                   | Fonte do logo                          |
| --------------------------------------- | -------------------------------------- |
| Criptomoedas                            | Serviço público de ícones por símbolo  |
| Ações, ETFs, REITs e FIIs               | Serviço público de logos por ticker    |
| Índices, Forex, Commodities e Treasury  | Sem logo: usa o ícone da classe        |

> Os logos vêm de serviços de terceiros e podem estar indisponíveis ou desatualizados para alguns tickers. Nesses casos, o ícone de reserva é exibido. A lógica está em `core/asset_logos.py`.

Ícones e cores por classe (metadados de interface, sem significado financeiro):

| Classe      | Ícone | Cor       |
| ----------- | ----- | --------- |
| Criptomoeda | ₿     | `#F59E0B` |
| Ação        | 📈    | `#2563EB` |
| ETF         | 📊    | `#7C3AED` |
| REIT        | 🏢    | `#0F766E` |
| FII         | 🏠    | `#0891B2` |
| Índice      | 📐    | `#475569` |
| Forex       | 💱    | `#16A34A` |
| Commodity   | 🛢️   | `#B45309` |
| Renda Fixa  | 💵    | `#0E7490` |

Os valores são definidos em `CATEGORY_METADATA` e aplicados pela função `_asset()`.

---

## 29. Identificação e consulta

Cada registro possui um `ticker` único. O índice interno `ASSET_BY_TICKER` permite localizar os metadados a partir do ticker.

| Função            | Finalidade                                                                  |
| ----------------- | --------------------------------------------------------------------------- |
| `get_asset(t)`    | Retorna os metadados de um ativo                                            |
| `get_assets(...)` | Filtra por classe, subclasse, mercado, tipo de dado e grupo                 |
| `get_tickers()`   | Lista os tickers para consulta de dados                                     |
| `get_hierarchy()` | Gera a hierarquia Classe → Subclasse → Mercado → Ativos                     |

Exemplo:

```python
from core.assets import get_asset, get_assets

asset = get_asset("PETR4.SA")
acoes_eua = get_assets(asset_class="Ação", market="EUA")
```

Retorno de `get_asset("PETR4.SA")`:

```python
{
    "ticker": "PETR4.SA",
    "name": "Petrobras PN",
    "class": "Ação",
    "subcategory": "Energia",
    "market": "Brasil/B3",
    "description": "Petróleo e gás",
    "group": "br_stocks",
    "icon": "📈",
    "category_color": "#2563EB",
    "data_type": "stock"
}
```

---

## 30. Integração com o yfinance

O catálogo **não consulta** dados de mercado. Ele fornece metadados e identificadores. A camada de dados (`core/data_loader.py`) usa os tickers para consultar o Yahoo Finance por meio do `yfinance`.

```text
Catálogo  →  define o que a aplicação oferece
yfinance  →  define quais dados estão efetivamente disponíveis
```

Essas duas camadas devem permanecer conceitualmente separadas.

---

## 31. Validação automática

A função `validate_catalog()` verifica:

1. **Quantidade:** exatamente 120 ativos.
2. **Unicidade:** nenhum ticker duplicado (o erro informa os tickers envolvidos).
3. **Campos obrigatórios:** ticker, name, class, subcategory, market, description, group, icon, category_color e data_type.

---

## 32. Regras para inclusão de novos ativos

1. Confirmar o ticker usado pelo Yahoo Finance e verificar se há dados.
2. Definir nome de exibição, classe, subclasse e mercado.
3. Escrever uma descrição curta e objetiva, **sem linguagem de recomendação**.
4. Associar ao grupo correto e ao `data_type` da classe.
5. Evitar duplicidade de ticker.
6. Atualizar a quantidade esperada em `validate_catalog()` (hoje fixa em 120).
7. Atualizar este documento, incluindo as seções 22 e 35.
8. Atualizar `GROUP_MAPPING` em `app/ui/sidebar.py` se for criado um novo grupo.
9. Executar os testes (incluindo `tests/test_catalog_doc.py`).
10. Confirmar que `validate_catalog()` continua funcionando.

Exemplo de inclusão:

```python
_asset(
    "EXEMPLO",
    "Ativo Exemplo",
    "Ação",
    "Tecnologia",
    "EUA",
    "Descrição resumida do ativo",
    "us_stocks",
)
```

`icon`, `category_color` e `data_type` são herdados da classe, salvo quando sobrescritos.

---

## 33. Manutenção e responsabilidades

O catálogo é a **fonte central de verdade** dos ativos disponíveis na interface. Não cadastre o mesmo ticker diretamente em outros módulos; use:

```python
from core.assets import get_assets, get_tickers
```

**O catálogo é responsável por:** identificação, classificação, organização, descrição, agrupamento, metadados visuais, tipo técnico e fornecimento dos tickers.

**O catálogo não é responsável por:** buscar dados históricos, calcular indicadores, retorno, volatilidade, Sharpe ou drawdown, emitir recomendações de investimento ou garantir a disponibilidade dos dados externos.

---

## 34. Relação com as análises

```text
Catálogo → Seleção do ativo → Ticker → Consulta de dados
        → Verificação de disponibilidade → Tratamento
        → Análise (retorno, volatilidade, drawdown, Sharpe,
                   indicadores técnicos, sazonalidade, correlação)
        → Visualização
```

---

## 35. Lista consolidada dos 120 tickers

Lista completa, na ordem do catálogo, usada para auditoria, testes e manutenção.

```text
BTC-USD
ETH-USD
BNB-USD
SOL-USD
XRP-USD
ADA-USD
DOGE-USD
AVAX-USD
TRX-USD
LINK-USD

PETR4.SA
VALE3.SA
ITUB4.SA
BBAS3.SA
BBDC4.SA
ITSA4.SA
WEGE3.SA
ABEV3.SA
B3SA3.SA
RENT3.SA
AXIA3.SA
SUZB3.SA

AAPL
MSFT
NVDA
AMZN
GOOGL
META
TSLA
AVGO
BRK-B
JPM
V
MA
LLY
WMT
XOM

ASML
SAP
NESN.SW
MC.PA
SHEL
NOVO-B.CO
SIE.DE
AIR.PA

TSM
BABA
SONY
005930.KS
0700.HK
7203.T
000660.KS
9988.HK

SPY
QQQ
VTI
VT
EEM
EWZ
IWM
DIA
VEA
VOO

BND
AGG
TLT
IEF
SHY
TIP

VNQ
O
PLD
AMT
SPG

MXRF11.SA
HGLG11.SA
KNRI11.SA
XPML11.SA
BTLG11.SA

^BVSP
^GSPC
^IXIC
^DJI
^RUT
^VIX
^FTSE
^GDAXI
^FCHI
^N225
^HSI
000001.SS

USDBRL=X
EURUSD=X
GBPUSD=X
USDJPY=X
USDCHF=X
AUDUSD=X
USDCAD=X
USDCNY=X

GC=F
SI=F
HG=F
PL=F
CL=F
BZ=F
NG=F
ZS=F
ZC=F
ZW=F
KC=F
CC=F
SB=F
CT=F

^IRX
^FVX
^TNX
^TYX
BIL
SHV
VGSH
```

---

## 36. Checklist de atualização

Antes de fazer commit de uma alteração no catálogo:

```text
[ ] O ticker foi validado e retorna dados?
[ ] Nome, classe, subclasse, mercado e descrição foram preenchidos?
[ ] O grupo e o data_type estão corretos?
[ ] Não existe ticker duplicado?
[ ] A quantidade esperada em validate_catalog() foi atualizada?
[ ] Os números da página "Sobre o Projeto" foram conferidos?
[ ] GROUP_MAPPING cobre todos os grupos?
[ ] As seções 22 e 35 deste documento foram atualizadas?
[ ] Os testes foram executados?
```

---

## 37. Avisos

### 37.1 Aviso metodológico

A presença de um ativo neste catálogo significa apenas que ele foi **selecionado para fazer parte do universo de análise do Argos DataLab**. Isso não significa recomendação de investimento, indicação de compra ou venda, avaliação de qualidade, previsão de valorização, garantia de liquidez ou garantia de disponibilidade permanente dos dados.

### 37.2 Aviso acadêmico

O Argos DataLab é desenvolvido para fins de pesquisa, estudo, ensino, análise exploratória e desenvolvimento tecnológico (PIBITI UFPI 2026–2027). As funcionalidades atuais constituem um **protótipo evolutivo**. O catálogo faz parte da infraestrutura metodológica do projeto e poderá ser atualizado conforme a pesquisa avança.

---

## 38. Controle de consistência e pendências

O código (`core/assets.py`) é a **fonte operacional** do catálogo; este documento é a **fonte documental**. Alterou o catálogo → atualize os testes → atualize este documento → execute a validação → faça o commit.

O teste `tests/test_catalog_doc.py` compara a lista da seção 35 com `ASSETS` e confere se o texto da seção 2 coincide com `core/catalog_notice.py`.

**Pendências de alinhamento entre código e documentação (verificar):**

| # | Item                                                                                                                                              |
| - | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Confirmar que `ANNUALIZATION_FACTORS` em `core/config.py` segue a seção 26 (252, 52, 12, 2, 1).                                                  |
| 2 | A volatilidade mensal da Análise Individual ainda usa √365; deve passar a √252 conforme a seção 26.                                              |
| 3 | O prefixo de moeda da Análise Individual só distingue `.SA`, `=X`, `^`/`.SS` e "demais = US$". Ativos `.SW`, `.PA`, `.DE`, `.CO`, `.KS`, `.HK` e `.T` aparecem com "US$" apesar de cotados em moeda local (seção 24.1). |
| 4 | Séries de yield (`^IRX`, `^FVX`, `^TNX`, `^TYX`) são exibidas com prefixo "Pts", mas são taxas em percentual (seção 24.4).                        |
| 5 | Os números do catálogo na página "Sobre o Projeto" são digitados à mão; devem ser calculados a partir de `ASSETS`.                               |
| 6 | O texto da interface chama os 13 grupos de "classes"; padronizar a terminologia (ver nota na seção 1).                                           |

---

## 39. Status atual

| Item                       | Valor                                          |
| -------------------------- | ---------------------------------------------- |
| **Status**                 | Catálogo definido (amostra inicial intencional) |
| **Total de ativos**        | 120                                            |
| **Grupos**                 | 13                                             |
| **Classes técnicas**       | 9                                              |
| **Fonte de identificação** | Tickers do Yahoo Finance / `yfinance`          |
| **Implementação**          | `core/assets.py`                               |
| **Documentação**           | `docs/catalogo-de-ativos.md`                   |
| **Última revisão**         | 07/10/2026                                     |

```text
120 ATIVOS
     ├── 13 GRUPOS (menu)
     ├── 9 CLASSES (campo class)
     ├── Classe → Subclasse → Mercado → Ticker
     └── yfinance → dados históricos → verificação de disponibilidade → análises
```

**Argos DataLab — Catálogo centralizado de ativos financeiros.**