"""Badger CFO FastAPI application.

Run:  uvicorn app.main:app --reload

Serves both the JSON API and the installable PWA front-end. When
APP_ACCESS_CODE is set, the API requires the access code (the PWA shell and
static assets stay public so the app can load and show its login screen).
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.api.routes import (
    auth,
    exchanges,
    market,
    plaid,
    portfolio,
    recommendations,
    reports,
    sources,
    tradingview,
    wallets,
    webapp,
)
from app.database import init_db
from app.security.web_auth import require_access
from app.web import routes as web_routes

STATIC_DIR = Path(__file__).parent / "web" / "static"


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


# Public PWA shell + static assets.
app.include_router(web_routes.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Auth + PWA data API (webapp router self-guards every route).
app.include_router(auth.router)
app.include_router(webapp.router)

# Protect the lower-level data/integration routers with the same access code.
_guard = [Depends(require_access)]
app.include_router(sources.router, dependencies=_guard)
app.include_router(plaid.router, dependencies=_guard)
app.include_router(exchanges.router, dependencies=_guard)
app.include_router(wallets.router, dependencies=_guard)
app.include_router(portfolio.router, dependencies=_guard)
app.include_router(reports.router, dependencies=_guard)
app.include_router(recommendations.router, dependencies=_guard)
app.include_router(market.router, dependencies=_guard)

# TradingView webhook stays open (external source; it only stores signals,
# can never trade) — guarding it would break TradingView's POSTs.
app.include_router(tradingview.router)
