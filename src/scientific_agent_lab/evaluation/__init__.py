"""Replayable, contract-based evaluation of scientific-agent reports."""

from .contracts import evaluate
from .metrics import score

__all__ = ["evaluate", "score"]
