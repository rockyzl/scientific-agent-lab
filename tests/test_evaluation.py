import json
from pathlib import Path

from scientific_agent_lab.evaluation.contracts import evaluate
from scientific_agent_lab.schemas import (
    NextAction,
    RecommendedMeasurement,
    ReplayRecord,
    ScientificAgentReport,
    ScientificHypothesis,
    MissingEvidence,
    ScientificInput,
)
from scientific_agent_lab.workflow import run_workflow

SAMPLE = Path(__file__).resolve().parents[1] / "examples/materials_demo/sample_input.json"


def test_good_report_passes_all_contracts():
    inp = ScientificInput.from_dict(json.loads(SAMPLE.read_text()))
    report, replay = run_workflow(inp)
    result = evaluate(report, replay)
    assert result.passed == result.total == 9
    assert result.score == 1.0
    names_passed = {c["name"] for c in result.contracts if c["passed"]}
    assert "result_is_reproducible" in names_passed
    assert replay.reproducibility.input_sha256  # provenance present


def test_overclaimed_report_fails_a_contract():
    # An adversarial report: claims ACCEPT despite a missing measurement, and states an
    # un-hedged conclusion. The overclaim contract must catch it.
    bad = ScientificAgentReport(
        question="q?",
        domain="test",
        observed_features=[],
        possible_interpretations=[ScientificHypothesis(statement="It is definitely phase X.", confidence=0.99)],
        evidence=[],
        assumptions=[],
        uncertainty=[],
        missing_evidence=[MissingEvidence(name="cycling_stability")],
        recommended_next_measurement=RecommendedMeasurement(action=NextAction.ACCEPT),
        human_review_checklist=[],
        confidence_level=0.99,
        limitations="",
    )
    replay = ReplayRecord(input={}, steps=[{"step": 1}], report=bad.to_dict())
    result = evaluate(bad, replay)
    names_failed = {c["name"] for c in result.contracts if not c["passed"]}
    assert "recommendations_are_not_overclaimed" in names_failed
    assert result.score < 1.0
