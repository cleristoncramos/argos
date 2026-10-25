"""
Mapeamento de ativos para URLs de logo/ícone, usado para exibir
imagens visuais dos ativos selecionados nas páginas do Argos.

Fontes usadas (gratuitas, sem necessidade de chave de API):
- Criptomoedas: CoinCap (ícones estáticos por símbolo).
- Ações/ETFs/REITs/FIIs: Financial Modeling Prep (logos públicos por ticker).
- Índices, Forex, Commodities, Treasury: sem fonte confiável de logo --
  o chamador deve usar o emoji de fallback já presente em ASSETS["icon"].

No modo de demonstração (ARGOS_DEMO_MODE=true) nenhum logo remoto é usado:
a função devolve None e o chamador exibe o emoji de fallback, sem rede.
"""

from functools import lru_cache
from typing import Optional

from core.demo_mode import is_demo_mode


# ==========================================================
# Criptomoedas
# ==========================================================
CRYPTO_LOGO_BASE_URL = "https://assets.coincap.io/assets/icons/{symbol}@2x.png"


# Tickers do Yahoo com sufixo numérico de desambiguação (ex.: UNI7083-USD).
CRYPTO_SYMBOL_OVERRIDES = {"UNI7083-USD": "uni"}


def _crypto_symbol_from_ticker(ticker: str) -> str:
    """Extrai o símbolo da moeda a partir do ticker (ex: 'BTC-USD' -> 'btc')."""
    override = CRYPTO_SYMBOL_OVERRIDES.get(ticker.upper())
    return override or ticker.split("-")[0].lower()


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
    # A fonte guarda o logo da Embraer pelo ticker anterior (EMBR3).
    "EMBJ3.SA": "https://images.financialmodelingprep.com/symbol/EMBR3.SA.png",
}


# Tickers sem logo utilizável na fonte, verificados em 24/10/2026 com todos os
# ativos do catálogo: imagem em branco (V, QQQ), imagem genérica igual para
# emissores diferentes (KNRI11, BTLG11) ou endereço inexistente (404). Para
# eles a interface mostra o ícone da classe: o Streamlit remove o atributo
# `onerror` do HTML, então uma imagem quebrada não cai sozinha no ícone.
UNAVAILABLE_LOGOS = {
    "V", "QQQ",
    "KNRI11.SA", "BTLG11.SA",
    "MXRF11.SA", "HGLG11.SA", "KNCR11.SA", "HGRU11.SA", "VISC11.SA",
    "BOVA11.SA", "IVVB11.SA", "DIVO11.SA", "GOLD11.SA", "HASH11.SA",
    "AXIA3.SA",
}


@lru_cache(maxsize=256)
def _remote_logo_url(ticker: str, group: str) -> Optional[str]:
    ticker_upper = ticker.upper()

    if ticker_upper in UNAVAILABLE_LOGOS:
        return None

    if ticker_upper in SPECIAL_LOGO_MAP:
        return SPECIAL_LOGO_MAP[ticker_upper]

    group_normalized = (group or "").lower()

    # ETFs da B3 classificados pela exposição (cripto, ouro) usam a fonte de ações.
    if ticker_upper.endswith(".SA"):
        return STOCK_LOGO_BASE_URL.format(ticker=ticker_upper)

    if group_normalized == "crypto":
        symbol = _crypto_symbol_from_ticker(ticker)
        return CRYPTO_LOGO_BASE_URL.format(symbol=symbol)

    if group_normalized in STOCK_LIKE_GROUPS:
        return STOCK_LOGO_BASE_URL.format(ticker=ticker_upper)

    # indexes, forex, commodities, treasury/rates: sem fonte confiável
    return None


def get_asset_logo_url(ticker: str, group: str) -> Optional[str]:
    """
    Retorna a URL do logo/ícone do ativo, ou None se não houver uma
    fonte confiável para esse grupo/ticker. Nesse caso, o chamador deve
    usar o emoji de fallback do próprio ativo (campo "icon" em ASSETS).

    No modo de demonstração devolve sempre None (sem imagens remotas).
    """
    if is_demo_mode():
        return None
    return _remote_logo_url(ticker, group)


# Compatibilidade com quem consultava/limpava o cache da função original.
get_asset_logo_url.cache_clear = _remote_logo_url.cache_clear
get_asset_logo_url.cache_info = _remote_logo_url.cache_info