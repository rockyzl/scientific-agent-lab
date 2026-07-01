"""Confidence / uncertainty computation.

Confidence is *calibrated to coverage*: missing required evidence drags it down, and a
required measurement that is only satisfied by a prediction gets partial credit. This is
what keeps the agent honest instead of confidently wrong.
"""

from __future__ import annotations

from ..schemas import ObservedFeature, RequiredEvidence


def overall_confidence(
    observations: list[ObservedFeature], required: list[RequiredEvidence]
) -> float:
    if not required:
        if not observations:
            return 0.0
        return round(sum(o.confidence for o in observations) / len(observations), 2)

    obs_by_name = {o.name: o for o in observations}
    conf_sum = 0.0
    for r in required:
        o = obs_by_name.get(r.name)
        if o is None:
            continue  # missing required contributes 0
        weight = 1.0 if o.kind == r.kind else 0.5  # kind mismatch -> partial credit
        conf_sum += weight * o.confidence
    return round(conf_sum / len(required), 2)  # coverage-weighted mean
