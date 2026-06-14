# The Council of Indicators — 100 Indicators, Organized

The "100 indicators" idea from Nagayna 1.0 is kept, but made *smarter*. A hundred indicators must not behave like a chaotic pile of lines on a chart. They are organized into **groups**, each answering a specific question. Nagayna then weighs the groups in context rather than tallying raw signals.

---

## Group 1 — Trend indicators

**Question: Is the market going up, down, or sideways?**

- EMA
- SMA
- WMA
- Hull Moving Average (HMA)
- Ichimoku Cloud
- Supertrend
- ADX
- Parabolic SAR
- Moving Average Ribbon

## Group 2 — Momentum indicators

**Question: Does the move have strength behind it?**

- RSI
- MACD
- Stochastic
- CCI
- Momentum
- TRIX
- ROC
- Williams %R
- KDJ

## Group 3 — Volatility indicators

**Question: How dangerous and sharp is the market right now?**

- ATR
- Bollinger Bands
- Keltner Channel
- Donchian Channel
- Historical Volatility
- Standard Deviation

## Group 4 — Volume indicators

**Question: Is the move confirmed by money, or is it a false impulse?**

- OBV
- Volume Profile
- VWAP
- Chaikin Money Flow
- Money Flow Index
- Accumulation/Distribution
- Volume Delta
- CVD (Cumulative Volume Delta)

## Group 5 — Levels and zones

**Question: Where are support, resistance, liquidity zones, and reversal points?**

- Pivot Points
- Fibonacci Retracement
- Fibonacci Extension
- Support / Resistance
- Market Structure
- Liquidity Zones
- Order Blocks
- Fair Value Gaps

---

## Group 6 — Multi-timeframe analysis

Nagayna analyzes not one chart but several timeframes at once:

`1m · 5m · 15m · 1h · 4h · 1D · 1W · 1M`

Example: if there's a long signal on the 5-minute but strong resistance on the daily, Nagayna warns:

> "A short-term long is possible, but globally price is at resistance. The trade should be short, with a tight stop."

This is how Nagayna avoids the classic beginner trap of trading a small timeframe against the dominant higher-timeframe trend.

---

## Group 7 — Market context

Beyond the chart of a single asset, Nagayna factors in:

- Bitcoin trend
- Ethereum trend
- Bitcoin dominance
- total crypto market cap
- stablecoin inflows / outflows
- funding rates
- liquidations
- open interest
- Fear & Greed Index
- ETF flows
- macroeconomic calendar

---

## How the groups combine

The decision is **contextual weighting**, not a vote count:

1. Each group produces a stance (bullish / bearish / neutral) plus a confidence.
2. Group 6 (multi-timeframe) can **override** a lower-timeframe signal that fights the higher timeframe.
3. Group 7 (context) and the [news module](./INTEGRATIONS.md#news-intelligence) act as a **veto/dampener**: strong technicals can be overruled by high external risk.
4. The [Risk Engine](./RISK_ENGINE.md) has the final say and can block the trade entirely.

The output is never a bare "buy/sell" — it is a reasoned scenario with entry, invalidation, stop, targets, leverage ceiling, and a probability/risk label.
