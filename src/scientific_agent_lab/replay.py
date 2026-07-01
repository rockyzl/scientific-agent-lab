"""Replay helpers — the reasoning trace as an auditable, re-playable artifact."""

from __future__ import annotations

import json

from .schemas import ReplayRecord


def replay_to_json(record: ReplayRecord) -> str:
    return json.dumps(record.to_dict(), indent=2, default=str)


def step_names(record: ReplayRecord) -> list[str]:
    return [f"{s['step']}:{s['agent']}" for s in record.steps]
