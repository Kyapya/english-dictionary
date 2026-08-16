from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.semantic_resolution_gate import validate_manifest


def _body_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SemanticResolutionGateTests(unittest.TestCase):
    def _fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path, dict]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "entries" / "a").mkdir(parents=True)
        (root / "audits" / "runs" / "a" / "apple" / "cycle-001").mkdir(
            parents=True
        )
        entry_body = "＃意味・用法・関連表現\n1. 【名詞】test\n"
        entry = root / "entries" / "a" / "apple.md"
        entry.write_text(
            "---\nword: apple\n---\n" + entry_body,
            encoding="utf-8",
        )
        body_sha = _body_sha(entry_body.rstrip("\n"))

        assertion = {
            "id": "IC01:A1",
            "statement": "ordinary item delivery must not be generalized as this sense",
            "polarity": "must_not_hold",
            "scope": "definition and core image",
        }
        raw_blind = {
            "stage": "final_blind",
            "independent_candidates": [
                {
                    "id": "IC01",
                    "surface_form": "apple",
                    "frame": "apple in <context>",
                    "meaning": "test meaning",
                    "disposition": "included",
                    "rationale": "test rationale",
                    "semantic_assertions": [assertion],
                }
            ],
            "article_findings": [],
        }
        raw_path = (
            root
            / "audits"
            / "runs"
            / "a"
            / "apple"
            / "cycle-001"
            / "final_blind.json"
        )
        raw_path.write_text(json.dumps(raw_blind), encoding="utf-8")
        revision_path = (
            root
            / "audits"
            / "runs"
            / "a"
            / "apple"
            / "cycle-001"
            / "revision-001.md"
        )
        revision_path.write_text(entry_body.rstrip("\n"), encoding="utf-8")
        cold_finding = {
            "id": "CR-001-001",
            "location": "sense 1 heading",
            "severity": "high",
            "description": "the definition is overbroad",
            "reason": "the scope must be constrained",
            "suggested_direction": "narrow the statement",
            "scope_anchors": [
                {
                    "id": "CR-001-001:A1",
                    "exact_quote": "1. 【名詞】test",
                    "location_hint": "sense 1 heading",
                }
            ],
        }
        raw_cold_path = revision_path.with_name("cold_review.json")
        raw_cold_path.write_text(
            json.dumps(
                {
                    "stage": "cold_review",
                    "summary": "one finding",
                    "findings": [cold_finding],
                }
            ),
            encoding="utf-8",
        )

        manifest = {
            "schema_version": "content_audit_v3",
            "entry_path": "entries/a/apple.md",
            "body_sha256": body_sha,
            "current_cycle": {
                "body_revisions": [
                    {
                        "body_sha256": body_sha,
                        "snapshot_path": "audits/runs/a/apple/cycle-001/revision-001.md",
                    }
                ],
                "raw_outputs": {
                    "cold_review": {
                        "path": "audits/runs/a/apple/cycle-001/cold_review.json"
                    },
                    "final_blind": {
                        "path": "audits/runs/a/apple/cycle-001/final_blind.json"
                    },
                    "final_review": {
                        "path": "audits/runs/a/apple/cycle-001/final_review.json"
                    },
                }
            },
            "targets": [
                {"id": "definition:001", "text": "1. 【名詞】test"},
            ],
            "relations": [
                {
                    "id": "core_sense_mapping:001",
                    "target_ids": ["definition:001"],
                },
            ],
            "cold_review": {
                "completed": True,
                "summary": "one finding",
                "execution": {"input_body_sha256": body_sha},
                "findings": [cold_finding],
            },
            "resolutions": [
                {
                    "id": "CR-001-001",
                    "status": "adopted",
                    "problem_confirmed": True,
                    "affected_target_ids": ["definition:001"],
                    "affected_relation_ids": ["core_sense_mapping:001"],
                    "scope_anchor_results": [
                        {
                            "id": "CR-001-001:A1",
                            "status": "corrected",
                            "affected_target_ids": ["definition:001"],
                            "article_queries": ["delivery"],
                            "notes": "checked the anchored heading",
                        }
                    ],
                    "semantic_invariant_ids": ["SC001"],
                    "resolved_on_body_sha256": body_sha,
                }
            ],
            "final_review": {
                "decision": "pass",
                "inventory_comparison": [],
                "target_results": [],
                "relation_results": [],
                "candidate_results": [],
                "blind_finding_results": [],
                "evidence_checks": [],
                "blockers": [],
                "blind_review": {"article_findings": []},
                "independent_candidates": [
                    {
                        "id": "IC01",
                        "surface_form": "apple",
                        "frame": "apple in <context>",
                        "meaning": "test meaning",
                        "disposition": "included",
                        "rationale": "test rationale",
                        "article_target_ids": ["definition:001"],
                        "semantic_assertions": [assertion],
                    }
                ],
                "finding_results": [
                    {
                        "id": "CR-001-001",
                        "status": "pass",
                        "resolution_status": "resolved",
                        "verified_body_sha256": body_sha,
                        "verified_invariant_ids": ["SC001"],
                        "blast_radius_target_ids": ["definition:001"],
                        "blast_radius_relation_ids": ["core_sense_mapping:001"],
                        "blast_radius_queries_checked": ["delivery"],
                        "blast_radius_query_results": [
                            {
                                "query": "delivery",
                                "match_count": 0,
                                "matched_target_ids": [],
                            }
                        ],
                    }
                ],
            },
            "semantic_gate": {
                "version": "semantic_resolution_v2",
                "body_sha256": body_sha,
                "constraints": [
                    {
                        "id": "SC001",
                        "source_type": "cold_finding",
                        "source_id": "CR-001-001",
                        "statement": "the repaired meaning relation must remain intact",
                        "polarity": "must_hold",
                        "scope": "definition and summaries",
                        "source_anchor_ids": ["CR-001-001:A1"],
                        "affected_target_ids": ["definition:001"],
                        "affected_relation_ids": ["core_sense_mapping:001"],
                        "article_queries": ["delivery"],
                        "verified_on_body_sha256": body_sha,
                        "verification_notes": "checked the latest body",
                    }
                ],
                "final_inventory_checks": [
                    {
                        "candidate_id": "IC01",
                        "assertion_ids": ["IC01:A1"],
                        "checked_on_body_sha256": body_sha,
                        "article_target_ids_checked": ["definition:001"],
                        "article_relation_ids_checked": ["core_sense_mapping:001"],
                        "article_queries_checked": ["delivery"],
                        "article_query_results": [
                            {
                                "query": "delivery",
                                "match_count": 0,
                                "matched_target_ids": [],
                            }
                        ],
                        "status": "pass",
                        "notes": "checked candidate semantics against the latest article",
                    }
                ],
            },
        }
        raw_final_path = revision_path.with_name("final_review.json")
        final = manifest["final_review"]
        raw_final_path.write_text(
            json.dumps(
                {
                    "stage": "final_review",
                    "adjudication": {
                        "decision": final["decision"],
                        "inventory_comparison": final["inventory_comparison"],
                        "target_results": final["target_results"],
                        "relation_results": final["relation_results"],
                        "candidate_results": final["candidate_results"],
                        "blind_finding_results": final["blind_finding_results"],
                        "finding_results": final["finding_results"],
                        "evidence_checks": final["evidence_checks"],
                        "final_inventory_checks": manifest["semantic_gate"][
                            "final_inventory_checks"
                        ],
                        "blockers": final["blockers"],
                    },
                }
            ),
            encoding="utf-8",
        )
        return temp, root, manifest

    def _sync_final_raw(self, root: Path, manifest: dict) -> None:
        final = manifest["final_review"]
        raw_path = (
            root
            / "audits"
            / "runs"
            / "a"
            / "apple"
            / "cycle-001"
            / "final_review.json"
        )
        raw_path.write_text(
            json.dumps(
                {
                    "stage": "final_review",
                    "adjudication": {
                        "decision": final["decision"],
                        "inventory_comparison": final["inventory_comparison"],
                        "target_results": final["target_results"],
                        "relation_results": final["relation_results"],
                        "candidate_results": final["candidate_results"],
                        "blind_finding_results": final["blind_finding_results"],
                        "finding_results": final["finding_results"],
                        "evidence_checks": final["evidence_checks"],
                        "final_inventory_checks": manifest["semantic_gate"][
                            "final_inventory_checks"
                        ],
                        "blockers": final["blockers"],
                    },
                }
            ),
            encoding="utf-8",
        )

    def test_valid_manifest_passes(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
        )
        self.assertEqual([], errors)

    def test_auto_phase_allows_normal_handoff_before_final_blind(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest["final_review"] = {"decision": "pending"}
        manifest["current_cycle"]["raw_outputs"] = {
            "cold_review": manifest["current_cycle"]["raw_outputs"]["cold_review"]
        }
        manifest["semantic_gate"].pop("final_inventory_checks")
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
            phase="auto",
        )
        self.assertEqual([], errors)

    def test_final_phase_does_not_allow_pending_final_artifacts(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest["final_review"] = {"decision": "pending"}
        manifest["current_cycle"] = {"raw_outputs": {}}
        manifest["semantic_gate"].pop("final_inventory_checks")
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
            phase="final",
        )
        self.assertTrue(errors)

    def test_stale_resolution_hash_is_rejected(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest["resolutions"][0]["resolved_on_body_sha256"] = "old-body"
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
        )
        self.assertTrue(any("resolution CR-001-001 is stale" in error for error in errors))

    def test_final_blast_radius_cannot_omit_constraint_scope(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest["final_review"]["finding_results"][0][
            "blast_radius_queries_checked"
        ] = []
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
        )
        self.assertTrue(
            any("blast radius omits article queries" in error for error in errors)
        )

    def test_cold_finding_requires_quote_anchored_scope(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest["cold_review"]["findings"][0]["scope_anchors"] = []
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
        )
        self.assertTrue(any("requires at least one scope anchor" in error for error in errors))

    def test_final_query_counts_are_recomputed_from_latest_body(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest["final_review"]["finding_results"][0][
            "blast_radius_query_results"
        ][0]["match_count"] = 1
        self._sync_final_raw(root, manifest)
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
        )
        self.assertTrue(any("incorrect match_count" in error for error in errors))

    def test_included_candidate_must_recheck_incident_relations(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest["semantic_gate"]["final_inventory_checks"][0][
            "article_relation_ids_checked"
        ] = []
        self._sync_final_raw(root, manifest)
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
        )
        self.assertTrue(any("relations incident to mapped targets" in error for error in errors))

    def test_final_raw_output_cannot_hide_item_level_manifest_changes(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest["final_review"]["finding_results"][0]["status"] = "fail"
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
        )
        self.assertTrue(any("exactly match every item-level" in error for error in errors))

    def test_blind_assertions_must_exist_in_raw_blind_output(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        raw_path = (
            root
            / "audits"
            / "runs"
            / "a"
            / "apple"
            / "cycle-001"
            / "final_blind.json"
        )
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
        raw["independent_candidates"][0].pop("semantic_assertions")
        raw_path.write_text(json.dumps(raw), encoding="utf-8")
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
        )
        self.assertTrue(
            any("were not fixed in the sealed final_blind raw output" in error for error in errors)
        )

    def test_missing_gate_is_allowed_only_in_compat_mode(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest.pop("semantic_gate")
        strict = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
        )
        compat = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=False,
        )
        self.assertTrue(any("semantic_gate is required" in error for error in strict))
        self.assertEqual([], compat)

    def test_compat_mode_rejects_checked_v3_without_gate(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest.pop("semantic_gate")
        entry = root / "entries" / "a" / "apple.md"
        entry.write_text(
            "---\nword: apple\nstatus: checked\nchecked: true\n---\n"
            + "＃意味・用法・関連表現\n1. 【名詞】test\n",
            encoding="utf-8",
        )
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=False,
        )
        self.assertTrue(any("cannot keep a checked/final" in error for error in errors))

    def test_explicit_invalidation_allows_demoted_legacy_audit(self) -> None:
        temp, root, manifest = self._fixture()
        self.addCleanup(temp.cleanup)
        manifest.pop("semantic_gate")
        entry = root / "entries" / "a" / "apple.md"
        entry.write_text(
            "---\nword: apple\nstatus: needs_review\nchecked: false\n---\n"
            + "＃意味・用法・関連表現\n1. 【名詞】test\n",
            encoding="utf-8",
        )
        (root / "audits" / "review_invalidations.json").write_text(
            json.dumps(
                {
                    "schema_version": "review_invalidations_v1",
                    "invalidations": [
                        {
                            "entry_path": "entries/a/apple.md",
                            "body_sha256": manifest["body_sha256"],
                            "status": "invalidated",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        errors = validate_manifest(
            manifest,
            root / "audits" / "a" / "apple.json",
            repo_root=root,
            require_gate=True,
        )
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
