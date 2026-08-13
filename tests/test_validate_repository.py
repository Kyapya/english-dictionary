from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from validate_repository import validate_repository  # noqa: E402


class ValidateRepositoryTests(unittest.TestCase):
    def test_checked_in_repository_is_consistent(self) -> None:
        self.assertEqual(validate_repository(REPO_ROOT), [])

    def test_review_ready_queue_row_cannot_claim_checked_true(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            entry = root / "entries" / "s" / "sample.md"
            entry.parent.mkdir(parents=True)
            entry.write_text(
                "---\n"
                "headword: sample\n"
                "status: review_ready\n"
                "prompt_version: entry_spec_v5\n"
                "checked: true\n"
                "---\n",
                encoding="utf-8",
            )
            queue = root / "queue" / "words.csv"
            queue.parent.mkdir(parents=True)
            queue.write_text(
                "headword,type,status,priority,file,prompt_version,model,created_at,"
                "updated_at,checked,notes\n"
                "sample,word,review_ready,1,entries/s/sample.md,entry_spec_v5,unknown,"
                "2026-08-13,2026-08-13,true,\n",
                encoding="utf-8",
            )
            errors = validate_repository(root)
        self.assertTrue(
            any(
                "review_ready is inconsistent with checked=true" in error
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
