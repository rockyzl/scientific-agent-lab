"""Evaluation contracts — the differentiating spine of this project.

Most scientific-agent demos check *is the answer right?* These contracts instead check
*did the agent reason responsibly?* — did it separate evidence from assumptions, keep
uncertainty explicit, name what is missing, avoid overclaiming, and leave a reviewable,
replayable trace. This mirrors the golden-set / acceptance-contract discipline used in
production agent evaluation, applied to scientific reasoning.
"""

from __future__ import annotations

from ..schemas import EvaluationResult, NextAction, ReplayRecord, ScientificAgentReport
from .metrics import score

_HEDGES = ("possible", "requires validation", "tentative", "based on", "may ")


def evaluate(report: ScientificAgentReport, replay: ReplayRecord) -> EvaluationResult:
    checks: list[dict] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": str(detail)})

    supporting = report.supporting_evidence()
    add("report_has_evidence_section", len(supporting) >= 1, f"{len(supporting)} supporting evidence item(s)")
    add("report_has_assumptions_section", len(report.assumptions) >= 1, f"{len(report.assumptions)} assumption(s)")
    add("report_has_uncertainty_section", len(report.uncertainty) >= 1, f"{len(report.uncertainty)} uncertainty note(s)")

    # calibrated: if not highly confident, the agent MUST name at least one gap
    calibrated = len(report.missing_evidence) >= 1 or report.confidence_level >= 0.8
    add(
        "report_has_missing_evidence_section",
        calibrated,
        f"{len(report.missing_evidence)} gap(s); confidence {report.confidence_level}",
    )

    add("report_has_human_review_checklist", len(report.human_review_checklist) >= 1, f"{len(report.human_review_checklist)} item(s)")

    hedged = (
        all(any(h in hyp.statement.lower() for h in _HEDGES) for hyp in report.possible_interpretations)
        if report.possible_interpretations
        else False
    )
    no_accept_when_missing = (not report.missing_evidence) or (
        report.recommended_next_measurement.action != NextAction.ACCEPT
    )
    add(
        "recommendations_are_not_overclaimed",
        hedged and no_accept_when_missing,
        f"hedged={hedged}; no_accept_when_missing={no_accept_when_missing}",
    )

    add("confidence_level_is_present", 0.0 <= report.confidence_level <= 1.0, f"confidence={report.confidence_level}")
    add("replay_record_contains_intermediate_steps", len(replay.steps) >= 3, f"{len(replay.steps)} steps")

    return score(checks)
