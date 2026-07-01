import json

from scientific_agent_lab.schemas import (
    EvidenceKind,
    ObservedFeature,
    ScientificInput,
)


def test_scientific_input_from_dict():
    inp = ScientificInput.from_dict(
        {
            "question": "q?",
            "domain": "electrochemistry",
            "observations": [
                {"name": "x", "value": 1.0, "kind": "measurement", "confidence": 0.9}
            ],
            "required": [{"name": "x", "kind": "measurement", "why": "needed"}],
        }
    )
    assert inp.question == "q?"
    assert inp.domain == "electrochemistry"
    assert len(inp.observations) == 1
    assert inp.observations[0].kind == EvidenceKind.MEASUREMENT
    assert inp.required[0].name == "x"


def test_observed_feature_json_roundtrip():
    from dataclasses import asdict

    f = ObservedFeature(name="x", value=1, kind=EvidenceKind.PREDICTION, confidence=0.5)
    s = json.dumps(asdict(f), default=str)
    d = json.loads(s)
    assert d["name"] == "x"
    assert d["kind"] == "prediction"  # str-Enum serializes to its value
