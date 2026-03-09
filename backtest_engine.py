"""Backtest engine: position management and P&L tracking."""

import pandas as pd
import numpy as np
from config import (
    INITIAL_CAPITAL, RISK_PER_TRADE, SPREAD_PIPS, BACKTEST_START,
    ATR_SL_MULTIPLIER_FOREX, ATR_SL_MULTIPLIER_ETF,
    MIN_SL_PCT_FOREX, MIN_SL_PCT_ETF, MAX_LEVERAGE,
    SL_COOLDOWN_BARS,
)

# Commodity/ETF tickers that are NOT forex
COMMODITY_TICKERS = {"GLD", "SLV", "USO", "GDX"}


def get_spread(pair: str, price: float) -> float:
    """Return estimated half-spread (slippage per side) in price units."""
    if pair in COMMODITY_TICKERS:
        return price * 0.0001  # ~1 bps per side for liquid ETFs
    if "JPY" in pair:
        return SPREAD_PIPS * 0.01 / 2
    return SPREAD_PIPS * 0.0001 / 2


def get_atr_sl_multiplier(pair: str) -> float:
    """Return ATR multiplier for stop placement based on instrument type."""
    if pair in COMMODITY_TICKERS:
        return ATR_SL_MULTIPLIER_ETF
    return ATR_SL_MULTIPLIER_FOREX


def get_min_sl_distance(pair: str, price: float) -> float:
    """Return minimum stop distance in price units."""
    if pair in COMMODITY_TICKERS:
        return price * MIN_SL_PCT_ETF
    return price * MIN_SL_PCT_FOREX


def run_backtest(df: pd.DataFrame, pair: str) -> dict:
    """Run backtest on a single pair. Returns trades list and equity curve."""

    # Filter to backtest period only (indicators already computed on full data)
    bt = df.loc[BACKTEST_START:].copy()

    trades = []
    equity = [INITIAL_CAPITAL]
    capital = INITIAL_CAPITAL
    position = None
    cooldown_until = -1  # bar index when cooldown expires

    for i in range(len(bt)):
        row = bt.iloc[i]
        date = bt.index[i]
        price = row["Close"]
        slip = get_spread(pair, price)

        # --- Check exits first if we have a position ---
        if position is not None:
            hit_sl = False
            hit_exit = False

            if position["direction"] == "LONG":
                if row["Low"] <= position["sl"]:
                    exit_price = position["sl"]
                    hit_sl = True
                elif row["Close"] < row["SMA_20"]:
                    exit_price = row["Close"] - slip
                    hit_exit = True

                if hit_sl or hit_exit:
                    pnl = (exit_price - position["entry_price"]) * position["size"]
                    capital += pnl
                    trades.append({
                        "pair": pair,
                        "direction": "LONG",
                        "entry_date": position["entry_date"],
                        "exit_date": date,
                        "entry_price": position["entry_price"],
                        "exit_price": exit_price,
                        "sl": position["sl"],
                        "size": position["size"],
                        "pnl": pnl,
                        "pnl_pct": pnl / INITIAL_CAPITAL * 100,
                        "exit_reason": "SL" if hit_sl else "SMA_Cross",
                    })
                    if hit_sl:
                        cooldown_until = i + SL_COOLDOWN_BARS
                    position = None

            elif position["direction"] == "SHORT":
                if row["High"] >= position["sl"]:
                    exit_price = position["sl"]
                    hit_sl = True
                elif row["Close"] > row["SMA_20"]:
                    exit_price = row["Close"] + slip
                    hit_exit = True

                if hit_sl or hit_exit:
                    pnl = (position["entry_price"] - exit_price) * position["size"]
                    capital += pnl
                    trades.append({
                        "pair": pair,
                        "direction": "SHORT",
                        "entry_date": position["entry_date"],
                        "exit_date": date,
                        "entry_price": position["entry_price"],
                        "exit_price": exit_price,
                        "sl": position["sl"],
                        "size": position["size"],
                        "pnl": pnl,
                        "pnl_pct": pnl / INITIAL_CAPITAL * 100,
                        "exit_reason": "SL" if hit_sl else "SMA_Cross",
                    })
                    if hit_sl:
                        cooldown_until = i + SL_COOLDOWN_BARS
                    position = None

        # --- Check entries (only if no position and cooldown expired) ---
        if position is None and i >= cooldown_until:
            atr = row.get("ATR", 0)
            atr_mult = get_atr_sl_multiplier(pair)
            min_sl = get_min_sl_distance(pair, price)
            sl_distance = max(atr * atr_mult, min_sl)

            if row.get("Buy_Signal", False):
                entry_price = row["Close"] + slip
                sl = entry_price - sl_distance
                risk_per_unit = sl_distance
                size = (capital * RISK_PER_TRADE) / risk_per_unit
                # Cap position size by max leverage
                max_size = (capital * MAX_LEVERAGE) / entry_price
                size = min(size, max_size)
                position = {
                    "direction": "LONG",
                    "entry_price": entry_price,
                    "sl": sl,
                    "size": size,
                    "entry_date": date,
                }

            elif row.get("Sell_Signal", False):
                entry_price = row["Close"] - slip
                sl = entry_price + sl_distance
                risk_per_unit = sl_distance
                size = (capital * RISK_PER_TRADE) / risk_per_unit
                # Cap position size by max leverage
                max_size = (capital * MAX_LEVERAGE) / entry_price
                size = min(size, max_size)
                position = {
                    "direction": "SHORT",
                    "entry_price": entry_price,
                    "sl": sl,
                    "size": size,
                    "entry_date": date,
                }

        # Track equity
        if position is not None:
            if position["direction"] == "LONG":
                unrealized = (row["Close"] - position["entry_price"]) * position["size"]
            else:
                unrealized = (position["entry_price"] - row["Close"]) * position["size"]
            equity.append(capital + unrealized)
        else:
            equity.append(capital)

    # Close any open position at end
    if position is not None:
        last = bt.iloc[-1]
        slip = get_spread(pair, last["Close"])
        if position["direction"] == "LONG":
            exit_price = last["Close"] - slip
            pnl = (exit_price - position["entry_price"]) * position["size"]
        else:
            exit_price = last["Close"] + slip
            pnl = (position["entry_price"] - exit_price) * position["size"]
        capital += pnl
        trades.append({
            "pair": pair,
            "direction": position["direction"],
            "entry_date": position["entry_date"],
            "exit_date": bt.index[-1],
            "entry_price": position["entry_price"],
            "exit_price": exit_price,
            "sl": position["sl"],
            "size": position["size"],
            "pnl": pnl,
            "pnl_pct": pnl / INITIAL_CAPITAL * 100,
            "exit_reason": "End_of_Test",
        })
        equity[-1] = capital

    equity_series = pd.Series(equity, index=[bt.index[0] - pd.Timedelta(days=1)] + list(bt.index))

    return {
        "trades": trades,
        "equity": equity_series,
        "final_capital": capital,
    }
