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
from content_audit import build_manifest, extract_targets, validate_manifest  # noqa: E402


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
        assert isinstance(targets, list)
        target_ids = [target["id"] for target in targets]
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
        manifest["normal_review"] = {
            "role": "normal_checker",
            "reviewer_id": "normal-run-001",
            "reviewed_at": "2026-08-13T12:00:00Z",
            "completed": True,
            "independent_candidates": [
                {
                    "id": "candidate:001",
                    "surface_form": "sample",
                    "frame": "a sample of 〈名詞〉",
                    "meaning": "全体を表す一部",
                    "disposition": "included",
                    "article_target_ids": [target_ids[0]],
                    "rationale": "A current core use with independent support.",
                    "evidence_ids": ["evidence:001"],
                }
            ],
            "target_results": [
                {
                    "id": target["id"],
                    "status": "pass",
                    "notes": f"Checked {target['kind']} against its frame and context.",
                    "evidence_ids": ["evidence:001"]
                    if target["requires_evidence"]
                    else [],
                }
                for target in targets
            ],
        }
        manifest["cold_review"] = {
            "role": "cold_reviewer",
            "reviewer_id": "cold-run-001",
            "reviewed_at": "2026-08-13T12:05:00Z",
            "prompt_version": "cold_review_prompt_v1",
            "completed": True,
            "summary": "問題候補なし",
            "findings": [],
        }
        manifest["resolutions"] = []
        manifest["final_review"] = {
            "role": "final_adjudicator",
            "reviewer_id": "final-run-001",
            "reviewed_at": "2026-08-13T12:10:00Z",
            "completed": True,
            "body_sha256": manifest["body_sha256"],
            "decision": "pass",
            "target_results": [
                {
                    "id": target["id"],
                    "status": "pass",
                    "notes": f"Independently approved {target['kind']}.",
                    "evidence_checked": bool(target["requires_evidence"]),
                }
                for target in targets
            ],
            "candidate_results": [
                {
                    "id": "candidate:001",
                    "status": "pass",
                    "notes": "Inventory disposition and article mapping are supported.",
                    "evidence_checked": True,
                }
            ],
            "finding_results": [],
            "blockers": [],
        }
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

    def test_complete_three_party_manifest_passes(self) -> None:
        self._write(self._complete_manifest())
        self.assertEqual(validate_manifest(self.entry, self.audit, self.root), [])

    def test_missing_final_target_is_rejected(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["target_results"].pop()  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("final review is missing targets" in error for error in errors))

    def test_missing_normal_target_is_rejected(self) -> None:
        manifest = self._complete_manifest()
        manifest["normal_review"]["target_results"].pop()  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("normal review is missing targets" in error for error in errors))

    def test_missing_final_inventory_candidate_is_rejected(self) -> None:
        manifest = self._complete_manifest()
        manifest["final_review"]["candidate_results"] = []  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("final review is missing candidates" in error for error in errors))

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
        result["evidence_ids"] = []
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("requires at least one evidence id" in error for error in errors))

    def test_stale_body_approval_is_rejected(self) -> None:
        manifest = self._complete_manifest()
        self._write(manifest)
        self.entry.write_text(ENTRY_TEXT.replace("全体の性質", "母集団の性質"), encoding="utf-8")
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertTrue(any("body_sha256" in error for error in errors))

    def test_reviewer_roles_must_be_separate(self) -> None:
        manifest = copy.deepcopy(self._complete_manifest())
        manifest["final_review"]["reviewer_id"] = "normal-run-001"  # type: ignore[index]
        self._write(manifest)
        errors = validate_manifest(self.entry, self.audit, self.root)
        self.assertIn(
            "normal, cold, and final reviewer_id values must be distinct",
            errors,
        )

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
