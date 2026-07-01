"""Aggregate contract checks into a single EvaluationResult."""

from __future__ import annotations

from ..schemas import EvaluationResult


def score(checks: list[dict], version: str = "1") -> EvaluationResult:
    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    return EvaluationResult(
        contracts=checks,
        score=round(passed / total, 3) if total else 0.0,
        passed=passed,
        total=total,
        contract_set_version=version,
    )
