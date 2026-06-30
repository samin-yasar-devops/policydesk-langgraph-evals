"""Policy search over local, sanitized policy documents."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from langchain_core.tools import tool

from app.paths import POLICIES_DIR

TOOL_SEARCH_POLICIES = "search_policies"

# Which doc answers which kind of question.
_KEYWORD_TO_DOC = [
    (("ship", "deliver", "late", "transit", "sla"), "shipping.md"),
    (("identity", "verify", "verification", "privacy", "address", "account"), "identity_verification.md"),
    (("refund", "damage", "duplicate", "charge", "return", "replacement", "window"), "refunds.md"),
]


@lru_cache(maxsize=8)
def _read(doc: str) -> str:
    return (POLICIES_DIR / doc).read_text()


def _pick_doc(query: str) -> str:
    q = query.lower()
    for keywords, doc in _KEYWORD_TO_DOC:
        if any(k in q for k in keywords):
            return doc
    return "refunds.md"


def _first_section(text: str) -> tuple[str, str]:
    """Return (section title, snippet) for the first '## ' section of a doc."""
    title = "Policy"
    body: list[str] = []
    in_section = False
    for line in text.splitlines():
        if line.startswith("## "):
            if in_section:  # reached the next section — stop
                break
            title = line[3:].strip()
            in_section = True
        elif in_section and line.strip():
            body.append(line.strip())
    snippet = " ".join(body)[:300]
    return title, snippet


@tool
def search_policies(query: str) -> list[dict[str, Any]]:
    """Search local policy docs and return grounded citations for a query."""
    doc = _pick_doc(query)
    title, snippet = _first_section(_read(doc))
    citation_id = f"{doc}#{title.lower().replace(' ', '-')}"
    return [{"doc": doc, "section": title, "snippet": snippet, "citation_id": citation_id}]
