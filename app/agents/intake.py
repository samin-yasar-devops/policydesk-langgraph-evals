"""Intake agent: extract intent, entities, urgency, and missing information."""

from __future__ import annotations

from typing import Any

from app.reasoner import ORDER_REQUIRED, Reasoner


def intake(state: dict[str, Any], reasoner: Reasoner) -> dict[str, Any]:
    res = reasoner.extract_intake(state["user_message"])
    entities = {"order_id": res.order_id} if res.order_id else {}
    missing = ["order_id"] if (res.intent in ORDER_REQUIRED and not res.order_id) else []
    return {
        "intent": res.intent,
        "entities": entities,
        "urgency": res.urgency,
        "missing_info": missing,
        "route": ["intake"],
    }
