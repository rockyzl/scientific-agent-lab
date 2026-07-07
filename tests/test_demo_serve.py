"""Tests for the local live demo server (demo/serve.py) — the request path that
turns a scientific input into a report + evaluation + reproducibility record."""
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
_spec = importlib.util.spec_from_file_location("sal_demo_serve", ROOT / "demo" / "serve.py")
serve = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(serve)


def test_run_case_valid_preset_returns_full_result():
    out = serve.run_case(serve.CASES["rfb_catholyte"])
    assert set(out) >= {"input", "report", "eval", "replay"}
    assert out["eval"]["passed"] == out["eval"]["total"]  # fully passing (9/9)
    assert out["replay"]["reproducibility"]["n_steps"] == 5
    assert out["report"]["recommended_next_measurement"]["action"] in ("accept", "measure_again")


def test_run_case_rejects_input_without_question():
    for bad in ({}, {"domain": "materials"}, "not-a-dict", None):
        raised = False
        try:
            serve.run_case(bad)
        except ValueError:
            raised = True
        assert raised, f"run_case should reject malformed input: {bad!r}"


def test_missing_required_measurement_forces_measure_again():
    inp = {
        "question": "Is this a viable candidate?",
        "domain": "electrochemistry",
        "observations": [
            {"name": "redox_potential_V", "value": 0.85, "kind": "measurement", "confidence": 0.9, "source": "cv"}
        ],
        "required": [
            {"name": "redox_potential_V", "kind": "measurement", "why": "voltage window"},
            {"name": "cycling_stability", "kind": "measurement", "why": "decides real viability"},
        ],
    }
    out = serve.run_case(inp)
    assert out["report"]["recommended_next_measurement"]["action"] == "measure_again"
    assert any(m["name"] == "cycling_stability" for m in out["report"]["missing_evidence"])


def test_complete_evidence_can_accept():
    inp = {
        "question": "Is the required measurement satisfied?",
        "domain": "materials",
        "observations": [
            {"name": "phase_purity", "value": "single-phase", "kind": "measurement", "confidence": 0.95, "source": "xrd"}
        ],
        "required": [
            {"name": "phase_purity", "kind": "measurement", "why": "identifies the phase"}
        ],
    }
    out = serve.run_case(inp)
    assert out["report"]["recommended_next_measurement"]["action"] == "accept"
    assert not out["report"]["missing_evidence"]
    assert out["eval"]["passed"] == out["eval"]["total"]


def test_demo_presets_cover_both_decision_paths():
    actions = {serve.run_case(c)["report"]["recommended_next_measurement"]["action"] for c in serve.CASES.values()}
    assert "accept" in actions
    assert "measure_again" in actions
