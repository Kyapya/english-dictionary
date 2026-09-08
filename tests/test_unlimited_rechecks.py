import argparse
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import source_first_audit_gate as source
import entry_workflow_guard as guard
from tests.test_source_first_audit_gate import valid_v2_manifest
from tests.test_entry_workflow_guard import manifest


class UnlimitedRechecksTests(unittest.TestCase):
    def test_new_and_legacy_inventory_accept_many_rechecks_but_not_other_limits(self):
        for limit in (None, 1):
            value = valid_v2_manifest()
            gate = value["source_first_audit"]
            gate["limits"]["max_post_cold_rechecks"] = limit
            gate["usage"]["post_cold_rechecks_used"] = 100
            self.assertEqual(source.validate_manifest(value), [])
            gate["usage"]["final_attempts_used"] = 3
            self.assertTrue(any("max_final_attempts" in error for error in source.validate_manifest(value)))

    def test_record_attempt_retains_old_limit_and_increments_beyond_it(self):
        value = valid_v2_manifest()
        gate = value["source_first_audit"]
        gate["limits"]["max_post_cold_rechecks"] = 1
        gate["usage"]["post_cold_rechecks_used"] = 2
        with patch.object(source, "_load_entry", return_value=(Path("unused"), value)), patch.object(source, "_write"):
            self.assertEqual(source.command_record_attempt(argparse.Namespace(entry="unused", stage="post-cold")), 0)
        self.assertEqual(gate["usage"]["post_cold_rechecks_used"], 3)
        self.assertEqual(gate["limits"]["max_post_cold_rechecks"], 1)

    def test_exact_stop_recovery_preserves_unresolved_questions_and_counters(self):
        value = manifest()
        value.update(status="budget_exhausted", stop_reason="Source-first standard post-cold recheck limit reached (1/1); accepted corrections still require verification", open_questions=["Verify adopted corrections"])
        original = copy.deepcopy(value)
        self.assertTrue(guard.resume_legacy_recheck_stop(value))
        for key in original.keys() - {"status", "stop_reason"}:
            self.assertEqual(value[key], original[key])
        self.assertFalse(guard.resume_legacy_recheck_stop(value))
        for reason in ("research query budget exhausted", "final budget exhausted", "unknown recheck limit"):
            value.update(status="budget_exhausted", stop_reason=reason)
            self.assertFalse(guard.resume_legacy_recheck_stop(value))

    def test_inventory_recovery_keeps_pending_content_issues(self):
        value = valid_v2_manifest()
        gate = value["source_first_audit"]
        gate.update(research_status="budget_exhausted", stop_reason="post-cold recheck limit reached with adopted corrections awaiting verification", open_questions=["Verify translation"])
        usage = copy.deepcopy(gate["usage"])
        self.assertTrue(source.resume_legacy_recheck_stop(value))
        self.assertEqual(gate["usage"], usage)
        self.assertEqual(gate["open_questions"], ["Verify translation"])
        self.assertEqual(source.validate_manifest(value), [])


if __name__ == "__main__":
    unittest.main()
