# Memory & Self-Improvement

## Memory — the key feature

A regular chatbot forgets the details of long work or loses context. Nagayna has its own **memory base**. It stores:

- user profile;
- favorite assets;
- trading style;
- risk profile;
- past trades;
- past mistakes;
- successful patterns;
- failed patterns;
- strategies;
- reports;
- backtest results;
- paper-trading results;
- news that influenced trades;
- decisions that were made;
- explanations of *why* they were made.

Memory is **not one big pile of text** but a structured system:

| Store | Purpose |
|-------|---------|
| Relational database | Trades (entries, exits, stops, leverage, PnL) |
| Vector database | Notes and reasoning, for semantic recall |
| Logs | Decisions and their timestamps |
| Reports | Daily summaries |
| Strategy versions | Versioned strategy definitions |
| Model evaluations | Checks that improvements are real |

---

## Post-trade review

After **every** trade Nagayna writes a post-trade review. Examples:

> "The SOL trade closed at a loss. Reason: entry was made against the higher timeframe. There was a long signal on the 15-minute, but the 4H trend was still down. In future, when the lower and higher timeframes conflict, reduce position size or wait for confirmation."

> "The XRP trade was successful. Reason: trend, volume, level breakout, and a positive news backdrop all aligned. In future, similar configurations can be treated as strong — but only when funding rate is normal."

This way Nagayna doesn't just store data; it builds its own **base of experience**.

---

## The self-improvement cycle

Nagayna improves not magically, but through a clear loop:

1. Collect data.
2. Analyze the market.
3. Generate a trade idea.
4. Paper-trade, or real-trade with confirmation.
5. Record the result.
6. Analyze the mistake or success.
7. Update the rules.
8. Test new rules on history (backtest).
9. Compare the old and new strategy.
10. Adopt the improvement **only if it is genuinely better**.

> **Important:** Nagayna must not change its strategy chaotically every day. Otherwise it overfits and breaks.

### Cadence

- **Daily** — draws conclusions.
- **Weekly** — proposes improvements.
- Each improvement is **backtested**.
- The user **confirms** the new strategy version.
- The old version is **kept**.
- You can **roll back**.

It works like app updates. Example:

> "Strategy v1.3 outperformed v1.2 on XRP and SOL, but underperformed on BTC. Recommendation: use v1.3 for altcoins only, keep v1.2 for BTC."

---

## Training stages (overview)

Learning happens safely, before any real money is at stake. The full ladder of safety levels is in [SAFETY.md](./SAFETY.md), but the learning-relevant stages are:

- **Backtesting** — replay history: how many trades, win/loss counts, max drawdown, average win/loss, best/worst periods, where the strategy broke.
- **Paper trading** — simulated trades, no real money. Example monthly report:
  > "I executed 87 simulated trades. 52 profitable, 35 losing. Main mistake — entering too early in range-bound markets. Best results in trending markets. Recommendation: add an ADX filter and trade less in chop."
- **Demo exchange account** — if the exchange offers one, train as if on the real market without risking funds.

Every stage feeds the memory base and the self-improvement cycle above.
