"""Regression cases for suspicion's workflow stalls, not fabricated review evidence."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_passes
import handoff_provenance
import review_continuation as continuation
import review_liveness
import review_preflight
import review_results
import review_validation
import source_first_audit_gate as source_gate
import workflow_revision
from test_source_first_audit_gate import valid_v2_manifest


class SourcePhaseRegressionTests(unittest.TestCase):
    def collected(self):
        value = valid_v2_manifest()
        value.pop("final_review")
        gate = value["source_first_audit"]
        gate["article_comparison_started_at"] = None
        gate["source_union"] = []
        gate["claim_units"] = []
        gate["usage"]["final_attempts_used"] = 0
        return value

    def test_inventory_completion_does_not_require_future_article_mapping(self):
        self.assertEqual(source_gate.validate_manifest(self.collected(), allow_incomplete=True), [])

    def test_comparison_and_final_publication_still_require_mapping(self):
        value = self.collected()
        self.assertTrue(source_gate.validate_manifest(value))
        value["source_first_audit"]["article_comparison_started_at"] = "2026-08-23T10:05:00+09:00"
        errors = source_gate.validate_manifest(value, allow_incomplete=True)
        self.assertTrue(any("missing from source_union" in e for e in errors), errors)

    def test_partial_mapping_cannot_reference_unknown_facts(self):
        value = self.collected()
        value["source_first_audit"]["source_union"] = [{
            "id": "U1", "source_fact_ids": ["MISSING"], "canonical_statement": "claim",
            "disposition": "included", "rationale": "fixture",
        }]
        self.assertTrue(any("unknown facts" in e for e in source_gate.validate_manifest(value, allow_incomplete=True)))

    def test_inventory_timestamp_and_coverage_remain_required(self):
        for field, replacement in (("inventory_completed_at", None), ("coverage_axes", [])):
            value = self.collected()
            value["source_first_audit"][field] = replacement
            self.assertTrue(source_gate.validate_manifest(value, allow_incomplete=True))


class ReviewContractRegressionTests(unittest.TestCase):
    def review(self):
        return {"schema_version": "final_review_v3", "target_results": [{"id": "T1", "status": "pass"}],
                "finding_results": [], "notes": []}

    def test_specific_finding_note_needs_no_duplicate_overall_note(self):
        value = self.review()
        value["finding_results"] = [{"id": "F1", "status": "pass", "notes": "暫定合意の訳語修正を確認。"}]
        self.assertEqual(review_liveness.validate_final_review_liveness(value), [])

    def test_short_concrete_overall_observation_has_no_40_character_quota(self):
        value = self.review()
        value["notes"] = ["頻度を統計値と扱っていないことを確認。"]
        self.assertEqual(review_liveness.validate_final_review_liveness(value), [])

    def test_empty_and_boilerplate_all_pass_templates_are_still_rejected(self):
        for notes in ([], ["問題なし"], ["OK"], ["確認済み。"], ["   "]):
            value = self.review(); value["notes"] = notes
            self.assertTrue(review_liveness.validate_final_review_liveness(value), notes)

    def test_notes_on_actual_findings_still_required(self):
        self.assertTrue(review_results.needs_notes({"status": "pass"}, compact=True, field="finding_results"))
        self.assertFalse(review_results.needs_notes({"status": "pass"}, compact=True, field="target_results"))
        self.assertTrue(review_results.needs_notes({"status": "fail"}, compact=True, field="target_results"))

    def test_finding_ids_are_deterministic_and_do_not_mutate_raw_response(self):
        rows = [{"taxonomy_id": "lexical_relation_mislabel", "rationale": "fixture", "location": {"line_start": 5}}]
        original = copy.deepcopy(rows)
        a = review_validation.checker_findings_with_ids("frame-relation", rows)
        b = review_validation.checker_findings_with_ids("frame-relation", rows)
        self.assertEqual(a, b)
        self.assertEqual(rows, original)
        self.assertNotEqual(a, review_validation.checker_findings_with_ids("translation", rows))
        self.assertEqual(a, review_validation.checker_findings_with_ids("frame-relation", a))

    def test_explicit_ids_and_invalid_rows_remain_visible(self):
        rows = [{"id": "original", "rationale": "fixture"}, None]
        self.assertEqual(rows, review_validation.checker_findings_with_ids("frame-relation", rows))

    def test_compact_packet_exposes_trace_contract_and_keeps_every_decision_unjudged(self):
        # Only input preflight is mocked; test the actual packet/template builder.
        values = {name: {} for name in review_preflight.FINAL_INPUTS}
        values["source_inventory"] = {"source_first_audit": {"source_union": []}}
        values["pass_findings"] = {"pass_outputs": [{"pass_id": "translation", "findings": [{"rationale": "fixture"}]}], "independent_candidates": []}
        values["cold_review"] = {"findings": []}
        values["final_blind"] = {"article_findings": [], "independent_candidates": []}
        values["checker_recheck_manifest"] = {"pass_results": []}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); entry = root / "word.md"; entry.write_text("＃語源\nfixture\n", encoding="utf-8")
            for name, value in values.items():
                (root / (name + ".json")).write_text(json.dumps(value), encoding="utf-8")
            with mock.patch.object(review_validation, "final_input_report", return_value={"valid": True}), \
                 mock.patch.object(review_preflight.content_audit, "extract_targets", return_value=[]), \
                 mock.patch.object(review_preflight.content_audit, "extract_relations", return_value=[]):
                packet = review_preflight.final_inputs(entry, root, root, compact=True)
            self.assertEqual(packet["review_trace_contract"], review_results.TRACE_CONTRACT)
            row = packet["response_template"]["finding_results"][0]
            self.assertTrue(row["id"].startswith("CHK-translation-"))
            self.assertIsNone(row["status"])
            self.assertIsNone(packet["response_template"]["decision"])


LEXICAL = """＃意味・用法・関連表現
1. 【名詞】疑い
【日本語訳・定義】確証のない考え。
【頻度】〈8/10〉
【類義語】
・doubt
頻度: 〈8/10〉
定義: 確信がないこと。
例: Some doubt remains.
訳: 疑いが残る。
違い: 確信の欠如に焦点がある。
【語法・注意】節を伴う。
"""


class InputAndScopeRegressionTests(unittest.TestCase):
    def test_frequency_preamble_is_delivered_to_both_frequency_reviewers(self):
        preamble = "頻度スコアは編集上の定性的推定であり、統計値ではない。"
        text = LEXICAL.replace("1. 【名詞】", preamble + "\n\n1. 【名詞】")
        sections = check_passes.extract_sections(text)
        self.assertIn(preamble, [line["text"] for line in sections["frequency_register"]])
        router = check_passes.load_router()
        for pid in ("qualification", "evidence"):
            route = next(row for row in router["passes"] if row["id"] == pid)
            self.assertIn("frequency_register", route["sections"])
            self.assertIn("lexical_relations", route["sections"])
        self.assertNotIn(preamble, json.dumps(sections["pronunciation"], ensure_ascii=False))

    def test_new_hash_ignores_only_located_line_offsets(self):
        request = {"pass_id": "translation", "normalization_version": check_passes.SEMANTIC_INPUT_VERSION,
                   "input_sections": {"definitions": [{"line": 5, "text": "meaning"}]}}
        moved = copy.deepcopy(request); moved["input_sections"]["definitions"][0]["line"] = 100
        self.assertEqual(check_passes._normalized_request_hash(request), check_passes._normalized_request_hash(moved))
        moved["input_sections"]["definitions"][0]["text"] = "different meaning"
        self.assertNotEqual(check_passes._normalized_request_hash(request), check_passes._normalized_request_hash(moved))

    def test_legacy_hashes_and_unknown_shapes_do_not_silently_change(self):
        request = {"pass_id": "translation", "input_sections": {"definitions": [{"line": 5, "text": "meaning"}]}}
        moved = copy.deepcopy(request); moved["input_sections"]["definitions"][0]["line"] = 100
        self.assertNotEqual(check_passes._normalized_request_hash(request), check_passes._normalized_request_hash(moved))
        self.assertEqual(check_passes._without_line_offsets({"line": 5, "text": "meaning", "assertion_id": "A1"}),
                         {"line": 5, "text": "meaning", "assertion_id": "A1"})

    def test_unknown_normalization_version_fails_closed(self):
        self.assertTrue(check_passes.validate_request_integrity({"normalization_version": "invented"}))

    def test_lexical_numeric_frequency_only_has_two_required_passes(self):
        plan = workflow_revision.plan_rechecks(LEXICAL, LEXICAL.replace("頻度: 〈8/10〉", "頻度: 〈7/10〉"))
        self.assertEqual(plan["invalidated_passes"], ["evidence", "qualification"])
        self.assertEqual(plan["changed_facets"], ["lexical_relations.frequency_score"])
        self.assertFalse(plan["full_recheck"])

    def test_meaning_example_relation_or_added_text_is_not_frequency_only(self):
        for old, new in (("確信がないこと", "確信があること"), ("Some doubt remains.", "Doubt disappeared."),
                         ("・doubt", "・trust"), ("頻度: 〈8/10〉", "頻度: 〈7/10〉 日常的")):
            plan = workflow_revision.plan_rechecks(LEXICAL, LEXICAL.replace(old, new))
            self.assertEqual(set(plan["invalidated_passes"]), workflow_revision.UNIT_TO_PASSES["lexical_relations"])

    def test_unknown_or_sense_topology_change_still_rechecks_all_seven(self):
        for after in (LEXICAL.replace("1. 【名詞】", "1. 【動詞】"), LEXICAL + "\n＃未分類\n変更"):
            self.assertTrue(workflow_revision.plan_rechecks(LEXICAL, after)["full_recheck"])

    def test_frequency_and_usage_changes_compose_without_full_restart(self):
        after = LEXICAL.replace("頻度: 〈8/10〉", "頻度: 〈7/10〉").replace("節を伴う。", "that節を伴う。")
        plan = workflow_revision.plan_rechecks(LEXICAL, after)
        self.assertEqual(plan["invalidated_passes"], ["evidence", "qualification", "sense-structure"])


class SealedReplayRegressionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / "audits/runs/s/sample/run/stage1.json"
        self.source.parent.mkdir(parents=True)
        self.blind = {"axes": [], "reviewer": {"mode": "handoff", "agent_id": "original",
                      "declared_model": "model-a", "ingested_by": "human"}}
        self.source.write_text(json.dumps(self.blind), encoding="utf-8")
        self.raw = self.source.read_bytes()
        self.blind["reviewer"]["source_response"] = handoff_provenance.bind(self.source, self.root)
        self.blind["reviewer"]["ingested_by"] = "orchestrator"
        self.request_hash = "a" * 64
        self.response = {"reviewer": {"mode": "handoff", "agent_id": "replacement", "declared_model": "model-b", "ingested_by": "human"},
                         "stage1_replay": continuation.replay_template(self.blind, self.request_hash)}
        self.response["stage1_replay"]["reason"] = "Original review context expired."

    def validate(self, response=None, others=()):
        return continuation.validate_replay(response or self.response, self.blind, self.request_hash,
                                            other_agent_ids=others, repo_root=self.root)

    def test_lost_context_can_resume_without_rerunning_or_changing_stage1(self):
        frozen = copy.deepcopy(self.blind)
        self.assertEqual(self.validate(), [])
        self.assertEqual(self.blind, frozen)
        self.assertEqual(self.source.read_bytes(), self.raw)

    def test_original_same_reviewer_needs_no_replacement_receipt(self):
        self.assertEqual(self.validate({"reviewer": self.blind["reviewer"]}), [])

    def test_missing_receipt_or_each_tampered_binding_is_rejected(self):
        self.assertTrue(self.validate({"reviewer": self.response["reviewer"]}))
        for key in ("protocol", "previous_agent_id", "blind_record_sha256", "stage2_request_sha256", "reason"):
            response = copy.deepcopy(self.response); response["stage1_replay"][key] = ""
            self.assertTrue(self.validate(response), key)

    def test_replacement_cannot_impersonate_original_or_another_checker(self):
        response = copy.deepcopy(self.response); response["reviewer"]["agent_id"] = "original"
        self.assertTrue(self.validate(response))
        self.assertTrue(self.validate(others=["replacement"]))
        self.assertTrue(self.validate(others=["original"]))

    def test_missing_or_modified_original_response_is_not_replayable(self):
        self.blind["axes"] = [{"axis": "changed"}]
        self.response["stage1_replay"] = {**continuation.replay_template(self.blind, self.request_hash), "reason": "expired"}
        self.assertTrue(self.validate())
        self.blind["reviewer"].pop("source_response")
        self.assertTrue(self.validate())

    def test_replay_declaration_cannot_be_added_or_changed_by_ingester(self):
        raw = {"reviewer": self.response["reviewer"], "adjudications": []}
        path = self.source.parent / "stage2.json"; path.write_text(json.dumps(raw), encoding="utf-8")
        output = copy.deepcopy(raw)
        output["reviewer"]["source_response"] = handoff_provenance.bind(path, self.root)
        output["reviewer"]["ingested_by"] = "orchestrator"
        output["stage1_replay"] = self.response["stage1_replay"]
        self.assertTrue(handoff_provenance.validate(output, self.root, required=True))

    def test_real_stage2_ingester_resumes_saved_fixture_without_other_review_calls(self):
        import shutil
        import run_word_parallel as parallel
        fixture = ROOT / "tests/fixtures/acceptance"
        shutil.copytree(ROOT / "prompts", self.root / "prompts")
        shutil.copy2(ROOT / "audits/escaped_defect_taxonomy.json", self.root / "audits/escaped_defect_taxonomy.json")
        entry = self.root / "entries/c/conservation.md"; entry.parent.mkdir(parents=True)
        shutil.copy2(fixture / "conservation_4f26c07b_defective.md", entry)
        packet = next(row for row in check_passes.build_bundles(
            entry, blind_seed="acceptance-conservation-20260828", repo_root=self.root
        ) if row["pass_id"] == "frame-relation")
        alignment = check_passes.build_antonym_axis_alignment_key(
            entry, repo_root=self.root, blind_seed="acceptance-conservation-20260828"
        )
        raw = json.loads((fixture / "conservation_antonym_axis_blind_record.json").read_text())
        raw["reviewer"] = {"mode": "handoff", "agent_id": "original", "declared_model": "model-a", "ingested_by": "human"}
        raw = check_passes.bind_antonym_axis_blind_record(raw, packet)
        self.source.write_text(json.dumps(raw), encoding="utf-8")
        blind = copy.deepcopy(raw)
        blind["reviewer"]["source_response"] = handoff_provenance.bind(self.source, self.root)
        blind["reviewer"]["ingested_by"] = "orchestrator"
        cycle = self.source.parent; check_dir = cycle / "check_passes"; check_dir.mkdir()
        def write(name, value):
            path = check_dir / name
            path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
            return path
        saved = write("frame-relation.antonym-axis.blind-record.json", blind)
        write("frame-relation.request.json", packet)
        write("frame-relation.antonym-axis.alignment-key.json", alignment)
        stage2 = check_passes.materialize_antonym_axis_stage2_request(entry, packet, saved, alignment, repo_root=self.root)
        write("frame-relation.antonym-axis.stage2.request.json", stage2)
        ids = [row["id"] for row in check_passes.load_router()["passes"]]
        reviewers = {pid: {"mode": "handoff", "agent_id": "other-" + pid, "declared_model": "model-a", "ingested_by": "human"} for pid in ids}
        reviewers["frame-relation"] = blind["reviewer"]
        checkpoint = write("checker_passes.stage1.json", {"checker_reviewers": reviewers,
            "pass_outputs": [{"pass_id": pid, "reviewer": reviewers[pid], "findings": []} for pid in ids]})
        before = {path: path.read_bytes() for path in check_dir.iterdir()}
        response = json.loads((fixture / "conservation_antonym_axis_adjudication_record.json").read_text())
        response["reviewer"] = self.response["reviewer"]
        response["stage1_replay"] = {**continuation.replay_template(blind, continuation.digest(stage2)), "reason": "original fixture context unavailable"}
        response_path = cycle / "stage2.json"; response_path.write_text(json.dumps(response), encoding="utf-8")
        manifest = {"entry_path": "entries/c/conservation.md", "orchestrator": {"review_provenance_protocol": handoff_provenance.PROTOCOL}}
        # No provider or LLM is called: exercise the real deterministic ingester.
        target = parallel._process_parallel_stage2(manifest, cycle_dir=cycle, repo_root=self.root, response_path=response_path)
        aggregate = json.loads(target.read_text())
        frame = next(row for row in aggregate["pass_outputs"] if row["pass_id"] == "frame-relation")
        self.assertEqual(frame["reviewer"]["agent_id"], "replacement")
        self.assertEqual(frame["antonym_axis_blind_record"]["reviewer"]["agent_id"], "original")
        self.assertEqual(handoff_provenance.validate_checker(frame, self.root, required=True), [])
        for path, original_bytes in before.items():
            self.assertEqual(path.read_bytes(), original_bytes, str(path))
        self.assertEqual(len(aggregate["pass_outputs"]), 7)

    def test_actual_axis_validator_checks_replay_and_keeps_all_axis_judgments(self):
        fixture = ROOT / "tests/fixtures/acceptance"
        load = lambda name: json.loads((fixture / ("conservation_antonym_axis_" + name + ".json")).read_text())
        blind, packet, result = load("blind_record"), load("stage2_request"), load("adjudication_record")
        blind["reviewer"] = copy.deepcopy(self.blind["reviewer"])
        result["reviewer"] = copy.deepcopy(self.response["reviewer"])
        result["stage1_replay"] = {**continuation.replay_template(blind, continuation.digest(packet)), "reason": "expired"}
        bound = check_passes.bind_antonym_axis_adjudication_record(result, packet, blind)
        self.assertEqual(check_passes.validate_antonym_axis_adjudication_record(bound, packet, blind), [])
        bound["stage1_replay"]["blind_record_sha256"] = "b" * 64
        self.assertTrue(check_passes.validate_antonym_axis_adjudication_record(bound, packet, blind))
        bound["stage1_replay"]["blind_record_sha256"] = continuation.digest(blind)
        bound["adjudications"].pop()
        self.assertTrue(check_passes.validate_antonym_axis_adjudication_record(bound, packet, blind))


if __name__ == "__main__":
    unittest.main()
