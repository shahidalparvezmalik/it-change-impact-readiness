# Operating model and limitations

## Demonstration workflow

1. Treat each input file as a dated, fictional snapshot; check source, owner, freshness, and join keys before relying on it.
2. Run the CLI locally against the three CSV files. No credentials, external network access, or third-party packages are required.
3. Review each flag and explanation with the service owner. Confirm dependency relationships and schedule constraints in authoritative systems.
4. Route any genuine decision through the organisation's established change authority and approval process. The output is not an approval record.
5. Keep the evidence, owner decision, and final schedule in the organization's approved system—not in this sample repository.

## Operational safeguards

- Every result requires human review, even when no flags are raised.
- The CLI does not mutate the inputs or call an external system.
- Shared-dependency overlaps use only links marked `confirmed`; unconfirmed links raise a separate flag and are not treated as known conflicts.
- Fixed sample windows and IDs are synthetic. They do not describe an actual organization, supplier, maintenance window, or service.
- Rule thresholds and data completeness checks are illustrative, not validated as a control, risk model, or service-management standard.

## Explicit non-goals

This is not a complete change-management system. It does not create RFCs, classify standard/normal/emergency changes, calculate business impact, assign risk, decide approval routes, convene a CAB, check live change calendars, discover service dependencies, estimate outage probability, execute implementation/rollback, notify stakeholders, or claim compliance. It is not a substitute for ITSM, CMDB, monitoring, or change-authority records.
