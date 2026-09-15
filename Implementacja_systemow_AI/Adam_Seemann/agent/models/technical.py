"""Technical analysis indicators and calculations."""

import numpy as np
import pandas as pd


def calculate_sma(prices: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).

    Args:
        prices: Series of closing prices
        window: Period for moving average (default 20)

    Returns:
        Series of SMA values
    """
    return prices.rolling(window=window).mean()


# ============================
# PREDEFINED SMA SHORTCUTS
# ============================

def sma12(prices: pd.Series) -> pd.Series:
    """SMA 12 — short-term trend indicator."""
    return calculate_sma(prices, window=12)

def sma26(prices: pd.Series) -> pd.Series:
    """SMA 26 — medium-term trend indicator."""
    return calculate_sma(prices, window=26)

def sma50(prices: pd.Series) -> pd.Series:
    """SMA 50 — mid-term trend indicator."""
    return calculate_sma(prices, window=50)

def sma200(prices: pd.Series) -> pd.Series:
    """SMA 200 — long-term trend indicator."""
    return calculate_sma(prices, window=200)


def calculate_ema(prices: pd.Series, window: int = 20, adjust: bool = False) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).

    Args:
        prices: Series of closing prices
        window: Period for moving average (default 20)
        adjust: Whether to use adjustment factor (default False)

    Returns:
        Series of EMA values
    """
    return prices.ewm(span=window, adjust=adjust).mean()


# ============================
# PREDEFINED EMA SHORTCUTS
# ============================

def ema12(prices: pd.Series) -> pd.Series:
    """EMA 12 — short-term trend indicator."""
    return calculate_ema(prices, window=12)

def ema26(prices: pd.Series) -> pd.Series:
    """EMA 26 — used in MACD."""
    return calculate_ema(prices, window=26)

def ema50(prices: pd.Series) -> pd.Series:
    """EMA 50 — medium-term trend indicator."""
    return calculate_ema(prices, window=50)

def ema200(prices: pd.Series) -> pd.Series:
    """EMA 200 — long-term trend indicator."""
    return calculate_ema(prices, window=200)



def calculate_macd(
    prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Args:
        prices: Series of closing prices
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line period (default 9)

    Returns:
        Tuple of (MACD line, Signal line, Histogram)
    """
    fast_ema = calculate_ema(prices, window=fast_period)
    slow_ema = calculate_ema(prices, window=slow_period)

    macd = fast_ema - slow_ema
    signal = calculate_ema(macd, window=signal_period)
    histogram = macd - signal

    return macd, signal, histogram


def calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).

    Args:
        prices: Series of closing prices
        window: Period for RSI (default 14)

    Returns:
        Series of RSI values (0-100)
    """
    delta = prices.diff()

    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    avg_gains = gains.rolling(window=window).mean()
    avg_losses = losses.rolling(window=window).mean()

    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_atr(
    ohlc: pd.DataFrame,
    window: int = 14,
) -> pd.Series:
    """
    Calculate Average True Range (ATR).

    Args:
        ohlc: DataFrame with 'high', 'low', 'close' columns
        window: Period for ATR (default 14)

    Returns:
        Series of ATR values
    """
    high = ohlc["high"]
    low = ohlc["low"]
    close = ohlc["close"]

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=window).mean()

    return atr


def calculate_bollinger_bands(
    prices: pd.Series,
    window: int = 20,
    num_std: float = 2.0,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands.

    Args:
        prices: Series of closing prices
        window: Period for bands (default 20)
        num_std: Number of standard deviations (default 2)

    Returns:
        Tuple of (Upper band, Middle band (SMA), Lower band)
    """
    middle = calculate_sma(prices, window=window)
    std = prices.rolling(window=window).std()

    upper = middle + (num_std * std)
    lower = middle - (num_std * std)

    return upper, middle, lower


def calculate_obv(prices: pd.Series, volume: pd.Series) -> pd.Series:
    """
    Calculate On-Balance Volume (OBV).

    Args:
        prices: Series of closing prices
        volume: Series of volumes

    Returns:
        Series of OBV values
    """
    obv = pd.Series(0.0, index=prices.index)

    for i in range(1, len(prices)):
        if prices.iloc[i] > prices.iloc[i - 1]:
            obv.iloc[i] = obv.iloc[i - 1] + volume.iloc[i]
        elif prices.iloc[i] < prices.iloc[i - 1]:
            obv.iloc[i] = obv.iloc[i - 1] - volume.iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i - 1]

    return obv


def calculate_ad(
    ohlc: pd.DataFrame,
) -> pd.Series:
    """
    Calculate Accumulation/Distribution (A/D) line.

    A/D measures the cumulative flow of money into and out of a security.
    It combines price and volume to assess the strength of buying/selling pressure.

    Args:
        ohlc: DataFrame with 'high', 'low', 'close', 'volume' columns

    Returns:
        Series of A/D values
    """
    high = ohlc["high"]
    low = ohlc["low"]
    close = ohlc["close"]
    volume = ohlc["volume"]

    high_low_diff = high - low
    high_low_diff = high_low_diff.replace(0, 1)  # Avoid division by zero

    mfm = ((close - low) - (high - close)) / high_low_diff
    mfv = mfm * volume

    ad = mfv.cumsum()

    return ad

def calculate_stochastic_oscillator(
    ohlc: pd.DataFrame,
    k_window: int = 14,
    d_window: int = 3,
) -> tuple[pd.Series, pd.Series]:
    """
    Calculate Stochastic Oscillator (%K and %D).

    STS mierzy pozycję ceny zamknięcia względem zakresu
    najwyższych i najniższych cen w danym okresie.

    Args:
        ohlc: DataFrame with 'high', 'low', 'close' columns
        k_window: Lookback period for %K (default 14)
        d_window: Smoothing period for %D (default 3)

    Returns:
        Tuple of (%K, %D) as Series
    """
    high = ohlc["high"]
    low = ohlc["low"]
    close = ohlc["close"]

    lowest_low = low.rolling(window=k_window).min()
    highest_high = high.rolling(window=k_window).max()

    # Avoid division by zero
    range_ = (highest_high - lowest_low).replace(0, np.nan)

    percent_k = ((close - lowest_low) / range_) * 100
    percent_d = percent_k.rolling(window=d_window).mean()

    return percent_k, percent_d
