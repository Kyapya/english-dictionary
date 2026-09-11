from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import handoff_provenance as provenance
import publish_checkpoint as publish
import review_liveness
import merge_preflight
from file_lock import exclusive_lock


class ProvenanceTests(unittest.TestCase):
    def test_missing_original_is_not_independent_provenance(self):
        self.assertTrue(provenance.validate(
            {"reviewer": {"mode": "handoff", "agent_id": "invented"}},
            ROOT, required=True))

    def test_original_is_immutable_and_decisions_cannot_be_rewritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "audits/runs/t/test/run/handoff/final_review.response.json"
            path.parent.mkdir(parents=True)
            source = {"decision": "reject", "findings": [{"id": "F1"}]}
            path.write_text(json.dumps(source), encoding="utf-8")
            output = copy.deepcopy(source)
            output["reviewer"] = {"mode": "handoff", "agent_id": "actual", "ingested_by": "orchestrator",
                                  "source_response": provenance.bind(path, root)}
            path.write_text("new canonical response", encoding="utf-8")
            self.assertEqual(provenance.validate(output, root, required=True), [])
            output["decision"] = "pass"
            self.assertTrue(provenance.validate(output, root, required=True))
            output["decision"] = "reject"
            saved = root / output["reviewer"]["source_response"]["path"]
            saved.write_text("tampered", encoding="utf-8")
            self.assertTrue(provenance.validate(output, root, required=True))

    def test_traversal_is_rejected(self):
        self.assertTrue(provenance.validate(
            {"reviewer": {"mode": "handoff", "source_response":
                          {"path": "audits/runs/../../../../outside", "sha256": "a"*64}}},
            ROOT, required=True))

    def test_prefix_template_does_not_count_as_blind_review(self):
        examples, rows = [], []
        for index in range(5):
            sentence = f"The sample number {index} shows variation in color."
            prefix = " ".join(sentence.split()[:4])
            examples.append({"example_id": str(index), "example": sentence})
            rows.append({"example_id": str(index), "classification": "unique",
                         "candidate_sense_ids": ["sense:001"], "discriminating_terms": [prefix],
                         "rationale": f'The phrase "{prefix}" in the example {sentence} supports sense:001.'})
        request = {"input_sections": {"collocations_examples": examples, "sense_structure": []}}
        errors = review_liveness.validate_attribution_liveness({"attributions": rows}, request)
        self.assertIn(review_liveness.C1_SYNTHETIC_REVIEW, review_liveness.invalidation_ids(errors))

    def test_numbered_target_echo_is_not_review_reasoning(self):
        errors = review_liveness.validate_final_review_liveness(
            {"relation_results": [{"id": "r1", "notes": "Reviewed relation sequence 99 (r1): source relation"}]},
            relation_quotes={"r1": "source relation"})
        self.assertIn(review_liveness.C1_SYNTHETIC_REVIEW, review_liveness.invalidation_ids(errors))

    def test_real_zero_findings_are_still_allowed(self):
        self.assertEqual(review_liveness.zero_finding_run_errors(
            {"pass_outputs": []}, {"findings": []}, {"article_findings": []}), [])

    def test_lock_releases_after_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lock"
            with self.assertRaises(RuntimeError):
                with exclusive_lock(path):
                    raise RuntimeError("work failed")
            with exclusive_lock(path):
                self.assertTrue(path.exists())

    def test_squash_is_rejected_for_review_history(self):
        with mock.patch.object(merge_preflight.subprocess, "check_output",
                               return_value="audits/runs/t/test/r/final_blind.json\n"), \
             mock.patch("content_audit.validate_changed", return_value=[]):
            self.assertTrue(merge_preflight.validate("base", "head", "squash", ROOT))
            self.assertEqual(merge_preflight.validate("base", "head", "merge", ROOT), [])


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        self.remote = Path(self.temp.name) / "remote.git"
        subprocess.run(["git", "init", "--bare", str(self.remote)], capture_output=True, check=True)
        publish.git(self.root, "init", "-b", "main")
        publish.git(self.root, "config", "user.name", "Test")
        publish.git(self.root, "config", "user.email", "test@example.invalid")
        publish.git(self.root, "remote", "add", "origin", str(self.remote))
        (self.root / "a.txt").write_text("base", encoding="utf-8")
        self.commit()
        publish.git(self.root, "push", "origin", "main")
        publish.git(self.root, "switch", "-c", "entry/test")
        (self.root / "a.txt").write_text("new", encoding="utf-8")
        self.commit()

    def commit(self):
        publish.git(self.root, "add", "-A")
        publish.git(self.root, "commit", "-m", "test")

    def prepare(self):
        original = publish.git
        def local_only(root, *args):
            if args == ("remote", "get-url", "origin"):
                return "https://github.com/owner/repo.git"
            return original(root, *args)
        with mock.patch.object(publish, "git", side_effect=local_only):
            return publish.prepare(self.root, "owner/repo")

    def test_resume_keeps_progress_and_new_commit_creates_new_plan(self):
        first = self.prepare()
        state = publish.session(self.root, first["plan_id"])
        sha = state["plan"]["commits"][0]["entries"][0]["sha"]
        publish.record_progress(self.root, first["plan_id"], "blob", sha, None)
        self.assertTrue(self.prepare()["resumed"])
        self.assertIn(sha, publish.session(self.root, first["plan_id"])["blobs"])
        (self.root / "a.txt").write_text("next", encoding="utf-8")
        self.commit()
        second = self.prepare()
        self.assertNotEqual(first["plan_id"], second["plan_id"])
        with self.assertRaisesRegex(ValueError, "stale"):
            publish.session(self.root, first["plan_id"])

    def test_paging_does_not_reread_git_blob_or_probe_remote(self):
        prepared = self.prepare()
        state = publish.session(self.root, prepared["plan_id"])
        sha = state["plan"]["commits"][0]["entries"][0]["sha"]
        with mock.patch.object(publish.subprocess, "check_output", wraps=subprocess.check_output) as calls:
            publish.blob_page(self.root, sha, 0, 4, prepared["plan_id"])
            publish.blob_page(self.root, sha, 4, 4, prepared["plan_id"])
        self.assertEqual(sum("cat-file" in call.args[0] for call in calls.call_args_list), 1)
        self.assertEqual(sum("ls-remote" in call.args[0] for call in calls.call_args_list), 0)

    def test_destination_mismatch_fails_before_upload(self):
        with self.assertRaisesRegex(ValueError, "destination"):
            publish.prepare(self.root, "different/repo")

    def test_progress_cannot_include_unplanned_objects(self):
        prepared = self.prepare()
        with self.assertRaisesRegex(ValueError, "outside"):
            publish.record_progress(self.root, prepared["plan_id"], "blob", "f"*40, None)
