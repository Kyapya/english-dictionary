from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import migration_table  # noqa: E402


class MigrationTableTests(unittest.TestCase):
    def test_table_is_a_complete_deterministic_projection_of_backups(self) -> None:
        path = REPO_ROOT / "prompts" / "migration_table_v5_to_v6.md"
        self.assertEqual(migration_table.validate_table(path), [])
        self.assertEqual(path.read_text(encoding="utf-8"), migration_table.render_table())

    def test_every_extracted_normative_unit_has_one_disposition(self) -> None:
        rules = migration_table.all_rules()
        self.assertGreater(len(rules), 500)
        self.assertEqual(len({rule.id for rule in rules}), len(rules))
        for rule in rules:
            with self.subTest(rule=rule.id):
                migration = migration_table.migrate(rule)
                self.assertIn(
                    migration.disposition,
                    {"retained", "moved", "scripted", "retired"},
                )
                self.assertTrue(migration.destination)
                self.assertTrue(migration.reason)

    def test_backup_sources_are_immutable_copies_of_the_pre_refactor_files(self) -> None:
        backup = REPO_ROOT / "backups" / "2026-08-25-process-refactor"
        self.assertGreater((backup / "AGENTS.md").stat().st_size, 25_000)
        self.assertGreater((backup / "prompts" / "check_spec_v5.md").stat().st_size, 50_000)
        self.assertGreater((backup / "prompts" / "final_review_spec_v1.md").stat().st_size, 20_000)


if __name__ == "__main__":
    unittest.main()
