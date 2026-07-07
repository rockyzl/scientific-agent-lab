# scientific-agent-lab

[![CI](https://github.com/rockyzl/scientific-agent-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/rockyzl/scientific-agent-lab/actions/workflows/ci.yml)
&nbsp;![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
&nbsp;![License: MIT](https://img.shields.io/badge/license-MIT-green)

**scientific-agent-lab is not another scientific AI assistant. It is an evaluation,
reasoning, and reproducibility layer for scientific AI systems.**

Scientific workbenches and foundation models (Claude Science, BioNeMo, GPT, …) help
scientists *produce* results. This project sits one layer below them and asks the
question they mostly leave open: **when can you trust the result?** It makes scientific
reasoning **auditable, replayable, reviewable, reproducible, and testable**.

> Scientific agents should not only generate hypotheses; they should produce auditable
> reasoning artifacts that can be replayed, reviewed, and evaluated.

An agent may organize a workflow, but every conclusion must separate **evidence** from
**assumptions**, keep **uncertainty** explicit, name what evidence is **missing**,
recommend a **justified next action**, leave a **replayable trace**, and ship a
**reproducibility record** a human scientist can re-run.

> Status: early research prototype (v0.1). Not a validated scientific decision system.
> Runs fully offline — no API keys, no GPU, zero third-party dependencies.

## Why this exists

Autonomous science needs more than a model that emits a plausible-sounding answer. It
needs a reasoning layer that knows *what it knows, what it assumes, and what it still
needs to measure*. In production AI, that discipline is enforced with golden sets and
acceptance contracts. This project brings the same discipline to scientific discovery.

The differentiator is **evaluation-first**: the repo ships an evaluation harness that
scores whether an agent *reasoned responsibly*, not just whether it sounded confident.

## Where this sits

```
Foundation models          Claude · GPT · Gemini
        │
Scientific workbenches      Claude Science · BioNeMo        ← produce results
        │
Scientific workflow         agents · tool use · lab integration
        │
Scientific reasoning        evidence · uncertainty · human review   ◄─ scientific-agent-lab
        │
Scientific evaluation       golden sets · replay · acceptance contracts ◄─ scientific-agent-lab
```

Models change; **evaluation and reproducibility don't** — the same way `pytest` and CI
outlive any single language version. This project claims the bottom two layers.

## The workflow (v0 spine)

```
Scientific input (question + observations + what evidence is required)
      │
      ▼
1. observation_agent   → observed features
2. evidence_agent      → evidence (with provenance) · assumptions · missing evidence
3. hypothesis_agent    → tentative interpretations (never overclaimed)
4. planner_agent       → justified next action (measure / literature / simulate / review / accept)
5. reviewer_agent      → human-review checklist · explicit uncertainty
      │
      ▼
ScientificAgentReport  → Markdown + JSON + replay record + evaluation result
```

Every step is saved as a **replay artifact**, and the final report is scored against
**evaluation contracts**.

## Quickstart

```bash
git clone https://github.com/rockyzl/scientific-agent-lab
cd scientific-agent-lab

# no install needed — zero dependencies
PYTHONPATH=src python -m scientific_agent_lab.cli run \
  --input examples/materials_demo/sample_input.json \
  --output outputs/demo_report.md

# or install it
pip install -e .
scientific-agent-lab run -i examples/materials_demo/sample_input.json -o outputs/demo_report.md
```

This writes `outputs/demo_report.md`, `demo_report.json`, `replay_record.json`, and
`evaluation_result.json`. See a committed example in
[`examples/materials_demo/sample_output.md`](examples/materials_demo/sample_output.md).

### Local live demo (browser)

A stdlib-only server that runs the pipeline live — pick a preset case or edit the
JSON input and watch the five agents produce the auditable report, evaluation
scorecard, and reproducibility record:

```bash
python demo/serve.py            # → http://localhost:8000  (no dependencies)
```

## Evaluation contracts (the spine)

The harness checks whether a report reasoned responsibly:

1. `report_has_evidence_section`
2. `report_has_assumptions_section`
3. `report_has_uncertainty_section`
4. `report_has_missing_evidence_section` — if not highly confident, it must name a gap
5. `report_has_human_review_checklist`
6. `recommendations_are_not_overclaimed` — hedged language; no `accept` while evidence is missing
7. `confidence_level_is_present`
8. `replay_record_contains_intermediate_steps`
9. `result_is_reproducible` — a reproducibility record (input hash, versions, evidence sources, steps) is attached

An overclaimed report (e.g. `accept` despite a missing measurement) **fails** — see
`tests/test_evaluation.py`.

## Benchmark

Run the agent over a folder of scientific cases and score how well it *reasoned*:

```bash
PYTHONPATH=src python -m scientific_agent_lab.cli benchmark --cases benchmark/cases
```

```
case                           contracts  missing   conf     next_action  expect
rfb_catholyte_incomplete             9/9        2   0.29   measure_again    PASS
microscopy_phase_id_incomplete       9/9        2    0.3   measure_again    PASS
xrd_complete_accept                  9/9        0   0.89          accept    PASS
```

Each case carries expected properties (missing count, allowed next action, confidence
band); a case passes only if it meets them **and** all reasoning contracts.

## Reproducibility

Every run ships a **reproducibility record** (input hash, report content hash, package &
Python versions, skill versions, evidence sources, step count) and the evaluation result
is **versioned** (`contract_set_version`). Prove a result is re-runnable:

```bash
PYTHONPATH=src python -m scientific_agent_lab.cli verify -i examples/materials_demo/sample_input.json
# report_sha256  run1=1ba1e3321f320915  run2=1ba1e3321f320915
# REPRODUCIBLE ✓
```

Same input → identical report hash. Models change; this guarantee shouldn't.

## How this fits my other work

`scientific-agent-lab` is deliberately the **public integration + evaluation layer**, not
another model-training repo. It defines the schema, report, replay, and evaluation spine,
and is designed to *call* specialized engines later rather than duplicate them:

- **[scientific-foundation-model-lab](https://github.com/rockyzl/scientific-foundation-model-lab)** — molecular-property ML / RDKit / PyTorch baselines (a model engine).
- domain workflow & knowledge-graph engines (ChemGraph-style molecule→property workflows).
- flow-battery benchmark / dataset graphs (domain evaluation cases).

Those stay specialized; this repo is the clean, reviewable layer that connects data,
tools, evidence, and human judgment.

## Roadmap

See [`docs/roadmap.md`](docs/roadmap.md). Briefly:

- **Phase 0 (now):** evaluation spine, runnable end-to-end.
- **Phase 1 (done):** real **offline** literature retrieval — stdlib TF-IDF over a
  curated domain knowledge base (kept offline/deterministic by design; optional live
  arXiv / Crossref / Semantic Scholar connectors can be added later).
- **Phase 2:** scientific database connectors (Materials Project, PubChem, property tools).
- **Phase 3:** MCP-compatible tool connectors (instruments/tools as connectors).
- **Phase 4:** digital-twin adapters (microscopy / simulation).
- **Phase 5:** a benchmark + replay-based scientific-agent evaluation suite.

## Community

Built to grow with the emerging AI-for-Science / autonomous-science community — LLMs for
materials & chemistry, microscopy automation, digital twins, scientific tool use, and
human-in-the-loop scientific workflows. See [`docs/community-strategy.md`](docs/community-strategy.md).
(Inspired by that community; no endorsement or affiliation is implied.)

## Disclaimer

Research prototype. Interpretations are tentative and must be confirmed by a domain
expert. Literature retrieval runs over a small curated offline knowledge base (not a
live literature API). This offline build ships no vision model, so image-derived
features are unavailable — reported as missing evidence, never invented. Do not use for
real scientific or safety decisions.

## License

MIT — see [LICENSE](LICENSE).
