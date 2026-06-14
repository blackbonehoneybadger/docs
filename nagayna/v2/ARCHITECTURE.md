# Product Architecture

Nagayna is composed of 12 modules.

```
                        ┌─────────────────────────┐
                        │   1. User Interface      │
                        │  assets · charts ·       │
                        │  signals · risk · trades │
                        │  · PnL · journal · news  │
                        └────────────┬────────────┘
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
┌───────▼────────┐         ┌─────────▼─────────┐        ┌─────────▼────────┐
│ 2. Exchange    │         │ 3. TradingView    │        │ 11. News         │
│    Connector   │         │    Connector      │        │  Intelligence    │
└───────┬────────┘         └─────────┬─────────┘        └─────────┬────────┘
        │                            │                            │
┌───────▼─────────────────────────────────────────────────────────▼────────┐
│ 4. Market Data Engine  (candles, volume, order book, funding, OI, liq.)    │
└───────┬───────────────────────────────────────────────────────────────────┘
        │
┌───────▼────────┐   ┌──────────────────┐   ┌──────────────────────────────┐
│ 5. Indicator   │──▶│ 6. AI Reasoning  │──▶│ 10. Risk Engine (final gate) │
│    Engine      │   │    Engine        │   └──────────────┬───────────────┘
└────────────────┘   └────────┬─────────┘                  │
                              │                            │
        ┌──────────────────────┼──────────────────┐         │
┌───────▼──────┐   ┌───────────▼─────┐   ┌─────────▼─────┐  │
│ 8. Backtest  │   │ 9. Paper Trading│   │ 7. Memory     │◀─┘
│    Engine    │   │    Engine       │   │    Engine     │
└──────────────┘   └─────────────────┘   └───────┬───────┘
                                                  │
                                          ┌───────▼───────┐
                                          │ 12. Report    │
                                          │     Engine    │
                                          └───────────────┘
```

---

## The 12 modules

1. **User Interface** — the panel where the user sees assets, charts, signals, recommendations, risk, trades, PnL, journal, news, reports.

2. **Exchange Connector** — connects to Bybit, Coinbase, Kraken, KuCoin, OKX, and Binance (if available). Starts read-only. See [INTEGRATIONS.md](./INTEGRATIONS.md#exchanges).

3. **TradingView Connector** — receives signals: webhooks, alerts, Pine Script strategies, user indicators. See [INTEGRATIONS.md](./INTEGRATIONS.md#tradingview).

4. **Market Data Engine** — collects candles, volumes, order book, funding, open interest, liquidations, volatility.

5. **Indicator Engine** — computes the technical indicators. See [INDICATORS.md](./INDICATORS.md).

6. **AI Reasoning Engine** — explains the situation and forms a trade idea, weighing indicator groups, multi-timeframe, market context, and news.

7. **Memory Engine** — stores the history of decisions, trades, and conclusions. See [LEARNING.md](./LEARNING.md).

8. **Backtesting Engine** — tests strategies on history.

9. **Paper Trading Engine** — trains the system with no money.

10. **Risk Engine** — limits risk and acts as the final gate on every trade. See [RISK_ENGINE.md](./RISK_ENGINE.md).

11. **News Intelligence Engine** — scans news and events, filtered by importance. See [INTEGRATIONS.md](./INTEGRATIONS.md#news-intelligence).

12. **Report Engine** — creates daily, weekly, and monthly reports.

---

## Data flow in one line

Market data + TradingView signals + news → Indicator Engine → AI Reasoning Engine forms an idea → **Risk Engine gates it** → (backtest / paper / confirmation) → outcome recorded in Memory → Report Engine summarizes → self-improvement cycle. See [LEARNING.md](./LEARNING.md#the-self-improvement-cycle).
