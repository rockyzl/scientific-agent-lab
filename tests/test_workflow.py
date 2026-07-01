import json
from pathlib import Path

from scientific_agent_lab.schemas import NextAction, ScientificInput
from scientific_agent_lab.workflow import run_workflow

SAMPLE = Path(__file__).resolve().parents[1] / "examples/materials_demo/sample_input.json"


def _report():
    inp = ScientificInput.from_dict(json.loads(SAMPLE.read_text()))
    return run_workflow(inp)


def test_workflow_runs_end_to_end():
    report, replay = _report()
    assert len(report.observed_features) == 2
    assert 0.0 <= report.confidence_level <= 1.0
    assert len(replay.steps) == 5


def test_workflow_detects_missing_evidence():
    report, _ = _report()
    missing = {m.name for m in report.missing_evidence}
    assert "cycling_stability" in missing
    assert "reference_match" in missing


def test_workflow_recommends_measurement_when_gap_exists():
    report, _ = _report()
    # a required measurement is missing -> agent must not ACCEPT
    assert report.recommended_next_measurement.action == NextAction.MEASURE_AGAIN
