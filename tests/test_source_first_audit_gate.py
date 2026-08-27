from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.source_first_audit_gate import (
    PROFILES,
    _hydrate_generated_final_review,
    _is_non_entry_audit,
    _template,
    validate_manifest,
)


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


def valid_v2_manifest() -> dict:
    coverage = []
    facts_by_axis = {
        "lexical_senses": ["F1", "F2"],
        "part_of_speech_and_frames": ["F1"],
        "derived_and_related_forms": [],
        "specialist_and_legal_uses": [],
        "register_region_and_frequency": ["F2"],
        "pronunciation_and_etymology": [],
    }
    for axis, fact_ids in facts_by_axis.items():
        coverage.append(
            {
                "axis": axis,
                "status": "covered" if fact_ids else "not_applicable",
                "source_fact_ids": fact_ids,
                "notes": "Directly checked in selected sources." if fact_ids else "No separate claim for this axis.",
            }
        )
    return {
        "source_first_audit": {
            "version": "source_first_audit_v2",
            "profile": "standard",
            "profile_reason": "bounded default profile",
            "limits": copy.deepcopy(PROFILES["standard"]),
            "usage": {
                "sources_used": 2,
                "facts_used": 2,
                "research_rounds_used": 1,
                "post_cold_rechecks_used": 0,
                "final_attempts_used": 1,
            },
            "research_status": "complete",
            "stop_reason": "coverage_axes_closed",
            "open_questions": [],
            "inventory_completed_before_article_comparison": True,
            "inventory_completed_at": "2026-08-23T10:00:00+09:00",
            "article_comparison_started_at": "2026-08-23T10:05:00+09:00",
            "coverage_axes": coverage,
            "sources": [
                {
                    "id": "S1",
                    "locator": "dictionary-a",
                    "source_type": "dictionary",
                    "source_role": "general_lexicon",
                    "independence_group": "publisher-a",
                    "facts": [
                        {
                            "id": "F1",
                            "form": "example",
                            "kind": "sense",
                            "statement": "sense one",
                            "source_detail": "sense 1 definition",
                        }
                    ],
                },
                {
                    "id": "S2",
                    "locator": "dictionary-b",
                    "source_type": "dictionary",
                    "source_role": "general_lexicon",
                    "independence_group": "publisher-b",
                    "facts": [
                        {
                            "id": "F2",
                            "form": "example",
                            "kind": "register",
                            "statement": "formal register",
                            "source_detail": "register label",
                        }
                    ],
                },
            ],
            "source_union": [
                {
                    "id": "U1",
                    "source_fact_ids": ["F1", "F2"],
                    "canonical_statement": "sense one is formal",
                    "disposition": "included",
                    "rationale": "article claim",
                }
            ],
            "claim_units": [
                {
                    "id": "C1",
                    "union_ids": ["U1"],
                    "subject_form": "example",
                    "claim_type": "sense",
                    "statement": "example has a formal first sense",
                    "article_target_ids": ["definition:001", "register:001"],
                    "source_supports": [
                        {
                            "source_fact_id": "F1",
                            "support_summary": "Dictionary A directly defines the first sense.",
                        },
                        {
                            "source_fact_id": "F2",
                            "support_summary": "Dictionary B directly supplies the register label.",
                        },
                    ],
                }
            ],
        },
        "final_review": {
            "decision": "pass",
            "source_inventory_results": [
                {
                    "union_id": "U1",
                    "status": "pass",
                    "notes": "Compared the source union, claim, and direct article targets.",
                }
            ],
        },
    }


class SourceFirstAuditGateTests(unittest.TestCase):
    def test_escaped_defect_registry_is_not_an_entry_audit(self) -> None:
        self.assertTrue(_is_non_entry_audit(Path("audits/escaped_defects.json")))
        self.assertFalse(_is_non_entry_audit(Path("audits/a/apple.json")))

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

    def test_v2_valid_manifest_passes(self) -> None:
        self.assertEqual(validate_manifest(valid_v2_manifest(), require_current=True), [])

    def test_v2_rejects_unbounded_profile_values(self) -> None:
        data = valid_v2_manifest()
        data["source_first_audit"]["limits"]["max_sources"] = 100
        self.assertTrue(any("must equal 6" in e for e in validate_manifest(data)))

    def test_v2_requires_two_independent_general_sources(self) -> None:
        data = valid_v2_manifest()
        data["source_first_audit"]["sources"][1]["independence_group"] = "publisher-a"
        self.assertTrue(any("two independent" in e for e in validate_manifest(data)))

    def test_v2_complete_inventory_requires_a_research_round(self) -> None:
        data = valid_v2_manifest()
        data["source_first_audit"]["usage"]["research_rounds_used"] = 0
        self.assertTrue(any("at least one research round" in e for e in validate_manifest(data)))

    def test_v2_rejects_budget_exhausted_as_merge_complete(self) -> None:
        data = valid_v2_manifest()
        gate = data["source_first_audit"]
        gate["research_status"] = "budget_exhausted"
        gate["stop_reason"] = "fact budget reached"
        gate["open_questions"] = ["specialist boundary remains unresolved"]
        self.assertTrue(any("before merge" in e for e in validate_manifest(data)))
        self.assertFalse(
            any(
                "before merge" in e
                for e in validate_manifest(data, allow_incomplete=True)
            )
        )

    def test_empty_initialized_v2_is_valid_as_incomplete_progress(self) -> None:
        data = {
            "source_first_audit": _template("standard", "bounded default profile"),
            "final_review": {"source_inventory_results": []},
        }
        self.assertEqual([], validate_manifest(data, allow_incomplete=True))
        self.assertTrue(any("before merge" in e for e in validate_manifest(data)))

    def test_v2_does_not_duplicate_fact_and_target_lists_in_final_result(self) -> None:
        result = valid_v2_manifest()["final_review"]["source_inventory_results"][0]
        self.assertEqual(set(result), {"union_id", "status", "notes"})

    def test_v1_is_legacy_only_when_current_is_required(self) -> None:
        self.assertEqual(validate_manifest(valid_manifest()), [])
        self.assertTrue(
            any("source_first_audit_v2" in e for e in validate_manifest(valid_manifest(), require_current=True))
        )

    def test_generated_v4_hydrates_sha_verified_raw_final_results(self) -> None:
        base = valid_v2_manifest()
        raw_final = base["final_review"]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_path = root / "audits" / "runs" / "x" / "final_review.json"
            raw_path.parent.mkdir(parents=True)
            raw_path.write_text(
                json.dumps(raw_final, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            manifest = {
                "schema_version": "content_audit_v4",
                "source_first_audit": base["source_first_audit"],
                "final_decision": {"decision": "pass"},
                "raw_outputs": {
                    "final_review": {
                        "path": "audits/runs/x/final_review.json",
                        "sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest(),
                    }
                },
            }
            errors: list[str] = []
            hydrated = _hydrate_generated_final_review(
                manifest, errors, repo_root=root
            )
        self.assertEqual(errors, [])
        self.assertEqual(hydrated["final_review"], raw_final)
        self.assertEqual(
            validate_manifest(hydrated, require_current=True),
            [],
        )


if __name__ == "__main__":
    unittest.main()
