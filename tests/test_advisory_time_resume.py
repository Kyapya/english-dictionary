from __future__ import annotations

import copy
import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import entry_workflow_guard as guard
import run_word_v3
import start_word
import workflow_revision as revision
from tests.test_entry_workflow_guard import START, confirm_without_git, manifest


class AdvisoryTimeTests(unittest.TestCase):
    def test_every_nonterminal_stage_can_cross_time_targets(self):
        for stage in guard.STAGES[:-1]:
            with self.subTest(stage=stage):
                value = manifest()
                value["stage"] = stage
                original = copy.deepcopy(value)
                self.assertTrue(guard.enforce_budget(value, now=START + timedelta(days=30)))
                self.assertEqual(value["status"], "in_progress")
                self.assertIn("elapsed_target_exceeded", value["time_warnings"])
                # Observation is not heartbeat progress or a deadline reset.
                for key in original:
                    self.assertEqual(value[key], original[key], key)
                warnings = copy.deepcopy(value["time_warnings"])
                guard.enforce_budget(value, now=START + timedelta(days=31))
                self.assertEqual(value["time_warnings"], warnings)

    def test_late_remote_confirmation_then_draft_and_next_stage(self):
        value = manifest()
        confirm_without_git(value, at=START + timedelta(days=1))
        self.assertTrue(guard.advance_stage(value, stage="draft_saved", now=START + timedelta(days=1)))
        self.assertTrue(guard.advance_stage(value, stage="source_inventory_complete", now=START + timedelta(days=2)))
        self.assertEqual(guard.validate_manifest(value), [])
        self.assertTrue(guard.validate_manifest(value, merge_ready=True))

    def stopped(self, reason):
        value = manifest()
        confirm_without_git(value)
        value["status"] = "budget_exhausted"
        value["stop_reason"] = reason
        value["open_questions"] = ["check the preserved evidence before proceeding"]
        value["review_ingest_failures"] = {"stage": "cold_review", "count": 1,
            "last_error": "old error", "last_failed_at": "2026-08-24T00:01:00Z"}
        value["saved_results"] = {"checker_sha256": "a" * 64, "snapshot": "do not regenerate"}
        return value

    def test_legacy_clock_stop_resumes_once_without_resetting_any_progress(self):
        for reason in guard.LEGACY_TIME_STOP_REASONS:
            with self.subTest(reason=reason):
                value = self.stopped(reason)
                value.pop("time_policy")  # historical manifests predate advisory_v1
                original = copy.deepcopy(value)
                self.assertTrue(guard.resume_legacy_time_stop(value, now=START + timedelta(days=1)))
                for key in original.keys() - {"status", "stop_reason"}:
                    self.assertEqual(value[key], original[key], key)
                self.assertEqual(value["status"], "in_progress")
                self.assertEqual(value["time_stop_recoveries"][0]["previous_stop_reason"], reason)
                self.assertEqual(guard.validate_manifest(value), [])
                self.assertFalse(guard.resume_legacy_time_stop(value, now=START + timedelta(days=2)))
                self.assertEqual(len(value["time_stop_recoveries"]), 1)

    def test_non_time_and_invalid_stops_are_never_automatically_unblocked(self):
        for reason in ("research query budget exhausted", "candidate page budget exhausted",
                       "post-cold recheck budget exhausted", "cold_review handoff ingestion failed 3 times", ""):
            with self.subTest(reason=reason):
                value = self.stopped(reason)
                original = copy.deepcopy(value)
                self.assertFalse(guard.resume_legacy_time_stop(value))
                self.assertEqual(value, original)
        value = self.stopped("overall elapsed-time budget exhausted")
        value["review_ingest_failures"]["count"] = 3
        self.assertFalse(guard.resume_legacy_time_stop(value))
        value = self.stopped("overall elapsed-time budget exhausted")
        value["usage"]["research_queries"] = 999
        with self.assertRaisesRegex(ValueError, "invalid time-stopped"):
            guard.resume_legacy_time_stop(value)
        self.assertEqual(value["status"], "budget_exhausted")

    def test_even_explicit_restart_routes_clock_stops_to_same_run(self):
        value = self.stopped("overall elapsed-time budget exhausted")
        for allow in (True, False):
            status, rows = start_word.blocking_runs([value], allow_restart_after_budget_exhausted=allow)
            self.assertEqual(status, "resume_required")
            self.assertEqual(rows[0]["run_id"], value["run_id"])

    def test_remote_non_resumable_decision_is_not_overridden_by_summary(self):
        value = self.stopped("overall elapsed-time budget exhausted")
        value["time_stop_resumable"] = False
        value.pop("review_ingest_failures")  # remote summary omits full failure state
        status, _ = start_word.blocking_runs([value], allow_restart_after_budget_exhausted=False)
        self.assertEqual(status, "restart_confirmation_required")

    def test_resume_cli_publishes_recovery_without_review_calls(self):
        value = self.stopped("draft saved after pre-draft budget expired")
        value["publication"] = {"mode": "connector"}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "audits/workflow_runs/eliminate/run-001.json"
            guard._write(path, value)
            with patch.object(run_word_v3, "REPO_ROOT", root), \
                 patch.object(run_word_v3.publish_checkpoint, "select"), \
                 patch.object(run_word_v3.publish_checkpoint, "publish", return_value=True), \
                 patch.object(run_word_v3, "_commit_and_push") as publish, \
                 patch.object(run_word_v3, "execute_api_review_stage") as review, \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(run_word_v3._resume(path), 0)
            recovered = guard._read(path)
            self.assertEqual(recovered["run_id"], value["run_id"])
            self.assertEqual(recovered["saved_results"], value["saved_results"])
            self.assertEqual(recovered["stage_history"], value["stage_history"])
            self.assertEqual(json.loads(output.getvalue())["status"], "publication_pending")
            publish.assert_called_once()
            review.assert_not_called()

    def test_late_draft_partial_cursor_is_reconciled_without_double_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, value = run_word_v3.create_guard_manifest(
                "sample", repo_root=root, branch="word/sample", base_sha="a" * 40,
                run_id="legacy-late-draft", now=START)
            confirm_without_git(value)
            request = run_word_v3.next_stage_request(value)
            for relative in request["output_paths"]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}" if path.suffix == ".json" else "saved draft", encoding="utf-8")
            run_word_v3.record_cost(value, collection="stages", item_id="generation",
                                   input_bytes=100, duration_seconds=1400)
            guard.advance_stage(value, stage="draft_saved", now=START + timedelta(minutes=24))
            value["status"] = "budget_exhausted"
            value["stop_reason"] = "draft saved after pre-draft budget expired"
            costs = copy.deepcopy(value["metrics"])
            snapshots = {p: (root / p).read_bytes() for p in request["output_paths"]}
            original = copy.deepcopy(value)
            with patch.object(Path, "is_file", return_value=False):
                with self.assertRaisesRegex(ValueError, "every saved generation output"):
                    run_word_v3._recover_time_stop(value, repo_root=root)
            self.assertEqual(value, original)
            self.assertTrue(run_word_v3._recover_time_stop(value, repo_root=root))
            self.assertEqual(run_word_v3.next_stage_request(value)["name"], "mechanical_validator")
            self.assertEqual(value["metrics"], costs)
            self.assertEqual(guard.validate_manifest(value), [])
            self.assertEqual({p: (root / p).read_bytes() for p in snapshots}, snapshots)


class SelectiveRecheckTests(unittest.TestCase):
    BODY = "＃発音\n/test/\n＃意味・用法・関連表現\n1. 【名詞】見本\n【語法・注意】old\n【頻度】old"

    def test_multiple_local_edits_use_dependency_union(self):
        plan = revision.plan_rechecks(self.BODY, self.BODY.replace("old", "new"))
        self.assertFalse(plan["full_recheck"])
        self.assertEqual(set(plan["invalidated_passes"]), {"qualification", "sense-structure", "evidence"})
        self.assertEqual(len(plan["reusable_passes"]), 4)

    def test_pos_change_or_reordering_still_invalidates_every_pass(self):
        for after in (self.BODY.replace("【名詞】", "【動詞】"), self.BODY.replace("1. 【", "2. 【")):
            self.assertEqual(set(revision.plan_rechecks(self.BODY, after)["invalidated_passes"]), revision.ALL_CHECKER_PASSES)

    def test_renumbered_sense_swap_still_requires_full_recheck(self):
        before = "＃語義\n1. 【名詞】意味A\n2. 【名詞】意味B"
        after = "＃語義\n1. 【名詞】意味B\n2. 【名詞】意味A"
        self.assertTrue(revision.plan_rechecks(before, after)["full_recheck"])

    def test_moving_an_unchanged_note_to_another_sense_is_not_reusable(self):
        before = "＃語義\n1. 【名詞】意味A\n【語法・注意】only A\n2. 【名詞】意味B"
        after = "＃語義\n1. 【名詞】意味A\n2. 【名詞】意味B\n【語法・注意】only A"
        plan = revision.plan_rechecks(before, after)
        self.assertEqual(plan["changed_units"], ["usage_notes"])
        self.assertEqual(set(plan["invalidated_passes"]), revision.UNIT_TO_PASSES["usage_notes"])

    def test_all_pairs_of_classifiable_edits_compose_safely(self):
        units = list(revision.UNIT_TO_PASSES)
        before = {unit: ["unchanged"] for unit in units}
        for index, left in enumerate(units):
            for right in units[index + 1:]:
                after = copy.deepcopy(before)
                after[left] = after[right] = ["changed"]
                with patch.object(revision, "_semantic_snapshot", side_effect=[(before, []), (after, [])]):
                    plan = revision.plan_rechecks("before", "after")
                self.assertEqual(set(plan["invalidated_passes"]), revision.UNIT_TO_PASSES[left] | revision.UNIT_TO_PASSES[right])


if __name__ == "__main__":
    unittest.main()
