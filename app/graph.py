"""LangGraph wiring for PolicyDesk.

Flow:
    START -> intake -> (missing order id?) -> writer            # ask branch
                    -> order -> policy -> planner -> risk -> writer -> END

The approval gate is enforced in `writer`: when `risk` sets
`approval_required` and the request is not yet `approved`, the writer emits a
"pending approval" message and never calls `issue_refund`.
"""

from __future__ import annotations

from functools import partial
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.agents import intake, order, planner, policy, risk, writer
from app.reasoner import Reasoner, get_reasoner
from app.state import SupportState


def _route_after_intake(state: dict[str, Any]) -> str:
    return "writer" if state.get("missing_info") else "order"


def build_graph(reasoner: Reasoner | None = None):
    reasoner = reasoner or get_reasoner()
    g = StateGraph(SupportState)

    g.add_node("intake", partial(intake, reasoner=reasoner))
    g.add_node("order", partial(order, reasoner=reasoner))
    g.add_node("policy", partial(policy, reasoner=reasoner))
    g.add_node("planner", partial(planner, reasoner=reasoner))
    g.add_node("risk", partial(risk, reasoner=reasoner))
    g.add_node("writer", partial(writer, reasoner=reasoner))

    g.add_edge(START, "intake")
    g.add_conditional_edges("intake", _route_after_intake,
                            {"order": "order", "writer": "writer"})
    g.add_edge("order", "policy")
    g.add_edge("policy", "planner")
    g.add_edge("planner", "risk")
    g.add_edge("risk", "writer")
    g.add_edge("writer", END)

    return g.compile()
