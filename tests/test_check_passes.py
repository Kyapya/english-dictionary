from __future__ import annotations

import json
import hashlib
import re
import sys
import tempfile
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

    def test_all_thirteen_content_categories_have_exactly_one_owner(self) -> None:
        self.assertEqual(check_passes.validate_router(self.router), [])
        assignments = [
            category
            for item in self.router["passes"]
            for category in item["taxonomy_ids"]
        ]
        self.assertEqual(len(assignments), 13)
        self.assertEqual(len(set(assignments)), 13)
        self.assertNotIn("finding_scope_transfer_loss", assignments)
        self.assertNotIn("raw_adjudication_manifest_divergence", assignments)

    def test_each_pass_spec_has_the_required_contract(self) -> None:
        for item in self.router["passes"]:
            with self.subTest(check_pass=item["id"]):
                path = REPO_ROOT / item["specification"]
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

    def test_frame_relation_routes_to_v7_in_table_and_json(self) -> None:
        frame = next(
            item for item in self.router["passes"]
            if item["id"] == "frame-relation"
        )
        self.assertEqual(
            frame["specification"], "prompts/check_pass_frame_relation_v7.md"
        )
        rows = check_passes._router_table_rows(
            REPO_ROOT / "prompts" / "check_router_v6.md"
        )
        frame_row = next(item for item in rows if item["id"] == "frame-relation")
        self.assertEqual(frame_row["specification"], frame["specification"])

    def test_router_builds_section_limited_bundles(self) -> None:
        bundles = check_passes.build_bundles(
            REPO_ROOT / "entries" / "o" / "obvious.md"
        )
        self.assertEqual(len(bundles), 7)
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

    def test_example_attribution_blind_reclassification_fixture(self) -> None:
        entry = (
            REPO_ROOT
            / "tests"
            / "fixtures"
            / "example_attribution_polysemous.md"
        )
        record = json.loads(
            (
                REPO_ROOT
                / "tests"
                / "fixtures"
                / "example_attribution_polysemous_blind_record.json"
            ).read_text(encoding="utf-8")
        )
        expected = json.loads(
            (
                REPO_ROOT
                / "tests"
                / "fixtures"
                / "example_attribution_polysemous_expected.json"
            ).read_text(encoding="utf-8")
        )
        request = next(
            item
            for item in check_passes.build_bundles(entry)
            if item["pass_id"] == "example-attribution"
        )
        masked_examples = request["input_sections"]["collocations_examples"]
        self.assertTrue(
            all("assigned_sense_id" not in item for item in masked_examples)
        )
        serialized_examples = json.dumps(masked_examples, ensure_ascii=False)
        self.assertNotIn("用途:", serialized_examples)
        self.assertNotIn("【語法・注意】", serialized_examples)
        self.assertTrue(
            all(
                re.fullmatch(r"ex-[0-9a-f]{12}", item["example_id"])
                and "line" not in item
                for item in masked_examples
            )
        )

        source_orders = []
        for seed in ("shuffle-a", "shuffle-b"):
            seeded_request = next(
                item
                for item in check_passes.build_bundles(entry, blind_seed=seed)
                if item["pass_id"] == "example-attribution"
            )
            seeded_alignment = check_passes.build_example_attribution_alignment_key(
                entry, blind_seed=seed
            )
            sources = {
                item["example_id"]: item["source_example_id"]
                for item in seeded_alignment["examples"]
            }
            source_orders.append(
                [
                    sources[item["example_id"]]
                    for item in seeded_request["input_sections"][
                        "collocations_examples"
                    ]
                ]
            )
        self.assertNotEqual(source_orders[0], source_orders[1])

        alignment_key = check_passes.build_example_attribution_alignment_key(entry)
        self.assertTrue(
            all("assigned_sense_id" in item for item in alignment_key["examples"])
        )
        self.assertEqual(len(alignment_key["sense_usage_notes"]), 3)
        output = check_passes.reconcile_example_attribution(
            request,
            record,
            alignment_key,
            aligned_at="2026-08-26T10:01:00+09:00",
        )
        by_anchor = {
            item["anchor"]["line_start"]: item["example_id"]
            for item in alignment_key["examples"]
        }
        finding_ids = {
            by_anchor[item["location"]["line_start"]]
            for item in output["findings"]
        }
        self.assertEqual(finding_ids, set(expected["finding_example_ids"]))
        self.assertTrue(
            set(expected["normal_example_ids"]).isdisjoint(finding_ids)
        )
        self.assertTrue(
            all(
                item["taxonomy_id"] == expected["taxonomy_id"]
                and item["severity"] == expected["severity"]
                for item in output["findings"]
            )
        )
        self.assertEqual(
            check_passes.validate_pass_output(
                output, self.router, entry_path=entry
            ),
            [],
        )

    def test_example_attribution_rejects_alignment_before_blind_record(self) -> None:
        entry = REPO_ROOT / "tests" / "fixtures" / "example_attribution_polysemous.md"
        record = json.loads(
            (
                REPO_ROOT
                / "tests"
                / "fixtures"
                / "example_attribution_polysemous_blind_record.json"
            ).read_text(encoding="utf-8")
        )
        request = next(
            item
            for item in check_passes.build_bundles(entry)
            if item["pass_id"] == "example-attribution"
        )
        with self.assertRaisesRegex(ValueError, "later than"):
            check_passes.reconcile_example_attribution(
                request,
                record,
                check_passes.build_example_attribution_alignment_key(entry),
                aligned_at="2026-08-26T09:59:00+09:00",
            )

    def test_antonym_axis_acceptance_detects_change_without_false_blockers(self) -> None:
        fixture_dir = REPO_ROOT / "tests" / "fixtures" / "acceptance"
        entry = fixture_dir / "conservation_4f26c07b_defective.md"
        blind_record = json.loads(
            (fixture_dir / "conservation_antonym_axis_blind_record.json").read_text(
                encoding="utf-8"
            )
        )
        stored_stage2 = json.loads(
            (fixture_dir / "conservation_antonym_axis_stage2_request.json").read_text(
                encoding="utf-8"
            )
        )
        adjudication = json.loads(
            (
                fixture_dir
                / "conservation_antonym_axis_adjudication_record.json"
            ).read_text(encoding="utf-8")
        )
        expected_result = json.loads(
            (fixture_dir / "conservation_antonym_axis_result.json").read_text(
                encoding="utf-8"
            )
        )
        request = next(
            item
            for item in check_passes.build_bundles(
                entry, blind_seed="acceptance-conservation-20260828"
            )
            if item["pass_id"] == "frame-relation"
        )
        alignment = check_passes.build_antonym_axis_alignment_key(
            entry, blind_seed="acceptance-conservation-20260828"
        )
        self.assertEqual(
            hashlib.sha256(entry.read_bytes()).hexdigest(),
            "6ba1eb84a85f078c9d6fc842663eb7a02ea7d67e5e7d0ac4a5ec7b6a6299ea46",
        )
        self.assertEqual(request["schema_version"], "antonym_axis_blind_request_v1")
        for item in request["input_sections"]["antonym_items"]:
            self.assertEqual(
                set(item),
                {
                    "item_id",
                    "headword",
                    "sense_definition",
                    "antonym",
                    "antonym_definition",
                },
            )
            self.assertRegex(item["item_id"], r"^ant-[0-9a-f]{12}$")
        shuffled_orders = []
        opaque_id_sets = []
        for seed in ("axis-shuffle-a", "axis-shuffle-b"):
            seeded_request = next(
                item
                for item in check_passes.build_bundles(entry, blind_seed=seed)
                if item["pass_id"] == "frame-relation"
            )
            seeded_alignment = check_passes.build_antonym_axis_alignment_key(
                entry, blind_seed=seed
            )
            source_terms = {
                item["item_id"]: item["antonym"]
                for item in seeded_alignment["items"]
            }
            ids = [
                item["item_id"]
                for item in seeded_request["input_sections"]["antonym_items"]
            ]
            opaque_id_sets.append(set(ids))
            shuffled_orders.append([source_terms[item_id] for item_id in ids])
        self.assertNotEqual(shuffled_orders[0], shuffled_orders[1])
        self.assertTrue(opaque_id_sets[0].isdisjoint(opaque_id_sets[1]))
        serialized = json.dumps(request, ensure_ascii=False)
        for forbidden in ("違い:", "頻度:", "例:", "訳:", "【類義語】", "＃コアイメージ"):
            self.assertNotIn(forbidden, serialized)

        materialized = check_passes.materialize_antonym_axis_stage2_request(
            entry,
            request,
            fixture_dir / "conservation_antonym_axis_blind_record.json",
            alignment,
        )
        self.assertEqual(materialized, stored_stage2)
        result = check_passes.reconcile_antonym_axis(
            request,
            blind_record,
            materialized,
            adjudication,
            alignment,
            aligned_at="2026-08-28T10:01:00+00:00",
        )
        self.assertEqual(result, expected_result)
        self.assertEqual(
            check_passes.validate_pass_output(
                result,
                self.router,
                entry_path=entry,
                antonym_request=request,
                antonym_stage2_request=materialized,
                antonym_alignment_key=alignment,
                request_payload=materialized,
            ),
            [],
        )

        source_by_id = {
            item["item_id"]: item["antonym"] for item in alignment["items"]
        }
        flags_by_term = {
            source_by_id[item["item_id"]]: set(item["flags"])
            for item in adjudication["adjudications"]
        }
        self.assertIn("F1", flags_by_term["change"])
        accepted = {
            "exploitation",
            "depletion",
            "waste",
            "neglect",
            "deterioration",
            "destruction",
            "nonconservation",
        }
        self.assertTrue(
            all(not (flags_by_term[term] & {"F1", "F2", "F3"}) for term in accepted)
        )

        repeated = check_passes.reconcile_antonym_axis(
            request,
            blind_record,
            materialized,
            adjudication,
            alignment,
            aligned_at="2026-08-28T10:01:00+00:00",
        )
        self.assertEqual(repeated, result)

    def test_antonym_axis_stage2_disclosure_requires_saved_stage1_record(self) -> None:
        fixture_dir = REPO_ROOT / "tests" / "fixtures" / "acceptance"
        entry = fixture_dir / "conservation_4f26c07b_defective.md"
        request = next(
            item
            for item in check_passes.build_bundles(
                entry, blind_seed="acceptance-conservation-20260828"
            )
            if item["pass_id"] == "frame-relation"
        )
        alignment = check_passes.build_antonym_axis_alignment_key(
            entry, blind_seed="acceptance-conservation-20260828"
        )
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "not-saved.json"
            with self.assertRaisesRegex(ValueError, "process defect"):
                check_passes.materialize_antonym_axis_stage2_request(
                    entry, request, missing, alignment
                )

    def test_antonym_axis_rejects_nonchronological_alignment(self) -> None:
        fixture_dir = REPO_ROOT / "tests" / "fixtures" / "acceptance"
        entry = fixture_dir / "conservation_4f26c07b_defective.md"
        request = next(
            item
            for item in check_passes.build_bundles(
                entry, blind_seed="acceptance-conservation-20260828"
            )
            if item["pass_id"] == "frame-relation"
        )
        blind = json.loads(
            (fixture_dir / "conservation_antonym_axis_blind_record.json").read_text()
        )
        stage2 = json.loads(
            (fixture_dir / "conservation_antonym_axis_stage2_request.json").read_text()
        )
        adjudication = json.loads(
            (
                fixture_dir
                / "conservation_antonym_axis_adjudication_record.json"
            ).read_text()
        )
        alignment = check_passes.build_antonym_axis_alignment_key(
            entry, blind_seed="acceptance-conservation-20260828"
        )
        with self.assertRaisesRegex(ValueError, "later than"):
            check_passes.reconcile_antonym_axis(
                request,
                blind,
                stage2,
                adjudication,
                alignment,
                aligned_at="2026-08-28T10:00:00+00:00",
            )

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

    def test_pass_output_requires_independent_reviewer_provenance(self) -> None:
        errors = check_passes.validate_pass_output(
            {"pass_id": "translation", "findings": []}, self.router
        )
        self.assertTrue(any("reviewer" in error for error in errors))
        self.assertEqual(
            check_passes.validate_pass_output(
                {
                    "pass_id": "translation",
                    "reviewer": {
                        "mode": "handoff",
                        "declared_model": "independent-model",
                        "ingested_by": "human",
                    },
                    "findings": [],
                },
                self.router,
            ),
            [],
        )

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
