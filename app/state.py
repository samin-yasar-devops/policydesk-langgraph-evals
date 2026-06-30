"""Shared graph state for PolicyDesk.

`SupportState` is the single object that flows through every node. Two list
fields use additive reducers so the *trajectory* (which tools were called and
which nodes were visited) accumulates across the graph — this trajectory is
what the eval harness inspects.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, Literal, TypedDict

NextAction = Literal["answer", "ask", "refund", "replacement", "escalate"]
RiskLevel = Literal["low", "medium", "high"]


class SupportState(TypedDict, total=False):
    # --- input ---
    user_message: str

    # --- intake ---
    intent: str
    entities: dict[str, Any]
    urgency: str
    missing_info: list[str]

    # --- lookups ---
    order: dict[str, Any] | None
    payment_history: dict[str, Any] | None
    policy_citations: list[dict[str, Any]]

    # --- decision / guardrails ---
    next_action: NextAction
    refund_amount: float
    risk_level: RiskLevel
    approval_required: bool
    approved: bool

    # --- output ---
    final_response: str

    # --- trajectory (accumulated via reducers) ---
    tool_calls: Annotated[list[str], operator.add]
    route: Annotated[list[str], operator.add]


def initial_state(user_message: str, approved: bool = False) -> SupportState:
    """Build a fresh state for one support request."""
    return SupportState(
        user_message=user_message,
        entities={},
        missing_info=[],
        order=None,
        payment_history=None,
        policy_citations=[],
        refund_amount=0.0,
        risk_level="low",
        approval_required=False,
        approved=approved,
        final_response="",
        tool_calls=[],
        route=[],
    )
