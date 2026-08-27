from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import queue_status  # noqa: E402


class QueueStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(
            (REPO_ROOT / "audits" / "escaped_defects.json").read_text()
        )
        self.taxonomy = json.loads(
            (REPO_ROOT / "audits" / "escaped_defect_taxonomy.json").read_text()
        )

    def test_checked_in_escaped_defects_are_stage_valid(self) -> None:
        self.assertEqual(
            queue_status.validate_escaped_defects(
                self.registry,
                self.taxonomy,
                runs_root=REPO_ROOT / "audits" / "runs",
            ),
            [],
        )

    def test_unknown_stage_and_duplicate_id_are_rejected(self) -> None:
        value = copy.deepcopy(self.registry)
        value["defects"][0]["expected_stage"] = "pronunciation"
        value["defects"][1]["id"] = value["defects"][0]["id"]
        errors = queue_status.validate_escaped_defects(
            value,
            self.taxonomy,
            runs_root=REPO_ROOT / "audits" / "runs",
        )
        self.assertTrue(any("not registered" in error for error in errors))
        self.assertTrue(any("duplicated" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
