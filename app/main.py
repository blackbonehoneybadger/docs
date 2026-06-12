"""Badger CFO FastAPI application.

Run:  uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.api.routes import (
    exchanges,
    market,
    plaid,
    portfolio,
    recommendations,
    reports,
    sources,
    tradingview,
    wallets,
)
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Badger CFO / Boss My Life",
    description=(
        "Personal finance & investment command center. Read-only by design: "
        "no transfers, no trading, no withdrawals. AI proposes, user approves."
    ),
    version=__version__,
    lifespan=lifespan,
)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "version": __version__, "read_only": True}


app.include_router(sources.router)
app.include_router(plaid.router)
app.include_router(exchanges.router)
app.include_router(wallets.router)
app.include_router(portfolio.router)
app.include_router(reports.router)
app.include_router(recommendations.router)
app.include_router(tradingview.router)
app.include_router(market.router)
