from __future__ import annotations

import copy
import hashlib
import json
import subprocess
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
    validate_invalidation_registry,
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
        cycle = manifest["current_cycle"]
        assert isinstance(cycle, dict)
        cycle["started_at"] = "2026-08-13T10:55:00Z"
        cycle["change_reason"] = "Initial content audit."
        cycle["body_revisions"][0]["created_at"] = "2026-08-13T10:55:00Z"  # type: ignore[index]
        revision_snapshot = self.root / cycle["body_revisions"][0]["snapshot_path"]  # type: ignore[index]
        revision_snapshot.parent.mkdir(parents=True, exist_ok=True)
        revision_snapshot.write_text(content_audit._entry_body(self.entry), encoding="utf-8")
        for check in cycle["regression_checks"]:  # type: ignore[union-attr]
            check["status"] = "not_applicable"
            check["notes"] = "Checked; this defect category does not apply to the fixture."
        targets = manifest["targets"]
        relations = manifest["relations"]
        assert isinstance(targets, list)
        assert isinstance(relations, list)
        target_ids = [target["id"] for target in targets]
        relation_ids = [relation["id"] for relation in relations]
        manifest["evidence"] = [
            {
                "id": "evidence:001",
                "source_type": "official_primary",
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
                    "locator_kind": "sense_number",
                    "source_detail": "Sense 1, definition and first example.",
                    "source_excerpt_or_summary": "The source defines the same lemma, sense, and frame used by this audit subject.",
                    "supports": f"Directly supports {subject_type} {subject_id}.",
                    "applicability": "Applies to the same lemma, sense, and frame.",
                    "support_type": "direct",
                    "counterexample_checked": True,
                    "counterexample_method": "Checked the neighbouring senses and frame restrictions.",
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
                "seal_version": content_audit.BLIND_SEAL_VERSION,
                "completed": True,
                "recorded_at": "2026-08-13T12:08:00Z",
                "sealed_at": "2026-08-13T12:08:30Z",
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
                    "semantic_assertions": [
                        {
                            "id": "final-candidate:001:A1",
                            "statement": "The sample is a part selected to represent a larger whole.",
                            "polarity": "must_hold",
                            "scope": "sense 1 definition and examples",
                        }
                    ],
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
            "evidence_checks": [],
            "blockers": [],
        }
        required_final_links = {
            link_id
            for result_key in (
                "target_results",
                "relation_results",
                "candidate_results",
                "blind_finding_results",
                "finding_results",
            )
            for result in manifest["final_review"][result_key]  # type: ignore[index]
            for link_id in result.get("evidence_link_ids_checked", [])
        }
        required_final_links.update(
            link_id
            for item_key in ("independent_candidates", "inventory_comparison")
            for item in manifest["final_review"][item_key]  # type: ignore[index]
            for link_id in item.get("evidence_link_ids", [])
        )
        manifest["final_review"]["evidence_checks"] = [  # type: ignore[index]
            {
                "id": link_id,
                "status": "pass",
                "claim_supported": True,
                "locator_verified": True,
                "applicability_confirmed": True,
                "contradiction_status": "no_contradiction",
                "notes": "The cited passage directly supports the scoped claim.",
            }
            for link_id in sorted(required_final_links)
        ]
        manifest["final_review"]["blind_review"]["output_sha256"] = (  # type: ignore[index]
            blind_review_sha256(manifest["final_review"])  # type: ignore[arg-type,index]
        )

        raw_dir = self.root / "audits" / "runs" / "s" / "sample" / "cycle-001"
        raw_dir.mkdir(parents=True, exist_ok=True)

        def add_raw(stage: str, review_key: str, *, blind: bool = False) -> None:
            review = manifest[review_key]
            execution = review["execution"]  # type: ignore[index]
            relative = Path("audits/runs/s/sample/cycle-001") / f"{stage}.json"
            raw: dict[str, object] = {
                "stage": stage,
                "run_id": execution["run_id"],
                "input_body_sha256": execution["input_body_sha256"],
            }
            if stage == "normal_review":
                for key in ("independent_candidates", "target_results", "relation_results"):
                    raw[key] = review[key]  # type: ignore[index]
            elif stage == "cold_review":
                raw["summary"] = review["summary"]  # type: ignore[index]
                raw["findings"] = review["findings"]  # type: ignore[index]
            elif stage == "final_blind":
                raw["provisional_decision"] = review["blind_review"]["provisional_decision"]  # type: ignore[index]
                raw["independent_candidates"] = [
                    {
                        key: candidate[key]
                        for key in (
                            "id",
                            "surface_form",
                            "frame",
                            "meaning",
                            "disposition",
                            "rationale",
                            "semantic_assertions",
                        )
                    }
                    for candidate in review["independent_candidates"]  # type: ignore[index]
                ]
                raw["article_findings"] = review["blind_review"]["article_findings"]  # type: ignore[index]
            elif stage == "final_review":
                raw["adjudication"] = {
                    "decision": review["decision"],  # type: ignore[index]
                    "inventory_comparison": review["inventory_comparison"],  # type: ignore[index]
                    "target_results": review["target_results"],  # type: ignore[index]
                    "relation_results": review["relation_results"],  # type: ignore[index]
                    "candidate_results": review["candidate_results"],  # type: ignore[index]
                    "blind_finding_results": review["blind_finding_results"],  # type: ignore[index]
                    "finding_results": review["finding_results"],  # type: ignore[index]
                    "evidence_checks": review["evidence_checks"],  # type: ignore[index]
                    "final_inventory_checks": manifest["semantic_gate"]["final_inventory_checks"],  # type: ignore[index]
                    "blockers": review["blockers"],  # type: ignore[index]
                }
            content = json.dumps(raw, ensure_ascii=False, sort_keys=True).encode()
            (self.root / relative).write_bytes(content)
            reference = {
                "path": relative.as_posix(),
                "sha256": hashlib.sha256(content).hexdigest(),
                "input_body_sha256": execution["input_body_sha256"],
                "prompt_sha256": execution["prompt_sha256"],
                "run_id": execution["run_id"],
                "context_id": execution["context_id"],
            }
            if blind:
                reference["sealed_output_sha256"] = review["blind_review"]["output_sha256"]  # type: ignore[index]
            cycle["raw_outputs"][stage] = reference  # type: ignore[index]

        add_raw("normal_review", "normal_review")
        add_raw("cold_review", "cold_review")
        add_raw("final_blind", "final_review", blind=True)
        add_raw("final_review", "final_review")
        return manifest

    def _write(self, manifest: dict[str, object]) -> None:
        self.audit.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _blind_checkpoint(self, manifest: dict[str, object]) -> dict[str, object]:
        checkpoint = copy.deepcopy(manifest)
        final = checkpoint["final_review"]
        final["reviewed_at"] = ""  # type: ignore[index]
        final["completed"] = False  # type: ignore[index]
        final["decision"] = "pending"  # type: ignore[index]
        final["execution"]["completed_at"] = ""  # type: ignore[index]
        final["execution"]["reconciliation_started_at"] = ""  # type: ignore[index]
        final["execution"]["reconciliation_input_artifacts"] = []  # type: ignore[index]
        for key in (
            "inventory_comparison",
            "blind_finding_results",
            "target_results",
            "relation_results",
            "candidate_results",
            "finding_results",
            "evidence_checks",
            "blockers",
        ):
            final[key] = []  # type: ignore[index]
        for candidate in final["independent_candidates"]:  # type: ignore[index]
            candidate["article_target_ids"] = []
            candidate["evidence_link_ids"] = []
        final["blind_review"]["sealed_at"] = ""  # type: ignore[index]
        final["blind_review"]["output_sha256"] = ""  # type: ignore[index]
        checkpoint["semantic_gate"]["final_inventory_checks"] = []  # type: ignore[index]
        checkpoint["current_cycle"]["raw_outputs"]["final_review"] = {}  # type: ignore[index]
        checkpoint["current_cycle"]["raw_outputs"]["final_blind"][  # type: ignore[index]
            "sealed_output_sha256"
        ] = ""
        return checkpoint

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout.strip()

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
        self.assertNotIn("sense_membership", relation_kinds)
        self.assertIn("example_translation", relation_kinds)
        self.assertIn("sense_definition_consistency", relation_kinds)
        self.assertIn("definition_lexical_relation_consistency", relation_kinds)
        self.assertIn("article_learning_risk", relation_kinds)

        lexical_relation = next(
            relation
            for relation in relations
            if relation["kind"] == "definition_lexical_relation_consistency"
        )
        lexical_kinds = {
            target["kind"]
            for target in targets
            if target["id"] in lexical_relation["target_ids"]
        }
        self.assertEqual(
            {"sense_boundary", "definition", "synonym"}, lexical_kinds
        )

    def test_cast_core_mappings_are_reduced_to_nineteen_explicit_checks(self) -> None:
        cast_entry = REPO_ROOT / "entries" / "c" / "cast.md"
        relations = extract_relations(extract_targets(cast_entry))
        core_relations = [
            relation
            for relation in relations
            if relation["kind"] in {"core_sense_mapping", "core_inventory_consistency"}
        ]
        self.assertEqual(len(core_relations), 19)
        self.assertLess(
            len([relation for relation in relations if relation["kind"] == "risk_sense_pair"]),
            153,
        )

    def test_complete_three_party_manifest_passes(self) -> None:
        self._write(self._complete_manifest())
        self.assertEqual(validate_manifest(self.entry, self.audit, self.root), [])

    def test_superseded_invalidation_preserves_old_body_hash(self) -> None:
        registry = self.root / "audits" / "review_invalidations.json"
        registry.write_text(
            json.dumps(
                {
                    "schema_version": "review_invalidations_v1",
                    "invalidations": [
                        {
                            "entry_path": "entries/s/sample.md",
                            "body_sha256": "a" * 64,
                            "status": "superseded",
                            "invalidated_at": "2026-08-16T12:00:00Z",
                            "reason": "A legacy PASS escaped a semantic defect.",
                            "defect_categories": [
                                "cross_section_internal_contradiction"
                            ],
                            "superseded_at": "2026-08-16T13:00:00Z",
                            "superseded_by_body_sha256": content_audit.body_sha256(
                                self.entry
                            ),
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.assertEqual(validate_invalidation_registry(self.root), [])

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

    def test_completed_v3_stage_requires_raw_output(self) -> None:
        manifest = self._complete_manifest()
        manifest["current_cycle"]["raw_outputs"]["cold_review"] = {}  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("raw_outputs.cold_review" in error for error in errors))

    def test_v3_evidence_link_requires_claim_level_locator(self) -> None:
        manifest = self._complete_manifest()
        manifest["evidence_links"][0]["source_detail"] = ""  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("source_detail" in error for error in errors))

    def test_v3_evidence_link_requires_source_excerpt_or_summary(self) -> None:
        manifest = self._complete_manifest()
        manifest["evidence_links"][0]["source_excerpt_or_summary"] = ""  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("source_excerpt_or_summary" in error for error in errors))

    def test_final_pass_requires_item_level_evidence_checks(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["evidence_checks"].pop()  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("final evidence checks are missing" in error for error in errors))

    def test_high_risk_claim_requires_two_sources_or_primary(self) -> None:
        manifest = self._complete_manifest()
        manifest["evidence"][0]["source_type"] = "dictionary"  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("two independent sources or one primary source" in error for error in errors))

    def test_normal_and_cold_may_reference_an_earlier_cycle_revision(self) -> None:
        manifest = self._complete_manifest()
        earlier_body = content_audit._entry_body(self.entry).replace(
            "可算名詞として使う。", "通常は可算名詞として使う。"
        )
        earlier_hash = hashlib.sha256(earlier_body.encode()).hexdigest()
        earlier_path = Path("audits/runs/s/sample/cycle-001/revision-000.md")
        (self.root / earlier_path).write_text(earlier_body, encoding="utf-8")
        revisions = manifest["current_cycle"]["body_revisions"]  # type: ignore[index]
        revisions.insert(  # type: ignore[union-attr]
            0,
            {
                "revision_id": "revision-000",
                "body_sha256": earlier_hash,
                "snapshot_path": earlier_path.as_posix(),
                "created_at": "2026-08-13T10:50:00Z",
                "reason": "Body read by the independent checks before correction.",
            },
        )
        for stage in ("normal_review", "cold_review"):
            manifest[stage]["execution"]["input_body_sha256"] = earlier_hash  # type: ignore[index]
            manifest["current_cycle"]["raw_outputs"][stage][  # type: ignore[index]
                "input_body_sha256"
            ] = earlier_hash
        self._write(manifest)
        self.assertEqual(validate_manifest(self.entry, self.audit, self.root), [])

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

    def test_blind_review_seal_detects_semantic_assertion_changes(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["independent_candidates"][0][  # type: ignore[index]
            "semantic_assertions"
        ][0]["statement"] = "Changed after the blind review."
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
        manifest = self._blind_checkpoint(self._complete_manifest())
        self._write(manifest)
        self.assertEqual(seal_blind_review(self.audit), [])
        sealed = json.loads(self.audit.read_text(encoding="utf-8"))
        self.assertEqual(
            sealed["final_review"]["blind_review"]["seal_version"],
            content_audit.BLIND_SEAL_VERSION,
        )
        self.assertTrue(sealed["final_review"]["blind_review"]["sealed_at"])
        self.assertEqual(
            sealed["final_review"]["blind_review"]["output_sha256"],
            blind_review_sha256(sealed["final_review"]),
        )

    def test_blind_review_cannot_be_sealed_after_reconciliation(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["blind_review"]["output_sha256"] = ""  # type: ignore[index]
        self._write(manifest)
        errors = seal_blind_review(self.audit)
        self.assertTrue(any("before final adjudication" in error for error in errors))
        self.assertTrue(any("before reconciliation" in error for error in errors))

    def test_blind_chronology_accepts_separate_checkpoint_commit(self) -> None:
        complete = self._complete_manifest()
        checkpoint = self._blind_checkpoint(complete)
        self._git("init", "-q")
        self._git("config", "user.name", "Audit Test")
        self._git("config", "user.email", "audit@example.invalid")
        self._git("add", "entries/s/sample.md")
        self._git("commit", "-qm", "base")
        base = self._git("rev-parse", "HEAD")

        self._write(checkpoint)
        self.assertEqual(seal_blind_review(self.audit), [])
        sealed_checkpoint = json.loads(self.audit.read_text(encoding="utf-8"))
        self._git(
            "add",
            "audits/s/sample.json",
            "audits/runs/s/sample/cycle-001/final_blind.json",
        )
        self._git("commit", "-qm", "seal blind review")

        complete["final_review"]["blind_review"] = sealed_checkpoint["final_review"][  # type: ignore[index]
            "blind_review"
        ]
        complete["current_cycle"]["raw_outputs"]["final_blind"] = sealed_checkpoint[  # type: ignore[index]
            "current_cycle"
        ]["raw_outputs"]["final_blind"]
        self._write(complete)
        self._git(
            "add",
            "audits/s/sample.json",
            "audits/runs/s/sample/cycle-001/final_review.json",
        )
        self._git("commit", "-qm", "record final reconciliation")
        head = self._git("rev-parse", "HEAD")
        self.assertEqual(
            content_audit._validate_blind_chronology_transition(
                self.audit, base, head, self.root
            ),
            [],
        )

    def test_blind_chronology_rejects_single_commit_finalization(self) -> None:
        complete = self._complete_manifest()
        self._git("init", "-q")
        self._git("config", "user.name", "Audit Test")
        self._git("config", "user.email", "audit@example.invalid")
        self._git("add", "entries/s/sample.md")
        self._git("commit", "-qm", "base")
        base = self._git("rev-parse", "HEAD")
        self._write(complete)
        self._git(
            "add",
            "audits/s/sample.json",
            "audits/runs/s/sample/cycle-001/final_blind.json",
        )
        self._git("commit", "-qm", "blind and final together")
        head = self._git("rev-parse", "HEAD")
        errors = content_audit._validate_blind_chronology_transition(
            self.audit, base, head, self.root
        )
        self.assertTrue(any("pre-reconciliation checkpoint" in error for error in errors))

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
        manifest["current_cycle"]["raw_outputs"]["final_blind"][  # type: ignore[index]
            "sealed_output_sha256"
        ] = manifest["final_review"]["blind_review"]["output_sha256"]  # type: ignore[index]
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
                "scope_anchors": [
                    {
                        "id": "finding:hold:A1",
                        "exact_quote": "全体の性質を示すために取り出した一部。",
                        "location_hint": "Sense 1 definition",
                    }
                ],
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
                "locator_kind": "sense_number",
                "source_detail": "Sense 1 definition.",
                "source_excerpt_or_summary": "The compared source scopes remain in conflict.",
                "supports": "Supports keeping this finding on hold.",
                "applicability": "Applies to the disputed sense boundary.",
                "support_type": "context",
                "counterexample_checked": True,
                "counterexample_method": "Compared the conflicting source scopes.",
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
                "scope_anchor_results": [
                    {
                        "id": "finding:hold:A1",
                        "status": "not_applicable",
                        "affected_target_ids": [],
                        "article_queries": [],
                        "notes": "The unresolved finding was not treated as confirmed.",
                    }
                ],
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
            "locator_kind": "sense_number",
            "source_detail": "Sense 1 definition.",
            "source_excerpt_or_summary": "The source supports a narrower definition.",
            "supports": "Supports the finding as stated.",
            "applicability": "Applies to the reviewed definition.",
            "support_type": "direct",
            "counterexample_checked": True,
            "counterexample_method": "Checked neighbouring senses.",
            "counterexample_result": "No counterexample defeats the finding.",
        }
        resolution_link = {
            "id": "link:resolution",
            "subject_type": "resolution",
            "subject_id": "finding:001",
            "evidence_id": "evidence:001",
            "claim": "The required correction follows from the cited definition.",
            "locator": "sample entry, relevant definition",
            "locator_kind": "sense_number",
            "source_detail": "Sense 1 definition.",
            "source_excerpt_or_summary": "The source supports the required correction.",
            "supports": "Supports the recorded resolution.",
            "applicability": "Applies to the corrected scope.",
            "support_type": "direct",
            "counterexample_checked": True,
            "counterexample_method": "Checked neighbouring senses.",
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
                "scope_anchors": [
                    {
                        "id": "finding:001:A1",
                        "exact_quote": "全体の性質を示すために取り出した一部。",
                        "location_hint": "Sense 1 definition",
                    }
                ],
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
                "scope_anchor_results": [
                    {
                        "id": "finding:001:A1",
                        "status": "corrected",
                        "affected_target_ids": [target_id],
                        "article_queries": ["全体の性質"],
                        "notes": "Mapped the quoted definition to its current target.",
                    }
                ],
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

    def test_changed_body_cannot_rewrite_a_completed_cycle_in_place(self) -> None:
        base_manifest = self._complete_manifest()
        base_audit = (
            json.dumps(base_manifest, ensure_ascii=False, indent=2) + "\n"
        ).encode()
        base_entry = ENTRY_TEXT.encode()
        self.entry.write_text(
            ENTRY_TEXT.replace("全体の性質", "母集団の性質"), encoding="utf-8"
        )
        self._write(self._complete_manifest())

        def git_file_at(_ref: str, relative: str, _root: Path) -> bytes | None:
            if relative == "entries/s/sample.md":
                return base_entry
            if relative == "audits/s/sample.json":
                return base_audit
            return None

        with (
            patch.object(
                content_audit,
                "_git_changed_paths",
                return_value=["entries/s/sample.md", "audits/s/sample.json"],
            ),
            patch.object(content_audit, "_git_file_at", side_effect=git_file_at),
        ):
            errors = content_audit.validate_changed("base", "head", self.root)
        self.assertTrue(any("append an exact snapshot" in error for error in errors))
        self.assertTrue(any("new cycle_id" in error for error in errors))

    def test_start_cycle_archives_the_exact_previous_manifest(self) -> None:
        manifest = self._complete_manifest()
        self._write(manifest)
        previous_bytes = self.audit.read_bytes()
        self.entry.write_text(
            ENTRY_TEXT.replace("全体の性質", "母集団の性質"), encoding="utf-8"
        )
        errors = content_audit.start_review_cycle(
            self.entry,
            self.audit,
            "Correct the definition without rewriting prior evidence.",
            self.root,
        )
        self.assertEqual(errors, [])
        updated = json.loads(self.audit.read_text(encoding="utf-8"))
        record = updated["review_history"][-1]
        self.assertEqual(
            (self.root / record["snapshot_path"]).read_bytes(), previous_bytes
        )
        self.assertEqual(
            record["snapshot_sha256"], hashlib.sha256(previous_bytes).hexdigest()
        )
        self.assertEqual(updated["current_cycle"]["parent_cycle_id"], "cycle-001")
        self.assertEqual(updated["current_cycle"]["cycle_id"], "cycle-002")
        self.assertEqual(updated["body_sha256"], content_audit.body_sha256(self.entry))

    def test_add_revision_captures_the_new_body_without_rewriting_prior_snapshot(self) -> None:
        manifest = build_manifest(self.entry, self.root)
        first_revision = manifest["current_cycle"]["body_revisions"][0]  # type: ignore[index]
        first_snapshot = self.root / first_revision["snapshot_path"]
        first_snapshot.parent.mkdir(parents=True, exist_ok=True)
        first_snapshot.write_text(content_audit._entry_body(self.entry), encoding="utf-8")
        self._write(manifest)
        first_bytes = first_snapshot.read_bytes()
        self.entry.write_text(
            ENTRY_TEXT.replace("全体の性質", "母集団の性質"), encoding="utf-8"
        )
        errors = content_audit.add_body_revision(
            self.entry,
            self.audit,
            "Apply an adopted cold-review correction.",
            self.root,
        )
        self.assertEqual(errors, [])
        updated = json.loads(self.audit.read_text(encoding="utf-8"))
        revisions = updated["current_cycle"]["body_revisions"]
        self.assertEqual(len(revisions), 2)
        self.assertEqual(first_snapshot.read_bytes(), first_bytes)
        second_snapshot = self.root / revisions[-1]["snapshot_path"]
        self.assertEqual(
            second_snapshot.read_text(encoding="utf-8"),
            content_audit._entry_body(self.entry),
        )

    def test_deleted_audit_is_rejected_for_a_checked_entry(self) -> None:
        with patch.object(
            content_audit,
            "_git_changed_paths",
            return_value=["audits/s/sample.json"],
        ):
            errors = content_audit.validate_changed("base", "head", self.root)
        self.assertTrue(any("audit manifest not found" in error for error in errors))

    def test_sync_gate_rejects_checked_entry_without_audit(self) -> None:
        errors = content_audit.validate_sync([self.entry], self.root)
        self.assertTrue(any("audit manifest not found" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
