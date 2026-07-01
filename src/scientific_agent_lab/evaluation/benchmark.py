"""Replayable scientific-agent evaluation benchmark.

Runs the agent over a folder of scientific cases and reports, per case:
  - the acceptance-contract score (did it reason responsibly?), and
  - whether case-specific expectations hold (missing count, next action, confidence band).

This is the piece almost no one is building: a benchmark for *how* a scientific agent
reasons, not just whether one answer is right.
"""

from __future__ import annotations

import argparse
import json
import pathlib

from ..schemas import ScientificInput
from ..workflow import run_workflow
from .contracts import evaluate


def run_case(path: pathlib.Path) -> dict:
    d = json.loads(path.read_text())
    expect = d.get("expect", {})  # from_dict ignores unknown keys ("id", "expect")
    case_id = d.get("id", path.stem)

    report, replay = run_workflow(ScientificInput.from_dict(d))
    result = evaluate(report, replay)

    missing = len(report.missing_evidence)
    action = report.recommended_next_measurement.action.value
    conf = report.confidence_level

    checks: list[tuple[str, bool]] = []
    if "min_missing" in expect:
        checks.append(("min_missing", missing >= expect["min_missing"]))
    if "max_missing" in expect:
        checks.append(("max_missing", missing <= expect["max_missing"]))
    if "next_action_in" in expect:
        checks.append(("next_action_in", action in expect["next_action_in"]))
    if "max_confidence" in expect:
        checks.append(("max_confidence", conf <= expect["max_confidence"]))
    if "min_confidence" in expect:
        checks.append(("min_confidence", conf >= expect["min_confidence"]))

    return {
        "id": case_id,
        "contract_score": result.score,
        "contracts_passed": result.passed,
        "contracts_total": result.total,
        "missing": missing,
        "next_action": action,
        "confidence": conf,
        "expect_checks": checks,
        "expect_pass": all(v for _, v in checks),
    }


def run_benchmark(cases_dir: str | pathlib.Path) -> list[dict]:
    cases = sorted(pathlib.Path(cases_dir).glob("*.json"))
    return [run_case(c) for c in cases]


def is_fully_passing(r: dict) -> bool:
    return r["expect_pass"] and r["contract_score"] == 1.0


def format_report(results: list[dict]) -> str:
    header = f"{'case':<30}{'contracts':>10}{'missing':>9}{'conf':>7}{'next_action':>16}{'expect':>8}"
    lines = [header, "-" * len(header)]
    for r in results:
        contracts = f"{r['contracts_passed']}/{r['contracts_total']}"
        lines.append(
            f"{r['id']:<30}{contracts:>10}{r['missing']:>9}{r['confidence']:>7}"
            f"{r['next_action']:>16}{'PASS' if r['expect_pass'] else 'FAIL':>8}"
        )
    ok = sum(1 for r in results if is_fully_passing(r))
    lines.append("-" * len(header))
    lines.append(f"{ok}/{len(results)} cases fully pass (contracts 1.0 AND expectations met)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scientific-agent-lab-benchmark",
        description="Run the scientific-agent evaluation benchmark.",
    )
    parser.add_argument("--cases", default="benchmark/cases", help="folder of case JSON files")
    args = parser.parse_args(argv)
    results = run_benchmark(args.cases)
    print(format_report(results))
    return 0 if all(is_fully_passing(r) for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
