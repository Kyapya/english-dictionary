from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import measure_instruction_budget as budget  # noqa: E402


class InstructionBudgetTests(unittest.TestCase):
    def test_checked_in_measurement_matches_the_current_files(self) -> None:
        path = (
            REPO_ROOT
            / "process_improvement"
            / "records"
            / "process-refactor-v1.json"
        )
        self.assertEqual(budget.validate_record(path), [])

    def test_refactor_halves_per_word_instructions_and_bounds_each_execution(self) -> None:
        value = budget.measurement()
        self.assertEqual(value["before"]["required_instruction_bytes_per_word"], 167_869)
        self.assertLess(
            value["after"]["required_instruction_bytes_per_word"],
            value["before"]["required_instruction_bytes_per_word"] * 0.5,
        )
        self.assertLessEqual(
            value["after"]["max_instruction_bytes_in_one_execution"], 53_000
        )
        self.assertGreaterEqual(value["effect"]["percent_reduced_per_word"], 50)

    def test_no_checker_execution_receives_the_combined_pass_specs(self) -> None:
        value = budget.measurement()
        checker = [
            item
            for item in value["after"]["execution_bundles"]
            if str(item["execution"]).startswith("check_pass:")
        ]
        self.assertEqual(len(checker), 6)
        self.assertTrue(all(item["instruction_bytes"] <= 15_000 for item in checker))


if __name__ == "__main__":
    unittest.main()
