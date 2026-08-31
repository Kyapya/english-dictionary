from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from targeted_correction import build_record, validate_changed  # noqa: E402


BASE_ENTRY = """---
status: checked
checked: true
---
# sample

Original explanation.
"""


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def init_repo(root: Path) -> str:
    git(root, "init", "-b", "main")
    git(root, "config", "user.email", "test@example.com")
    git(root, "config", "user.name", "Targeted Correction Test")
    entry = root / "entries" / "s" / "sample.md"
    entry.parent.mkdir(parents=True)
    entry.write_text(BASE_ENTRY, encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-m", "Add checked sample")
    return git(root, "rev-parse", "HEAD")


def add_correction(root: Path, base: str, *, extra_file: bool = False) -> str:
    entry_path = "entries/s/sample.md"
    entry = root / entry_path
    head_text = BASE_ENTRY.replace("Original explanation.", "Corrected explanation.")
    entry.write_text(head_text, encoding="utf-8")
    diff_text = git(root, "diff", "--unified=3", base, "--", entry_path)
    record = build_record(
        entry_path=entry_path,
        base_text=BASE_ENTRY,
        head_text=head_text,
        diff_text=diff_text,
        user_request="Correct the explanation only.",
        reviewer="unit-test-reviewer",
        review_notes="Changed hunk checked against the request.",
        created_at="2026-08-31T05:30:00Z",
    )
    record_path = root / "audits" / "targeted_corrections" / "sample" / "20260831T053000Z.json"
    record_path.parent.mkdir(parents=True)
    record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if extra_file:
        (root / "README.md").write_text("unrelated\n", encoding="utf-8")
    git(root, "add", ".")
    git(root, "commit", "-m", "Apply targeted correction")
    return git(root, "rev-parse", "HEAD")


class TargetedCorrectionTests(unittest.TestCase):
    def test_checked_entry_with_bound_diff_record_passes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = init_repo(root)
            head = add_correction(root, base)
            self.assertEqual(validate_changed(base, head, root), [])

    def test_unrelated_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = init_repo(root)
            head = add_correction(root, base, extra_file=True)
            errors = validate_changed(base, head, root)
            self.assertTrue(any("may only change" in error for error in errors))

    def test_unchecked_base_cannot_create_targeted_record(self) -> None:
        unchecked = BASE_ENTRY.replace("status: checked", "status: review_ready").replace(
            "checked: true", "checked: false"
        )
        corrected = unchecked.replace("Original explanation.", "Corrected explanation.")
        with self.assertRaisesRegex(ValueError, "checked/final base"):
            build_record(
                entry_path="entries/s/sample.md",
                base_text=unchecked,
                head_text=corrected,
                diff_text="diff --git a/sample b/sample\n",
                user_request="Correct one sentence.",
                reviewer="unit-test-reviewer",
            )


if __name__ == "__main__":
    unittest.main()
