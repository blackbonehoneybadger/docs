# Nagayna Trading Strategy — Core Algorithm & Indicators

## Overview

Nagayna employs a sophisticated multi-indicator trading system that analyzes cryptocurrency markets using 100+ technical indicators, machine learning models, and reinforcement learning to generate optimal trading signals.

## Core Trading Philosophy

**Principle**: Use ensemble of indicators + adaptive ML to identify high-probability market movements while maintaining strict risk management.

**Goals**:
- Maximize risk-adjusted returns
- Minimize drawdowns (target < 5% per trade)
- Achieve consistent daily profits
- Adapt to changing market conditions

## The 100+ Technical Indicators

### Momentum Indicators (15)
1. **RSI** (Relative Strength Index) — Overbought/oversold conditions
2. **MACD** (Moving Average Convergence Divergence) — Trend following
3. **Stochastic Oscillator** — Momentum confirmation
4. **CCI** (Commodity Channel Index) — Cyclical analysis
5. **Williams %R** — Momentum reversal signals
6. **Momentum Indicator** — Price rate of change
7. **Force Index** — Volume-based momentum
8. **Coppock Curve** — Long-term trend changes
9. **KDJ Indicator** — Enhanced stochastic
10. **ROC** (Rate of Change) — Velocity measurement
11. **MFI** (Money Flow Index) — Volume + price oscillator
12. **Awesome Oscillator** — Momentum strength
13. **Ultimate Oscillator** — Multi-timeframe momentum
14. **Trix** — Trend identification
15. **Vortex Indicator** — Directional movement

### Trend Indicators (18)
16. **SMA** (Simple Moving Average) — Trend direction
17. **EMA** (Exponential Moving Average) — Responsive trend
18. **Bollinger Bands** — Volatility + support/resistance
19. **Ichimoku Cloud** — Support/resistance + trend
20. **Parabolic SAR** — Stop and reverse points
21. **ADX** (Average Directional Index) — Trend strength
22. **Aroon Indicator** — Trend existence
23. **ATR** (Average True Range) — Volatility measure
24. **Moving Average Envelope** — Volatility bands
25. **Hull Moving Average** — Lag-reduced MA
26. **TRIX** (Triple Exponential Average) — Trend smoothing
27. **DPO** (Detrended Price Oscillator) — Cycle detection
28. **Zig-Zag Indicator** — Pivot point identification
29. **Supertrend** — Trend following with dynamic SL
30. **KAMA** (Kaufman's Adaptive MA) — Adaptive trend
31. **Linear Regression** — Mathematical trend fit
32. **Regression Channel** — Standard deviation bands
33. Additional trend variants — Custom implementations

### Volume Indicators (12)
34. **OBV** (On Balance Volume) — Cumulative volume
35. **CMF** (Chaikin Money Flow) — Volume + price action
36. **A/D Line** (Accumulation/Distribution) — Buying pressure
37. **Volume Rate of Change** — Volume momentum
38. **Ease of Movement** — Volume efficiency
39. **Money Flow Index** — Volume + momentum (repeated)
40. **Volume Profile** — Historical volume distribution
41. **VWAP** (Volume Weighted Avg Price) — Average entry level
42. **Klinger Oscillator** — Volume-based momentum
43. **Price Volume Trend** — Trend + volume confirmation
44. **Volume Oscillator** — Volume trend
45. Additional volume variants

### Support/Resistance Indicators (12)
46. **Fibonacci Retracement** — Key support/resistance levels
47. **Pivot Points** (5-level) — Standard pivot analysis
48. **Camarilla Pivot** — Tighter pivot bands
49. **Woodie Pivot** — Alternative pivot calculation
50. **DeMark Pivot** — TD Sequential-based levels
51. **Psychological Levels** — Round numbers (100, 1000, etc.)
52. **Volume Profile POC** — Point of Control (highest volume)
53. **VAL/VAH** (Value Area Low/High) — Volume area
54. **Knots** — Custom key levels
55. **Resistance Cluster** — Confluence of S/R
56. **Order Block** — Historical imbalance zones
57. Additional S/R variants

### Volatility Indicators (10)
58. **ATR** — Average True Range (repeated)
59. **Standard Deviation** — Price dispersion
60. **Bollinger Band Width** — Volatility measure
61. **Bollinger Band %B** — Position within bands
62. **Keltner Channels** — ATR-based channels
63. **Donchian Channels** — Recent high/low bands
64. **Historical Volatility** — Past price movement
65. **VIX (Crypto VIX)** — Market fear gauge
66. **NATR** (Normalized ATR) — ATR as percentage
67. Additional volatility metrics

### Pattern Recognition (20+)
70. **Candlestick Patterns** — Engulfing, doji, hammer, etc.
71. **Elliott Wave Patterns** — 5-wave structure
72. **Head & Shoulders** — Reversal pattern detection
73. **Double Top/Bottom** — Double peak detection
74. **Triangle Patterns** — Symmetrical/ascending/descending
75. **Flag & Pennant** — Continuation patterns
76. **Cup & Handle** — Bullish continuation
77. **Wedge Patterns** — Rising/falling wedges
78. **Diamond Patterns** — Reversal formation
79. Additional chart patterns (20+ total)

### Correlation & Sentiment (8+)
90. **Cross-Asset Correlation** — Bitcoin/Ethereum correlation
91. **Market Sentiment Index** — Social media analysis
92. **Fear & Greed Index** — Emotional indicator
93. **Whale Wallet Movements** — Large holder activity
94. **Exchange Inflows** — Potential selling pressure
95. **On-Chain Metrics** — Active addresses, transactions
96. **Funding Rates** — Futures market sentiment
97. **IV (Implied Volatility)** — Options market expectations
98-100. **Custom Indicators** — Proprietary ML-derived signals

## Trading Signal Generation

### Signal Classification

**BUY Signal** — Generated when:
- 60%+ of indicators align bullish
- Volume confirms price action
- Support level intact
- Trend direction positive (ADX > 20)
- Risk/reward ratio favorable (min 1:2)

**SELL Signal** — Generated when:
- 60%+ of indicators align bearish
- Volume confirms price action
- Resistance level broken
- Trend direction negative (ADX > 20)
- Risk/reward ratio favorable

**NEUTRAL** — When:
- 40-60% indicator alignment
- Conflicting signals from different timeframes
- Low volatility environment
- Awaiting clearer setup

### Multi-Timeframe Analysis

Signals are validated across multiple timeframes:

| Timeframe | Weight | Purpose |
|-----------|--------|---------|
| 15-minute | 30% | Entry timing & quick reversals |
| 1-hour | 40% | Primary signal generation |
| 4-hour | 20% | Trend confirmation |
| 1-day | 10% | Macro direction |

**Example Signal**:
- 4h: Bullish trend (EMA slope positive)
- 1h: Breakout above resistance (Fibonacci level)
- 15m: Pullback entry with volume confirmation
- Result: HIGH CONFIDENCE BUY

## Risk Management Framework

### Position Sizing

```
Risk per trade = Account balance × 1%
Trade size = Risk per trade / (Entry - Stop Loss) distance

Example:
Account: $10,000
Max risk: $100
Stop loss distance: $100 from entry
Trade size: $100 / $100 = 1 unit
```

### Stop-Loss & Take-Profit

| Order Type | Level | Purpose |
|-----------|-------|---------|
| **Stop Loss** | 0.5% below entry | Maximum loss containment |
| **Take Profit 1** | 1% above entry | Partial profit lock (30% position) |
| **Take Profit 2** | 2% above entry | Full position close (70% position) |

**Example Trade**:
```
Entry: $10,000 (BTC @ $50,000)
Stop Loss: $49,750 (-0.5%)
TP 1: $50,500 (sell 30%)
TP 2: $51,000 (sell 70%)
Max Risk: $125 per 0.25 BTC
Expected Return: +$125-$175 per trade
Risk/Reward: 1:1.4 to 1:1.8
```

### Trailing Stop Implementation

- **Initial Stop**: 0.5% below entry
- **Activation Level**: +0.5% profit
- **Trail Distance**: 0.3% below highest price
- **Purpose**: Protect profits while allowing upside

## Machine Learning Integration

### Reinforcement Learning

The bot learns from each trade:

1. **Observation**: Market state (100+ indicators)
2. **Action**: Buy, sell, or hold
3. **Reward**: Profit/loss from trade
4. **Update**: Q-learning to improve future decisions

**Learning Rate**: Trades improve prediction accuracy by ~0.5% per 1,000 trades

### Adaptive Parameters

- **RSI Overbought Level**: Adjusts based on asset volatility (typically 65-75)
- **MACD Sensitivity**: Optimizes for market regime (slow vs. fast)
- **Bollinger Band Width**: Scales with realized volatility
- **Position Size**: Increases in high-win-rate periods, decreases in drawdowns

## Capital Management Strategy

### Initial Capital: $1,000

**Reinvestment Schedule**:
- Day 1-7: Trade with $1,000
- Week 2: Reinvest 50% of profits
- Week 3+: Daily reinvestment of 50% of profits

**Example Growth**:
```
Week 1: $1,000 → $1,050 (+5%)
Reinvest: +$25
Week 2: $1,075 → $1,129 (+5%)
Reinvest: +$27
Week 3: $1,156 → $1,214 (+5%)
...
Month 1: $1,000 → ~$1,215 (+21.5% from compounding)
Month 6: ~$2,431 (doubling + reinvestment)
Month 12: ~$5,917 (nearly 6x growth)
```

## Trade Execution

### Order Types

1. **Market Orders** — Immediate execution for strong signals
2. **Limit Orders** — Precise entry at key levels
3. **Grid Trading** — Multiple small positions (scaling in/out)
4. **DCA** (Dollar Cost Averaging) — Systematic entry over time

### Execution Rules

- **Slippage Tolerance**: 0.1-0.3% depending on liquidity
- **Order Timeout**: Cancel unfilled limit orders after 5 minutes
- **Partial Fills**: Accept 80%+ of intended amount
- **Multi-Chain Routing**: Use most liquid DEX per chain

## Performance Metrics

### Target Performance

| Metric | Target | Realistic Range |
|--------|--------|-----------------|
| **Win Rate** | 55-60% | 50-65% |
| **Profit Factor** | 1.5+ | 1.3-2.0 |
| **Sharpe Ratio** | 1.5+ | 1.0-2.5 |
| **Max Drawdown** | 5% | 3-8% |
| **Monthly Return** | 5-10% | 2-15% |
| **Annual Return** | 60-120% | 24-180% |

### Calculation Examples

**Win Rate**: 57 wins / 100 trades = 57%

**Profit Factor**: Total wins / Total losses = $5,700 / $3,800 = 1.5

**Sharpe Ratio**: (Return - Risk Free) / StdDev = (100% - 2%) / 65% = 1.51

---

**Status**: Active Development  
**Last Updated**: June 2026  
**Next Update**: Q3 2025 (Post-Launch Performance Data)
