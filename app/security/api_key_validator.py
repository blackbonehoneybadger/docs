"""Validation of user-supplied secrets.

Two jobs:
1. Reject anything that looks like a seed phrase or private key — we never
   store those, full stop.
2. Flag exchange API keys whose detected permissions include trade/withdraw.
"""

import re
from dataclasses import dataclass, field

# BIP-39 seed phrases are 12/15/18/21/24 lowercase words.
_SEED_WORD_COUNTS = {12, 15, 18, 21, 24}
_WORDS_RE = re.compile(r"^[a-z]+(?:\s+[a-z]+)+$")

# Common private key shapes.
_HEX_PRIVKEY_RE = re.compile(r"^(0x)?[0-9a-fA-F]{64}$")
_WIF_RE = re.compile(r"^[5KL][1-9A-HJ-NP-Za-km-z]{50,51}$")  # Bitcoin WIF

FORBIDDEN_PERMISSIONS = {"trade", "withdraw", "withdrawal", "transfer", "payment"}
ALLOWED_PERMISSIONS = {"read", "read_only", "readonly", "view", "balance", "account"}


@dataclass
class ValidationResult:
    ok: bool
    reason: str = ""
    warnings: list[str] = field(default_factory=list)


def looks_like_seed_phrase(text: str) -> bool:
    cleaned = text.strip().lower()
    if not _WORDS_RE.match(cleaned):
        return False
    return len(cleaned.split()) in _SEED_WORD_COUNTS


def looks_like_private_key(text: str) -> bool:
    cleaned = text.strip()
    return bool(_HEX_PRIVKEY_RE.match(cleaned) or _WIF_RE.match(cleaned))


def validate_sensitive_input(text: str) -> ValidationResult:
    """Run on ANY free-form user input before persisting it anywhere."""
    if looks_like_seed_phrase(text):
        return ValidationResult(
            ok=False,
            reason=(
                "Это похоже на seed phrase. Я НИКОГДА не сохраняю seed phrase. "
                "Никому её не отправляй — даже мне. Удали это сообщение."
            ),
        )
    if looks_like_private_key(text):
        return ValidationResult(
            ok=False,
            reason=(
                "Это похоже на private key. Я НИКОГДА не сохраняю приватные ключи. "
                "Используй только публичный адрес кошелька."
            ),
        )
    return ValidationResult(ok=True)


def validate_exchange_permissions(permissions: list[str]) -> ValidationResult:
    """Reject keys that can move money; warn on unknown permissions."""
    normalized = {p.strip().lower() for p in permissions if p.strip()}
    forbidden = normalized & FORBIDDEN_PERMISSIONS
    if forbidden:
        return ValidationResult(
            ok=False,
            reason=(
                f"API-ключ имеет запрещённые права: {', '.join(sorted(forbidden))}. "
                "Подключай только read-only ключи."
            ),
        )
    unknown = normalized - ALLOWED_PERMISSIONS
    warnings = (
        [f"Неизвестные права у ключа: {', '.join(sorted(unknown))}. Проверь, что ключ read-only."]
        if unknown
        else []
    )
    return ValidationResult(ok=True, warnings=warnings)
