"""The end-to-end scientific-reasoning workflow.

Runs the five agents in order and records every intermediate step as a replay artifact,
so the whole reasoning trace is auditable and re-playable.
"""

from __future__ import annotations

import hashlib
import json
import platform
from dataclasses import asdict

from .agents.evidence_agent import gather
from .agents.hypothesis_agent import hypothesize
from .agents.observation_agent import observe
from .agents.planner_agent import plan
from .agents.reviewer_agent import review
from .schemas import (
    EvidenceItem,
    ReplayRecord,
    ReproducibilityRecord,
    ScientificAgentReport,
    ScientificInput,
)
from .skills.uncertainty import overall_confidence
from .version import __version__


def _sha16(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def _reproducibility(
    inp: ScientificInput,
    steps: list[dict],
    evidence: list[EvidenceItem],
    report_dict: dict,
) -> ReproducibilityRecord:
    skills = [f"literature@{__version__}:offline-tfidf-kb"]
    if not inp.observations and inp.image_ref:
        skills.insert(0, f"vision@{__version__}:not-configured")
    return ReproducibilityRecord(
        input_sha256=_sha16(asdict(inp)),
        report_sha256=_sha16(report_dict),
        package_version=__version__,
        python_version=platform.python_version(),
        skills_used=skills,
        evidence_sources=sorted({e.source for e in evidence if e.source}),
        n_steps=len(steps),
        seed=None,  # deterministic in v0
        created_utc="",  # stamped by the CLI when written to disk
    )

_LIMITATIONS = (
    "This is a research prototype, not a validated scientific decision system. "
    "Interpretations are tentative and must be confirmed by a domain expert. "
    "Literature retrieval runs over a small curated offline knowledge base (not a "
    "live literature API). This offline build ships no vision model, so image-derived "
    "features are unavailable — reported as missing evidence, never invented."
)


def run_workflow(inp: ScientificInput) -> tuple[ScientificAgentReport, ReplayRecord]:
    steps: list[dict] = []

    features = observe(inp)
    steps.append(
        {"step": 1, "agent": "observation_agent", "output": [asdict(f) for f in features]}
    )

    evidence, assumptions, missing, weaknesses = gather(inp, features)
    steps.append(
        {
            "step": 2,
            "agent": "evidence_agent",
            "output": {
                "evidence": [asdict(e) for e in evidence],
                "assumptions": [asdict(a) for a in assumptions],
                "missing_evidence": [asdict(m) for m in missing],
            },
        }
    )

    hypotheses = hypothesize(inp, evidence)
    steps.append(
        {"step": 3, "agent": "hypothesis_agent", "output": [asdict(h) for h in hypotheses]}
    )

    confidence = overall_confidence(features, inp.required)
    recommendation = plan(missing, confidence)
    steps.append({"step": 4, "agent": "planner_agent", "output": asdict(recommendation)})

    checklist, uncertainty = review(features, evidence, missing, weaknesses, confidence)
    steps.append(
        {
            "step": 5,
            "agent": "reviewer_agent",
            "output": {
                "human_review_checklist": [asdict(c) for c in checklist],
                "uncertainty": [asdict(u) for u in uncertainty],
            },
        }
    )

    report = ScientificAgentReport(
        question=inp.question,
        domain=inp.domain,
        observed_features=features,
        possible_interpretations=hypotheses,
        evidence=evidence,
        assumptions=assumptions,
        uncertainty=uncertainty,
        missing_evidence=missing,
        recommended_next_measurement=recommendation,
        human_review_checklist=checklist,
        confidence_level=confidence,
        limitations=_LIMITATIONS,
    )
    report_dict = report.to_dict()
    replay = ReplayRecord(
        input=asdict(inp),
        steps=steps,
        report=report_dict,
        reproducibility=_reproducibility(inp, steps, evidence, report_dict),
    )
    return report, replay
