"""
data_fetcher.py
Obtiene datos históricos y titulares de activos usando yfinance.
Abstrae el acceso a datos para facilitar el cambio de proveedor en el futuro.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


def get_historical_data(ticker: str, months: int = 6) -> Optional[pd.DataFrame]:
    """
    Obtiene datos históricos de precios para un ticker.
    
    Args:
        ticker: Símbolo del activo (ej: AAPL).
        months: Cantidad de meses de historia (por defecto 6).
    
    Returns:
        DataFrame con columnas Open, High, Low, Close, Volume, o None si falla.
    """
    try:
        end = datetime.now()
        start = end - timedelta(days=months * 30)
        data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
        if data.empty or len(data) < 2:
            return None
        # yfinance puede devolver MultiIndex en columnas; normalizamos
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return None


def get_news_headlines(ticker: str, max_headlines: int = 10) -> list[str]:
    """
    Obtiene titulares recientes relacionados con el ticker usando yfinance.
    
    Args:
        ticker: Símbolo del activo.
        max_headlines: Número máximo de titulares a devolver.
    
    Returns:
        Lista de cadenas con titulares; vacía si no hay datos o falla.
    """
    try:
        obj = yf.Ticker(ticker)
        news = obj.news
        if not news:
            return []
        headlines = []
        for item in news[:max_headlines]:
            title = item.get("title") or item.get("link", "")
            if title and isinstance(title, str):
                headlines.append(title)
        return headlines
    except Exception:
        return []


def validate_ticker(ticker: str) -> bool:
    """
    Comprueba si el ticker existe y tiene datos descargables.
    
    Args:
        ticker: Símbolo a validar.
    
    Returns:
        True si el ticker parece válido y tiene datos.
    """
    if not ticker or not isinstance(ticker, str):
        return False
    ticker = ticker.strip().upper()
    if not ticker:
        return False
    data = get_historical_data(ticker, months=1)
    return data is not None and not data.empty
