#!/usr/bin/env python3
"""Normalize product event exports into privacy-preserving aggregates."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


FIELD_ALIASES = {
    "event": ("event_name", "event", "name", "action"),
    "user": ("user_id", "userId", "distinct_id", "distinctId", "anonymous_id", "anonymousId"),
    "timestamp": ("timestamp", "time", "occurred_at", "created_at", "datetime"),
}


def read_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".csv":
        return [dict(row) for row in csv.DictReader(text.splitlines())]

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        records = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"line {line_number} is not a JSON object")
            records.append(value)
        return records

    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        records = None
        for key in ("events", "data", "results"):
            if isinstance(payload.get(key), list):
                records = payload[key]
                break
        if records is None:
            records = [payload]
    else:
        raise ValueError("JSON input must be an object, an array, or newline-delimited objects")

    if not all(isinstance(record, dict) for record in records):
        raise ValueError("every event record must be an object")
    return records


def get_value(record: dict[str, Any], field: str) -> Any:
    value: Any = record
    for part in field.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def available_fields(records: Iterable[dict[str, Any]]) -> set[str]:
    fields: set[str] = set()
    for record in list(records)[:100]:
        fields.update(record.keys())
    return fields


def resolve_field(records: list[dict[str, Any]], kind: str, explicit: str | None) -> str:
    if explicit:
        if not any(get_value(record, explicit) is not None for record in records[:100]):
            raise ValueError(f"field '{explicit}' was not found in the sampled records")
        return explicit

    fields = available_fields(records)
    matches = [alias for alias in FIELD_ALIASES[kind] if alias in fields]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ValueError(f"could not find a {kind} field; pass --{kind}-field explicitly")
    raise ValueError(
        f"multiple possible {kind} fields found ({', '.join(matches)}); "
        f"pass --{kind}-field explicitly"
    )


def parse_timestamp(value: Any) -> datetime:
    if isinstance(value, bool) or value is None:
        raise ValueError("missing timestamp")
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.strip().replace(".", "", 1).isdigit()):
        numeric = float(value)
        if numeric > 10_000_000_000:
            numeric /= 1000
        return datetime.fromtimestamp(numeric, tz=timezone.utc)

    raw = str(value).strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError("timestamp is not ISO-8601 or Unix time") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_boundary(value: str | None) -> datetime | None:
    return parse_timestamp(value) if value else None


def ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def ordered_funnel(events_by_user: dict[str, list[tuple[datetime, str]]], steps: list[str]) -> dict[str, Any] | None:
    if not steps:
        return None

    reached: list[set[str]] = [set() for _ in steps]
    elapsed_seconds: list[float] = []

    for user_id, events in events_by_user.items():
        ordered = sorted(events, key=lambda item: item[0])
        step_index = 0
        first_time: datetime | None = None
        for occurred_at, event_name in ordered:
            if event_name != steps[step_index]:
                continue
            reached[step_index].add(user_id)
            if step_index == 0:
                first_time = occurred_at
            if step_index == len(steps) - 1:
                if first_time is not None:
                    elapsed_seconds.append((occurred_at - first_time).total_seconds())
                break
            step_index += 1

    entry_count = len(reached[0])
    step_results = []
    for index, step in enumerate(steps):
        count = len(reached[index])
        previous = len(reached[index - 1]) if index else count
        step_results.append(
            {
                "step": step,
                "entities": count,
                "conversion_from_previous": ratio(count, previous),
                "conversion_from_entry": ratio(count, entry_count),
            }
        )

    return {
        "entity": "mapped user field",
        "ordered": True,
        "steps": step_results,
        "completed_entities": len(reached[-1]),
        "median_seconds_to_final_step": (
            round(statistics.median(elapsed_seconds), 3) if elapsed_seconds else None
        ),
    }


def analyze_records(
    records: list[dict[str, Any]],
    *,
    event_field: str,
    user_field: str,
    timestamp_field: str,
    steps: list[str] | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
) -> dict[str, Any]:
    counters = Counter()
    event_counts: Counter[str] = Counter()
    events_by_user: dict[str, list[tuple[datetime, str]]] = defaultdict(list)
    seen: set[str] = set()

    for record in records:
        counters["input_rows"] += 1
        raw_event = get_value(record, event_field)
        raw_user = get_value(record, user_field)
        raw_timestamp = get_value(record, timestamp_field)
        if raw_event is None or str(raw_event).strip() == "":
            counters["missing_event"] += 1
            continue
        if raw_user is None or str(raw_user).strip() == "":
            counters["missing_user"] += 1
            continue
        try:
            occurred_at = parse_timestamp(raw_timestamp)
        except (ValueError, OverflowError, OSError):
            counters["invalid_timestamp"] += 1
            continue
        if start and occurred_at < start:
            counters["outside_window"] += 1
            continue
        if end and occurred_at > end:
            counters["outside_window"] += 1
            continue

        event_name = str(raw_event).strip()
        user_id = str(raw_user).strip()
        fingerprint = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str)
        if fingerprint in seen:
            counters["duplicate_rows"] += 1
            continue
        seen.add(fingerprint)
        counters["usable_rows"] += 1
        event_counts[event_name] += 1
        events_by_user[user_id].append((occurred_at, event_name))

    requested_steps = steps or []
    return {
        "schema_version": 1,
        "privacy": "aggregate output; raw identifiers and rows omitted",
        "field_mapping": {
            "event": event_field,
            "user": user_field,
            "timestamp": timestamp_field,
        },
        "window_utc": {
            "start": start.isoformat() if start else None,
            "end": end.isoformat() if end else None,
        },
        "quality": {
            "input_rows": counters["input_rows"],
            "usable_rows": counters["usable_rows"],
            "unique_entities": len(events_by_user),
            "missing_event": counters["missing_event"],
            "missing_user": counters["missing_user"],
            "invalid_timestamp": counters["invalid_timestamp"],
            "duplicate_rows": counters["duplicate_rows"],
            "outside_window": counters["outside_window"],
        },
        "event_totals": dict(sorted(event_counts.items())),
        "funnel": ordered_funnel(events_by_user, requested_steps),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize CSV/JSON/NDJSON product events into aggregate quality and funnel evidence."
    )
    parser.add_argument("input", type=Path, help="Path to an authorized event export")
    parser.add_argument("--step", action="append", default=[], help="Ordered funnel step; repeat for each step")
    parser.add_argument("--event-field", help="Event-name field, including dotted nested paths")
    parser.add_argument("--user-field", help="User or account identity field")
    parser.add_argument("--timestamp-field", help="Event timestamp field")
    parser.add_argument("--start", help="Inclusive UTC window start (ISO-8601 or Unix time)")
    parser.add_argument("--end", help="Inclusive UTC window end (ISO-8601 or Unix time)")
    parser.add_argument("--out", type=Path, help="Optional aggregate JSON output path")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        records = read_records(args.input)
        if not records:
            raise ValueError("the export contains no event records")
        if args.step and len(args.step) < 2:
            raise ValueError("provide at least two --step values for a funnel")
        if len(set(args.step)) != len(args.step):
            raise ValueError("funnel step names must be unique")

        event_field = resolve_field(records, "event", args.event_field)
        user_field = resolve_field(records, "user", args.user_field)
        timestamp_field = resolve_field(records, "timestamp", args.timestamp_field)
        result = analyze_records(
            records,
            event_field=event_field,
            user_field=user_field,
            timestamp_field=timestamp_field,
            steps=args.step,
            start=parse_boundary(args.start),
            end=parse_boundary(args.end),
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    output = json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2)
    try:
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"error: could not write aggregate output: {exc}", file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
