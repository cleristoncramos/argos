import yfinance as yf
import pandas as pd
import streamlit as st
from typing import Optional

@st.cache_data(ttl=3600, show_spinner=False)

def download_active_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d"
) -> Optional[pd.DataFrame]:
    """
    Baixa dados históricos e valida se o símbolo representa
    um ativo reconhecido pelo Yahoo Finance.
    """
    try:
        symbol = symbol.strip().upper()

        if not symbol:
            return None

        ticker = yf.Ticker(symbol)

        # Verifica se o ativo possui informações cadastrais.
        # Alguns ativos podem não fornecer todos os campos.
        try:
            info = ticker.info
        except Exception:
            info = {}

        # Indicadores mínimos de que o símbolo foi reconhecido.
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

        # Se o Yahoo não conseguir identificar o ativo,
        # não prossegue com o download.
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

        df = df.rename(columns={date_column: "Date"})
        df["Date"] = pd.to_datetime(df["Date"])

        if getattr(df["Date"].dt, "tz", None) is not None:
            df["Date"] = df["Date"].dt.tz_localize(None)

        df = df.sort_values("Date").reset_index(drop=True)

        return df

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