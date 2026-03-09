#!/usr/bin/env python3
"""
Forex Swing Trading Strategy Backtest
Based on: https://tradethatswing.com/moving-average-and-atr-forex-swing-trading-strategy/

Rules:
- Long: price > 100 SMA, candle body was below 20 SMA, daily close above 20 SMA
- Short: price < 100 SMA, candle body was above 20 SMA, daily close below 20 SMA
- Stop loss: low of trigger candle (long) / high of trigger candle (short)
- Exit: daily close on opposite side of 20 SMA
- ATR filter: only trade when ATR(14) > threshold

Data sources (in order of preference):
1. CSV files in data/ subfolder (e.g., data/EURUSD.csv with Date,Open,High,Low,Close)
2. Yahoo Finance API (requires yfinance + internet access)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# ── Configuration ──────────────────────────────────────────────
FAST_MA = 20
SLOW_MA = 100
ATR_PERIOD = 14
ATR_THRESHOLD = 0.0  # 0 = disabled; set per pair to filter chop
PAIRS = {
    "EURUSD=X": "EUR/USD",
    "GBPUSD=X": "GBP/USD",
    "JPY=X":    "USD/JPY",
    "AUDJPY=X": "AUD/JPY",
}
LOOKBACK_DAYS = 365 + SLOW_MA + 50  # extra bars for SMA warmup
DATA_DIR = Path(__file__).parent / "data"


def load_csv_data(pair_name):
    """Try to load data from CSV file in data/ directory."""
    csv_names = [
        pair_name.replace("/", ""),      # EURUSD
        pair_name.replace("/", "_"),      # EUR_USD
        pair_name,                        # EUR/USD
    ]
    for name in csv_names:
        path = DATA_DIR / f"{name}.csv"
        if path.exists():
            df = pd.read_csv(path, parse_dates=["Date"], index_col="Date")
            df = df[["Open", "High", "Low", "Close"]].dropna()
            return df
    return None


def fetch_yfinance_data(symbol, days):
    """Download daily OHLC data from Yahoo Finance."""
    try:
        import yfinance as yf
        end = datetime.now()
        start = end - timedelta(days=days)
        df = yf.download(symbol, start=start, end=end, interval="1d", progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close"]].dropna()
        if len(df) > 0:
            return df
    except Exception:
        pass
    return None


def get_data(symbol, pair_name, days):
    """Get data from CSV, Yahoo Finance, or generate sample data."""
    # 1. Try CSV
    df = load_csv_data(pair_name)
    if df is not None and len(df) > 0:
        print(f"  [CSV] Loaded {len(df)} bars from data/{pair_name.replace('/', '')}.csv")
        return df

    # 2. Try Yahoo Finance
    df = fetch_yfinance_data(symbol, days)
    if df is not None and len(df) > 0:
        print(f"  [YF] Downloaded {len(df)} bars from Yahoo Finance")
        return df

    # No data available
    print(f"  No data available. Provide CSV in data/ folder or ensure Yahoo Finance is accessible.")
    return None


def compute_indicators(df):
    """Add SMA and ATR columns."""
    df = df.copy()
    df["SMA_fast"] = df["Close"].rolling(FAST_MA).mean()
    df["SMA_slow"] = df["Close"].rolling(SLOW_MA).mean()

    # ATR calculation
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift(1)).abs()
    low_close = (df["Low"] - df["Close"].shift(1)).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(ATR_PERIOD).mean()

    return df.dropna()


def run_backtest(df, pair_name, atr_threshold=ATR_THRESHOLD):
    """Simulate trades and return list of trade results."""
    trades = []
    position = 0  # 1=long, -1=short, 0=flat
    entry_price = 0.0
    stop_loss = 0.0
    entry_date = None
    was_below = False
    was_above = False

    # Only use the last ~1 year of data for actual trading (after warmup)
    cutoff = df.index[-1] - timedelta(days=365)
    trade_start_idx = df.index.searchsorted(cutoff)

    for i in range(1, len(df)):
        row = df.iloc[i]
        date = df.index[i]
        o, h, l, c = row["Open"], row["High"], row["Low"], row["Close"]
        sma_fast = row["SMA_fast"]
        sma_slow = row["SMA_slow"]
        atr = row["ATR"]

        # Track candle body position relative to 20 SMA
        if o < sma_fast and c < sma_fast:
            was_below = True
        if o > sma_fast and c > sma_fast:
            was_above = True

        # Only generate signals in the trading window
        if i < trade_start_idx:
            continue

        atr_ok = atr_threshold == 0 or atr > atr_threshold

        # Check stop loss hits first (intrabar)
        if position == 1 and l <= stop_loss:
            pnl = stop_loss - entry_price
            trades.append({
                "pair": pair_name, "direction": "LONG", "entry_date": entry_date,
                "exit_date": date, "entry": entry_price, "exit": stop_loss,
                "pnl": pnl, "exit_reason": "SL",
            })
            position = 0
            was_below = False
            was_above = False
            continue

        if position == -1 and h >= stop_loss:
            pnl = entry_price - stop_loss
            trades.append({
                "pair": pair_name, "direction": "SHORT", "entry_date": entry_date,
                "exit_date": date, "entry": entry_price, "exit": stop_loss,
                "pnl": pnl, "exit_reason": "SL",
            })
            position = 0
            was_below = False
            was_above = False
            continue

        # Check SMA cross exits
        if position == 1 and c < sma_fast:
            pnl = c - entry_price
            trades.append({
                "pair": pair_name, "direction": "LONG", "entry_date": entry_date,
                "exit_date": date, "entry": entry_price, "exit": c,
                "pnl": pnl, "exit_reason": "SMA Cross",
            })
            position = 0
            was_below = True  # just closed below
            was_above = False

        if position == -1 and c > sma_fast:
            pnl = entry_price - c
            trades.append({
                "pair": pair_name, "direction": "SHORT", "entry_date": entry_date,
                "exit_date": date, "entry": entry_price, "exit": c,
                "pnl": pnl, "exit_reason": "SMA Cross",
            })
            position = 0
            was_above = True  # just closed above
            was_below = False

        # Entry signals (only when flat)
        if position == 0:
            # Long entry
            if c > sma_slow and was_below and c > sma_fast and atr_ok:
                position = 1
                entry_price = c
                stop_loss = l
                entry_date = date
                was_below = False
                was_above = False

            # Short entry
            elif c < sma_slow and was_above and c < sma_fast and atr_ok:
                position = -1
                entry_price = c
                stop_loss = h
                entry_date = date
                was_below = False
                was_above = False

    # Close any open position at end
    if position != 0:
        last = df.iloc[-1]
        c = last["Close"]
        pnl = (c - entry_price) if position == 1 else (entry_price - c)
        trades.append({
            "pair": pair_name, "direction": "LONG" if position == 1 else "SHORT",
            "entry_date": entry_date, "exit_date": df.index[-1],
            "entry": entry_price, "exit": c, "pnl": pnl, "exit_reason": "End",
        })

    return trades


def print_results(all_trades):
    """Print per-pair and overall summary."""
    if not all_trades:
        print("\nNo trades generated.")
        return

    df = pd.DataFrame(all_trades)
    df["duration"] = (pd.to_datetime(df["exit_date"]) - pd.to_datetime(df["entry_date"])).dt.days

    print("\n" + "=" * 80)
    print("FOREX SWING TRADING BACKTEST RESULTS")
    print("Strategy: 20/100 SMA + ATR Filter | Daily Timeframe | 1 Year")
    print("=" * 80)

    summary_rows = []

    for pair in df["pair"].unique():
        pair_df = df[df["pair"] == pair].copy()
        total = len(pair_df)
        wins = len(pair_df[pair_df["pnl"] > 0])
        losses = len(pair_df[pair_df["pnl"] <= 0])
        win_rate = (wins / total * 100) if total > 0 else 0
        net_pnl = pair_df["pnl"].sum()
        gross_profit = pair_df[pair_df["pnl"] > 0]["pnl"].sum()
        gross_loss = abs(pair_df[pair_df["pnl"] <= 0]["pnl"].sum())
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf")
        avg_duration = pair_df["duration"].mean()

        # Max drawdown (cumulative P&L)
        cum_pnl = pair_df["pnl"].cumsum()
        running_max = cum_pnl.cummax()
        drawdown = cum_pnl - running_max
        max_dd = drawdown.min()

        # Determine pip multiplier for display
        is_jpy = "JPY" in pair
        pip_mult = 100 if is_jpy else 10000

        print(f"\n{'─' * 50}")
        print(f"  {pair}")
        print(f"{'─' * 50}")
        print(f"  Total Trades:    {total}")
        print(f"  Wins / Losses:   {wins} / {losses}")
        print(f"  Win Rate:        {win_rate:.1f}%")
        print(f"  Net P&L:         {net_pnl:.5f} ({net_pnl * pip_mult:.1f} pips)")
        print(f"  Profit Factor:   {profit_factor:.2f}")
        print(f"  Max Drawdown:    {max_dd:.5f} ({max_dd * pip_mult:.1f} pips)")
        print(f"  Avg Duration:    {avg_duration:.1f} days")

        # Print individual trades
        print(f"\n  {'#':<3} {'Dir':<6} {'Entry Date':<12} {'Exit Date':<12} {'Entry':>10} {'Exit':>10} {'P&L (pips)':>10} {'Reason':<10}")
        for idx, (_, t) in enumerate(pair_df.iterrows(), 1):
            ed = pd.to_datetime(t["entry_date"]).strftime("%Y-%m-%d")
            xd = pd.to_datetime(t["exit_date"]).strftime("%Y-%m-%d")
            pnl_pips = t["pnl"] * pip_mult
            print(f"  {idx:<3} {t['direction']:<6} {ed:<12} {xd:<12} {t['entry']:>10.4f} {t['exit']:>10.4f} {pnl_pips:>+10.1f} {t['exit_reason']:<10}")

        summary_rows.append({
            "Pair": pair, "Trades": total, "Win Rate": f"{win_rate:.1f}%",
            "Net P&L (pips)": f"{net_pnl * pip_mult:+.1f}",
            "PF": f"{profit_factor:.2f}",
            "Max DD (pips)": f"{max_dd * pip_mult:.1f}",
            "Avg Days": f"{avg_duration:.1f}",
        })

    # Summary table
    print(f"\n{'=' * 80}")
    print("SUMMARY COMPARISON")
    print(f"{'=' * 80}")
    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))

    # Overall stats
    total_trades = len(df)
    total_wins = len(df[df["pnl"] > 0])
    overall_wr = total_wins / total_trades * 100 if total_trades > 0 else 0
    print(f"\nOverall: {total_trades} trades, {overall_wr:.1f}% win rate")
    print()


def main():
    all_trades = []

    print("Forex Swing Trading Backtest")
    print(f"Settings: SMA({FAST_MA}/{SLOW_MA}), ATR({ATR_PERIOD}), Threshold={ATR_THRESHOLD}")
    print()

    for symbol, name in PAIRS.items():
        print(f"Loading {name}...")
        df = get_data(symbol, name, LOOKBACK_DAYS)
        if df is None or df.empty:
            print(f"  No data for {name}, skipping.")
            continue
        df = compute_indicators(df)
        start_date = df.index[-1] - timedelta(days=365)
        print(f"  Trading window: {start_date:%Y-%m-%d} to {df.index[-1]:%Y-%m-%d}")
        trades = run_backtest(df, name)
        print(f"  Found {len(trades)} trades")
        all_trades.extend(trades)

    print_results(all_trades)


if __name__ == "__main__":
    main()
