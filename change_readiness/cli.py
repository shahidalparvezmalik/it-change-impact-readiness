"""Command-line entry point for the offline change review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .assessment import evaluate_changes
from .io import load_csv, write_reports

_CHANGE_COLUMNS = {
    "change_id", "title", "service_id", "planned_start_utc", "planned_end_utc",
    "owner", "implementation_plan", "test_evidence", "rollback_plan", "approver",
}
_DEPENDENCY_COLUMNS = {"service_id", "dependency_id", "verification_status"}
_BLACKOUT_COLUMNS = {"scope_type", "scope_id", "start_utc", "end_utc", "reason"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review synthetic IT change requests; no approvals or actions are made.")
    parser.add_argument("--changes", required=True, help="CSV of proposed change requests")
    parser.add_argument("--dependencies", required=True, help="CSV mapping services to verified dependencies")
    parser.add_argument("--blackouts", required=True, help="CSV of service/dependency blackout windows")
    parser.add_argument("--output-dir", required=True, help="Directory for review.csv, review.json and summary.json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        changes = load_csv(args.changes, _CHANGE_COLUMNS)
        dependencies = load_csv(args.dependencies, _DEPENDENCY_COLUMNS)
        blackouts = load_csv(args.blackouts, _BLACKOUT_COLUMNS)
        results = evaluate_changes(changes, dependencies, blackouts)
        summary = write_reports(results, args.output_dir)
    except (OSError, ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(
        f"Reviewed {summary['change_count']} change(s); "
        f"{summary['changes_with_flags']} change(s) flagged; "
        f"every result requires human review. Reports: {Path(args.output_dir)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())