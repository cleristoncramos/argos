import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Optional


def download_active_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d"
) -> Optional[pd.DataFrame]:
    """
    Baixa dados históricos de um ativo usando yfinance.
    
    Parâmetros:
    - symbol: Símbolo do ativo (ex: BTC-USD, AAPL, USD=BRL)
    - start_date: Data inicial no formato YYYY-MM-DD
    - end_date: Data final no formato YYYY-MM-DD
    - interval: Intervalo dos dados (1d, 1wk, 1mo)
    
    Retorna:
    - DataFrame com os dados ou None em caso de erro
    """
    try:
        # Criar ticker do ativo
        ticker = yf.Ticker(symbol)
        
        # Baixar histórico
        df = ticker.history(
            start=start_date,
            end=end_date,
            interval=interval
        )
        
        # Verificar se há dados
        if df.empty:
            print(f"Nenhum dado encontrado para {symbol} no período especificado.")
            return None
        
        # Resetar índice para ter 'Date' como coluna
        df = df.reset_index()
        
        # Garantir que Date seja datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        return df
        
    except Exception as e:
        print(f"Erro ao baixar dados: {e}")
        return None


def validate_data(df: pd.DataFrame) -> dict:
    """
    Valida a qualidade dos dados.
    
    Retorna um dicionário com informações sobre:
    - Valores ausentes
    - Datas duplicadas
    - Valores negativos ou anômalos
    """
    validation = {
        'total_rows': len(df),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_dates': df['Date'].duplicated().sum(),
        'negative_close': (df['Close'] < 0).sum() if 'Close' in df.columns else 0,
        'has_data': len(df) > 0
    }
    return validation