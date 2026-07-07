"""Step 2 — build evidence, surface assumptions, and detect missing/weak evidence.

This is the heart of the "evidence governance" spine: every observed feature becomes an
Evidence item with provenance; required-but-absent evidence becomes an explicit gap; and
a required *measurement* satisfied only by a *prediction* is flagged as a weakness (not
silently accepted).
"""

from __future__ import annotations

from ..schemas import (
    Assumption,
    EvidenceItem,
    MissingEvidence,
    ObservedFeature,
    RequiredEvidence,
    ScientificInput,
)
from ..skills.literature import search as literature_search


def gather(
    inp: ScientificInput, features: list[ObservedFeature]
) -> tuple[
    list[EvidenceItem],
    list[Assumption],
    list[MissingEvidence],
    list[tuple[RequiredEvidence, ObservedFeature]],
]:
    evidence: list[EvidenceItem] = [
        EvidenceItem(
            claim=f"{f.name} = {f.value}",
            kind=f.kind,
            value=f.value,
            confidence=f.confidence,
            source=f.source or f.name,
            caveats=f.caveats,
        )
        for f in features
    ]

    assumptions: list[Assumption] = [
        Assumption(
            statement="Observed features are representative of the sample/region under study.",
            basis="standard sampling assumption",
            confidence=0.5,
        )
    ]

    obs_by_name = {f.name: f for f in features}
    missing: list[MissingEvidence] = []
    weaknesses: list[tuple[RequiredEvidence, ObservedFeature]] = []
    for r in inp.required:
        o = obs_by_name.get(r.name)
        if o is None:
            missing.append(
                MissingEvidence(
                    name=r.name,
                    expected_kind=r.kind,
                    why_needed=r.why or "required to support the conclusion",
                )
            )
        elif o.kind != r.kind:
            weaknesses.append((r, o))
            assumptions.append(
                Assumption(
                    statement=(
                        f"'{r.name}' is treated as adequate although it is a "
                        f"{o.kind.value}, not a direct {r.kind.value}."
                    ),
                    basis="evidence-kind mismatch",
                    confidence=0.3,
                )
            )

    # literature hook — real offline TF-IDF retrieval over a curated domain
    # knowledge base (deterministic; see skills/literature.py).
    evidence.extend(literature_search(inp.question, inp.domain, k=2))
    return evidence, assumptions, missing, weaknesses
