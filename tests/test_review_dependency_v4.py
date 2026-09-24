from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from review_dependency_v4 import snapshot, invalidated, reuse_receipt
from review_validation import checker_finding_id, checker_findings_with_ids
from generate_audit_manifest import _source_gate_with_final_review_attempt
from tests.test_content_audit import ENTRY_TEXT


class ContentDependencies(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.entry = Path(self.temp.name) / "sample.md"
        self.entry.write_text(ENTRY_TEXT, encoding="utf-8")
        self.inventory = {"source_first_audit": {"sources": [], "source_union": [],
                                                    "claim_units": [], "usage": {"research_rounds_used": 1}}}

    def snap(self, inventory=None):
        return snapshot(self.entry, inventory or self.inventory, specification_sha256="a" * 64)

    def test_translation_revises_its_sense_without_invalidating_pronunciation(self):
        old = self.snap()
        self.entry.write_text(ENTRY_TEXT.replace("私たちはその材料の試料を調べた。", "私たちは材料の試料を調べた。"), encoding="utf-8")
        new = self.snap()
        plan = invalidated(old, new)
        self.assertFalse(plan["full_content_review"])
        self.assertTrue(any(x.startswith("sense:") for x in plan["invalidated_areas"]))
        self.assertIn("pronunciation", plan["reusable_areas"])
        raw = {"area_keys": old["areas"], "raw_response_path": "review.raw.json",
               "raw_response_sha256": "b" * 64}
        reused = reuse_receipt(raw, old, new, "pronunciation")
        self.assertEqual(reused["original_body_sha256"], old["body_sha256"])
        self.assertEqual(reused["current_body_sha256"], new["body_sha256"])
        with self.assertRaises(ValueError):
            reuse_receipt(raw, old, new, plan["invalidated_areas"][0])

    def test_metadata_only_is_free_and_fact_content_is_not(self):
        old = self.snap()
        updated = copy.deepcopy(self.inventory)
        updated["source_first_audit"]["usage"]["research_rounds_used"] = 2
        self.assertEqual(invalidated(old, self.snap(updated))["invalidated_areas"], [])
        # An attributed source fact is a dependency of the actual claim area.
        from content_audit import extract_targets
        target = next(t for t in extract_targets(self.entry) if t["sense"])
        updated["source_first_audit"].update({
            "sources": [{"id": "source", "locator": "https://example.com", "facts": [
                {"id": "fact", "statement": "Original assertion"}]}],
            "claim_units": [{"id": "claim", "article_target_ids": [target["id"]],
                             "source_supports": [{"source_fact_id": "fact"}]}]})
        with_source = self.snap(updated)
        revised = copy.deepcopy(updated)
        revised["source_first_audit"]["sources"][0]["facts"][0]["statement"] = "Revised assertion"
        changed = invalidated(with_source, self.snap(revised))
        self.assertTrue(any(x.startswith("sense:") for x in changed["invalidated_areas"]))
        self.assertIn("pronunciation", changed["reusable_areas"])

    def test_sense_split_is_broad(self):
        old = self.snap()
        self.entry.write_text(ENTRY_TEXT + "\n2. 【名詞】別の意味\n\n【日本語訳・定義】新しい語義。\n", encoding="utf-8")
        changed = invalidated(old, self.snap())
        self.assertTrue(changed["full_content_review"])
        self.assertIn("pronunciation", changed["invalidated_areas"])

    def test_ci_contracts_preserve_raw_and_inventory(self):
        finding = {"severity": "minor", "rationale": "A specific translation issue"}
        original = copy.deepcopy(finding)
        self.assertEqual(checker_finding_id("translation", finding),
                         checker_findings_with_ids("translation", [finding])[0]["id"])
        self.assertEqual(finding, original)
        source_gate = {"usage": {"final_attempts_used": 0}}
        review = {"decision": "pass", "reviewer": {"agent_id": "independent"},
                  "recorded_at": "2026-09-23T12:00:00+00:00"}
        derived = _source_gate_with_final_review_attempt(source_gate, review)
        self.assertEqual(source_gate["usage"]["final_attempts_used"], 0)
        self.assertEqual(derived["usage"]["final_attempts_used"], 1)
        self.assertEqual(_source_gate_with_final_review_attempt(derived, review), derived)


if __name__ == "__main__":
    unittest.main()
