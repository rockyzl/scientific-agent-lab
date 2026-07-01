import json
from pathlib import Path

from scientific_agent_lab.evaluation.contracts import evaluate
from scientific_agent_lab.schemas import ScientificInput
from scientific_agent_lab.workflow import run_workflow

SAMPLE = Path(__file__).resolve().parents[1] / "examples/materials_demo/sample_input.json"


def _run():
    inp = ScientificInput.from_dict(json.loads(SAMPLE.read_text()))
    return run_workflow(inp)


def test_same_input_gives_identical_report_hash():
    _, r1 = _run()
    _, r2 = _run()
    assert r1.reproducibility.report_sha256
    assert r1.reproducibility.report_sha256 == r2.reproducibility.report_sha256


def test_reproducibility_record_is_populated():
    _, replay = _run()
    repro = replay.reproducibility
    assert repro.input_sha256
    assert repro.report_sha256
    assert repro.python_version
    assert repro.package_version
    assert repro.n_steps == 5


def test_evaluation_result_is_versioned():
    report, replay = _run()
    result = evaluate(report, replay)
    assert result.contract_set_version  # non-empty version stamp
