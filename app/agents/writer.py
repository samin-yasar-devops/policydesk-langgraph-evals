"""Response writer: produce the final customer-facing reply and execute the
approved action (if any). Never issues a refund that is pending approval; never
invents compensation."""

from __future__ import annotations

from typing import Any

from app.reasoner import INJECTION, PRIVACY_REQUEST, Reasoner
from app.tools import (
    TOOL_CREATE_TICKET,
    TOOL_ISSUE_REFUND,
    create_ticket,
    issue_refund,
)


def writer(state: dict[str, Any], reasoner: Reasoner) -> dict[str, Any]:
    updates: dict[str, Any] = {"route": ["writer"]}
    tools: list[str] = []

    intent = state.get("intent")
    next_action = state.get("next_action")
    order = state.get("order") or {}
    order_id = order.get("order_id") or (state.get("entities") or {}).get("order_id")

    if state.get("missing_info"):
        pass  # ask for the order id; no action
    elif intent in (INJECTION, PRIVACY_REQUEST):
        pass  # refuse; no action
    elif next_action == "ask":
        pass  # identity verification request; no action
    elif state.get("approval_required") and not state.get("approved"):
        pass  # refund pending human approval — must NOT issue it
    elif next_action == "refund":
        issue_refund.invoke({"order_id": order_id, "amount": state.get("refund_amount", 0.0)})
        tools.append(TOOL_ISSUE_REFUND)
    elif next_action == "escalate":
        create_ticket.invoke({"order_id": order_id, "reason": "customer escalation"})
        tools.append(TOOL_CREATE_TICKET)

    updates["final_response"] = reasoner.write_response(state)
    if tools:
        updates["tool_calls"] = tools
    return updates
