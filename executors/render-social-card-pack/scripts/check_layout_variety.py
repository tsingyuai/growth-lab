#!/usr/bin/env python3
"""Fail a card pack when its composition fingerprints are too repetitive."""

import argparse
import json
import math
from pathlib import Path


FIELDS = ("archetype", "title_anchor", "visual_mass", "reading_path", "screenshot_geometry")
VAGUE_MOVES = ("换截图", "换颜色", "换文案", "颜色变化", "截图变化", "文案变化")


def fail(message, errors):
    errors.append(message)


def box_area(slot, scene):
    if "box_norm" in slot:
        return float(slot["box_norm"][2]) * float(slot["box_norm"][3])
    if "box" in slot:
        size = scene.get("canvas_size")
        if not size:
            return None
        return (float(slot["box"][2]) / size[0]) * (float(slot["box"][3]) / size[1])
    return None


def intersects(a, b):
    if "box_norm" not in a or "box_norm" not in b:
        return False
    ax, ay, aw, ah = map(float, a["box_norm"])
    bx, by, bw, bh = map(float, b["box_norm"])
    return min(ax + aw, bx + bw) > max(ax, bx) and min(ay + ah, by + bh) > max(ay, by)


def check_scene(card, ledger_path, errors):
    scene_ref = card.get("scene")
    if not scene_ref:
        return
    scene_path = (ledger_path.parent / scene_ref).resolve()
    if not scene_path.exists():
        fail(f"{card['page']}: scene 不存在: {scene_ref}", errors)
        return
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    slots = scene.get("slots", [])
    if not slots:
        fail(f"{card['page']}: scene 必须包含 slots", errors)
        return
    if len(slots) == 1:
        return

    areas = sorted((box_area(slot, scene) for slot in slots), reverse=True)
    areas = [value for value in areas if value is not None]
    rotations = {float(slot.get("rotation", 0)) for slot in slots}
    overlap = any(intersects(a, b) for i, a in enumerate(slots) for b in slots[i + 1 :])
    geometry = card["screenshot_geometry"]
    if geometry != "workspace-triptych" and len(areas) >= 2:
        dominant = areas[0] >= areas[1] * 1.35
        if not dominant and not overlap and len(rotations) == 1:
            fail(f"{card['page']}: 多截图仍是平均分格;需主次面积差、重叠或旋转变化", errors)


def check(ledger_path):
    data = json.loads(ledger_path.read_text(encoding="utf-8"))
    cards = data.get("cards")
    errors = []
    if not isinstance(cards, list) or not cards:
        return ["ledger 必须包含非空 cards 数组"]

    for index, card in enumerate(cards, 1):
        card.setdefault("page", f"{index:02d}")
        missing = [field for field in FIELDS + ("unique_move",) if not card.get(field)]
        if missing:
            fail(f"{card['page']}: 缺少 {', '.join(missing)}", errors)
            continue
        check_scene(card, ledger_path, errors)

    if errors:
        return errors

    count = len(cards)
    minimum_archetypes = 4 if count >= 5 else min(3, count)
    archetypes = {card["archetype"] for card in cards}
    if len(archetypes) < minimum_archetypes:
        fail(f"整组仅 {len(archetypes)} 种 archetype; {count}P 至少需要 {minimum_archetypes} 种", errors)

    for field, minimum in (("title_anchor", 2), ("visual_mass", 3), ("reading_path", 3)):
        values = {card[field] for card in cards}
        required = min(minimum, count)
        if len(values) < required:
            fail(f"{field} 仅 {len(values)} 种;至少需要 {required} 种", errors)

    max_anchor_repeat = max(2, math.ceil(count * 0.6))
    for anchor in {card["title_anchor"] for card in cards}:
        repeated = sum(card["title_anchor"] == anchor for card in cards)
        if repeated > max_anchor_repeat:
            fail(f"title_anchor={anchor} 出现 {repeated}/{count};上限 {max_anchor_repeat}", errors)

    fingerprints = [tuple(card[field] for field in FIELDS) for card in cards]
    for index, fingerprint in enumerate(fingerprints):
        if fingerprint in fingerprints[:index]:
            fail(f"{cards[index]['page']}: 与前卡版式指纹完全重复", errors)

    moves = [card["unique_move"].strip() for card in cards]
    if len(set(moves)) != len(moves):
        fail("unique_move 必须逐卡不同,不能用同一装饰动作冒充版式变化", errors)
    for card, move in zip(cards, moves):
        if any(token in move for token in VAGUE_MOVES):
            fail(f"{card['page']}: unique_move={move} 只是素材变化,必须写结构动作", errors)

    for index in range(1, count):
        same = sum(cards[index - 1][field] == cards[index][field] for field in FIELDS)
        if same >= 4:
            fail(f"{cards[index - 1]['page']}→{cards[index]['page']}: 相邻卡 {same}/5 个版式维度相同", errors)

    shot_cards = [card for card in cards if card.get("screenshot_geometry") != "none"]
    if len(shot_cards) >= 3:
        geometries = {card["screenshot_geometry"] for card in shot_cards}
        if len(geometries) < 3:
            fail(f"截图卡仅 {len(geometries)} 种 screenshot_geometry;至少需要 3 种", errors)
    return errors


def main():
    parser = argparse.ArgumentParser(description="检查整组小红书卡片的版式多样性")
    parser.add_argument("--ledger", required=True, help="版式指纹 JSON")
    args = parser.parse_args()
    ledger = Path(args.ledger).resolve()
    errors = check(ledger)
    if errors:
        print("layout variety failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("layout variety passed")


if __name__ == "__main__":
    main()
