"""Fernet encryption for secrets at rest (Plaid tokens, exchange API keys).

Secrets are never logged and never echoed back to Telegram or API responses.
"""

from cryptography.fernet import Fernet

from app.config import get_settings


class EncryptionError(Exception):
    pass


def _fernet() -> Fernet:
    key = get_settings().fernet_key
    if not key:
        raise EncryptionError(
            "FERNET_KEY is not set. Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_secret(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_secret(ciphertext: str) -> str:
    return _fernet().decrypt(ciphertext.encode()).decode()


def mask_secret(secret: str, visible: int = 4) -> str:
    """Safe display form: never show more than the last few characters."""
    if not secret:
        return ""
    if len(secret) <= visible:
        return "*" * len(secret)
    return "*" * (len(secret) - visible) + secret[-visible:]
