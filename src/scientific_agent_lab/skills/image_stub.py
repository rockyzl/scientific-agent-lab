"""Image feature skill — PLACEHOLDER.

A real vision / foundation model plugs in here (that is the Phase-1..4 work). For the
first version we return a deterministic mock so the whole pipeline runs end-to-end with
no model, no GPU, and no API key. The mock is clearly labelled as such.
"""

from __future__ import annotations

from ..schemas import EvidenceKind, ObservedFeature


def features_from_image(image_ref: str) -> list[ObservedFeature]:
    return [
        ObservedFeature(
            name="mock_texture_descriptor",
            value="lamellar",
            kind=EvidenceKind.MEASUREMENT,
            confidence=0.4,
            source=f"image_stub:{image_ref}",
            caveats="MOCK feature — replace with a real vision model (see roadmap).",
        )
    ]
