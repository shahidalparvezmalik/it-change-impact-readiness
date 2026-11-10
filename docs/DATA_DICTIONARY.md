# Data dictionary

All bundled records are fictional. Replace them only with approved, sanitized exports if adapting the code; do not place production or personal data in this public repository.

## `data/change_requests.csv`

| Column | Meaning |
|---|---|
| `change_id` | Unique identifier for a proposed change |
| `title` | Short descriptive label |
| `service_id` | Service identifier used to join to dependency and blackout records |
| `planned_start_utc`, `planned_end_utc` | Proposed time interval in ISO-8601 with UTC offset |
| `owner` | Named fictional accountable owner |
| `implementation_plan` | Short summary/reference for the implementation approach |
| `test_evidence` | Short summary/reference for validation evidence |
| `rollback_plan` | Short summary/reference for backout planning |
| `approver` | Fictional approver/authority reference; the tool does not contact or consult them |

The five evidence columns are required as CSV headers. Blank values are permitted and become review flags.

## `data/service_dependencies.csv`

| Column | Meaning |
|---|---|
| `service_id` | Service identifier matching a change request |
| `dependency_id` | Stable fictional dependency key used for joins |
| `dependency_name` | Human-readable fictional label |
| `verification_status` | Only `confirmed` links are used in shared-dependency collision checks; any other value is surfaced as unconfirmed |

## `data/blackout_windows.csv`

| Column | Meaning |
|---|---|
| `scope_type` | `service` or `dependency` |
| `scope_id` | Matching service or dependency identifier |
| `start_utc`, `end_utc` | Blackout interval in ISO-8601 with UTC offset |
| `reason` | Fictional explanation shown in the review reason |

A blackout is a supplied planning record, not proof of a published or authoritative freeze.

## Outputs

- `review.csv`: one row per change, with semicolon-separated flags, explanations, and related change IDs.
- `review.json`: the same findings in structured form.
- `summary.json`: total changes, flagged changes, counts by flag, and the constant `HUMAN_REVIEW_ONLY` status.
