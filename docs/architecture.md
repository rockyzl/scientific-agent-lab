# Architecture

## Core contract (`schemas.py`)

Everything flows through a small set of dataclasses (stdlib only):

- `ScientificInput` — question, domain, observations, and the **required** evidence the
  question needs (used to detect gaps).
- `ObservedFeature`, `EvidenceItem` — carry a value **and its provenance** (`EvidenceKind`:
  measurement / prediction / inference / literature / prior / missing).
- `Assumption`, `UncertaintyNote`, `MissingEvidence` — the things most demos hide.
- `RecommendedMeasurement` (a `NextAction`), `HumanReviewItem`.
- `ScientificAgentReport` — the full structured output.
- `ReplayRecord` — the step-by-step reasoning trace.
- `EvaluationResult` — contract scores.

## Pipeline (`workflow.py`)

Five small agents run in order; each appends its output to the replay record:

| Step | Agent | Produces |
|---|---|---|
| 1 | `observation_agent` | observed features (from input or an image skill) |
| 2 | `evidence_agent` | evidence + assumptions + missing/weak evidence |
| 3 | `hypothesis_agent` | tentative interpretations (hedged) |
| 4 | `planner_agent` | a justified next action |
| 5 | `reviewer_agent` | human-review checklist + uncertainty |

Confidence is **coverage-calibrated** (`skills/uncertainty.py`): missing required evidence
and prediction-instead-of-measurement drag it down.

## Evaluation (`evaluation/`)

`contracts.py` scores whether the report reasoned responsibly (evidence vs assumptions,
uncertainty present, gaps named, no overclaim, replayable). This is the differentiator —
the same golden-set / acceptance-contract discipline used in production agent evaluation,
applied to scientific reasoning.

## Extensibility

- **Skills** (`skills/`) are pluggable capabilities. v0 ships a real offline
  `literature` retrieval (stdlib TF-IDF over a curated knowledge base) and a still-mocked
  `image_stub`; a real vision model replaces the latter without touching the spine.
- **Instruments / tools** become connectors later (Phase 3: MCP-compatible). The spine
  never needs to know whether evidence came from a microscope, a database, or a
  simulation — only its `EvidenceKind` and confidence.
- **Engines** (property models, knowledge graphs, benchmarks) live in separate repos and
  are *called*, not duplicated here.
