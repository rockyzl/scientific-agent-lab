#!/usr/bin/env python3
"""Local live demo server for scientific-agent-lab — stdlib only, no dependencies.

    python demo/serve.py            # then open http://localhost:8000
    python demo/serve.py 8123       # custom port

Serves a small UI that runs the REAL pipeline live: pick a preset case or paste
your own scientific input, and watch the five deterministic agents produce an
auditable report + evaluation + reproducibility record. Fully offline; no API keys.
"""
from __future__ import annotations

import http.server
import json
import pathlib
import socketserver
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scientific_agent_lab.evaluation.contracts import evaluate  # noqa: E402
from scientific_agent_lab.report import to_json  # noqa: E402
from scientific_agent_lab.schemas import ScientificInput  # noqa: E402
from scientific_agent_lab.workflow import run_workflow  # noqa: E402

HERE = pathlib.Path(__file__).parent
HTML = (HERE / "index.html").read_text(encoding="utf-8")


def _load_cases() -> dict:
    cases = {}
    cdir = ROOT / "benchmark" / "cases"
    for fp in sorted(cdir.glob("*.json")):
        raw = json.loads(fp.read_text())
        key = fp.stem.split("_", 1)[-1] if "_" in fp.stem else fp.stem
        cases[key] = raw
    return cases


CASES = _load_cases()


def run_case(inp_dict: dict) -> dict:
    if not isinstance(inp_dict, dict) or not inp_dict.get("question"):
        raise ValueError("input must be an object with at least a 'question' field")
    inp = ScientificInput.from_dict(inp_dict)
    report, replay = run_workflow(inp)
    result = evaluate(report, replay)
    return {
        "input": inp_dict,
        "report": json.loads(to_json(report)),
        "eval": json.loads(to_json(result)),
        "replay": json.loads(to_json(replay)),
    }


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code: int, body, ctype: str = "application/json") -> None:
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            self._send(200, HTML, "text/html; charset=utf-8")
        elif self.path == "/cases":
            self._send(200, json.dumps(CASES))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/run":
            self._send(404, json.dumps({"error": "not found"}))
            return
        n = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            body = json.loads(raw or b"{}")
            self._send(200, json.dumps(run_case(body.get("input") or {})))
        except Exception as e:  # noqa: BLE001
            self._send(400, json.dumps({"error": f"{type(e).__name__}: {e}"}))

    def log_message(self, *args) -> None:  # quiet
        pass


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"scientific-agent-lab live demo → http://localhost:{port}  ({len(CASES)} preset cases)")
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")


if __name__ == "__main__":
    main()
