# Roadmap

The first version deliberately does one thing well: the **evidence + evaluation spine**.
Everything else is layered on top without redesigning the core.

- **Phase 0 — spine (now).** Schemas, five-step workflow, replay record, evaluation
  contracts, Markdown/JSON reports, one runnable demo. Mocked image + literature skills.
  Zero dependencies.
- **Phase 1 — real literature retrieval (done, offline).** `literature_stub` replaced by
  a real stdlib TF-IDF retrieval over a curated domain knowledge base — kept offline and
  deterministic to preserve reproducibility. Optional live connectors (arXiv / Crossref /
  Semantic Scholar) can attach real citations later without touching the spine.
- **Phase 2 — scientific database connectors.** Materials Project, PubChem, molecular
  property tools; predicted values labelled `prediction`, DB facts labelled `literature`.
- **Phase 3 — MCP-compatible tool connectors.** Instruments and tools exposed as
  connectors so the agent can request evidence, not just receive it.
- **Phase 4 — digital-twin adapters.** Microscopy / simulation digital twins as evidence
  sources and as targets for the recommended next action.
- **Phase 5 — scientific-agent evaluation suite.** A replayable benchmark of scientific
  reasoning cases (materials, chemistry, microscopy) with per-case acceptance contracts —
  the piece almost no one is building.

## Design rules

- Keep the core dependency-light and runnable on clone.
- No heavy orchestration framework (LangGraph / AutoGen / CrewAI) until the spine demands
  it.
- New capabilities enter as **skills** or **connectors**, never by bloating the spine.
- Honesty over impressiveness: mocks are labelled; nothing is overclaimed.
