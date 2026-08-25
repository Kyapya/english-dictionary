from __future__ import annotations

import json
import shutil
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
                "finding_resolution",
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
            by_name["final_blind"].input_scope, ("latest entry body only",)
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
                "run_word_v3",
            )
            self.assertEqual(manifest["metrics"]["total_cycles"], 1)
            self.assertEqual(manifest["metrics"]["total_revisions"], 0)
            self.assertEqual(
                [item["id"] for item in manifest["metrics"]["checker_passes"]],
                [item["id"] for item in manifest["orchestrator"]["checker_passes"]],
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

    def test_cost_metrics_record_stage_pass_rule_and_total_revision_cost(self) -> None:
        started = datetime(2026, 8, 25, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "prompts").mkdir()
            shutil.copy2(
                REPO_ROOT / "prompts" / "check_router_v6.md",
                root / "prompts" / "check_router_v6.md",
            )
            _, value = run_word.create_guard_manifest(
                "obvious",
                repo_root=root,
                branch="word/obvious",
                base_sha="a" * 40,
                run_id="cost-run",
                now=started,
            )
            run_word.record_cost(
                value,
                collection="stages",
                item_id="generation",
                input_bytes=128,
                duration_seconds=3.5,
                defects_detected=0,
                revision_count=1,
            )
            run_word.record_cost(
                value,
                collection="checker_passes",
                item_id="translation",
                input_bytes=512,
                duration_seconds=1.25,
                defects_detected=2,
            )
            run_word.begin_additional_cycle(value)
            run_word.finalize_cost_metrics(
                value, now=started + timedelta(seconds=20)
            )
            self.assertEqual(value["metrics"]["total_cycles"], 2)
            self.assertEqual(value["metrics"]["total_revisions"], 1)
            self.assertEqual(value["metrics"]["total_duration_seconds"], 20)
            translation = next(
                item
                for item in value["metrics"]["checker_passes"]
                if item["id"] == "translation"
            )
            self.assertEqual(translation["input_bytes"], 512)
            self.assertEqual(translation["defects_detected"], 2)

    def test_final_reconciliation_gets_only_the_v2_input_bundle(self) -> None:
        by_name = {stage.name: stage for stage in run_word.build_plan("obvious")}
        final = by_name["final_review"]
        self.assertEqual(
            final.input_scope,
            (
                "latest entry body",
                "sealed final-blind output",
                "all checker, cold, and sealed final-blind findings",
                "finding resolution records",
            ),
        )
        self.assertEqual(
            final.specification_files, ("prompts/final_review_spec_v2.md",)
        )

    def test_orchestrator_completes_every_stage_in_order_with_costs(self) -> None:
        started = datetime(2026, 8, 25, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "prompts").mkdir()
            shutil.copy2(
                REPO_ROOT / "prompts" / "check_router_v6.md",
                root / "prompts" / "check_router_v6.md",
            )
            _, value = run_word.create_guard_manifest(
                "obvious",
                repo_root=root,
                branch="word/obvious",
                base_sha="a" * 40,
                run_id="e2e-run",
                now=started,
            )
            confirmed_at = started + timedelta(seconds=1)
            value["remote_checkpoint"] = {
                "confirmed": True,
                "confirmed_at": guard._format_time(confirmed_at),
                "commit_sha": "b" * 40,
            }
            value["stage"] = "preflight_pushed"
            value["stage_history"].append(
                {
                    "stage": "preflight_pushed",
                    "recorded_at": guard._format_time(confirmed_at),
                    "notes": "test checkpoint",
                }
            )
            value["last_heartbeat_at"] = guard._format_time(confirmed_at)
            while (request := run_word.next_stage_request(value)) is not None:
                pass_costs = None
                if request["name"] == "checker_passes":
                    pass_costs = {
                        item["id"]: {
                            "input_bytes": 100,
                            "duration_seconds": 0.1,
                            "defects_detected": 0,
                        }
                        for item in value["metrics"]["checker_passes"]
                    }
                run_word.complete_orchestrated_stage(
                    value,
                    stage=request["name"],
                    input_bytes=100,
                    duration_seconds=0.5,
                    revision_count=1 if request["name"] == "generation" else 0,
                    checker_pass_costs=pass_costs,
                    now=started + timedelta(minutes=2),
                    verify_outputs=False,
                )
            self.assertEqual(value["status"], "completed")
            self.assertEqual(value["metrics"]["total_cycles"], 1)
            self.assertEqual(value["metrics"]["total_revisions"], 1)
            self.assertEqual(
                value["orchestrator_state"]["completed_stages"],
                [item["name"] for item in value["orchestrator"]["stages"]],
            )
            self.assertEqual(guard.validate_manifest(value, merge_ready=True), [])

    def test_stage_cannot_complete_without_exact_planned_outputs(self) -> None:
        started = datetime(2026, 8, 25, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "prompts").mkdir()
            shutil.copy2(
                REPO_ROOT / "prompts" / "check_router_v6.md",
                root / "prompts" / "check_router_v6.md",
            )
            _, value = run_word.create_guard_manifest(
                "obvious",
                repo_root=root,
                branch="word/obvious",
                base_sha="a" * 40,
                run_id="output-run",
                now=started,
            )
            value["remote_checkpoint"] = {
                "confirmed": True,
                "confirmed_at": guard._format_time(started),
                "commit_sha": "b" * 40,
            }
            value["stage"] = "preflight_pushed"
            value["stage_history"].append(
                {
                    "stage": "preflight_pushed",
                    "recorded_at": guard._format_time(started),
                    "notes": "test checkpoint",
                }
            )
            with self.assertRaisesRegex(ValueError, "stage outputs do not exist"):
                run_word.complete_orchestrated_stage(
                    value,
                    stage="generation",
                    input_bytes=10,
                    duration_seconds=1,
                    repo_root=root,
                )
            self.assertEqual(
                value["orchestrator_state"]["completed_stages"], ["guard_start"]
            )

    def test_record_revision_commits_only_the_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"], cwd=root, check=True
            )
            entry = root / "entries" / "t" / "test.md"
            entry.parent.mkdir(parents=True)
            entry.write_text("first\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "initial"], cwd=root, check=True)
            entry.write_text("second\n", encoding="utf-8")
            sha = run_word.record_entry_revision(
                entry, "adopt resolved finding", repo_root=root, push=False
            )
            changed = subprocess.run(
                ["git", "show", "--pretty=", "--name-only", sha],
                cwd=root,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.splitlines()
            self.assertEqual(changed, ["entries/t/test.md"])
            self.assertFalse((root / "audits" / "runs").exists())


if __name__ == "__main__":
    unittest.main()
