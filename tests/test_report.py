import json
from pathlib import Path

from scientific_agent_lab.report import to_json, to_markdown
from scientific_agent_lab.schemas import ScientificInput
from scientific_agent_lab.workflow import run_workflow

SAMPLE = Path(__file__).resolve().parents[1] / "examples/materials_demo/sample_input.json"


def test_markdown_has_required_sections():
    inp = ScientificInput.from_dict(json.loads(SAMPLE.read_text()))
    report, _ = run_workflow(inp)
    md = to_markdown(report)
    for header in (
        "## Observed features",
        "## Possible interpretations",
        "## Evidence",
        "## Assumptions",
        "## Uncertainty",
        "## Missing evidence",
        "## Human review checklist",
        "## Limitations",
    ):
        assert header in md


def test_json_report_parses():
    inp = ScientificInput.from_dict(json.loads(SAMPLE.read_text()))
    report, _ = run_workflow(inp)
    data = json.loads(to_json(report))
    assert data["domain"] == "electrochemistry"
    assert "recommended_next_measurement" in data
