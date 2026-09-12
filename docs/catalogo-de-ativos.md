# 📚 Catálogo de Ativos — Argos DataLab

> Catálogo oficial dos ativos financeiros disponibilizados pelo **Argos DataLab** para consulta, análise exploratória, comparação de desempenho, indicadores técnicos e métricas de risco.

---

## 1. Visão geral

O **Argos DataLab** mantém um catálogo centralizado de ativos financeiros para garantir uma estrutura padronizada de seleção, organização e identificação dos instrumentos utilizados pela aplicação.

O catálogo é implementado no módulo:

```text
core/assets.py
```

A estrutura foi concebida para separar:

* **classe do ativo**;
* **subclasse**;
* **mercado**;
* **ticker**;
* **nome de exibição**;
* **descrição**;
* **grupo de interface**;
* **tipo de dado**;
* **ícone**;
* **cor de categoria**.

O catálogo atualmente contém **120 ativos**, distribuídos em **13 grupos principais**.

> [!IMPORTANT]
> Este documento descreve o catálogo efetivamente implementado no código-fonte do Argos DataLab.
>
> O catálogo é uma estrutura de **metadados editoriais para seleção e organização da interface**. A existência de um ticker no catálogo não garante que o Yahoo Finance disponibilize a mesma profundidade de histórico, fundamentos, dividendos ou demais informações para todos os tipos de ativos.

---

# 2. Objetivos do catálogo

O catálogo possui os seguintes objetivos:

1. Centralizar os ativos disponíveis na aplicação;
2. Evitar a duplicação de definições de ativos em diferentes módulos;
3. Padronizar nomes, classes, subclasses e mercados;
4. Facilitar a construção dos menus da interface;
5. Permitir filtros por diferentes dimensões;
6. Fornecer uma lista de tickers para consulta no `yfinance`;
7. Permitir a construção de uma hierarquia navegável;
8. Facilitar a manutenção e expansão futura do projeto;
9. Garantir a validação estrutural do catálogo;
10. Manter uma referência documental dos ativos suportados.

---

# 3. Quantidade de ativos

O catálogo possui atualmente:

| Indicador                     | Quantidade |
| ----------------------------- | ---------: |
| **Total de ativos**           |    **120** |
| Grupos principais             |     **13** |
| Classes de ativos             |      **9** |
| Registros com ticker único    |    **120** |
| Campos obrigatórios por ativo |     **11** |

A quantidade total é validada automaticamente pelo código.

```python
if len(ASSETS) != 120:
    raise ValueError(...)
```

Caso a quantidade seja diferente de 120, a validação do catálogo gera um erro.

---

# 4. Estrutura hierárquica

A aplicação organiza os ativos segundo a seguinte estrutura:

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
        ├── Nvidia
        └── Alphabet
```

Essa hierarquia é gerada pela função:

```python
get_hierarchy()
```

---

# 5. Classes de ativos

O catálogo utiliza nove classes principais:

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

# 6. Grupos do catálogo

A ordem dos grupos é deliberadamente mantida no código para garantir estabilidade no menu da aplicação.

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

# 7. Campos dos registros

Cada ativo é representado por um registro padronizado.

## 7.1 Campos principais

| Campo            | Descrição                                              |
| ---------------- | ------------------------------------------------------ |
| `ticker`         | Símbolo utilizado para identificação/consulta do ativo |
| `name`           | Nome de exibição do ativo                              |
| `class`          | Classe principal do ativo                              |
| `subcategory`    | Subclasse ou segmento                                  |
| `market`         | Mercado, país ou região associado                      |
| `description`    | Descrição resumida                                     |
| `group`          | Grupo utilizado na organização do menu                 |
| `icon`           | Ícone visual associado à classe                        |
| `category_color` | Cor visual associada à classe                          |
| `data_type`      | Tipo técnico utilizado pela aplicação                  |

---

# 8. ₿ Criptomoedas

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

# 9. 🇧🇷 Ações Brasil

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
> O catálogo utiliza atualmente `AXIA3.SA` para representar a **Axia Energia (Antiga Eletrobras)**. Esse registro deve ser considerado a referência oficial do projeto para essa posição do catálogo.

---

# 10. 🇺🇸 Ações EUA

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

# 11. 🇪🇺 Ações Europa

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

---

# 12. 🌏 Ações Ásia

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
> O catálogo possui duas listagens relacionadas à Alibaba: `BABA`, identificada como China/EUA ADR, e `9988.HK`, identificada como Hong Kong. Elas devem ser tratadas pelo sistema como **tickers distintos**, pois são registros diferentes no catálogo.

---

# 13. 📈 ETFs de ações

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

---

# 14. 💵 ETFs de renda fixa

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

# 15. 🏢 REITs / Mercado imobiliário

**Total: 5 ativos**

|  # | Ticker | Nome                     | Subclasse        | Mercado | Descrição                       |
| -: | ------ | ------------------------ | ---------------- | ------- | ------------------------------- |
| 70 | `VNQ`  | Vanguard Real Estate ETF | Imobiliário      | EUA     | Carteira diversificada de REITs |
| 71 | `O`    | Realty Income            | Imobiliário      | EUA     | Imóveis comerciais              |
| 72 | `PLD`  | Prologis                 | Logística        | EUA     | Galpões e imóveis logísticos    |
| 73 | `AMT`  | American Tower           | Infraestrutura   | EUA     | Torres de telecomunicações      |
| 74 | `SPG`  | Simon Property Group     | Shopping centers | EUA     | Centros comerciais              |

> [!NOTE]
> Embora `VNQ` seja um ETF, no catálogo atual ele está classificado deliberadamente na classe `REIT`, dentro do grupo `reits`, para representar o segmento de mercado imobiliário.

---

# 16. 🏠 FIIs Brasil

**Total: 5 ativos**

|  # | Ticker      | Nome                    | Subclasse | Mercado   | Descrição                        |
| -: | ----------- | ----------------------- | --------- | --------- | -------------------------------- |
| 75 | `MXRF11.SA` | Maxi Renda              | Papel     | Brasil/B3 | Fundo imobiliário de recebíveis  |
| 76 | `HGLG11.SA` | Pátria Log              | Logística | Brasil/B3 | Imóveis logísticos               |
| 77 | `KNRI11.SA` | Kinea Renda Imobiliária | Híbrido   | Brasil/B3 | Escritórios e imóveis logísticos |
| 78 | `XPML11.SA` | XP Malls                | Shopping  | Brasil/B3 | Shopping centers                 |
| 79 | `BTLG11.SA` | BTG Logística           | Logística | Brasil/B3 | Galpões logísticos               |

---

# 17. 📊 Índices de mercado

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

---

# 18. 💱 Forex

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

# 19. 🛢️ Commodities

**Total: 14 ativos**

## 19.1 Metais

|   # | Ticker | Nome    | Mercado   | Descrição                  |
| --: | ------ | ------- | --------- | -------------------------- |
| 100 | `GC=F` | Ouro    | EUA/COMEX | Contrato futuro de ouro    |
| 101 | `SI=F` | Prata   | EUA/COMEX | Contrato futuro de prata   |
| 102 | `HG=F` | Cobre   | EUA/COMEX | Contrato futuro de cobre   |
| 103 | `PL=F` | Platina | EUA/NYMEX | Contrato futuro de platina |

## 19.2 Energia

|   # | Ticker | Nome           | Mercado    | Descrição      |
| --: | ------ | -------------- | ---------- | -------------- |
| 104 | `CL=F` | Petróleo WTI   | EUA/NYMEX  | Petróleo WTI   |
| 105 | `BZ=F` | Petróleo Brent | Global/ICE | Petróleo Brent |
| 106 | `NG=F` | Gás Natural    | EUA/NYMEX  | Gás natural    |

## 19.3 Agrícolas

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
> Os ativos desta classe utilizam `data_type = "future"`, refletindo que os registros representam contratos futuros de commodities.

---

# 20. 💵 Treasury / taxas de juros

**Total: 7 ativos**

Esta categoria possui uma característica específica: o catálogo combina **índices de rendimento (yield)** e **ETFs de Treasuries**.

## 20.1 Treasury — indicadores de yield

|   # | Ticker | Nome                | Subclasse   | Mercado | Descrição                       |
| --: | ------ | ------------------- | ----------- | ------- | ------------------------------- |
| 114 | `^IRX` | Treasury 13 Semanas | Curto prazo | EUA     | Yield de Treasury de 13 semanas |
| 115 | `^FVX` | Treasury 5 Anos     | Médio prazo | EUA     | Yield de Treasury de 5 anos     |
| 116 | `^TNX` | Treasury 10 Anos    | Longo prazo | EUA     | Yield de Treasury de 10 anos    |
| 117 | `^TYX` | Treasury 30 Anos    | Longo prazo | EUA     | Yield de Treasury de 30 anos    |

## 20.2 Treasury — ETFs

|   # | Ticker | Nome                     | Subclasse         | Mercado | Descrição                       |
| --: | ------ | ------------------------ | ----------------- | ------- | ------------------------------- |
| 118 | `BIL`  | Treasury 1-3 Meses (BIL) | Curto prazo       | EUA     | ETF de T-Bills de 1 a 3 meses   |
| 119 | `SHV`  | Treasury < 1 Ano (SHV)   | Curto prazo       | EUA     | ETF de Treasuries de até 1 ano  |
| 120 | `VGSH` | Treasury 1-3 Anos (VGSH) | Curto/médio prazo | EUA     | ETF de Treasuries de 1 a 3 anos |

> [!IMPORTANT]
> Os tickers `^IRX`, `^FVX`, `^TNX` e `^TYX` representam **indicadores de rendimento (yield)** e não devem ser interpretados da mesma forma que uma ação ou ETF.
>
> Já `BIL`, `SHV` e `VGSH` representam **ETFs negociados** que oferecem exposição a títulos do Tesouro americano.

---

# 21. Resumo quantitativo

A composição atual do catálogo é:

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

# 22. Distribuição por classe técnica

Os grupos são associados às seguintes classes técnicas:

| Classe      | Grupos associados                | Data type    |
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

---

# 23. Identificação dos ativos

Cada registro possui um `ticker` único.

Exemplos:

```text
BTC-USD
PETR4.SA
AAPL
SPY
VNQ
MXRF11.SA
^GSPC
USDBRL=X
GC=F
^TNX
```

O catálogo mantém um índice interno:

```python
ASSET_BY_TICKER
```

Esse índice permite localizar rapidamente os metadados de um ativo a partir do ticker.

---

# 24. Consulta individual

O módulo disponibiliza a função:

```python
get_asset(ticker)
```

Exemplo conceitual:

```python
from core.assets import get_asset

asset = get_asset("PETR4.SA")
```

O retorno contém os metadados do ativo.

Exemplo:

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

# 25. Filtragem do catálogo

A função:

```python
get_assets()
```

permite filtrar o catálogo por:

* classe;
* subclasse;
* mercado;
* tipo de dado;
* grupo.

Exemplo:

```python
from core.assets import get_assets

assets = get_assets(
    asset_class="Ação",
    market="EUA"
)
```

Outro exemplo:

```python
assets = get_assets(
    asset_class="Commodity"
)
```

---

# 26. Obtenção dos tickers

A função:

```python
get_tickers()
```

extrai os tickers do catálogo para utilização nas consultas de dados.

Exemplo:

```python
from core.assets import get_tickers

tickers = get_tickers()
```

O resultado é uma lista semelhante a:

```python
[
    "BTC-USD",
    "ETH-USD",
    "PETR4.SA",
    "AAPL",
    "SPY",
    ...
]
```

Essa estrutura pode ser utilizada nas consultas do `yfinance`.

---

# 27. Integração com o yfinance

O catálogo não realiza diretamente a consulta de dados de mercado.

Sua responsabilidade é fornecer os **metadados e identificadores dos ativos**.

A camada de dados utiliza os tickers para consultar o Yahoo Finance por meio do `yfinance`.

Exemplo:

```python
import yfinance as yf

data = yf.download(
    ["PETR4.SA", "VALE3.SA", "AAPL"],
    period="1y"
)
```

Para consultas individuais:

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")

history = ticker.history(
    period="1y"
)
```

> [!IMPORTANT]
> O catálogo e a camada de consulta devem permanecer conceitualmente separados.
>
> O catálogo define **o que a aplicação oferece**.
>
> A camada `yfinance` define **quais dados estão efetivamente disponíveis para consulta**.

---

# 28. Tipos de dados

O campo `data_type` é utilizado para identificar tecnicamente a natureza do ativo.

## `crypto`

Utilizado para criptomoedas.

Exemplo:

```text
BTC-USD
ETH-USD
SOL-USD
```

## `stock`

Utilizado para ações.

Exemplo:

```text
PETR4.SA
AAPL
NVDA
ASML
```

## `etf`

Utilizado para ETFs.

Exemplo:

```text
SPY
QQQ
BND
TLT
```

## `reit`

Utilizado para REITs.

Exemplo:

```text
O
PLD
AMT
```

## `fii`

Utilizado para FIIs brasileiros.

Exemplo:

```text
MXRF11.SA
HGLG11.SA
KNRI11.SA
```

## `index`

Utilizado para índices de mercado.

Exemplo:

```text
^BVSP
^GSPC
^VIX
```

## `forex`

Utilizado para pares de moedas.

Exemplo:

```text
USDBRL=X
EURUSD=X
USDJPY=X
```

## `future`

Utilizado para contratos futuros de commodities.

Exemplo:

```text
GC=F
CL=F
ZS=F
```

## `bond_yield`

Utilizado para instrumentos classificados pelo projeto como renda fixa/Treasury.

Exemplo:

```text
^TNX
^TYX
BIL
SHV
VGSH
```

---

# 29. Ícones e identidade visual

Cada classe possui um ícone padrão.

| Classe      | Ícone |
| ----------- | ----- |
| Criptomoeda | ₿     |
| Ação        | 📈    |
| ETF         | 📊    |
| REIT        | 🏢    |
| FII         | 🏠    |
| Índice      | 📐    |
| Forex       | 💱    |
| Commodity   | 🛢️   |
| Renda Fixa  | 💵    |

Os ícones são definidos no dicionário:

```python
CATEGORY_METADATA
```

e aplicados automaticamente aos registros por meio da função:

```python
_asset()
```

---

# 30. Cores das categorias

O catálogo também mantém uma cor padrão para cada classe.

| Classe      | Cor       |
| ----------- | --------- |
| Criptomoeda | `#F59E0B` |
| Ação        | `#2563EB` |
| ETF         | `#7C3AED` |
| REIT        | `#0F766E` |
| FII         | `#0891B2` |
| Índice      | `#475569` |
| Forex       | `#16A34A` |
| Commodity   | `#B45309` |
| Renda Fixa  | `#0E7490` |

Essas cores são metadados da interface e não possuem significado financeiro.

---

# 31. Validação automática

O catálogo possui uma função de validação:

```python
validate_catalog()
```

Essa validação verifica três aspectos principais:

### 31.1 Quantidade

O catálogo deve possuir exatamente:

```text
120 ativos
```

### 31.2 Unicidade

Não são permitidos tickers duplicados.

Caso sejam encontrados registros duplicados, o sistema gera erro informando os tickers envolvidos.

### 31.3 Campos obrigatórios

Cada registro deve possuir:

```text
ticker
name
class
subcategory
market
description
group
icon
category_color
data_type
```

A ausência de qualquer campo obrigatório gera erro durante a validação.

---

# 32. Regras para inclusão de novos ativos

Quando um novo ativo for incluído no catálogo, recomenda-se seguir as seguintes regras:

1. Confirmar o ticker utilizado pelo Yahoo Finance;
2. Definir um nome de exibição claro;
3. Classificar corretamente o ativo;
4. Definir uma subclasse;
5. Informar o mercado correspondente;
6. Criar uma descrição curta e objetiva;
7. Associar o ativo ao grupo correto;
8. Utilizar o `data_type` correspondente à classe;
9. Evitar duplicidade de ticker;
10. Atualizar este documento;
11. Executar os testes;
12. Confirmar que `validate_catalog()` continua funcionando.

---

# 33. Exemplo de inclusão

Um novo ativo deve seguir o padrão utilizado pelo módulo:

```python
_asset(
    "TICKER",
    "Nome do ativo",
    "Classe",
    "Subclasse",
    "Mercado",
    "Descrição",
    "grupo",
)
```

Exemplo:

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

Os metadados de:

```text
icon
category_color
data_type
```

são herdados automaticamente da classe, salvo quando explicitamente sobrescritos.

---

# 34. Expansão futura

O catálogo foi projetado para permitir expansão.

Possíveis futuras categorias incluem:

* novos mercados acionários;
* novos ETFs;
* mais FIIs;
* mais REITs;
* novos instrumentos de renda fixa;
* novas commodities;
* novos índices;
* novos pares cambiais;
* outros instrumentos financeiros disponibilizados pela fonte de dados.

A expansão deve preservar a arquitetura:

```text
Classe
→ Subclasse
→ Mercado
→ Ativo
```

---

# 35. Critérios para manutenção

O catálogo deve ser tratado como uma **fonte central de verdade para os ativos disponíveis na interface**.

Evite cadastrar o mesmo ticker diretamente em diferentes módulos.

### Não recomendado

```python
stocks = [
    "PETR4.SA",
    "VALE3.SA",
]
```

em vários arquivos independentes.

### Recomendado

```python
from core.assets import get_assets
```

ou:

```python
from core.assets import get_tickers
```

Dessa maneira, alterações no catálogo são propagadas de forma centralizada.

---

# 36. Responsabilidades do catálogo

O catálogo é responsável por:

* identificação;
* classificação;
* organização;
* descrição;
* agrupamento;
* metadados visuais;
* tipo técnico;
* fornecimento dos tickers.

O catálogo **não é responsável** por:

* buscar dados históricos;
* calcular indicadores;
* calcular retorno;
* calcular volatilidade;
* calcular Sharpe;
* calcular drawdown;
* realizar recomendações de investimento;
* garantir disponibilidade dos dados externos.

---

# 37. Relação com as análises do Argos DataLab

Os ativos do catálogo podem alimentar diferentes funcionalidades da aplicação, incluindo:

```text
Catálogo
   ↓
Seleção do ativo
   ↓
Ticker
   ↓
Consulta de dados
   ↓
Tratamento
   ↓
Análise
   ├── Retorno
   ├── Volatilidade
   ├── Drawdown
   ├── Sharpe
   ├── Indicadores técnicos
   ├── Sazonalidade
   └── Correlação
   ↓
Visualização
```

O catálogo, portanto, funciona como a camada de identificação e organização que conecta a interface à camada de dados.

---

# 38. Lista consolidada dos 120 tickers

Para facilitar auditorias, testes e manutenção, segue a lista completa na ordem atual do catálogo:

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

# 39. Checklist de atualização

Antes de realizar commit de uma alteração no catálogo:

```text
[ ] O ticker foi validado?
[ ] O ativo possui nome de exibição?
[ ] A classe foi definida?
[ ] A subclasse foi definida?
[ ] O mercado foi definido?
[ ] A descrição foi preenchida?
[ ] O grupo está correto?
[ ] O data_type está correto?
[ ] Não existe ticker duplicado?
[ ] A quantidade esperada foi atualizada?
[ ] O catálogo foi validado?
[ ] Os testes foram executados?
[ ] Este documento foi atualizado?
```

---

# 40. Referência técnica

O catálogo foi desenvolvido para funcionar como camada de metadados sobre a infraestrutura de consulta de dados do Argos DataLab.

A integração com o `yfinance` deve considerar que diferentes tipos de instrumentos podem oferecer diferentes conjuntos de informações e níveis de histórico.

A documentação oficial do `yfinance` apresenta suporte para:

* `Ticker`;
* múltiplos tickers;
* histórico;
* download de dados;
* ETFs e fundos;
* informações financeiras;
* dividendos;
* desdobramentos;
* dados de mercado;
* consultas específicas por instrumento.

---

# 41. Aviso metodológico

A presença de um ativo neste catálogo significa apenas que ele foi **selecionado para fazer parte do universo de análise do Argos DataLab**.

Isso não significa:

* recomendação de investimento;
* indicação de compra ou venda;
* avaliação de qualidade do ativo;
* previsão de valorização;
* garantia de liquidez;
* garantia de disponibilidade permanente dos dados.

Os dados externos podem sofrer alterações, indisponibilidade ou limitações específicas de acordo com o ativo e a fonte utilizada.

---

# 42. Aviso acadêmico

O Argos DataLab está sendo desenvolvido para fins de:

* pesquisa;
* estudo;
* ensino;
* análise exploratória;
* desenvolvimento tecnológico.

O catálogo de ativos constitui parte da infraestrutura metodológica do projeto e poderá ser atualizado conforme a evolução da pesquisa e dos requisitos da aplicação.

---

# 43. Arquivo de implementação

A fonte de implementação deste catálogo é:

```text
core/assets.py
```

A documentação correspondente é:

```text
docs/catalogo-de-ativos.md
```

Estrutura recomendada:

```text
argos/
├── app/
├── core/
│   └── assets.py
├── docs/
│   └── catalogo-de-ativos.md
├── tests/
├── requirements.txt
└── README.md
```

---

# 44. Controle de consistência

O código-fonte deve permanecer como a **fonte operacional** do catálogo.

Este documento deve permanecer como a **fonte documental**.

Sempre que houver alteração estrutural no arquivo:

```text
core/assets.py
```

o arquivo:

```text
docs/catalogo-de-ativos.md
```

deve ser revisado para manter a documentação sincronizada.

A regra geral é:

```text
Alterou o catálogo?
        ↓
Atualizou os testes?
        ↓
Atualizou a documentação?
        ↓
Executou a validação?
        ↓
Commit
```

---

# 45. Status atual

**Status:** ✅ Catálogo definido

**Versão:** Catálogo de 120 ativos

**Total de ativos:** 120

**Total de grupos:** 13

**Fonte de identificação:** Tickers utilizados pelo ecossistema Yahoo Finance/yfinance

**Arquivo de implementação:**

```text
core/assets.py
```

**Arquivo de documentação:**

```text
docs/catalogo-de-ativos.md
```

**Última finalidade definida:**

> Base centralizada de ativos financeiros para seleção, organização e análise no Argos DataLab.

---

## 📌 Resumo

O catálogo atual do Argos DataLab reúne **120 ativos financeiros**, distribuídos entre criptomoedas, ações brasileiras, ações americanas, ações europeias, ações asiáticas, ETFs, REITs, FIIs, índices, Forex, commodities e instrumentos relacionados a Treasury e taxas de juros.

Sua estrutura padronizada permite que a aplicação mantenha uma única fonte de metadados para a seleção de ativos e para a integração com a camada de consulta de dados.

```text
120 ATIVOS
     │
     ├── 13 GRUPOS
     │
     ├── 9 CLASSES
     │
     ├── CLASSE
     │      ↓
     │   SUBCLASSE
     │      ↓
     │    MERCADO
     │      ↓
     │    TICKER
     │
     └── yfinance
            ↓
       Dados históricos
            ↓
          Análises
```

**Argos DataLab — Catálogo centralizado de ativos financeiros.**
