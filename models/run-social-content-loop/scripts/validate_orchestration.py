#!/usr/bin/env python3
"""Validate cross-platform social research, brief, and package orchestration."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


PLATFORMS = {"x", "xiaohongshu", "wechat", "instagram", "tiktok", "email"}
SOURCE_PLATFORMS = PLATFORMS | {"user-provided"}
LEARNING_SCOPES = {"topic", "structure", "tone", "visual", "format"}
OUTPUT_FORMATS = {"text", "image", "video"}
GOVERNANCE_FIELDS = {
    "all_stages_scope_acknowledged",
    "skill_neutrality_persistent_acknowledged",
    "publisher_responsibility_accepted",
    "account_authority_confirmed",
    "safety_rules_remain_applicable_acknowledged",
}


class ValidationError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"无法读取有效 JSON：{path}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"顶层必须是对象：{path}")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_copy_fingerprint(text: str) -> str:
    without_tags = re.sub(r"(?<!\S)#[^\s#]+", "", text.casefold())
    return " ".join(without_tags.split())


def unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValidationError(f"{label} 不得重复。")


def required_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{label} 必须是非空字符串。")
    return value.strip()


def safe_path(base: Path, raw: Any, label: str) -> Path:
    value = required_text(raw, label)
    candidate = (base / value).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise ValidationError(f"{label} 必须位于 {base} 内。") from exc
    return candidate


def safe_file(base: Path, raw: Any, label: str) -> Path:
    candidate = safe_path(base, raw, label)
    if not candidate.is_file():
        raise ValidationError(f"{label} 文件不存在：{raw}")
    return candidate


def validate_governance(value: Any, required: bool) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError("content_governance 必须是对象。")
    if required:
        missing = sorted(field for field in GOVERNANCE_FIELDS if value.get(field) is not True)
        if missing:
            raise ValidationError("内容生成前缺少全生命周期确认：" + ", ".join(missing))
        required_text(value.get("confirmed_at"), "content_governance.confirmed_at")
    return value


def validate_plan(
    run_dir: Path, require_governance: bool, require_evidence: bool
) -> tuple[dict[str, Any], list[str], dict[str, dict[str, Any]]]:
    plan_path = run_dir / "research-plan.json"
    plan = read_json(plan_path)
    if plan.get("schema_version") != 1:
        raise ValidationError("research-plan schema_version 必须是 1。")
    required_text(plan.get("run_id"), "run_id")
    required_text(plan.get("objective"), "objective")
    research = plan.get("research")
    distribution = plan.get("distribution")
    if not isinstance(research, dict) or not isinstance(distribution, dict):
        raise ValidationError("research 和 distribution 必须是对象。")
    if research.get("mode") not in {"independent", "synthesize"}:
        raise ValidationError("research.mode 无效。")
    sources = research.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValidationError("research.sources 至少包含一个来源。")
    source_map: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValidationError("research.sources 项必须是对象。")
        source_id = required_text(source.get("id"), f"sources[{index}].id")
        if source_id in source_map:
            raise ValidationError("research source id 不得重复。")
        if source.get("platform") not in SOURCE_PLATFORMS:
            raise ValidationError(f"sources[{index}].platform 无效。")
        if source.get("role") not in {"primary", "supporting"}:
            raise ValidationError(f"sources[{index}].role 无效。")
        files = source.get("evidence_files")
        if not isinstance(files, list) or not files:
            raise ValidationError(f"sources[{index}].evidence_files 不能为空。")
        for file_index, raw in enumerate(files):
            label = f"sources[{index}].evidence_files[{file_index}]"
            if require_evidence:
                safe_file(run_dir, raw, label)
            else:
                safe_path(run_dir, raw, label)
        source_map[source_id] = source
    if not any(source.get("role") == "primary" for source in sources):
        raise ValidationError("至少需要一个 primary research source。")
    scopes = research.get("learning_scope")
    if not isinstance(scopes, list) or not scopes or not set(scopes) <= LEARNING_SCOPES:
        raise ValidationError("research.learning_scope 包含无效值或为空。")
    unique(scopes, "research.learning_scope")
    targets = distribution.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ValidationError("distribution.targets 至少包含一个目标。")
    target_map: dict[str, dict[str, Any]] = {}
    for index, target in enumerate(targets):
        if not isinstance(target, dict) or target.get("platform") not in PLATFORMS:
            raise ValidationError(f"targets[{index}].platform 无效。")
        platform = target["platform"]
        if platform in target_map:
            raise ValidationError("distribution target platform 不得重复。")
        if target.get("account_role") not in {"official", "brand", "personal"}:
            raise ValidationError(f"targets[{index}].account_role 无效。")
        required_text(target.get("objective"), f"targets[{index}].objective")
        if target.get("adapter_mode") not in {"platform-native", "close-adaptation", "close-replication"}:
            raise ValidationError(f"targets[{index}].adapter_mode 无效。")
        formats = target.get("formats", ["text"])
        if not isinstance(formats, list) or not formats or not set(formats) <= OUTPUT_FORMATS:
            raise ValidationError(f"targets[{index}].formats 无效或为空。")
        unique(formats, f"targets[{index}].formats")
        if target.get("adapter_mode") == "close-replication":
            policy = target.get("replication_policy")
            if not isinstance(policy, dict):
                raise ValidationError(f"targets[{index}].replication_policy 必须明确确认。")
            for field in ("risk_accepted", "single_reference_only", "replace_source_assets"):
                if policy.get(field) is not True:
                    raise ValidationError(f"targets[{index}].replication_policy.{field} 必须为 true。")
            required_text(policy.get("rights_basis"), f"targets[{index}].replication_policy.rights_basis")
            required_text(policy.get("confirmed_at"), f"targets[{index}].replication_policy.confirmed_at")
        target_map[platform] = target
    expected_mode = "single-target" if len(targets) == 1 else "multi-target"
    if distribution.get("mode") != expected_mode:
        raise ValidationError(f"distribution.mode 应为 {expected_mode}。")
    if len(targets) > 1 and any(target["adapter_mode"] != "platform-native" for target in targets):
        raise ValidationError("多平台输出必须使用 platform-native。")
    validate_governance(plan.get("content_governance"), require_governance)
    return plan, list(target_map), source_map


def validate_brief(run_dir: Path, plan: dict[str, Any], targets: list[str], source_map: dict[str, dict[str, Any]]) -> dict[str, Any]:
    plan_path = run_dir / "research-plan.json"
    brief_path = run_dir / "canonical-brief.json"
    brief = read_json(brief_path)
    if brief.get("schema_version") != 1 or brief.get("status") != "approved":
        raise ValidationError("canonical brief 必须是 schema 1 且 status=approved。")
    if brief.get("research_plan_sha256") != sha256_file(plan_path):
        raise ValidationError("canonical brief 引用的 research plan 哈希不匹配。")
    if brief.get("content_governance") != plan.get("content_governance"):
        raise ValidationError("canonical brief 必须继承相同 content_governance。")
    facts = brief.get("product_facts")
    if not isinstance(facts, list) or not facts:
        raise ValidationError("canonical brief 至少需要一个 product fact。")
    for fact_index, fact in enumerate(facts):
        required_text(fact.get("claim") if isinstance(fact, dict) else None, f"product_facts[{fact_index}].claim")
        files = fact.get("evidence_files") if isinstance(fact, dict) else None
        if not isinstance(files, list) or not files:
            raise ValidationError(f"product_facts[{fact_index}].evidence_files 不能为空。")
        for file_index, raw in enumerate(files):
            safe_file(run_dir, raw, f"product_facts[{fact_index}].evidence_files[{file_index}]")
    for label in ("audience", "objective", "core_message"):
        required_text(brief.get(label), f"canonical-brief.{label}")
    insights = brief.get("insights")
    if not isinstance(insights, list) or not insights:
        raise ValidationError("canonical brief 至少需要一个 insight。")
    for index, insight in enumerate(insights):
        required_text(insight.get("insight") if isinstance(insight, dict) else None, f"insights[{index}].insight")
        ids = insight.get("source_ids") if isinstance(insight, dict) else None
        if not isinstance(ids, list) or not ids or not set(ids) <= set(source_map):
            raise ValidationError(f"insights[{index}].source_ids 无效。")
    boundaries = brief.get("source_boundaries")
    if not isinstance(boundaries, list) or not boundaries:
        raise ValidationError("canonical brief 缺少 source_boundaries。")
    directions = brief.get("target_directions")
    if not isinstance(directions, list):
        raise ValidationError("target_directions 必须是数组。")
    direction_platforms = [item.get("platform") for item in directions if isinstance(item, dict)]
    if set(direction_platforms) != set(targets) or len(direction_platforms) != len(targets):
        raise ValidationError("target_directions 必须与 distribution.targets 一一对应。")
    plan_scopes = set(plan["research"]["learning_scope"])
    for index, direction in enumerate(directions):
        required_text(direction.get("message_job"), f"target_directions[{index}].message_job")
        scopes = direction.get("learning_scope")
        if not isinstance(scopes, list) or not scopes or not set(scopes) <= plan_scopes:
            raise ValidationError(f"target_directions[{index}].learning_scope 超出计划。")
        reference = direction.get("primary_reference_id")
        if reference is not None and reference not in source_map:
            raise ValidationError(f"target_directions[{index}].primary_reference_id 无效。")
        target = next(item for item in plan["distribution"]["targets"] if item["platform"] == direction["platform"])
        if target["adapter_mode"] == "close-replication":
            if reference is None or source_map[reference].get("role") != "primary":
                raise ValidationError(f"target_directions[{index}] close-replication 必须绑定一个 primary reference。")
            required_scopes = {"structure", "visual", "format"}
            if not required_scopes <= set(scopes):
                raise ValidationError(f"target_directions[{index}] close-replication 必须包含 structure、visual、format。")
    return brief


def validate_packages(run_dir: Path, plan: dict[str, Any], brief: dict[str, Any], targets: list[str]) -> None:
    brief_hash = sha256_file(run_dir / "canonical-brief.json")
    target_map = {item["platform"]: item for item in plan["distribution"]["targets"]}
    copy_fingerprints: dict[str, str] = {}
    for platform in targets:
        package_dir = run_dir / "packages" / platform
        manifest = read_json(package_dir / "publish-manifest.json")
        if manifest.get("schema_version") != 1 or manifest.get("platform") != platform:
            raise ValidationError(f"{platform} package schema/platform 无效。")
        if manifest.get("canonical_brief_sha256") != brief_hash:
            raise ValidationError(f"{platform} package 的 canonical brief 哈希不匹配。")
        target = target_map[platform]
        if manifest.get("account_role") != target["account_role"]:
            raise ValidationError(f"{platform} package 的 account_role 不匹配。")
        if manifest.get("adapter_mode") != target["adapter_mode"]:
            raise ValidationError(f"{platform} package 的 adapter_mode 不匹配。")
        if target["adapter_mode"] == "close-replication" and manifest.get("replication_policy") != target.get("replication_policy"):
            raise ValidationError(f"{platform} package 没有继承 close-replication 风险确认。")
        copy_path = safe_file(package_dir, manifest.get("copy_file"), f"{platform}.copy_file")
        copy_text = copy_path.read_text(encoding="utf-8").strip()
        if not copy_text:
            raise ValidationError(f"{platform}.copy_file 不能为空。")
        copy_fingerprints[platform] = native_copy_fingerprint(copy_text)
        safe_file(package_dir, manifest.get("source_boundary_file"), f"{platform}.source_boundary_file")
        assets = manifest.get("asset_files")
        if not isinstance(assets, list):
            raise ValidationError(f"{platform}.asset_files 必须是数组。")
        for index, raw in enumerate(assets):
            safe_file(package_dir, raw, f"{platform}.asset_files[{index}]")
        if "video" in target.get("formats", ["text"]):
            video_manifest_path = safe_file(
                package_dir,
                manifest.get("video_manifest_file"),
                f"{platform}.video_manifest_file",
            )
            video_manifest = read_json(video_manifest_path)
            if video_manifest.get("status") != "rendered-not-published":
                raise ValidationError(f"{platform} video manifest 状态无效。")
            video_files = video_manifest.get("files") or {}
            safe_file(
                video_manifest_path.parent,
                video_files.get("video"),
                f"{platform}.video.files.video",
            )
        if not isinstance(manifest.get("native_constraints"), dict) or not manifest["native_constraints"]:
            raise ValidationError(f"{platform}.native_constraints 不能为空。")
        if manifest.get("content_governance") != plan.get("content_governance"):
            raise ValidationError(f"{platform} package 没有继承 content_governance。")
        publish = manifest.get("publish")
        if not isinstance(publish, dict) or publish.get("approved") is not False or publish.get("auto_publish") is not False:
            raise ValidationError(f"{platform} package 生成阶段必须保持发布关闭。")
    if len(targets) > 1:
        fingerprints = list(copy_fingerprints.values())
        if len(fingerprints) != len(set(fingerprints)):
            raise ValidationError("多平台正文去除标签后重复；必须分别生成平台原生版本。")


def validate(run_dir: Path, stage: str) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    if not run_dir.is_dir():
        raise ValidationError(f"run directory 不存在：{run_dir}")
    plan, targets, source_map = validate_plan(
        run_dir, require_governance=stage != "plan", require_evidence=stage != "plan"
    )
    brief = None
    if stage in {"generation", "packages"}:
        brief = validate_brief(run_dir, plan, targets, source_map)
    if stage == "packages":
        assert brief is not None
        validate_packages(run_dir, plan, brief, targets)
    return {"status": "valid", "stage": stage, "targets": targets, "source_count": len(source_map)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate social content orchestration")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--stage", choices=("plan", "generation", "packages"), required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.run_dir), args.stage), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        raise SystemExit(1)
