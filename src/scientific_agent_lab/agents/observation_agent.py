"""Step 1 — turn raw input into observed features."""

from __future__ import annotations

from ..schemas import ObservedFeature, ScientificInput
from ..skills.image_stub import features_from_image


def observe(inp: ScientificInput) -> list[ObservedFeature]:
    if inp.observations:
        return list(inp.observations)
    if inp.image_ref:
        return features_from_image(inp.image_ref)
    return []
