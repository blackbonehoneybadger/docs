"""Outbound Telegram messaging via Bot API (plain HTTPS, no extra deps)."""

from pathlib import Path

import httpx
from sqlalchemy import select

from app.config import get_settings

API = "https://api.telegram.org"


def _default_chat_id() -> str | None:
    """Use the first registered user's chat id when none is given."""
    from app.database import SessionLocal
    from app.models import User

    with SessionLocal() as db:
        user = db.scalars(select(User).where(User.telegram_chat_id.is_not(None))).first()
        return user.telegram_chat_id if user else None


def _token() -> str | None:
    return get_settings().telegram_bot_token or None


def send_telegram_message(text: str, chat_id: str | None = None) -> bool:
    token = _token()
    chat = chat_id or _default_chat_id()
    if not token or not chat:
        return False
    try:
        # Telegram caps messages at 4096 chars — split long reports.
        for chunk_start in range(0, len(text), 4000):
            httpx.post(
                f"{API}/bot{token}/sendMessage",
                json={"chat_id": chat, "text": text[chunk_start:chunk_start + 4000]},
                timeout=15,
            )
        return True
    except Exception:
        return False


def send_telegram_document(path: Path, chat_id: str | None = None, caption: str = "") -> bool:
    token = _token()
    chat = chat_id or _default_chat_id()
    if not token or not chat or not path.exists():
        return False
    try:
        with open(path, "rb") as fh:
            httpx.post(
                f"{API}/bot{token}/sendDocument",
                data={"chat_id": chat, "caption": caption},
                files={"document": (path.name, fh)},
                timeout=60,
            )
        return True
    except Exception:
        return False


def send_telegram_photo(path: Path, chat_id: str | None = None, caption: str = "") -> bool:
    token = _token()
    chat = chat_id or _default_chat_id()
    if not token or not chat or not path.exists():
        return False
    try:
        with open(path, "rb") as fh:
            httpx.post(
                f"{API}/bot{token}/sendPhoto",
                data={"chat_id": chat, "caption": caption},
                files={"photo": (path.name, fh)},
                timeout=60,
            )
        return True
    except Exception:
        return False
