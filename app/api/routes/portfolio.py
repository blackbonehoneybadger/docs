"""Portfolio overview, allocation, and risk."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.crypto_agent import CryptoAgent
from app.agents.risk_agent import RiskAgent
from app.api.deps import get_or_create_default_user
from app.database import get_db
from app.services import cfo_service

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("")
def portfolio(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    summary = cfo_service.compute_summary(db, user)
    holdings = CryptoAgent().holdings(db, user.id)
    return {
        "net_worth": summary.net_worth,
        "total_assets": summary.total_assets,
        "total_liabilities": summary.total_liabilities,
        "total_crypto": summary.total_crypto,
        "freedom_ratio": summary.freedom_ratio,
        "survival_ratio": summary.survival_ratio,
        "holdings": [
            {"symbol": h.symbol, "amount": h.amount, "value": h.total_value,
             "location": h.location}
            for h in holdings
        ],
    }


@router.get("/allocation")
def allocation(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    agent = CryptoAgent()
    holdings = agent.holdings(db, user.id)
    total = agent.total_value(holdings)
    by_symbol: dict[str, float] = {}
    for h in holdings:
        by_symbol[h.symbol] = by_symbol.get(h.symbol, 0.0) + (h.total_value or 0.0)
    return {
        "total_value": total,
        "allocation": {
            symbol: round(value / total * 100, 2) if total > 0 else 0.0
            for symbol, value in by_symbol.items()
        },
        "exchange_exposure_percent": round(agent.exchange_exposure(holdings) * 100, 2),
    }


@router.get("/risk")
def risk(db: Session = Depends(get_db)):
    user = get_or_create_default_user(db)
    summary = cfo_service.compute_summary(db, user)
    return {
        "report": RiskAgent().render_risks(summary),
        "credit_utilization": summary.credit_utilization,
        "survival_ratio": summary.survival_ratio,
        "free_cash": summary.today_free_cash,
    }
