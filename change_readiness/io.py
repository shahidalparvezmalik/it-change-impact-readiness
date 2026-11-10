"""CSV and JSON output helpers for the change-review CLI."""

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

_FIELDS = ("change_id", "title", "service_id", "review_status", "flags", "reasons", "related_changes")


def load_csv(path: str | Path, required_columns: set[str]) -> list[dict[str, str]]:
    """Read a UTF-8 CSV and reject missing required headers."""
    source = Path(path)
    with source.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        present = set(reader.fieldnames or [])
        missing = sorted(required_columns - present)
        if missing:
            raise ValueError(f"{source}: missing required columns: {', '.join(missing)}")
        return [
            {key: (value or "").strip() for key, value in row.items() if key is not None}
            for row in reader
        ]


def write_reports(results: Sequence[Mapping[str, object]], output_dir: str | Path) -> dict[str, object]:
    """Write machine-readable review reports and return their summary."""
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    normalized = [dict(result) for result in results]

    with (root / "review.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=_FIELDS)
        writer.writeheader()
        for result in normalized:
            writer.writerow({
                field: "; ".join(result.get(field, [])) if field in ("flags", "reasons", "related_changes") else result.get(field, "")
                for field in _FIELDS
            })

    (root / "review.json").write_text(
        json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    counts: Counter[str] = Counter()
    for result in normalized:
        counts.update(set(result.get("flags", [])))
    summary: dict[str, object] = {
        "change_count": len(normalized),
        "changes_with_flags": sum(bool(result.get("flags")) for result in normalized),
        "flag_counts": dict(sorted(counts.items())),
        "review_status": "HUMAN_REVIEW_ONLY",
    }
    (root / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary