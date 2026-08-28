from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from entry_workflow_guard import (  # noqa: E402
    MAX_REVIEW_INGEST_FAILURES,
    PROFILES,
    _is_registered_review_demotion,
    advance_stage,
    clear_review_ingest_failures,
    confirm_remote_checkpoint,
    enforce_budget,
    new_manifest,
    record_research,
    record_review_ingest_failure,
    validate_manifest,
)


START = datetime(2026, 8, 24, 0, 0, tzinfo=timezone.utc)


def manifest() -> dict:
    return new_manifest(
        headword="eliminate",
        entry_path="entries/e/eliminate.md",
        branch="add/eliminate-v5",
        base_sha="a" * 40,
        run_id="run-001",
        now=START,
    )


def confirm_without_git(value: dict, *, at: datetime = START + timedelta(minutes=1)) -> None:
    value["remote_checkpoint"] = {
        "confirmed": True,
        "confirmed_at": at.isoformat().replace("+00:00", "Z"),
        "commit_sha": "b" * 40,
    }
    value["stage"] = "preflight_pushed"
    value["stage_history"].append(
        {
            "stage": "preflight_pushed",
            "recorded_at": at.isoformat().replace("+00:00", "Z"),
            "notes": "test remote checkpoint",
        }
    )
    value["last_heartbeat_at"] = at.isoformat().replace("+00:00", "Z")


class EntryWorkflowGuardTests(unittest.TestCase):
    def test_standard_profile_has_hard_runtime_and_attempt_limits(self) -> None:
        value = manifest()
        self.assertEqual(value["limits"], PROFILES["standard"])
        self.assertEqual(value["status"], "in_progress")
        self.assertEqual(value["stage"], "preflight")
        self.assertEqual(validate_manifest(value), [])

    def test_run_word_v2_manifest_requires_cost_metrics(self) -> None:
        value = manifest()
        value["orchestrator"] = {
            "orchestrator_version": "run_word_v2",
            "stages": [],
            "checker_passes": [],
        }
        self.assertTrue(
            any("requires metrics" in error for error in validate_manifest(value))
        )

    def test_extended_profile_requires_reason(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires profile_reason"):
            new_manifest(
                headword="cast",
                entry_path="entries/c/cast.md",
                branch="update/cast",
                base_sha="a" * 40,
                profile="extended",
                now=START,
            )

    def test_deadlines_cannot_be_extended_after_start(self) -> None:
        value = manifest()
        value["deadline_at"] = (START + timedelta(hours=6)).isoformat().replace("+00:00", "Z")
        self.assertTrue(any("fixed profile runtime" in error for error in validate_manifest(value)))

    def test_research_is_blocked_before_remote_checkpoint(self) -> None:
        with self.assertRaisesRegex(ValueError, "after preflight_pushed"):
            record_research(manifest(), queries=1, candidate_pages=1, now=START)

    def test_attempt_budget_stops_and_preserves_manifest_state(self) -> None:
        value = manifest()
        confirm_without_git(value)
        self.assertTrue(
            record_research(
                value,
                queries=PROFILES["standard"]["max_research_queries"],
                candidate_pages=1,
                now=START + timedelta(minutes=2),
            )
        )
        self.assertFalse(
            record_research(
                value,
                queries=1,
                candidate_pages=0,
                now=START + timedelta(minutes=3),
            )
        )
        self.assertEqual(value["status"], "budget_exhausted")
        self.assertEqual(value["stop_reason"], "research query budget exhausted")
        self.assertTrue(any("merge-ready" in error for error in validate_manifest(value, merge_ready=True)))

    def test_missing_heartbeat_stops_run(self) -> None:
        value = manifest()
        confirm_without_git(value)
        self.assertFalse(enforce_budget(value, now=START + timedelta(minutes=12)))
        self.assertEqual(value["status"], "budget_exhausted")
        self.assertEqual(value["stop_reason"], "heartbeat gap budget exhausted")

    def test_late_draft_is_saved_as_terminal_safe_stop(self) -> None:
        value = manifest()
        confirm_without_git(value)
        value["last_heartbeat_at"] = (START + timedelta(minutes=19)).isoformat().replace(
            "+00:00", "Z"
        )
        self.assertFalse(
            advance_stage(
                value,
                stage="draft_saved",
                notes="best effort draft persisted",
                now=START + timedelta(minutes=21),
            )
        )
        self.assertEqual(value["stage"], "draft_saved")
        self.assertEqual(value["status"], "budget_exhausted")
        self.assertEqual(value["stop_reason"], "draft saved after pre-draft budget expired")

    def test_stage_order_cannot_skip_checkpoint(self) -> None:
        value = manifest()
        confirm_without_git(value)
        with self.assertRaisesRegex(ValueError, "next stage"):
            advance_stage(
                value,
                stage="normal_review_complete",
                now=START + timedelta(minutes=2),
            )

    def test_remote_confirmation_requires_pushed_manifest_commit(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            remote = root / "remote.git"
            work = root / "work"
            subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
            subprocess.run(["git", "init", "-b", "main", str(work)], check=True, capture_output=True)
            subprocess.run(
                ["git", "-C", str(work), "config", "user.email", "test@example.com"], check=True
            )
            subprocess.run(
                ["git", "-C", str(work), "config", "user.name", "Workflow Test"], check=True
            )
            subprocess.run(
                ["git", "-C", str(work), "remote", "add", "origin", str(remote)], check=True
            )
            subprocess.run(
                ["git", "-C", str(work), "switch", "-c", "add/eliminate-v5"],
                check=True,
                capture_output=True,
            )
            value = manifest()
            path = work / "audits" / "workflow_runs" / "eliminate" / "run-001.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(work), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(work), "commit", "-m", "Start eliminate workflow"],
                check=True,
                capture_output=True,
            )
            sha = subprocess.run(
                ["git", "-C", str(work), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            subprocess.run(
                ["git", "-C", str(work), "push", "-u", "origin", "add/eliminate-v5"],
                check=True,
                capture_output=True,
            )

            confirm_remote_checkpoint(
                value,
                manifest_path=path,
                commit_sha=sha,
                repo_root=work,
                now=START + timedelta(minutes=1),
            )

            self.assertTrue(value["remote_checkpoint"]["confirmed"])
            self.assertEqual(value["remote_checkpoint"]["commit_sha"], sha)
            self.assertEqual(value["stage"], "preflight_pushed")
            self.assertEqual(validate_manifest(value), [])

    def test_registered_body_preserving_review_demotion_needs_no_completed_run(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-b", "main", str(root)], check=True, capture_output=True)
            subprocess.run(
                ["git", "-C", str(root), "config", "user.email", "test@example.com"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "config", "user.name", "Workflow Test"],
                check=True,
            )
            entry = root / "entries" / "y" / "yield.md"
            audit = root / "audits" / "y" / "yield.json"
            registry = root / "audits" / "review_invalidations.json"
            entry.parent.mkdir(parents=True)
            audit.parent.mkdir(parents=True)
            entry.write_text(
                "---\nheadword: yield\nstatus: checked\nupdated_at: 2026-08-26\n"
                "checked: true\n---\nunchanged body\n",
                encoding="utf-8",
            )
            audit.write_text(
                json.dumps({"cycle_id": "run-1"}) + "\n", encoding="utf-8"
            )
            registry.write_text(
                json.dumps(
                    {
                        "schema_version": "review_invalidations_v1",
                        "reason_catalog": {"B1_term_not_in_example": "test"},
                        "invalidations": [],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-m", "base"],
                check=True,
                capture_output=True,
            )
            base = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            entry.write_text(
                "---\nheadword: yield\nstatus: needs_review\nupdated_at: 2026-08-27\n"
                "checked: false\n---\nunchanged body\n",
                encoding="utf-8",
            )
            audit.write_text(
                json.dumps(
                    {
                        "cycle_id": "run-1",
                        "invalidated_by": ["B1_term_not_in_example"],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            registry.write_text(
                json.dumps(
                    {
                        "schema_version": "review_invalidations_v1",
                        "reason_catalog": {"B1_term_not_in_example": "test"},
                        "invalidations": [
                            {
                                "status": "invalidated_run",
                                "entry_path": "entries/y/yield.md",
                                "run_id": "run-1",
                                "invalidated_by": ["B1_term_not_in_example"],
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(root), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-m", "invalidate"],
                check=True,
                capture_output=True,
            )
            head = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            changed = {
                "entries/y/yield.md",
                "audits/y/yield.json",
                "audits/review_invalidations.json",
            }
            self.assertTrue(
                _is_registered_review_demotion(
                    "entries/y/yield.md",
                    base=base,
                    head=head,
                    changed=changed,
                    repo_root=root,
                )
            )
            self.assertFalse(
                _is_registered_review_demotion(
                    "entries/y/yield.md",
                    base=base,
                    head=head,
                    changed=changed - {"audits/review_invalidations.json"},
                    repo_root=root,
                )
            )


class ReviewIngestFailureTests(unittest.TestCase):
    def test_repeated_ingestion_failures_stop_the_run(self) -> None:
        value = manifest()
        confirm_without_git(value)
        for attempt in range(1, MAX_REVIEW_INGEST_FAILURES):
            running = record_review_ingest_failure(
                value,
                stage="checker_passes",
                error="handoff response is missing: checker_passes.stage2.response.json",
                now=START + timedelta(minutes=attempt),
            )
            self.assertTrue(running)
            self.assertEqual(value["review_ingest_failures"]["count"], attempt)
            self.assertEqual(value["status"], "in_progress")
        running = record_review_ingest_failure(
            value,
            stage="checker_passes",
            error="handoff response is missing: checker_passes.stage2.response.json",
            now=START + timedelta(minutes=MAX_REVIEW_INGEST_FAILURES),
        )
        self.assertFalse(running)
        self.assertEqual(value["status"], "budget_exhausted")
        self.assertIn("checker_passes", value["stop_reason"])
        self.assertTrue(value["open_questions"])
        self.assertEqual(validate_manifest(value), [])

    def test_failed_ingestion_does_not_refresh_the_heartbeat(self) -> None:
        value = manifest()
        confirm_without_git(value)
        heartbeat = value["last_heartbeat_at"]
        self.assertTrue(
            record_review_ingest_failure(
                value, stage="cold_review", error="boom", now=START + timedelta(minutes=2)
            )
        )
        self.assertEqual(value["last_heartbeat_at"], heartbeat)

    def test_elapsed_budget_stops_the_run_even_while_ingestion_keeps_failing(self) -> None:
        value = manifest()
        confirm_without_git(value)
        limit = PROFILES["standard"]["max_elapsed_minutes"]
        running = record_review_ingest_failure(
            value,
            stage="checker_passes",
            error="boom",
            now=START + timedelta(minutes=limit + 1),
        )
        self.assertFalse(running)
        self.assertEqual(value["status"], "budget_exhausted")
        self.assertEqual(value["stop_reason"], "overall elapsed-time budget exhausted")

    def test_a_new_stage_and_a_successful_ingestion_reset_the_streak(self) -> None:
        value = manifest()
        confirm_without_git(value)
        record_review_ingest_failure(
            value, stage="checker_passes", error="boom", now=START + timedelta(minutes=2)
        )
        record_review_ingest_failure(
            value, stage="cold_review", error="boom", now=START + timedelta(minutes=3)
        )
        self.assertEqual(value["review_ingest_failures"]["stage"], "cold_review")
        self.assertEqual(value["review_ingest_failures"]["count"], 1)
        clear_review_ingest_failures(value)
        self.assertNotIn("review_ingest_failures", value)


if __name__ == "__main__":
    unittest.main()
