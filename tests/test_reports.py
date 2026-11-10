import csv
import json
import tempfile
import unittest
from pathlib import Path

from change_readiness.io import write_reports


class ReportWritingTests(unittest.TestCase):
    def test_writes_review_csv_json_and_summary(self):
        results = [
            {
                "change_id": "CHG-001",
                "title": "Core network maintenance",
                "service_id": "svc-core",
                "review_status": "HUMAN_REVIEW",
                "flags": ["OVERLAPPING_CHANGE_WINDOW", "MISSING_REQUIRED_EVIDENCE"],
                "reasons": ["Missing rollback plan."],
                "related_changes": ["CHG-002"],
            },
            {
                "change_id": "CHG-002",
                "title": "Portal update",
                "service_id": "svc-portal",
                "review_status": "HUMAN_REVIEW",
                "flags": [],
                "reasons": ["No rule-based flags; human review is still required."],
                "related_changes": [],
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            summary = write_reports(results, directory)
            root = Path(directory)
            with (root / "review.csv").open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            saved_json = json.loads((root / "review.json").read_text(encoding="utf-8"))
            saved_summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual(len(rows), 2)
        self.assertIn("OVERLAPPING_CHANGE_WINDOW", rows[0]["flags"])
        self.assertEqual(saved_json, results)
        self.assertEqual(summary, saved_summary)
        self.assertEqual(summary["change_count"], 2)
        self.assertEqual(summary["changes_with_flags"], 1)
        self.assertEqual(summary["flag_counts"]["MISSING_REQUIRED_EVIDENCE"], 1)


if __name__ == "__main__":
    unittest.main()