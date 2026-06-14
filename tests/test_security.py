"""Seed phrase / private key rejection, key permission checks, encryption."""

import pytest

from app.security.api_key_validator import (
    validate_exchange_permissions,
    validate_sensitive_input,
)
from app.security.encryption import decrypt_secret, encrypt_secret, mask_secret
from app.security.permissions import (
    ForbiddenActionError,
    assert_action_allowed,
    filter_plaid_products,
)

SEED_12 = "abandon ability able about above absent absorb abstract absurd abuse access accident"
HEX_KEY = "0x" + "ab" * 32


def test_seed_phrase_rejected():
    verdict = validate_sensitive_input(SEED_12)
    assert not verdict.ok
    assert "seed" in verdict.reason.lower()


def test_private_key_rejected():
    assert not validate_sensitive_input(HEX_KEY).ok


def test_normal_text_accepted():
    assert validate_sensitive_input("Получил 300 cash").ok
    assert validate_sensitive_input("/add_wallet Cold1 Solana 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU").ok


def test_trade_permission_rejected():
    verdict = validate_exchange_permissions(["read", "trade"])
    assert not verdict.ok


def test_withdraw_permission_rejected():
    assert not validate_exchange_permissions(["withdraw"]).ok


def test_read_only_permission_ok():
    verdict = validate_exchange_permissions(["read"])
    assert verdict.ok
    assert not verdict.warnings


def test_unknown_permission_warns():
    verdict = validate_exchange_permissions(["unknown"])
    assert verdict.ok
    assert verdict.warnings


def test_forbidden_actions_raise():
    for action in ("transfer", "trade", "withdraw", "payment_execution"):
        with pytest.raises(ForbiddenActionError):
            assert_action_allowed(action)
    assert_action_allowed("read_balances")  # no exception


def test_plaid_products_filtered():
    assert filter_plaid_products(["transactions", "balance"]) == ["transactions", "balance"]
    with pytest.raises(ForbiddenActionError):
        filter_plaid_products(["transactions", "transfer"])


def test_encryption_roundtrip():
    secret = "super-secret-api-key"
    encrypted = encrypt_secret(secret)
    assert encrypted != secret
    assert decrypt_secret(encrypted) == secret


def test_mask_secret():
    assert mask_secret("abcdefgh") == "****efgh"
    assert "abcd" not in mask_secret("abcdefgh")
