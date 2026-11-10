import tempfile
import unittest
from pathlib import Path

from change_readiness.io import load_csv


class CsvLoadingTests(unittest.TestCase):
    def test_loads_rows_after_validating_required_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "changes.csv"
            path.write_text("change_id,service_id\nCHG-001,svc-a\n", encoding="utf-8")

            rows = load_csv(path, {"change_id", "service_id"})

        self.assertEqual(rows, [{"change_id": "CHG-001", "service_id": "svc-a"}])

    def test_rejects_missing_required_headers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "changes.csv"
            path.write_text("change_id\nCHG-001\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing required columns: service_id"):
                load_csv(path, {"change_id", "service_id"})


if __name__ == "__main__":
    unittest.main()