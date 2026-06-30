"""Order database tools (reads from a fake JSON 'database')."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from langchain_core.tools import tool

from app.paths import ORDERS_FILE

TOOL_LOOKUP_ORDER = "lookup_order"
TOOL_CHECK_PAYMENT_HISTORY = "check_payment_history"


@lru_cache(maxsize=1)
def _orders() -> dict[str, Any]:
    return json.loads(ORDERS_FILE.read_text())


@tool
def lookup_order(order_id: str) -> dict[str, Any]:
    """Look up an order by its id in the order database.

    Returns the order record, or {"found": False} if the id is unknown.
    """
    order = _orders().get(order_id)
    if order is None:
        return {"found": False, "order_id": order_id}
    return {"found": True, **order}


@tool
def check_payment_history(order_id: str) -> dict[str, Any]:
    """Return the payment history for an order and flag duplicate charges."""
    order = _orders().get(order_id)
    if order is None:
        return {"found": False, "order_id": order_id, "payments": [], "duplicate_charge": False}
    payments = order.get("payments", [])
    amounts = [p["amount"] for p in payments]
    duplicate = len(amounts) > len(set(map(repr, amounts))) or len(payments) > 1
    duplicate_amount = payments[0]["amount"] if duplicate and payments else 0.0
    return {
        "found": True,
        "order_id": order_id,
        "payments": payments,
        "duplicate_charge": duplicate,
        "duplicate_amount": duplicate_amount,
    }
