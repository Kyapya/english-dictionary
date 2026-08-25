from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import entry_workflow_guard as guard  # noqa: E402
import run_word  # noqa: E402


class RunWordTests(unittest.TestCase):
    def test_dry_run_prints_complete_stage_contract_without_writing(self) -> None:
        before = set((REPO_ROOT / "audits" / "workflow_runs").rglob("*.json"))
        completed = subprocess.run(
            [sys.executable, "scripts/run_word.py", "--dry-run", "test word"],
            cwd=REPO_ROOT,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["entry_path"], "entries/t/test-word.md")
        self.assertEqual(
            [stage["name"] for stage in payload["stages"]],
            [
                "guard_start",
                "generation",
                "mechanical_validator",
                "checker_passes",
                "cold_review",
                "final_blind",
                "blind_seal",
                "final_review",
                "status_update",
                "export",
            ],
        )
        self.assertEqual(
            set((REPO_ROOT / "audits" / "workflow_runs").rglob("*.json")),
            before,
        )
        for stage in payload["stages"]:
            self.assertIn("input_scope", stage)
            self.assertIn("specification_files", stage)
            self.assertIn("output_paths", stage)
            self.assertIsInstance(stage["instruction_bytes"], int)
        self.assertEqual(len(payload["checker_passes"]), 6)
        self.assertTrue(
            all(item["instruction_bytes"] <= 15_000 for item in payload["checker_passes"])
        )

    def test_context_free_stages_receive_no_project_history(self) -> None:
        by_name = {
            stage.name: stage for stage in run_word.build_plan("obvious")
        }
        self.assertEqual(
            by_name["cold_review"].input_scope,
            ("entry body without front matter",),
        )
        self.assertEqual(
            by_name["final_blind"].input_scope, ("latest entry only",)
        )
        for name in ("cold_review", "final_blind"):
            joined = " ".join(
                by_name[name].input_scope
                + by_name[name].specification_files
            )
            self.assertNotIn("ACTIVE.md", joined)
            self.assertNotIn("finding", joined)

    def test_guard_start_uses_guard_manifest_and_keeps_budget_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            started = datetime(2026, 8, 25, tzinfo=timezone.utc)
            path, manifest = run_word.create_guard_manifest(
                "obvious",
                repo_root=root,
                branch="word/obvious",
                base_sha="a" * 40,
                run_id="test-run",
                now=started,
            )
            self.assertTrue(path.is_file())
            self.assertEqual(manifest["schema_version"], guard.SCHEMA_VERSION)
            self.assertEqual(
                manifest["limits"], guard.PROFILES["standard"]
            )
            self.assertEqual(
                manifest["orchestrator"]["orchestrator_version"],
                "run_word_v1",
            )
            reloaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(reloaded, manifest)

    def test_heartbeat_stops_instead_of_extending_budget(self) -> None:
        started = datetime(2026, 8, 25, tzinfo=timezone.utc)
        manifest = guard.new_manifest(
            headword="obvious",
            entry_path="entries/o/obvious.md",
            branch="word/obvious",
            base_sha="a" * 40,
            now=started,
        )
        deadline = manifest["deadline_at"]
        self.assertFalse(
            run_word.heartbeat_manifest(
                manifest, now=started + timedelta(minutes=11)
            )
        )
        self.assertEqual(manifest["status"], "budget_exhausted")
        self.assertEqual(manifest["deadline_at"], deadline)

    def test_guard_checkpoint_mapping_is_ordered(self) -> None:
        planned = [
            checkpoint
            for stage in run_word.build_plan("obvious")
            for checkpoint in stage.guard_checkpoints
        ]
        self.assertEqual(planned, list(guard.STAGES))


if __name__ == "__main__":
    unittest.main()
