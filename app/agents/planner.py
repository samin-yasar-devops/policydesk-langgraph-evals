"""Resolution planner: decide the next action (answer, ask, refund, replacement, escalate)."""

from __future__ import annotations

from typing import Any

from app.reasoner import Reasoner


def planner(state: dict[str, Any], reasoner: Reasoner) -> dict[str, Any]:
    decision = reasoner.decide_action(state)
    return {"next_action": decision.next_action, "route": ["planner"]}
