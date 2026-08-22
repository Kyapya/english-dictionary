from __future__ import annotations

import copy
import unittest

from scripts.source_first_audit_gate import validate_manifest


def valid_manifest() -> dict:
    return {
        "source_first_audit": {
            "version": "source_first_audit_v1",
            "inventory_completed_before_article_comparison": True,
            "inventory_completed_at": "2026-08-22T10:00:00+09:00",
            "article_comparison_started_at": "2026-08-22T10:05:00+09:00",
            "sources": [
                {
                    "id": "S1",
                    "locator": "dictionary-a",
                    "source_type": "dictionary",
                    "facts": [
                        {
                            "id": "F1",
                            "form": "example",
                            "kind": "sense",
                            "statement": "sense one",
                            "source_detail": "sense 1 definition",
                        },
                        {
                            "id": "F2",
                            "form": "examplee",
                            "kind": "derived_form",
                            "statement": "derived form role",
                            "source_detail": "derived entry",
                        },
                    ],
                },
                {
                    "id": "S2",
                    "locator": "dictionary-b",
                    "source_type": "dictionary",
                    "facts": [
                        {
                            "id": "F3",
                            "form": "example",
                            "kind": "sense",
                            "statement": "sense one",
                            "source_detail": "main definition",
                        }
                    ],
                },
            ],
            "source_union": [
                {
                    "id": "U1",
                    "source_fact_ids": ["F1", "F3"],
                    "canonical_statement": "sense one",
                    "disposition": "included",
                    "rationale": "same lexical sense",
                    "article_target_ids": ["definition:001"],
                },
                {
                    "id": "U2",
                    "source_fact_ids": ["F2"],
                    "canonical_statement": "derived form role",
                    "disposition": "integrated",
                    "rationale": "covered in word formation",
                    "article_target_ids": ["word_formation:001"],
                },
            ],
            "claim_units": [
                {
                    "id": "C1",
                    "subject_form": "example",
                    "claim_type": "sense",
                    "statement": "example has sense one",
                    "source_fact_ids": ["F1", "F3"],
                    "article_target_ids": ["definition:001"],
                    "source_supports": [
                        {"source_fact_id": "F1", "support_summary": "Dictionary A directly defines this sense."},
                        {"source_fact_id": "F3", "support_summary": "Dictionary B independently defines this sense."},
                    ],
                },
                {
                    "id": "C2",
                    "subject_form": "examplee",
                    "claim_type": "derived_form",
                    "statement": "examplee names the derived role",
                    "source_fact_ids": ["F2"],
                    "article_target_ids": ["word_formation:001"],
                    "source_supports": [
                        {"source_fact_id": "F2", "support_summary": "The dedicated derived entry defines this exact form."}
                    ],
                },
            ],
        },
        "final_review": {
            "decision": "pass",
            "source_inventory_results": [
                {
                    "union_id": "U1",
                    "source_fact_ids_checked": ["F1", "F3"],
                    "article_target_ids_checked": ["definition:001"],
                    "status": "pass",
                    "notes": "Directly compared both source facts with the article.",
                },
                {
                    "union_id": "U2",
                    "source_fact_ids_checked": ["F2"],
                    "article_target_ids_checked": ["word_formation:001"],
                    "status": "pass",
                    "notes": "Checked the exact derived form and its article target.",
                },
            ],
        },
    }


class SourceFirstAuditGateTests(unittest.TestCase):
    def test_valid_manifest_passes(self) -> None:
        self.assertEqual(validate_manifest(valid_manifest()), [])

    def test_inventory_must_precede_article_comparison(self) -> None:
        data = valid_manifest()
        data["source_first_audit"]["inventory_completed_at"] = "2026-08-22T10:10:00+09:00"
        self.assertTrue(any("before article comparison" in e for e in validate_manifest(data)))

    def test_derived_forms_cannot_be_grouped(self) -> None:
        data = valid_manifest()
        data["source_first_audit"]["sources"][0]["facts"][1]["form"] = "examplee/exampleor"
        self.assertTrue(any("exactly one form" in e for e in validate_manifest(data)))

    def test_every_source_fact_must_reach_union(self) -> None:
        data = valid_manifest()
        data["source_first_audit"]["source_union"][1]["source_fact_ids"] = []
        self.assertTrue(any("missing from source_union" in e for e in validate_manifest(data)))

    def test_claim_support_must_match_claim_facts(self) -> None:
        data = valid_manifest()
        data["source_first_audit"]["claim_units"][0]["source_supports"] = [
            {"source_fact_id": "F1", "support_summary": "Dictionary A directly defines this sense."}
        ]
        self.assertTrue(any("source_supports must cover" in e for e in validate_manifest(data)))

    def test_final_reviewer_must_check_source_union_directly(self) -> None:
        data = valid_manifest()
        data["final_review"]["source_inventory_results"] = data["final_review"]["source_inventory_results"][:1]
        self.assertTrue(any("missing union ids" in e for e in validate_manifest(data)))

    def test_pass_cannot_hide_failed_source_result(self) -> None:
        data = valid_manifest()
        data["final_review"]["source_inventory_results"][0]["status"] = "fail"
        self.assertTrue(any("final decision pass" in e for e in validate_manifest(data)))


if __name__ == "__main__":
    unittest.main()
