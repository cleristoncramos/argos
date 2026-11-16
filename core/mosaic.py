"""
Mosaico de ativos da página inicial (revisto em 16/11/2026).

- Uma logomarca para cada um dos 148 ativos do catálogo:
  - logo próprio do ativo (CoinCap para criptomoedas e Financial Modeling Prep para
    ações, ETFs, REITs e FIIs), como em core/asset_logos.py;
  - fundos e ETFs sem logo próprio na fonte mostram a logomarca da gestora ou do
    emissor (por exemplo, iShares no BOVA11 e Pátria no HGLG11);
  - índices, câmbio e taxas do Tesouro mostram a bandeira do país (ou as duas
    bandeiras do par de moedas) com um código curto;
  - commodities e o HASH11 mostram um emblema desenhado: símbolo químico nos metais
    e código do contrato nos demais.
- Categorias para filtrar o mosaico e a ordem das faixas animadas.
- Clique numa logomarca: Análise Individual do ativo com 5 anos e frequência mensal.

No modo de demonstração nenhuma imagem remota é usada: todos os ativos mostram o
emblema desenhado, sem rede. Sem Streamlit.
"""

from __future__ import annotations

from typing import Iterable, Mapping, Optional

from core.asset_logos import STOCK_LOGO_BASE_URL, get_asset_logo_url
from core.assets import ASSET_GROUPS
from core.demo_mode import is_demo_mode

# Destino do clique numa logomarca (pedido do orientador, 16/11/2026).
TARGET_PERIOD = "5 anos"
TARGET_FREQUENCY = "Mensal"

FLAG_URL = "https://flagcdn.com/w80/{code}.png"

# Fundos e ETFs sem logo próprio utilizável: logomarca da gestora ou do emissor,
# pelo ticker dela na mesma fonte. Os logos brancos ganham fundo escuro.
ISSUER_LOGOS: dict[str, tuple[str, str, Optional[str]]] = {
    # ticker: (ticker do logo na fonte, quem é, fundo para logo branco)
    "V": ("V", "Visa", "#1A1F71"),
    "QQQ": ("QQQ", "Invesco", "#14213D"),
    "BOVA11.SA": ("SHV", "iShares (BlackRock)", None),
    "IVVB11.SA": ("SHV", "iShares (BlackRock)", None),
    "DIVO11.SA": ("ITUB4.SA", "It Now (Itaú)", None),
    "KNRI11.SA": ("ITUB4.SA", "Kinea (Itaú)", None),
    "KNCR11.SA": ("ITUB4.SA", "Kinea (Itaú)", None),
    "MXRF11.SA": ("XP", "XP Asset", "#111111"),
    "GOLD11.SA": ("XP", "Trend (XP)", "#111111"),
    "HGLG11.SA": ("PAX", "Pátria", None),
    "HGRU11.SA": ("PAX", "Pátria", None),
    "BTLG11.SA": ("BPAC11.SA", "BTG Pactual", None),
    "VISC11.SA": ("VINP", "Vinci", None),
    "AXIA3.SA": ("ELET3.SA", "Eletrobras, hoje Axia Energia", None),
    "BIL": ("BIL", "SPDR", None),
    "SHV": ("SHV", "iShares (BlackRock)", None),
    "VGSH": ("VGSH", "Vanguard", None),
}

# Índices e taxas: país do mercado e código curto.
INDEX_FLAGS: dict[str, tuple[str, str]] = {
    "^BVSP": ("br", "IBOV"),
    "^GSPC": ("us", "SPX"),
    "^IXIC": ("us", "COMP"),
    "^DJI": ("us", "DJI"),
    "^RUT": ("us", "RUT"),
    "^VIX": ("us", "VIX"),
    "^FTSE": ("gb", "UKX"),
    "^GDAXI": ("de", "DAX"),
    "^FCHI": ("fr", "CAC"),
    "^N225": ("jp", "N225"),
    "^HSI": ("hk", "HSI"),
    "000001.SS": ("cn", "SSE"),
    "^IRX": ("us", "13S"),
    "^FVX": ("us", "5A"),
    "^TNX": ("us", "10A"),
    "^TYX": ("us", "30A"),
}

# Moeda -> bandeira (flagcdn usa "eu" para a União Europeia).
CURRENCY_FLAGS = {
    "USD": "us", "BRL": "br", "EUR": "eu", "GBP": "gb", "JPY": "jp",
    "CHF": "ch", "AUD": "au", "CAD": "ca", "CNY": "cn",
}

# Emblemas desenhados: texto e cor de fundo.
EMBLEMS: dict[str, tuple[str, str]] = {
    "GC=F": ("Au", "#B8901F"),
    "SI=F": ("Ag", "#8A949E"),
    "HG=F": ("Cu", "#B06A3B"),
    "PL=F": ("Pt", "#6B7785"),
    "CL=F": ("WTI", "#1F2937"),
    "BZ=F": ("BRENT", "#334155"),
    "NG=F": ("NG", "#1E3A5F"),
    "ZS=F": ("ZS", "#5B7B2A"),
    "ZC=F": ("ZC", "#B7871A"),
    "ZW=F": ("ZW", "#A47E3B"),
    "KC=F": ("KC", "#6F4E37"),
    "CC=F": ("CC", "#7B3F00"),
    "SB=F": ("SB", "#7C8B99"),
    "CT=F": ("CT", "#7D8F69"),
    "HASH11.SA": ("HASH", "#111111"),
}

# Categorias do filtro, na ordem dos botões.
CATEGORIES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("acoes", "Ações", ("br_stocks", "us_stocks", "europe_stocks", "asia_stocks")),
    ("cripto", "Cripto", ("crypto",)),
    ("etfs", "ETFs", ("equity_etfs", "fixed_income_etfs")),
    ("imobiliario", "Imobiliário", ("reits", "brazil_fiis")),
    ("indices", "Índices", ("indexes",)),
    ("cambio", "Câmbio", ("forex",)),
    ("commodities", "Commodities", ("commodities",)),
    ("juros", "Juros", ("treasury",)),
)
CATEGORY_OF_GROUP = {group: key for key, _, groups in CATEGORIES for group in groups}
GROUP_NAMES = {g["key"]: g["label"].split(" ", 1)[-1] for g in ASSET_GROUPS}


def monogram(ticker: str) -> str:
    """Até 4 caracteres do ticker, sem prefixos e sufixos de bolsa."""
    core = ticker.lstrip("^").split(".")[0].split("-")[0].split("=")[0]
    return (core or ticker)[:4].upper()


def _emblem(text: str, color: str) -> dict:
    return {"kind": "mark", "text": text, "bg": color}


def logo_spec(asset: Mapping[str, str], demo: Optional[bool] = None) -> dict:
    """Como desenhar a logomarca de um ativo no mosaico."""
    demo = is_demo_mode() if demo is None else demo
    ticker = str(asset["ticker"]).upper()
    color = asset.get("category_color", "#475569")
    fallback = monogram(ticker)
    if demo:
        text, bg = EMBLEMS.get(ticker, (fallback, color))
        return _emblem(text, bg)
    if ticker in EMBLEMS:
        return _emblem(*EMBLEMS[ticker])
    if ticker in ISSUER_LOGOS:
        symbol, issuer, background = ISSUER_LOGOS[ticker]
        own = symbol == ticker
        return {
            "kind": "img",
            "src": STOCK_LOGO_BASE_URL.format(ticker=symbol),
            "bg": background or "#FFFFFF",
            "note": "" if own else f"Logomarca da gestora ou emissora: {issuer}",
            "fallback": fallback,
        }
    if ticker in INDEX_FLAGS:
        code, tag = INDEX_FLAGS[ticker]
        return {"kind": "flags", "src": [FLAG_URL.format(code=code)], "tag": tag, "fallback": fallback}
    if asset.get("group") == "forex":
        pair = ticker.split("=")[0]
        flags = [CURRENCY_FLAGS.get(pair[:3]), CURRENCY_FLAGS.get(pair[3:6])]
        if all(flags):
            return {"kind": "flags", "src": [FLAG_URL.format(code=c) for c in flags],
                    "tag": f"{pair[:3]}/{pair[3:6]}", "fallback": fallback}
    url = get_asset_logo_url(ticker, asset.get("group", ""))
    if url:
        return {"kind": "img", "src": url, "bg": "#FFFFFF", "note": "", "fallback": fallback}
    return _emblem(fallback, color)


def interleave_by_class(assets: Iterable[Mapping[str, str]]) -> list:
    """Alterna as classes para que cada faixa misture tipos de ativo."""
    buckets: dict[str, list] = {}
    for asset in assets:
        buckets.setdefault(asset["class"], []).append(asset)
    queues = list(buckets.values())
    mixed = []
    while any(queues):
        for queue in queues:
            if queue:
                mixed.append(queue.pop(0))
    return mixed


def mosaic_data(assets: Iterable[Mapping[str, str]], lanes: int = 4, demo: Optional[bool] = None) -> dict:
    """Dados do componente: peças (na ordem das faixas), categorias e número de faixas."""
    ordered = interleave_by_class(list(assets))
    tiles = [
        {
            "t": a["ticker"],
            "n": a["name"],
            "g": GROUP_NAMES.get(a.get("group", ""), a.get("class", "")),
            "cat": CATEGORY_OF_GROUP.get(a.get("group", ""), "outros"),
            "c": a.get("category_color", "#475569"),
            "lane": index % lanes,
            "logo": logo_spec(a, demo),
        }
        for index, a in enumerate(ordered)
    ]
    counts = {key: sum(1 for t in tiles if t["cat"] == key) for key, _, _ in CATEGORIES}
    categories = [{"key": "todos", "label": "Todos", "count": len(tiles)}] + [
        {"key": key, "label": label, "count": counts[key]} for key, label, _ in CATEGORIES if counts[key]
    ]
    return {"tiles": tiles, "categories": categories, "lanes": lanes,
            "period": TARGET_PERIOD, "frequency": TARGET_FREQUENCY}
