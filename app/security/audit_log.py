"""Audit logging helper. Secrets must never reach this module."""

from sqlalchemy.orm import Session

from app.models.audit import AuditLogEntry

_SENSITIVE_KEYS = {"api_key", "api_secret", "passphrase", "access_token", "token", "secret", "password"}


def _scrub(details: dict | None) -> dict | None:
    if not details:
        return details
    return {k: ("***" if k.lower() in _SENSITIVE_KEYS else v) for k, v in details.items()}


def log_event(
    db: Session,
    event_type: str,
    action: str,
    user_id: int | None = None,
    actor: str = "system",
    details: dict | None = None,
) -> AuditLogEntry:
    entry = AuditLogEntry(
        user_id=user_id,
        event_type=event_type,
        actor=actor,
        action=action,
        details=_scrub(details),
    )
    db.add(entry)
    db.commit()
    return entry
