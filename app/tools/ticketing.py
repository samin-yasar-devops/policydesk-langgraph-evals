"""Ticketing / escalation tool (mock)."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

TOOL_CREATE_TICKET = "create_ticket"


@tool
def create_ticket(order_id: str, reason: str) -> dict[str, Any]:
    """Open a support ticket / escalation for an order (mock)."""
    return {
        "ok": True,
        "action": "ticket_created",
        "order_id": order_id,
        "reason": reason,
        "ticket_id": f"TK-{order_id}",
    }
