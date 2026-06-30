# Design notes

Short rationale for the decisions in this repo — the things worth being able to
explain rather than just point at.

## Why a deterministic stub is the default backend

The agent's reasoning sits behind a small interface (`app/reasoner.py`) with two
implementations: a rule-based `StubReasoner` and an LLM-backed one. The stub is the
default, and that's deliberate.

The eval suite is the part of this project I actually care about, and an eval suite is
only useful if it's a reliable signal. If every run depended on a live model, the suite
would cost tokens, need an API key, and give slightly different answers each time —
which makes it useless as a regression gate. With the stub, `python -m evals.run_evals`
is fully reproducible and runs anywhere, so a failing case means something changed in
*my* code, not in the model's mood that day. The real-model backend is there to show the
same graph runs against an actual LLM, but it's opt-in.

## Why the evals assert on tools and routing, not wording

A support agent can produce a perfectly fluent reply while doing something wrong:
refunding money it should have escalated, skipping the payment-history check, or reading
back another customer's address. Grading the final text misses all of that.

So the cases assert on the recorded trajectory — which tools were called, which path the
graph took, what the risk/approval state ended up as — and treat the wording as the least
important thing. `forbidden_tool_not_called` is the one I'd point to first: it's the check
that proves the agent *didn't* take an unsafe action, which matters more than any phrasing.

## Why tools are chosen by the nodes, not the model

Each node decides which tools to call; the model only classifies intent, picks an action,
and writes prose. That's what lets the structural evals stay meaningful regardless of
backend — switching from the stub to a real model changes the wording, not which tools
fire or how the graph routes. It also keeps the tools auditable: they're plain functions
over local data, so there's a single obvious place to gate or log a sensitive action.

## Where the guardrail lives

`risk` is the only node that sets `approval_required` and records the approval request;
`writer` is the only node that can issue a refund, and it refuses to while approval is
pending. Keeping the decision (`risk`) and the action (`writer`) in separate nodes makes
the gate easy to reason about and easy to test — the high-value-refund case asserts the
approval tool fired and the refund tool did not.

## Known limitations

- The stub's replies are templated; they read a bit stiff because the stub is rules, not
  a language model. The real-model backend produces nicer prose.
- Under the real-model backend the wording (and occasionally the intent classification)
  varies between runs, so the text-matching checks should be read loosely there; the
  tool/routing/state checks remain the dependable signal.
- The data and tools are mocks. Wiring this to real systems would mean real auth, real
  audit logging, and rate limiting — none of which are in scope here. The approval gate
  and the trace artifacts are the seams where those would attach.
