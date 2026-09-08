from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import start_words as batch

# This backend stands in for the existing orchestrator, not for an LLM review.
# Real legacy workflow regression tests still run in the repository-wide suite.
STARTER = r'''
import json, pathlib, subprocess, sys
word = sys.argv[1]
if word == "broken":
    print(json.dumps({"reason": "fixture failure"}))
    sys.exit(5)
if word == "existing":
    print(json.dumps({"reason": "unfinished guarded workflow exists", "runs": [
        {"branch": "existing-branch", "run_path": "audits/workflow_runs/existing/old.json"}]}))
    sys.exit(3)
slug = word.lower().replace(" ", "-")
root = pathlib.Path.cwd()
p = root / "audits/workflow_runs" / slug / "fixed-run.json"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps({"headword":word, "branch":subprocess.check_output(
    ["git", "branch", "--show-current"], text=True).strip(), "status":"in_progress",
    "stage":"preflight", "started_at":"2030-01-01T00:00:00Z",
    "deadline_at":"2030-01-01T01:00:00Z", "review_ingest_failures":{"count":2}}))
(root / "queue/words.csv").write_text("headword,status\n" + word + ",draft\n")
subprocess.run(["git", "config", "dictionary.publishMode", "connector"], check=True)
print(p.relative_to(root))
'''


class WordBatchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "control"
        self.root.mkdir()
        self.run_git("init", "-b", "main")
        self.run_git("config", "user.name", "Batch Tests")
        self.run_git("config", "user.email", "batch@example.invalid")
        (self.root / "scripts").mkdir()
        (self.root / "scripts/start_word.py").write_text(STARTER)
        (self.root / "scripts/run_word.py").write_text("# existing workflow fixture\n")
        (self.root / "queue").mkdir()
        (self.root / "queue/words.csv").write_text("headword,status\n")
        self.run_git("add", ".")
        self.run_git("commit", "-m", "fixture")
        remote = Path(self.temporary.name) / "remote.git"
        subprocess.run(["git", "clone", "--bare", str(self.root), str(remote)],
                       check=True, capture_output=True)
        self.run_git("remote", "add", "origin", str(remote))
        self.queue = batch.Queue(self.root)

    def run_git(self, *args):
        return batch.git(self.root, *args)

    def job(self, slug):
        return batch.read(self.queue.job_path(slug))

    def change_status(self, slug, status):
        job = self.job(slug)
        path = self.queue.workspace(job) / job["run_path"]
        value = batch.read(path)
        value["status"] = status
        batch.write(path, value)
        return path

    def test_single_word_uses_same_route(self):
        receipt = self.queue.enqueue(["alpha"])
        result = self.queue.dispatch()
        self.assertEqual(1, len(receipt["jobs"]))
        self.assertEqual(1, result["counts"]["active"])
        self.assertTrue(result["jobs"][0]["run_path"].endswith("fixed-run.json"))

    def test_enqueue_does_not_start_timer_or_modify_word_ledger(self):
        self.queue.enqueue(["alpha", "beta"])
        for job in self.queue.jobs():
            self.assertEqual("queued", job["status"])
            self.assertNotIn("started_at", job)
            self.assertFalse(self.queue.workspace(job).exists())
        self.assertEqual("headword,status\n", (self.root / "queue/words.csv").read_text())
        self.assertFalse((self.root / "audits").exists())

    def test_case_duplicates_and_quoted_phrases(self):
        self.assertEqual(["Alpha", "take off", "beta"],
                         batch.parse_words(["Alpha", "alpha", "take off", "beta, beta"]))
        self.queue.enqueue(["Alpha", "alpha"])
        self.assertEqual(1, len(self.queue.jobs()))

    def test_empty_or_unsafe_input(self):
        for value in ("", "日本語", "../alpha", "alpha;rm", "123"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                batch.parse_words([value])

    def test_text_and_json_word_files(self):
        path = self.root / "input.txt"
        path.write_text("alpha\nbeta、take off\n", encoding="utf-8")
        self.assertEqual(["alpha", "beta", "take off"], batch.parse_words([], path))
        path = self.root / "input.json"
        path.write_text('["alpha", "beta", "take off"]')
        self.assertEqual(["alpha", "beta", "take off"], batch.parse_words([], path))
        path.write_text('["alpha", 1]')
        with self.assertRaises(ValueError):
            batch.parse_words([], path)

    def test_new_request_accepted_during_active_words(self):
        self.queue.enqueue(["alpha", "beta"])
        self.queue.dispatch()
        self.queue.enqueue(["gamma", "alpha"])
        result = self.queue.dispatch()
        self.assertEqual(2, result["counts"]["active"])
        self.assertEqual(1, result["counts"]["queued"])
        self.assertEqual(3, len(self.queue.jobs()))

    def test_workspaces_indices_config_and_ledger_are_isolated(self):
        self.queue.enqueue(["alpha", "beta"])
        self.queue.dispatch()
        a = self.queue.workspace(self.job("alpha"))
        b = self.queue.workspace(self.job("beta"))
        self.assertNotEqual(a, b)
        self.assertNotEqual(batch.git(a, "rev-parse", "--git-common-dir"), str(self.queue.common))
        batch.git(a, "config", "dictionary.publishMode", "git")
        self.assertEqual("connector", batch.git(b, "config", "dictionary.publishMode"))
        self.assertEqual("main", self.run_git("branch", "--show-current"))
        self.assertEqual("headword,status\nalpha,draft\n", (a / "queue/words.csv").read_text())
        self.assertEqual("headword,status\nbeta,draft\n", (b / "queue/words.csv").read_text())
        self.assertEqual("headword,status\n", (self.root / "queue/words.csv").read_text())

    def test_one_failure_does_not_stop_siblings(self):
        self.queue.enqueue(["broken", "alpha"])
        result = self.queue.dispatch()
        self.assertEqual(1, result["counts"]["active"])
        self.assertEqual("blocked", self.job("broken")["status"])
        self.queue.enqueue(["beta"])
        self.assertEqual(2, self.queue.dispatch()["counts"]["active"])

    def test_dispatch_does_not_start_same_job_again(self):
        self.queue.enqueue(["alpha"])
        self.queue.dispatch()
        job = self.job("alpha")
        path = self.queue.workspace(job) / job["run_path"]
        before = path.read_bytes()
        self.queue.enqueue(["alpha"])
        with patch.object(self.queue, "_prepare", side_effect=AssertionError("duplicate start")):
            self.queue.dispatch()
        self.assertEqual(before, path.read_bytes())

    def test_completed_releases_slot_without_changing_manifest(self):
        self.queue.enqueue(["alpha", "beta"])
        self.queue.dispatch(max_active=1)
        path = self.change_status("alpha", "completed")
        before = path.read_bytes()
        result = self.queue.dispatch(max_active=1)
        self.assertEqual(1, result["counts"]["completed"])
        self.assertEqual(1, result["counts"]["active"])
        self.assertEqual(before, path.read_bytes())

    def test_exhausted_budget_is_not_reset(self):
        self.queue.enqueue(["alpha", "beta"])
        self.queue.dispatch(max_active=1)
        path = self.change_status("alpha", "budget_exhausted")
        before = path.read_bytes()
        self.queue.dispatch(max_active=1)
        self.queue.recover("alpha")
        self.assertEqual("blocked", self.job("alpha")["status"])
        self.assertEqual("active", self.job("beta")["status"])
        self.assertEqual(before, path.read_bytes())

    def test_time_warning_is_visible_without_restarting_or_changing_worker(self):
        self.queue.enqueue(["alpha", "beta"])
        self.queue.dispatch(max_active=1)
        job = self.job("alpha")
        path = self.queue.workspace(job) / job["run_path"]
        value = batch.read(path)
        value["last_heartbeat_at"] = "2030-01-02T00:00:00Z"
        value["time_warnings"] = {"elapsed_target_exceeded": {"stage": "cold_review_complete"}}
        batch.write(path, value)
        before = path.read_bytes()
        with patch.object(self.queue, "_prepare", side_effect=AssertionError("do not restart")):
            result = self.queue.dispatch(max_active=1)
        row = next(row for row in result["jobs"] if row["slug"] == "alpha")
        self.assertEqual(row["time_warnings"], value["time_warnings"])
        self.assertEqual(row["last_heartbeat_at"], value["last_heartbeat_at"])
        self.assertEqual(row["status"], "active")
        self.assertEqual(result["counts"]["queued"], 1)
        self.assertEqual(before, path.read_bytes())

    def test_existing_remote_run_is_not_bypassed(self):
        self.queue.enqueue(["existing", "alpha"])
        result = self.queue.dispatch()
        job = self.job("existing")
        self.assertEqual("blocked", job["status"])
        self.assertEqual("existing-branch", job["blocked_runs"][0]["branch"])
        self.assertEqual(1, result["counts"]["active"])

    def test_interrupted_preparation_never_requeued_implicitly(self):
        self.queue.enqueue(["alpha"])
        job = self.job("alpha")
        job["status"] = "preparing"
        batch.write(self.queue.job_path("alpha"), job)
        with patch.object(self.queue, "_prepare", side_effect=AssertionError("restart")):
            self.assertEqual(1, self.queue.dispatch()["counts"]["preparing"])
        with self.assertRaises(ValueError):
            self.queue.recover("alpha")

    def test_recover_existing_manifest_keeps_failure_counter_and_deadline(self):
        self.queue.enqueue(["alpha"])
        self.queue.dispatch()
        job = self.job("alpha")
        path = self.queue.workspace(job) / job["run_path"]
        before = path.read_bytes()
        job["status"] = "preparing"
        job["run_path"] = None
        batch.write(self.queue.job_path("alpha"), job)
        self.queue.recover("alpha")
        self.assertEqual("active", self.job("alpha")["status"])
        self.assertEqual(before, path.read_bytes())

    def test_simultaneous_intake_deduplicates(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda _: self.queue.enqueue(["alpha", "beta"]), range(8)))
        self.assertEqual(2, len(self.queue.jobs()))
        self.assertEqual(8, len(list((self.root / "queue/batches").glob("*.json"))))

    def test_simultaneous_dispatch_respects_shared_limit(self):
        self.queue.enqueue(["alpha", "beta", "gamma", "delta"])
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.queue.dispatch(max_active=2), range(2)))
        self.assertEqual(2, self.queue.snapshot()["counts"]["active"])
        self.assertEqual(2, self.queue.snapshot()["counts"]["queued"])

    def test_mode_conflict_has_no_partial_new_job(self):
        self.queue.enqueue(["beta"])
        with self.assertRaises(ValueError):
            self.queue.enqueue(["alpha", "beta"], publish_mode="git")
        self.assertFalse(self.queue.job_path("alpha").exists())

    def test_capacity_not_silently_increased(self):
        self.queue.enqueue(["alpha", "beta"])
        self.queue.dispatch(max_active=1)
        with self.assertRaises(ValueError):
            self.queue.dispatch(max_active=2)

    def test_omitted_capacity_uses_existing_configuration(self):
        self.queue.enqueue(["alpha", "beta"])
        self.queue.dispatch(max_active=1)
        self.assertEqual(1, self.queue.dispatch()["counts"]["active"])
        self.queue.configure(2)
        self.assertEqual(2, self.queue.dispatch()["counts"]["active"])

    def test_missing_workspace_does_not_restart(self):
        self.queue.enqueue(["alpha"])
        job = self.job("alpha")
        job.update(status="active", run_path="audits/workflow_runs/alpha/fixed-run.json")
        batch.write(self.queue.job_path("alpha"), job)
        with patch.object(self.queue, "_prepare", side_effect=AssertionError("restart")):
            result = self.queue.dispatch()
        self.assertEqual(1, result["counts"]["active"])
        self.assertFalse(result["jobs"][0]["workspace_available"])

    def test_no_baseline_does_not_adopt_old_manifest_during_clone(self):
        self.queue.enqueue(["alpha"])
        job = self.job("alpha")
        workspace = self.queue.workspace(job)
        directory = workspace / "audits/workflow_runs/alpha"
        directory.mkdir(parents=True)
        batch.write(directory / "old.json", {"headword": "alpha", "status": "completed"})
        job["status"] = "preparing"
        batch.write(self.queue.job_path("alpha"), job)
        self.assertEqual(1, self.queue.snapshot()["counts"]["preparing"])

    def test_corrupt_manifest_fails_closed_for_only_that_word(self):
        self.queue.enqueue(["alpha", "beta"])
        self.queue.dispatch()
        job = self.job("alpha")
        path = self.queue.workspace(job) / job["run_path"]
        path.write_text("not JSON")
        self.assertEqual(1, self.queue.snapshot()["counts"]["blocked"])
        self.assertEqual("active", self.job("beta")["status"])

    def test_path_traversal_run_is_rejected(self):
        self.queue.enqueue(["alpha"])
        self.queue.dispatch()
        job = self.job("alpha")
        job["run_path"] = "../../outside.json"
        batch.write(self.queue.job_path("alpha"), job)
        self.assertEqual(1, self.queue.snapshot()["counts"]["blocked"])

    def test_3000_words_are_queued_without_3000_runs_or_huge_output(self):
        receipt = self.queue.enqueue([f"word{i}" for i in range(3000)])
        result = self.queue.snapshot()
        self.assertEqual(3000, len(receipt["jobs"]))
        self.assertEqual(3000, result["counts"]["queued"])
        self.assertEqual(100, len(result["jobs"]))
        self.assertEqual(2900, result["omitted_jobs"])
        self.assertFalse((self.queue.control / "workers").exists())


if __name__ == "__main__":
    unittest.main()
