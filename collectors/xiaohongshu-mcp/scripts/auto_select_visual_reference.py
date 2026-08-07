#!/usr/bin/env python3
"""Choose one reviewed Xiaohongshu visual candidate without user interaction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


DIMENSIONS = {
    "promotional_hierarchy": 25,
    "content_visualization": 20,
    "proof_zone": 20,
    "layout_whitespace": 15,
    "mobile_readability": 10,
    "product_adaptability": 10,
}


def read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} 顶层必须是对象")
    return value


def select(candidates_path: Path, review_path: Path) -> dict[str, Any]:
    candidates = read_object(candidates_path)
    review = read_object(review_path)
    candidate_by_id = {
        str(item.get("note_id")): item
        for item in candidates.get("candidates") or []
        if isinstance(item, dict) and item.get("note_id")
    }
    reviews = review.get("items")
    if not isinstance(reviews, list) or set(candidate_by_id) != {
        str(item.get("note_id")) for item in reviews if isinstance(item, dict)
    }:
        raise ValueError("visual review 必须恰好覆盖所有候选")
    ranked: list[tuple[int, int, int, str, dict[str, Any]]] = []
    for item in reviews:
        note_id = str(item.get("note_id"))
        scores = item.get("scores")
        if not isinstance(scores, dict):
            raise ValueError(f"{note_id} 缺少 scores")
        normalized: dict[str, int] = {}
        for dimension, maximum in DIMENSIONS.items():
            value = scores.get(dimension)
            if not isinstance(value, int) or value < 0 or value > maximum:
                raise ValueError(f"{note_id}.{dimension} 必须是 0 到 {maximum} 的整数")
            normalized[dimension] = value
        total = sum(normalized.values())
        hard_reject = bool(item.get("hard_reject"))
        if hard_reject or total < 75:
            continue
        ranked.append(
            (
                total,
                normalized["product_adaptability"],
                normalized["promotional_hierarchy"],
                note_id,
                item,
            )
        )
    if not ranked:
        raise ValueError(
            "没有达到 75 分且通过硬门禁的视觉候选；请先向用户说明本批不合格判断，"
            "并询问是否提供其认为合适的小红书笔记，或授权重新查询"
        )
    ranked.sort(reverse=True)
    total, _, _, note_id, review_item = ranked[0]
    candidate = candidate_by_id[note_id]
    images = candidate.get("image_files")
    if not isinstance(images, list) or not images:
        raise ValueError("最高分候选没有可用图片")
    rejected = sorted(set(candidate_by_id) - {note_id})
    return {
        "schema_version": 1,
        "selection_mode": "autonomous-policy-approved",
        "disclosure": "internal-only-do-not-display-reference-by-default",
        "primary": {
            "note_id": note_id,
            "reference_image": images[0],
            "score": total,
            "reasons": {
                "topic_fit": str(review_item.get("topic_fit") or "符合本轮产品主题"),
                "visual_quality": str(review_item.get("visual_quality") or "通过视觉质量门禁"),
                "product_fit": str(review_item.get("product_fit") or "结构可承载真实产品证据"),
                "non_copying_boundary": str(
                    review_item.get("non_copying_boundary")
                    or "仅学习结构，替换原文、品牌、人物和来源素材"
                ),
            },
        },
        "rejected_candidate_ids": rejected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = select(args.candidates, args.review)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"output": str(args.out), "primary_note_id": result["primary"]["note_id"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
