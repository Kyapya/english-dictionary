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

        manifest = {
            "schema_version": "content_audit_v3",
            "entry_path": "entries/a/apple.md",
            "body_sha256": body_sha,
            "current_cycle": {
                "raw_outputs": {
                    "final_blind": {
                        "path": "audits/runs/a/apple/cycle-001/final_blind.json"
                    }
                }
            },
            "targets": [
                {"id": "definition:001"},
            ],
            "relations": [
                {"id": "core_sense_mapping:001"},
            ],
            "resolutions": [
                {
                    "id": "CR-001-001",
                    "status": "adopted",
                    "problem_confirmed": True,
                    "affected_target_ids": ["definition:001"],
                    "affected_relation_ids": ["core_sense_mapping:001"],
                    "semantic_invariant_ids": ["SC001"],
                    "resolved_on_body_sha256": body_sha,
                }
            ],
            "final_review": {
                "decision": "pass",
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
                    }
                ],
            },
            "semantic_gate": {
                "version": "semantic_resolution_v1",
                "body_sha256": body_sha,
                "constraints": [
                    {
                        "id": "SC001",
                        "source_type": "cold_finding",
                        "source_id": "CR-001-001",
                        "statement": "the repaired meaning relation must remain intact",
                        "polarity": "must_hold",
                        "scope": "definition and summaries",
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
                        "status": "pass",
                        "notes": "checked candidate semantics against the latest article",
                    }
                ],
            },
        }
        return temp, root, manifest

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


if __name__ == "__main__":
    unittest.main()
