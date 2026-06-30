"""CLI entry point.

    python -m app.run "My package arrived damaged. Can I get a refund?"
    python -m app.run "I want a full refund for order C3071." --approve
"""

from __future__ import annotations

import argparse

from dotenv import load_dotenv

from app.graph import build_graph
from app.state import initial_state


def run(message: str, approved: bool = False) -> dict:
    graph = build_graph()
    return graph.invoke(initial_state(message, approved=approved))


def _print(result: dict) -> None:
    print("\n=== Response ===")
    print(result.get("final_response", ""))
    print("\n=== Trajectory ===")
    print(f"route          : {' -> '.join(result.get('route', []))}")
    print(f"tools called   : {', '.join(result.get('tool_calls', [])) or '(none)'}")
    print(f"intent         : {result.get('intent')}")
    print(f"next_action    : {result.get('next_action')}")
    print(f"risk_level     : {result.get('risk_level')}")
    print(f"approval_req.  : {result.get('approval_required')}")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="PolicyDesk support agent")
    parser.add_argument("message", help="the customer's support request")
    parser.add_argument("--approve", action="store_true",
                        help="simulate a human approving a gated action")
    args = parser.parse_args()
    _print(run(args.message, approved=args.approve))


if __name__ == "__main__":
    main()
