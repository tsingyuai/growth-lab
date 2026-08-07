#!/usr/bin/env python3
"""Normalize common webmaster CSV/JSON exports without external dependencies."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any


ALIASES = {
    "query": {"query", "keyword", "search query", "搜索词", "关键词", "查询"},
    "page": {"page", "url", "landing page", "top pages", "页面", "网页"},
    "impressions": {"impressions", "impression", "展现", "展示", "曝光"},
    "clicks": {"clicks", "click", "点击", "点击次数"},
    "ctr": {"ctr", "click through rate", "click-through rate", "点击率"},
    "position": {"position", "average position", "avg position", "平均排名", "排名"},
    "date": {"date", "day", "日期", "时间"},
    "country": {"country", "国家", "地区"},
    "device": {"device", "设备"},
    "status": {"status", "index status", "coverage state", "索引状态", "收录状态", "状态"},
}

DIMENSIONS = {"query", "page", "date", "country", "device", "status"}
METRICS = {"impressions", "clicks", "ctr", "position"}


def normalized_name(value: str) -> str:
    return re.sub(r"[_\-\s]+", " ", value.strip().lower())


def build_field_map(columns: list[str]) -> tuple[dict[str, str], list[str]]:
    alias_lookup = {
        normalized_name(alias): canonical
        for canonical, aliases in ALIASES.items()
        for alias in aliases
    }
    field_map: dict[str, str] = {}
    unmapped: list[str] = []
    claimed: set[str] = set()
    for source in columns:
        canonical = alias_lookup.get(normalized_name(source))
        if canonical and canonical not in claimed:
            field_map[source] = canonical
            claimed.add(canonical)
        else:
            unmapped.append(source)
    return field_map, unmapped


def parse_number(value: Any, *, percent: bool = False) -> float | int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    else:
        text = str(value).strip().replace(",", "").replace("，", "")
        is_percent = text.endswith("%")
        if is_percent:
            text = text[:-1].strip()
        try:
            number = float(text)
        except ValueError:
            return None
        if is_percent:
            number /= 100
    if percent and number > 1:
        number /= 100
    return int(number) if number.is_integer() and not percent else number


def read_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]
    if suffix == ".json":
        with path.open("r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict):
            rows = next(
                (payload[key] for key in ("rows", "data", "results") if isinstance(payload.get(key), list)),
                None,
            )
        else:
            rows = None
        if rows is None or not all(isinstance(row, dict) for row in rows):
            raise ValueError("JSON must be an array of objects or contain a rows/data/results array")
        return [dict(row) for row in rows]
    raise ValueError("Only .csv and .json exports are supported")


def normalize_rows(rows: list[dict[str, Any]], field_map: dict[str, str]) -> tuple[list[dict[str, Any]], list[str]]:
    normalized: list[dict[str, Any]] = []
    warnings: list[str] = []
    invalid_counts = {metric: 0 for metric in METRICS}
    for row in rows:
        item: dict[str, Any] = {}
        for source, canonical in field_map.items():
            value = row.get(source)
            if canonical in METRICS:
                parsed = parse_number(value, percent=canonical == "ctr")
                if value not in (None, "") and parsed is None:
                    invalid_counts[canonical] += 1
                item[canonical] = parsed
            else:
                item[canonical] = str(value).strip() if value not in (None, "") else None
        normalized.append(item)
    for metric, count in invalid_counts.items():
        if count:
            warnings.append(f"{count} row(s) contain an invalid {metric} value")
    return normalized, warnings


def quality_checks(rows: list[dict[str, Any]], mapped: set[str]) -> list[str]:
    warnings: list[str] = []
    if not mapped & DIMENSIONS:
        warnings.append("No recognized dimension field was found")
    if not mapped & METRICS and "status" not in mapped:
        warnings.append("No recognized performance metric or index-status field was found")
    comparable = 0
    inconsistent = 0
    for row in rows:
        impressions, clicks, ctr = row.get("impressions"), row.get("clicks"), row.get("ctr")
        if isinstance(impressions, (int, float)) and impressions > 0 and isinstance(clicks, (int, float)) and isinstance(ctr, (int, float)):
            comparable += 1
            if abs(clicks / impressions - ctr) > 0.02:
                inconsistent += 1
    if inconsistent:
        warnings.append(f"CTR differs from clicks/impressions by more than 2 percentage points in {inconsistent}/{comparable} comparable row(s)")
    if not rows:
        warnings.append("The export contains no data rows")
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Source .csv or .json export")
    parser.add_argument("--out", type=Path, help="Write normalized JSON to this path; stdout if omitted")
    parser.add_argument("--source", help="Source platform, for example bing or gsc")
    parser.add_argument("--site", help="Site property represented by the export")
    parser.add_argument("--date-from", dest="date_from", help="Analysis window start (YYYY-MM-DD)")
    parser.add_argument("--date-to", dest="date_to", help="Analysis window end (YYYY-MM-DD)")
    args = parser.parse_args()

    rows = read_rows(args.input)
    columns = list(dict.fromkeys(key for row in rows for key in row.keys()))
    field_map, unmapped = build_field_map(columns)
    normalized, warnings = normalize_rows(rows, field_map)
    warnings.extend(quality_checks(normalized, set(field_map.values())))
    result = {
        "provenance": {
            "source": args.source,
            "site": args.site,
            "date_from": args.date_from,
            "date_to": args.date_to,
            "input_file": args.input.name,
        },
        "schema": {
            "field_map": field_map,
            "unmapped_fields": unmapped,
        },
        "quality": {
            "row_count": len(normalized),
            "warnings": warnings,
        },
        "rows": normalized,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
