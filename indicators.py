"""
indicators.py
Cálculo de indicadores técnicos a partir de series de precios.
"""

import pandas as pd
import numpy as np
from typing import Optional


def moving_average(series: pd.Series, window: int) -> Optional[float]:
    """
    Calcula la media móvil simple sobre los últimos 'window' períodos.
    
    Args:
        series: Serie de precios (ej: cierre).
        window: Ventana en períodos (ej: 20 o 50).
    
    Returns:
        Valor de la media móvil en el último período, o None si no hay datos suficientes.
    """
    if series is None or len(series) < window:
        return None
    return float(series.rolling(window=window).mean().iloc[-1])


def rsi_simple(series: pd.Series, period: int = 14) -> Optional[float]:
    """
    RSI simple (Relative Strength Index) basado en ganancias/pérdidas promedio.
    
    Args:
        series: Serie de precios de cierre.
        period: Período típico del RSI (por defecto 14).
    
    Returns:
        Valor del RSI entre 0 y 100, o None si no hay datos suficientes.
    """
    if series is None or len(series) < period + 1:
        return None
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean().iloc[-1]
    avg_loss = loss.rolling(window=period).mean().iloc[-1]
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return float(round(rsi, 2))


def volatility_returns(series: pd.Series, annualize: bool = True) -> Optional[float]:
    """
    Volatilidad como desviación estándar de los retornos.
    Por defecto anualizada (asumiendo ~252 días de trading).
    
    Args:
        series: Serie de precios de cierre.
        annualize: Si True, multiplica por sqrt(252) para volatilidad anual.
    
    Returns:
        Volatilidad (decimal, ej: 0.20 = 20%), o None.
    """
    if series is None or len(series) < 2:
        return None
    returns = series.pct_change().dropna()
    if returns.empty:
        return None
    vol = returns.std()
    if annualize:
        vol = vol * np.sqrt(252)
    return float(round(vol, 4))


def compute_all_indicators(prices: pd.DataFrame) -> dict:
    """
    Calcula todos los indicadores requeridos a partir del DataFrame de precios.
    Espera al menos una columna 'Close' (o la primera columna numérica como cierre).
    
    Args:
        prices: DataFrame con al menos una columna de cierre.
    
    Returns:
        Diccionario con ma_20, ma_50, rsi, volatility y último precio.
    """
    result = {
        "ma_20": None,
        "ma_50": None,
        "rsi": None,
        "volatility": None,
        "last_close": None,
    }
    if prices is None or prices.empty:
        return result
    close = prices["Close"] if "Close" in prices.columns else prices.iloc[:, 0]
    result["last_close"] = float(close.iloc[-1])
    result["ma_20"] = moving_average(close, 20)
    result["ma_50"] = moving_average(close, 50)
    result["rsi"] = rsi_simple(close, 14)
    result["volatility"] = volatility_returns(close, True)
    return result
