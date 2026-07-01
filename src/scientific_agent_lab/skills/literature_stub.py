"""Literature retrieval skill — PLACEHOLDER.

Phase 1 replaces this with real arXiv / Crossref / Semantic Scholar search. For now it
returns a single honestly-labelled mock item so the evidence pipeline has a literature
hook without blocking on live APIs.
"""

from __future__ import annotations

from ..schemas import EvidenceItem, EvidenceKind


def search(query: str, k: int = 1) -> list[EvidenceItem]:
    return [
        EvidenceItem(
            claim=f"Related prior work may exist for: {query}",
            kind=EvidenceKind.LITERATURE,
            value=None,
            confidence=0.2,
            source="literature_stub",
            caveats="MOCK retrieval — not a real search (see roadmap).",
        )
    ][:k]
