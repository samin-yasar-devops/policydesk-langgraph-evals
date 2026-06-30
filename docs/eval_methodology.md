# Eval methodology

The eval harness is the point of this repo. It regression-tests agent **behavior**,
not just whether the final answer reads well.

## Why trajectory and state, not just text

A support agent can produce a perfectly fluent answer while doing the wrong thing —
issuing a refund it should have escalated, skipping the payment lookup, or leaking
another customer's data. Final-answer matching misses all of that. So each case asserts
on the recorded **trajectory** (`tool_calls`, `route`) and **state** (`risk_level`,
`approval_required`, `policy_citations`) in addition to the text.

## Evaluator types (`evals/evaluators.py`)

| Evaluator | What it checks |
| --- | --- |
| `final_answer_contains` | Required substrings appear in the reply |
| `required_tool_called` | The case's required tools were all invoked |
| `forbidden_tool_not_called` | No forbidden tool was invoked (the unsafe-action check) |
| `approval_gate_triggered` | `approval_required` matches and the gate fired without issuing the refund |
| `policy_citation_present` | The reply is grounded in a policy citation |
| `no_private_data_leaked` | No other customer's email/address appears in the reply |
| `route_matches_expected` | The graph took the expected path |

A case passes only when **every** opted-in check passes.

## Cases (`evals/cases.yaml`)

Ten scenarios cover the happy path and the failure modes that matter: damaged-item
refund, double-charge (payment lookup + approval), high-value refund (approval gate),
missing order id (clarify), privacy refusal, late delivery (SLA), out-of-window return
(offer alternative), angry escalation (no invented compensation), ambiguous identity
(request verification), and prompt injection (ignore the unsafe instruction).

## Metrics

`run_evals` prints aggregate metrics: cases passed, tool-call accuracy, approval-gate
accuracy, policy-grounding accuracy, and **unsafe-action rate** (fraction of cases where
a forbidden tool was actually called — target 0%).

## Determinism and the two backends

Under the default **stub** backend the entire pipeline is deterministic: 10/10 every
run, with no API key and no tokens. This is what makes the suite a real regression gate.

Under `POLICYDESK_LLM=claude`, tool selection and routing stay deterministic (they live
in the nodes, not the model), so the structural evaluators remain the stable signal.
Only `final_answer_contains` should be read loosely there, since the wording comes from
the model.

## Trace artifacts

Every run writes `evals/traces/<case>.json` so a human can inspect the full trajectory.
`evals/golden_traces/` holds two committed reference traces for quick diffing.
