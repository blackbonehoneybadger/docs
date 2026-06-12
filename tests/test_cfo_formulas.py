"""CFO formula unit tests + integration through compute_summary."""

from datetime import date, timedelta

from app.database import SessionLocal
from app.models import CashEntry, CryptoHolding, FinancialAccount, UpcomingObligation, User
from app.services import cfo_service


def test_freedom_ratio():
    assert cfo_service.freedom_ratio(1000, 2000) == 0.5
    assert cfo_service.freedom_ratio(2000, 2000) == 1.0
    assert cfo_service.freedom_ratio(100, 0) == 0.0


def test_survival_ratio():
    assert cfo_service.survival_ratio(6000, 2000) == 3.0


def test_net_worth():
    assert cfo_service.net_worth(10000, 4000) == 6000


def test_today_free_cash():
    assert cfo_service.today_free_cash(1000, 500, 200) == 300


def test_investment_capacity():
    assert cfo_service.investment_capacity(300, 90) == 210


def test_personal_spending_allowance_zero_when_negative():
    assert cfo_service.personal_spending_allowance(-50, 0.3) == 0.0
    assert cfo_service.personal_spending_allowance(100, 0.3) == 30.0


def test_compute_summary_end_to_end():
    with SessionLocal() as db:
        user = User(name="Test", monthly_expenses_estimate=2000.0,
                    monthly_passive_income=500.0, emergency_buffer=200.0)
        db.add(user)
        db.commit()

        db.add_all([
            FinancialAccount(user_id=user.id, name="Chase", account_type="checking",
                             current_balance=1500.0),
            FinancialAccount(user_id=user.id, name="Capital One", account_type="credit_card",
                             current_balance=400.0, credit_limit=1000.0),
            CashEntry(user_id=user.id, amount=300.0, type="cash_income"),
            CashEntry(user_id=user.id, amount=50.0, type="cash_expense"),
            CryptoHolding(user_id=user.id, symbol="BTC", amount=0.01, total_value=600.0),
            UpcomingObligation(user_id=user.id, name="Car lease", amount=399.0,
                               due_date=date.today() + timedelta(days=5)),
            UpcomingObligation(user_id=user.id, name="Far away", amount=999.0,
                               due_date=date.today() + timedelta(days=60)),
        ])
        db.commit()

        s = cfo_service.compute_summary(db, user)

        assert s.total_cash == 250.0
        assert s.total_bank == 1500.0
        assert s.total_credit_card_debt == 400.0
        assert s.total_crypto == 600.0
        assert s.total_assets == 250.0 + 1500.0 + 600.0
        assert s.total_liabilities == 400.0
        assert s.net_worth == 1950.0
        # only the 14-day obligation counts
        assert s.upcoming_obligations_total == 399.0
        assert s.today_free_cash == 1750.0 - 399.0 - 200.0
        assert s.credit_utilization == 0.4
        assert s.freedom_ratio == 0.25
