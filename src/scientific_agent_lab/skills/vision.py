"""Vision skill — the pluggable hook for image-derived observed features.

By design this offline, zero-dependency build ships NO vision model, so it does
NOT invent image features: a tool whose whole point is evidence honesty must not
fabricate its own observations. When an image is provided but no vision model is
configured, image-derived features are simply unavailable — if the question
depends on them, they surface downstream as *missing evidence*, never as made-up
data. A real vision / foundation model plugs in here by returning ``ObservedFeature``
items with genuine provenance (that is the Phase 1-4 work in the roadmap).
"""
from __future__ import annotations

from ..schemas import ObservedFeature


def features_from_image(image_ref: str) -> list[ObservedFeature]:
    # No vision model configured in this offline build → no fabricated features.
    return []
