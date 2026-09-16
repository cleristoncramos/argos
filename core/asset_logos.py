"""
Mapeamento de ativos para URLs de logo/ícone, usado para exibir
imagens visuais dos ativos selecionados nas páginas do Argos DataLab.

Fontes usadas (gratuitas, sem necessidade de chave de API):
- Criptomoedas: CoinCap (ícones estáticos por símbolo).
- Ações/ETFs/REITs/FIIs: Financial Modeling Prep (logos públicos por ticker).
- Índices, Forex, Commodities, Treasury: sem fonte confiável de logo --
  o chamador deve usar o emoji de fallback já presente em ASSETS["icon"].
"""

from functools import lru_cache
from typing import Optional


# ==========================================================
# Criptomoedas
# ==========================================================
CRYPTO_LOGO_BASE_URL = "https://assets.coincap.io/assets/icons/{symbol}@2x.png"


def _crypto_symbol_from_ticker(ticker: str) -> str:
    """Extrai o símbolo da moeda a partir do ticker (ex: 'BTC-USD' -> 'btc')."""
    return ticker.split("-")[0].lower()


# ==========================================================
# Ações, ETFs, REITs e FIIs
# ==========================================================
STOCK_LOGO_BASE_URL = "https://images.financialmodelingprep.com/symbol/{ticker}.png"

STOCK_LIKE_GROUPS = {
    "br_stocks",
    "us_stocks",
    "europe_stocks",
    "asia_stocks",
    "equity_etfs",
    "fixed_income_etfs",
    "reits",
    "brazil_fiis",
    "fiis",
}


# ==========================================================
# Casos especiais (índices e commodities mais conhecidos).
# Amplie este dicionário conforme novos ativos forem adicionados.
# ==========================================================
SPECIAL_LOGO_MAP = {
    "^GSPC": "https://images.financialmodelingprep.com/symbol/%5EGSPC.png",
    "^DJI": "https://images.financialmodelingprep.com/symbol/%5EDJI.png",
    "^IXIC": "https://images.financialmodelingprep.com/symbol/%5EIXIC.png",
}


@lru_cache(maxsize=256)
def get_asset_logo_url(ticker: str, group: str) -> Optional[str]:
    """
    Retorna a URL do logo/ícone do ativo, ou None se não houver uma
    fonte confiável para esse grupo/ticker. Nesse caso, o chamador deve
    usar o emoji de fallback do próprio ativo (campo "icon" em ASSETS).
    """
    ticker_upper = ticker.upper()

    if ticker_upper in SPECIAL_LOGO_MAP:
        return SPECIAL_LOGO_MAP[ticker_upper]

    group_normalized = (group or "").lower()

    if group_normalized == "crypto":
        symbol = _crypto_symbol_from_ticker(ticker)
        return CRYPTO_LOGO_BASE_URL.format(symbol=symbol)

    if group_normalized in STOCK_LIKE_GROUPS:
        return STOCK_LOGO_BASE_URL.format(ticker=ticker_upper)

    # indexes, forex, commodities, treasury/rates: sem fonte confiável
    return None