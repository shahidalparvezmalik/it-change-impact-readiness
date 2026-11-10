"""Deterministic checks for proposed changes; results never authorize work."""

from datetime import datetime, timezone
from typing import Iterable, Mapping


def _timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def evaluate_changes(
    changes: Iterable[Mapping[str, str]],
    dependencies: Iterable[Mapping[str, str]],
    blackout_windows: Iterable[Mapping[str, str]],
) -> list[dict[str, object]]:
    """Flag overlapping windows on one service or a confirmed shared dependency."""
    rows = [dict(row) for row in changes]
    blackout_rows = [dict(row) for row in blackout_windows]
    ids = [str(row.get("change_id", "")).strip() for row in rows]
    if any(not change_id for change_id in ids):
        raise ValueError("Every change must have a change_id")
    if len(ids) != len(set(ids)):
        raise ValueError("change_id values must be unique")
    links: dict[str, set[str]] = {}
    unconfirmed_services: set[str] = set()
    for link in dependencies:
        service_id = str(link.get("service_id", ""))
        status = str(link.get("verification_status", "")).lower()
        if status == "confirmed":
            links.setdefault(service_id, set()).add(str(link.get("dependency_id", "")))
        elif service_id:
            unconfirmed_services.add(service_id)

    windows = []
    for row in rows:
        start = _timestamp(row["planned_start_utc"])
        end = _timestamp(row["planned_end_utc"])
        if end <= start:
            raise ValueError(f"{row['change_id']}: end must be later than start")
        windows.append((start, end))

    flags = [set() for _ in rows]
    reasons = [set() for _ in rows]
    related = [set() for _ in rows]
    required_evidence = ("owner", "implementation_plan", "test_evidence", "rollback_plan", "approver")
    for index, row in enumerate(rows):
        missing = [field for field in required_evidence if not str(row.get(field, "")).strip()]
        if missing:
            flags[index].add("MISSING_REQUIRED_EVIDENCE")
            reasons[index].update(f"Missing required evidence: {field}." for field in missing)
        service_id = str(row.get("service_id", "")).strip()
        if not service_id:
            flags[index].add("MISSING_SERVICE_ID")
            reasons[index].add("Missing required service_id for impact review.")
        elif service_id in unconfirmed_services:
            flags[index].add("UNCONFIRMED_DEPENDENCY")
            reasons[index].add("At least one dependency record for this service is not confirmed.")
        if service_id and service_id not in links:
            flags[index].add("SERVICE_DEPENDENCIES_UNMAPPED")
            reasons[index].add("No confirmed dependency mapping is available for this service.")

    for left in range(len(rows)):
        for right in range(left + 1, len(rows)):
            a, b = rows[left], rows[right]
            shared = links.get(a["service_id"], set()) & links.get(b["service_id"], set())
            same_service = bool(str(a.get("service_id", "")).strip()) and str(a.get("service_id", "")).strip() == str(b.get("service_id", "")).strip()
            overlap = windows[left][0] < windows[right][1] and windows[right][0] < windows[left][1]
            if overlap and (same_service or shared):
                scope = f"service {a['service_id']}" if same_service else "shared dependency " + ", ".join(sorted(shared))
                for index, other in ((left, b["change_id"]), (right, a["change_id"])):
                    flags[index].add("OVERLAPPING_CHANGE_WINDOW")
                    reasons[index].add(f"Overlapping planned window with {other} on {scope}.")
                    related[index].add(other)

    for index, row in enumerate(rows):
        service_id = row["service_id"]
        resources = {("service", service_id)}
        resources.update(("dependency", dependency_id) for dependency_id in links.get(service_id, set()))
        for blackout in blackout_rows:
            scope = (str(blackout.get("scope_type", "")).lower(), str(blackout.get("scope_id", "")))
            if scope not in resources:
                continue
            blackout_start = _timestamp(blackout["start_utc"])
            blackout_end = _timestamp(blackout["end_utc"])
            if blackout_end <= blackout_start:
                raise ValueError(f"invalid blackout window for {row['change_id']}")
            if windows[index][0] < blackout_end and blackout_start < windows[index][1]:
                label = str(blackout.get("reason", "")).strip() or "unnamed blackout"
                flags[index].add("BLACKOUT_WINDOW_CONFLICT")
                reasons[index].add(f"Planned window intersects blackout: {label} ({scope[0]} {scope[1]}).")

    return [
        {
            "change_id": row["change_id"],
            "title": row.get("title", ""),
            "service_id": row["service_id"],
            "review_status": "HUMAN_REVIEW",
            "flags": sorted(flags[index]),
            "reasons": sorted(reasons[index]) or ["No overlap flag; human review is still required."],
            "related_changes": sorted(related[index]),
        }
        for index, row in enumerate(rows)
    ]
