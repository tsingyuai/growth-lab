import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from normalize_product_events import analyze_records, read_records, resolve_field


class NormalizeProductEventsTests(unittest.TestCase):
    def test_ordered_funnel_requires_prerequisites(self):
        records = [
            {"event_name": "signup", "user_id": "u1", "timestamp": "2026-01-01T00:00:00Z"},
            {"event_name": "workspace", "user_id": "u1", "timestamp": "2026-01-01T00:01:00Z"},
            {"event_name": "output", "user_id": "u1", "timestamp": "2026-01-01T00:03:00Z"},
            {"event_name": "signup", "user_id": "u2", "timestamp": "2026-01-01T00:00:00Z"},
            {"event_name": "output", "user_id": "u2", "timestamp": "2026-01-01T00:02:00Z"},
        ]
        result = analyze_records(
            records,
            event_field="event_name",
            user_field="user_id",
            timestamp_field="timestamp",
            steps=["signup", "workspace", "output"],
        )
        self.assertEqual([step["entities"] for step in result["funnel"]["steps"]], [2, 1, 1])
        self.assertEqual(result["funnel"]["median_seconds_to_final_step"], 180.0)

    def test_out_of_order_step_does_not_complete(self):
        records = [
            {"event": "workspace", "distinct_id": "u1", "time": "2026-01-01T00:00:00Z"},
            {"event": "signup", "distinct_id": "u1", "time": "2026-01-01T00:01:00Z"},
            {"event": "output", "distinct_id": "u1", "time": "2026-01-01T00:02:00Z"},
        ]
        result = analyze_records(
            records,
            event_field="event",
            user_field="distinct_id",
            timestamp_field="time",
            steps=["signup", "workspace", "output"],
        )
        self.assertEqual([step["entities"] for step in result["funnel"]["steps"]], [1, 0, 0])

    def test_quality_counts_duplicates_and_invalid_rows(self):
        valid = {"event": "signup", "user_id": "secret-user", "timestamp": 1_767_225_600}
        records = [valid, dict(valid), {"event": "signup", "user_id": "", "timestamp": 1_767_225_600}]
        result = analyze_records(
            records,
            event_field="event",
            user_field="user_id",
            timestamp_field="timestamp",
        )
        self.assertEqual(result["quality"]["usable_rows"], 1)
        self.assertEqual(result["quality"]["duplicate_rows"], 1)
        self.assertEqual(result["quality"]["missing_user"], 1)
        self.assertNotIn("secret-user", json.dumps(result))

    def test_same_event_time_with_different_properties_is_not_deduplicated(self):
        records = [
            {"event": "action", "user_id": "u1", "timestamp": 1_767_225_600, "properties": {"kind": "a"}},
            {"event": "action", "user_id": "u1", "timestamp": 1_767_225_600, "properties": {"kind": "b"}},
        ]
        result = analyze_records(
            records,
            event_field="event",
            user_field="user_id",
            timestamp_field="timestamp",
        )
        self.assertEqual(result["quality"]["usable_rows"], 2)
        self.assertEqual(result["quality"]["duplicate_rows"], 0)

    def test_window_is_inclusive(self):
        records = [
            {"event": "a", "user_id": "u1", "timestamp": "2026-01-01T00:00:00Z"},
            {"event": "b", "user_id": "u1", "timestamp": "2026-01-02T00:00:00Z"},
        ]
        boundary = datetime(2026, 1, 1, tzinfo=timezone.utc)
        result = analyze_records(
            records,
            event_field="event",
            user_field="user_id",
            timestamp_field="timestamp",
            start=boundary,
            end=boundary,
        )
        self.assertEqual(result["quality"]["usable_rows"], 1)
        self.assertEqual(result["quality"]["outside_window"], 1)

    def test_reads_csv_and_resolves_common_aliases(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            path.write_text(
                "event_name,user_id,timestamp\nsignup,u1,2026-01-01T00:00:00Z\n",
                encoding="utf-8",
            )
            records = read_records(path)
        self.assertEqual(resolve_field(records, "event", None), "event_name")
        self.assertEqual(resolve_field(records, "user", None), "user_id")
        self.assertEqual(resolve_field(records, "timestamp", None), "timestamp")


if __name__ == "__main__":
    unittest.main()
