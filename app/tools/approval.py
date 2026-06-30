"""Human-approval gate tool (mock)."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

TOOL_REQUEST_HUMAN_APPROVAL = "request_human_approval"


@tool
def request_human_approval(action: str, reason: str) -> dict[str, Any]:
    """Record a request for human approval of a sensitive action (mock).

    Returns a pending approval ticket. The action is NOT executed until a human
    grants approval out of band.
    """
    return {
        "ok": True,
        "status": "pending_approval",
        "action": action,
        "reason": reason,
        "approval_id": f"AP-{abs(hash((action, reason))) % 100000:05d}",
    }
