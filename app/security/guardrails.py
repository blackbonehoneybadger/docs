"""Recommendation guardrails — the Risk Agent's rulebook.

Every investment recommendation passes through check_recommendation()
before it can be shown to the user. Rules (from the spec):

1. Emergency fund < 1 month of expenses  -> no aggressive investments.
2. Upcoming obligations > available cash -> no investments at all.
3. High credit utilization               -> warning before investing.
4. All-in requests                       -> reject.
5. Leverage / futures requests           -> high-risk warning (reject by default).
6. Exchange has an active risk alert     -> advise reducing exchange exposure.
7. Asset already above max allocation    -> do not advise buying more.
8. Not enough data                       -> say "данных недостаточно".
"""

from dataclasses import dataclass, field

HIGH_UTILIZATION_THRESHOLD = 0.5
ALL_IN_THRESHOLD = 0.9  # >=90% of free cash into one position counts as all-in


@dataclass
class FinancialContext:
    monthly_expenses: float = 0.0
    liquid_cash: float = 0.0
    available_cash: float = 0.0
    upcoming_obligations_total: float = 0.0
    credit_utilization: float = 0.0  # 0..1
    investment_capacity: float = 0.0
    has_data: bool = True


@dataclass
class RecommendationDraft:
    symbol: str | None = None
    amount: float = 0.0
    recommendation_type: str = "buy_more"
    uses_leverage: bool = False
    is_all_in_request: bool = False
    current_allocation_percent: float | None = None
    max_allocation_percent: float | None = None
    exchange_risk_alert: bool = False
    aggressive: bool = False


@dataclass
class GuardrailVerdict:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def emergency_fund_months(ctx: FinancialContext) -> float:
    if ctx.monthly_expenses <= 0:
        return 0.0
    return ctx.liquid_cash / ctx.monthly_expenses


def check_recommendation(ctx: FinancialContext, draft: RecommendationDraft) -> GuardrailVerdict:
    reasons: list[str] = []
    warnings: list[str] = []

    # Rule 8: insufficient data
    if not ctx.has_data:
        return GuardrailVerdict(allowed=False, reasons=["Данных недостаточно для рекомендации."])

    # Rule 4: all-in is always rejected
    if draft.is_all_in_request or (
        ctx.investment_capacity > 0 and draft.amount >= ctx.investment_capacity * ALL_IN_THRESHOLD
    ):
        reasons.append("All-in запрещён. Диверсификация обязательна.")

    # Rule 5: leverage / futures
    if draft.uses_leverage:
        reasons.append(
            "Leverage/futures — high-risk. Запрещено политикой: сначала emergency fund и cashflow."
        )

    # Rule 2: obligations exceed available cash
    if ctx.upcoming_obligations_total > ctx.available_cash:
        reasons.append(
            "Ближайшие обязательства больше доступного cash. Сегодня инвестиции запрещены."
        )

    # Rule 1: weak emergency fund blocks aggressive plays
    if draft.aggressive and emergency_fund_months(ctx) < 1.0:
        reasons.append(
            "Emergency fund меньше 1 месяца расходов — агрессивные инвестиции запрещены."
        )

    # Rule 7: over max allocation
    if (
        draft.recommendation_type == "buy_more"
        and draft.current_allocation_percent is not None
        and draft.max_allocation_percent is not None
        and draft.current_allocation_percent >= draft.max_allocation_percent
    ):
        reasons.append(
            f"{draft.symbol or 'Актив'} уже на максимуме аллокации "
            f"({draft.current_allocation_percent:.1f}% >= {draft.max_allocation_percent:.1f}%). "
            "Докупка не советуется."
        )

    # Rule 3: high credit utilization -> warning, not a hard block
    if ctx.credit_utilization >= HIGH_UTILIZATION_THRESHOLD:
        warnings.append(
            f"Credit utilization {ctx.credit_utilization * 100:.0f}% — высокая. "
            "Сначала подумай о снижении долга."
        )

    # Rule 6: exchange risk alert
    if draft.exchange_risk_alert:
        warnings.append(
            "По бирже есть risk alert — рассмотри сокращение exposure / перевод на cold wallet."
        )

    return GuardrailVerdict(allowed=not reasons, reasons=reasons, warnings=warnings)
