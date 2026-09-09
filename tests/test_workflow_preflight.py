from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tarfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import publish_checkpoint as publish
import review_preflight as preflight
import run_word

CYCLE = ROOT / "audits/runs/c/commission/20260907T100725Z-307ceedc"
ENTRY = ROOT / "entries/c/commission.md"
MANIFEST = ROOT / "audits/workflow_runs/commission/20260907T100725Z-307ceedc.json"


class ReviewPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        # Freeze regression inputs at the incident commit, so future commission
        # corrections do not silently change the expected review fixture.
        data = subprocess.check_output(["git", "-C", str(ROOT), "archive", "dbcdfce512fa825f995896570692ac904b832393", "prompts", "entries/c/commission.md", "audits/runs/c/commission", "audits/workflow_runs/commission", "audits/escaped_defect_taxonomy.json", "audits/review_invalidations.json"])
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            archive.extractall(cls.root, filter="data")
        gitdir = publish.git(ROOT, "rev-parse", "--absolute-git-dir")
        (cls.root / ".git").write_text("gitdir: " + gitdir + "\n")
        cls.cycle = cls.root / CYCLE.relative_to(ROOT)
        cls.entry = cls.root / ENTRY.relative_to(ROOT)
        cls.manifest = cls.root / MANIFEST.relative_to(ROOT)

    def test_default_without_api_key_selects_handoff(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(run_word.build_parser().parse_args([]).reviewer_mode, "handoff")

    def test_packet_has_complete_inventories_and_no_assumed_passes(self):
        packet = preflight.final_inputs(self.entry, self.cycle, self.root)
        self.assertEqual(len(packet["inventories"]["target_results"]), 166)
        self.assertEqual(len(packet["inventories"]["relation_results"]), 118)
        self.assertEqual(len(packet["inventories"]["source_inventory_results"]), 14)
        for field, rows in packet["inventories"].items():
            self.assertEqual([row["id"] for row in rows], [row["id"] for row in packet["response_template"][field]])
            self.assertTrue(all(row["status"] is None for row in packet["response_template"][field]))

    def test_missing_input_fails_before_git_or_reviewer(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "source_inventory"):
                preflight.final_inputs(ENTRY, Path(directory), ROOT)

    def test_frozen_packet_cannot_be_rebound(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            preflight.freeze(path, {"body": "original"})
            before = path.read_bytes()
            preflight.freeze(path, {"body": "original"})
            with self.assertRaisesRegex(ValueError, "immutable"):
                preflight.freeze(path, {"body": "revised"})
            self.assertEqual(path.read_bytes(), before)

    def test_changed_source_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            cycle = Path(directory)
            path = cycle / "source_inventory.json"
            path.write_text("original")
            packet = {"_output_metadata": {"input_body_sha256": preflight.audit.body_sha256(ENTRY)}, "input_bindings": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}}
            preflight.check_bindings(packet, ENTRY, cycle)
            path.write_text("changed")
            with self.assertRaisesRegex(ValueError, "changed after dispatch"):
                preflight.check_bindings(packet, ENTRY, cycle)

    def test_real_cold_failure_is_detected_without_mutations(self):
        manifest = json.loads(self.manifest.read_text())
        manifest["run_id"] = "20260907T094627Z-7fe74815"
        manifest["orchestrator"] = run_word.plan_payload("commission", self.root, reviewer_mode="handoff")
        manifest["orchestrator_state"]["next_stage_index"] = 4
        before = copy.deepcopy(manifest)
        old_cycle = self.cycle.parent / manifest["run_id"]
        hashes = {p: p.read_bytes() for p in old_cycle.rglob("*.json")}
        with self.assertRaisesRegex(ValueError, "COLD-001.*exact quote") as error:
            preflight.validate(manifest, stage="cold_review", declared_model="gpt-5", reviewer_agent_id="cold-independent", repo_root=self.root, ingest=run_word.ingest_handoff_review)
        self.assertIn("COLD-005", str(error.exception))
        self.assertEqual(manifest, before)
        self.assertEqual(hashes, {p: p.read_bytes() for p in old_cycle.rglob("*.json")})

    def test_final_review_rehearsal_passes_without_mutations(self):
        manifest = json.loads(self.manifest.read_text())
        manifest["orchestrator_state"]["next_stage_index"] = 10
        hashes = {p: p.read_bytes() for p in self.cycle.rglob("*.json")}
        result = preflight.validate(manifest, stage="final_review", declared_model="gpt-5", reviewer_agent_id="final-independent", repo_root=self.root, ingest=run_word.ingest_handoff_review)
        self.assertTrue(result["valid"])
        self.assertEqual(hashes, {p: p.read_bytes() for p in self.cycle.rglob("*.json")})

    def test_same_invalid_response_does_not_exhaust_three_attempts(self):
        manifest = json.loads(self.manifest.read_text())
        manifest.update(status="in_progress", stage="normal_review_complete", review_preflight=preflight.VERSION)
        manifest["orchestrator_state"]["next_stage_index"] = 4
        path = self.root / "retry.json"
        path.write_text(json.dumps(manifest))
        implementation = run_word._parallel._v3
        with mock.patch.object(implementation, "REPO_ROOT", self.root), mock.patch.object(implementation, "retry_pending_process_improvement"), mock.patch.object(implementation, "record_pending_process_event"), mock.patch.object(preflight, "validate", side_effect=ValueError("fixture format error")) as validation, mock.patch("sys.stdout", new_callable=io.StringIO):
            for _ in range(3):
                self.assertEqual(implementation._resume(path, ingest_review="cold_review", declared_model="gpt-5", reviewer_agent_id="independent"), 1)
        result = json.loads(path.read_text())
        self.assertEqual(result["status"], "in_progress")
        self.assertNotIn("review_ingest_failures", result)
        self.assertEqual(result["review_preflight_failures"]["count"], 1)
        self.assertEqual(validation.call_count, 1)


class PublishTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node is needed only for the Work connector adapter")
    def test_connector_adapter_chunking_and_hash_rejection(self):
        result = subprocess.run(["node", "--test", str(ROOT / "tests/test_publish_checkpoint.cjs")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        remote = Path(self.temp.name) / "remote.git"
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
        self.root.mkdir()
        publish.git(self.root, "init", "-b", "main")
        publish.git(self.root, "config", "user.name", "Test")
        publish.git(self.root, "config", "user.email", "test@example.invalid")
        publish.git(self.root, "remote", "add", "origin", str(remote))
        (self.root / "initial").write_text("initial")
        self.commit("initial")
        publish.git(self.root, "push", "origin", "main")
        publish.git(self.root, "switch", "-c", "entry/test")

    def commit(self, message):
        publish.git(self.root, "add", "-A")
        publish.git(self.root, "commit", "-m", message)

    def test_connector_never_calls_git_push(self):
        publish.select(self.root, "connector")
        with mock.patch.object(publish, "git", wraps=publish.git) as call:
            self.assertFalse(publish.publish(self.root))
            self.assertFalse(any("push" in c.args for c in call.call_args_list))

    def test_plan_preserves_binary_deletion_and_seal_order(self):
        (self.root / "blind_seal.json").write_text("sealed")
        self.commit("seal")
        (self.root / "final_review.json").write_text("reviewed")
        (self.root / "binary.xlsx").write_bytes(bytes(range(256)) * 100)
        (self.root / "initial").unlink()
        self.commit("final")
        plan = publish.plan(self.root)
        self.assertEqual([c["message"] for c in plan["commits"]], ["seal", "final"])
        self.assertIn({"path": "initial", "mode": "100644", "type": "blob", "sha": None}, plan["commits"][1]["entries"])
        publish.git(self.root, "push", "origin", "HEAD:entry/test")
        with self.assertRaisesRegex(ValueError, "advanced"):
            publish.plan(self.root)
        accepted = publish.accept(self.root, publish.git(self.root, "rev-parse", "HEAD"))
        self.assertEqual(accepted["local_head"], accepted["remote_head"])
        publish.select(self.root, "connector")
        self.assertTrue(publish.publish(self.root))
        self.assertEqual(publish.plan(self.root)["commits"], [])

    def test_receipt_cannot_accept_wrong_head(self):
        (self.root / "changed").write_text("new")
        self.commit("change")
        with self.assertRaisesRegex(ValueError, "differs"):
            publish.accept(self.root, "0" * 40)


if __name__ == "__main__":
    unittest.main()
