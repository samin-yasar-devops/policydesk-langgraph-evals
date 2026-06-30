"""Policy agent: search local sanitized policy docs for grounding citations."""

from __future__ import annotations

from typing import Any

from app.reasoner import IDENTITY, LATE_DELIVERY, PRIVACY_REQUEST, Reasoner
from app.tools import TOOL_SEARCH_POLICIES, search_policies

_QUERY_BY_INTENT = {
    LATE_DELIVERY: "shipping delivery late sla",
    IDENTITY: "identity verification",
    PRIVACY_REQUEST: "privacy address account",
}


def policy(state: dict[str, Any], reasoner: Reasoner) -> dict[str, Any]:
    query = _QUERY_BY_INTENT.get(state.get("intent"), "refund damage return window")
    citations = search_policies.invoke({"query": query})
    return {
        "policy_citations": citations,
        "tool_calls": [TOOL_SEARCH_POLICIES],
        "route": ["policy"],
    }
