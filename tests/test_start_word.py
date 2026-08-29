from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import start_word


class StartWordGuardTests(unittest.TestCase):
    def test_in_progress_run_always_requires_resume(self) -> None:
        runs = [
            {
                "run_id": "run-1",
                "status": "in_progress",
                "stage": "checker_passes",
                "started_at": "2026-08-29T03:00:00Z",
            }
        ]
        status, blockers = start_word.blocking_runs(
            runs, allow_restart_after_budget_exhausted=True
        )
        self.assertEqual(status, "resume_required")
        self.assertEqual([item["run_id"] for item in blockers], ["run-1"])

    def test_budget_exhausted_requires_explicit_restart(self) -> None:
        runs = [
            {
                "run_id": "run-1",
                "status": "budget_exhausted",
                "stage": "preflight",
                "started_at": "2026-08-29T03:00:00Z",
            }
        ]
        status, blockers = start_word.blocking_runs(
            runs, allow_restart_after_budget_exhausted=False
        )
        self.assertEqual(status, "restart_confirmation_required")
        self.assertEqual(len(blockers), 1)

        status, blockers = start_word.blocking_runs(
            runs, allow_restart_after_budget_exhausted=True
        )
        self.assertIsNone(status)
        self.assertEqual(blockers, [])

    def test_older_failed_run_does_not_block_after_completion(self) -> None:
        runs = [
            {
                "run_id": "failed-old",
                "status": "budget_exhausted",
                "stage": "preflight",
                "started_at": "2026-08-29T02:00:00Z",
            },
            {
                "run_id": "completed-new",
                "status": "completed",
                "stage": "completed",
                "started_at": "2026-08-29T03:00:00Z",
            },
        ]
        status, blockers = start_word.blocking_runs(
            runs, allow_restart_after_budget_exhausted=False
        )
        self.assertIsNone(status)
        self.assertEqual(blockers, [])

    def test_only_fresh_start_is_guarded(self) -> None:
        headword, allow = start_word._new_start_args(["disorder", "--reviewer-mode", "handoff"])
        self.assertEqual(headword, "disorder")
        self.assertFalse(allow)

        headword, _ = start_word._new_start_args(
            ["--resume", "audits/workflow_runs/disorder/run.json"]
        )
        self.assertIsNone(headword)

        headword, _ = start_word._new_start_args(["--dry-run", "disorder"])
        self.assertIsNone(headword)

    def test_restart_flag_is_not_forwarded_to_run_word(self) -> None:
        self.assertEqual(
            start_word._forward_args(
                ["disorder", "--restart-after-budget-exhausted", "--profile", "standard"]
            ),
            ["disorder", "--profile", "standard"],
        )


if __name__ == "__main__":
    unittest.main()
