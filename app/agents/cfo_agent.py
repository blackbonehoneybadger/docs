"""CFO Agent: cashflow, free cash, obligations, net worth, ratios."""

from sqlalchemy.orm import Session

from app.models import User
from app.services import cfo_service
from app.services.cfo_service import CfoSummary


class CfoAgent:
    name = "cfo"

    def analyze(self, db: Session, user: User) -> CfoSummary:
        return cfo_service.compute_summary(db, user)

    def render_overview(self, s: CfoSummary) -> str:
        goal_pct = min(s.freedom_ratio * 100, 100)
        lines = [
            "1. Общая картина",
            "",
            f"Net Worth: ${s.net_worth:,.2f}",
            f"Total Assets: ${s.total_assets:,.2f}",
            f"Total Liabilities: ${s.total_liabilities:,.2f}",
            "",
            f"Freedom Ratio: {s.freedom_ratio * 100:.1f}%",
            f"Survival Ratio: {s.survival_ratio:.1f} месяцев",
            "",
            "Цель 2030:",
            "Пассивный доход должен покрыть 100% расходов.",
            f"Сейчас покрыто: {goal_pct:.1f}%.",
            f"До цели осталось: {max(100 - goal_pct, 0):.1f}%.",
        ]
        return "\n".join(lines)

    def render_cashflow(self, s: CfoSummary) -> str:
        lines = [
            "4. Сегодняшний cashflow",
            "",
            f"Доступно сейчас: ${s.available_cash:,.2f}",
            f"Нужно зарезервировать под платежи: ${s.upcoming_obligations_total:,.2f}",
            f"Emergency buffer: ${s.emergency_buffer:,.2f}",
            f"Свободно сегодня: ${s.today_free_cash:,.2f}",
            "",
            "Рекомендация:",
            f"- Можно потратить на себя: ${s.personal_spending_allowance:,.2f}",
            f"- Лучше оставить в cash: ${max(s.today_free_cash - s.personal_spending_allowance - s.investment_capacity, 0):,.2f}",
            f"- Можно инвестировать: ${s.investment_capacity:,.2f}",
        ]
        if s.today_free_cash <= 0:
            lines += ["", "Сегодня инвестиций не делать. Главная цель — сохранить cashflow."]
        return "\n".join(lines)
