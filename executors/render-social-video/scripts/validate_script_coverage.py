#!/usr/bin/env python3
"""Validate a locked production script and its shot-by-shot asset evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_schema(document: dict, schema_name: str, failures: list[str]) -> None:
    schema = load_json(ROOT / "schemas" / schema_name)
    for error in sorted(Draft202012Validator(schema).iter_errors(document), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "root"
        failures.append(f"{schema_name}: {location}: {error.message}")


def resolve_declared(base: Path, value: str) -> Path:
    candidate = Path(value)
    return candidate.resolve() if candidate.is_absolute() else (base / candidate).resolve()


def validate(
    script_path: Path,
    evidence_path: Path | None,
    for_production: bool,
    plan_path: Path | None = None,
) -> dict:
    failures: list[str] = []
    script = load_json(script_path)
    validate_schema(script, "video-script.schema.json", failures)

    mode = script.get("workflow_mode")
    status = script.get("status")
    if for_production:
        if mode == "human-reviewed" and status not in {"approved", "locked"}:
            failures.append("human-reviewed script must be approved before asset collection or rendering")
        if mode == "fully-automated" and status != "locked":
            failures.append("fully-automated script must be locked before asset collection or rendering")

    shots = script.get("shots") or []
    shot_ids: set[str] = set()
    expected_start = 0.0
    for shot in shots:
        shot_id = str(shot.get("id") or "")
        if shot_id in shot_ids:
            failures.append(f"duplicate shot id: {shot_id}")
        shot_ids.add(shot_id)
        start = float(shot.get("start_seconds") or 0)
        end = float(shot.get("end_seconds") or 0)
        if abs(start - expected_start) > 0.02:
            failures.append(f"shot {shot_id} does not start at the previous shot end")
        if end <= start:
            failures.append(f"shot {shot_id} has a non-positive duration")
        expected_start = end
        requirement_ids = [str(item.get("id") or "") for item in shot.get("requirements") or []]
        if len(requirement_ids) != len(set(requirement_ids)):
            failures.append(f"shot {shot_id} has duplicate requirement ids")
    if shots and abs(expected_start - float(script.get("total_duration_seconds") or 0)) > 0.02:
        failures.append("total_duration_seconds does not match the final shot end")

    if evidence_path is None:
        if for_production:
            failures.append("asset evidence ledger is required for production")
        return {"status": "pass" if not failures else "failed", "failures": failures}

    evidence = load_json(evidence_path)
    validate_schema(evidence, "asset-evidence-ledger.schema.json", failures)
    if str(evidence.get("script_sha256") or "") != sha256_file(script_path):
        failures.append("asset evidence ledger is not bound to the current script hash")
    declared_script = resolve_declared(evidence_path.parent, str(evidence.get("script_file") or ""))
    if declared_script != script_path:
        failures.append("asset evidence ledger points to a different script file")

    evidence_by_shot = {str(item.get("shot_id") or ""): item for item in evidence.get("shots") or []}
    if set(evidence_by_shot) != shot_ids:
        failures.append("asset evidence ledger does not cover the exact script shot set")
    for shot in shots:
        shot_id = str(shot["id"])
        observed = evidence_by_shot.get(shot_id)
        if not observed:
            continue
        asset = resolve_declared(evidence_path.parent, str(observed.get("asset_file") or ""))
        if not asset.is_file():
            failures.append(f"shot {shot_id} asset file is missing")
        elif sha256_file(asset) != str(observed.get("asset_sha256") or ""):
            failures.append(f"shot {shot_id} asset hash does not match")
        expected_requirements = {str(item["id"]): item for item in shot.get("requirements") or []}
        observed_requirements = {
            str(item.get("requirement_id") or ""): item for item in observed.get("requirements") or []
        }
        if set(observed_requirements) != set(expected_requirements):
            failures.append(f"shot {shot_id} does not cover the exact requirement set")
        duration = float(shot["end_seconds"]) - float(shot["start_seconds"])
        for requirement_id, requirement in expected_requirements.items():
            result = observed_requirements.get(requirement_id)
            if not result:
                continue
            timestamp = float(result.get("evidence_timestamp_seconds") or 0)
            if timestamp > duration + 0.02:
                failures.append(f"shot {shot_id} requirement {requirement_id} evidence is outside the shot")
            if float(result.get("observed_hold_seconds") or 0) + 0.02 < float(requirement["minimum_hold_seconds"]):
                failures.append(f"shot {shot_id} requirement {requirement_id} readable hold is too short")
            evidence_file = resolve_declared(evidence_path.parent, str(result.get("evidence_file") or ""))
            if not evidence_file.is_file():
                failures.append(f"shot {shot_id} requirement {requirement_id} evidence file is missing")

    if for_production and plan_path is None:
        failures.append("video plan is required for the production coverage gate")
    if plan_path is not None:
        plan = load_json(plan_path)
        scenes = plan.get("scenes") or []
        if [str(scene.get("id") or "") for scene in scenes] != [str(shot.get("id") or "") for shot in shots]:
            failures.append("video plan scene order does not exactly match the script shots")
        source_roles = {
            "screen-recording": "screen-recording",
            "product-screenshot": "product-screenshot",
            "rendered-card": "rendered-card",
            "deterministic-animation": "deterministic-animation",
            "generated-broll": "generated-broll",
        }
        for shot, scene in zip(shots, scenes):
            shot_id = str(shot["id"])
            duration = float(shot["end_seconds"]) - float(shot["start_seconds"])
            if abs(float(scene.get("duration") or 0) - duration) > 0.02:
                failures.append(f"scene {shot_id} duration does not match the script")
            if str(scene.get("narration") or "") != str(shot.get("narration") or ""):
                failures.append(f"scene {shot_id} narration does not match the script")
            if str(shot.get("subtitle") or "") != str(shot.get("narration") or ""):
                failures.append(f"scene {shot_id} subtitle differs from narration but the renderer has one text track")
            expected_role = source_roles.get(str(shot.get("source_type") or ""))
            if expected_role and str(scene.get("asset_role") or "") != expected_role:
                failures.append(f"scene {shot_id} asset role does not match the script source type")
            observed = evidence_by_shot.get(shot_id)
            if observed and scene.get("asset"):
                plan_asset = resolve_declared(plan_path.parent, str(scene["asset"]))
                evidence_asset = resolve_declared(evidence_path.parent, str(observed["asset_file"]))
                if plan_asset != evidence_asset:
                    failures.append(f"scene {shot_id} plan asset differs from the verified evidence asset")

    return {
        "status": "pass" if not failures else "failed",
        "script": str(script_path),
        "evidence": str(evidence_path),
        "shot_count": len(shots),
        "requirement_count": sum(len(shot.get("requirements") or []) for shot in shots),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", required=True, type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--for-production", action="store_true")
    args = parser.parse_args()
    try:
        result = validate(
            args.script.expanduser().resolve(),
            args.evidence.expanduser().resolve() if args.evidence else None,
            args.for_production,
            args.plan.expanduser().resolve() if args.plan else None,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = {"status": "failed", "failures": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
