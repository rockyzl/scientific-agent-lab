"""Command-line entry point.

    python -m scientific_agent_lab.cli run \
        --input examples/materials_demo/sample_input.json \
        --output outputs/demo_report.md

Writes four artifacts next to --output: the markdown report, the JSON report, the replay
record, and the evaluation result.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation.contracts import evaluate
from .report import to_json, to_markdown
from .schemas import ScientificInput
from .workflow import run_workflow


def _run(args: argparse.Namespace) -> int:
    inp = ScientificInput.from_dict(json.loads(Path(args.input).read_text()))
    report, replay = run_workflow(inp)
    result = evaluate(report, replay)

    out_md = Path(args.output)
    out_dir = out_md.parent if str(out_md.parent) else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_md.stem

    out_md.write_text(to_markdown(report))
    (out_dir / f"{stem}.json").write_text(to_json(report))
    (out_dir / "replay_record.json").write_text(to_json(replay))
    (out_dir / "evaluation_result.json").write_text(to_json(result))

    print("Wrote:")
    for p in (out_md, out_dir / f"{stem}.json", out_dir / "replay_record.json", out_dir / "evaluation_result.json"):
        print(f"  {p}")
    print(
        f"Evaluation: {result.passed}/{result.total} contracts passed (score {result.score}). "
        f"Next action = {report.recommended_next_measurement.action.value}; "
        f"confidence = {report.confidence_level}."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scientific-agent-lab",
        description="Evidence-grounded scientific agent with replayable evaluation.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="run the reasoning workflow on an input JSON")
    run.add_argument("--input", "-i", required=True, help="path to a ScientificInput JSON")
    run.add_argument("--output", "-o", default="outputs/demo_report.md", help="markdown output path")
    run.set_defaults(func=_run)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
