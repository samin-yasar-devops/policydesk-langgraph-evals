"""Order agent: read the fake order database; pull payment history when relevant."""

from __future__ import annotations

from typing import Any

from app.reasoner import DOUBLE_CHARGE, Reasoner
from app.tools import (
    TOOL_CHECK_PAYMENT_HISTORY,
    TOOL_LOOKUP_ORDER,
    check_payment_history,
    lookup_order,
)


def order(state: dict[str, Any], reasoner: Reasoner) -> dict[str, Any]:
    updates: dict[str, Any] = {"route": ["order"]}
    tools: list[str] = []
    order_id = (state.get("entities") or {}).get("order_id")
    if order_id:
        result = lookup_order.invoke({"order_id": order_id})
        tools.append(TOOL_LOOKUP_ORDER)
        if result.get("found"):
            updates["order"] = result
        if state.get("intent") == DOUBLE_CHARGE:
            updates["payment_history"] = check_payment_history.invoke({"order_id": order_id})
            tools.append(TOOL_CHECK_PAYMENT_HISTORY)
    if tools:
        updates["tool_calls"] = tools
    return updates
