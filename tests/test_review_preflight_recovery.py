from __future__ import annotations

import copy
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import entry_workflow_guard as guard
import generate_audit_manifest as audit
import review_preflight
import review_recovery
import review_validation
import run_word_v3 as runner


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def minimal(root: Path, stage: str = "final_review") -> tuple[dict, Path, Path]:
    entry = root / "entries/s/sample.md"
    entry.parent.mkdir(parents=True, exist_ok=True)
    entry.write_text("# sample\n\nExample body.\n", encoding="utf-8")
    cycle = root / "audits/runs/s/sample/recovery-test"
    cycle.mkdir(parents=True, exist_ok=True)
    manifest = guard.new_manifest(headword="sample", entry_path="entries/s/sample.md",
                                  branch="fix/sample", base_sha="a" * 40, run_id="recovery-test")
    manifest.update(review_preflight=review_preflight.VERSION, process_improvement={})
    manifest["orchestrator"] = {"stages": [{
        "name": stage, "reviewer_mode": "handoff", "specification_files": [],
        "output_paths": [str((cycle / (stage + ".json")).relative_to(root))],
        "input_packet_path": str((cycle / "handoff" / (stage + ".request.md")).relative_to(root)),
    }]}
    manifest["orchestrator_state"] = {"next_stage_index": 0, "completed_stages": ["generation", "checker_passes", "cold_review"], "stage_outputs": {"generation": ["entries/s/sample.md"]}}
    return manifest, entry, cycle


class SharedInputValidationTests(unittest.TestCase):
    def test_metadata_reports_multiple_fields_with_expected_and_actual(self):
        errors = review_validation.metadata_errors({"input_body_sha256": "old"}, "source_inventory", "new", {"headword"})
        self.assertGreater(len(errors), 3)
        row = next(e for e in errors if e["path"].endswith("input_body_sha256"))
        self.assertEqual((row["expected"], row["actual"]), ("new", "old"))
        with self.assertRaisesRegex(ValueError, "source_inventory.input_body_sha256 is stale"):
            audit._validate_metadata({"input_body_sha256": "old"}, "source_inventory", "new", {"headword"})

    def test_resolution_diagnostics_include_missing_extra_and_stale_rows(self):
        rows = [{"id": "extra", "finding_id": "extra", "status": "resolved", "disposition": "adopted", "rationale": "specific", "resolved_body_sha256": "old"}]
        errors = review_validation.resolution_errors(rows, {"missing"}, "new")
        coverage = next(e for e in errors if e["code"] == "resolution_coverage")
        self.assertEqual(coverage["missing"], ["missing"])
        self.assertEqual(coverage["extra"], ["extra"])
        self.assertTrue(any(e["path"].endswith("resolved_body_sha256") for e in errors))

    def test_duplicate_ids_fail_and_explicit_empty_lists_remain_valid(self):
        errors = []
        self.assertIsNone(review_validation.index_rows([{"id": "x"}, {"id": "x"}], "rows", errors))
        self.assertEqual(errors[0]["code"], "duplicate_id")
        self.assertEqual(review_validation.resolution_errors([], set(), "hash"), [])

    def test_binding_check_collects_all_changes_without_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, entry, cycle = minimal(root)
            write(cycle / "a.json", {"a": 1})
            packet = {"_output_metadata": {"input_body_sha256": "old"},
                      "input_bindings": {"a.json": "old", "b.json": "missing"}}
            before = (cycle / "a.json").read_bytes()
            with self.assertRaises(review_preflight.PreflightError) as caught:
                review_preflight.check_bindings(packet, entry, cycle)
            self.assertEqual(len(caught.exception.report["errors"]), 3)
            self.assertEqual((cycle / "a.json").read_bytes(), before)

    def test_original_checker_snapshot_is_still_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input_snapshot.json"
            review_preflight.freeze(path, {"body": "old"})
            with self.assertRaisesRegex(ValueError, "immutable review input changed"):
                review_preflight.freeze(path, {"body": "new"})
            self.assertEqual(read(path), {"body": "old"})


class EvidentInputRegressionTests(unittest.TestCase):
    """Mutate the actual completed evident input bundle, never production files."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT / "prompts", self.root / "prompts")
        original = sorted(p for p in (ROOT / "audits/runs/e/evident").iterdir()
                          if p.is_dir() and (p / "final_review.json").is_file())[-1]
        self.cycle = self.root / original.relative_to(ROOT)
        shutil.copytree(original, self.cycle)
        self.entry = self.root / "entries/e/evident.md"
        self.entry.parent.mkdir(parents=True)
        shutil.copy2(ROOT / "entries/e/evident.md", self.entry)
        self.history = mock.patch.object(review_validation, "_sealed_in_history", return_value=True)
        self.history.start()
        self.addCleanup(self.history.stop)

    def report(self):
        return review_validation.final_input_report(self.entry, self.cycle, self.root)

    def test_completed_evident_inputs_pass_input_only_checks(self):
        report = self.report()
        self.assertTrue(report["valid"], json.dumps(report, ensure_ascii=False, indent=2))

    def test_stale_source_and_resolution_id_mismatch_are_reported_together(self):
        source_path = self.cycle / "source_inventory.json"
        resolution_path = self.cycle / "resolutions.json"
        original_source, original_resolutions = source_path.read_bytes(), resolution_path.read_bytes()
        source = read(source_path)
        source["input_body_sha256"] = "stale-source-body"
        write(source_path, source)
        resolutions = read(resolution_path)
        self.assertTrue(resolutions["resolutions"], "regression fixture needs a finding")
        missing = resolutions["resolutions"][0]["id"]
        resolutions["resolutions"][0].update(id="unexpected-finding", finding_id="unexpected-finding")
        write(resolution_path, resolutions)
        report = self.report()
        self.assertFalse(report["valid"])
        self.assertTrue(any(e["path"] == "source_inventory.input_body_sha256" for e in report["errors"]))
        coverage = next(e for e in report["errors"] if e["code"] == "resolution_coverage")
        self.assertIn(missing, coverage["missing"])
        self.assertEqual(coverage["extra"], ["unexpected-finding"])
        source_path.write_bytes(original_source)
        resolution_path.write_bytes(original_resolutions)
        self.assertTrue(self.report()["valid"])

    def test_malformed_input_does_not_hide_independent_stale_hash(self):
        (self.cycle / "targeted_adjudications.json").write_text("{broken", encoding="utf-8")
        source = read(self.cycle / "source_inventory.json")
        source["input_body_sha256"] = "stale"
        write(self.cycle / "source_inventory.json", source)
        report = self.report()
        self.assertTrue(any(e["code"] == "malformed_json" for e in report["errors"]))
        self.assertTrue(any(e["path"] == "source_inventory.input_body_sha256" for e in report["errors"]))
        self.assertTrue(report["blocked_checks"])

    def test_no_api_review_call_or_packet_is_created_for_invalid_inputs(self):
        source = read(self.cycle / "source_inventory.json")
        source["input_body_sha256"] = "stale"
        write(self.cycle / "source_inventory.json", source)
        packet_path = self.cycle / "final_review.request.json"
        packet_path.unlink(missing_ok=True)
        manifest = {"entry_path": "entries/e/evident.md", "run_id": self.cycle.name,
                    "review_preflight": review_preflight.VERSION,
                    "orchestrator": {"stages": [{"name": "final_review", "reviewer_mode": "api",
                        "specification_files": ["prompts/final_review_spec_v2.md"],
                        "output_paths": [str((self.cycle / "final_review.json").relative_to(self.root))]}]},
                    "orchestrator_state": {"next_stage_index": 0}}
        with mock.patch.object(runner.review_call, "execute_review") as call:
            with self.assertRaises(review_preflight.PreflightError):
                runner.execute_api_review_stage(manifest, repo_root=self.root,
                                                provider="openai", model="test-reviewer", api_key="test-only")
        call.assert_not_called()
        self.assertFalse(packet_path.exists())

    def test_missing_original_snapshot_binding_is_reported(self):
        snapshot_path = self.cycle / "check_passes/input_snapshot.json"
        snapshot = read(snapshot_path)
        removed = next(iter(snapshot["request_hashes"]))
        del snapshot["request_hashes"][removed]
        write(snapshot_path, snapshot)
        report = self.report()
        self.assertFalse(report["valid"])
        self.assertTrue(any(e["code"] == "immutable_request_changed"
                            and e["path"] == removed + ".request.json" for e in report["errors"]))

    def test_explicit_bad_evidence_ids_are_not_treated_as_optional(self):
        source = read(self.cycle / "source_inventory.json")
        source["evidence_link_ids"] = None
        write(self.cycle / "source_inventory.json", source)
        report = self.report()
        self.assertFalse(report["valid"])
        self.assertTrue(any(e["code"] == "evidence_ids" for e in report["errors"]))

    def test_template_keeps_every_decision_unjudged(self):
        values = review_preflight.final_inputs(self.entry, self.cycle, self.root)
        template = values["response_template"]
        self.assertIsNone(template["decision"])
        for rows in template.values():
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict) and "status" in row:
                        self.assertIsNone(row["status"])


class ReviewRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.manifest, self.entry, self.cycle = minimal(self.root)
        self.path = self.root / "run.json"
        self.response = self.cycle / "handoff/final_review.response.json"
        write(self.path, self.manifest)
        write(self.response, {"revision": 0})
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(mock.patch.object(runner, "REPO_ROOT", self.root))
        self.stack.enter_context(mock.patch.object(runner, "heartbeat_manifest", return_value=True))
        self.stack.enter_context(mock.patch.object(runner, "retry_pending_process_improvement"))
        self.stack.enter_context(mock.patch.object(runner, "ensure_process_improvement_input"))
        self.stack.enter_context(mock.patch.object(runner, "record_pending_process_event"))
        self.stack.enter_context(redirect_stdout(io.StringIO()))

    def resume(self):
        return runner._resume(self.path, ingest_review="final_review", declared_model="reviewer", reviewer_agent_id="independent-agent")

    def test_three_distinct_preflight_errors_do_not_stop_or_reingest(self):
        before = copy.deepcopy(self.manifest)
        with mock.patch.object(review_preflight, "validate", side_effect=ValueError("contract invalid")), \
                mock.patch.object(runner, "ingest_handoff_review") as ingest:
            for i in range(3):
                write(self.response, {"revision": i})
                self.assertEqual(self.resume(), 1)
        ingest.assert_not_called()
        saved = read(self.path)
        self.assertEqual(saved["status"], "in_progress")
        self.assertNotIn("review_ingest_failures", saved)
        self.assertEqual(saved["review_preflight_failures"]["count"], 3)
        for key in ("run_id", "started_at", "stage_history", "orchestrator_state", "usage"):
            self.assertEqual(saved[key], before[key])

    def test_unchanged_rejection_is_not_revalidated_or_counted_again(self):
        with mock.patch.object(review_preflight, "validate", side_effect=ValueError("invalid")) as validate:
            self.assertEqual(self.resume(), 1)
            self.assertEqual(self.resume(), 1)
        self.assertEqual(validate.call_count, 1)
        self.assertEqual(read(self.path)["review_preflight_failures"]["count"], 1)

    def test_corrected_response_ingests_on_same_run_and_preserves_rejections(self):
        with mock.patch.object(review_preflight, "validate", side_effect=ValueError("invalid")):
            self.resume()
        write(self.response, {"revision": "corrected"})
        with mock.patch.object(review_preflight, "validate", return_value={"valid": True}), \
                mock.patch.object(runner, "ingest_handoff_review", return_value=self.cycle / "final_review.json") as ingest:
            self.assertEqual(self.resume(), 0)
        ingest.assert_called_once()
        saved = read(self.path)
        self.assertEqual(saved["run_id"], self.manifest["run_id"])
        self.assertEqual(saved["orchestrator_state"], self.manifest["orchestrator_state"])
        self.assertEqual(saved["review_correction"]["status"], "resolved")
        self.assertEqual(saved["review_preflight_failures"]["count"], 1)

    def test_unexpected_runtime_error_keeps_execution_failure_path(self):
        with mock.patch.object(review_preflight, "validate", side_effect=RuntimeError("runtime failure")), \
                mock.patch.object(runner, "_report_review_failure", return_value=2) as failure:
            self.assertEqual(self.resume(), 2)
        failure.assert_called_once()
        self.assertNotIn("review_preflight_failures", read(self.path))

    def test_api_input_preflight_rejection_is_not_an_execution_failure(self):
        error = review_validation.PreflightError({"valid": False, "errors": [{"message": "stale source"}], "blocked_checks": []})
        with mock.patch.object(runner, "execute_api_review_stage", side_effect=error), \
                mock.patch.object(runner, "_report_review_failure") as failure:
            self.assertEqual(runner._resume(self.path, call_review=True), 1)
        failure.assert_not_called()
        self.assertNotIn("review_ingest_failures", read(self.path))

    def test_validation_rehearsal_does_not_write_into_real_run(self):
        manifest, entry, cycle = minimal(self.root, "cold_review")
        (self.root / "prompts").mkdir()
        before = copy.deepcopy(manifest)
        def ingest(value, **kwargs):
            value["mutated"] = True
            destination = kwargs["repo_root"] / cycle.relative_to(self.root) / "cold_review.json"
            write(destination, {"created_in_copy": True})
        review_preflight.validate(manifest, stage="cold_review", declared_model="reviewer", reviewer_agent_id="other",
                                  repo_root=self.root, ingest=ingest)
        self.assertEqual(manifest, before)
        self.assertFalse((cycle / "cold_review.json").exists())


class LegacyStopAndPacketTests(unittest.TestCase):
    def legacy(self):
        value = guard.new_manifest(headword="sample", entry_path="entries/s/sample.md",
                                   branch="fix/sample", base_sha="a" * 40, run_id="legacy")
        value.update(status="budget_exhausted", stop_reason="final_review handoff ingestion failed 3 times",
                     review_ingest_failures={"stage": "final_review", "count": 3, "last_error": "invalid input"},
                     last_rejected_review={"fingerprint": "a" * 64, "error": "invalid input"},
                     open_questions=["preserve this question"])
        return value

    def test_validated_legacy_recovery_preserves_identity_counts_and_questions(self):
        value = self.legacy()
        before = copy.deepcopy(value)
        with mock.patch.object(review_recovery, "fingerprint", return_value="b" * 64), \
                mock.patch.object(review_preflight, "validate", return_value={"valid": True}) as validate:
            self.assertTrue(review_recovery.recover_preflight_stop(value, stage="final_review", declared_model="reviewer",
                              reviewer_agent_id="other", repo_root=ROOT, ingest=mock.Mock()))
        validate.assert_called_once()
        self.assertEqual(value["status"], "in_progress")
        for key in ("run_id", "started_at", "stage_history", "usage", "open_questions", "review_ingest_failures"):
            self.assertEqual(value[key], before[key])
        self.assertEqual(len(value["review_preflight_recoveries"]), 1)

    def test_failed_recovery_leaves_terminal_state_unchanged(self):
        value = self.legacy()
        before = copy.deepcopy(value)
        with mock.patch.object(review_recovery, "fingerprint", return_value="b" * 64), \
                mock.patch.object(review_preflight, "validate", side_effect=ValueError("still invalid")):
            with self.assertRaises(ValueError):
                review_recovery.recover_preflight_stop(value, stage="final_review", declared_model="reviewer",
                    reviewer_agent_id="other", repo_root=ROOT, ingest=mock.Mock())
        self.assertEqual(value, before)

    def test_unchanged_or_unrelated_terminal_stops_cannot_be_recovered(self):
        value = self.legacy()
        with mock.patch.object(review_recovery, "fingerprint", return_value="a" * 64), \
                mock.patch.object(review_preflight, "validate") as validate:
            with self.assertRaisesRegex(ValueError, "unchanged"):
                review_recovery.recover_preflight_stop(value, stage="final_review", declared_model="reviewer",
                    reviewer_agent_id="other", repo_root=ROOT, ingest=mock.Mock())
        validate.assert_not_called()
        for reason in ("research query budget exhausted", "final review attempt budget exhausted", "unknown"):
            value["stop_reason"] = reason
            self.assertFalse(review_recovery.is_recoverable_preflight_stop(value, stage="final_review"))
        value = self.legacy()
        value.pop("last_rejected_review")
        self.assertFalse(review_recovery.is_recoverable_preflight_stop(value, stage="final_review"))

    def test_actual_execution_failures_still_stop_at_three_and_keep_history(self):
        value = guard.new_manifest(headword="sample", entry_path="entries/s/sample.md", branch="fix/sample", base_sha="a" * 40)
        for i in range(3):
            running = guard.record_review_ingest_failure(value, stage="final_review", error="runtime")
            self.assertEqual(running, i < 2)
        self.assertEqual(value["status"], "budget_exhausted")
        self.assertEqual(value["review_ingest_failure_total"], 3)
        self.assertEqual(len(value["review_ingest_failure_events"]), 3)
        guard.clear_review_ingest_failures(value)
        self.assertEqual(value["review_ingest_failure_history"][-1]["count"], 3)
        self.assertEqual(value["review_ingest_failure_total"], 3)

    def test_refresh_preserves_old_packet_response_and_checker_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, entry, cycle = minimal(root)
            packet_path = cycle / "final_review.request.json"
            old = {"_output_metadata": {"input_body_sha256": audit.body_sha256(entry)}, "input_bindings": {"source_inventory.json": "old"}}
            write(packet_path, old)
            write(cycle / "handoff/final_review.response.json", {"old_response": True})
            write(cycle / "check_passes/input_snapshot.json", {"immutable": True})
            snapshot = (cycle / "check_passes/input_snapshot.json").read_bytes()
            new = {**copy.deepcopy(old), "input_bindings": {"source_inventory.json": "new"}, "response_template": {"decision": None}}
            review_recovery.bind_final_packet(new, packet_path, refresh=True)
            before_state = copy.deepcopy(manifest["orchestrator_state"])
            review_recovery.replace_final_packet(manifest, packet_path, new)
            archive = cycle / manifest["review_packet_revisions"][-1]["archive"]
            self.assertEqual(read(archive / "final_review.request.json"), old)
            self.assertEqual(read(archive / "handoff/final_review.response.json"), {"old_response": True})
            self.assertFalse((cycle / "handoff/final_review.response.json").exists())
            self.assertEqual((cycle / "check_passes/input_snapshot.json").read_bytes(), snapshot)
            self.assertEqual(manifest["orchestrator_state"], before_state)
            self.assertEqual(read(packet_path)["input_revision_id"], new["response_template"]["input_revision_id"])
            write(cycle / "handoff/final_review.response.json", {"input_revision_id": "obsolete"})
            with self.assertRaisesRegex(ValueError, "input_revision_id"):
                runner.ingest_handoff_review(manifest, stage="final_review", declared_model="reviewer", reviewer_agent_id="other", repo_root=root)

    def test_packet_refresh_cannot_hide_a_body_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, entry, cycle = minimal(root)
            path = cycle / "final_review.request.json"
            old = {"_output_metadata": {"input_body_sha256": "old-body"}, "input_bindings": {"source": "old"}}
            write(path, old)
            with self.assertRaisesRegex(ValueError, "body changed"):
                review_recovery.replace_final_packet(manifest, path, {"_output_metadata": {"input_body_sha256": "new-body"}, "input_bindings": {"source": "new"}})
            self.assertEqual(read(path), old)
            self.assertNotIn("review_packet_revisions", manifest)


if __name__ == "__main__":
    unittest.main()
