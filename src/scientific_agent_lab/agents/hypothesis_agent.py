"""Step 3 — propose *tentative* interpretations, never overclaimed conclusions."""

from __future__ import annotations

from ..schemas import EvidenceItem, EvidenceKind, ScientificHypothesis, ScientificInput


def hypothesize(
    inp: ScientificInput, evidence: list[EvidenceItem]
) -> list[ScientificHypothesis]:
    supporting = [e for e in evidence if e.kind != EvidenceKind.MISSING]
    claims = [e.claim for e in supporting]
    conf = 0.0
    if supporting:
        conf = round(min(0.6, sum(e.confidence for e in supporting) / len(supporting)), 2)
    statement = (
        f"Possible interpretation for '{inp.question}': the available evidence is "
        "consistent with a candidate explanation, but this requires validation before "
        "any conclusion is drawn."
    )
    return [ScientificHypothesis(statement=statement, supported_by=claims, confidence=conf)]
