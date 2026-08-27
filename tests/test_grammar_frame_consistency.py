from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import validate_entry  # noqa: E402


class GrammarFrameConsistencyTests(unittest.TestCase):
    def test_yield_d3_and_d4_are_mechanically_detected(self) -> None:
        _, body = validate_entry._split_front_matter(
            (REPO_ROOT / "tests" / "fixtures" / "acceptance" / "yield_defective.md")
            .read_text(encoding="utf-8")
        )
        errors, _ = validate_entry.grammar_frame_diagnostics(
            body.splitlines(), "yield"
        )
        joined = "\n".join(errors)
        self.assertIn("yield oneself to 〈誘惑・感情〉", joined)
        self.assertIn("yield the right of way to 〈車・歩行者〉", joined)
        self.assertIn("yield precedence to 〈人・もの〉", joined)
        self.assertIn("yield the floor to 〈発言者〉", joined)

    def test_transitive_only_sense_rejects_prepositional_frame(self) -> None:
        errors, _ = validate_entry.grammar_frame_diagnostics(
            [
                "1. 【他動詞・試験】試験語義",
                "【文法パターン】testword to 〈人〉＝人に向かう",
            ],
            "testword",
        )
        self.assertTrue(any("transitive-only" in error for error in errors))

    def test_unclassified_pattern_is_only_a_warning(self) -> None:
        errors, warnings = validate_entry.grammar_frame_diagnostics(
            [
                "1. 【自動詞・試験】試験語義",
                "【文法パターン】refuse to testword＝拒む",
            ],
            "testword",
        )
        self.assertEqual(errors, [])
        self.assertTrue(warnings)


if __name__ == "__main__":
    unittest.main()
