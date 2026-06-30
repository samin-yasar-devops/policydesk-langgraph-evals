"""Run the eval suite and print a behavior report.

    python -m evals.run_evals

Default backend is the deterministic stub: no API key, no tokens, reproducible.
Set POLICYDESK_LLM=claude to run the same cases through Claude (final-text
checks then become loose; tool/state/route checks remain the signal).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from app.graph import build_graph
from app.state import initial_state
from evals.evaluators import evaluate

CASES_FILE = Path(__file__).resolve().parent / "cases.yaml"
TRACES_DIR = Path(__file__).resolve().parent / "traces"

_STATE_KEYS = ("intent", "next_action", "risk_level", "approval_required",
               "refund_amount", "policy_citations")


def _trace(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": case["id"],
        "input": case["input"],
        "final_response": result.get("final_response", ""),
        "tool_calls": result.get("tool_calls", []),
        "route": result.get("route", []),
        "state": {k: result.get(k) for k in _STATE_KEYS},
    }


def main() -> int:
    load_dotenv()
    backend = os.environ.get("POLICYDESK_LLM", "stub")
    if backend == "claude" and not os.environ.get("ANTHROPIC_API_KEY"):
        print("!! POLICYDESK_LLM=claude but ANTHROPIC_API_KEY is not set.")
        return 2

    cases = yaml.safe_load(CASES_FILE.read_text())
    graph = build_graph()
    TRACES_DIR.mkdir(exist_ok=True)

    rows: list[tuple[str, bool, list]] = []
    n_pass = tool_ok = approval_total = approval_ok = 0
    policy_total = policy_ok = unsafe = 0

    for case in cases:
        expected = case.get("expected", {})
        result = graph.invoke(initial_state(case["input"]))
        trace = _trace(case, result)
        (TRACES_DIR / f"{case['id']}.json").write_text(json.dumps(trace, indent=2))

        checks = evaluate(trace, expected)
        by_name = {c.name: c for c in checks}
        case_pass = all(c.passed for c in checks)
        n_pass += case_pass
        rows.append((case["id"], case_pass, [c for c in checks if not c.passed]))

        tool_checks = [by_name[n] for n in ("required_tool_called", "forbidden_tool_not_called")
                       if n in by_name]
        if tool_checks and all(c.passed for c in tool_checks):
            tool_ok += 1
        if "approval_gate_triggered" in by_name:
            approval_total += 1
            approval_ok += by_name["approval_gate_triggered"].passed
        if "policy_citation_present" in by_name:
            policy_total += 1
            policy_ok += by_name["policy_citation_present"].passed
        if "forbidden_tool_not_called" in by_name and not by_name["forbidden_tool_not_called"].passed:
            unsafe += 1

    total = len(cases)
    print(f"\nPolicyDesk eval results  (backend: {backend})\n" + "=" * 48)
    for cid, ok, failures in rows:
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {cid}")
        for f in failures:
            print(f"         - {f.name}: {f.detail}")

    def pct(num: int, den: int) -> str:
        return f"{(100 * num / den):.0f}%" if den else "n/a"

    print("\n" + "-" * 48)
    print(f"  Cases passed            : {n_pass} / {total}")
    print(f"  Tool-call accuracy      : {pct(tool_ok, total)}")
    print(f"  Approval-gate accuracy  : {pct(approval_ok, approval_total)}")
    print(f"  Policy-grounding accuracy: {pct(policy_ok, policy_total)}")
    print(f"  Unsafe-action rate      : {pct(unsafe, total)}")
    print(f"\n  Traces written to {TRACES_DIR}")

    return 0 if n_pass == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
