"""Deterministic, sanitized fake tools.

None of these touch a real service (no Stripe, Gmail, Slack, or live database).
They read local JSON/Markdown so the whole agent is reproducible and safe to
open-source. Tool *names* are also recorded into the graph trajectory; the
constants below are the single source of truth for those names.
"""

from app.tools.approval import TOOL_REQUEST_HUMAN_APPROVAL, request_human_approval
from app.tools.order_lookup import (
    TOOL_CHECK_PAYMENT_HISTORY,
    TOOL_LOOKUP_ORDER,
    check_payment_history,
    lookup_order,
)
from app.tools.policy_search import TOOL_SEARCH_POLICIES, search_policies
from app.tools.refund import TOOL_ISSUE_REFUND, issue_refund
from app.tools.ticketing import TOOL_CREATE_TICKET, create_ticket

__all__ = [
    "lookup_order",
    "check_payment_history",
    "search_policies",
    "issue_refund",
    "request_human_approval",
    "create_ticket",
    "TOOL_LOOKUP_ORDER",
    "TOOL_CHECK_PAYMENT_HISTORY",
    "TOOL_SEARCH_POLICIES",
    "TOOL_ISSUE_REFUND",
    "TOOL_REQUEST_HUMAN_APPROVAL",
    "TOOL_CREATE_TICKET",
]
