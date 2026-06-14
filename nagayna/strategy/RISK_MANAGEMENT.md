# Risk Management Framework — Nagayna Trading Bot

## Executive Summary

Nagayna implements a multi-layered risk management system to protect capital, ensure consistent performance, and adapt to market volatility. The framework combines mechanical risk controls, AI-driven monitoring, and manual intervention protocols.

---

## Core Risk Management Principles

1. **Never risk more than 1% per trade** — Ensures long-term survival
2. **Adapt to market conditions** — Dynamic position sizing based on volatility
3. **Diversify across assets & blockchains** — Reduce single-point-of-failure risk
4. **Continuous monitoring** — Real-time alerts for critical conditions
5. **Human oversight** — Critical decisions reviewed by traders

---

## Risk Metrics & Monitoring

### Per-Trade Risk Metrics

| Metric | Target | Limit | Action |
|--------|--------|-------|--------|
| **Trade Risk** | 0.5-1% | 2% max | Reject if exceeded |
| **Stop Loss** | 0.5% | 1% max | Tighten SL if needed |
| **Take Profit** | 1-2% | 5% max | Lock profits early |
| **Risk/Reward Ratio** | 1:2 | 1:1 minimum | Pass trade if poor |

### Portfolio-Level Risk Metrics

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| **Max Drawdown** | 5% | 7% | 10% |
| **Daily Loss Limit** | 2% | 3% | 5% |
| **Weekly Loss Limit** | 5% | 8% | 12% |
| **Monthly Loss Limit** | 10% | 15% | 20% |
| **Volatility (Sharpe)** | >1.5 | 1.0-1.5 | <1.0 |

### Trade Health Metrics

**Win Rate**: Should stay above 50%
- 50-55%: Acceptable
- 45-50%: Caution - review strategy
- <45%: Critical - halt trading, investigate

**Profit Factor**: (Total Wins / Total Losses)
- >2.0: Excellent
- 1.5-2.0: Good
- 1.2-1.5: Acceptable
- <1.2: Poor - adjust strategy

**Expectancy**: Average profit per trade
- E = (Win% × Avg Win) - (Loss% × Avg Loss)
- Target: E > +0.5% per trade

---

## Position Sizing System

### Kelly Criterion (Modified)

Standard Kelly formula adjusted for crypto volatility:
```
Position Size = (Win% - Loss%) / (Avg Win% / Avg Loss%)
```

**Example Calculation**:
```
Win Rate: 57%
Win% = 57%, Loss% = 43%
Avg Win: 1.5%, Avg Loss: 0.5%

Kelly% = (0.57 - 0.43) / (1.5 / 0.5)
       = 0.14 / 3
       = 0.0467 ≈ 4.7%

Conservative (50% Kelly): 2.35% per trade
Recommended (25% Kelly): 1.17% per trade (use this)
```

### Volatility-Adjusted Sizing

Position size scales inversely with market volatility:

```
Adjusted Size = Base Size × (Target Volatility / Current Volatility)

Example:
Base Size: 1.5%
Current ATR: 2.0%
Target ATR: 1.0%

Adjusted = 1.5% × (1.0 / 2.0) = 0.75%
```

### Account-Based Position Limits

| Account Size | Base Risk | Max Position | Contracts |
|-------------|-----------|--------------|-----------|
| $1,000 | 0.5% | $5 | 0.0001 BTC |
| $5,000 | 0.75% | $37 | 0.0007 BTC |
| $10,000 | 1% | $100 | 0.002 BTC |
| $50,000 | 1% | $500 | 0.01 BTC |
| $100,000 | 1% | $1,000 | 0.02 BTC |

---

## Stop-Loss & Take-Profit Management

### Standard Exit Strategy

```
Entry Level: $50,000
Position Risk: $100 (0.5% of $20,000 account)
Stop Loss: $49,750 (-$250, 0.5%)

Exit Plan:
├─ Take Profit 1: $50,500 (sell 30% position, +$150)
├─ Take Profit 2: $51,000 (sell 70% position, +$350)
└─ Stop Loss: $49,750 (sell remaining, -$250)

Expected Return: +$250
Worst Case: -$250
Risk/Reward: 1:1
```

### Trailing Stop Implementation

Activates at 0.5% profit to protect gains while allowing upside:

```
Entry: $50,000
Activation: $50,250 (0.5% profit)
Trail Distance: 0.3% below highest price

Action Sequence:
Price: $50,500 → Trail SL: $50,350
Price: $51,000 → Trail SL: $50,850
Price: $51,500 → Trail SL: $51,350
Price: $51,200 (drops) → Exit at $51,350 (trail SL hit)
Final P&L: +$1,350 (+2.7%)
```

### Time-Based Exit

Trades held maximum:
- Quick scalps: 5-30 minutes
- Swing trades: 4-24 hours
- Position trades: 1-7 days

If time limit reached without profit target:
- Exit at market price
- Record trade outcome
- Analyze for improvement

---

## Market Condition Adjustments

### Volatility Regimes

**Low Volatility (ATR < 0.5%)**
- Tighter stops (0.25% - 0.3%)
- Larger positions (1.5% risk)
- More frequent trading
- Focus on precision

**Normal Volatility (ATR 0.5% - 1.5%)**
- Standard stops (0.5%)
- Standard positions (1% risk)
- Regular trading
- Balanced approach

**High Volatility (ATR > 1.5%)**
- Wider stops (0.75% - 1%)
- Smaller positions (0.5% risk)
- Fewer trades
- Focus on quality setups

**Extreme Volatility (ATR > 3%)**
- Very wide stops (1%)
- Tiny positions (0.25% risk)
- Only best setups
- Consider halt trading

### Trend-Based Adjustments

**Strong Uptrend (ADX > 40, DI+ > DI-)**
- Larger positions (+0.5% risk)
- Tighter trailing stops
- More aggressive re-entry
- Higher profit targets

**Strong Downtrend (ADX > 40, DI- > DI+)**
- Smaller positions (-0.25% risk)
- Focus on shorts
- Quick exits
- Lower profit targets

**Ranging Market (ADX < 20)**
- Mean-reversion strategies
- Smaller positions (-0.25% risk)
- Frequent reversals expected
- Quick exits on breakout

---

## Portfolio-Level Risk Controls

### Sector Diversification

Maximum allocation per sector:
```
Bitcoin (BTC):      25% of portfolio
Ethereum (ETH):     20%
DeFi tokens:        15%
L1 Blockchains:     15%
Alts/Emerging:      25%
```

### Blockchain Diversification

Maximum per chain:
- Ethereum: 35% TVL
- BSC: 25% TVL
- Polygon: 20% TVL
- Avalanche: 10% TVL
- Solana: 10% TVL

### Time Diversification

Spread trades across time:
- Don't enter all capital in single trade
- Stagger entries over 1-4 hours
- Reduces timing risk
- Improves average entry

---

## Automated Risk Controls

### Circuit Breaker System

**Daily Loss Limit Triggered at -2%**
```
Account: $100,000
Loss: -$2,000
Action: Pause new trades for 30 minutes
Reason: Reduce emotional trading
```

**Weekly Loss Limit Triggered at -5%**
```
Account: $100,000
Loss: -$5,000
Action: Reduce position sizes by 50%
Action: Review trades for patterns
Action: Require manual approval for trades
```

**Monthly Loss Limit Triggered at -10%**
```
Account: $100,000
Loss: -$10,000
Action: Full trading halt for 24 hours
Action: Management review required
Action: Strategy adjustment required
```

### Correlation Monitoring

Tracks cross-asset correlation:
- BTC/ETH correlation: Use only if <0.7
- Reduce overlap if correlation > 0.8
- Diversify to non-correlated assets

### Liquidity Controls

Minimum liquidity required per trade:
- Order size: Max 5% of 5-minute volume
- Slippage tolerance: 0.1-0.3% max
- Order timeout: 5 minutes (cancel if unfilled)
- Re-route to alternate DEX if insufficient liquidity

---

## Leverage & Margin Trading

### Conservative Leverage Policy

- **Margin Trading**: Disabled by default
- **Leverage Limit**: Maximum 1.5:1 if enabled (only for experienced traders)
- **Collateral Ratio**: Maintain 3:1 minimum (75% available margin)
- **Liquidation Price**: Never within 5% of entry price

### Leverage Trade Example

```
Account: $10,000
Leverage: 1.5x
Effective Capital: $15,000

Trade Size: $5,000 (33% of effective capital)
Risk per trade: 0.5% of $10,000 = $50
Stop Loss: $49.50
Position: 0.1 BTC @ $50,000

Leverage Liquidation Price: $48,000
Safety Margin: $2,000 (vs $50 risk)
Safety Factor: 40x
```

**Leverage Usage Guidelines**:
- Use ONLY in low-volatility conditions
- Reduce position size by 50% when leveraged
- Monitor constantly for liquidation risk
- Disable if margin ratio below 2:1

---

## Dynamic Risk Adjustment

### Winning Streak Protocol

When profit factor > 2.0 and win rate > 60%:

| Days Win | Position Adjustment | Action |
|----------|------------------|--------|
| 3+ wins | +0.25% position | Increase activity |
| 5+ wins | +0.5% position | Increase size more |
| 10+ wins | +0.5%, increase frequency | Optimize profits |

### Losing Streak Protocol

When win rate < 45% and losing 3+ consecutive trades:

| Losses | Position Adjustment | Action |
|--------|------------------|--------|
| 2 losses | No change | Review strategy |
| 3 losses | -0.25% position | Reduce activity |
| 5 losses | -0.5% position, 30min pause | Halt trading |
| 7 losses | -0.75%, full review | Strategy overhaul |

---

## Risk Monitoring Dashboard

### Key Metrics to Monitor

**Daily Check**:
- P&L (daily, weekly, monthly)
- Win rate trend
- Average trade duration
- Slippage per trade
- Largest loss/win

**Weekly Check**:
- Sharpe ratio
- Maximum drawdown
- Correlation changes
- Liquidity conditions
- Blockchain health

**Monthly Check**:
- Strategy effectiveness
- Indicator accuracy
- Capital efficiency
- Risk-adjusted returns
- Market regime changes

---

## Risk Escalation Procedures

### Level 1: Caution (Yellow Alert)
- Drawdown -5% to -7%
- Win rate 45-50%
- Action: Reduce position sizes 25%

### Level 2: Warning (Orange Alert)
- Drawdown -7% to -10%
- Win rate <45%
- 5+ consecutive losses
- Action: Reduce position sizes 50%, manual approval required

### Level 3: Critical (Red Alert)
- Drawdown > -10%
- Win rate < 40%
- System failure or exchange issues
- Action: Full trading halt, management review

### Recovery Protocol
1. Halt all new trades
2. Analyze recent trades (last 50)
3. Identify common patterns
4. Adjust parameters or rules
5. Backtest new configuration
6. Resume with reduced position sizes
7. Gradually increase as performance improves

---

## Stress Testing & Scenario Planning

### Historical Stress Tests

**2017 Bear Market Scenario**
- Simulate -40% market crash
- Portfolio: -15% (diversified)
- Recovery time: 45 days
- Lesson: Diversification critical

**2022 Luna Collapse Scenario**
- Simulate -95% collapse on altcoin
- Portfolio impact: -5% (due to position limits)
- Recovery time: 60 days
- Lesson: Position sizing saves portfolio

**2024 Flash Crash Scenario**
- Simulate -20% in 1 minute
- SL execution: 2% slippage
- Portfolio impact: -0.5%
- Lesson: Slippage limits effective

---

## Continuous Improvement

### Monthly Risk Review

1. Analyze P&L distribution
2. Identify largest losses
3. Review stop-loss effectiveness
4. Check slippage trends
5. Evaluate risk metrics
6. Adjust parameters if needed
7. Update risk limits based on volatility

### Quarterly Risk Audit

1. Full strategy review
2. Backtest against new data
3. Update correlations
4. Review leverage policy
5. Assess new risks
6. Plan improvements
7. Document changes

---

**Status**: Active Framework  
**Last Updated**: June 2026  
**Review Schedule**: Monthly reviews, quarterly audits
