"""Risk / compliance agent: the guardrail.

Deterministic rules over the plan. High-value refunds (> $100) are blocked
behind a human-approval gate: this node records the approval request and does
NOT issue the refund. Sensitive intents (privacy, identity, prompt injection)
are marked high risk.
"""

from __future__ import annotations

from typing import Any

from app.reasoner import DOUBLE_CHARGE, IDENTITY, INJECTION, PRIVACY_REQUEST, Reasoner
from app.tools import TOOL_REQUEST_HUMAN_APPROVAL, request_human_approval

APPROVAL_THRESHOLD = 100.0


def risk(state: dict[str, Any], reasoner: Reasoner) -> dict[str, Any]:
    intent = state.get("intent")
    next_action = state.get("next_action")
    order = state.get("order") or {}

    refund_amount = 0.0
    if next_action == "refund":
        if intent == DOUBLE_CHARGE:
            ph = state.get("payment_history") or {}
            refund_amount = ph.get("duplicate_amount") or order.get("amount", 0.0)
        else:
            refund_amount = order.get("amount", 0.0)

    updates: dict[str, Any] = {"refund_amount": refund_amount, "route": ["risk"]}

    if next_action == "refund" and refund_amount > APPROVAL_THRESHOLD:
        request_human_approval.invoke({
            "action": f"refund ${refund_amount:.2f} for order {order.get('order_id')}",
            "reason": "refund amount exceeds the auto-approval limit",
        })
        updates.update(
            approval_required=True,
            risk_level="high",
            tool_calls=[TOOL_REQUEST_HUMAN_APPROVAL],
        )
    elif intent in (PRIVACY_REQUEST, IDENTITY, INJECTION):
        updates.update(approval_required=False, risk_level="high")
    elif next_action in ("refund", "escalate"):
        updates.update(approval_required=False, risk_level="medium")
    else:
        updates.update(approval_required=False, risk_level="low")

    return updates
