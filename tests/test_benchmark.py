from pathlib import Path

from scientific_agent_lab.evaluation.benchmark import is_fully_passing, run_benchmark

CASES = Path(__file__).resolve().parents[1] / "benchmark/cases"


def test_benchmark_all_cases_fully_pass():
    results = run_benchmark(CASES)
    assert len(results) >= 3
    for r in results:
        assert is_fully_passing(r), f"case {r['id']} failed: {r}"


def test_benchmark_covers_accept_and_measure_paths():
    actions = {r["next_action"] for r in run_benchmark(CASES)}
    assert "accept" in actions       # a complete, high-confidence case
    assert "measure_again" in actions  # an incomplete case that must not accept
