"""Mechanical phrase identity regressions through the real workflow entrypoints.

All repositories and remotes are temporary and local. The review responses below
are test fixtures, not linguistic judgments: they exercise real request hashing,
ingest receipts, coverage checks, and finalization without replacing those gates.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import compact_workflow as flow
import start_words as batch
from tests.test_content_audit import ENTRY_TEXT


FIELDS = [
    "headword", "type", "status", "priority", "file", "prompt_version", "model",
    "created_at", "updated_at", "checked", "notes",
]


class PhraseWorkflowIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        for directory in ("scripts", "prompts"):
            shutil.copytree(ROOT / directory, self.root / directory,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (self.root / ".gitignore").write_text("__pycache__/\n*.pyc\n", encoding="utf-8")
        self.entry = self.write_entry("take off", "take-off", "phrase")
        self.inventory = self.root / "audits/runs/t/take-off/source_inventory.json"
        flow._save(self.inventory, {"source_first_audit": {
            "sources": [
                {"source_type": "learner_dictionary", "locator": "https://example.com/one",
                 "independence_group": "one", "facts": []},
                {"source_type": "general_dictionary", "locator": "https://example.com/two",
                 "independence_group": "two", "facts": []},
            ],
            "source_union": [], "claim_units": [],
        }})
        self.queue_path = self.root / "queue/words.csv"
        self.write_queue([self.row("take off", "phrase", "entries/t/take-off.md")])
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Phrase workflow tests")
        self.git("config", "user.email", "phrase-tests@example.invalid")
        self.git("add", ".")
        self.git("commit", "-m", "Mechanical workflow fixture")
        self.remote = self.base / "origin.git"
        subprocess.run(["git", "clone", "--bare", str(self.root), str(self.remote)],
                       check=True, capture_output=True, text=True)
        self.git("remote", "add", "origin", str(self.remote))
        self.git("checkout", "-b", "words/phrase-identity")

    def git(self, *arguments: str) -> str:
        return subprocess.check_output(["git", "-C", str(self.root), *arguments],
                                       text=True, stderr=subprocess.PIPE).strip()

    def cli(self, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, f"scripts/{script}.py", *arguments],
                              cwd=self.root, capture_output=True, text=True, timeout=30)

    def successful_cli(self, script: str, *arguments: str) -> str:
        result = self.cli(script, *arguments)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def write_entry(self, headword: str, slug: str, kind: str) -> Path:
        entry = self.root / "entries" / slug[0] / f"{slug}.md"
        entry.parent.mkdir(parents=True, exist_ok=True)
        text = (ENTRY_TEXT.replace("headword: sample", f"headword: {headword}", 1)
                .replace("type: word", f"type: {kind}", 1)
                .replace("status: checked", "status: draft", 1)
                .replace("checked: true", "checked: false", 1))
        if kind == "phrase":
            text = (text.replace("・a sample of 〈名詞〉", f"・{headword}", 1)
                    .replace("We examined a sample of the material.",
                             "The planes take off on time.", 1))
        entry.write_text(text, encoding="utf-8")
        return entry

    @staticmethod
    def row(headword: str, kind: str, entry_path: str) -> dict[str, str]:
        return dict(zip(FIELDS, [headword, kind, "pending", "7", entry_path,
                                "entry_spec_v5", "fixture-model", "2026-08-13",
                                "2026-08-13", "false", "existing queue identity"]))

    def write_queue(self, rows: list[dict[str, str]]) -> None:
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        with self.queue_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def rows(self, root: Path | None = None) -> list[dict[str, str]]:
        with ((root or self.root) / "queue/words.csv").open(
                encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    def start(self, headword: str) -> tuple[Path, dict]:
        output = self.successful_cli("start_word", headword, "--compact",
                                     "--publish-mode", "connector",
                                     "--reviewer-mode", "handoff")
        run = self.root / output
        self.assertTrue(run.is_file(), output)
        return run, flow._json(run)

    def assert_identity(self, manifest: dict, headword: str, slug: str, kind: str) -> None:
        self.assertEqual(manifest["workflow_contract_version"], flow.VERSION)
        self.assertEqual(manifest["headword"], headword)
        self.assertEqual(manifest["slug"], slug)
        self.assertEqual(manifest["type"], kind)
        self.assertEqual(manifest["entry_path"], f"entries/{slug[0]}/{slug}.md")
        self.assertEqual(manifest["inventory_path"],
                         f"audits/runs/{slug[0]}/{slug}/source_inventory.json")

    def review_fixture(self, run: Path, manifest: dict) -> dict[Path, bytes]:
        areas = list(flow.current(manifest, self.root)["areas"])
        self.assertTrue(areas)
        for role in ("A", "B"):
            request = flow.prepare(manifest, run, role, root=self.root)
            raw = request.parent / f"review-{role}.response.raw.json"
            flow._save(raw, {"schema_version": "compact_review_response_v1",
                             "checked_areas": areas, "unchecked_areas": [],
                             "findings": []})
            flow.ingest(manifest, run, role, request, raw,
                        execution_id=f"fixture-reviewer-{role}",
                        model="mechanical-test-fixture", root=self.root)
            if role == "A":
                self.assertEqual(flow.status(manifest, root=self.root)["publish_gate"],
                                 "blocked")
        self.assertEqual(flow.status(manifest, root=self.root)["publish_gate"], "pass")
        self.assertEqual(len(manifest["review_receipts"]), 2)
        return {path: path.read_bytes() for path in
                (run.parent / run.stem / "compact").glob("*.json")}

    def test_dry_run_keeps_phrase_display_headword_and_slug_without_writes(self) -> None:
        before = self.queue_path.read_bytes()
        plan = json.loads(self.successful_cli("start_word", "take off", "--compact", "--dry-run"))
        self.assertEqual(plan["headword"], "take off")
        self.assertEqual(plan["slug"], "take-off")
        self.assertEqual(plan["workflow_contract_version"], flow.VERSION)
        self.assertEqual(self.queue_path.read_bytes(), before)
        self.assertFalse((self.root / "audits/workflow_runs").exists())

    def test_existing_phrase_reuses_queue_row_and_slug_paths(self) -> None:
        before = self.queue_path.read_bytes()
        run, manifest = self.start("take off")
        self.assert_identity(manifest, "take off", "take-off", "phrase")
        self.assertEqual(run.parent.relative_to(self.root).as_posix(),
                         "audits/workflow_runs/take-off")
        self.assertEqual(self.queue_path.read_bytes(), before)
        self.assertEqual(len(self.rows()), 1)
        self.assertFalse((self.root / "audits/workflow_runs/take off").exists())

    def test_slug_input_uses_existing_phrase_display_identity(self) -> None:
        before = self.queue_path.read_bytes()
        _, manifest = self.start("take-off")
        self.assert_identity(manifest, "take off", "take-off", "phrase")
        self.assertEqual(self.queue_path.read_bytes(), before)

    def test_existing_entry_metadata_supplies_phrase_identity_without_queue_row(self) -> None:
        self.write_queue([])
        _, manifest = self.start("take-off")
        self.assert_identity(manifest, "take off", "take-off", "phrase")
        self.assertEqual([(row["headword"], row["type"], row["file"]) for row in self.rows()],
                         [("take off", "phrase", "entries/t/take-off.md")])

    def test_existing_queue_supplies_phrase_identity_before_entry_exists(self) -> None:
        self.entry.unlink()
        before = self.queue_path.read_bytes()
        _, manifest = self.start("take-off")
        self.assert_identity(manifest, "take off", "take-off", "phrase")
        self.assertEqual(self.queue_path.read_bytes(), before)

    def test_new_phrase_adds_one_phrase_row_with_hyphenated_paths(self) -> None:
        self.write_queue([])
        run, manifest = self.start("look up")
        self.assert_identity(manifest, "look up", "look-up", "phrase")
        self.assertEqual(run.parent.name, "look-up")
        rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["headword"], rows[0]["type"], rows[0]["status"],
                          rows[0]["file"]),
                         ("look up", "phrase", "pending", "entries/l/look-up.md"))

    def test_single_word_retains_word_type_and_existing_paths(self) -> None:
        self.write_queue([])
        _, manifest = self.start("sample")
        self.assert_identity(manifest, "sample", "sample", "word")
        self.assertEqual([(row["headword"], row["type"], row["file"]) for row in self.rows()],
                         [("sample", "word", "entries/s/sample.md")])

    def test_duplicate_slug_rows_are_rejected_before_mutation(self) -> None:
        self.write_queue([self.row("take off", "phrase", "entries/t/take-off.md"),
                          self.row("take-off", "word", "entries/t/take-off.md")])
        queue_before, entry_before = self.queue_path.read_bytes(), self.entry.read_bytes()
        result = self.cli("start_word", "take off", "--compact")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.queue_path.read_bytes(), queue_before)
        self.assertEqual(self.entry.read_bytes(), entry_before)
        self.assertFalse((self.root / "audits/workflow_runs").exists())

    def test_wrong_queue_entry_path_is_rejected_before_mutation(self) -> None:
        self.write_queue([self.row("take off", "phrase", "entries/t/take.md")])
        queue_before, entry_before = self.queue_path.read_bytes(), self.entry.read_bytes()
        result = self.cli("start_word", "take off", "--compact")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.queue_path.read_bytes(), queue_before)
        self.assertEqual(self.entry.read_bytes(), entry_before)
        self.assertFalse((self.root / "audits/workflow_runs").exists())

    def test_reviewed_phrase_finalizes_once_without_rewriting_review_evidence(self) -> None:
        run, manifest = self.start("take off")
        evidence = self.review_fixture(run, manifest)
        receipts = json.loads(json.dumps(manifest["review_receipts"]))
        relative = run.relative_to(self.root).as_posix()
        result = json.loads(self.successful_cli("compact_workflow", "--resume", relative,
                                               "--finalize"))
        self.assertEqual(result["status"], "completed")
        completed = flow._json(run)
        self.assert_identity(completed, "take off", "take-off", "phrase")
        self.assertEqual(flow.validate_completed(completed, root=self.root), [])
        self.assertEqual(completed["review_receipts"], receipts)
        for path, original in evidence.items():
            self.assertEqual(path.read_bytes(), original, path.as_posix())
        rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["headword"], rows[0]["type"], rows[0]["status"],
                          rows[0]["checked"], rows[0]["file"]),
                         ("take off", "phrase", "checked", "true", "entries/t/take-off.md"))
        self.assertIn("headword: take off\ntype: phrase\n", self.entry.read_text(encoding="utf-8"))
        before = self.queue_path.read_bytes()
        self.successful_cli("compact_workflow", "--resume", relative, "--finalize")
        self.assertEqual(self.queue_path.read_bytes(), before)
        self.assertEqual(len(self.rows()), 1)
        self.git("add", ".")
        self.git("commit", "-m", "Finalize reviewed phrase fixture")
        for script in ("checker_subagent_gate", "entry_workflow_guard", "content_audit",
                       "semantic_resolution_gate", "source_first_audit_gate"):
            extra = ["--merge-ready"] if script == "entry_workflow_guard" else []
            self.successful_cli(script, "validate-changed", "--base", "main", "--head", "HEAD", *extra)
        self.successful_cli("merge_preflight", "--base", "main", "--head", "HEAD")
        self.successful_cli("content_audit", "validate-sync", "entries/t/take-off.md")
        self.successful_cli("semantic_resolution_gate", "validate-entries", "entries/t/take-off.md")
        self.successful_cli("import_to_notion", "--entry", "entries/t/take-off.md", "--dry-run")

    def test_old_slug_only_manifest_finalizes_against_existing_phrase_queue(self) -> None:
        run, manifest = self.start("take off")
        manifest["headword"] = "take-off"
        manifest.pop("slug", None)
        manifest.pop("type", None)
        flow._save(run, manifest)
        evidence = self.review_fixture(run, manifest)
        receipts = json.loads(json.dumps(manifest["review_receipts"]))
        relative = run.relative_to(self.root).as_posix()
        self.successful_cli("compact_workflow", "--resume", relative, "--finalize")
        completed = flow._json(run)
        self.assertEqual(flow.validate_completed(completed, root=self.root), [])
        self.assertEqual(completed["review_receipts"], receipts)
        self.assertEqual([(row["headword"], row["type"], row["status"]) for row in self.rows()],
                         [("take off", "phrase", "checked")])
        self.assertIn("headword: take off\ntype: phrase\n", self.entry.read_text(encoding="utf-8"))
        for path, original in evidence.items():
            self.assertTrue(path.is_file(), path.as_posix())
            self.assertEqual(path.read_bytes(), original, path.as_posix())
        self.assertFalse((self.root / "audits/workflow_runs/take off").exists())

    def test_unreviewed_phrase_cannot_finalize_or_modify_queue(self) -> None:
        run, _ = self.start("take off")
        queue_before, entry_before = self.queue_path.read_bytes(), self.entry.read_bytes()
        result = self.cli("compact_workflow", "--resume",
                          run.relative_to(self.root).as_posix(), "--finalize")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("publish gate is blocked", result.stderr)
        self.assertEqual(self.queue_path.read_bytes(), queue_before)
        self.assertEqual(self.entry.read_bytes(), entry_before)

    def test_remote_unfinished_phrase_blocks_slug_alias_and_resumes_same_run(self) -> None:
        run, manifest = self.start("take off")
        relative = run.relative_to(self.root).as_posix()
        original = run.read_bytes()
        self.git("add", ".")
        self.git("commit", "-m", "Unfinished phrase fixture")
        self.git("push", "origin", "HEAD")
        self.git("checkout", "-b", "words/duplicate-attempt", "main")
        queue_before = self.queue_path.read_bytes()
        for headword in ("take off", "take-off"):
            with self.subTest(headword=headword):
                result = self.cli("start_word", headword, "--compact")
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "resume_required")
                self.assertEqual([row["run_id"] for row in payload["runs"]],
                                 [manifest["run_id"]])
                self.assertEqual(payload["runs"][0]["run_path"], relative)
        self.assertEqual(self.queue_path.read_bytes(), queue_before)
        self.assertFalse((self.root / "audits/workflow_runs").exists())
        self.git("checkout", "words/phrase-identity")
        state = json.loads(self.successful_cli("start_word", "--resume", relative))
        self.assertEqual(state["publish_gate"], "blocked")
        self.assertEqual(run.read_bytes(), original)
        self.assertEqual(list(run.parent.glob("*.json")), [run])
        self.assertEqual(len(self.rows()), 1)

    def test_batch_intake_and_real_dispatch_preserve_phrase_identity(self) -> None:
        queue = batch.Queue(self.root)
        original = self.queue_path.read_bytes()
        queue.enqueue(["take off"])
        job = batch.read(queue.job_path("take-off"))
        self.assertEqual((job["headword"], job["slug"], job["status"]),
                         ("take off", "take-off", "queued"))
        self.assertEqual(self.queue_path.read_bytes(), original)
        result = queue.dispatch(max_active=1)
        self.assertEqual(result["counts"]["active"], 1, result)
        job = batch.read(queue.job_path("take-off"))
        workspace = queue.workspace(job)
        self.assertEqual(job["headword"], "take off")
        self.assertEqual(Path(job["run_path"]).parent.as_posix(),
                         "audits/workflow_runs/take-off")
        self.assert_identity(batch.read(workspace / job["run_path"]),
                             "take off", "take-off", "phrase")
        self.assertEqual([(row["headword"], row["type"]) for row in self.rows(workspace)],
                         [("take off", "phrase")])
        self.assertEqual(self.queue_path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
