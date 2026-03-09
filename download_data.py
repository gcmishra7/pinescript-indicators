"""Download daily forex data via yfinance."""

import os
import pandas as pd
import yfinance as yf
from config import PAIRS, DATA_START, BACKTEST_END, DATA_DIR


def download_all():
    os.makedirs(DATA_DIR, exist_ok=True)
    data = {}
    for name, ticker in PAIRS.items():
        print(f"Downloading {name} ({ticker})...")
        df = yf.download(ticker, start=DATA_START, end=BACKTEST_END, auto_adjust=True)
        if df.empty:
            print(f"  WARNING: No data for {name}")
            continue
        # Flatten multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.to_csv(os.path.join(DATA_DIR, f"{name}.csv"))
        data[name] = df
        print(f"  Got {len(df)} rows: {df.index[0].date()} to {df.index[-1].date()}")
    return data


def load_all():
    data = {}
    for name in PAIRS:
        path = os.path.join(DATA_DIR, f"{name}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path, index_col=0, parse_dates=True)
            data[name] = df
    return data


if __name__ == "__main__":
    download_all()
