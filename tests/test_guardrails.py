"""Guardrail rules from the spec — each numbered rule has a test."""

from app.security.guardrails import (
    FinancialContext,
    RecommendationDraft,
    check_recommendation,
    emergency_fund_months,
)


def _healthy_ctx(**overrides) -> FinancialContext:
    base = dict(
        monthly_expenses=2000.0,
        liquid_cash=4000.0,
        available_cash=4000.0,
        upcoming_obligations_total=500.0,
        credit_utilization=0.1,
        investment_capacity=300.0,
        has_data=True,
    )
    base.update(overrides)
    return FinancialContext(**base)


def test_rule1_weak_emergency_fund_blocks_aggressive():
    ctx = _healthy_ctx(liquid_cash=1000.0)  # 0.5 months
    draft = RecommendationDraft(symbol="SOL", amount=50, aggressive=True)
    verdict = check_recommendation(ctx, draft)
    assert not verdict.allowed
    assert any("emergency fund" in r.lower() for r in verdict.reasons)


def test_rule1_weak_emergency_fund_allows_conservative():
    ctx = _healthy_ctx(liquid_cash=1000.0)
    draft = RecommendationDraft(symbol="BTC", amount=50, aggressive=False)
    assert check_recommendation(ctx, draft).allowed


def test_rule2_obligations_exceed_cash_blocks_everything():
    ctx = _healthy_ctx(upcoming_obligations_total=5000.0)
    draft = RecommendationDraft(symbol="BTC", amount=10)
    verdict = check_recommendation(ctx, draft)
    assert not verdict.allowed


def test_rule3_high_utilization_warns_but_does_not_block():
    ctx = _healthy_ctx(credit_utilization=0.8)
    draft = RecommendationDraft(symbol="BTC", amount=50)
    verdict = check_recommendation(ctx, draft)
    assert verdict.allowed
    assert verdict.warnings


def test_rule4_all_in_rejected_explicit():
    verdict = check_recommendation(
        _healthy_ctx(), RecommendationDraft(symbol="SOL", amount=10, is_all_in_request=True)
    )
    assert not verdict.allowed
    assert any("all-in" in r.lower() for r in verdict.reasons)


def test_rule4_all_in_rejected_by_amount():
    ctx = _healthy_ctx(investment_capacity=100.0)
    verdict = check_recommendation(ctx, RecommendationDraft(symbol="SOL", amount=95))
    assert not verdict.allowed


def test_rule5_leverage_rejected():
    verdict = check_recommendation(
        _healthy_ctx(), RecommendationDraft(symbol="BTC", amount=10, uses_leverage=True)
    )
    assert not verdict.allowed
    assert any("leverage" in r.lower() for r in verdict.reasons)


def test_rule6_exchange_risk_alert_warns():
    verdict = check_recommendation(
        _healthy_ctx(), RecommendationDraft(symbol="BTC", amount=10, exchange_risk_alert=True)
    )
    assert verdict.allowed
    assert any("risk alert" in w for w in verdict.warnings)


def test_rule7_over_max_allocation_blocks_buy_more():
    draft = RecommendationDraft(
        symbol="SOL", amount=10, recommendation_type="buy_more",
        current_allocation_percent=40.0, max_allocation_percent=30.0,
    )
    verdict = check_recommendation(_healthy_ctx(), draft)
    assert not verdict.allowed


def test_rule8_no_data_means_no_recommendation():
    verdict = check_recommendation(
        _healthy_ctx(has_data=False), RecommendationDraft(symbol="BTC", amount=10)
    )
    assert not verdict.allowed
    assert any("данных недостаточно" in r.lower() for r in verdict.reasons)


def test_emergency_fund_months():
    assert emergency_fund_months(_healthy_ctx()) == 2.0
    assert emergency_fund_months(_healthy_ctx(monthly_expenses=0)) == 0.0
