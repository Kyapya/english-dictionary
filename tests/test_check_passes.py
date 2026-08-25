from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_passes  # noqa: E402
import generate_audit_manifest  # noqa: E402


class CheckPassTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = check_passes.load_router()

    def test_all_twelve_content_categories_have_exactly_one_owner(self) -> None:
        self.assertEqual(check_passes.validate_router(self.router), [])
        assignments = [
            category
            for item in self.router["passes"]
            for category in item["taxonomy_ids"]
        ]
        self.assertEqual(len(assignments), 12)
        self.assertEqual(len(set(assignments)), 12)
        self.assertNotIn("finding_scope_transfer_loss", assignments)
        self.assertNotIn("raw_adjudication_manifest_divergence", assignments)

    def test_each_pass_spec_is_small_and_has_the_required_contract(self) -> None:
        for item in self.router["passes"]:
            with self.subTest(check_pass=item["id"]):
                path = REPO_ROOT / item["specification"]
                self.assertLessEqual(path.stat().st_size, 15_000)
                text = path.read_text(encoding="utf-8")
                for marker in (
                    "## 目的",
                    "## 担当タクソノミー分類",
                    "## 検査ルール",
                    "## 入力として受け取るセクション",
                    "## findingの出力スキーマ",
                    "taxonomy_id",
                    "location",
                    "severity",
                    "rationale",
                ):
                    self.assertIn(marker, text)

    def test_router_builds_section_limited_bundles(self) -> None:
        bundles = check_passes.build_bundles(
            REPO_ROOT / "entries" / "o" / "obvious.md"
        )
        self.assertEqual(len(bundles), 6)
        by_id = {bundle["pass_id"]: bundle for bundle in bundles}
        self.assertEqual(
            set(by_id["pronunciation"]["input_sections"]),
            {"pronunciation"},
        )
        self.assertEqual(
            set(by_id["translation"]["input_sections"]),
            {"definitions", "collocations_examples", "lexical_relations"},
        )
        serialized = json.dumps(bundles, ensure_ascii=False)
        self.assertNotIn("process_improvement/ACTIVE.md", serialized)
        self.assertNotIn('"front matter"', serialized)

    def test_pass_cannot_emit_another_pass_taxonomy(self) -> None:
        output = {
            "pass_id": "pronunciation",
            "findings": [
                {
                    "taxonomy_id": "sense_boundary_overlap",
                    "location": {
                        "section": "pronunciation",
                        "line_start": 1,
                        "line_end": 1,
                        "exact_quote": "x",
                    },
                    "severity": "blocking",
                    "rationale": "wrong owner",
                }
            ],
        }
        errors = check_passes.validate_pass_output(output, self.router)
        self.assertTrue(any("not owned" in error for error in errors))

    def test_known_obvious_and_assess_defect_types_remain_routed(self) -> None:
        known = {
            "obvious": {
                "regional_qualification",
                "sense_boundary_overlap",
                "technical_terminology_conventionality",
            },
            "assess": {
                "absolute_scope_counterexample",
                "sense_boundary_overlap",
                "technical_terminology_conventionality",
                "example_translation_alignment",
                "lexical_relation_mislabel",
                "compound_component_generalization",
                "pronunciation_symbol_explanation",
                "argument_slot_role_mismatch",
                "cross_section_internal_contradiction",
            },
        }
        owners = {
            category: item["id"]
            for item in self.router["passes"]
            for category in item["taxonomy_ids"]
        }
        for word, categories in known.items():
            with self.subTest(word=word):
                self.assertTrue(categories <= set(owners))
                self.assertTrue(all(owners[category] for category in categories))

    def test_known_defect_regression_locations_reach_their_owner_pass(self) -> None:
        cases = REPO_ROOT / "tests" / "fixtures" / "check_pass_v6_regressions.json"
        results = check_passes.replay_regression_cases(cases)
        self.assertEqual(len(results), 12)
        self.assertEqual({item["word"] for item in results}, {"obvious", "assess"})
        self.assertTrue(all(item["status"] == "PASS" for item in results))

    def test_body_digest_excludes_front_matter(self) -> None:
        source = REPO_ROOT / "entries" / "o" / "obvious.md"
        original = source.read_text(encoding="utf-8")
        modified = original.replace("status: final", "status: checked", 1)
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "obvious.md"
            candidate.write_text(modified, encoding="utf-8")
            before = check_passes.build_bundles(source)[0]["input_body_sha256"]
            after = check_passes.build_bundles(candidate)[0]["input_body_sha256"]
        self.assertEqual(before, after)

    def test_body_digest_matches_manifest_canonicalization(self) -> None:
        source = REPO_ROOT / "entries" / "o" / "obvious.md"
        checker_digest = check_passes.build_bundles(source)[0][
            "input_body_sha256"
        ]
        self.assertEqual(
            checker_digest,
            generate_audit_manifest.body_sha256(source),
        )


if __name__ == "__main__":
    unittest.main()
