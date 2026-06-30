"""Refund tool — the gated, irreversible-style action (mocked)."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

TOOL_ISSUE_REFUND = "issue_refund"


@tool
def issue_refund(order_id: str, amount: float) -> dict[str, Any]:
    """Issue a refund for an order (mock). This is a sensitive, irreversible
    action and must only be called after policy and risk checks have passed."""
    return {
        "ok": True,
        "action": "refund_issued",
        "order_id": order_id,
        "amount": round(float(amount), 2),
        "reference": f"RF-{order_id}",
    }
