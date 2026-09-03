from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from entry_workflow_guard import PROFILES, enforce_budget, new_manifest  # noqa: E402


START = datetime(2026, 9, 3, 0, 0, tzinfo=timezone.utc)


def post_draft_manifest() -> dict:
    value = new_manifest(
        headword="publicity",
        entry_path="entries/p/publicity.md",
        branch="add/publicity",
        base_sha="a" * 40,
        profile="extended",
        profile_reason="regression test for post-draft runtime behavior",
        run_id="publicity-runtime-regression",
        now=START,
    )
    confirmed_at = START + timedelta(minutes=1)
    value["remote_checkpoint"] = {
        "confirmed": True,
        "confirmed_at": confirmed_at.isoformat().replace("+00:00", "Z"),
        "commit_sha": "b" * 40,
    }
    value["stage"] = "draft_saved"
    value["stage_history"].extend(
        [
            {
                "stage": "preflight_pushed",
                "recorded_at": confirmed_at.isoformat().replace("+00:00", "Z"),
                "notes": "test remote checkpoint",
            },
            {
                "stage": "draft_saved",
                "recorded_at": (START + timedelta(minutes=2)).isoformat().replace(
                    "+00:00", "Z"
                ),
                "notes": "draft persisted",
            },
        ]
    )
    return value


class PostDraftRuntimeBudgetTests(unittest.TestCase):
    def test_live_post_draft_run_can_cross_elapsed_target(self) -> None:
        value = post_draft_manifest()
        limit = PROFILES["extended"]["max_elapsed_minutes"]
        heartbeat = START + timedelta(minutes=limit - 1)
        value["last_heartbeat_at"] = heartbeat.isoformat().replace("+00:00", "Z")

        self.assertTrue(
            enforce_budget(value, now=START + timedelta(minutes=limit + 1))
        )
        self.assertEqual(value["status"], "in_progress")
        self.assertEqual(value["stop_reason"], "")

    def test_stale_post_draft_run_does_not_stop_on_heartbeat(self) -> None:
        value = post_draft_manifest()
        limit = PROFILES["extended"]["max_elapsed_minutes"]
        heartbeat = START + timedelta(minutes=limit - 1)
        value["last_heartbeat_at"] = heartbeat.isoformat().replace("+00:00", "Z")

        self.assertTrue(
            enforce_budget(value, now=START + timedelta(minutes=limit + 11))
        )
        self.assertEqual(value["status"], "in_progress")
        self.assertEqual(value["stop_reason"], "")


if __name__ == "__main__":
    unittest.main()
