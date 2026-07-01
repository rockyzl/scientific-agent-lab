"""Data contracts for evidence-grounded scientific agents.

The whole project rests on one idea: an agent may *organize* a scientific workflow,
but every conclusion must be grounded in **evidence**, keep its **assumptions** and
**uncertainty** explicit, name what evidence is **missing**, and stay **human-reviewable**.

These dataclasses (stdlib only — zero third-party deps, so it runs on clone) are the
contract every agent output must satisfy, and what the evaluation harness checks.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class EvidenceKind(str, Enum):
    """Provenance of a piece of evidence — the thing that makes it trustworthy."""

    MEASUREMENT = "measurement"  # from an instrument / real observation
    PREDICTION = "prediction"    # from a model
    INFERENCE = "inference"      # reasoned from other evidence
    LITERATURE = "literature"    # from a paper / database
    PRIOR = "prior"              # assumed / prior knowledge
    MISSING = "missing"          # a known gap: evidence we do NOT have


class NextAction(str, Enum):
    """What the agent recommends doing next when it is not yet confident."""

    MEASURE_AGAIN = "measure_again"
    LITERATURE_SEARCH = "literature_search"
    SIMULATION = "simulation"
    HUMAN_REVIEW = "human_review"
    ACCEPT = "accept"  # confident enough; no further action


@dataclass
class ObservedFeature:
    name: str
    value: Any = None
    kind: EvidenceKind = EvidenceKind.MEASUREMENT
    confidence: float = 0.5
    source: str = ""
    caveats: str = ""


@dataclass
class RequiredEvidence:
    """What the question *needs* in order to be answerable — used to detect gaps."""

    name: str
    kind: EvidenceKind = EvidenceKind.MEASUREMENT
    why: str = ""


@dataclass
class EvidenceItem:
    claim: str
    kind: EvidenceKind
    value: Any = None
    confidence: float = 0.0
    source: str = ""
    caveats: str = ""


@dataclass
class Assumption:
    statement: str
    basis: str = ""
    confidence: float = 0.0


@dataclass
class ScientificHypothesis:
    statement: str
    supported_by: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class UncertaintyNote:
    note: str
    severity: str = "medium"  # low | medium | high


@dataclass
class MissingEvidence:
    name: str
    expected_kind: EvidenceKind = EvidenceKind.MEASUREMENT
    why_needed: str = ""


@dataclass
class RecommendedMeasurement:
    action: NextAction = NextAction.HUMAN_REVIEW
    target: str = ""
    rationale: str = ""


@dataclass
class HumanReviewItem:
    question: str
    why: str = ""


@dataclass
class ScientificInput:
    question: str
    domain: str = "general"
    image_ref: str | None = None
    observations: list[ObservedFeature] = field(default_factory=list)
    required: list[RequiredEvidence] = field(default_factory=list)
    context: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "ScientificInput":
        obs = [
            ObservedFeature(
                name=o["name"],
                value=o.get("value"),
                kind=EvidenceKind(o.get("kind", "measurement")),
                confidence=float(o.get("confidence", 0.5)),
                source=o.get("source", ""),
                caveats=o.get("caveats", ""),
            )
            for o in d.get("observations", [])
        ]
        req = [
            RequiredEvidence(
                name=r["name"],
                kind=EvidenceKind(r.get("kind", "measurement")),
                why=r.get("why", ""),
            )
            for r in d.get("required", [])
        ]
        return cls(
            question=d["question"],
            domain=d.get("domain", "general"),
            image_ref=d.get("image_ref"),
            observations=obs,
            required=req,
            context=d.get("context", ""),
        )


@dataclass
class ScientificAgentReport:
    question: str
    domain: str
    observed_features: list[ObservedFeature]
    possible_interpretations: list[ScientificHypothesis]
    evidence: list[EvidenceItem]
    assumptions: list[Assumption]
    uncertainty: list[UncertaintyNote]
    missing_evidence: list[MissingEvidence]
    recommended_next_measurement: RecommendedMeasurement
    human_review_checklist: list[HumanReviewItem]
    confidence_level: float
    limitations: str

    def supporting_evidence(self) -> list[EvidenceItem]:
        return [e for e in self.evidence if e.kind != EvidenceKind.MISSING]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvaluationResult:
    contracts: list[dict] = field(default_factory=list)
    score: float = 0.0
    passed: int = 0
    total: int = 0
    contract_set_version: str = "1"  # versioned so results stay comparable over time

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReproducibilityRecord:
    """Everything needed to re-run and audit a result — the difference between a demo
    and science. If someone cannot reproduce it, it is not a scientific result."""

    input_sha256: str = ""
    report_sha256: str = ""  # content hash of the report — stable across re-runs
    package_version: str = ""
    python_version: str = ""
    skills_used: list[str] = field(default_factory=list)
    evidence_sources: list[str] = field(default_factory=list)
    n_steps: int = 0
    seed: int | None = None
    created_utc: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReplayRecord:
    input: dict
    steps: list[dict]
    report: dict
    created_utc: str = ""
    reproducibility: ReproducibilityRecord = field(default_factory=ReproducibilityRecord)

    def to_dict(self) -> dict:
        return asdict(self)
