"""Indicator calculations: SMA and ATR."""

import pandas as pd
import numpy as np
from config import SMA_FAST, SMA_SLOW, ATR_PERIOD, ATR_THRESHOLD_LOOKBACK, ATR_THRESHOLD_PERCENTILE


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add SMA, ATR, and ATR threshold columns to dataframe."""
    df = df.copy()

    # Simple Moving Averages
    df["SMA_20"] = df["Close"].rolling(SMA_FAST).mean()
    df["SMA_100"] = df["Close"].rolling(SMA_SLOW).mean()

    # ATR (Average True Range)
    high = df["High"]
    low = df["Low"]
    close_prev = df["Close"].shift(1)
    tr = pd.concat([
        high - low,
        (high - close_prev).abs(),
        (low - close_prev).abs(),
    ], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(ATR_PERIOD).mean()

    # ATR threshold: rolling median over lookback period
    df["ATR_Threshold"] = df["ATR"].rolling(ATR_THRESHOLD_LOOKBACK, min_periods=ATR_PERIOD).quantile(ATR_THRESHOLD_PERCENTILE)

    # ATR filter: True when volatility is sufficient
    df["ATR_Active"] = df["ATR"] > df["ATR_Threshold"]

    return df
