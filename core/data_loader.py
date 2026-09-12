from typing import Optional
import time
from datetime import datetime, timedelta

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
    Normaliza os parâmetros públicos, ajusta a data final e delega o download à função cacheada.
    """
    normalized_symbol = str(symbol).strip().upper()
    normalized_start_date = str(start_date).strip()
    
    # Adiciona 1 dia à data final para garantir que o Yahoo Finance inclua o último pregão
    try:
        end_dt = datetime.strptime(str(end_date).strip(), "%Y-%m-%d")
        normalized_end_date = (end_dt + timedelta(days=1)).strftime("%Y-%m-%d")
    except ValueError:
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
    max_retries: int = 3,
) -> Optional[pd.DataFrame]:
    """
    Baixa dados históricos do Yahoo Finance para parâmetros já normalizados.
    Implementa retries automáticos e limpeza de colunas MultiIndex.
    """
    for attempt in range(max_retries):
        try:
            ticker = yf.Ticker(symbol)

            # O download direto de history é mais estável que chamar .info() antes
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=False,
            )

            # Se vier vazio, aguarda e tenta novamente (evita bloqueios temporários)
            if df is None or df.empty:
                if attempt < max_retries - 1:
                    time.sleep(1.5)
                    continue
                else:
                    return None

            # Corrige bug do yfinance que retorna MultiIndex em versões recentes
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0] for col in df.columns]

            required_columns = {
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            }

            if not required_columns.issubset(df.columns):
                if attempt < max_retries - 1:
                    time.sleep(1.5)
                    continue
                else:
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
            if attempt < max_retries - 1:
                time.sleep(1.5)
                continue
            else:
                return None
                
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