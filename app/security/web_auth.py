"""Access gate for the web app / API.

When APP_ACCESS_CODE is set, every protected route requires the code
(via the httponly `badger_auth` cookie set at login, or an X-Access-Code
header). Empty code = local development mode (open).
"""

from fastapi import HTTPException, Request, status

from app.config import get_settings


def access_required() -> bool:
    return bool(get_settings().app_access_code)


def check_code(request: Request) -> bool:
    code = get_settings().app_access_code
    if not code:
        return True
    provided = request.cookies.get("badger_auth") or request.headers.get("X-Access-Code")
    return provided == code


def require_access(request: Request) -> None:
    if not check_code(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access code required",
        )
