"""Configuration for MA + ATR Forex Swing Trading Strategy Backtest."""

# Instruments (Yahoo Finance tickers)
PAIRS = {
    # Forex
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    # "USDJPY": "USDJPY=X",  # Disabled: 0% win rate across all phases
    # "AUDUSD": "AUDUSD=X",  # Disabled: consistent loser, SMA strategy doesn't fit
    # Commodities
    "GLD": "GLD",
    "SLV": "SLV",
    "USO": "USO",       # US Oil Fund ETF
    "GDX": "GDX",       # Gold Miners (bonus)
}

# Date range (extra warmup for 100 SMA)
BACKTEST_START = "2025-03-09"
BACKTEST_END = "2026-03-09"
DATA_START = "2024-06-01"  # ~9 months warmup for 100 SMA

# Indicator settings
SMA_FAST = 20
SMA_SLOW = 100
ATR_PERIOD = 14

# ATR filter: only trade when ATR > ATR_THRESHOLD_PERCENTILE of rolling ATR
# We use the median (50th percentile) of a 252-day rolling ATR as threshold
ATR_THRESHOLD_LOOKBACK = 252
ATR_THRESHOLD_PERCENTILE = 0.50

# Trading costs (spread in price units — set per pair in backtest)
SPREAD_PIPS = 2

# Initial capital
INITIAL_CAPITAL = 10_000
RISK_PER_TRADE = 0.02  # 2% risk per trade

# Stop loss: ATR-based placement
ATR_SL_MULTIPLIER_FOREX = 1.5   # Stop = entry +/- N * ATR for forex
ATR_SL_MULTIPLIER_ETF = 2.0     # Stop = entry +/- N * ATR for commodity ETFs
MIN_SL_PCT_FOREX = 0.005        # Minimum 0.5% stop distance for forex
MIN_SL_PCT_ETF = 0.01           # Minimum 1.0% stop distance for ETFs
MAX_LEVERAGE = 20               # Max notional / capital ratio

# Cooldown: skip N bars after a stop loss exit before re-entering same pair
SL_COOLDOWN_BARS = 5

# Output
DATA_DIR = "data"
RESULTS_DIR = "results"
