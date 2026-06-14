# Risk Engine

The Risk Engine is the **heart of Nagayna's safety**. Risk management sits *above* profit in the product's priorities.

---

## What it decides

The Risk Engine answers, for every potential trade:

- how much can be lost in this trade;
- what leverage is acceptable;
- where the stop goes;
- where the take-profit goes;
- what the position size should be;
- how much has already been lost today;
- whether there's correlation with other open positions;
- whether too many trades are already open;
- whether we're trading on emotion;
- whether important news is near;
- whether funding is too high;
- whether volatility is too high.

---

## Example responses

> "The trade is possible, but risk is elevated. Recommended risk: 0.5% of deposit. Leverage: no more than 2x. Reason: high volatility, Bitcoin near a key level, positive funding."

> "Trade blocked by risk rules. Today's daily loss limit has already been reached."

> **Nagayna must be able to say "no". This is very important.**

The ability to refuse a trade — even a technically attractive one — is a feature, not a limitation. It is what separates a disciplined system from a gambling tool.

---

## Core controls

| Control | Default behavior |
|---------|------------------|
| Risk per trade | Recommend a % of deposit (e.g. 0.5–1%), scaled down in high volatility |
| Leverage ceiling | Capped per setup; lowered when volatility / funding are extreme |
| Stop-loss | Always proposed; required before a trade is confirmed |
| Take-profit | Proposed (often staged: first target / second target) |
| Daily loss limit | Hard stop — blocks new trades for the day once hit |
| Max trades/day | Prevents overtrading |
| Open-position correlation | Flags stacking of correlated exposure |
| News proximity | Blocks/dampens leveraged entries near high-impact events (e.g. FOMC, CPI) |
| Emotion check | Warns against revenge/FOMO patterns (rapid re-entries after losses) |
| Emergency stop | One action halts everything |

---

## Relationship to the rest of the system

- The [Council of Indicators](./INDICATORS.md) and the [News module](./INTEGRATIONS.md#news-intelligence) produce a trade *idea*.
- The Risk Engine is the **last gate**: it can resize, restrict, or fully block that idea.
- In [confirmation mode](./SAFETY.md#level-5--real-account-confirmation-mode), the Risk Engine's proposed stop/TP/leverage/size are what the user sees and confirms.
- In [semi-auto mode](./SAFETY.md#level-6--semi-auto-mode), the Risk Engine enforces the hard limits automatically.

Profit is never allowed to override these rules.
