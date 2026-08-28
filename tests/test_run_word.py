from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import entry_workflow_guard as guard  # noqa: E402
import run_word  # noqa: E402
import check_passes  # noqa: E402


class RunWordTests(unittest.TestCase):
    def test_dry_run_prints_complete_stage_contract_without_writing(self) -> None:
        before = set((REPO_ROOT / "audits" / "workflow_runs").rglob("*.json"))
        completed = subprocess.run(
            [sys.executable, "scripts/run_word.py", "--dry-run", "test word"],
            cwd=REPO_ROOT,
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["entry_path"], "entries/t/test-word.md")
        self.assertEqual(
            [stage["name"] for stage in payload["stages"]],
            [
                "guard_start",
                "generation",
                "mechanical_validator",
                "checker_passes",
                "cold_review",
                "final_blind",
                "blind_seal",
                "finding_resolution",
                "final_review",
                "status_update",
                "export",
            ],
        )
        self.assertEqual(
            set((REPO_ROOT / "audits" / "workflow_runs").rglob("*.json")),
            before,
        )
        for stage in payload["stages"]:
            self.assertIn("input_scope", stage)
            self.assertIn("specification_files", stage)
            self.assertIn("output_paths", stage)
            self.assertIsInstance(stage["instruction_bytes"], int)
        review_stages = {
            stage["name"]: stage
            for stage in payload["stages"]
            if stage["name"] in run_word.REVIEW_STAGES
        }
        self.assertEqual(set(review_stages), run_word.REVIEW_STAGES)
        self.assertTrue(
            all(
                stage["reviewer_mode"] == "api" and stage["input_packet_path"]
                for stage in review_stages.values()
            )
        )
        self.assertEqual(len(payload["checker_passes"]), 7)
        self.assertTrue(
            all(item["instruction_bytes"] <= 15_000 for item in payload["checker_passes"])
        )
        attribution = next(
            item
            for item in payload["checker_passes"]
            if item["id"] == "example-attribution"
        )
        self.assertIn("stage1_output_path", attribution)
        self.assertIn("alignment_key_path", attribution)
        frame = next(
            item
            for item in payload["checker_passes"]
            if item["id"] == "frame-relation"
        )
        self.assertEqual(
            frame["specification"], "prompts/check_pass_frame_relation_v7.md"
        )
        for key in (
            "stage1_output_path",
            "stage2_request_path",
            "stage2_output_path",
            "alignment_key_path",
        ):
            self.assertIn(key, frame)

    def test_context_free_stages_receive_no_project_history(self) -> None:
        by_name = {
            stage.name: stage for stage in run_word.build_plan("obvious")
        }
        self.assertEqual(
            by_name["cold_review"].input_scope,
            ("entry body without front matter",),
        )
        self.assertEqual(
            by_name["final_blind"].input_scope, ("latest entry body only",)
        )
        for name in ("cold_review", "final_blind"):
            joined = " ".join(
                by_name[name].input_scope
                + by_name[name].specification_files
            )
            self.assertNotIn("ACTIVE.md", joined)
            self.assertNotIn("finding", joined)

    def test_handoff_packet_is_prepared_and_blind_record_is_reconciled_on_ingest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(REPO_ROOT / "prompts", root / "prompts")
            (root / "audits").mkdir()
            shutil.copy2(
                REPO_ROOT / "audits" / "escaped_defect_taxonomy.json",
                root / "audits" / "escaped_defect_taxonomy.json",
            )
            entry = root / "entries" / "s" / "sample.md"
            entry.parent.mkdir(parents=True)
            shutil.copy2(
                REPO_ROOT / "tests" / "fixtures" / "example_attribution_polysemous.md",
                entry,
            )
            manifest = {
                "entry_path": "entries/s/sample.md",
                "run_id": "handoff-run",
                "orchestrator": run_word.plan_payload(
                    "sample", root, reviewer_mode="handoff"
                ),
                "orchestrator_state": {
                    "next_stage_index": 3,
                    "completed_stages": [
                        "guard_start",
                        "generation",
                        "mechanical_validator",
                    ],
                    "stage_outputs": {},
                },
            }
            packet_path = run_word.prepare_handoff(manifest, repo_root=root)
            self.assertTrue(packet_path.is_file())
            self.assertIn("Independent review handoff", packet_path.read_text())

            cycle = root / "audits" / "runs" / "s" / "sample" / "handoff-run"
            check_dir = cycle / "check_passes"
            request = json.loads(
                (check_dir / "example-attribution.request.json").read_text()
            )
            alignment = json.loads(
                (check_dir / "example-attribution.alignment-key.json").read_text()
            )
            owner = {
                item["example_id"]: item["assigned_sense_id"]
                for item in alignment["examples"]
            }
            attributions = []
            for item in request["input_sections"]["collocations_examples"]:
                quote = item["example"]
                attributions.append(
                    {
                        "example_id": item["example_id"],
                        "classification": "unique",
                        "candidate_sense_ids": [owner[item["example_id"]]],
                        "discriminating_terms": [quote],
                        "rationale": f"The exact wording {quote} identifies this use.",
                    }
                )
            record = {
                "schema_version": "example_attribution_blind_record_v1",
                "pass_id": "example-attribution",
                "input_body_sha256": request["input_body_sha256"],
                "blind_request_sha256": check_passes._digest_json(request),
                "recorded_at": "2020-01-01T00:00:00+00:00",
                "attributions": attributions,
            }
            antonym_request = json.loads(
                (check_dir / "frame-relation.request.json").read_text()
            )
            antonym_record = {
                "schema_version": "antonym_axis_blind_record_v1",
                "pass_id": "frame-relation",
                "input_body_sha256": antonym_request["input_body_sha256"],
                "blind_request_sha256": check_passes._digest_json(
                    antonym_request
                ),
                "recorded_at": "2020-01-01T00:00:00+00:00",
                "axes": [],
            }
            router = check_passes.load_router(root / "prompts" / "check_router_v6.md")
            outputs = [
                (
                    {
                        "pass_id": item["id"],
                        "blind_attribution_record": record,
                    }
                    if item["id"] == "example-attribution"
                    else (
                        {
                            "pass_id": item["id"],
                            "antonym_axis_blind_record": antonym_record,
                        }
                        if item["id"] == "frame-relation"
                        else {"pass_id": item["id"], "findings": []}
                    )
                )
                for item in router["passes"]
            ]
            response = cycle / "handoff" / "checker_passes.response.json"
            response.write_text(json.dumps({"pass_outputs": outputs}), encoding="utf-8")
            stage2_handoff = run_word.ingest_handoff_review(
                manifest,
                stage="checker_passes",
                declared_model="independent-reviewer",
                repo_root=root,
            )
            self.assertEqual(
                stage2_handoff.name, "checker_passes.stage2.request.md"
            )
            with self.assertRaisesRegex(
                ValueError, "stage 1 is already ingested"
            ):
                run_word.ingest_handoff_review(
                    manifest,
                    stage="checker_passes",
                    declared_model="independent-reviewer",
                    repo_root=root,
                )
            stage2_request = json.loads(
                (
                    check_dir
                    / "frame-relation.antonym-axis.stage2.request.json"
                ).read_text()
            )
            stage2_response = {
                "schema_version": "antonym_axis_adjudication_record_v1",
                "pass_id": "frame-relation",
                "input_body_sha256": stage2_request["input_body_sha256"],
                "stage2_request_sha256": check_passes._digest_json(stage2_request),
                "blind_record_sha256": stage2_request["blind_record_sha256"],
                "adjudications": [],
                "frame_findings": [],
                "unrouted_observations": [],
            }
            (cycle / "handoff" / "checker_passes.stage2.response.json").write_text(
                json.dumps(stage2_response), encoding="utf-8"
            )
            target = run_word.ingest_handoff_review(
                manifest,
                stage="checker_passes",
                declared_model="independent-reviewer",
                repo_root=root,
            )
            ingested = json.loads(target.read_text())
            attribution = next(
                item
                for item in ingested["pass_outputs"]
                if item["pass_id"] == "example-attribution"
            )
            self.assertIn("aligned_at", attribution)
            self.assertTrue(
                all(
                    row["example_id"].startswith("ex-")
                    for row in attribution["blind_attribution_record"]["attributions"]
                )
            )
            frame = next(
                item
                for item in ingested["pass_outputs"]
                if item["pass_id"] == "frame-relation"
            )
            self.assertIn("antonym_axis_blind_record", frame)
            self.assertIn("antonym_axis_adjudication_record", frame)
            with self.assertRaisesRegex(ValueError, "must differ"):
                run_word.ingest_handoff_review(
                    manifest,
                    stage="checker_passes",
                    declared_model="synthetic-fixture",
                    repo_root=root,
                )

    def test_api_mode_materializes_run_bound_checker_requests(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(REPO_ROOT / "prompts", root / "prompts")
            (root / "audits").mkdir()
            shutil.copy2(
                REPO_ROOT / "audits" / "escaped_defect_taxonomy.json",
                root / "audits" / "escaped_defect_taxonomy.json",
            )
            entry = root / "entries" / "s" / "sample.md"
            entry.parent.mkdir(parents=True)
            shutil.copy2(
                REPO_ROOT / "tests" / "fixtures" / "example_attribution_polysemous.md",
                entry,
            )
            manifest = {
                "entry_path": "entries/s/sample.md",
                "run_id": "api-run",
                "orchestrator": run_word.plan_payload(
                    "sample", root, reviewer_mode="api"
                ),
                "orchestrator_state": {
                    "next_stage_index": 3,
                    "completed_stages": [
                        "guard_start",
                        "generation",
                        "mechanical_validator",
                    ],
                    "stage_outputs": {},
                },
            }
            paths, packet = run_word.prepare_review_inputs(
                manifest, repo_root=root
            )
            self.assertEqual(packet["stage"], "checker_passes")
            self.assertEqual(len([path for path in paths if path.name.endswith(".request.json")]), 7)
            self.assertTrue(
                any(path.name == "example-attribution.alignment-key.json" for path in paths)
            )
            self.assertTrue(
                any(
                    path.name
                    == "frame-relation.antonym-axis.alignment-key.json"
                    for path in paths
                )
            )
            attribution = next(
                item for item in packet["requests"]
                if item["pass_id"] == "example-attribution"
            )
            self.assertTrue(
                all(
                    item["example_id"].startswith("ex-")
                    for item in attribution["input_sections"]["collocations_examples"]
                )
            )

    def test_api_mode_calls_validates_and_mechanically_aggregates_checker_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(REPO_ROOT / "prompts", root / "prompts")
            (root / "audits").mkdir()
            shutil.copy2(
                REPO_ROOT / "audits" / "escaped_defect_taxonomy.json",
                root / "audits" / "escaped_defect_taxonomy.json",
            )
            entry = root / "entries" / "s" / "sample.md"
            entry.parent.mkdir(parents=True)
            shutil.copy2(
                REPO_ROOT / "tests" / "fixtures" / "example_attribution_polysemous.md",
                entry,
            )
            manifest = {
                "entry_path": "entries/s/sample.md",
                "run_id": "api-call-run",
                "orchestrator": run_word.plan_payload(
                    "sample", root, reviewer_mode="api"
                ),
                "orchestrator_state": {
                    "next_stage_index": 3,
                    "completed_stages": [
                        "guard_start",
                        "generation",
                        "mechanical_validator",
                    ],
                    "stage_outputs": {},
                },
            }

            def provider_response(
                provider: str,
                *,
                model: str,
                api_key: str,
                prompt: str,
                request_payload: dict[str, object],
                endpoint: str | None = None,
            ) -> dict[str, object]:
                pass_id = str(request_payload["pass_id"])
                schema = str(request_payload.get("schema_version", ""))
                if schema == "antonym_axis_blind_request_v1":
                    sections = request_payload["input_sections"]
                    assert isinstance(sections, dict)
                    items = sections["antonym_items"]
                    assert isinstance(items, list)
                    payload = {
                        "schema_version": "antonym_axis_blind_record_v1",
                        "pass_id": pass_id,
                        "input_body_sha256": request_payload["input_body_sha256"],
                        "blind_request_sha256": check_passes._digest_json(
                            request_payload
                        ),
                        "recorded_at": "2020-01-01T00:00:00+00:00",
                        "axes": [
                            {
                                "item_id": item["item_id"],
                                "axis": "状態",
                                "relation_type": "状態",
                                "reason": "The definition supplies a state opposition.",
                            }
                            for item in items
                        ],
                    }
                elif schema == "antonym_axis_adjudication_request_v1":
                    sections = request_payload["input_sections"]
                    assert isinstance(sections, dict)
                    items = sections["antonym_axis_items"]
                    assert isinstance(items, list)
                    payload = {
                        "schema_version": "antonym_axis_adjudication_record_v1",
                        "pass_id": pass_id,
                        "input_body_sha256": request_payload["input_body_sha256"],
                        "stage2_request_sha256": check_passes._digest_json(
                            request_payload
                        ),
                        "blind_record_sha256": request_payload[
                            "blind_record_sha256"
                        ],
                        "adjudications": [
                            {
                                "item_id": item["item_id"],
                                "flags": [],
                                "rationale": "The named axis remains grounded after disclosure.",
                            }
                            for item in items
                        ],
                        "frame_findings": [],
                        "unrouted_observations": [],
                    }
                elif pass_id == "example-attribution":
                    sections = request_payload["input_sections"]
                    assert isinstance(sections, dict)
                    senses = sections["sense_structure"]
                    examples = sections["collocations_examples"]
                    assert isinstance(senses, list) and isinstance(examples, list)
                    candidate = str(senses[0]["sense_id"])
                    payload = {
                        "schema_version": "example_attribution_blind_record_v1",
                        "pass_id": pass_id,
                        "input_body_sha256": request_payload["input_body_sha256"],
                        "blind_request_sha256": check_passes._digest_json(
                            request_payload
                        ),
                        "recorded_at": "2020-01-01T00:00:00+00:00",
                        "attributions": [
                            {
                                "example_id": item["example_id"],
                                "classification": "unique",
                                "candidate_sense_ids": [candidate],
                                "discriminating_terms": [item["example"]],
                                "rationale": (
                                    "The exact wording " + str(item["example"])
                                    + " identifies this use."
                                ),
                            }
                            for item in examples
                        ],
                    }
                else:
                    payload = {"pass_id": pass_id, "findings": []}
                return {
                    "id": f"resp-{pass_id}",
                    "output_text": json.dumps(payload),
                }

            with mock.patch.object(
                run_word.review_call,
                "call_provider",
                side_effect=provider_response,
            ):
                paths = run_word.execute_api_review_stage(
                    manifest,
                    repo_root=root,
                    provider="openai",
                    model="independent-reviewer",
                    api_key="not-used",
                )

            cycle = root / "audits" / "runs" / "s" / "sample" / "api-call-run"
            aggregate = json.loads((cycle / "pass_findings.json").read_text())
            self.assertEqual(len(aggregate["pass_outputs"]), 7)
            self.assertTrue(all(item.get("reviewer") for item in aggregate["pass_outputs"]))
            attribution = next(
                item
                for item in aggregate["pass_outputs"]
                if item["pass_id"] == "example-attribution"
            )
            self.assertIn("aligned_at", attribution)
            self.assertTrue(
                (cycle / "check_passes" / "example-attribution.blind-record.json").is_file()
            )
            self.assertTrue(
                (
                    cycle
                    / "check_passes"
                    / "frame-relation.antonym-axis.blind-record.json"
                ).is_file()
            )
            self.assertTrue(
                (
                    cycle
                    / "check_passes"
                    / "frame-relation.antonym-axis.adjudication-record.json"
                ).is_file()
            )
            self.assertEqual(len(list((cycle / "raw").glob("checker-*.response.json"))), 8)
            self.assertIn(cycle / "pass_findings.json", paths)

    def test_acceptance_d1_requires_blocking_example_attribution_finding(self) -> None:
        expected = [
            {
                "id": "D1",
                "taxonomy_id": "example_sense_attribution_mismatch",
                "exact_quote": "target quote",
            }
        ]
        wrong_stage = {
            "stage": "cold_review",
            "taxonomy_id": "example_sense_attribution_mismatch",
            "severity": "blocking",
            "location": {"exact_quote": "target quote"},
        }
        self.assertFalse(
            run_word.match_acceptance_defects(expected, [wrong_stage], [])[0][
                "detected"
            ]
        )
        correct = {
            **wrong_stage,
            "stage": "check_pass:example-attribution",
        }
        self.assertTrue(
            run_word.match_acceptance_defects(expected, [correct], [])[0][
                "detected"
            ]
        )

    def test_guard_start_uses_guard_manifest_and_keeps_budget_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            started = datetime(2026, 8, 25, tzinfo=timezone.utc)
            path, manifest = run_word.create_guard_manifest(
                "obvious",
                repo_root=root,
                branch="word/obvious",
                base_sha="a" * 40,
                run_id="test-run",
                now=started,
            )
            self.assertTrue(path.is_file())
            self.assertEqual(manifest["schema_version"], guard.SCHEMA_VERSION)
            self.assertEqual(
                manifest["limits"], guard.PROFILES["standard"]
            )
            self.assertEqual(
                manifest["orchestrator"]["orchestrator_version"],
                "run_word_v3",
            )
            self.assertEqual(manifest["metrics"]["total_cycles"], 1)
            self.assertEqual(manifest["metrics"]["total_revisions"], 0)
            self.assertEqual(
                [item["id"] for item in manifest["metrics"]["checker_passes"]],
                [item["id"] for item in manifest["orchestrator"]["checker_passes"]],
            )
            reloaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(reloaded, manifest)

    def test_heartbeat_stops_instead_of_extending_budget(self) -> None:
        started = datetime(2026, 8, 25, tzinfo=timezone.utc)
        manifest = guard.new_manifest(
            headword="obvious",
            entry_path="entries/o/obvious.md",
            branch="word/obvious",
            base_sha="a" * 40,
            now=started,
        )
        deadline = manifest["deadline_at"]
        self.assertFalse(
            run_word.heartbeat_manifest(
                manifest, now=started + timedelta(minutes=11)
            )
        )
        self.assertEqual(manifest["status"], "budget_exhausted")
        self.assertEqual(manifest["deadline_at"], deadline)

    def test_guard_checkpoint_mapping_is_ordered(self) -> None:
        planned = [
            checkpoint
            for stage in run_word.build_plan("obvious")
            for checkpoint in stage.guard_checkpoints
        ]
        self.assertEqual(planned, list(guard.STAGES))

    def test_cost_metrics_record_stage_pass_rule_and_total_revision_cost(self) -> None:
        started = datetime(2026, 8, 25, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "prompts").mkdir()
            shutil.copy2(
                REPO_ROOT / "prompts" / "check_router_v6.md",
                root / "prompts" / "check_router_v6.md",
            )
            _, value = run_word.create_guard_manifest(
                "obvious",
                repo_root=root,
                branch="word/obvious",
                base_sha="a" * 40,
                run_id="cost-run",
                now=started,
            )
            run_word.record_cost(
                value,
                collection="stages",
                item_id="generation",
                input_bytes=128,
                duration_seconds=3.5,
                defects_detected=0,
                revision_count=1,
            )
            run_word.record_cost(
                value,
                collection="checker_passes",
                item_id="translation",
                input_bytes=512,
                duration_seconds=1.25,
                defects_detected=2,
            )
            run_word.begin_additional_cycle(value)
            run_word.finalize_cost_metrics(
                value, now=started + timedelta(seconds=20)
            )
            self.assertEqual(value["metrics"]["total_cycles"], 2)
            self.assertEqual(value["metrics"]["total_revisions"], 1)
            self.assertEqual(value["metrics"]["total_duration_seconds"], 20)
            translation = next(
                item
                for item in value["metrics"]["checker_passes"]
                if item["id"] == "translation"
            )
            self.assertEqual(translation["input_bytes"], 512)
            self.assertEqual(translation["defects_detected"], 2)

    def test_final_reconciliation_gets_only_the_v2_input_bundle(self) -> None:
        by_name = {stage.name: stage for stage in run_word.build_plan("obvious")}
        final = by_name["final_review"]
        self.assertEqual(
            final.input_scope,
            (
                "latest entry body",
                "sealed final-blind output",
                "all checker, cold, and sealed final-blind findings",
                "finding resolution records",
            ),
        )
        self.assertEqual(
            final.specification_files, ("prompts/final_review_spec_v2.md",)
        )

    def test_orchestrator_completes_every_stage_in_order_with_costs(self) -> None:
        started = datetime(2026, 8, 25, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "prompts").mkdir()
            shutil.copy2(
                REPO_ROOT / "prompts" / "check_router_v6.md",
                root / "prompts" / "check_router_v6.md",
            )
            _, value = run_word.create_guard_manifest(
                "obvious",
                repo_root=root,
                branch="word/obvious",
                base_sha="a" * 40,
                run_id="e2e-run",
                now=started,
            )
            confirmed_at = started + timedelta(seconds=1)
            value["remote_checkpoint"] = {
                "confirmed": True,
                "confirmed_at": guard._format_time(confirmed_at),
                "commit_sha": "b" * 40,
            }
            value["stage"] = "preflight_pushed"
            value["stage_history"].append(
                {
                    "stage": "preflight_pushed",
                    "recorded_at": guard._format_time(confirmed_at),
                    "notes": "test checkpoint",
                }
            )
            value["last_heartbeat_at"] = guard._format_time(confirmed_at)
            while (request := run_word.next_stage_request(value)) is not None:
                pass_costs = None
                if request["name"] == "checker_passes":
                    pass_costs = {
                        item["id"]: {
                            "input_bytes": 100,
                            "duration_seconds": 0.1,
                            "defects_detected": 0,
                        }
                        for item in value["metrics"]["checker_passes"]
                    }
                run_word.complete_orchestrated_stage(
                    value,
                    stage=request["name"],
                    input_bytes=100,
                    duration_seconds=0.5,
                    revision_count=1 if request["name"] == "generation" else 0,
                    checker_pass_costs=pass_costs,
                    now=started + timedelta(minutes=2),
                    verify_outputs=False,
                )
            self.assertEqual(value["status"], "completed")
            self.assertEqual(value["metrics"]["total_cycles"], 1)
            self.assertEqual(value["metrics"]["total_revisions"], 1)
            self.assertEqual(
                value["orchestrator_state"]["completed_stages"],
                [item["name"] for item in value["orchestrator"]["stages"]],
            )
            self.assertEqual(guard.validate_manifest(value, merge_ready=True), [])

    def test_stage_cannot_complete_without_exact_planned_outputs(self) -> None:
        started = datetime(2026, 8, 25, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "prompts").mkdir()
            shutil.copy2(
                REPO_ROOT / "prompts" / "check_router_v6.md",
                root / "prompts" / "check_router_v6.md",
            )
            _, value = run_word.create_guard_manifest(
                "obvious",
                repo_root=root,
                branch="word/obvious",
                base_sha="a" * 40,
                run_id="output-run",
                now=started,
            )
            value["remote_checkpoint"] = {
                "confirmed": True,
                "confirmed_at": guard._format_time(started),
                "commit_sha": "b" * 40,
            }
            value["stage"] = "preflight_pushed"
            value["stage_history"].append(
                {
                    "stage": "preflight_pushed",
                    "recorded_at": guard._format_time(started),
                    "notes": "test checkpoint",
                }
            )
            with self.assertRaisesRegex(ValueError, "stage outputs do not exist"):
                run_word.complete_orchestrated_stage(
                    value,
                    stage="generation",
                    input_bytes=10,
                    duration_seconds=1,
                    repo_root=root,
                )
            self.assertEqual(
                value["orchestrator_state"]["completed_stages"], ["guard_start"]
            )

    def test_record_revision_commits_only_the_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"], cwd=root, check=True
            )
            entry = root / "entries" / "t" / "test.md"
            entry.parent.mkdir(parents=True)
            entry.write_text("first\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "initial"], cwd=root, check=True)
            entry.write_text("second\n", encoding="utf-8")
            sha = run_word.record_entry_revision(
                entry, "adopt resolved finding", repo_root=root, push=False
            )
            changed = subprocess.run(
                ["git", "show", "--pretty=", "--name-only", sha],
                cwd=root,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.splitlines()
            self.assertEqual(changed, ["entries/t/test.md"])
            self.assertFalse((root / "audits" / "runs").exists())


class ResumeIngestFailureTests(unittest.TestCase):
    def _manifest_path(self, root: Path) -> Path:
        manifest = guard.new_manifest(
            headword="sample",
            entry_path="entries/s/sample.md",
            branch="add/sample",
            base_sha="a" * 40,
            run_id="resume-run",
        )
        manifest["remote_checkpoint"] = {
            "confirmed": True,
            "confirmed_at": manifest["started_at"],
            "commit_sha": "b" * 40,
        }
        path = root / "resume-run.json"
        guard._write(path, manifest)
        return path

    def test_failed_ingestion_is_charged_to_the_guard_instead_of_raising(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self._manifest_path(Path(directory))
            failure = ValueError(
                "handoff response is missing: handoff/checker_passes.stage2.response.json"
            )
            with mock.patch.object(
                run_word, "ingest_handoff_review", side_effect=failure
            ):
                for attempt in range(1, guard.MAX_REVIEW_INGEST_FAILURES):
                    code = run_word._resume(
                        path,
                        ingest_review="checker_passes",
                        declared_model="independent-reviewer",
                    )
                    self.assertEqual(code, 1)
                    manifest = guard._read(path)
                    self.assertEqual(
                        manifest["review_ingest_failures"]["count"], attempt
                    )
                    self.assertEqual(manifest["status"], "in_progress")
                code = run_word._resume(
                    path,
                    ingest_review="checker_passes",
                    declared_model="independent-reviewer",
                )
            self.assertEqual(code, 2)
            manifest = guard._read(path)
            self.assertEqual(manifest["status"], "budget_exhausted")
            self.assertIn("checker_passes", manifest["stop_reason"])
            self.assertEqual(guard.validate_manifest(manifest), [])
            self.assertEqual(
                run_word._resume(
                    path,
                    ingest_review="checker_passes",
                    declared_model="independent-reviewer",
                ),
                2,
            )


if __name__ == "__main__":
    unittest.main()
