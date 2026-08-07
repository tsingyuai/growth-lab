#!/usr/bin/env python3
"""Validate the non-compensating visual self-review gate for social cards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import sys


SCORES = {
    "content_completeness", "hierarchy", "composition", "layout_vitality",
    "mobile_readability", "evidence_strength", "visual_finish", "benchmark_parity",
}
CARD_CHECKS = {
    "one_clear_job", "no_placeholder_content", "no_purposeless_empty_zone",
    "exact_copy", "evidence_target_visible", "phone_scale_checked",
}
SEQUENCE_CHECKS = {
    "distinct_compositions", "no_template_repetition",
    "distinct_product_states", "coherent_visual_system",
}


def fail(message: str) -> None:
    raise ValueError(message)


def require_true_map(value: object, keys: set[str], label: str) -> None:
    if not isinstance(value, dict):
        fail(f"{label} must be an object")
    missing = sorted(keys - set(value))
    if missing:
        fail(f"{label} missing: {', '.join(missing)}")
    failed = sorted(key for key in keys if value.get(key) is not True)
    if failed:
        fail(f"{label} failed: {', '.join(failed)}")


def validate_review(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid quality review: {exc}")
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        fail("schema_version must be 1")
    if data.get("status") != "pass":
        fail("status must be pass; failed candidates require rework")
    attempt = data.get("attempt")
    if not isinstance(attempt, int) or isinstance(attempt, bool) or not 1 <= attempt <= 3:
        fail("attempt must be an integer from 1 to 3")
    if data.get("reviewed_at_phone_scale") is not True:
        fail("reviewed_at_phone_scale must be true")
    benchmark = data.get("benchmark")
    if not isinstance(benchmark, dict) or not str(benchmark.get("source") or "").strip():
        fail("benchmark.source is required")
    if benchmark.get("approved_by_user") is not True:
        fail("benchmark must be approved by the user")
    cards = data.get("cards")
    if not isinstance(cards, list) or not cards:
        fail("cards must be a non-empty array")
    seen: set[str] = set()
    for index, card in enumerate(cards):
        label = f"cards[{index}]"
        if not isinstance(card, dict):
            fail(f"{label} must be an object")
        card_id = str(card.get("id") or "").strip()
        if not card_id or card_id in seen:
            fail(f"{label}.id is missing or duplicated")
        seen.add(card_id)
        output = card.get("output")
        if not isinstance(output, str):
            fail(f"{label}.output is required")
        relative = PurePosixPath(output)
        if relative.is_absolute() or ".." in relative.parts or relative.parts[:1] != ("render",) or relative.suffix.lower() != ".png":
            fail(f"{label}.output must be a safe render/*.png path")
        if card.get("decision") != "approved":
            fail(f"{label}.decision must be approved")
        scores = card.get("scores")
        if not isinstance(scores, dict):
            fail(f"{label}.scores must be an object")
        missing_scores = sorted(SCORES - set(scores))
        if missing_scores:
            fail(f"{label}.scores missing: {', '.join(missing_scores)}")
        failed_scores = sorted(
            key for key in SCORES
            if not isinstance(scores.get(key), (int, float))
            or isinstance(scores.get(key), bool)
            or not 4 <= float(scores[key]) <= 5
        )
        if failed_scores:
            fail(f"{label}.scores below 4 or invalid: {', '.join(failed_scores)}")
        require_true_map(card.get("checks"), CARD_CHECKS, f"{label}.checks")
        if card.get("failure_modes") not in ([], None):
            fail(f"{label}.failure_modes must be empty for an approved card")
        if card.get("next_action") != "none":
            fail(f"{label}.next_action must be none for an approved card")
    require_true_map(data.get("sequence_checks"), SEQUENCE_CHECKS, "sequence_checks")
    if data.get("rework_items") not in ([], None):
        fail("rework_items must be empty when status is pass")
    return {"ok": True, "status": "pass", "attempt": attempt, "card_ids": sorted(seen)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate_review(args.review)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
