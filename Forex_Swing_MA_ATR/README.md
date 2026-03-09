# Forex Swing Trading: Moving Average + ATR Strategy

A Python backtest implementation of the [Moving Average and ATR Forex Swing Trading Strategy](https://tradethatswing.com/moving-average-and-atr-forex-swing-trading-strategy/) from TradeThatSwing.com.

## Strategy Rules

**Timeframe:** Daily chart

**Indicators:** 20 SMA, 100 SMA, 14-period ATR

### Entry Rules

**Long:**
1. Price must be above the 100 SMA (bullish trend)
2. At least one prior candle body (open AND close) was below the 20 SMA
3. Current candle closes above the 20 SMA
4. ATR must be above threshold (if set)

**Short:**
1. Price must be below the 100 SMA (bearish trend)
2. At least one prior candle body (open AND close) was above the 20 SMA
3. Current candle closes below the 20 SMA
4. ATR must be above threshold (if set)

### Stop Loss
- Long: Low of the trigger candle (fixed, does not trail)
- Short: High of the trigger candle (fixed, does not trail)

### Exit
- Daily close on the opposite side of the 20 SMA

### ATR Filter
Set a threshold based on historical ATR levels for the pair. Only trade when ATR is above that level to avoid choppy markets. Set to 0 to disable.

## Running the Backtest

```bash
python3 backtest.py
```

### Data Sources (checked in order)

1. **CSV files** in `data/` subfolder (e.g., `data/EURUSD.csv` with columns: Date, Open, High, Low, Close)
2. **Yahoo Finance** via `yfinance` (requires internet access)
3. **Generated sample data** for testing strategy logic when no real data is available

### Configuration

Edit the constants at the top of `backtest.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `FAST_MA` | 20 | Fast moving average period |
| `SLOW_MA` | 100 | Slow moving average period |
| `ATR_PERIOD` | 14 | ATR calculation period |
| `ATR_THRESHOLD` | 0.0 | Minimum ATR to allow trades (0 = disabled) |

### Backtest Pairs
- EUR/USD
- GBP/USD
- USD/JPY
- AUD/JPY

## Output

Per-pair results include:
- Total trades, win rate, net P&L (in pips)
- Profit factor, max drawdown
- Average trade duration
- Individual trade log with entry/exit details

## Dependencies

- Python 3.8+
- pandas, numpy
- yfinance (optional, for live data)

```bash
pip install pandas numpy yfinance
```

## Disclaimer

This strategy is for educational and research purposes only. Trading involves substantial risk of loss. Past performance (including backtests) is not indicative of future results. Always use proper risk management.

## Credit

Strategy based on the article by [TradeThatSwing.com](https://tradethatswing.com/moving-average-and-atr-forex-swing-trading-strategy/).
