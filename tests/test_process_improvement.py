from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import process_improvement as pi  # noqa: E402
import run_word  # noqa: E402


class ProcessImprovementV2AcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        improvement = self.root / "process_improvement"
        (improvement / "records").mkdir(parents=True)
        (improvement / "records" / "PI-0001.json").write_text(
            json.dumps({"old": "knowledge body must be removed"}), encoding="utf-8"
        )
        (improvement / "ACTIVE.md").write_text("old active body", encoding="utf-8")
        (improvement / "retirement_state.json").write_text("{}", encoding="utf-8")
        (self.root / "prompts").mkdir()
        (self.root / "prompts" / "entry.md").write_text(
            "# Current entry specification\n\nKeep evidence scoped.\n",
            encoding="utf-8",
        )
        shutil.copy2(
            REPO_ROOT / "prompts" / "check_router_v6.md",
            self.root / "prompts" / "check_router_v6.md",
        )
        pi.migrate_v2(
            knowledge_epoch="test-epoch-v2",
            pre_migration_sha="a" * 40,
            migrated_at="2026-09-06T00:00:00Z",
            repo_root=self.root,
        )

    def source(self, event_id: str, *, epoch: str = "test-epoch-v2") -> dict:
        return {
            "event_id": event_id,
            "knowledge_epoch": epoch,
            "origin_kind": "synthetic_test",
            "source_ref": f"audits/synthetic/{event_id}.json",
            "observed_at": "2026-09-06T00:01:00Z",
            "content_sha256": hashlib.sha256(event_id.encode()).hexdigest(),
        }

    def submission(
        self,
        suffix: str,
        *,
        status: str = "active",
        required_tags: list[str] | None = None,
        excluded_tags: list[str] | None = None,
        recipient: str = "generator",
        phase: str = "generation",
    ) -> dict:
        accepted = status != "candidate"
        record = {
            "title": f"Reusable finding {suffix}",
            "status": status,
            "category": "quality",
            "priority": 50,
            "problem": {
                "observed": f"A concrete cross-entry problem was observed in run {suffix}.",
                "action": (
                    f"When condition {suffix} is confirmed, compare every affected example "
                    "against its assigned sense before saving the draft."
                ),
                "reusable_because": (
                    "The same assignment failure can occur with any polysemous headword."
                ),
                "conditions": {
                    "required_tags": required_tags or [],
                    "excluded_tags": excluded_tags or [],
                },
                "exclusions": "Do not apply when the required feature has not been confirmed.",
                "uncertainties": "No causal effect is claimed from this observation alone.",
            },
            "delivery": {"recipients": [recipient], "phases": [phase]},
            "validation": {
                "decision": "accepted" if accepted else "pending",
                "rationale": (
                    "The coordinator accepted the action from a fixed synthetic finding."
                    if accepted
                    else "Generalization awaits coordinator confirmation."
                ),
                "evidence_refs": [f"synthetic:{suffix}"] if accepted else [],
                "specification_context": (
                    [
                        {
                            "path": "prompts/entry.md",
                            "scope": "file",
                            "sha256": pi.dependency_sha256(
                                self.root, "prompts/entry.md"
                            ),
                        }
                    ]
                    if accepted
                    else []
                ),
            },
            "evidence_observation": (
                "The synthetic adopted finding records the observed mismatch and correction."
            ),
        }
        if status == "integrated":
            record["integration"] = {
                "refs": ["prompts/entry.md"],
                "verification_refs": [f"synthetic:{suffix}:test"],
                "reason": "The behavior is now enforced by the canonical specification.",
            }
        if status == "retired":
            record["lifecycle"] = {
                "reason": "A later finding proved this action misleading.",
                "evidence_refs": [f"synthetic:{suffix}:retirement"],
            }
        return record

    def create(
        self, suffix: str, *, status: str = "active", **kwargs: object
    ) -> str:
        receipt = pi.ingest_learning_delta(
            self.source(f"run-{suffix}"),
            {
                "schema_version": pi.DELTA_SCHEMA_VERSION,
                "reviewed": True,
                "items": [
                    {
                        "action": "create",
                        "record": self.submission(
                            suffix, status=status, **kwargs  # type: ignore[arg-type]
                        ),
                    }
                ],
            },
            repo_root=self.root,
        )
        return receipt["applied"][0]["knowledge_id"]

    def test_a01_empty_initial_state_is_valid(self) -> None:
        self.assertEqual(pi.validate_registry(self.root), [])
        records, errors = pi._load_records(self.root)
        self.assertEqual((records, errors), ([], []))
        selected = pi.select_knowledge(
            recipient="generator", phase="generation", repo_root=self.root
        )
        self.assertEqual(selected["selected"], [])
        self.assertNotIn("old active body", selected["input_text"])

    def test_a02_reset_reexecution_is_no_op_and_preserves_new_knowledge(self) -> None:
        record_id = self.create("a02", status="candidate")
        legacy = self.root / "process_improvement" / "records" / "PI-0999.json"
        legacy.write_text('{"old": true}', encoding="utf-8")
        retirement = self.root / "process_improvement" / "retirement_state.json"
        retirement.write_text("{}", encoding="utf-8")
        result = pi.migrate_v2(
            knowledge_epoch="test-epoch-v2",
            pre_migration_sha="a" * 40,
            migrated_at="2026-09-06T00:02:00Z",
            repo_root=self.root,
        )
        self.assertEqual(result["status"], "no_op")
        self.assertTrue(
            (self.root / "process_improvement" / "records" / f"{record_id}.json").is_file()
        )
        self.assertFalse(legacy.exists())
        self.assertFalse(retirement.exists())

    def test_a03_legacy_registry_cannot_flow_into_selection(self) -> None:
        legacy = self.root / "process_improvement" / "records" / "PI-0999.json"
        legacy.write_text(json.dumps({"action_rule": "old body"}), encoding="utf-8")
        selected = pi.select_knowledge(
            recipient="generator", phase="generation", repo_root=self.root
        )
        self.assertNotIn("old body", selected["input_text"])
        self.assertTrue(any("legacy" in error for error in pi.validate_registry(self.root)))

    def test_a04_old_event_cannot_create_current_knowledge(self) -> None:
        with self.assertRaisesRegex(ValueError, "old or unknown event epoch"):
            pi.ingest_learning_delta(
                self.source("old", epoch="old-epoch"),
                {
                    "schema_version": pi.DELTA_SCHEMA_VERSION,
                    "reviewed": True,
                    "items": [
                        {"action": "create", "record": self.submission("old")}
                    ],
                },
                repo_root=self.root,
            )

    def test_a05_first_useful_event_can_become_candidate_without_escape(self) -> None:
        record_id = self.create("a05", status="candidate")
        record = json.loads(
            (
                self.root
                / "process_improvement"
                / "records"
                / f"{record_id}.json"
            ).read_text()
        )
        self.assertEqual(record["status"], "candidate")
        self.assertNotIn("escaped_defect_ids", record)

    def test_a06_unadjudicated_material_cannot_be_active(self) -> None:
        value = self.submission("a06")
        value["validation"]["decision"] = "pending"
        value["validation"]["evidence_refs"] = []
        with self.assertRaisesRegex(ValueError, "active knowledge requires"):
            pi.ingest_learning_delta(
                self.source("run-a06"),
                {
                    "schema_version": pi.DELTA_SCHEMA_VERSION,
                    "reviewed": True,
                    "items": [{"action": "create", "record": value}],
                },
                repo_root=self.root,
            )

    def test_a07_generic_notes_rejected_and_no_learning_creates_no_record(self) -> None:
        value = self.submission("a07", status="candidate")
        value["problem"]["action"] = "注意する"
        with self.assertRaisesRegex(ValueError, "concrete reusable action"):
            pi.ingest_learning_delta(
                self.source("run-a07-bad"),
                {
                    "schema_version": pi.DELTA_SCHEMA_VERSION,
                    "reviewed": True,
                    "items": [{"action": "create", "record": value}],
                },
                repo_root=self.root,
            )
        receipt = pi.ingest_learning_delta(
            self.source("run-a07-none"),
            {
                "schema_version": pi.DELTA_SCHEMA_VERSION,
                "reviewed": True,
                "items": [],
            },
            repo_root=self.root,
        )
        self.assertEqual(receipt["status"], "no_applicable")
        self.assertEqual(pi._load_records(self.root)[0], [])

    def test_a08_cross_entry_reuse_reaches_run_b_input(self) -> None:
        record_id = self.create(
            "a08", required_tags=["polysemous"], status="active"
        )
        snapshot = pi.create_input_snapshot(
            run_id="run-b-different-headword",
            recipient="generator",
            phase="generation",
            output_path=(self.root / "audits" / "run-b" / "pi.snapshot.md"),
            features={"polysemous"},
            repo_root=self.root,
        )
        self.assertEqual(snapshot["selected"][0]["id"], record_id)
        self.assertIn(record_id, (self.root / snapshot["snapshot_path"]).read_text())

    def test_a09_status_condition_and_unknown_condition_are_excluded(self) -> None:
        candidate = self.create("a09-candidate", status="candidate")
        retired = self.create("a09-retired", status="retired")
        integrated = self.create("a09-integrated", status="integrated")
        conditional = self.create(
            "a09-conditional", status="active", required_tags=["special"]
        )
        selection = pi.select_knowledge(
            recipient="generator", phase="generation", repo_root=self.root
        )
        self.assertEqual(selection["selected"], [])
        reasons = {row["id"]: row["reason"] for row in selection["skipped"]}
        self.assertEqual(reasons[candidate], "status:candidate")
        self.assertEqual(reasons[retired], "status:retired")
        self.assertEqual(reasons[integrated], "status:integrated")
        self.assertEqual(reasons[conditional], "condition_unknown_or_mismatch")

    def test_a10_public_orchestrator_materializes_actual_generator_input(self) -> None:
        record_id = self.create("a10", status="active")
        path, manifest = run_word.create_guard_manifest(
            "different-headword",
            repo_root=self.root,
            branch="feat/test",
            base_sha="b" * 40,
            run_id="public-run-b",
        )
        self.assertTrue(path.is_file())
        request = run_word.next_stage_request(manifest)
        self.assertEqual(request["name"], "generation")
        snapshot_path = self.root / request["process_improvement_input_path"]
        self.assertTrue(snapshot_path.is_file())
        self.assertIn(record_id, snapshot_path.read_text())
        self.assertEqual(pi.validate_registry(self.root), [])

    def test_a08_a10_a20_joined_end_to_end(self) -> None:
        """Mocks coordinator semantics; it does not prove real quality improvement."""

        self.assertEqual(pi._load_records(self.root)[0], [])
        record_id = self.create("joined-a", status="active")
        _, run_b = run_word.create_guard_manifest(
            "joined-different-headword",
            repo_root=self.root,
            branch="feat/joined",
            base_sha="c" * 40,
            run_id="joined-run-b",
        )
        snapshot = run_b["process_improvement"]["snapshots"][0]
        self.assertEqual(snapshot["selected"][0]["id"], record_id)
        self.assertIn(
            record_id, (self.root / snapshot["snapshot_path"]).read_text()
        )
        pi.record_snapshot_delivery(snapshot, repo_root=self.root)
        pi.ingest_learning_delta(
            self.source("joined-run-b-result"),
            {
                "schema_version": pi.DELTA_SCHEMA_VERSION,
                "reviewed": True,
                "items": [
                    {
                        "action": "observe",
                        "knowledge_id": record_id,
                        "knowledge_version": 1,
                        "outcome": "action_confirmed",
                        "observation": (
                            "The mocked coordinator recorded the prescribed comparison."
                        ),
                    }
                ],
            },
            repo_root=self.root,
        )
        aggregate = pi.aggregate_observations(self.root)["by_version"][0]
        self.assertEqual(
            aggregate["outcomes"], {"action_confirmed": 1, "delivered": 1}
        )
        (self.root / "prompts" / "entry.md").write_text(
            "dependency changed", encoding="utf-8"
        )
        after_change = pi.select_knowledge(
            recipient="generator", phase="generation", repo_root=self.root
        )
        self.assertEqual(after_change["selected"], [])
        self.assertEqual(after_change["skipped"][0]["reason"], "needs_recheck")

    def test_a11_checker_cold_and_final_blind_have_no_pi_input(self) -> None:
        stages = {stage.name: stage for stage in run_word.build_plan("isolation")}
        for name in ("checker_passes", "cold_review", "final_blind"):
            self.assertIsNone(stages[name].process_improvement_input_path)
            serialized = json.dumps(stages[name].to_dict(self.root))
            self.assertNotIn("snapshot.md", serialized)
            self.assertNotIn("PI2-", serialized)

    def test_a13_missing_delta_is_pending_and_saved_delta_resumes(self) -> None:
        _, manifest = run_word.create_guard_manifest(
            "resume-word",
            repo_root=self.root,
            branch="feat/test",
            base_sha="b" * 40,
            run_id="resume-run",
        )
        output = self.root / "audits" / "generation.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps({"entry_features": []}), encoding="utf-8")
        first = run_word.process_stage_learning(
            manifest,
            stage="generation",
            output_paths=["audits/generation.json"],
            repo_root=self.root,
        )
        self.assertEqual(first["status"], "pending")
        output.write_text(
            json.dumps(
                {
                    "learning_delta": {
                        "schema_version": pi.DELTA_SCHEMA_VERSION,
                        "reviewed": True,
                        "items": [],
                    }
                }
            ),
            encoding="utf-8",
        )
        manifest["orchestrator_state"]["stage_outputs"]["generation"] = [
            "audits/generation.json"
        ]
        run_word.retry_pending_process_improvement(manifest, repo_root=self.root)
        self.assertEqual(
            manifest["process_improvement"]["processing"]["generation"]["status"],
            "no_applicable",
        )

    def test_a14_same_event_and_observation_are_idempotent(self) -> None:
        source = self.source("run-a14")
        delta = {
            "schema_version": pi.DELTA_SCHEMA_VERSION,
            "reviewed": True,
            "items": [
                {"action": "create", "record": self.submission("a14")}
            ],
        }
        first = pi.ingest_learning_delta(source, delta, repo_root=self.root)
        second = pi.ingest_learning_delta(source, delta, repo_root=self.root)
        self.assertEqual(first, second)
        self.assertEqual(len(pi._load_records(self.root)[0]), 1)

    def test_a15_id_and_version_collisions_do_not_overwrite(self) -> None:
        record_id = self.create("a15")
        current = json.loads(
            (
                self.root / "process_improvement" / "records" / f"{record_id}.json"
            ).read_text()
        )
        current["evidence_observation"] = "A conflicting update was independently observed."
        with self.assertRaisesRegex(ValueError, "concurrent knowledge update"):
            pi.ingest_learning_delta(
                self.source("run-a15-revise"),
                {
                    "schema_version": pi.DELTA_SCHEMA_VERSION,
                    "reviewed": True,
                    "items": [
                        {
                            "action": "revise",
                            "knowledge_id": record_id,
                            "expected_version": 0,
                            "record": current,
                        }
                    ],
                },
                repo_root=self.root,
            )
        self.assertEqual(
            json.loads(
                (
                    self.root
                    / "process_improvement"
                    / "records"
                    / f"{record_id}.json"
                ).read_text()
            )["version"],
            1,
        )

    def test_a15_interrupted_atomic_replace_preserves_existing_record(self) -> None:
        record_id = self.create("a15-atomic")
        path = (
            self.root
            / "process_improvement"
            / "records"
            / f"{record_id}.json"
        )
        before = path.read_bytes()
        with mock.patch.object(pi.os, "replace", side_effect=OSError("interrupted")):
            with self.assertRaisesRegex(OSError, "interrupted"):
                pi._atomic_json(path, {"corrupt": True})
        self.assertEqual(path.read_bytes(), before)

    def test_a16_dependency_change_is_scoped_and_excludes_knowledge(self) -> None:
        record_id = self.create("a16")
        (self.root / "entries").mkdir()
        (self.root / "entries" / "unrelated.md").write_text("unrelated", encoding="utf-8")
        before = pi.select_knowledge(
            recipient="generator", phase="generation", repo_root=self.root
        )
        self.assertEqual(before["selected"][0]["id"], record_id)
        (self.root / "prompts" / "entry.md").write_text("changed", encoding="utf-8")
        after = pi.select_knowledge(
            recipient="generator", phase="generation", repo_root=self.root
        )
        self.assertEqual(after["selected"], [])
        self.assertEqual(after["skipped"][0]["reason"], "needs_recheck")

    def test_a17_reconfirmation_requires_evidence_and_creates_new_version(self) -> None:
        record_id = self.create("a17")
        (self.root / "prompts" / "entry.md").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "evidence_ref"):
            pi.reconfirm_record(
                record_id=record_id,
                expected_version=1,
                evidence_ref="",
                rationale="",
                repo_root=self.root,
            )
        pi.reconfirm_record(
            record_id=record_id,
            expected_version=1,
            evidence_ref="synthetic:reconfirmation",
            rationale="The coordinator verified the action under the changed specification.",
            observed_at="2026-09-06T00:10:00Z",
            repo_root=self.root,
        )
        current = pi._load_records(self.root)[0][0]
        self.assertEqual(current["version"], 2)

    def test_a18_delivery_is_not_action_or_effect(self) -> None:
        record_id = self.create("a18")
        snapshot = pi.create_input_snapshot(
            run_id="run-a18",
            recipient="generator",
            phase="generation",
            output_path=self.root / "audits" / "a18.snapshot.md",
            repo_root=self.root,
        )
        self.assertEqual(pi.aggregate_observations(self.root)["by_version"], [])
        pi.record_snapshot_delivery(snapshot, repo_root=self.root)
        aggregate = pi.aggregate_observations(self.root)["by_version"][0]
        self.assertEqual(aggregate["knowledge_id"], record_id)
        self.assertEqual(aggregate["outcomes"], {"delivered": 1})

    def test_a19_retirement_review_is_removed_without_checker_mutation(self) -> None:
        before = (REPO_ROOT / "prompts" / "check_router_v6.md").read_bytes()
        completed = subprocess.run(
            [sys.executable, "scripts/process_improvement.py", "retirement-review"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("removed", completed.stderr)
        self.assertEqual(
            before, (REPO_ROOT / "prompts" / "check_router_v6.md").read_bytes()
        )

    def test_a20_result_observation_returns_to_same_id_and_version(self) -> None:
        record_id = self.create("a20")
        delta = {
            "schema_version": pi.DELTA_SCHEMA_VERSION,
            "reviewed": True,
            "items": [
                {
                    "action": "observe",
                    "knowledge_id": record_id,
                    "knowledge_version": 1,
                    "outcome": "action_confirmed",
                    "observation": "The coordinator recorded the prescribed comparison.",
                    "metrics": {
                        "input_bytes": 0,
                        "duration_seconds": None,
                        "revision_count": 0,
                    },
                }
            ],
        }
        pi.ingest_learning_delta(
            self.source("run-b-a20"),
            delta,
            repo_root=self.root,
        )
        aggregate = pi.aggregate_observations(self.root)["by_version"][0]
        self.assertEqual(aggregate["knowledge_id"], record_id)
        self.assertEqual(aggregate["knowledge_version"], 1)
        self.assertEqual(aggregate["outcomes"]["action_confirmed"], 1)
        missing = copy.deepcopy(delta)
        missing["items"][0]["knowledge_version"] = 99
        with self.assertRaisesRegex(ValueError, "missing knowledge version"):
            pi.ingest_learning_delta(
                self.source("a20-missing"), missing, repo_root=self.root
            )
        self.assertNotIn("duration_seconds", aggregate["measurements"])
        self.assertEqual(aggregate["measurements"]["input_bytes"]["sum"], 0.0)

    def test_a21_sem2_versions_keep_separate_history_and_observations(self) -> None:
        record_id = self.create("a21")
        old = json.loads(
            (
                self.root / "process_improvement" / "records" / f"{record_id}.json"
            ).read_text()
        )
        old["problem"]["action"] += " Record the sense identifier in the work table."
        old["evidence_observation"] = "A second synthetic run justified revising the action."
        pi.ingest_learning_delta(
            self.source("run-a21-revise"),
            {
                "schema_version": pi.DELTA_SCHEMA_VERSION,
                "reviewed": True,
                "items": [
                    {
                        "action": "revise",
                        "knowledge_id": record_id,
                        "expected_version": 1,
                        "record": old,
                    }
                ],
            },
            repo_root=self.root,
        )
        self.assertTrue(
            (
                self.root
                / "process_improvement"
                / "history"
                / f"{record_id}.v1.json"
            ).is_file()
        )
        self.assertEqual(pi._load_records(self.root)[0][0]["version"], 2)

    def test_a22_integrated_knowledge_is_not_redundantly_delivered(self) -> None:
        record_id = self.create("a22", status="integrated")
        selected = pi.select_knowledge(
            recipient="generator", phase="generation", repo_root=self.root
        )
        self.assertEqual(selected["selected"], [])
        self.assertEqual(
            next(row for row in selected["skipped"] if row["id"] == record_id)[
                "reason"
            ],
            "status:integrated",
        )

    def test_a23_input_limit_keeps_items_whole_and_adds_no_llm_call(self) -> None:
        self.create("a23-first")
        self.create("a23-second")
        selection = pi.select_knowledge(
            recipient="generator",
            phase="generation",
            max_items=1,
            max_bytes=2048,
            repo_root=self.root,
        )
        self.assertEqual(len(selection["selected"]), 1)
        self.assertTrue(any(row["reason"] == "item_limit" for row in selection["skipped"]))
        snapshot = pi.create_input_snapshot(
            run_id="a23",
            recipient="generator",
            phase="generation",
            output_path=self.root / "audits" / "a23.snapshot.md",
            max_items=1,
            max_bytes=2048,
            repo_root=self.root,
        )
        self.assertEqual(snapshot["additional_llm_calls"], 0)
        self.assertLessEqual(snapshot["input_bytes"], 2048)
        self.assertNotIn("…", (self.root / snapshot["snapshot_path"]).read_text())
        with self.assertRaisesRegex(ValueError, "empty input size"):
            pi.select_knowledge(
                recipient="generator",
                phase="generation",
                max_bytes=1,
                repo_root=self.root,
            )

    def test_a24_invalid_pi_falls_back_without_weakening_workflow(self) -> None:
        invalid_indexes = (
            "{broken",
            json.dumps(
                {
                    "schema_version": pi.INDEX_SCHEMA_VERSION,
                    "knowledge_epoch": "test-epoch-v2",
                    "records": [
                        {"id": "broken", "status": "active", "recipients": 3}
                    ],
                }
            ),
        )
        corrupt = self.root / "process_improvement" / "index.json"
        for index, content in enumerate(invalid_indexes):
            with self.subTest(index=index):
                corrupt.write_text(content, encoding="utf-8")
                _, manifest = run_word.create_guard_manifest(
                    "fallback-word",
                    repo_root=self.root,
                    branch="feat/test",
                    base_sha="b" * 40,
                    run_id=f"fallback-run-{index}",
                )
                snapshot = manifest["process_improvement"]["snapshots"][0]
                self.assertIn("fallback", snapshot)
                self.assertEqual(manifest["status"], "in_progress")
                self.assertEqual(len(manifest["orchestrator"]["checker_passes"]), 7)
                self.assertIn(
                    "final_blind",
                    [
                        stage["name"]
                        for stage in manifest["orchestrator"]["stages"]
                    ],
                )

    def test_a25_legacy_audit_remains_readable_but_is_not_counted(self) -> None:
        old = self.root / "audits" / "workflow_runs" / "old" / "run.json"
        old.parent.mkdir(parents=True)
        old.write_text(
            json.dumps(
                {
                    "status": "completed",
                    "metrics": {
                        "schema_version": "workflow_cost_v1",
                        "process_rules": [{"id": "PI-0001"}],
                    },
                }
            ),
            encoding="utf-8",
        )
        self.assertEqual(pi.validate_registry(self.root), [])
        self.assertEqual(pi.aggregate_observations(self.root)["by_version"], [])


if __name__ == "__main__":
    unittest.main()
