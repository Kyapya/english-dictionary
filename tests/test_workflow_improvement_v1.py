from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_passes  # noqa: E402
import review_liveness  # noqa: E402
import workflow_revision  # noqa: E402
import generate_audit_manifest  # noqa: E402


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _source_inventory(body: str) -> dict[str, object]:
    return {
        "schema_version": "source_inventory_v2",
        "stage": "source_inventory",
        "input_body_sha256": _digest(body),
        "source_first_audit": {
            "version": "source_first_audit_v2",
            "profile": "standard",
            "profile_reason": "fixture",
            "limits": {
                "max_sources": 6,
                "max_facts": 48,
                "max_research_rounds": 2,
                "max_post_cold_rechecks": 1,
                "max_final_attempts": 2,
            },
            "usage": {
                "sources_used": 2,
                "facts_used": 2,
                "research_rounds_used": 1,
                "post_cold_rechecks_used": 0,
                "final_attempts_used": 0,
            },
            "research_status": "complete",
            "stop_reason": "coverage_axes_closed",
            "open_questions": [],
            "inventory_completed_before_article_comparison": True,
            "inventory_completed_at": "2026-09-05T00:00:00Z",
            "article_comparison_started_at": "2026-09-05T00:01:00Z",
            "coverage_axes": [
                {
                    "axis": axis,
                    "status": "covered" if axis == "pronunciation_and_etymology" else "not_applicable",
                    "source_fact_ids": ["F-1", "F-2"] if axis == "pronunciation_and_etymology" else [],
                    "notes": "fixture coverage",
                }
                for axis in (
                    "lexical_senses",
                    "part_of_speech_and_frames",
                    "derived_and_related_forms",
                    "specialist_and_legal_uses",
                    "register_region_and_frequency",
                    "pronunciation_and_etymology",
                )
            ],
            "sources": [
                {
                    "id": "S-1",
                    "locator": "https://example.test/one",
                    "source_type": "dictionary",
                    "source_role": "general_lexicon",
                    "independence_group": "one",
                    "facts": [{
                        "id": "F-1",
                        "form": "sample",
                        "kind": "pronunciation",
                        "statement": "The pronunciation is /sample/.",
                        "source_detail": "pronunciation field",
                    }],
                },
                {
                    "id": "S-2",
                    "locator": "https://example.test/two",
                    "source_type": "dictionary",
                    "source_role": "general_lexicon",
                    "independence_group": "two",
                    "facts": [{
                        "id": "F-2",
                        "form": "sample",
                        "kind": "pronunciation",
                        "statement": "The pronunciation is /sample/.",
                        "source_detail": "headword IPA",
                    }],
                },
            ],
            "source_union": [{
                "id": "U-1",
                "source_fact_ids": ["F-1", "F-2"],
                "canonical_statement": "The headword pronunciation is /sample/.",
                "disposition": "integrated",
                "rationale": "two independent sources agree",
            }],
            "claim_units": [{
                "id": "C-1",
                "union_ids": ["U-1"],
                "subject_form": "sample",
                "claim_type": "pronunciation",
                "statement": "sample is pronounced /sample/.",
                "article_target_ids": ["pronunciation:001"],
                "source_supports": [
                    {"source_fact_id": "F-1", "support_summary": "The first source directly supplies the pronunciation."},
                    {"source_fact_id": "F-2", "support_summary": "The second source independently supplies the pronunciation."},
                ],
            }],
        },
    }


class EvidenceContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.body = "＃ 発音\n/sample/\n\n＃ 語義\n1. 【名詞】見本"
        self.inventory = _source_inventory(self.body)

    def test_evidence_context_is_minimal_bound_and_usage_neutral(self) -> None:
        gate = self.inventory["source_first_audit"]
        gate["sources"][0]["facts"].append({
            "id": "F-3",
            "form": "sample",
            "kind": "usage_note",
            "statement": "The word is sometimes used figuratively.",
            "source_detail": "usage paragraph",
        })
        gate["usage"]["facts_used"] = 3
        gate["source_union"].append({
            "id": "U-2",
            "source_fact_ids": ["F-3"],
            "canonical_statement": "A figurative use exists.",
            "disposition": "integrated",
            "rationale": "kept as a separate usage claim",
        })
        gate["claim_units"].append({
            "id": "C-2",
            "union_ids": ["U-2"],
            "subject_form": "sample",
            "claim_type": "usage_note",
            "statement": "The word can be figurative.",
            "article_target_ids": ["usage_note:001"],
            "source_supports": [{
                "source_fact_id": "F-3",
                "support_summary": "The source usage paragraph records the figurative use.",
            }],
        })
        before_usage = copy.deepcopy(self.inventory["source_first_audit"]["usage"])
        packet = check_passes.build_evidence_context(
            self.inventory,
            input_body_sha256=_digest(self.body),
            relevant_sections={"pronunciation"},
        )
        self.assertEqual(packet["schema_version"], "evidence_context_v1")
        self.assertEqual([item["id"] for item in packet["claim_units"]], ["C-1"])
        self.assertEqual([item["id"] for item in packet["source_union"]], ["U-1"])
        self.assertEqual({item["id"] for item in packet["sources"]}, {"S-1", "S-2"})
        self.assertEqual(self.inventory["source_first_audit"]["usage"], before_usage)
        self.assertEqual(check_passes.validate_evidence_context(packet), [])

    def test_routed_evidence_bundle_requires_context_and_api_handoff_share_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            entry = Path(directory) / "sample.md"
            entry.write_text(self.body, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source-first artifact is required"):
                check_passes.build_bundles(
                    entry, repo_root=ROOT, require_evidence_context=True
                )
            api = check_passes.build_bundles(
                entry,
                repo_root=ROOT,
                source_inventory=self.inventory,
                require_evidence_context=True,
                blind_seed="same-run",
            )
            handoff = check_passes.build_bundles(
                entry,
                repo_root=ROOT,
                source_inventory=self.inventory,
                require_evidence_context=True,
                blind_seed="same-run",
            )
        api_evidence = next(row for row in api if row["pass_id"] == "evidence")
        handoff_evidence = next(row for row in handoff if row["pass_id"] == "evidence")
        self.assertEqual(api_evidence, handoff_evidence)
        self.assertIn("evidence_context", api_evidence)

    def test_evidence_context_fails_closed_for_missing_incomplete_or_stale_inventory(self) -> None:
        with self.assertRaisesRegex(ValueError, "source-first artifact is required"):
            check_passes.build_evidence_context(
                None,
                input_body_sha256=_digest(self.body),
                relevant_sections={"pronunciation"},
            )
        incomplete = copy.deepcopy(self.inventory)
        incomplete["source_first_audit"]["research_status"] = "in_progress"
        with self.assertRaisesRegex(ValueError, "research_status must be complete"):
            check_passes.build_evidence_context(
                incomplete,
                input_body_sha256=_digest(self.body),
                relevant_sections={"pronunciation"},
            )
        with self.assertRaisesRegex(ValueError, "body hash"):
            check_passes.build_evidence_context(
                self.inventory,
                input_body_sha256="f" * 64,
                relevant_sections={"pronunciation"},
            )

    def test_evidence_context_rejects_broken_support_reference(self) -> None:
        broken = copy.deepcopy(self.inventory)
        broken["source_first_audit"]["claim_units"][0]["source_supports"][0]["source_fact_id"] = "missing"
        with self.assertRaisesRegex(ValueError, "source-first artifact is invalid"):
            check_passes.build_evidence_context(
                broken,
                input_body_sha256=_digest(self.body),
                relevant_sections={"pronunciation"},
            )

    def test_checker_request_integrity_rejects_tampered_evidence_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            entry = Path(directory) / "sample.md"
            entry.write_text(self.body, encoding="utf-8")
            requests = check_passes.build_bundles(
                entry,
                repo_root=ROOT,
                source_inventory=self.inventory,
                require_evidence_context=True,
            )
        evidence = next(item for item in requests if item["pass_id"] == "evidence")
        evidence["evidence_context"]["claim_units"][0]["statement"] = "tampered"
        errors = check_passes.validate_request_integrity(evidence, repo_root=ROOT)
        self.assertIn("checker normalized input hash mismatch", errors)


class RevisionScopeTests(unittest.TestCase):
    def test_pronunciation_only_rechecks_only_pronunciation_and_evidence(self) -> None:
        before = "＃発音記号\n/a/\n\n＃意味・用法・関連表現\n1. 【名詞】見本"
        after = before.replace("/a/", "/b/")
        plan = workflow_revision.plan_rechecks(before, after)
        self.assertEqual(plan["changed_units"], ["pronunciation"])
        self.assertEqual(plan["invalidated_passes"], ["evidence", "pronunciation"])
        self.assertFalse(plan["full_recheck"])

    def test_example_change_invalidates_translation_attribution_and_frame(self) -> None:
        before = "＃意味・用法・関連表現\n1. 【名詞】見本\n【コロケーション】\n・a sample\n例: Old.\n訳: 旧。"
        after = before.replace("Old.", "New.")
        invalidated = set(workflow_revision.plan_rechecks(before, after)["invalidated_passes"])
        self.assertTrue({"translation", "example-attribution", "frame-relation"} <= invalidated)

    def test_sense_split_and_unclassified_change_fall_back_to_all_passes(self) -> None:
        before = "＃意味・用法・関連表現\n1. 【名詞】見本"
        split = before + "\n2. 【名詞】標本"
        self.assertTrue(workflow_revision.plan_rechecks(before, split)["full_recheck"])
        unknown_before = before + "\n\n＃未分類\n自由記述A"
        unknown_after = before + "\n\n＃未分類\n自由記述B"
        self.assertTrue(workflow_revision.plan_rechecks(unknown_before, unknown_after)["full_recheck"])

    def test_cache_reuse_requires_all_hash_and_validation_conditions(self) -> None:
        expected = {
            "pass_id": "pronunciation",
            "spec_sha256": "a" * 64,
            "normalized_input_sha256": "b" * 64,
            "source_artifact_sha256": "c" * 64,
        }
        record = {
            **expected,
            "output_sha256": "d" * 64,
            "schema_valid": True,
            "reviewer_independent": True,
            "request_binding_valid": True,
        }
        self.assertEqual(workflow_revision.reuse_errors(record, expected), [])
        for key in ("spec_sha256", "normalized_input_sha256", "source_artifact_sha256"):
            stale = dict(record)
            stale[key] = "e" * 64
            self.assertTrue(workflow_revision.reuse_errors(stale, expected), key)


class OrderingAndAdjudicationTests(unittest.TestCase):
    def test_resolution_partitions_findings_exactly_once(self) -> None:
        pre = [{"id": "P-1", "finding_id": "P-1", "status": "resolved", "disposition": "rejected"}]
        post = [{"id": "B-1", "finding_id": "B-1", "status": "resolved", "disposition": "adopted"}]
        self.assertEqual(
            workflow_revision.validate_resolution_partition(
                checker_and_cold_ids={"P-1"},
                final_blind_ids={"B-1"},
                pre_blind_resolutions=pre,
                post_blind_resolutions=post,
            ),
            [],
        )
        self.assertTrue(
            workflow_revision.validate_resolution_partition(
                checker_and_cold_ids={"P-1"},
                final_blind_ids={"B-1"},
                pre_blind_resolutions=[*pre, post[0]],
                post_blind_resolutions=post,
            )
        )

    def test_final_blind_chronology_requires_post_revision_body_and_time(self) -> None:
        errors = workflow_revision.final_blind_chronology_errors(
            cold_review={"recorded_at": "2026-09-05T00:00:00Z"},
            pre_blind_revision={
                "recorded_at": "2026-09-05T00:01:00Z",
                "output_body_sha256": "a" * 64,
            },
            final_blind={
                "recorded_at": "2026-09-05T00:02:00Z",
                "input_body_sha256": "a" * 64,
            },
        )
        self.assertEqual(errors, [])
        stale = workflow_revision.final_blind_chronology_errors(
            cold_review={"recorded_at": "2026-09-05T00:00:00Z"},
            pre_blind_revision={
                "recorded_at": "2026-09-05T00:01:00Z",
                "output_body_sha256": "a" * 64,
            },
            final_blind={
                "recorded_at": "2026-09-04T23:59:00Z",
                "input_body_sha256": "b" * 64,
            },
        )
        self.assertGreaterEqual(len(stale), 2)

    def test_zero_findings_do_not_trigger_secondary_reviews(self) -> None:
        self.assertEqual(
            review_liveness.zero_finding_run_errors(
                {"pass_outputs": []},
                {"findings": []},
                {"article_findings": [], "independent_candidates": []},
            ),
            [],
        )

    def test_specific_conflict_triggers_targeted_adjudication_and_insufficient_blocks(self) -> None:
        issues = workflow_revision.unresolved_issue_actions(
            [{
                "id": "ISSUE-1",
                "kind": "judgment_conflict",
                "question": "Is this use regional?",
                "article_excerpt": "mainly British",
                "judgments": [{"reviewer_agent_id": "a", "conclusion": "yes", "evidence": ["F-1"]},
                             {"reviewer_agent_id": "b", "conclusion": "no", "evidence": ["F-2"]}],
            }]
        )
        self.assertEqual(issues[0]["action"], "targeted_adjudication")
        record = {
            "schema_version": "targeted_adjudication_v1",
            "issue_id": "ISSUE-1",
            "reviewer": {"agent_id": "c"},
            "decision": "insufficient_evidence",
            "rationale": "The two existing sources do not settle the region.",
            "applicable_scope": "frequency_register",
        }
        self.assertTrue(workflow_revision.targeted_adjudication_blocks_pass(record))

    def test_targeted_adjudicator_must_differ_from_conflicting_reviewers(self) -> None:
        record = {
            "schema_version": "targeted_adjudication_v1",
            "issue_id": "ISSUE-1",
            "reviewer": {"agent_id": "checker-a"},
            "decision": "resolved_correct",
            "rationale": "The cited source limits the label to British English.",
            "applicable_scope": "frequency_register",
        }
        errors = workflow_revision.validate_targeted_adjudication(
            record, conflicting_agent_ids=["checker-a", "cold-b"]
        )
        self.assertIn(
            "targeted adjudicator must be independent of conflicting reviewers",
            errors,
        )

    def test_old_completed_cycle_without_new_artifacts_remains_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = generate_audit_manifest._validate_workflow_improvement_artifacts(
                cycle_dir=Path(directory),
                repo_root=Path(directory),
                raw={},
                current_hash="a" * 64,
                checker_and_cold_ids=set(),
                final_blind_ids=set(),
            )
        self.assertIsNone(result)

    def test_new_artifacts_require_current_recheck_and_final_blind_chronology(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cycle = root / "audits" / "runs" / "s" / "sample" / "cycle-new"
            cycle.mkdir(parents=True)
            current_hash = "b" * 64
            final_blind = {
                "recorded_at": "2026-09-05T00:03:00Z",
                "input_body_sha256": current_hash,
            }
            (cycle / "final_blind.json").write_text(json.dumps(final_blind))
            artifacts = {
                "pre_blind_resolution.json": {
                    "schema_version": "pre_blind_resolution_v1",
                    "resolutions": [],
                },
                "pre_blind_revision.json": {
                    "schema_version": "pre_blind_revision_v1",
                    "input_body_sha256": "a" * 64,
                    "output_body_sha256": current_hash,
                    "recorded_at": "2026-09-05T00:02:00Z",
                },
                "checker_recheck_manifest.json": {
                    "schema_version": "checker_recheck_manifest_v1",
                    "current_body_sha256": current_hash,
                    "pass_results": [
                        {
                            "pass_id": pass_id,
                            "mode": "rechecked",
                            "validated_on_body_sha256": current_hash,
                            "spec_sha256": "c" * 64,
                            "normalized_input_sha256": "d" * 64,
                            "source_artifact_sha256": "e" * 64,
                            "output_sha256": "f" * 64,
                            "schema_valid": True,
                            "reviewer_independent": True,
                            "request_binding_valid": True,
                        }
                        for pass_id in sorted(workflow_revision.ALL_CHECKER_PASSES)
                    ],
                },
                "post_blind_resolution.json": {
                    "schema_version": "post_blind_resolution_v1",
                    "resolutions": [],
                },
                "post_blind_verification.json": {
                    "schema_version": "post_blind_verification_v1",
                    "verified_body_sha256": current_hash,
                    "checker_recheck_completed": False,
                    "final_blind_repeated": False,
                },
            }
            for name, value in artifacts.items():
                (cycle / name).write_text(json.dumps(value))
            result = generate_audit_manifest._validate_workflow_improvement_artifacts(
                cycle_dir=cycle,
                repo_root=root,
                raw={
                    "normal_review": {"input_body_sha256": "a" * 64},
                    "cold_review": {
                        "input_body_sha256": "a" * 64,
                        "recorded_at": "2026-09-05T00:01:00Z",
                    },
                    "final_blind": final_blind,
                    "final_review": {"decision": "pass"},
                },
                current_hash=current_hash,
                checker_and_cold_ids=set(),
                final_blind_ids=set(),
            )
            (cycle / "post_blind_resolution.json").write_text(
                json.dumps(
                    {
                        "schema_version": "post_blind_resolution_v1",
                        "resolutions": [{
                            "id": "B-1",
                            "finding_id": "B-1",
                            "status": "resolved",
                            "disposition": "adopted",
                        }],
                    }
                )
            )
            with self.assertRaisesRegex(ValueError, "repeated final blind"):
                generate_audit_manifest._validate_workflow_improvement_artifacts(
                    cycle_dir=cycle,
                    repo_root=root,
                    raw={
                        "normal_review": {"input_body_sha256": "a" * 64},
                        "cold_review": {
                            "input_body_sha256": "a" * 64,
                            "recorded_at": "2026-09-05T00:01:00Z",
                        },
                        "final_blind": final_blind,
                        "final_review": {"decision": "pass"},
                    },
                    current_hash=current_hash,
                    checker_and_cold_ids=set(),
                    final_blind_ids={"B-1"},
                )
        self.assertEqual(result["schema_version"], "workflow_revision_v1")


if __name__ == "__main__":
    unittest.main()
