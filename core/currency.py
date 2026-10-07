"""Moeda e unidade de cotação de um ticker, a partir do sufixo."""

from dataclasses import dataclass

YIELD_TICKERS = {"^IRX", "^FVX", "^TNX", "^TYX"}

# sufixo -> (código, prefixo exibido, nome)
SUFFIX_CURRENCY = {
    ".SA": ("BRL", "R$ ", "Real (BRL)"),
    ".SW": ("CHF", "CHF ", "Franco suíço (CHF)"),
    ".PA": ("EUR", "€ ", "Euro (EUR)"),
    ".DE": ("EUR", "€ ", "Euro (EUR)"),
    ".CO": ("DKK", "DKK ", "Coroa dinamarquesa (DKK)"),
    ".KS": ("KRW", "₩ ", "Won sul-coreano (KRW)"),
    ".HK": ("HKD", "HK$ ", "Dólar de Hong Kong (HKD)"),
    ".T": ("JPY", "¥ ", "Iene (JPY)"),
}


@dataclass(frozen=True)
class CurrencyInfo:
    code: str      # BRL, USD, EUR..., PTS, FX, PCT
    prefix: str    # texto antes do número ("" quando não se aplica)
    label: str     # nome legível da unidade
    kind: str      # "price" | "points" | "rate" | "fx"


def currency_info(ticker) -> CurrencyInfo:
    t = str(ticker or "").strip().upper()

    if t in YIELD_TICKERS:
        return CurrencyInfo("PCT", "", "% a.a. (taxa)", "rate")

    if t.startswith("^") or t.endswith(".SS"):
        return CurrencyInfo("PTS", "Pts ", "Pontos", "points")

    if t.endswith("=X"):
        return CurrencyInfo("FX", "", "Taxa de câmbio", "fx")

    for suffix, (code, prefix, label) in SUFFIX_CURRENCY.items():
        if t.endswith(suffix):
            return CurrencyInfo(code, prefix, label, "price")

    return CurrencyInfo("USD", "US$ ", "Dólar (USD)", "price")


def is_crypto(ticker) -> bool:
    return str(ticker or "").strip().upper().endswith("-USD")