"""Signal generation based on MA crossover + ATR filter."""

import pandas as pd
import numpy as np


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Generate BUY/SELL signals.

    BUY:  Close > SMA_100 AND Close crosses above SMA_20 AND ATR_Active
    SELL: Close < SMA_100 AND Close crosses below SMA_20 AND ATR_Active
    """
    df = df.copy()

    # Previous bar's position relative to SMA_20
    prev_close = df["Close"].shift(1)
    prev_sma20 = df["SMA_20"].shift(1)

    # Cross above SMA_20: previous close was below, current close is above
    cross_above = (prev_close < prev_sma20) & (df["Close"] > df["SMA_20"])
    # Cross below SMA_20: previous close was above, current close is below
    cross_below = (prev_close > prev_sma20) & (df["Close"] < df["SMA_20"])

    # Trend filter
    above_100 = df["Close"] > df["SMA_100"]
    below_100 = df["Close"] < df["SMA_100"]

    # ATR filter
    atr_ok = df["ATR_Active"]

    # Signals
    df["Buy_Signal"] = cross_above & above_100 & atr_ok
    df["Sell_Signal"] = cross_below & below_100 & atr_ok

    return df
