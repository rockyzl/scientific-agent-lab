"""Step 4 — recommend a justified next action (the closed-loop 'decide what to do next')."""

from __future__ import annotations

from ..schemas import MissingEvidence, NextAction, RecommendedMeasurement


def plan(missing: list[MissingEvidence], confidence: float) -> RecommendedMeasurement:
    if missing:
        kinds = {m.expected_kind for m in missing}
        from ..schemas import EvidenceKind

        if EvidenceKind.MEASUREMENT in kinds:
            target = next(m.name for m in missing if m.expected_kind == EvidenceKind.MEASUREMENT)
            return RecommendedMeasurement(
                action=NextAction.MEASURE_AGAIN,
                target=target,
                rationale=f"A required measurement ('{target}') is missing; acquire it before concluding.",
            )
        if EvidenceKind.LITERATURE in kinds:
            target = next(m.name for m in missing if m.expected_kind == EvidenceKind.LITERATURE)
            return RecommendedMeasurement(
                action=NextAction.LITERATURE_SEARCH,
                target=target,
                rationale=f"A required reference ('{target}') is missing; search the literature/databases.",
            )
        return RecommendedMeasurement(
            action=NextAction.HUMAN_REVIEW,
            rationale="Required evidence is missing and cannot be auto-acquired.",
        )
    if confidence < 0.4:
        return RecommendedMeasurement(
            action=NextAction.HUMAN_REVIEW,
            rationale="No missing evidence, but overall confidence is low.",
        )
    if confidence < 0.7:
        return RecommendedMeasurement(
            action=NextAction.SIMULATION,
            rationale="Moderate confidence; a simulation could disambiguate before committing.",
        )
    return RecommendedMeasurement(
        action=NextAction.ACCEPT,
        rationale="Evidence is sufficient and confident; no further action required.",
    )
