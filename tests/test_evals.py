"""Evaluator unit tests + a full-suite smoke test (all offline, stub backend)."""

import json
from pathlib import Path

import pytest
import yaml

from app.graph import build_graph
from app.reasoner import StubReasoner
from app.state import initial_state
from evals.evaluators import (
    evaluate,
    forbidden_tool_not_called,
    required_tool_called,
)

ROOT = Path(__file__).resolve().parent.parent
CASES = yaml.safe_load((ROOT / "evals" / "cases.yaml").read_text())
GOLDEN = ROOT / "evals" / "golden_traces"


def _golden(name):
    return json.loads((GOLDEN / name).read_text())


def test_required_tool_called_detects_missing():
    trace = {"tool_calls": ["lookup_order"]}
    assert required_tool_called(trace, ["lookup_order"]).passed
    assert not required_tool_called(trace, ["issue_refund"]).passed


def test_forbidden_tool_not_called_detects_violation():
    trace = {"tool_calls": ["issue_refund"]}
    assert forbidden_tool_not_called(trace, ["request_human_approval"]).passed
    assert not forbidden_tool_not_called(trace, ["issue_refund"]).passed


def test_golden_double_charge_blocks_refund():
    trace = _golden("double_charge_escalation.json")
    assert trace["state"]["approval_required"] is True
    assert "request_human_approval" in trace["tool_calls"]
    assert "issue_refund" not in trace["tool_calls"]


def test_full_suite_passes_under_stub():
    graph = build_graph(reasoner=StubReasoner())
    failures = []
    for case in CASES:
        result = graph.invoke(initial_state(case["input"]))
        trace = {
            "id": case["id"],
            "final_response": result.get("final_response", ""),
            "tool_calls": result.get("tool_calls", []),
            "route": result.get("route", []),
            "state": {k: result.get(k) for k in
                      ("intent", "next_action", "risk_level", "approval_required",
                       "refund_amount", "policy_citations")},
        }
        for check in evaluate(trace, case.get("expected", {})):
            if not check.passed:
                failures.append(f"{case['id']}: {check.name} ({check.detail})")
    assert not failures, "eval failures:\n" + "\n".join(failures)


@pytest.mark.claude
def test_full_graph_with_claude_backend():
    """Opt-in: runs the graph through Claude. Skips unless explicitly enabled."""
    import os

    if os.environ.get("POLICYDESK_LLM") != "claude" or not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("set POLICYDESK_LLM=claude and ANTHROPIC_API_KEY to run")
    from app.reasoner import ClaudeReasoner

    graph = build_graph(reasoner=ClaudeReasoner())
    result = graph.invoke(initial_state("My order B2048 arrived damaged. Can I get a refund?"))
    # Tool/routing behavior is deterministic even with Claude.
    assert "lookup_order" in result["tool_calls"]
    assert result["final_response"]
