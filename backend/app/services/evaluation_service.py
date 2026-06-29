"""Minimal fixed evaluation set for Phase 2 regression checks.

This is not a full benchmark runner. It provides a repeatable question set and
keyword expectations so Phase 2 verification can document that hybrid retrieval,
trace visibility, and abstention behavior remain testable across changes.
"""

from __future__ import annotations

import csv
from pathlib import Path

_FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "tests"
    / "fixtures"
    / "phase2_eval_questions.csv"
)


def load_phase2_eval_questions() -> list[dict[str, str]]:
    with _FIXTURE_PATH.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))
