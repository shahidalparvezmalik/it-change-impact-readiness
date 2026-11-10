import unittest

from change_readiness.assessment import evaluate_changes


class ChangeAssessmentTests(unittest.TestCase):
    def test_duplicate_change_ids_are_rejected(self):
        change = {
            "change_id": "CHG-DUP",
            "title": "Example",
            "service_id": "svc-demo",
            "planned_start_utc": "2026-12-17T22:00:00Z",
            "planned_end_utc": "2026-12-17T23:00:00Z",
        }

        with self.assertRaisesRegex(ValueError, "change_id values must be unique"):
            evaluate_changes([change, change], [], [])

    def test_missing_service_id_is_flagged_and_does_not_create_false_conflict(self):
        changes = [
            {"change_id": "CHG-010", "title": "First", "service_id": "", "planned_start_utc": "2026-12-21T22:00:00Z", "planned_end_utc": "2026-12-21T23:00:00Z"},
            {"change_id": "CHG-011", "title": "Second", "service_id": "", "planned_start_utc": "2026-12-21T22:15:00Z", "planned_end_utc": "2026-12-21T23:15:00Z"},
        ]

        results = evaluate_changes(changes, [], [])

        for result in results:
            self.assertIn("MISSING_SERVICE_ID", result["flags"])
            self.assertNotIn("OVERLAPPING_CHANGE_WINDOW", result["flags"])

    def test_unconfirmed_dependency_is_reported_without_being_used_for_conflicts(self):
        change = {
            "change_id": "CHG-005",
            "title": "Finance service update",
            "service_id": "svc-finance",
            "planned_start_utc": "2026-12-16T01:00:00Z",
            "planned_end_utc": "2026-12-16T02:00:00Z",
            "owner": "Ops E",
            "implementation_plan": "Update service",
            "test_evidence": "Test run",
            "rollback_plan": "Restore snapshot",
            "approver": "Manager E",
        }
        results = evaluate_changes(
            [change],
            [{"service_id": "svc-finance", "dependency_id": "dep-unverified", "verification_status": "unconfirmed"}],
            [],
        )

        self.assertIn("UNCONFIRMED_DEPENDENCY", results[0]["flags"])
        self.assertIn("SERVICE_DEPENDENCIES_UNMAPPED", results[0]["flags"])
        self.assertFalse(results[0]["related_changes"])

    def test_dependency_blackout_window_is_flagged(self):
        change = {
            "change_id": "CHG-004",
            "title": "Application configuration update",
            "service_id": "svc-app",
            "planned_start_utc": "2026-12-15T22:00:00Z",
            "planned_end_utc": "2026-12-15T23:00:00Z",
            "owner": "Ops D",
            "implementation_plan": "Apply config",
            "test_evidence": "Test record",
            "rollback_plan": "Restore previous config",
            "approver": "Manager D",
        }
        results = evaluate_changes(
            [change],
            [{"service_id": "svc-app", "dependency_id": "dep-edge", "verification_status": "confirmed"}],
            [{
                "scope_type": "dependency",
                "scope_id": "dep-edge",
                "start_utc": "2026-12-15T22:30:00Z",
                "end_utc": "2026-12-15T22:45:00Z",
                "reason": "network freeze",
            }],
        )

        self.assertIn("BLACKOUT_WINDOW_CONFLICT", results[0]["flags"])
        self.assertTrue(any("network freeze" in reason for reason in results[0]["reasons"]))

    def test_missing_rollback_and_test_evidence_are_flagged(self):
        change = {
            "change_id": "CHG-003",
            "title": "Payroll service restart",
            "service_id": "svc-payroll",
            "planned_start_utc": "2026-12-14T22:00:00Z",
            "planned_end_utc": "2026-12-14T23:00:00Z",
            "owner": "Ops C",
            "implementation_plan": "Restart plan",
            "test_evidence": "",
            "rollback_plan": "",
            "approver": "Manager C",
        }
        results = evaluate_changes(
            [change],
            [{"service_id": "svc-payroll", "dependency_id": "dep-payroll", "verification_status": "confirmed"}],
            [],
        )

        self.assertIn("MISSING_REQUIRED_EVIDENCE", results[0]["flags"])
        self.assertTrue(any("test_evidence" in reason for reason in results[0]["reasons"]))
        self.assertTrue(any("rollback_plan" in reason for reason in results[0]["reasons"]))

    def test_overlapping_changes_on_a_shared_dependency_are_flagged(self):
        changes = [
            {
                "change_id": "CHG-001",
                "title": "Payments database maintenance",
                "service_id": "svc-payments",
                "planned_start_utc": "2026-12-12T22:00:00Z",
                "planned_end_utc": "2026-12-12T23:00:00Z",
                "owner": "Ops A",
                "implementation_plan": "Plan A",
                "test_evidence": "Test A",
                "rollback_plan": "Backout A",
                "approver": "Manager A",
            },
            {
                "change_id": "CHG-002",
                "title": "Portal gateway update",
                "service_id": "svc-portal",
                "planned_start_utc": "2026-12-12T22:30:00Z",
                "planned_end_utc": "2026-12-12T23:30:00Z",
                "owner": "Ops B",
                "implementation_plan": "Plan B",
                "test_evidence": "Test B",
                "rollback_plan": "Backout B",
                "approver": "Manager B",
            },
        ]
        dependencies = [
            {"service_id": "svc-payments", "dependency_id": "dep-core-net", "verification_status": "confirmed"},
            {"service_id": "svc-portal", "dependency_id": "dep-core-net", "verification_status": "confirmed"},
        ]

        results = evaluate_changes(changes, dependencies, [])

        self.assertEqual(results[0]["review_status"], "HUMAN_REVIEW")
        self.assertIn("OVERLAPPING_CHANGE_WINDOW", results[0]["flags"])
        self.assertEqual(results[0]["related_changes"], ["CHG-002"])
        self.assertIn("OVERLAPPING_CHANGE_WINDOW", results[1]["flags"])


if __name__ == "__main__":
    unittest.main()