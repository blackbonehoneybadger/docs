"""Access-code login for the web app."""

from fastapi import APIRouter, Response
from pydantic import BaseModel

from app.config import get_settings
from app.security.web_auth import access_required

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginIn(BaseModel):
    code: str


@router.get("/status")
def status():
    """Tell the front-end whether a code is required at all."""
    return {"access_required": access_required()}


@router.post("/login")
def login(payload: LoginIn, response: Response):
    code = get_settings().app_access_code
    if not code:
        return {"status": "ok", "note": "open mode"}
    if payload.code != code:
        return Response(status_code=401)
    # 30 days, httponly so JS can't leak it; lax keeps it on top-level nav.
    response.set_cookie(
        "badger_auth", payload.code, max_age=60 * 60 * 24 * 30,
        httponly=True, samesite="lax",
    )
    return {"status": "ok"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("badger_auth")
    return {"status": "ok"}
