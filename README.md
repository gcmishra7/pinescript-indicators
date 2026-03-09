# Pine Script Indicators

Collection of custom Pine Script indicators for TradingView.

## Available Indicators

### 1. [MTF Strategy Visual](MTF_Strategy_Visual/)
A professional multi-timeframe EMA cloud strategy with ATR volatility filtering.

**Features:**
- Multi-timeframe analysis (HTF/MTF/LTF)
- EMA cloud visualization with 6 EMAs
- ATR volatility filter
- Sideways market detection
- Entry signal labels (BUY/SELL)
- Automatic TP/SL levels based on ATR
- Real-time dashboard
- TradingView alerts

**Best For:** Day trading, swing trading, crypto, forex, stocks

[View Documentation →](MTF_Strategy_Visual/README.md)

### 2. [Forex Swing MA+ATR](Forex_Swing_MA_ATR/)
Python backtest of the Moving Average + ATR Forex Swing Trading Strategy from TradeThatSwing.com.

**Features:**
- 20/100 SMA trend-following strategy
- ATR volatility filter
- Python backtesting with trade-by-trade results
- Supports CSV data files and Yahoo Finance

**Best For:** Forex swing trading on daily timeframe

[View Documentation →](Forex_Swing_MA_ATR/README.md)

## Installation

Each indicator folder contains:
- `indicator.pine` - Copy this into TradingView Pine Editor
- `README.md` - Installation and usage instructions
- `PARAMETERS.md` - Detailed parameter tuning guide

## Usage

1. Navigate to the indicator folder
2. Copy the code from `indicator.pine`
3. Open TradingView Pine Editor
4. Paste the code and click "Add to Chart"
5. Configure parameters as needed

## Support

For issues or questions, please open an issue on GitHub.

## License

MIT License - Free to use and modify