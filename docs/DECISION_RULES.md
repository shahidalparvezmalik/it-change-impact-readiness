# Decision rules

This prototype intentionally uses discrete flags rather than a numerical risk score. The rules are deterministic, visible, and suitable only for demonstrating a human-review workflow on fictional data.

| Rule | Trigger | Output |
|---|---|---|
| Required evidence | Any of `owner`, `implementation_plan`, `test_evidence`, `rollback_plan`, or `approver` is blank | `MISSING_REQUIRED_EVIDENCE` plus the missing field names |
| Service context | `service_id` is blank | `MISSING_SERVICE_ID` |
| Dependency coverage | A nonblank service has no confirmed dependency rows | `SERVICE_DEPENDENCIES_UNMAPPED` |
| Dependency verification | A service has one or more dependency rows not marked `confirmed` | `UNCONFIRMED_DEPENDENCY` |
| Window collision | Two proposed windows overlap and affect the same nonblank service or share at least one confirmed dependency | `OVERLAPPING_CHANGE_WINDOW`, the other change ID, and the matching scope |
| Blackout intersection | A change window intersects a blackout for its service or a confirmed dependency | `BLACKOUT_WINDOW_CONFLICT` and the blackout label/scope |
| Human accountability | Always | `review_status=HUMAN_REVIEW` |

## Time semantics

- Inputs are ISO-8601 timestamps with a UTC offset, such as `2026-12-12T22:00:00Z`.
- Intervals are half-open: `[start, end)`. Two windows that only touch at an endpoint are not overlapping.
- End must be later than start. Invalid timestamps or intervals stop the run with an error instead of silently producing a report.
- The prototype normalizes offsets to UTC for comparison.

## What the rules do not mean

A flag is not a risk rating, rejection, approval, or policy decision. A missing flag is not proof that a change is safe. The rule set does not model business criticality, change type, rollback feasibility, risk appetite, CAB policy, maintenance capacity, or actual dependency discovery. Local change authorities must define and validate their own process.
