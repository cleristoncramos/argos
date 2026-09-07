from typing import Optional

import pandas as pd
import streamlit as st
import yfinance as yf


def download_active_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
) -> Optional[pd.DataFrame]:
    """
    Normaliza os parâmetros públicos e delega o download à função cacheada.
    """
    normalized_symbol = str(symbol).strip().upper()
    normalized_start_date = str(start_date).strip()
    normalized_end_date = str(end_date).strip()
    normalized_interval = str(interval).strip().lower()

    if not normalized_symbol:
        return None

    return _download_active_data_cached(
        symbol=normalized_symbol,
        start_date=normalized_start_date,
        end_date=normalized_end_date,
        interval=normalized_interval,
    )


@st.cache_data(
    ttl=3600,
    show_spinner=False,
)
def _download_active_data_cached(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
) -> Optional[pd.DataFrame]:
    """
    Baixa dados históricos do Yahoo Finance para parâmetros já normalizados.

    Esta função é interna e cacheada. Seus parâmetros devem chegar
    normalizados para que chamadas equivalentes reutilizem a mesma entrada
    do cache.
    """
    try:
        ticker = yf.Ticker(symbol)

        try:
            info = ticker.info
        except Exception:
            info = {}

        has_identity = any(
            info.get(field)
            for field in [
                "shortName",
                "longName",
                "symbol",
                "exchange",
                "quoteType",
            ]
        )

        if not has_identity:
            return None

        df = ticker.history(
            start=start_date,
            end=end_date,
            interval=interval,
            auto_adjust=False,
        )

        required_columns = {
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        }

        if df.empty or not required_columns.issubset(df.columns):
            return None

        df = df.reset_index()

        if "Date" in df.columns:
            date_column = "Date"
        elif "Datetime" in df.columns:
            date_column = "Datetime"
        else:
            return None

        df = df.rename(
            columns={
                date_column: "Date",
            }
        )

        df["Date"] = pd.to_datetime(
            df["Date"],
        )

        if getattr(df["Date"].dt, "tz", None) is not None:
            df["Date"] = df["Date"].dt.tz_localize(
                None,
            )

        return df.sort_values(
            "Date",
        ).reset_index(
            drop=True,
        )

    except Exception:
        return None

def validate_data(df: pd.DataFrame) -> dict:
    """
    Gera indicadores básicos de qualidade do DataFrame baixado.
    """
    if df is None or df.empty:
        return {
            "total_rows": 0,
            "missing_values": {},
            "duplicate_dates": 0,
            "negative_close": 0,
            "has_data": False,
        }

    return {
        "total_rows": len(df),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_dates": (
            df["Date"].duplicated().sum()
            if "Date" in df.columns
            else 0
        ),
        "negative_close": (
            (df["Close"] < 0).sum()
            if "Close" in df.columns
            else 0
        ),
        "has_data": len(df) > 0,
    }