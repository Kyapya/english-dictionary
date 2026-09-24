from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_passes


class CompactTaxonomyCoverage(unittest.TestCase):
    def test_all_legacy_content_taxonomy_ids_are_owned_by_a_or_b(self):
        router = check_passes.load_router(ROOT / "prompts/check_router_v6.md")
        required = {tax for item in router["passes"] for tax in item["taxonomy_ids"]}
        compact = json.loads((ROOT / "prompts/compact_review_contract_v1.json").read_text(encoding="utf-8"))
        self.assertEqual(set(compact["legacy_taxonomy_map"]), required)
        self.assertEqual(set(compact["legacy_taxonomy_map"].values()), {"A", "B"})
        for axis in ("pronunciation_symbol_explanation", "example_sense_attribution_mismatch",
                     "argument_slot_role_mismatch", "regional_qualification", "lexical_relation_mislabel"):
            self.assertIn(axis, compact["legacy_taxonomy_map"])


if __name__ == "__main__":
    unittest.main()
