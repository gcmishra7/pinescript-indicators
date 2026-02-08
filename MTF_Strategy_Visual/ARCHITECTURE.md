# MTF Strategy Visual - Architecture Overview

## Signal Generation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    MULTI-TIMEFRAME ANALYSIS                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   HTF (60m)  │     │   MTF (10m)  │     │   LTF (Now)  │
│              │     │              │     │              │
│  6 EMAs      │     │  6 EMAs      │     │  6 EMAs      │
│  5,8,13,21   │────▶│  5,8,13,21   │────▶│  5,8,13,21   │
│  34,55       │     │  34,55       │     │  34,55       │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
  ┌─────────┐         ┌─────────┐         ┌─────────┐
  │ Bullish?│         │Aligned? │         │ Break?  │
  │ Bearish?│         │  HTF?   │         │  Cloud? │
  │Sideways?│         │         │         │         │
  └─────────┘         └─────────┘         └─────────┘
       │                    │                    │
       └────────────┬───────┴────────────────────┘
                    ▼
            ┌───────────────┐
            │  ATR FILTER   │
            │               │
            │ Is volatility │
            │   sufficient? │
            └───────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  SIGNAL GEN   │
            │               │
            │  BUY / SELL?  │
            └───────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
   ┌─────────┐           ┌─────────┐
   │   BUY   │           │  SELL   │
   └─────────┘           └─────────┘
        │                       │
        ▼                       ▼
   ┌─────────────────────────────┐
   │   TP/SL CALCULATION         │
   │   Entry, SL, TP1, TP2, TP3  │
   └─────────────────────────────┘
                │
                ▼
   ┌─────────────────────────────┐
   │   VISUAL DISPLAY            │
   │   Labels, Lines, Dashboard  │
   └─────────────────────────────┘
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT PARAMETERS                          │
├─────────────────────────────────────────────────────────────────┤
│  EMA Settings    │  ATR Filter  │  Timeframes  │  Visuals/Risk  │
└─────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │     HTF      │  │     MTF      │  │     LTF      │
    │   EMAs (6)   │  │   EMAs (6)   │  │   EMAs (6)   │
    └──────────────┘  └──────────────┘  └──────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ▼
                    ┌──────────────────┐
                    │   CORE LOGIC     │
                    ├──────────────────┤
                    │ • Alignment Checks│
                    │ • ATR Filtering  │
                    │ • Sideways Detect│
                    │ • Signal Gen     │
                    └──────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   VISUALS    │  │  DASHBOARD   │  │    ALERTS    │
    ├──────────────┤  ├──────────────┤  ├──────────────┤
    │ • BG Colors  │  │ • Status     │  │ • Buy Signal │
    │ • Labels     │  │ • ATR        │  │ • Sell Signal│
    │ • Lines      │  │ • Bias       │  │ • Sideways   │
    │ • Boxes      │  │ • Alignment  │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘
```

## Signal Generation Logic

```
┌─────────────────────────────────────────────────────────────┐
│                     BUY SIGNAL CONDITIONS                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. HTF Bias = Bullish ✓                                   │
│     └─ EMAs in ascending order (5>8>13>21>34>55)          │
│                                                              │
│  2. MTF Aligned Bullish ✓                                  │
│     └─ EMAs ascending AND HTF bullish                       │
│                                                              │
│  3. Cloud Break Up ✓                                        │
│     └─ Price crosses above EMA1 (fastest EMA)              │
│                                                              │
│  4. ATR Active ✓                                            │
│     └─ Current ATR > ATR MA × Threshold                     │
│                                                              │
│  5. NOT Sideways ✓                                          │
│     └─ Market not choppy/ranging                            │
│                                                              │
│  ALL 5 CONDITIONS MUST BE TRUE                              │
│  ────────────────────────────────────▶  🟢 BUY SIGNAL       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    SELL SIGNAL CONDITIONS                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. HTF Bias = Bearish ✓                                   │
│     └─ EMAs in descending order (5<8<13<21<34<55)          │
│                                                              │
│  2. MTF Aligned Bearish ✓                                  │
│     └─ EMAs descending AND HTF bearish                      │
│                                                              │
│  3. Cloud Break Down ✓                                      │
│     └─ Price crosses below EMA1 (fastest EMA)              │
│                                                              │
│  4. ATR Active ✓                                            │
│     └─ Current ATR > ATR MA × Threshold                     │
│                                                              │
│  5. NOT Sideways ✓                                          │
│     └─ Market not choppy/ranging                            │
│                                                              │
│  ALL 5 CONDITIONS MUST BE TRUE                              │
│  ────────────────────────────────────▶  🔴 SELL SIGNAL      │
└─────────────────────────────────────────────────────────────┘
```

## TP/SL Calculation Logic

```
┌──────────────────────────────────────────────────────────────┐
│                   BUY TRADE TP/SL LEVELS                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Entry Price (EP) = Current Close                            │
│                                                               │
│  Stop Loss (SL) = EP - (ATR × 1.5)                          │
│     └─ Below entry to protect from downside                  │
│                                                               │
│  Take Profit 1 (TP1) = EP + (ATR × 1.5)   ← Quick profit   │
│     └─ Take 50% position here, move SL to breakeven         │
│                                                               │
│  Take Profit 2 (TP2) = EP + (ATR × 2.5)   ← Medium profit  │
│     └─ Take 30% position here, trail SL to TP1              │
│                                                               │
│  Take Profit 3 (TP3) = EP + (ATR × 4.0)   ← Large profit   │
│     └─ Take 20% position or trail stop                       │
│                                                               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                  SELL TRADE TP/SL LEVELS                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Entry Price (EP) = Current Close                            │
│                                                               │
│  Stop Loss (SL) = EP + (ATR × 1.5)                          │
│     └─ Above entry to protect from upside                    │
│                                                               │
│  Take Profit 1 (TP1) = EP - (ATR × 1.5)   ← Quick profit   │
│     └─ Take 50% position here, move SL to breakeven         │
│                                                               │
│  Take Profit 2 (TP2) = EP - (ATR × 2.5)   ← Medium profit  │
│     └─ Take 30% position here, trail SL to TP1              │
│                                                               │
│  Take Profit 3 (TP3) = EP - (ATR × 4.0)   ← Large profit   │
│     └─ Take 20% position or trail stop                       │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Dashboard Information Flow

```
┌─────────────────────────────────────────┐
│         MTF STRATEGY DASHBOARD          │
├─────────────────────────────────────────┤
│  Status:      [Active/Waiting/Sideways] │ ← Overall condition
│  ATR:         [Current value]           │ ← Volatility measure
│  Volatility:  [Normal/Low/Medium]       │ ← Volatility state
│  HTF:         [Bullish/Bearish/Sideway] │ ← Higher TF direction
│  MTF:         [Aligned/Not Aligned]     │ ← Medium TF alignment
│  LTF:         [Bullish/Bearish/Neutral] │ ← Lower TF direction
│  Signal:      [BUY/SELL/NONE]          │ ← Last signal
└─────────────────────────────────────────┘
            │
            ▼
    Updates in real-time
    on each new bar
```

## Visual Elements Map

```
CHART VIEW:
┌────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────┐           │
│ │   🟢 MTF STRATEGY DASHBOARD          │  ← Table │
│ │   Status: Active                     │           │
│ └──────────────────────────────────────┘           │
│                                                     │
│  ┌──────────────────────────┐                      │
│  │ ⬜ Sideways Market       │  ← Gray Box          │
│  └──────────────────────────┘                      │
│                                                     │
│              📈 SELL ← Red Label (above candle)    │
│              $50,123                                │
│              ┄┄┄┄┄┄  ← Green TP Lines (dashed)    │
│              ┄┄┄┄┄┄                                │
│              ┄┄┄┄┄┄                                │
│              ──────  ← Blue Entry Line (solid)     │
│ ││││││││││││││││││                                 │
│ ││││││││││││││││││  ← Price Candles                │
│              ┄┄┄┄┄┄  ← Red SL Line (dashed)        │
│              BUY ← Green Label (below candle)      │
│              $48,567                                │
│                                                     │
│ [Green Background]  ← Bullish HTF bias             │
│ [Red Background]    ← Bearish HTF bias             │
│ [Gray Background]   ← Sideways market              │
└────────────────────────────────────────────────────┘
```

## File Structure

```
MTF_Strategy_Visual/
│
├── indicator.pine              ← Main indicator code (313 lines)
│   ├─ Inputs (23 parameters)
│   ├─ EMA Calculations (18 EMAs across 3 timeframes)
│   ├─ Functions (3: bullish/bearish/converged)
│   ├─ ATR Filter Logic
│   ├─ Signal Generation (BUY/SELL)
│   ├─ Visual Elements (bgcolor, labels, lines, boxes)
│   ├─ Dashboard (table with 8 data rows)
│   └─ Alerts (3 conditions)
│
├── README.md                   ← User guide (146 lines)
│   ├─ Features
│   ├─ Installation
│   ├─ Strategy logic
│   ├─ Visual guide
│   ├─ Recommended settings
│   └─ Risk management
│
├── PARAMETERS.md               ← Tuning guide (433 lines)
│   ├─ EMA settings
│   ├─ ATR filter tuning
│   ├─ Timeframe configuration
│   ├─ Strategy presets
│   ├─ Asset-specific settings
│   └─ Quick reference tables
│
├── QUICKSTART.md               ← Quick guide (194 lines)
│   ├─ 2-minute installation
│   ├─ First-time setup
│   ├─ Reading the indicator
│   ├─ Trade checklists
│   └─ FAQ
│
├── TESTING.md                  ← Validation guide (194 lines)
│   ├─ Syntax checks
│   ├─ Logic validation
│   ├─ TradingView testing
│   ├─ Performance tests
│   └─ Edge cases
│
├── ARCHITECTURE.md             ← This file
│   ├─ Signal flow diagrams
│   ├─ Component architecture
│   ├─ Logic visualization
│   └─ Visual element map
│
└── IMPLEMENTATION_SUMMARY.md   ← Project summary
    ├─ Completion status
    ├─ Implementation details
    ├─ Requirements checklist
    └─ Quality metrics
```

## Code Organization

```
indicator.pine Structure:

Lines 1-50:    INPUT PARAMETERS
               - EMA settings (6 inputs)
               - ATR filter (4 inputs)
               - Timeframes (2 inputs)
               - Visual settings (10 inputs)
               - Risk management (4 inputs)

Lines 52-78:   EMA CALCULATIONS
               - LTF EMAs (6 calculations)
               - HTF EMAs (6 request.security calls)
               - MTF EMAs (6 request.security calls)

Lines 80-97:   HELPER FUNCTIONS
               - is_ema_bullish()
               - is_ema_bearish()
               - is_ema_converged()

Lines 99-111:  ATR FILTER
               - ATR and ATR MA calculation
               - Active volatility check
               - Contraction detection

Lines 113-140: MULTI-TIMEFRAME ANALYSIS
               - HTF bias determination
               - MTF alignment check
               - LTF trigger detection
               - Cloud breaks
               - Sideways detection

Lines 142-179: SIGNAL GENERATION
               - BUY signal conditions
               - SELL signal conditions
               - TP/SL calculations

Lines 181-192: EMA ZONE VISUALIZATION
               - Background colors

Lines 194-206: SIDEWAYS DETECTION
               - Gray boxes for sideways zones

Lines 208-224: SIGNAL LABELS
               - BUY labels (green, below)
               - SELL labels (red, above)

Lines 226-245: TP/SL VISUALIZATION
               - Entry lines (blue)
               - Stop loss (red dashed)
               - Take profits (green dashed)

Lines 247-301: DASHBOARD
               - Table creation
               - 8 data rows
               - Real-time updates

Lines 303-313: ALERT CONDITIONS
               - Buy Signal alert
               - Sell Signal alert
               - Sideways Market alert
```

## Performance Considerations

### Efficient Multi-Timeframe Calls
```
✅ GOOD: 12 request.security() calls (necessary)
   - 6 for HTF EMAs
   - 6 for MTF EMAs
   - Called once per bar
   
❌ AVOID: Calling request.security() in loops
❌ AVOID: Redundant security calls
```

### Memory Management
```
✅ GOOD: var table dashboard (created once)
✅ GOOD: Objects created on barstate.isconfirmed
✅ GOOD: Max limits set (500 boxes/labels/lines)

❌ AVOID: Creating objects on every tick
❌ AVOID: Infinite object creation
```

### Calculation Efficiency
```
✅ GOOD: Simple boolean logic
✅ GOOD: Efficient conditionals
✅ GOOD: Minimal nested calculations

❌ AVOID: Complex loops
❌ AVOID: Recursive functions
```

## Usage Flow

```
1. USER INSTALLS
   │
   ▼
2. CONFIGURE PARAMETERS
   │
   ▼
3. INDICATOR LOADS
   │
   ├─▶ Calculates 18 EMAs
   ├─▶ Computes ATR filter
   ├─▶ Determines HTF/MTF/LTF states
   └─▶ Checks signal conditions
   │
   ▼
4. VISUAL DISPLAY
   │
   ├─▶ Background color (bias)
   ├─▶ Dashboard (status)
   └─▶ Labels/Lines (signals)
   │
   ▼
5. USER MONITORS
   │
   ├─▶ Waits for alignment
   ├─▶ Checks dashboard
   └─▶ Watches for signals
   │
   ▼
6. SIGNAL APPEARS
   │
   ├─▶ BUY or SELL label
   ├─▶ TP/SL lines drawn
   └─▶ Alert triggered (optional)
   │
   ▼
7. USER TRADES
   │
   ├─▶ Enter at signal price
   ├─▶ Set SL at red line
   └─▶ Set TPs at green lines
```

---

## Quick Reference

### Signal Requirements
- ✅ HTF aligned (all EMAs in order)
- ✅ MTF aligned with HTF
- ✅ LTF cloud break
- ✅ ATR active (sufficient volatility)
- ✅ Not sideways market

### Visual Indicators
- 🟢 Green background = Bullish
- 🔴 Red background = Bearish
- ⚪ Gray background = Sideways
- 🟢 BUY label = Long entry
- 🔴 SELL label = Short entry
- 🔵 Blue line = Entry price
- 🔴 Red dashed = Stop loss
- 🟢 Green dashed = Take profits

### Default Settings
- HTF: 60 minutes
- MTF: 10 minutes
- LTF: Current chart
- EMAs: 5, 8, 13, 21, 34, 55
- ATR: 14 period
- TP/SL: 1.5, 2.5, 4.0, 1.5 multipliers
