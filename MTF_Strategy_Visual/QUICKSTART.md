# Quick Start Guide

## Installation (2 minutes)

1. **Open TradingView** → Go to any chart (e.g., BTCUSD)
2. **Open Pine Editor** → Click "Pine Editor" tab at bottom of screen
3. **Copy Code** → Copy entire contents from `indicator.pine`
4. **Paste & Save** → Paste in Pine Editor, click "Save"
5. **Add to Chart** → Click "Add to Chart"

Done! The indicator should now be visible on your chart.

## First Time Setup

### Step 1: Choose Your Asset
- **Crypto**: BTC/USD, ETH/USD
- **Forex**: EUR/USD, GBP/USD
- **Stocks**: AAPL, SPY, TSLA

### Step 2: Set Chart Timeframe
- **Scalping**: 1-3 minutes
- **Day Trading**: 5-15 minutes
- **Swing Trading**: 1-4 hours

### Step 3: Configure Indicator Settings

Click the **gear icon** ⚙️ next to indicator name to open settings:

#### Timeframes Tab
- **HTF (Higher)**: Set to 4-12x your chart timeframe
  - Chart = 5min → HTF = 60min
  - Chart = 15min → HTF = 4H
  - Chart = 1H → HTF = Daily
- **MTF (Medium)**: Set between chart and HTF
  - Chart = 5min → MTF = 15min
  - Chart = 15min → MTF = 60min

#### Keep Defaults
For first test, keep all other settings at default values.

## Reading the Indicator

### Background Colors
- 🟢 **Green** = Bullish market (look for BUY signals)
- 🔴 **Red** = Bearish market (look for SELL signals)
- ⚪ **Gray** = Sideways/choppy (avoid trading)

### Signal Labels
- 🟢 **BUY** = Long entry signal
  - Appears below candle
  - Shows entry price
- 🔴 **SELL** = Short entry signal
  - Appears above candle
  - Shows entry price

### Take Profit / Stop Loss Lines
After a signal appears, you'll see:
- 🔵 **Blue Solid** = Entry price
- 🔴 **Red Dashed** = Stop loss
- 🟢 **Green Dashed** = TP1, TP2, TP3

### Dashboard (Top Right)
Shows real-time status:
```
┌─────────────────┐
│ MTF Strategy    │
├─────────────────┤
│ Status: Active  │  ← Trading conditions met?
│ ATR: 45.2       │  ← Current volatility
│ Volatility: Norm│  ← Market condition
│ HTF: Bullish    │  ← Higher timeframe direction
│ MTF: Aligned ↑  │  ← Medium timeframe aligned?
│ LTF: Bullish    │  ← Lower timeframe direction
│ Signal: BUY     │  ← Last signal generated
└─────────────────┘
```

## Taking a Trade

### ✅ Valid BUY Trade Checklist
1. Background is **green** (bullish HTF)
2. Dashboard shows **HTF: Bullish**
3. Dashboard shows **MTF: Aligned ↑**
4. Dashboard shows **Status: Active** (not Sideways)
5. **BUY label** appears with entry price
6. TP/SL lines are drawn

### ✅ Valid SELL Trade Checklist
1. Background is **red** (bearish HTF)
2. Dashboard shows **HTF: Bearish**
3. Dashboard shows **MTF: Aligned ↓**
4. Dashboard shows **Status: Active** (not Sideways)
5. **SELL label** appears with entry price
6. TP/SL lines are drawn

### 🚫 When NOT to Trade
- Background is **gray** (sideways market)
- Dashboard shows **Status: Sideways**
- Dashboard shows **MTF: Not Aligned**
- No clear signal label appears

## Trade Management

### Entry
- Enter at the price shown on the BUY/SELL label
- Or wait for next candle confirmation

### Stop Loss
- Place stop at the **red dashed line**
- This is typically 1.5x ATR from entry

### Take Profits
1. **TP1** (green dashed): Take 50% profit, move SL to breakeven
2. **TP2** (green dashed): Take 30% profit, trail SL to TP1
3. **TP3** (green dashed): Take final 20% or trail stop

### Example Trade
```
Entry: $50,000
SL:    $49,250 (1.5 ATR = $750)
TP1:   $50,750 (1.5 ATR = $750) - Take 50%, move SL to $50,000
TP2:   $51,250 (2.5 ATR = $1250) - Take 30%, trail SL to $50,750
TP3:   $53,000 (4.0 ATR = $3000) - Take 20% or trail
```

## Setting Up Alerts

1. Click **Alert** button (clock icon) on TradingView
2. Select **MTF Strategy Visual**
3. Choose condition:
   - **Buy Signal** → Get notified on long opportunities
   - **Sell Signal** → Get notified on short opportunities
   - **Sideways Market** → Get warned when market is choppy
4. Set notification method (app, email, webhook)
5. Click **Create**

## Common Questions

**Q: Why no signals appearing?**
A: Check that all conditions align:
- HTF must be bullish or bearish (not sideways)
- MTF must align with HTF
- ATR must be active (sufficient volatility)
- LTF must break EMA cloud

**Q: Too many false signals?**
A: Increase timeframes or ATR threshold:
- Use higher HTF (try 4H instead of 1H)
- Increase "ATR Threshold Multiplier" to 1.2-1.5

**Q: Missing good moves?**
A: Decrease ATR threshold:
- Lower "ATR Threshold Multiplier" to 0.8-0.9
- Use lower timeframes

**Q: Dashboard not showing?**
A: Enable in settings:
- Settings → Display Options → "Show Dashboard" ✓

## Tips for Success

1. **Start with demo/paper trading**
2. **Use proper position sizing** (risk 1-2% per trade)
3. **Don't trade against the HTF bias**
4. **Wait for all conditions to align**
5. **Avoid gray zones** (sideways markets)
6. **Keep a trading journal**
7. **Backtest on historical data first**

## Recommended Reading

- `README.md` - Full documentation
- `PARAMETERS.md` - Detailed parameter tuning guide
- `TESTING.md` - Validation checklist

## Next Steps

1. ✅ Install indicator (2 minutes)
2. ✅ Configure timeframes for your asset
3. ✅ Watch live for 1-2 days to understand signals
4. ✅ Paper trade for 1-2 weeks
5. ✅ Start with small position sizes
6. ✅ Gradually increase as confidence grows

## Support

For help or questions:
- Check `PARAMETERS.md` for detailed explanations
- Review `README.md` for strategy logic
- Open issue on GitHub for bugs/features

---

**Remember**: This is a tool to assist your trading, not a guaranteed profit system. Always use proper risk management and never risk more than you can afford to lose.
