"""Risk Agent: gatekeeper for every recommendation. Wraps the guardrails."""

from sqlalchemy.orm import Session

from app.security.audit_log import log_event
from app.security.guardrails import (
    FinancialContext,
    GuardrailVerdict,
    RecommendationDraft,
    check_recommendation,
)
from app.services.cfo_service import CfoSummary


class RiskAgent:
    name = "risk"

    def context_from_summary(self, s: CfoSummary) -> FinancialContext:
        return FinancialContext(
            monthly_expenses=s.monthly_expenses,
            liquid_cash=s.available_cash,
            available_cash=s.available_cash,
            upcoming_obligations_total=s.upcoming_obligations_total,
            credit_utilization=s.credit_utilization,
            investment_capacity=s.investment_capacity,
            has_data=True,
        )

    def review(
        self, db: Session, user_id: int, summary: CfoSummary, draft: RecommendationDraft
    ) -> GuardrailVerdict:
        verdict = check_recommendation(self.context_from_summary(summary), draft)
        log_event(
            db,
            event_type="ai_decision",
            actor=self.name,
            action=f"guardrail_review:{draft.recommendation_type}:{draft.symbol or '-'}",
            user_id=user_id,
            details={
                "allowed": verdict.allowed,
                "reasons": verdict.reasons,
                "warnings": verdict.warnings,
                "amount": draft.amount,
            },
        )
        return verdict

    def render_risks(self, summary: CfoSummary) -> str:
        lines = ["Риски сегодня:", ""]
        flagged = False
        if summary.upcoming_obligations_total > summary.available_cash:
            lines.append("- КРИТИЧНО: обязательства превышают доступный cash.")
            flagged = True
        if summary.credit_utilization >= 0.5:
            lines.append(
                f"- Credit utilization {summary.credit_utilization * 100:.0f}% — высокая."
            )
            flagged = True
        if summary.survival_ratio < 1:
            lines.append("- Emergency fund меньше 1 месяца расходов.")
            flagged = True
        if summary.today_free_cash <= 0:
            lines.append("- Свободного cash сегодня нет — режим экономии.")
            flagged = True
        if not flagged:
            lines.append("- Критичных рисков не обнаружено.")
        return "\n".join(lines)
