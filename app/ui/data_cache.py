"""
Cache dos downloads de dados históricos (camada de interface).

O `core/data_loader.py` é puro; aqui as funções de busca recebem o
`st.cache_data` e são injetadas em `download_active_data`. As páginas usam
este módulo, e não o do core, para aproveitar o cache entre execuções.
"""

from typing import Optional

import pandas as pd
import streamlit as st

from core import data_loader
from core.demo_mode import load_demo_frame


@st.cache_data(
    ttl=3600,
    max_entries=64,
    show_spinner=False,
)
def _cached_fetch(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
) -> pd.DataFrame:
    """Download cacheado por 1 hora. Falhas (DataUnavailable) não ficam em cache."""
    return data_loader.fetch_history(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
    )


@st.cache_data(
    ttl=3600,
    max_entries=16,
    show_spinner=False,
)
def _cached_demo(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str,
    directory: str,
) -> pd.DataFrame:
    """Leitura cacheada dos dados salvos (a pasta entra na chave do cache)."""
    return load_demo_frame(symbol, start_date, end_date, interval, directory)


def download_active_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
) -> Optional[pd.DataFrame]:
    """Mesmo contrato de `core.data_loader.download_active_data`, com cache."""
    return data_loader.download_active_data(
        symbol,
        start_date,
        end_date,
        interval,
        fetch=_cached_fetch,
        load_demo=_cached_demo,
    )


def clear_cache() -> None:
    """Esvazia o cache dos downloads (usado nos testes)."""
    _cached_fetch.clear()
    _cached_demo.clear()
