# Integrations

## TradingView

TradingView is one of Nagayna's key elements — a visual and analytical layer. The user may already have a TradingView subscription.

Ideal logic: the user opens a chart (e.g. XRP/USDT), picks a timeframe (e.g. 15m), with indicators on the chart. Nagayna should be able to:

- understand the chosen asset;
- understand the timeframe;
- read candle data;
- factor in indicators;
- receive TradingView alert signals;
- work with Pine Script strategies;
- connect to webhook notifications;
- save signals;
- compare TradingView signals against its own analysis.

**Realistic at the start:** don't try to "see" the browser visually — use **TradingView alerts and webhooks**.

Example: in TradingView an alert is configured — "If RSI < 30 and price breaks EMA, send a webhook to Nagayna." Nagayna receives the signal and begins its own analysis:

> "TradingView gave a long signal. Checking higher timeframes, news, volume, funding, Bitcoin trend."

So TradingView becomes a **source of signals**, but the final decision is made by Nagayna.

---

## Exchanges

Nagayna supports exchanges **gradually**. At the start: Bybit; Binance (if available in the user's region); Coinbase; Kraken; OKX; KuCoin.

**First mode — read-only:**

- get balance;
- get positions;
- get trade history;
- get prices;
- get candles;
- get fees.

Then → paper trading. Then → orders with confirmation.

**Important:** Nagayna must not hold unprotected full access to money. API keys must be restricted (read-only first, no withdrawals, IP whitelist where possible, encrypted, separate emergency stop). See [SAFETY.md](./SAFETY.md#api-key-hygiene).

---

## News Intelligence

Nagayna keeps a finger on the pulse. It monitors:

- news on Bitcoin, Ethereum, and the user's assets (XRP, SOL, …);
- listings / delistings;
- ETF news;
- SEC / CFTC news and court rulings;
- hacks and bridge exploits;
- whale movements;
- token unlocks;
- airdrops and presales;
- macro calendar: CPI, FOMC, interest rates, dollar index, stock market, Nasdaq;
- liquidations, funding rate, open interest.

But news must not flood the user as chaos — Nagayna **filters by importance**:

> "XRP news released. Likely impact: medium. Price has already partly reacted. Don't enter on emotion."

> "FOMC in 2 hours. High risk of sharp volatility. Better not to open new leveraged trades."

---

## BTC Profit Vault

The original 1.0 idea — converting profit to BTC and sending part to a cold wallet — is **kept but made safe**.

If the user is in profit, Nagayna *proposes* splitting it:

- part stays for trading;
- part moves to a stable asset;
- part converts to BTC;
- part is withdrawn to a cold wallet.

At the start this is a **recommendation, not an automatic action**:

> "This week's profit was $320. By your rules, 30% of profit can be moved to BTC — that's $96. Confirm the plan?"

The user decides or confirms. A semi-auto mode may be added later, **but never with seed-phrase storage**.

> **Nagayna must never ask for a seed phrase. Never.**

---

## DeFi module

DeFi is added cautiously. At the start Nagayna is a **DeFi Scanner, not a DeFi Trader**. It analyzes:

- yield;
- protocol risk;
- TVL;
- audit status;
- smart-contract risk;
- bridge risk;
- impermanent loss;
- history of hacks;
- token unlocks;
- liquidity depth.

Example:

> "This pool offers high APY, but risk is high: small TVL, no serious audit, highly volatile token. Not recommended."

Later additions: Aave monitoring, Uniswap liquidity, DEX price comparison, bridge comparison, wallet risk scoring. **Automatic DeFi interaction only after an audit and strong protection.**
