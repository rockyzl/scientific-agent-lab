"""Step 5 — produce a human-review checklist and explicit uncertainty notes.

Human review is a first-class step, not an afterthought: the agent hands the scientist a
short list of the exact things a human should check before trusting or acting.
"""

from __future__ import annotations

from ..schemas import (
    EvidenceItem,
    EvidenceKind,
    HumanReviewItem,
    MissingEvidence,
    ObservedFeature,
    RequiredEvidence,
    UncertaintyNote,
)


def review(
    features: list[ObservedFeature],
    evidence: list[EvidenceItem],
    missing: list[MissingEvidence],
    weaknesses: list[tuple[RequiredEvidence, ObservedFeature]],
    confidence: float,
) -> tuple[list[HumanReviewItem], list[UncertaintyNote]]:
    checklist: list[HumanReviewItem] = [
        HumanReviewItem(
            question="Do the observed features actually support the stated interpretation?",
            why="guard against over-reading noisy or limited data",
        )
    ]
    for m in missing:
        checklist.append(
            HumanReviewItem(
                question=f"Would acquiring '{m.name}' change the conclusion?",
                why=m.why_needed,
            )
        )
    checklist.append(
        HumanReviewItem(
            question="Is the recommended next action appropriate and safe to run?",
            why="human-in-the-loop gate before any experiment or write action",
        )
    )

    uncertainty: list[UncertaintyNote] = []
    for e in evidence:
        if e.kind != EvidenceKind.MISSING and e.confidence < 0.5:
            uncertainty.append(
                UncertaintyNote(
                    note=f"Low-confidence evidence: {e.claim} (confidence {e.confidence}).",
                    severity="high" if e.confidence < 0.3 else "medium",
                )
            )
    for r, o in weaknesses:
        uncertainty.append(
            UncertaintyNote(
                note=f"'{r.name}' is a {o.kind.value}, not a direct {r.kind.value}.",
                severity="medium",
            )
        )
    if not uncertainty:
        uncertainty.append(
            UncertaintyNote(note="Residual uncertainty from limited sampling.", severity="low")
        )
    return checklist, uncertainty
