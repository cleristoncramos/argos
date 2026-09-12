"""Catálogo centralizado de ativos suportados pelo Argos DataLab.

Os registros deste módulo são metadados editoriais para seleção e
organização da interface. Eles não garantem que o Yahoo Finance ofereça
a mesma profundidade de histórico, fundamentos, dividendos ou informações
para todos os tipos de ativos.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from copy import deepcopy
from typing import Any


AssetRecord = dict[str, str]


CATEGORY_METADATA: dict[str, dict[str, str]] = {
    "Criptomoeda": {
        "icon": "₿",
        "category_color": "#F59E0B",
        "data_type": "crypto",
    },
    "Ação": {
        "icon": "📈",
        "category_color": "#2563EB",
        "data_type": "stock",
    },
    "ETF": {
        "icon": "📊",
        "category_color": "#7C3AED",
        "data_type": "etf",
    },
    "REIT": {
        "icon": "🏢",
        "category_color": "#0F766E",
        "data_type": "reit",
    },
    "FII": {
        "icon": "🏠",
        "category_color": "#0891B2",
        "data_type": "fii",
    },
    "Índice": {
        "icon": "📐",
        "category_color": "#475569",
        "data_type": "index",
    },
    "Forex": {
        "icon": "💱",
        "category_color": "#16A34A",
        "data_type": "forex",
    },
    "Commodity": {
        "icon": "🛢️",
        "category_color": "#B45309",
        "data_type": "future",
    },
    "Renda Fixa": {
        "icon": "💵",
        "category_color": "#0E7490",
        "data_type": "bond_yield",
    },
}


# A ordem dos grupos é deliberada para manter o menu estável.
ASSET_GROUPS: list[dict[str, str]] = [
    {"key": "crypto", "label": "₿ Criptomoedas", "class": "Criptomoeda"},
    {"key": "br_stocks", "label": "🇧🇷 Ações Brasil", "class": "Ação"},
    {"key": "us_stocks", "label": "🇺🇸 Ações EUA", "class": "Ação"},
    {"key": "europe_stocks", "label": "🇪🇺 Ações Europa", "class": "Ação"},
    {"key": "asia_stocks", "label": "🌏 Ações Ásia", "class": "Ação"},
    {"key": "equity_etfs", "label": "📈 ETFs de ações", "class": "ETF"},
    {"key": "fixed_income_etfs", "label": "💵 ETFs de renda fixa", "class": "ETF"},
    {"key": "reits", "label": "🏢 REITs / Mercado imobiliário", "class": "REIT"},
    {"key": "brazil_fiis", "label": "🏠 FIIs Brasil", "class": "FII"},
    {"key": "indexes", "label": "📊 Índices de mercado", "class": "Índice"},
    {"key": "forex", "label": "💱 Forex", "class": "Forex"},
    {"key": "commodities", "label": "🛢️ Commodities", "class": "Commodity"},
    {"key": "treasury", "label": "💵 Treasury / taxas de juros", "class": "Renda Fixa"},
]


def _asset(
    ticker: str,
    name: str,
    asset_class: str,
    subcategory: str,
    market: str,
    description: str,
    group: str,
    *,
    data_type: str | None = None,
    icon: str | None = None,
    category_color: str | None = None,
) -> AssetRecord:
    category = CATEGORY_METADATA[asset_class]

    return {
        "ticker": ticker,
        "name": name,
        "class": asset_class,
        "subcategory": subcategory,
        "market": market,
        "description": description,
        "group": group,
        "icon": icon or category["icon"],
        "category_color": category_color or category["category_color"],
        "data_type": data_type or category["data_type"],
    }


ASSETS: list[AssetRecord] = [
    _asset("BTC-USD", "Bitcoin", "Criptomoeda", "Cripto principal", "Global", "Principal criptomoeda por capitalização", "crypto"),
    _asset("ETH-USD", "Ethereum", "Criptomoeda", "Smart contracts", "Global", "Principal plataforma de contratos inteligentes", "crypto"),
    _asset("BNB-USD", "BNB", "Criptomoeda", "Exchange/Blockchain", "Global", "Token associado ao ecossistema BNB", "crypto"),
    _asset("SOL-USD", "Solana", "Criptomoeda", "Smart contracts", "Global", "Blockchain de alta capacidade", "crypto"),
    _asset("XRP-USD", "XRP", "Criptomoeda", "Pagamentos", "Global", "Ativo voltado a pagamentos e liquidação", "crypto"),
    _asset("ADA-USD", "Cardano", "Criptomoeda", "Smart contracts", "Global", "Blockchain de contratos inteligentes", "crypto"),
    _asset("DOGE-USD", "Dogecoin", "Criptomoeda", "Meme coin", "Global", "Criptomoeda originada como meme", "crypto"),
    _asset("AVAX-USD", "Avalanche", "Criptomoeda", "Smart contracts", "Global", "Plataforma blockchain", "crypto"),
    _asset("TRX-USD", "TRON", "Criptomoeda", "Blockchain", "Global", "Rede blockchain focada em aplicações descentralizadas", "crypto"),
    _asset("LINK-USD", "Chainlink", "Criptomoeda", "Oracle", "Global", "Rede de oráculos para aplicações blockchain", "crypto"),

    _asset("PETR4.SA", "Petrobras PN", "Ação", "Energia", "Brasil/B3", "Petróleo e gás", "br_stocks"),
    _asset("VALE3.SA", "Vale", "Ação", "Mineração", "Brasil/B3", "Mineração e metais", "br_stocks"),
    _asset("ITUB4.SA", "Itaú Unibanco PN", "Ação", "Bancos", "Brasil/B3", "Banco privado", "br_stocks"),
    _asset("BBAS3.SA", "Banco do Brasil", "Ação", "Bancos", "Brasil/B3", "Banco de controle estatal", "br_stocks"),
    _asset("BBDC4.SA", "Bradesco PN", "Ação", "Bancos", "Brasil/B3", "Banco privado", "br_stocks"),
    _asset("ITSA4.SA", "Itaúsa", "Ação", "Holding financeira", "Brasil/B3", "Holding de participações", "br_stocks"),
    _asset("WEGE3.SA", "WEG", "Ação", "Indústria", "Brasil/B3", "Equipamentos elétricos e automação", "br_stocks"),
    _asset("ABEV3.SA", "Ambev", "Ação", "Consumo", "Brasil/B3", "Bebidas", "br_stocks"),
    _asset("B3SA3.SA", "B3", "Ação", "Infraestrutura financeira", "Brasil/B3", "Bolsa e infraestrutura de mercado", "br_stocks"),
    _asset("RENT3.SA", "Localiza", "Ação", "Serviços", "Brasil/B3", "Locação de veículos", "br_stocks"),
    _asset("AXIA3.SA", "Axia Energia (Antiga Eletrobras)", "Ação", "Energia elétrica", "Brasil/B3", "Geração e transmissão de energia", "br_stocks"),
    _asset("SUZB3.SA", "Suzano", "Ação", "Papel e celulose", "Brasil/B3", "Celulose e papel", "br_stocks"),

    _asset("AAPL", "Apple", "Ação", "Tecnologia", "EUA", "Eletrônicos e serviços", "us_stocks"),
    _asset("MSFT", "Microsoft", "Ação", "Tecnologia", "EUA", "Software e computação em nuvem", "us_stocks"),
    _asset("NVDA", "Nvidia", "Ação", "Semicondutores", "EUA", "Chips e computação para IA", "us_stocks"),
    _asset("AMZN", "Amazon", "Ação", "Tecnologia/Varejo", "EUA", "E-commerce e cloud", "us_stocks"),
    _asset("GOOGL", "Alphabet", "Ação", "Tecnologia", "EUA", "Google, publicidade e cloud", "us_stocks"),
    _asset("META", "Meta Platforms", "Ação", "Tecnologia", "EUA", "Redes sociais e publicidade digital", "us_stocks"),
    _asset("TSLA", "Tesla", "Ação", "Automóveis", "EUA", "Veículos elétricos e energia", "us_stocks"),
    _asset("AVGO", "Broadcom", "Ação", "Semicondutores", "EUA", "Semicondutores e infraestrutura tecnológica", "us_stocks"),
    _asset("BRK-B", "Berkshire Hathaway", "Ação", "Holding", "EUA", "Conglomerado de investimentos", "us_stocks"),
    _asset("JPM", "JPMorgan Chase", "Ação", "Bancos", "EUA", "Serviços financeiros", "us_stocks"),
    _asset("V", "Visa", "Ação", "Pagamentos", "EUA", "Rede global de pagamentos", "us_stocks"),
    _asset("MA", "Mastercard", "Ação", "Pagamentos", "EUA", "Rede global de pagamentos", "us_stocks"),
    _asset("LLY", "Eli Lilly", "Ação", "Farmacêutica", "EUA", "Medicamentos", "us_stocks"),
    _asset("WMT", "Walmart", "Ação", "Varejo", "EUA", "Varejo e supermercados", "us_stocks"),
    _asset("XOM", "Exxon Mobil", "Ação", "Energia", "EUA", "Petróleo e gás", "us_stocks"),

    _asset("ASML", "ASML Holding", "Ação", "Semicondutores", "Holanda", "Equipamentos para fabricação de chips", "europe_stocks"),
    _asset("SAP", "SAP", "Ação", "Software", "Alemanha", "Software empresarial", "europe_stocks"),
    _asset("NESN.SW", "Nestlé", "Ação", "Consumo", "Suíça", "Alimentos e bebidas", "europe_stocks"),
    _asset("MC.PA", "LVMH", "Ação", "Luxo", "França", "Bens de luxo", "europe_stocks"),
    _asset("SHEL", "Shell", "Ação", "Energia", "Reino Unido", "Petróleo e gás", "europe_stocks"),
    _asset("NOVO-B.CO", "Novo Nordisk", "Ação", "Farmacêutica", "Dinamarca", "Produtos farmacêuticos", "europe_stocks"),
    _asset("SIE.DE", "Siemens", "Ação", "Indústria", "Alemanha", "Automação e tecnologia industrial", "europe_stocks"),
    _asset("AIR.PA", "Airbus", "Ação", "Aeroespacial", "França", "Aviação e defesa", "europe_stocks"),

    _asset("TSM", "Taiwan Semiconductor", "Ação", "Semicondutores", "Taiwan/EUA ADR", "Fabricação de chips", "asia_stocks"),
    _asset("BABA", "Alibaba", "Ação", "Tecnologia/E-commerce", "China/EUA ADR", "E-commerce e cloud", "asia_stocks"),
    _asset("SONY", "Sony", "Ação", "Eletrônicos/Entretenimento", "Japão", "Eletrônicos e entretenimento", "asia_stocks"),
    _asset("005930.KS", "Samsung Electronics", "Ação", "Tecnologia", "Coreia do Sul", "Eletrônicos e semicondutores", "asia_stocks"),
    _asset("0700.HK", "Tencent", "Ação", "Tecnologia", "Hong Kong", "Internet, games e serviços digitais", "asia_stocks"),
    _asset("7203.T", "Toyota", "Ação", "Automóveis", "Japão", "Automóveis", "asia_stocks"),
    _asset("000660.KS", "SK Hynix", "Ação", "Semicondutores", "Coreia do Sul", "Memórias e semicondutores", "asia_stocks"),
    _asset("9988.HK", "Alibaba Group", "Ação", "Tecnologia/E-commerce", "Hong Kong", "E-commerce e tecnologia", "asia_stocks"),

    _asset("SPY", "SPDR S&P 500 ETF", "ETF", "Large Cap EUA", "EUA", "Replica o S&P 500", "equity_etfs"),
    _asset("QQQ", "Invesco QQQ", "ETF", "Nasdaq-100", "EUA", "Grandes empresas não financeiras do Nasdaq", "equity_etfs"),
    _asset("VTI", "Vanguard Total Stock Market", "ETF", "Mercado EUA", "EUA", "Mercado acionário americano amplo", "equity_etfs"),
    _asset("VT", "Vanguard Total World Stock", "ETF", "Global", "Global", "Ações de mercados mundiais", "equity_etfs"),
    _asset("EEM", "iShares MSCI Emerging Markets", "ETF", "Emergentes", "Global", "Mercados emergentes", "equity_etfs"),
    _asset("EWZ", "iShares MSCI Brazil", "ETF", "Brasil", "EUA/Brasil", "Ações brasileiras", "equity_etfs"),
    _asset("IWM", "iShares Russell 2000", "ETF", "Small Caps", "EUA", "Pequenas empresas americanas", "equity_etfs"),
    _asset("DIA", "SPDR Dow Jones Industrial Average", "ETF", "Large Cap", "EUA", "Replica o Dow Jones", "equity_etfs"),
    _asset("VEA", "Vanguard FTSE Developed Markets", "ETF", "Internacional", "Global", "Mercados desenvolvidos fora dos EUA", "equity_etfs"),
    _asset("VOO", "Vanguard S&P 500", "ETF", "Large Cap EUA", "EUA", "Replica o S&P 500", "equity_etfs"),

    _asset("BND", "Vanguard Total Bond Market", "ETF", "Bonds EUA", "EUA", "Mercado amplo de títulos americanos", "fixed_income_etfs"),
    _asset("AGG", "iShares Core U.S. Aggregate Bond", "ETF", "Bonds EUA", "EUA", "Renda fixa americana ampla", "fixed_income_etfs"),
    _asset("TLT", "iShares 20+ Year Treasury Bond", "ETF", "Treasury longo", "EUA", "Treasuries de longo prazo", "fixed_income_etfs"),
    _asset("IEF", "iShares 7-10 Year Treasury Bond", "ETF", "Treasury médio", "EUA", "Treasuries de prazo intermediário", "fixed_income_etfs"),
    _asset("SHY", "iShares 1-3 Year Treasury Bond", "ETF", "Treasury curto", "EUA", "Treasuries de curto prazo", "fixed_income_etfs"),
    _asset("TIP", "iShares TIPS Bond", "ETF", "Inflação", "EUA", "Títulos protegidos contra inflação", "fixed_income_etfs"),

    _asset("VNQ", "Vanguard Real Estate ETF", "REIT", "Imobiliário", "EUA", "Carteira diversificada de REITs", "reits"),
    _asset("O", "Realty Income", "REIT", "Imobiliário", "EUA", "Imóveis comerciais", "reits"),
    _asset("PLD", "Prologis", "REIT", "Logística", "EUA", "Galpões e imóveis logísticos", "reits"),
    _asset("AMT", "American Tower", "REIT", "Infraestrutura", "EUA", "Torres de telecomunicações", "reits"),
    _asset("SPG", "Simon Property Group", "REIT", "Shopping centers", "EUA", "Centros comerciais", "reits"),

    _asset("MXRF11.SA", "Maxi Renda", "FII", "Papel", "Brasil/B3", "Fundo imobiliário de recebíveis", "brazil_fiis"),
    _asset("HGLG11.SA", "Pátria Log", "FII", "Logística", "Brasil/B3", "Imóveis logísticos", "brazil_fiis"),
    _asset("KNRI11.SA", "Kinea Renda Imobiliária", "FII", "Híbrido", "Brasil/B3", "Escritórios e imóveis logísticos", "brazil_fiis"),
    _asset("XPML11.SA", "XP Malls", "FII", "Shopping", "Brasil/B3", "Shopping centers", "brazil_fiis"),
    _asset("BTLG11.SA", "BTG Logística", "FII", "Logística", "Brasil/B3", "Galpões logísticos", "brazil_fiis"),

    _asset("^BVSP", "Ibovespa", "Índice", "Ações", "Brasil", "Principal índice da B3", "indexes"),
    _asset("^GSPC", "S&P 500", "Índice", "Large Cap", "EUA", "500 grandes empresas americanas", "indexes"),
    _asset("^IXIC", "Nasdaq Composite", "Índice", "Tecnologia/Mercado", "EUA", "Empresas listadas no Nasdaq", "indexes"),
    _asset("^DJI", "Dow Jones", "Índice", "Large Cap", "EUA", "30 grandes empresas americanas", "indexes"),
    _asset("^RUT", "Russell 2000", "Índice", "Small Caps", "EUA", "Pequenas empresas americanas", "indexes"),
    _asset("^VIX", "CBOE Volatility Index", "Índice", "Volatilidade", "EUA", "Expectativa de volatilidade do S&P 500", "indexes"),
    _asset("^FTSE", "FTSE 100", "Índice", "Large Cap", "Reino Unido", "Principais empresas britânicas", "indexes"),
    _asset("^GDAXI", "DAX", "Índice", "Large Cap", "Alemanha", "Principais empresas alemãs", "indexes"),
    _asset("^FCHI", "CAC 40", "Índice", "Large Cap", "França", "Principais empresas francesas", "indexes"),
    _asset("^N225", "Nikkei 225", "Índice", "Large Cap", "Japão", "Principais empresas japonesas", "indexes"),
    _asset("^HSI", "Hang Seng", "Índice", "Large Cap", "Hong Kong", "Principais empresas de Hong Kong", "indexes"),
    _asset("000001.SS", "Shanghai Composite", "Índice", "Mercado amplo", "China", "Mercado acionário de Xangai", "indexes"),

    _asset("USDBRL=X", "USD/BRL", "Forex", "Major/EM", "Global", "Dólar americano contra real", "forex"),
    _asset("EURUSD=X", "EUR/USD", "Forex", "Major", "Global", "Euro contra dólar", "forex"),
    _asset("GBPUSD=X", "GBP/USD", "Forex", "Major", "Global", "Libra contra dólar", "forex"),
    _asset("USDJPY=X", "USD/JPY", "Forex", "Major", "Global", "Dólar contra iene", "forex"),
    _asset("USDCHF=X", "USD/CHF", "Forex", "Major", "Global", "Dólar contra franco suíço", "forex"),
    _asset("AUDUSD=X", "AUD/USD", "Forex", "Major", "Global", "Dólar australiano contra dólar", "forex"),
    _asset("USDCAD=X", "USD/CAD", "Forex", "Major", "Global", "Dólar contra dólar canadense", "forex"),
    _asset("USDCNY=X", "USD/CNY", "Forex", "China", "Global", "Dólar contra yuan", "forex"),

    _asset("GC=F", "Ouro", "Commodity", "Metal precioso", "EUA/COMEX", "Contrato futuro de ouro", "commodities"),
    _asset("SI=F", "Prata", "Commodity", "Metal precioso", "EUA/COMEX", "Contrato futuro de prata", "commodities"),
    _asset("HG=F", "Cobre", "Commodity", "Metal industrial", "EUA/COMEX", "Contrato futuro de cobre", "commodities"),
    _asset("PL=F", "Platina", "Commodity", "Metal precioso", "EUA/NYMEX", "Contrato futuro de platina", "commodities"),
    _asset("CL=F", "Petróleo WTI", "Commodity", "Energia", "EUA/NYMEX", "Petróleo WTI", "commodities"),
    _asset("BZ=F", "Petróleo Brent", "Commodity", "Energia", "Global/ICE", "Petróleo Brent", "commodities"),
    _asset("NG=F", "Gás Natural", "Commodity", "Energia", "EUA/NYMEX", "Gás natural", "commodities"),
    _asset("ZS=F", "Soja", "Commodity", "Agrícola", "EUA/CBOT", "Soja", "commodities"),
    _asset("ZC=F", "Milho", "Commodity", "Agrícola", "EUA/CBOT", "Milho", "commodities"),
    _asset("ZW=F", "Trigo", "Commodity", "Agrícola", "EUA/CBOT", "Trigo", "commodities"),
    _asset("KC=F", "Café", "Commodity", "Agrícola", "EUA/ICE", "Café", "commodities"),
    _asset("CC=F", "Cacau", "Commodity", "Agrícola", "EUA/ICE", "Cacau", "commodities"),
    _asset("SB=F", "Açúcar", "Commodity", "Agrícola", "EUA/ICE", "Açúcar", "commodities"),
    _asset("CT=F", "Algodão", "Commodity", "Agrícola", "EUA/ICE", "Algodão", "commodities"),

    _asset("^IRX", "Treasury 13 Semanas", "Renda Fixa", "Curto prazo", "EUA", "Yield de Treasury de 13 semanas", "treasury"),
    _asset("^FVX", "Treasury 5 Anos", "Renda Fixa", "Médio prazo", "EUA", "Yield de Treasury de 5 anos", "treasury"),
    _asset("^TNX", "Treasury 10 Anos", "Renda Fixa", "Longo prazo", "EUA", "Yield de Treasury de 10 anos", "treasury"),
    _asset("^TYX", "Treasury 30 Anos", "Renda Fixa", "Longo prazo", "EUA", "Yield de Treasury de 30 anos", "treasury"),
    _asset("BIL", "Treasury 1-3 Meses (BIL)", "Renda Fixa", "Curto prazo", "EUA", "ETF de T-Bills de 1 a 3 meses", "treasury"),
    _asset("SHV", "Treasury < 1 Ano (SHV)", "Renda Fixa", "Curto prazo", "EUA", "ETF de Treasuries de até 1 ano", "treasury"),
    _asset("VGSH", "Treasury 1-3 Anos (VGSH)", "Renda Fixa", "Curto/médio prazo", "EUA", "ETF de Treasuries de 1 a 3 anos", "treasury"),
]


ASSET_BY_TICKER: dict[str, AssetRecord] = {
    asset["ticker"]: asset
    for asset in ASSETS
}


def get_asset(ticker: str) -> AssetRecord | None:
    """Retorna uma cópia dos metadados do ticker informado."""
    asset = ASSET_BY_TICKER.get(ticker.strip())
    return deepcopy(asset) if asset else None


def get_assets(
    *,
    asset_class: str | None = None,
    subcategory: str | None = None,
    market: str | None = None,
    data_type: str | None = None,
    group: str | None = None,
) -> list[AssetRecord]:
    """Filtra ativos por classe, subclasse, mercado, grupo ou tipo."""
    filters = {
        "class": asset_class,
        "subcategory": subcategory,
        "market": market,
        "data_type": data_type,
        "group": group,
    }

    return [
        deepcopy(asset)
        for asset in ASSETS
        if all(
            expected is None or asset[key] == expected
            for key, expected in filters.items()
        )
    ]


def get_tickers(assets: Iterable[Mapping[str, Any]] | None = None) -> list[str]:
    """Extrai tickers para uso em yf.download() ou yf.Tickers()."""
    source = ASSETS if assets is None else assets
    return [str(asset["ticker"]) for asset in source]


def get_hierarchy() -> dict[str, dict[str, dict[str, list[AssetRecord]]]]:
    """Monta Classe → Subclasse → Mercado → Ativos."""
    hierarchy: dict[str, dict[str, dict[str, list[AssetRecord]]]] = {}

    for asset in ASSETS:
        class_node = hierarchy.setdefault(asset["class"], {})
        subcategory_node = class_node.setdefault(
            asset["subcategory"],
            {},
        )
        market_node = subcategory_node.setdefault(
            asset["market"],
            [],
        )
        market_node.append(deepcopy(asset))

    return hierarchy


def validate_catalog() -> None:
    """Valida unicidade, campos obrigatórios e quantidade do catálogo."""
    required_fields = {
        "ticker",
        "name",
        "class",
        "subcategory",
        "market",
        "description",
        "group",
        "icon",
        "category_color",
        "data_type",
    }

    if len(ASSETS) != 120:
        raise ValueError(
            f"O catálogo deveria conter 120 ativos, mas contém {len(ASSETS)}."
        )

    tickers = [asset["ticker"] for asset in ASSETS]
    duplicated_tickers = {
        ticker
        for ticker in tickers
        if tickers.count(ticker) > 1
    }

    if duplicated_tickers:
        raise ValueError(
            "Tickers duplicados no catálogo: "
            + ", ".join(sorted(duplicated_tickers))
        )

    for asset in ASSETS:
        missing_fields = required_fields - asset.keys()
        if missing_fields:
            raise ValueError(
                f"Campos ausentes em {asset.get('ticker')}: "
                + ", ".join(sorted(missing_fields))
            )


validate_catalog()


__all__ = [
    "ASSETS",
    "ASSET_BY_TICKER",
    "ASSET_GROUPS",
    "CATEGORY_METADATA",
    "get_asset",
    "get_assets",
    "get_hierarchy",
    "get_tickers",
    "validate_catalog",
]