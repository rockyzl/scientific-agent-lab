"""scientific-agent-lab — an open-source framework for evidence-grounded scientific
agents, with replayable evaluation and human review as the core spine."""

from .evaluation.contracts import evaluate
from .report import to_json, to_markdown
from .schemas import (
    Assumption,
    EvidenceItem,
    EvidenceKind,
    HumanReviewItem,
    MissingEvidence,
    NextAction,
    ObservedFeature,
    RecommendedMeasurement,
    RequiredEvidence,
    ScientificAgentReport,
    ScientificHypothesis,
    ScientificInput,
    UncertaintyNote,
)
from .workflow import run_workflow

__version__ = "0.1.0"

__all__ = [
    "ScientificInput",
    "ObservedFeature",
    "RequiredEvidence",
    "EvidenceItem",
    "EvidenceKind",
    "Assumption",
    "ScientificHypothesis",
    "UncertaintyNote",
    "MissingEvidence",
    "RecommendedMeasurement",
    "NextAction",
    "HumanReviewItem",
    "ScientificAgentReport",
    "run_workflow",
    "evaluate",
    "to_markdown",
    "to_json",
]
