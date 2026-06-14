"""CFO math: the formulas everything else is built on.

Freedom Ratio       = Monthly Passive Income / Monthly Expenses
Survival Ratio      = Liquid Cash / Monthly Expenses
Net Worth           = Total Assets - Total Liabilities
Today Free Cash     = Available Cash - Upcoming 14d Obligations - Emergency Buffer
Investment Capacity = Today Free Cash - Personal Spending Allowance
"""

from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import (
    CashEntry,
    CryptoHolding,
    DailySnapshot,
    FinancialAccount,
    UpcomingObligation,
    User,
)

LIABILITY_TYPES = {"credit_card", "loan"}
BANK_TYPES = {"checking", "savings"}


@dataclass
class CfoSummary:
    total_cash: float
    total_bank: float
    total_credit_card_debt: float
    total_loans: float
    total_crypto: float
    total_investments: float
    total_assets: float
    total_liabilities: float
    net_worth: float
    monthly_expenses: float
    passive_income: float
    freedom_ratio: float
    survival_ratio: float
    available_cash: float
    upcoming_obligations_total: float
    emergency_buffer: float
    today_free_cash: float
    personal_spending_allowance: float
    investment_capacity: float
    credit_utilization: float


def freedom_ratio(passive_income: float, monthly_expenses: float) -> float:
    if monthly_expenses <= 0:
        return 0.0
    return passive_income / monthly_expenses


def survival_ratio(liquid_cash: float, monthly_expenses: float) -> float:
    if monthly_expenses <= 0:
        return 0.0
    return liquid_cash / monthly_expenses


def net_worth(total_assets: float, total_liabilities: float) -> float:
    return total_assets - total_liabilities


def today_free_cash(available_cash: float, upcoming_obligations: float, emergency_buffer: float) -> float:
    return available_cash - upcoming_obligations - emergency_buffer


def investment_capacity(free_cash: float, personal_spending_allowance: float) -> float:
    return free_cash - personal_spending_allowance


def personal_spending_allowance(free_cash: float, ratio: float) -> float:
    """Share of free cash the user may spend on themselves; 0 when free cash <= 0."""
    if free_cash <= 0:
        return 0.0
    return round(free_cash * ratio, 2)


def cash_balance(db: Session, user_id: int) -> float:
    income = db.scalar(
        select(func.coalesce(func.sum(CashEntry.amount), 0.0)).where(
            CashEntry.user_id == user_id, CashEntry.type == "cash_income"
        )
    )
    expense = db.scalar(
        select(func.coalesce(func.sum(CashEntry.amount), 0.0)).where(
            CashEntry.user_id == user_id, CashEntry.type == "cash_expense"
        )
    )
    adjustment = db.scalar(
        select(func.coalesce(func.sum(CashEntry.amount), 0.0)).where(
            CashEntry.user_id == user_id, CashEntry.type == "cash_adjustment"
        )
    )
    return float(income) - float(expense) + float(adjustment)


def upcoming_obligations_total(db: Session, user_id: int, horizon_days: int | None = None) -> float:
    horizon = horizon_days or get_settings().obligation_horizon_days
    cutoff = date.today() + timedelta(days=horizon)
    total = db.scalar(
        select(func.coalesce(func.sum(UpcomingObligation.amount), 0.0)).where(
            UpcomingObligation.user_id == user_id,
            UpcomingObligation.status == "pending",
            UpcomingObligation.due_date <= cutoff,
        )
    )
    return float(total)


def compute_summary(db: Session, user: User) -> CfoSummary:
    settings = get_settings()
    accounts = db.scalars(
        select(FinancialAccount).where(FinancialAccount.user_id == user.id)
    ).all()

    total_bank = sum(a.current_balance for a in accounts if a.account_type in BANK_TYPES)
    cc_debt = sum(a.current_balance for a in accounts if a.account_type == "credit_card")
    loans = sum(a.current_balance for a in accounts if a.account_type == "loan")
    investments = sum(a.current_balance for a in accounts if a.account_type == "investment")

    cc_limits = sum(a.credit_limit or 0.0 for a in accounts if a.account_type == "credit_card")
    credit_utilization = (cc_debt / cc_limits) if cc_limits > 0 else 0.0

    holdings = db.scalars(
        select(CryptoHolding).where(CryptoHolding.user_id == user.id)
    ).all()
    total_crypto = sum(h.total_value or 0.0 for h in holdings)

    total_cash = cash_balance(db, user.id)
    liquid = total_cash + total_bank
    assets = liquid + total_crypto + investments
    liabilities = cc_debt + loans
    nw = net_worth(assets, liabilities)

    obligations = upcoming_obligations_total(db, user.id)
    buffer = user.emergency_buffer or settings.emergency_buffer
    free = today_free_cash(liquid, obligations, buffer)
    allowance = personal_spending_allowance(free, settings.personal_spending_ratio)
    capacity = max(investment_capacity(free, allowance), 0.0) if free > 0 else 0.0

    return CfoSummary(
        total_cash=round(total_cash, 2),
        total_bank=round(total_bank, 2),
        total_credit_card_debt=round(cc_debt, 2),
        total_loans=round(loans, 2),
        total_crypto=round(total_crypto, 2),
        total_investments=round(investments, 2),
        total_assets=round(assets, 2),
        total_liabilities=round(liabilities, 2),
        net_worth=round(nw, 2),
        monthly_expenses=user.monthly_expenses_estimate,
        passive_income=user.monthly_passive_income,
        freedom_ratio=round(freedom_ratio(user.monthly_passive_income, user.monthly_expenses_estimate), 4),
        survival_ratio=round(survival_ratio(liquid, user.monthly_expenses_estimate), 2),
        available_cash=round(liquid, 2),
        upcoming_obligations_total=round(obligations, 2),
        emergency_buffer=buffer,
        today_free_cash=round(free, 2),
        personal_spending_allowance=allowance,
        investment_capacity=round(capacity, 2),
        credit_utilization=round(credit_utilization, 4),
    )


def save_snapshot(db: Session, user: User, summary: CfoSummary,
                  pdf_path: str | None = None, image_path: str | None = None) -> DailySnapshot:
    snapshot = DailySnapshot(
        user_id=user.id,
        snapshot_date=date.today(),
        total_cash=summary.total_cash,
        total_bank=summary.total_bank,
        total_credit_card_debt=summary.total_credit_card_debt,
        total_crypto=summary.total_crypto,
        total_investments=summary.total_investments,
        total_assets=summary.total_assets,
        total_liabilities=summary.total_liabilities,
        net_worth=summary.net_worth,
        monthly_expenses_estimate=summary.monthly_expenses,
        passive_income=summary.passive_income,
        freedom_ratio=summary.freedom_ratio,
        survival_ratio=summary.survival_ratio,
        today_free_cash=summary.today_free_cash,
        personal_spending_allowance=summary.personal_spending_allowance,
        investment_capacity=summary.investment_capacity,
        pdf_path=pdf_path,
        image_path=image_path,
    )
    db.add(snapshot)
    db.commit()
    return snapshot
