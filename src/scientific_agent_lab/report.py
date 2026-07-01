"""Render a ScientificAgentReport to Markdown and JSON."""

from __future__ import annotations

import json

from .schemas import ScientificAgentReport


def to_json(obj) -> str:
    data = obj.to_dict() if hasattr(obj, "to_dict") else obj
    return json.dumps(data, indent=2, default=str)


def to_markdown(r: ScientificAgentReport) -> str:
    L: list[str] = []
    L.append(f"# Scientific Agent Report")
    L.append("")
    L.append(f"**Question:** {r.question}")
    L.append(f"**Domain:** {r.domain}")
    L.append(f"**Confidence level:** {r.confidence_level}")
    rec = r.recommended_next_measurement
    target = f" ({rec.target})" if rec.target else ""
    L.append(f"**Recommended next action:** `{rec.action.value}`{target} — {rec.rationale}")
    L.append("")

    L.append("## Observed features")
    if r.observed_features:
        L.append("| feature | value | kind | confidence | source |")
        L.append("|---|---|---|---|---|")
        for f in r.observed_features:
            L.append(f"| {f.name} | {f.value} | {f.kind.value} | {f.confidence} | {f.source} |")
    else:
        L.append("_none provided_")
    L.append("")

    L.append("## Possible interpretations")
    for h in r.possible_interpretations:
        L.append(f"- {h.statement} _(confidence {h.confidence})_")
    L.append("")

    L.append("## Evidence")
    for e in r.supporting_evidence():
        cav = f" — _{e.caveats}_" if e.caveats else ""
        L.append(f"- **[{e.kind.value}]** {e.claim} _(confidence {e.confidence}, source: {e.source})_{cav}")
    L.append("")

    L.append("## Assumptions")
    for a in r.assumptions:
        L.append(f"- {a.statement} _(basis: {a.basis})_")
    L.append("")

    L.append("## Uncertainty")
    for u in r.uncertainty:
        L.append(f"- _({u.severity})_ {u.note}")
    L.append("")

    L.append("## Missing evidence")
    if r.missing_evidence:
        for m in r.missing_evidence:
            L.append(f"- **{m.name}** (expected {m.expected_kind.value}) — {m.why_needed}")
    else:
        L.append("_no required evidence is missing_")
    L.append("")

    L.append("## Human review checklist")
    for c in r.human_review_checklist:
        L.append(f"- [ ] {c.question} _({c.why})_")
    L.append("")

    L.append("## Limitations")
    L.append(r.limitations)
    L.append("")
    return "\n".join(L)
