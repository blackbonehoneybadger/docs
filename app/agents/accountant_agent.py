"""Accountant Agent: categorization, recurring payments, due dates."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FinancialAccount, Transaction, UpcomingObligation

# Naive keyword categorizer; replace with a smarter model later.
CATEGORY_KEYWORDS = {
    "еда": "food", "food": "food", "groceries": "food", "продукты": "food",
    "бензин": "transport", "gas": "transport", "uber": "transport",
    "аренда": "housing", "rent": "housing", "lease": "housing",
    "страховка": "insurance", "insurance": "insurance",
    "телефон": "phone", "phone": "phone",
    "подписка": "subscription", "subscription": "subscription",
    "netflix": "subscription", "spotify": "subscription",
    "работа": "income", "salary": "income", "зарплата": "income",
}


class AccountantAgent:
    name = "accountant"

    def categorize(self, description: str | None) -> str:
        if not description:
            return "other"
        lowered = description.lower()
        for keyword, category in CATEGORY_KEYWORDS.items():
            if keyword in lowered:
                return category
        return "other"

    def find_subscriptions(self, db: Session, user_id: int) -> list[Transaction]:
        txns = db.scalars(
            select(Transaction).where(Transaction.user_id == user_id)
        ).all()
        return [t for t in txns if self.categorize(t.description) == "subscription"]

    def upcoming(self, db: Session, user_id: int) -> list[UpcomingObligation]:
        return list(
            db.scalars(
                select(UpcomingObligation)
                .where(
                    UpcomingObligation.user_id == user_id,
                    UpcomingObligation.status == "pending",
                )
                .order_by(UpcomingObligation.due_date)
            )
        )

    def render_obligations(self, db: Session, user_id: int) -> str:
        obligations = self.upcoming(db, user_id)
        lines = ["3. Ближайшие платежи", "", "Следующие 14 дней:", ""]
        total = 0.0
        today = date.today()
        horizon = [o for o in obligations if (o.due_date - today).days <= 14]
        if not horizon:
            lines.append("- Нет платежей в ближайшие 14 дней (или данные не внесены).")
        for o in horizon:
            days = (o.due_date - today).days
            lines.append(f"- {o.name}: ${o.amount:,.2f}, через {days} дн.")
            total += o.amount
        lines += ["", f"Total upcoming obligations: ${total:,.2f}"]
        return "\n".join(lines)

    def render_banks(self, db: Session, user_id: int) -> str:
        accounts = db.scalars(
            select(FinancialAccount).where(FinancialAccount.user_id == user_id)
        ).all()
        lines = ["2. Банки и карты", ""]
        if not accounts:
            lines.append("Нет добавленных счетов. Используй /add_card или /connect_bank.")
        for a in accounts:
            if a.account_type == "credit_card":
                util = (a.current_balance / a.credit_limit * 100) if a.credit_limit else 0
                lines += [
                    f"{a.name}:",
                    f"- Balance owed: ${a.current_balance:,.2f}",
                    f"- Credit limit: ${a.credit_limit or 0:,.2f}",
                    f"- Utilization: {util:.0f}%",
                ]
                if a.minimum_payment:
                    lines.append(f"- Minimum payment: ${a.minimum_payment:,.2f}")
                if a.next_due_date:
                    lines.append(f"- Due date: {a.next_due_date.isoformat()}")
                lines.append("")
            elif a.account_type in ("checking", "savings"):
                lines += [
                    f"{a.name}:",
                    f"- Balance: ${a.current_balance:,.2f}",
                ]
                if a.available_balance is not None:
                    lines.append(f"- Available: ${a.available_balance:,.2f}")
                lines.append("")
        return "\n".join(lines).rstrip()
