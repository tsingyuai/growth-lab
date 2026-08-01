#!/usr/bin/env python3
"""Validate that one, and only one, visual learning reference was selected."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_REASONS = ("topic_fit", "visual_quality", "product_fit", "non_copying_boundary")


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def validate(selection_path: Path, candidates_path: Path) -> dict[str, Any]:
    selection = read_json(selection_path)
    candidates = read_json(candidates_path)
    if selection.get("schema_version") != 1:
        raise ValueError("selection schema_version must be 1")
    primary = selection.get("primary")
    if not isinstance(primary, dict):
        raise ValueError("selection must contain exactly one primary object")
    if isinstance(selection.get("primaries"), list) or isinstance(selection.get("selected"), list):
        raise ValueError("multiple-primary fields are not allowed")
    note_id = str(primary.get("note_id") or "")
    candidate_by_id = {
        str(item.get("note_id")): item
        for item in candidates.get("candidates") or []
        if isinstance(item, dict)
    }
    if note_id not in candidate_by_id:
        raise ValueError("primary note_id is not present in visual-candidates.json")
    reference_image = str(primary.get("reference_image") or "")
    if reference_image not in candidate_by_id[note_id].get("image_files", []):
        raise ValueError("primary reference_image is not one of the candidate image files")
    root = candidates_path.parent.resolve()
    image_path = (root / reference_image).resolve()
    if root not in image_path.parents or not image_path.is_file():
        raise ValueError("primary reference image is missing or outside the run directory")
    reasons = primary.get("reasons")
    if not isinstance(reasons, dict):
        raise ValueError("primary reasons must be an object")
    for key in REQUIRED_REASONS:
        if not str(reasons.get(key) or "").strip():
            raise ValueError(f"primary reasons.{key} is required")
    rejected = selection.get("rejected_candidate_ids")
    expected_rejected = set(candidate_by_id) - {note_id}
    if set(rejected or []) != expected_rejected:
        raise ValueError("rejected_candidate_ids must contain every non-primary candidate exactly once")
    return {"primary_note_id": note_id, "reference_image": reference_image}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a single visual reference selection")
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--candidates", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate(args.selection, args.candidates)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
