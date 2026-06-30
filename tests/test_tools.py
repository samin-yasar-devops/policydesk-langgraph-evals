"""Deterministic tool behavior — no LLM, no network."""

from app.tools import (
    check_payment_history,
    create_ticket,
    issue_refund,
    lookup_order,
    request_human_approval,
    search_policies,
)


def test_lookup_order_found():
    order = lookup_order.invoke({"order_id": "B2048"})
    assert order["found"] is True
    assert order["amount"] == 35.0
    assert order["damaged"] is True


def test_lookup_order_not_found():
    order = lookup_order.invoke({"order_id": "ZZZZ9"})
    assert order["found"] is False


def test_check_payment_history_flags_duplicate():
    ph = check_payment_history.invoke({"order_id": "A1029"})
    assert ph["duplicate_charge"] is True
    assert ph["duplicate_amount"] == 120.0


def test_check_payment_history_single_charge():
    ph = check_payment_history.invoke({"order_id": "B2048"})
    assert ph["duplicate_charge"] is False


def test_search_policies_routes_to_doc():
    assert search_policies.invoke({"query": "late delivery"})[0]["doc"] == "shipping.md"
    assert search_policies.invoke({"query": "privacy address"})[0]["doc"] == "identity_verification.md"
    refund_cite = search_policies.invoke({"query": "refund damage"})[0]
    assert refund_cite["doc"] == "refunds.md"
    assert refund_cite["snippet"]  # non-empty grounding text


def test_action_tools_are_mocks():
    assert issue_refund.invoke({"order_id": "B2048", "amount": 35.0})["action"] == "refund_issued"
    assert request_human_approval.invoke(
        {"action": "refund", "reason": "high value"})["status"] == "pending_approval"
    assert create_ticket.invoke({"order_id": "G7054", "reason": "x"})["action"] == "ticket_created"
