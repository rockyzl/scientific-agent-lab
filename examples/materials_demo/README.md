# Materials demo — nonaqueous redox-flow-battery catholyte screening

A small, domain-authentic example: an agent is asked whether a candidate redox-active
molecule is a viable nonaqueous RFB catholyte, given a measured redox potential and a
*predicted* solubility, with cycling stability and a literature reference still missing.

Run it:

```bash
PYTHONPATH=src python -m scientific_agent_lab.cli run \
  --input examples/materials_demo/sample_input.json \
  --output outputs/demo_report.md
```

What to notice in the output ([`sample_output.md`](sample_output.md)):

- The predicted solubility is **not** silently accepted as a measurement — it becomes an
  explicit assumption + uncertainty note.
- The two missing required items (`cycling_stability`, `reference_match`) are named.
- Confidence is **low (0.29)** because required evidence is missing.
- The recommended next action is `measure_again` (cycling stability), not `accept`.
- A human-review checklist is produced.
- All 9 evaluation contracts pass — the agent reasoned responsibly.
