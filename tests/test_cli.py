import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from change_readiness.cli import main


class CliTests(unittest.TestCase):
    def test_cli_reads_three_inputs_and_writes_review_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "changes.csv").write_text(
                "change_id,title,service_id,planned_start_utc,planned_end_utc,owner,implementation_plan,test_evidence,rollback_plan,approver\n"
                "CHG-001,Demo change,svc-demo,2026-12-20T22:00:00Z,2026-12-20T23:00:00Z,Owner,Plan,Test,Rollback,Approver\n",
                encoding="utf-8",
            )
            (root / "dependencies.csv").write_text(
                "service_id,dependency_id,verification_status\nsvc-demo,dep-demo,confirmed\n",
                encoding="utf-8",
            )
            (root / "blackouts.csv").write_text(
                "scope_type,scope_id,start_utc,end_utc,reason\nservice,svc-demo,2026-12-20T22:30:00Z,2026-12-20T23:30:00Z,freeze\n",
                encoding="utf-8",
            )
            output = root / "reports"
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main([
                    "--changes", str(root / "changes.csv"),
                    "--dependencies", str(root / "dependencies.csv"),
                    "--blackouts", str(root / "blackouts.csv"),
                    "--output-dir", str(output),
                ])

            summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(summary["change_count"], 1)
        self.assertEqual(summary["flag_counts"]["BLACKOUT_WINDOW_CONFLICT"], 1)
        self.assertIn("human review", stdout.getvalue().lower())


if __name__ == "__main__":
    unittest.main()