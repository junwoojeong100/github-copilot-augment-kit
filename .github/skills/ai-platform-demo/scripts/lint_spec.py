#!/usr/bin/env python3
"""Fast pre-QA lint for a demo-spec.json.

Runs render_demo's full structural / semantic / security validation, then checks the
interaction invariants that the browser QA (scripts/verify_demo.js) enforces.
This catches the common gotchas in under a second instead of a ~2 minute Puppeteer cycle.

The timing thresholds mirror the fixed Golden Runtime plus the waits in verify_demo.js.
Run this before rendering and before the browser QA:

    python3 -B scripts/lint_spec.py <demo-spec.json>
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_demo  # noqa: E402

ORCH_SUMMARY_RE = re.compile(r"decision package|의사결정 패키지", re.IGNORECASE)


def _reject_constant(value: str):
    raise render_demo.SpecError(f"non-finite JSON constant is not allowed: {value}")


def qa_invariants(spec: dict) -> list[str]:
    """Return a list of QA-invariant problems (empty means all satisfied)."""
    problems: list[str] = []

    ops = spec.get("operations", {}).get("action", {})
    if ops.get("recommendationBefore") == ops.get("recommendationAfter"):
        problems.append(
            "operations.action.recommendationBefore equals recommendationAfter: the re-optimize "
            "action will not visibly change the recommendation."
        )

    orchestration = spec.get("agents", {}).get("orchestration", {})
    if not ORCH_SUMMARY_RE.search(str(orchestration.get("summary", ""))):
        problems.append(
            "agents.orchestration.summary must contain '의사결정 패키지' (or 'decision package'): "
            "browser QA checks the chat log for that phrase after orchestration runs."
        )

    governance = spec.get("governance", {})
    cards = governance.get("cards", [])
    final_score = governance.get("evaluation", {}).get("finalScore")
    if cards and final_score is not None:
        try:
            visible_score = float(cards[0].get("value"))
            final_numeric = float(final_score)
        except (TypeError, ValueError):
            pass
        else:
            if (
                math.isfinite(visible_score)
                and math.isfinite(final_numeric)
                and math.isclose(visible_score, final_numeric, rel_tol=0, abs_tol=1e-9)
            ):
                problems.append(
                    "governance.cards[0].value equals evaluation.finalScore: the evaluation score "
                    "will not visibly change on run — set cards[0].value to the initial score."
                )

    output = spec.get("simulator", {}).get("output", {})
    good = output.get("goodThreshold")
    warn = output.get("warningThreshold")
    if isinstance(good, (int, float)) and isinstance(warn, (int, float)) and not good > warn:
        problems.append(
            "simulator.output.goodThreshold must be greater than warningThreshold: the runtime "
            "treats a HIGH output as good/green, so frame the output as a positive score."
        )

    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Fast pre-QA lint for a demo-spec.json.")
    parser.add_argument("spec", type=Path, help="Path to demo-spec.json")
    args = parser.parse_args()

    try:
        with args.spec.open(encoding="utf-8") as stream:
            spec = json.load(stream, parse_constant=_reject_constant)
    except (OSError, ValueError, render_demo.SpecError) as error:
        print(f"[lint] cannot read spec: {error}")
        return 2
    if not isinstance(spec, dict):
        print("[lint] top-level JSON must be an object")
        return 2

    # 1) Full structural / semantic / security validation (same as render_demo --validate-only).
    try:
        spec = render_demo.sanitize_rich_fields(spec)
        render_demo.validate_spec(spec)
    except render_demo.SpecError as error:
        print(f"[lint] STRUCTURE: {error}")
        return 1

    # 2) Interaction / timing invariants enforced by the browser QA.
    problems = qa_invariants(spec)
    if problems:
        print("[lint] QA-invariant problems:")
        for item in problems:
            print(f"  - {item}")
        return 1

    print("[lint] OK — structure valid and QA invariants satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
