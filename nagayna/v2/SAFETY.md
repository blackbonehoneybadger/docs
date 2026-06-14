# Safety Model

Safety is the defining feature of Nagayna 2.0. Capability is unlocked **gradually**, and the human stays in control at every step.

---

## The 6 safety levels

Nagayna must operate in safe mode for a long time before any real trading.

### Level 1 — Backtesting
Test a strategy on historical data. "What would have happened if we'd traded XRP with this strategy for the last 12 months?" Reports trade count, profitable/losing counts, max drawdown, average win/loss, best/worst periods, and where the strategy broke.

### Level 2 — Paper trading
Trading with no real money. Nagayna *pretends* to open trades; no funds are used. "Train on XRP for a month in paper mode. Record every decision." After a month it reports results and lessons.

### Level 3 — Demo exchange account
If the exchange provides a demo account, Nagayna connects and trains as if on the real market — without risking the user's money.

### Level 4 — Real account, read-only
Nagayna only **reads** real account data: balance, positions, trade history, PnL, open orders. **It has no right to trade.**

### Level 5 — Real account, confirmation mode
Nagayna can prepare a trade, but the user must press confirm:

> "Nagayna proposes a long on XRP. Entry: 0.6250. Stop: 0.6110. Take profit: 0.6480. Leverage: 3x. Risk: 1% of deposit. Confirm?"

The user clicks **Yes** or **No**.

### Level 6 — Semi-auto mode
Only after long validation may the user allow partial automation — **with limits**:

- max 1% risk per trade;
- max 3 trades per day;
- no trading during important news;
- no leverage above a set X;
- a daily loss limit;
- an emergency **"stop everything"** button.

---

## Why you can't give it real money right away

This is critical. Even the smartest AI can be wrong. The market can behave illogically. News can drop suddenly. An exchange can fail. An API can lag. Indicators can give false signals.

So Nagayna develops step by step:

1. Analysis first.
2. Then paper trading.
3. Then demo trading.
4. Then read-only connection to a real exchange.
5. Then trades **only with user confirmation**.
6. Then small real amounts.
7. Then strict limits.
8. Only then semi-automatic mode.

> The goal of Nagayna is not to "get rich quick" but to build a **disciplined decision-making system**.

---

## API key hygiene

Nagayna must never hold unprotected full access to funds. Exchange API keys must be restricted:

- read-only at first;
- **no withdrawals**;
- no access to withdrawal functions;
- IP whitelist where possible;
- encrypted at rest;
- a separate emergency stop.

> **Nagayna must never ask for a seed phrase. Never.**

---

## What NOT to do at launch

At the start, Nagayna must **not**:

- launch an ICO;
- promise profit;
- give the bot full access to money;
- store a seed phrase;
- run auto-trading without limits;
- use high leverage;
- connect to DeFi without an audit;
- run aggressive "the AI earns for you" marketing;
- sell the token as an investment;
- claim that Nagayna "always beats the market".

These constraints are deliberate guardrails, not temporary limitations — they protect both users and the project's credibility.
