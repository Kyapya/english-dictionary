from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import simple_workflow as flow
from import_to_notion import _select_rows


class SimpleWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "prompts").mkdir()
        for name in ("entry_spec_v5.md", "independent_entry_review.md"):
            shutil.copyfile(ROOT / "prompts" / name, self.root / "prompts" / name)
        self.entry = self.root / "entries/t/take-off.md"
        self.entry.parent.mkdir(parents=True)
        self.body = "＃ take off\n\n【意味】\n離陸する。  \n"
        self.entry.write_text("---\nheadword: take off\nstatus: review_ready\nchecked: false\n"
                              "model: WRITER-PRIVATE-MODEL\nself_verdict: WRITER-VERDICT\n---\n"
                              + self.body, encoding="utf-8")
        self.write_queue([{"headword": "take off", "file": "entries/t/take-off.md",
                           "status": "review_ready", "checked": "false"}])

    def write_queue(self, rows):
        (self.root / "queue").mkdir(exist_ok=True)
        with (self.root / "queue/words.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["headword", "file", "status", "checked"])
            writer.writeheader()
            writer.writerows(rows)

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in self.root.rglob("*") if p.is_file() and "__pycache__" not in p.parts}

    def invoke(self, *arguments):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = flow.main(list(arguments), repo_root=self.root)
        return code, out.getvalue(), err.getvalue()

    def test_all_normal_entrypoints_work_without_git_or_legacy_engines(self):
        scripts = self.root / "scripts"
        scripts.mkdir()
        for name in ("start_word.py", "start_words.py", "run_word.py", "simple_workflow.py", "slugify.py"):
            shutil.copyfile(ROOT / "scripts" / name, scripts / name)
        before = self.snapshot()
        for name in ("start_word", "start_words", "run_word", "simple_workflow"):
            with self.subTest(entrypoint=name):
                completed = subprocess.run([sys.executable, str(scripts / f"{name}.py"),
                                            "take-off", "alpha", "--reviewer-mode", "api"],
                                           cwd=self.root, text=True, encoding="utf-8",
                                           capture_output=True, timeout=15)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                payload = json.loads(completed.stdout)
                self.assertEqual(payload["mode"], "plan_only")
                self.assertEqual(payload["workflow"], flow.VERSION)
                self.assertFalse(payload["review_performed"])
                self.assertFalse(payload["files_changed"])
                self.assertEqual(payload["entries"][0]["headword"], "take off")
                self.assertEqual(payload["entries"][1]["entry_path"], "entries/a/alpha.md")
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / ".git").exists())
        self.assertFalse((self.root / "audits").exists())

    def test_dry_run_and_default_are_identical_and_read_only(self):
        before = self.snapshot()
        default = self.invoke("take off", "alpha")
        dry = self.invoke("take off", "alpha", "--dry-run")
        self.assertEqual(default, dry)
        self.assertEqual(default[0], 0)
        self.assertEqual(before, self.snapshot())

    def test_explicit_modes_are_the_only_legacy_routes(self):
        for arguments in (["a"], ["--dry-run", "a"], ["a", "--reviewer-mode", "api"]):
            self.assertFalse(flow.is_legacy_request(arguments))
        for arguments in (["a", "--legacy"], ["a", "--compact"], ["--resume", "old.json"],
                          ["--resume=old.json"]):
            self.assertTrue(flow.is_legacy_request(arguments))

    def test_intake_preserves_phrases_and_existing_identity(self):
        words = flow.parse_words([" take  off,ALPHA、alpha", "it's", "it’s", "take-off"])
        self.assertEqual(words, ["take off", "ALPHA", "it's"])
        self.assertEqual(flow.plan(["take-off"], self.root)["entries"][0]["headword"], "take off")

    def test_text_and_json_intake_files(self):
        path = self.root / "words.txt"
        path.write_text("take off\nalpha", encoding="utf-8-sig")
        self.assertEqual(flow.parse_words([], path), ["take off", "alpha"])
        path = self.root / "words.json"
        path.write_text('["take off", "alpha"]', encoding="utf-8")
        self.assertEqual(flow.parse_words([], path), ["take off", "alpha"])
        path.write_text('{"words": ["alpha"]}', encoding="utf-8")
        with self.assertRaises(ValueError):
            flow.parse_words([], path)

    def test_invalid_headwords_and_duplicate_queue_fail_without_writes(self):
        for words in ([], ["..."], ["../alpha"], ["語"], ["a; rm"]):
            with self.subTest(words=words), self.assertRaises(ValueError):
                flow.parse_words(words)
        self.write_queue([{"headword": "take off"}, {"headword": "take-off"}])
        before = self.snapshot()
        self.assertEqual(self.invoke("take off")[0], 2)
        self.assertEqual(before, self.snapshot())

    def test_ambiguous_slug_collision_is_rejected(self):
        with self.assertRaises(ValueError):
            flow.parse_words(["a.b", "a b"])

    def test_wrong_queue_path_is_rejected(self):
        self.write_queue([{"headword": "take off", "file": "entries/t/take.md"}])
        self.assertEqual(self.invoke("take off")[0], 2)

    def test_queue_path_escape_is_rejected(self):
        self.write_queue([{"headword": "take off", "file": "../outside.md"}])
        self.assertEqual(self.invoke("take off")[0], 2)

    def test_packet_has_complete_body_and_rules_but_no_writer_metadata(self):
        before = self.snapshot()
        packet = flow.review_packet("entries/t/take-off.md", self.root)
        self.assertTrue(packet.endswith(self.body))
        self.assertIn((self.root / "prompts/entry_spec_v5.md").read_text(encoding="utf-8").rstrip(), packet)
        self.assertIn("任意の表現改善", packet)
        self.assertNotIn("WRITER-PRIVATE-MODEL", packet)
        self.assertNotIn("WRITER-VERDICT", packet)
        self.assertEqual(before, self.snapshot())

    def test_packet_accepts_body_only_and_rejects_broken_front_matter(self):
        self.entry.write_text(self.body, encoding="utf-8")
        self.assertTrue(flow.review_packet("entries/t/take-off.md", self.root).endswith(self.body))
        for body in ("---\nstatus: draft\n", "---\nstatus: draft\n---\n", ""):
            self.entry.write_text(body, encoding="utf-8")
            with self.assertRaises(ValueError):
                flow.review_packet("entries/t/take-off.md", self.root)

    def test_packet_cannot_read_outside_entries(self):
        for path in ("../outside.md", "AGENTS.md", "entries/t/sample.txt"):
            self.assertEqual(self.invoke("--review-entry", path)[0], 2)

    def test_symlink_cannot_escape_repository(self):
        outside = self.root / "outside.md"
        outside.write_text("not an entry", encoding="utf-8")
        link = self.root / "entries/t/link.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable on this platform")
        with self.assertRaises(ValueError):
            flow.review_packet("entries/t/link.md", self.root)

    def test_output_is_opt_in_and_cannot_overwrite_sources_or_existing_packet(self):
        original = self.entry.read_bytes()
        code, _, _ = self.invoke("--review-entry", "entries/t/take-off.md", "--output", str(self.entry))
        self.assertEqual(code, 2)
        self.assertEqual(self.entry.read_bytes(), original)
        (self.root / "exports").mkdir()
        output = self.root / "exports/take-off-review.md"
        code, message, _ = self.invoke("--review-entry", "entries/t/take-off.md", "--output", str(output))
        self.assertEqual(code, 0)
        self.assertIn("NOT been performed", message)
        packet = output.read_bytes()
        self.assertEqual(self.invoke("--review-entry", "entries/t/take-off.md", "--output", str(output))[0], 2)
        self.assertEqual(output.read_bytes(), packet)
        self.assertEqual(self.entry.read_bytes(), original)

    def test_mixed_options_are_rejected(self):
        self.assertEqual(self.invoke("alpha", "--review-entry", "entries/t/take-off.md")[0], 2)
        self.assertEqual(self.invoke("alpha", "--output", "output.md")[0], 2)


class LightweightContractTests(unittest.TestCase):
    def test_body_content_and_format_contracts_are_preserved_exactly(self):
        old = (ROOT / "prompts/legacy_entry_spec_v5.md").read_text(encoding="utf-8")
        new = (ROOT / "prompts/entry_spec_v5.md").read_text(encoding="utf-8")
        start = "## 本文の大見出し"
        old_body = old.split(start, 1)[1].split("## draft checkpoint後", 1)[0]
        new_body = new.split(start, 1)[1].split("## リポジトリへの保存", 1)[0]
        old_body = old_body.replace("生成前の独立棚卸しから決定する", "確認した語義と構文の関係から決定する")
        # The approved label expansion retains the historical content contract.
        old_body = old_body.replace("【コロケーション】", "【コロケーション・構文例】")
        old_body = old_body.replace("## 文法パターンとコロケーション", "## 文法パターンとコロケーション・構文例")
        migration_note = "この欄は、典型的な語の組み合わせと、学習価値のある構文の例示を扱う。新規作成・修正時の正規見出しは `【コロケーション・構文例】` とする。既存の `【コロケーション】` は互換入力として受け付け、一括再保存を必須にしない。\n\n"
        self.assertIn(migration_note, new_body)
        self.assertEqual(new_body.replace(migration_note, ""), old_body)
        # Source research is still substantive; its administrative logging is not.
        start, end = "## 根拠確認", "## 語義・構文の網羅性"
        self.assertEqual(new.split(start, 1)[1].split(end, 1)[0],
                         old.split(start, 1)[1].split("## 生成前の棚卸し", 1)[0])
        for marker in ("必須条件と傾向", "完全な統語フレーム", "語義別頻度",
                       "最小対立の必須化", "同じ語義を過度に細分化しない"):
            self.assertIn(marker, new)
        for marker in ("record-research", "normal_review.independent_candidates", "draft_saved", "final_review_spec_v3"):
            self.assertNotIn(marker, new)

    def test_preserved_legacy_spec_has_exact_original_blob(self):
        content = (ROOT / "prompts/legacy_entry_spec_v5.md").read_bytes()
        blob = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()
        self.assertEqual(blob, "8216823f0ab4332739b7876826488d5dcfb4762b")

    def test_normal_ci_and_notion_have_same_mechanical_contract(self):
        for name in ("validate.yml", "sync-notion.yml"):
            workflow = (ROOT / ".github/workflows" / name).read_text(encoding="utf-8")
            for removed in ("checker_subagent_gate.py", "content_audit.py", "entry_workflow_guard.py",
                            "semantic_resolution_gate.py", "source_first_audit_gate.py", "merge_preflight.py",
                            "targeted_correction.py"):
                self.assertNotIn(removed, workflow)
            for retained in ("scripts/validate_entry.py", "scripts/validate_repository.py"):
                self.assertIn(retained, workflow)
        validate = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertIn("python -m unittest discover -s tests -v", validate)
        self.assertIn("os: [ubuntu-latest, windows-latest]", validate)
        self.assertIn('test "$RESULT" = "success"', validate)
        notion = (ROOT / ".github/workflows/sync-notion.yml").read_text(encoding="utf-8")
        self.assertIn("scripts/import_to_notion.py", notion)
        self.assertNotIn("--include-unchecked", notion)

    def test_notion_still_requires_both_reviewed_status_and_checked_true(self):
        rows = [{"headword": status + checked, "file": "entries/a/a.md", "status": status, "checked": checked}
                for status in ("draft", "review_ready", "needs_review", "checked", "final")
                for checked in ("true", "false")]
        selected = _select_rows(rows, False, None)
        self.assertEqual([row["headword"] for row in selected], ["checkedtrue", "finaltrue"])


if __name__ == "__main__":
    unittest.main()
