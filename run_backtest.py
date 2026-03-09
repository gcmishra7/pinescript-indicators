"""Main orchestrator: download, compute, backtest, analyze."""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from config import RESULTS_DIR
from download_data import download_all, load_all
from indicators import compute_indicators
from signals import generate_signals
from backtest_engine import run_backtest
from analysis import (
    compute_metrics,
    plot_equity_curves,
    plot_trades_on_chart,
    plot_drawdown,
    save_trade_log,
    print_summary,
)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Phase 1: Download data
    print("=" * 60)
    print("PHASE 1: Downloading data...")
    print("=" * 60)
    download_all()
    data = load_all()

    if not data:
        print("ERROR: No data downloaded. Exiting.")
        return

    all_results = {}
    all_metrics = {}
    all_trades = []

    for pair, df in data.items():
        print(f"\n{'—' * 40}")
        print(f"Processing {pair}...")
        print(f"{'—' * 40}")

        # Phase 2: Indicators
        df = compute_indicators(df)

        # Phase 3: Signals
        df = generate_signals(df)

        buy_count = df["Buy_Signal"].sum()
        sell_count = df["Sell_Signal"].sum()
        print(f"  Signals found: {buy_count} BUY, {sell_count} SELL")

        # Phase 4: Backtest
        result = run_backtest(df, pair)
        all_results[pair] = result
        all_trades.extend(result["trades"])

        print(f"  Trades executed: {len(result['trades'])}")
        print(f"  Final capital: ${result['final_capital']:.2f}")

        # Phase 5: Metrics
        metrics = compute_metrics(result["trades"], result["equity"])
        all_metrics[pair] = metrics

        # Per-pair chart
        plot_trades_on_chart(df, result["trades"], pair)

    # Aggregate charts
    plot_equity_curves(all_results)
    plot_drawdown(all_results)
    save_trade_log(all_trades)
    print_summary(all_metrics)

    print(f"\nResults saved to {os.path.abspath(RESULTS_DIR)}/")
    print("  - equity_curves.png")
    print("  - drawdown.png")
    print("  - <pair>_trades.png (per pair)")
    print("  - trade_log.csv")
    print("  - summary.csv")


if __name__ == "__main__":
    main()
