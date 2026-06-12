"""Hard capability boundary: actions the system can never perform.

The allowlist/denylist below is checked before any integration call.
There is intentionally NO code path that moves money anywhere in the app.
"""

FORBIDDEN_ACTIONS = {
    "transfer",
    "payment_initiation",
    "ach_movement",
    "money_movement",
    "payment_execution",
    "trade",
    "order_create",
    "withdraw",
    "withdrawal",
}

ALLOWED_PLAID_PRODUCTS = {"transactions", "balance", "liabilities", "investments"}
FORBIDDEN_PLAID_PRODUCTS = {"transfer", "payment_initiation", "standing_orders"}


class ForbiddenActionError(Exception):
    pass


def assert_action_allowed(action: str) -> None:
    if action.strip().lower() in FORBIDDEN_ACTIONS:
        raise ForbiddenActionError(
            f"Action '{action}' is permanently forbidden: the system is read-only by design."
        )


def filter_plaid_products(products: list[str]) -> list[str]:
    """Keep only read-only Plaid products; raise on explicit money-movement ones."""
    result = []
    for product in products:
        p = product.strip().lower()
        if p in FORBIDDEN_PLAID_PRODUCTS:
            raise ForbiddenActionError(f"Plaid product '{p}' is forbidden (money movement).")
        if p in ALLOWED_PLAID_PRODUCTS:
            result.append(p)
    return result
