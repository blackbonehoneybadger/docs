"""JSON API consumed by the PWA front-end. All routes require the access code
(when one is configured). Thin wrappers over the existing services/agents.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.accountant_agent import AccountantAgent
from app.agents.cfo_agent import CfoAgent
from app.agents.crypto_agent import CryptoAgent
from app.agents.orchestrator import OrchestratorAgent
from app.agents.risk_agent import RiskAgent
from app.api.deps import get_or_create_default_user
from app.config import get_settings
from app.database import get_db
from app.models import CashEntry, FinancialAccount, InvestmentRecommendation, UpcomingObligation
from app.security.web_auth import require_access
from app.services import cfo_service, market_service

router = APIRouter(prefix="/api", tags=["webapp"], dependencies=[Depends(require_access)])


# ---------------------------------------------------------------- dashboard
@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    s = cfo_service.compute_summary(db, user)
    goal_pct = min(s.freedom_ratio * 100, 100)
    return {
        "name": user.name,
        "date": date.today().isoformat(),
        "net_worth": s.net_worth,
        "total_assets": s.total_assets,
        "total_liabilities": s.total_liabilities,
        "total_cash": s.total_cash,
        "total_bank": s.total_bank,
        "total_crypto": s.total_crypto,
        "total_credit_card_debt": s.total_credit_card_debt,
        "available_cash": s.available_cash,
        "today_free_cash": s.today_free_cash,
        "personal_spending_allowance": s.personal_spending_allowance,
        "investment_capacity": s.investment_capacity,
        "upcoming_obligations_total": s.upcoming_obligations_total,
        "emergency_buffer": s.emergency_buffer,
        "freedom_ratio": s.freedom_ratio,
        "survival_ratio": s.survival_ratio,
        "credit_utilization": s.credit_utilization,
        "goal_progress_percent": round(goal_pct, 1),
        "monthly_expenses": s.monthly_expenses,
        "passive_income": s.passive_income,
    }


@router.get("/portfolio")
def portfolio(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    agent = CryptoAgent()
    holdings = agent.holdings(db, user.id)
    total = agent.total_value(holdings)
    return {
        "total_value": total,
        "exchange_exposure_percent": round(agent.exchange_exposure(holdings) * 100, 1),
        "holdings": [
            {
                "symbol": h.symbol,
                "amount": h.amount,
                "value": h.total_value or 0.0,
                "location": h.location,
                "allocation_percent": round(
                    (h.total_value or 0.0) / total * 100, 1
                ) if total else 0.0,
                "action": agent.suggest_action(db, user.id, h),
            }
            for h in holdings
        ],
    }


@router.get("/banks")
def banks(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    rows = db.scalars(
        select(FinancialAccount).where(FinancialAccount.user_id == user.id)
    ).all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "type": a.account_type,
            "balance": a.current_balance,
            "available": a.available_balance,
            "credit_limit": a.credit_limit,
            "utilization": round(a.current_balance / a.credit_limit * 100, 1)
            if a.credit_limit else None,
            "next_due_date": a.next_due_date,
        }
        for a in rows
    ]


@router.get("/obligations")
def obligations(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    rows = AccountantAgent().upcoming(db, user.id)
    today = date.today()
    return [
        {
            "id": o.id,
            "name": o.name,
            "amount": o.amount,
            "due_date": o.due_date.isoformat(),
            "days_left": (o.due_date - today).days,
            "frequency": o.frequency,
        }
        for o in rows
    ]


@router.get("/report")
def report(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    text = OrchestratorAgent().build_daily_report(db, user)
    return {"text": text}


@router.get("/risk")
def risk(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    s = cfo_service.compute_summary(db, user)
    return {"report": RiskAgent().render_risks(s)}


@router.get("/recommendations")
def recommendations(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    rows = db.scalars(
        select(InvestmentRecommendation).where(
            InvestmentRecommendation.user_id == user.id,
            InvestmentRecommendation.recommendation_date == date.today(),
        )
    ).all()
    if not rows:
        s = cfo_service.compute_summary(db, user)
        _, rows = OrchestratorAgent().build_daily_recommendation(db, user, s)
    return [
        {
            "id": r.id,
            "type": r.recommendation_type,
            "symbol": r.symbol,
            "amount_suggested": r.amount_suggested,
            "reason": r.reason,
            "risk_level": r.risk_level,
            "confidence": r.confidence,
            "status": r.status,
        }
        for r in rows
    ]


# ---------------------------------------------------------------- mutations
class CashIn(BaseModel):
    amount: float
    type: str  # cash_income / cash_expense
    description: str | None = None


class CardIn(BaseModel):
    name: str
    account_type: str = "credit_card"
    current_balance: float = 0.0
    credit_limit: float | None = None


class ObligationIn(BaseModel):
    name: str
    amount: float
    due_date: date
    frequency: str = "one_time"


@router.post("/cash")
def add_cash(payload: CashIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    if payload.type not in ("cash_income", "cash_expense", "cash_adjustment"):
        raise HTTPException(status_code=400, detail="bad type")
    db.add(CashEntry(user_id=user.id, amount=abs(payload.amount),
                     type=payload.type, description=payload.description))
    db.commit()
    return {"status": "ok"}


@router.post("/card")
def add_card(payload: CardIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    db.add(FinancialAccount(
        user_id=user.id, name=payload.name, account_type=payload.account_type,
        current_balance=payload.current_balance, credit_limit=payload.credit_limit,
        external_source="manual",
    ))
    db.commit()
    return {"status": "ok"}


@router.post("/obligations")
def add_obligation(payload: ObligationIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    db.add(UpcomingObligation(user_id=user.id, **payload.model_dump()))
    db.commit()
    return {"status": "ok"}


@router.post("/recommendations/{rec_id}/{decision}")
def decide(rec_id: int, decision: str, db: Session = Depends(get_db)):
    if decision not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="bad decision")
    rec = db.get(InvestmentRecommendation, rec_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="not found")
    rec.status = "approved" if decision == "approve" else "rejected"
    db.commit()
    return {"status": rec.status}


@router.post("/sync")
def sync(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    for symbol in ("BTC", "ETH", "SOL"):
        market_service.sync_price(db, symbol)
    updated = market_service.revalue_holdings(db, user.id)
    return {"status": "ok", "holdings_updated": updated}


@router.get("/settings")
def settings_info(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    return {
        "name": user.name,
        "monthly_expenses": user.monthly_expenses_estimate,
        "passive_income": user.monthly_passive_income,
        "emergency_buffer": user.emergency_buffer,
        "read_only": True,
    }


class ProfileIn(BaseModel):
    name: str | None = None
    monthly_expenses: float | None = None
    passive_income: float | None = None
    emergency_buffer: float | None = None


@router.post("/settings")
def update_settings(payload: ProfileIn, db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    if payload.name is not None:
        user.name = payload.name
    if payload.monthly_expenses is not None:
        user.monthly_expenses_estimate = payload.monthly_expenses
    if payload.passive_income is not None:
        user.monthly_passive_income = payload.passive_income
    if payload.emergency_buffer is not None:
        user.emergency_buffer = payload.emergency_buffer
    db.commit()
    return {"status": "ok"}
