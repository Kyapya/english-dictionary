from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import content_audit  # noqa: E402
from content_audit import (  # noqa: E402
    blind_review_sha256,
    build_manifest,
    extract_relations,
    extract_targets,
    seal_blind_review,
    validate_manifest,
)


ENTRY_TEXT = """---
headword: sample
type: word
status: checked
prompt_version: entry_spec_v5
model: unknown
created_at: 2026-08-13
updated_at: 2026-08-13
checked: true
tags: []
---

＃発音記号

米・英: /ˈsæmpəl/  

第1音節に強勢を置く。  

＃語源

ラテン語系の語にさかのぼる。  

＃意味・用法・関連表現

1. 【名詞】例、見本

【日本語訳・定義】全体の性質を示すために取り出した一部。  

【頻度】〈8/10〉  

【レジスター/領域】一般。  

【文法パターン】a sample of 〈名詞〉＝～の見本／take a sample＝試料を採取する。  

【コロケーション】

・a sample of 〈名詞〉  
用途: 全体から取り出した一部を示す。  
例: We examined a sample of the material.  
訳: 私たちはその材料の試料を調べた。  

【語法・注意】可算名詞として使う。  

【類義語】

・example  
定義: 説明のために示す例。  
頻度: 〈10/10〉  
違い: sampleより説明目的に広く使う。  
例: This is a good example.  
訳: これはよい例だ。  
"""


class ContentAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.entry = self.root / "entries" / "s" / "sample.md"
        self.entry.parent.mkdir(parents=True)
        self.entry.write_text(ENTRY_TEXT, encoding="utf-8")
        self.audit = self.root / "audits" / "s" / "sample.json"
        self.audit.parent.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _complete_manifest(self) -> dict[str, object]:
        manifest = build_manifest(self.entry, self.root)
        targets = manifest["targets"]
        relations = manifest["relations"]
        assert isinstance(targets, list)
        assert isinstance(relations, list)
        target_ids = [target["id"] for target in targets]
        relation_ids = [relation["id"] for relation in relations]
        manifest["evidence"] = [
            {
                "id": "evidence:001",
                "source_type": "dictionary",
                "citation": "Example Dictionary, sample",
                "locator": "sample entry",
                "supports": "The recorded form, grammar, and sense inventory.",
                "checked_at": "2026-08-13",
            }
        ]
        evidence_links: list[dict[str, object]] = []

        def add_link(subject_type: str, subject_id: str) -> str:
            link_id = f"link:{len(evidence_links) + 1:03d}"
            evidence_links.append(
                {
                    "id": link_id,
                    "subject_type": subject_type,
                    "subject_id": subject_id,
                    "evidence_id": "evidence:001",
                    "claim": f"Claim checked for {subject_type} {subject_id}.",
                    "locator": "sample entry, relevant definition and example",
                    "supports": f"Directly supports {subject_type} {subject_id}.",
                    "support_type": "direct",
                    "counterexample_checked": True,
                    "counterexample_result": "No contradictory current example was found.",
                }
            )
            return link_id

        target_links = {target_id: add_link("target", target_id) for target_id in target_ids}
        relation_links = {
            relation_id: add_link("relation", relation_id)
            for relation_id in relation_ids
        }
        normal_candidate_link = add_link("normal_candidate", "candidate:001")
        final_candidate_link = add_link("final_candidate", "final-candidate:001")
        comparison_link = add_link("inventory_comparison", "comparison:001")
        manifest["evidence_links"] = evidence_links
        manifest["normal_review"] = {
            "role": "normal_checker",
            "reviewer_id": "normal-run-001",
            "reviewed_at": "2026-08-13T12:00:00Z",
            "completed": True,
            "execution": {
                "run_id": "normal-run-001",
                "context_id": "normal-context-001",
                "started_at": "2026-08-13T11:00:00Z",
                "completed_at": "2026-08-13T12:00:00Z",
                "input_body_sha256": manifest["body_sha256"],
                "prompt_sha256": "a" * 64,
                "context_mode": "isolated",
                "input_artifacts": ["entry_body", "check_spec"],
            },
            "independent_candidates": [
                {
                    "id": "candidate:001",
                    "surface_form": "sample",
                    "frame": "a sample of 〈名詞〉",
                    "meaning": "全体を表す一部",
                    "disposition": "included",
                    "article_target_ids": [target_ids[0]],
                    "rationale": "A current core use with independent support.",
                    "evidence_link_ids": [normal_candidate_link],
                }
            ],
            "target_results": [
                {
                    "id": target["id"],
                    "status": "pass",
                    "notes": f"Checked {target['kind']} against its frame and context.",
                    "evidence_link_ids": [target_links[target["id"]]],
                }
                for target in targets
            ],
            "relation_results": [
                {
                    "id": relation["id"],
                    "status": "pass",
                    "notes": f"Checked cross-target relation {relation['kind']}.",
                    "evidence_link_ids": [relation_links[relation["id"]]],
                }
                for relation in relations
            ],
        }
        manifest["cold_review"] = {
            "role": "cold_reviewer",
            "reviewer_id": "cold-run-001",
            "reviewed_at": "2026-08-13T12:05:00Z",
            "prompt_version": "cold_review_prompt_v1",
            "completed": True,
            "execution": {
                "run_id": "cold-run-001",
                "context_id": "cold-context-001",
                "started_at": "2026-08-13T12:01:00Z",
                "completed_at": "2026-08-13T12:05:00Z",
                "input_body_sha256": manifest["body_sha256"],
                "prompt_sha256": "b" * 64,
                "context_mode": "context_free",
                "input_artifacts": ["entry_body", "cold_review_prompt"],
            },
            "summary": "問題候補なし",
            "findings": [],
        }
        manifest["resolutions"] = []
        manifest["final_review"] = {
            "role": "final_adjudicator",
            "reviewer_id": "final-run-001",
            "reviewed_at": "2026-08-13T12:10:00Z",
            "completed": True,
            "execution": {
                "run_id": "final-run-001",
                "context_id": "final-context-001",
                "started_at": "2026-08-13T12:06:00Z",
                "completed_at": "2026-08-13T12:10:00Z",
                "input_body_sha256": manifest["body_sha256"],
                "prompt_sha256": "c" * 64,
                "context_mode": "context_free",
                "input_artifacts": ["entry_body", "final_review_spec"],
                "reconciliation_started_at": "2026-08-13T12:09:00Z",
                "reconciliation_input_artifacts": [
                    "entry_body",
                    "final_review_spec",
                    "audit_manifest",
                    "evidence_sources",
                ],
            },
            "body_sha256": manifest["body_sha256"],
            "decision": "pass",
            "blind_review": {
                "completed": True,
                "recorded_at": "2026-08-13T12:08:00Z",
                "body_sha256": manifest["body_sha256"],
                "audit_visible": False,
                "provisional_decision": "pass",
                "article_findings": [],
                "output_sha256": "",
            },
            "independent_candidates": [
                {
                    "id": "final-candidate:001",
                    "surface_form": "sample",
                    "frame": "a sample of 〈名詞〉",
                    "meaning": "全体を表す一部",
                    "disposition": "included",
                    "article_target_ids": [target_ids[0]],
                    "rationale": "Independently identified before seeing the audit manifest.",
                    "evidence_link_ids": [final_candidate_link],
                }
            ],
            "inventory_comparison": [
                {
                    "id": "comparison:001",
                    "normal_candidate_ids": ["candidate:001"],
                    "final_candidate_ids": ["final-candidate:001"],
                    "comparison": "match",
                    "status": "pass",
                    "rationale": "Both independent inventories identify the same core frame.",
                    "evidence_link_ids": [comparison_link],
                }
            ],
            "blind_finding_results": [],
            "target_results": [
                {
                    "id": target["id"],
                    "status": "pass",
                    "notes": f"Independently approved {target['kind']}.",
                    "evidence_link_ids_checked": [target_links[target["id"]]],
                }
                for target in targets
            ],
            "relation_results": [
                {
                    "id": relation["id"],
                    "status": "pass",
                    "notes": f"Independently approved relation {relation['kind']}.",
                    "evidence_link_ids_checked": [relation_links[relation["id"]]],
                }
                for relation in relations
            ],
            "candidate_results": [
                {
                    "id": "candidate:001",
                    "status": "pass",
                    "notes": "Inventory disposition and article mapping are supported.",
                    "evidence_link_ids_checked": [normal_candidate_link],
                }
            ],
            "finding_results": [],
            "blockers": [],
        }
        manifest["final_review"]["blind_review"]["output_sha256"] = (  # type: ignore[index]
            blind_review_sha256(manifest["final_review"])  # type: ignore[arg-type,index]
        )
        return manifest

    def _write(self, manifest: dict[str, object]) -> None:
        self.audit.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_extracts_generic_review_units(self) -> None:
        targets = extract_targets(self.entry)
        kinds = [target["kind"] for target in targets]
        self.assertIn("pronunciation", kinds)
        self.assertIn("etymology", kinds)
        self.assertIn("definition", kinds)
        self.assertEqual(kinds.count("grammar_pattern"), 2)
        self.assertIn("collocation", kinds)
        self.assertIn("synonym", kinds)
        self.assertTrue(
            all(
                target["requires_evidence"]
                for target in targets
                if target["kind"]
                in {
                    "pronunciation",
                    "definition",
                    "grammar_pattern",
                    "collocation",
                    "usage_note",
                }
            )
        )
        relations = extract_relations(targets)
        relation_kinds = {relation["kind"] for relation in relations}
        self.assertIn("sense_membership", relation_kinds)
        self.assertIn("example_translation", relation_kinds)
        self.assertIn("article_learning_risk", relation_kinds)

    def test_complete_three_party_manifest_passes(self) -> None:
        self._write(self._complete_manifest())
        self.assertEqual(validate_manifest(self.entry, self.audit, self.root), [])

    def test_missing_final_target_is_rejected(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["target_results"].pop()  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("every generated target" in error for error in errors))

    def test_missing_normal_target_is_rejected(self) -> None:
        manifest = self._complete_manifest()
        manifest["normal_review"]["target_results"].pop()  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("every generated target" in error for error in errors))

    def test_missing_final_inventory_candidate_is_rejected(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["independent_candidates"] = []  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("independent inventory" in error for error in errors))

    def test_missing_final_relation_is_rejected(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["relation_results"].pop()  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("every generated relation" in error for error in errors))

    def test_missing_required_evidence_is_rejected(self) -> None:
        manifest = self._complete_manifest()
        required_id = next(
            target["id"]
            for target in manifest["targets"]  # type: ignore[index]
            if target["requires_evidence"]
        )
        result = next(
            item
            for item in manifest["normal_review"]["target_results"]  # type: ignore[index]
            if item["id"] == required_id
        )
        result["evidence_link_ids"] = []
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("requires at least one evidence link id" in error for error in errors))

    def test_stale_body_approval_is_rejected(self) -> None:
        manifest = self._complete_manifest()
        self._write(manifest)
        self.entry.write_text(ENTRY_TEXT.replace("全体の性質", "母集団の性質"), encoding="utf-8")
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("body_sha256" in error for error in errors))

    def test_reviewer_roles_must_be_separate(self) -> None:
        manifest = copy.deepcopy(self._complete_manifest())
        manifest["final_review"]["reviewer_id"] = "normal-run-001"  # type: ignore[index]
        manifest["final_review"]["execution"]["run_id"] = "normal-run-001"  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertIn(
            "normal, cold, and final execution.run_id values must be distinct",
            errors,
        )

    def test_review_contexts_must_be_separate(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["execution"]["context_id"] = "normal-context-001"  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertIn(
            "normal, cold, and final execution.context_id values must be distinct",
            errors,
        )

    def test_final_blind_review_cannot_see_audit(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["blind_review"]["audit_visible"] = True  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("audit_visible" in error for error in errors))

    def test_blind_review_seal_detects_later_changes(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["independent_candidates"][0]["meaning"] = "changed"  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("output_sha256" in error for error in errors))

    def test_reconciliation_ids_do_not_change_blind_seal(self) -> None:
        manifest = self._complete_manifest()
        before = manifest["final_review"]["blind_review"]["output_sha256"]  # type: ignore[index]
        manifest["final_review"]["independent_candidates"][0][  # type: ignore[index]
            "article_target_ids"
        ] = [manifest["targets"][-1]["id"]]  # type: ignore[index]
        manifest["final_review"]["independent_candidates"][0][  # type: ignore[index]
            "evidence_link_ids"
        ] = ["link:added-after-blind-review"]
        after = blind_review_sha256(manifest["final_review"])  # type: ignore[arg-type,index]
        self.assertEqual(after, before)

    def test_blind_review_can_be_sealed_before_reconciliation(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["blind_review"]["output_sha256"] = ""  # type: ignore[index]
        self._write(manifest)
        self.assertEqual(seal_blind_review(self.audit), [])
        sealed = json.loads(self.audit.read_text(encoding="utf-8"))
        self.assertEqual(
            sealed["final_review"]["blind_review"]["output_sha256"],
            blind_review_sha256(sealed["final_review"]),
        )

    def test_reconciliation_cannot_start_before_blind_output(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["execution"]["reconciliation_started_at"] = (  # type: ignore[index]
            "2026-08-13T12:07:00Z"
        )
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("reconciliation started before blind" in error for error in errors))

    def test_identical_notes_are_allowed(self) -> None:
        manifest = self._complete_manifest()
        for section in ("normal_review", "final_review"):
            for key in ("target_results", "relation_results"):
                for result in manifest[section][key]:  # type: ignore[index]
                    result["notes"] = "The same concise result is valid for these checks."
        self._write(manifest)
        self.assertEqual(validate_manifest(self.entry, self.audit, self.root), [])

    def test_reject_is_a_valid_completed_audit_state(self) -> None:
        manifest = self._complete_manifest()
        self.entry.write_text(
            ENTRY_TEXT.replace("status: checked", "status: needs_review").replace(
                "checked: true", "checked: false"
            ),
            encoding="utf-8",
        )
        manifest["final_review"]["decision"] = "reject"  # type: ignore[index]
        manifest["final_review"]["target_results"][0]["status"] = "fail"  # type: ignore[index]
        manifest["final_review"]["blind_review"]["provisional_decision"] = "reject"  # type: ignore[index]
        manifest["final_review"]["blind_review"]["output_sha256"] = blind_review_sha256(  # type: ignore[index]
            manifest["final_review"]  # type: ignore[arg-type,index]
        )
        manifest["final_review"]["blockers"] = [  # type: ignore[index]
            {
                "id": "blocker:001",
                "subject_id": manifest["targets"][0]["id"],  # type: ignore[index]
                "problem": "The reviewed claim is not supported.",
                "required_change": "Correct the claim and repeat final adjudication.",
            }
        ]
        self._write(manifest)
        self.assertEqual(validate_manifest(self.entry, self.audit, self.root), [])

    def test_hold_is_a_valid_externalized_pre_adjudication_state(self) -> None:
        manifest = self._complete_manifest()
        self.entry.write_text(
            ENTRY_TEXT.replace("status: checked", "status: needs_review").replace(
                "checked: true", "checked: false"
            ),
            encoding="utf-8",
        )
        manifest["final_review"] = build_manifest(self.entry, self.root)["final_review"]
        manifest["evidence_links"] = [  # type: ignore[index]
            link
            for link in manifest["evidence_links"]  # type: ignore[index]
            if link["subject_type"] not in {"final_candidate", "inventory_comparison"}
        ]
        manifest["cold_review"]["summary"] = "1件を追加確認のため保留"  # type: ignore[index]
        manifest["cold_review"]["findings"] = [  # type: ignore[index]
            {
                "id": "finding:hold",
                "location": "definition:001",
                "description": "The current sources conflict.",
                "reason": "The scope cannot yet be determined.",
                "suggested_direction": "Check an additional authoritative source.",
                "evidence_link_ids": [],
            }
        ]
        manifest["evidence_links"].append(  # type: ignore[union-attr]
            {
                "id": "link:hold",
                "subject_type": "resolution",
                "subject_id": "finding:hold",
                "evidence_id": "evidence:001",
                "claim": "The available sources leave the scope unresolved.",
                "locator": "sample entry, relevant definition",
                "supports": "Supports keeping this finding on hold.",
                "support_type": "context",
                "counterexample_checked": True,
                "counterexample_result": "The conflict remains unresolved.",
            }
        )
        manifest["resolutions"] = [
            {
                "id": "finding:hold",
                "status": "hold",
                "problem_confirmed": False,
                "rationale": "Current evidence is conflicting.",
                "required_changes": [],
                "affected_target_ids": [],
                "affected_relation_ids": [],
                "implemented_changes": [],
                "remaining_risk": "The claim may be too broad.",
                "evidence_link_ids": ["link:hold"],
            }
        ]
        self._write(manifest)
        self.assertEqual(validate_manifest(self.entry, self.audit, self.root), [])

    def test_adopted_finding_requires_structured_implementation_record(self) -> None:
        manifest = self._complete_manifest()
        target_id = manifest["targets"][0]["id"]  # type: ignore[index]
        finding_link = {
            "id": "link:finding",
            "subject_type": "finding",
            "subject_id": "finding:001",
            "evidence_id": "evidence:001",
            "claim": "The cold finding identifies a real content issue.",
            "locator": "sample entry, relevant definition",
            "supports": "Supports the finding as stated.",
            "support_type": "direct",
            "counterexample_checked": True,
            "counterexample_result": "No counterexample defeats the finding.",
        }
        resolution_link = {
            "id": "link:resolution",
            "subject_type": "resolution",
            "subject_id": "finding:001",
            "evidence_id": "evidence:001",
            "claim": "The required correction follows from the cited definition.",
            "locator": "sample entry, relevant definition",
            "supports": "Supports the recorded resolution.",
            "support_type": "direct",
            "counterexample_checked": True,
            "counterexample_result": "No contradictory current evidence was found.",
        }
        manifest["evidence_links"].extend([finding_link, resolution_link])  # type: ignore[union-attr]
        manifest["cold_review"]["summary"] = "1件の問題候補を検出"  # type: ignore[index]
        manifest["cold_review"]["findings"] = [  # type: ignore[index]
            {
                "id": "finding:001",
                "location": "definition:001",
                "description": "The definition is too broad.",
                "reason": "The cited source supports a narrower scope.",
                "suggested_direction": "Narrow the definition.",
                "evidence_link_ids": ["link:finding"],
            }
        ]
        manifest["resolutions"] = [
            {
                "id": "finding:001",
                "status": "adopted",
                "problem_confirmed": True,
                "rationale": "The issue is supported by the cited definition.",
                "required_changes": ["Narrow the definition."],
                "affected_target_ids": [target_id],
                "affected_relation_ids": [],
                "implemented_changes": [],
                "remaining_risk": "No remaining risk after the recorded correction.",
                "evidence_link_ids": ["link:resolution"],
            }
        ]
        manifest["final_review"]["finding_results"] = [  # type: ignore[index]
            {
                "id": "finding:001",
                "finding_validity": "valid",
                "resolution_status": "resolved",
                "status": "pass",
                "verified_changes": ["Verified the narrowed definition."],
                "unresolved_problem": "",
                "notes": "The required change is present in the current body.",
                "evidence_link_ids_checked": ["link:resolution"],
            }
        ]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("implemented_changes" in error for error in errors))

    def test_changed_checked_entry_requires_a_complete_audit(self) -> None:
        with patch.object(
            content_audit,
            "_git_changed_paths",
            return_value=["entries/s/sample.md"],
        ):
            errors = content_audit.validate_changed("base", "head", self.root)
        self.assertTrue(any("audit manifest not found" in error for error in errors))

    def test_changed_checked_entry_cannot_bypass_audit_with_an_old_version(self) -> None:
        self.entry.write_text(
            ENTRY_TEXT.replace("entry_spec_v5", "entry_spec_v4"),
            encoding="utf-8",
        )
        with patch.object(
            content_audit,
            "_git_changed_paths",
            return_value=["entries/s/sample.md"],
        ):
            errors = content_audit.validate_changed("base", "head", self.root)
        self.assertTrue(any("audit manifest not found" in error for error in errors))

    def test_changed_audit_is_validated_against_its_entry(self) -> None:
        self._write(self._complete_manifest())
        with patch.object(
            content_audit,
            "_git_changed_paths",
            return_value=["audits/s/sample.json"],
        ):
            errors = content_audit.validate_changed("base", "head", self.root)
        self.assertEqual(errors, [])

    def test_deleted_audit_is_rejected_for_a_checked_entry(self) -> None:
        with patch.object(
            content_audit,
            "_git_changed_paths",
            return_value=["audits/s/sample.json"],
        ):
            errors = content_audit.validate_changed("base", "head", self.root)
        self.assertTrue(any("audit manifest not found" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
