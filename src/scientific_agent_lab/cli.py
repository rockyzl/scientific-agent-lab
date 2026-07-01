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
from datetime import datetime, timezone
from pathlib import Path

from .evaluation.benchmark import format_report, is_fully_passing, run_benchmark
from .evaluation.contracts import evaluate
from .report import to_json, to_markdown
from .schemas import ScientificInput
from .workflow import run_workflow


def _run(args: argparse.Namespace) -> int:
    inp = ScientificInput.from_dict(json.loads(Path(args.input).read_text()))
    report, replay = run_workflow(inp)
    replay.reproducibility.created_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
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


def _benchmark(args: argparse.Namespace) -> int:
    results = run_benchmark(args.cases)
    print(format_report(results))
    return 0 if all(is_fully_passing(r) for r in results) else 1


def _verify(args: argparse.Namespace) -> int:
    """Run the same input twice and confirm the report content hash is identical."""
    inp = ScientificInput.from_dict(json.loads(Path(args.input).read_text()))
    _, r1 = run_workflow(inp)
    _, r2 = run_workflow(inp)
    h1, h2 = r1.reproducibility.report_sha256, r2.reproducibility.report_sha256
    ok = bool(h1) and h1 == h2
    print(f"report_sha256  run1={h1}  run2={h2}")
    print("REPRODUCIBLE ✓" if ok else "NOT REPRODUCIBLE ✗")
    return 0 if ok else 1


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

    bench = sub.add_parser("benchmark", help="run the evaluation benchmark over a cases folder")
    bench.add_argument("--cases", default="benchmark/cases", help="folder of case JSON files")
    bench.set_defaults(func=_benchmark)

    verify = sub.add_parser("verify", help="run an input twice and check the report hash is identical")
    verify.add_argument("--input", "-i", required=True, help="path to a ScientificInput JSON")
    verify.set_defaults(func=_verify)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
