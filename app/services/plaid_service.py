"""Plaid integration (sandbox-ready, read-only products only).

Money-movement products are rejected at the permissions layer. Without Plaid
credentials all functions degrade to clear errors / no-ops so the rest of the
app keeps working on manual data.
"""

from datetime import datetime

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import ConnectedSource, FinancialAccount, PlaidItem
from app.security.encryption import decrypt_secret, encrypt_secret
from app.security.permissions import filter_plaid_products

PLAID_HOSTS = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com",
}


class PlaidNotConfiguredError(Exception):
    pass


def _base_payload() -> dict:
    settings = get_settings()
    if not settings.plaid_client_id or not settings.plaid_secret:
        raise PlaidNotConfiguredError(
            "PLAID_CLIENT_ID / PLAID_SECRET не заданы. См. docs/PLAID_SANDBOX.md"
        )
    return {"client_id": settings.plaid_client_id, "secret": settings.plaid_secret}


def _host() -> str:
    return PLAID_HOSTS[get_settings().plaid_env]


def create_link_token(user_id: int) -> dict:
    settings = get_settings()
    products = filter_plaid_products(settings.plaid_products.split(","))
    payload = {
        **_base_payload(),
        "user": {"client_user_id": str(user_id)},
        "client_name": "Badger CFO",
        "products": products,
        "country_codes": settings.plaid_country_codes.split(","),
        "language": "en",
    }
    resp = httpx.post(f"{_host()}/link/token/create", json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()


def exchange_public_token(db: Session, user_id: int, public_token: str) -> PlaidItem:
    payload = {**_base_payload(), "public_token": public_token}
    resp = httpx.post(f"{_host()}/item/public_token/exchange", json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    item = PlaidItem(
        user_id=user_id,
        item_id=data["item_id"],
        encrypted_access_token=encrypt_secret(data["access_token"]),
        status="active",
    )
    db.add(item)
    db.add(
        ConnectedSource(
            user_id=user_id,
            source_type="plaid",
            provider_name="plaid",
            display_name=f"Plaid item {data['item_id'][:8]}",
            read_only=True,
        )
    )
    db.commit()
    return item


def sync_accounts(db: Session, user_id: int) -> int:
    """Pull balances for every Plaid item; upsert FinancialAccount rows."""
    items = db.scalars(select(PlaidItem).where(PlaidItem.user_id == user_id)).all()
    synced = 0
    for item in items:
        token = decrypt_secret(item.encrypted_access_token)
        resp = httpx.post(
            f"{_host()}/accounts/balance/get",
            json={**_base_payload(), "access_token": token},
            timeout=20,
        )
        resp.raise_for_status()
        for acct in resp.json().get("accounts", []):
            existing = db.scalars(
                select(FinancialAccount).where(
                    FinancialAccount.user_id == user_id,
                    FinancialAccount.external_id == acct["account_id"],
                )
            ).first()
            balances = acct.get("balances", {})
            fields = dict(
                name=acct.get("name", "Account"),
                institution=item.institution_name,
                account_type=_map_account_type(acct),
                subtype=acct.get("subtype"),
                mask=acct.get("mask"),
                currency=balances.get("iso_currency_code") or "USD",
                current_balance=balances.get("current") or 0.0,
                available_balance=balances.get("available"),
                credit_limit=balances.get("limit"),
                external_id=acct["account_id"],
                external_source="plaid",
                raw_data=acct,
            )
            if existing:
                for key, value in fields.items():
                    setattr(existing, key, value)
            else:
                db.add(FinancialAccount(user_id=user_id, **fields))
            synced += 1
        item.last_successful_sync_at = datetime.utcnow()
    db.commit()
    return synced


def _map_account_type(acct: dict) -> str:
    plaid_type = acct.get("type", "other")
    subtype = acct.get("subtype") or ""
    if plaid_type == "depository":
        return "savings" if subtype == "savings" else "checking"
    if plaid_type == "credit":
        return "credit_card"
    if plaid_type == "loan":
        return "loan"
    if plaid_type == "investment":
        return "investment"
    return "other"
