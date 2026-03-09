"""Performance analysis and visualization."""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from config import INITIAL_CAPITAL, RESULTS_DIR


def compute_metrics(trades: list, equity: pd.Series) -> dict:
    """Compute performance metrics from trade list and equity curve."""
    if not trades:
        return {"num_trades": 0}

    tdf = pd.DataFrame(trades)
    wins = tdf[tdf["pnl"] > 0]
    losses = tdf[tdf["pnl"] <= 0]

    # Drawdown
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_dd = drawdown.min()

    # Sharpe (annualized from daily equity returns)
    daily_ret = equity.pct_change().dropna()
    sharpe = (daily_ret.mean() / daily_ret.std() * np.sqrt(252)) if daily_ret.std() > 0 else 0

    # Holding period
    tdf["holding_days"] = (tdf["exit_date"] - tdf["entry_date"]).dt.days

    total_return = (equity.iloc[-1] - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100

    return {
        "num_trades": len(tdf),
        "win_rate": len(wins) / len(tdf) * 100 if len(tdf) > 0 else 0,
        "total_return_pct": total_return,
        "final_capital": equity.iloc[-1],
        "max_drawdown_pct": max_dd * 100,
        "sharpe_ratio": sharpe,
        "avg_win": wins["pnl"].mean() if len(wins) > 0 else 0,
        "avg_loss": losses["pnl"].mean() if len(losses) > 0 else 0,
        "profit_factor": abs(wins["pnl"].sum() / losses["pnl"].sum()) if len(losses) > 0 and losses["pnl"].sum() != 0 else float("inf"),
        "avg_holding_days": tdf["holding_days"].mean(),
        "total_pnl": tdf["pnl"].sum(),
        "num_long": len(tdf[tdf["direction"] == "LONG"]),
        "num_short": len(tdf[tdf["direction"] == "SHORT"]),
    }


def plot_equity_curves(all_results: dict):
    """Plot equity curves for all pairs on one chart."""
    fig, ax = plt.subplots(figsize=(14, 6))
    for pair, res in all_results.items():
        ax.plot(res["equity"].index, res["equity"].values, label=pair, linewidth=1.5)
    ax.axhline(INITIAL_CAPITAL, color="gray", linestyle="--", alpha=0.5)
    ax.set_title("Equity Curves — MA + ATR Forex Swing Strategy", fontsize=14)
    ax.set_ylabel("Equity ($)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "equity_curves.png"), dpi=150)
    plt.close()


def plot_trades_on_chart(df: pd.DataFrame, trades: list, pair: str):
    """Plot price chart with SMA lines and trade entry/exit markers."""
    from config import BACKTEST_START
    bt = df.loc[BACKTEST_START:]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), height_ratios=[3, 1], sharex=True)

    # Price + SMAs
    ax1.plot(bt.index, bt["Close"], color="black", linewidth=0.8, label="Close")
    ax1.plot(bt.index, bt["SMA_20"], color="blue", linewidth=0.8, alpha=0.7, label="SMA 20")
    ax1.plot(bt.index, bt["SMA_100"], color="orange", linewidth=0.8, alpha=0.7, label="SMA 100")

    # Trade markers
    for t in trades:
        color = "green" if t["direction"] == "LONG" else "red"
        marker_entry = "^" if t["direction"] == "LONG" else "v"
        ax1.scatter(t["entry_date"], t["entry_price"], marker=marker_entry, color=color, s=80, zorder=5)
        ax1.scatter(t["exit_date"], t["exit_price"], marker="x", color=color, s=80, zorder=5)
        ax1.plot([t["entry_date"], t["exit_date"]], [t["entry_price"], t["exit_price"]],
                 color=color, alpha=0.3, linewidth=1)

    ax1.set_title(f"{pair} — Trades", fontsize=13)
    ax1.legend(loc="upper left", fontsize=8)
    ax1.grid(True, alpha=0.3)

    # ATR subplot
    ax2.plot(bt.index, bt["ATR"], color="purple", linewidth=0.8, label="ATR")
    ax2.plot(bt.index, bt["ATR_Threshold"], color="gray", linestyle="--", linewidth=0.8, label="ATR Threshold")
    ax2.fill_between(bt.index, bt["ATR"], bt["ATR_Threshold"],
                     where=bt["ATR"] > bt["ATR_Threshold"], alpha=0.2, color="green", label="Active")
    ax2.set_title("ATR Filter", fontsize=10)
    ax2.legend(loc="upper left", fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, f"{pair}_trades.png"), dpi=150)
    plt.close()


def plot_drawdown(all_results: dict):
    """Plot drawdown curves for all pairs."""
    fig, ax = plt.subplots(figsize=(14, 4))
    for pair, res in all_results.items():
        eq = res["equity"]
        dd = (eq - eq.cummax()) / eq.cummax() * 100
        ax.plot(dd.index, dd.values, label=pair, linewidth=1)
    ax.set_title("Drawdown (%)", fontsize=13)
    ax.set_ylabel("Drawdown %")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "drawdown.png"), dpi=150)
    plt.close()


def save_trade_log(all_trades: list):
    """Save all trades to CSV."""
    if all_trades:
        tdf = pd.DataFrame(all_trades)
        tdf.to_csv(os.path.join(RESULTS_DIR, "trade_log.csv"), index=False)


def print_summary(all_metrics: dict):
    """Print summary table to console and save to file."""
    rows = []
    for pair, m in all_metrics.items():
        rows.append({
            "Pair": pair,
            "Trades": m.get("num_trades", 0),
            "Long": m.get("num_long", 0),
            "Short": m.get("num_short", 0),
            "Win Rate %": f"{m.get('win_rate', 0):.1f}",
            "Total Return %": f"{m.get('total_return_pct', 0):.2f}",
            "Max DD %": f"{m.get('max_drawdown_pct', 0):.2f}",
            "Sharpe": f"{m.get('sharpe_ratio', 0):.2f}",
            "Profit Factor": f"{m.get('profit_factor', 0):.2f}",
            "Avg Hold (days)": f"{m.get('avg_holding_days', 0):.1f}",
        })
    summary = pd.DataFrame(rows)
    print("\n" + "=" * 90)
    print("BACKTEST RESULTS — MA + ATR Forex Swing Trading Strategy")
    print("=" * 90)
    print(summary.to_string(index=False))
    print("=" * 90)
    summary.to_csv(os.path.join(RESULTS_DIR, "summary.csv"), index=False)
