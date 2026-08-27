from __future__ import annotations

import json
import copy
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import content_audit  # noqa: E402
import check_passes  # noqa: E402
import generate_audit_manifest as generator  # noqa: E402
from tests.test_content_audit import ENTRY_TEXT  # noqa: E402
from tests.test_source_first_audit_gate import valid_v2_manifest  # noqa: E402


class GeneratedAuditManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "prompts").mkdir(parents=True)
        shutil.copy2(
            REPO_ROOT / "prompts" / "check_router_v6.md",
            self.root / "prompts" / "check_router_v6.md",
        )
        self.entry = self.root / "entries" / "s" / "sample.md"
        self.entry.parent.mkdir(parents=True)
        self.entry.write_text(ENTRY_TEXT, encoding="utf-8")
        self.cycle = self.root / "audits" / "runs" / "s" / "sample" / "cycle-001"
        self.cycle.mkdir(parents=True)
        self.audit = self.root / "audits" / "s" / "sample.json"
        self.audit.parent.mkdir(parents=True, exist_ok=True)
        self.body_hash = generator.body_sha256(self.entry)
        self._write_raw_fixture()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _metadata(self, stage: str, artifacts: list[str], identity: str) -> dict:
        return {
            "schema_version": f"{stage}_v2",
            "stage": stage,
            "run_id": f"{identity}-run",
            "context_id": f"{identity}-context",
            "input_body_sha256": self.body_hash,
            "prompt_sha256": "a" * 64,
            "input_artifacts": artifacts,
            "recorded_at": "2026-08-25T10:00:00+09:00",
        }

    def _write(self, name: str, value: dict) -> None:
        (self.cycle / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _results(ids: set[str] | dict[str, str], **extra: object) -> list[dict]:
        notes = ids if isinstance(ids, dict) else {}
        return [
            {
                "id": item_id,
                "status": "pass",
                "notes": notes.get(item_id, f"checked {item_id}"),
                **extra,
            }
            for item_id in sorted(ids)
        ]

    @staticmethod
    def _reviewer(model: str = "fixture-primary") -> dict:
        return {
            "mode": "handoff",
            "declared_model": model,
            "ingested_by": "human",
        }

    def _write_raw_fixture(self) -> None:
        source_gate = copy.deepcopy(valid_v2_manifest()["source_first_audit"])
        source = {
            **self._metadata(
                "source_inventory", ["headword", "source_first_spec"], "normal"
            ),
            "evidence_link_ids": [],
            "source_first_audit": source_gate,
        }
        self._write("source_inventory.json", source)
        router = json.loads(
            (REPO_ROOT / "prompts" / "check_router_v6.md")
            .read_text(encoding="utf-8")
            .split("<!-- CHECK_ROUTER_V6_JSON_BEGIN -->", 1)[1]
            .split("```json", 1)[1]
            .split("```", 1)[0]
        )
        attribution_request = next(
            item
            for item in check_passes.build_bundles(self.entry)
            if item["pass_id"] == "example-attribution"
        )
        attribution_record = {
            "schema_version": "example_attribution_blind_record_v1",
            "pass_id": "example-attribution",
            "input_body_sha256": self.body_hash,
            "blind_request_sha256": check_passes._digest_json(
                attribution_request
            ),
            "recorded_at": "2026-08-25T10:00:00+09:00",
            "reviewer": self._reviewer(),
            "attributions": [
                {
                    "example_id": attribution_request["input_sections"][
                        "collocations_examples"
                    ][0]["example_id"],
                    "classification": "unique",
                    "candidate_sense_ids": ["sense:001"],
                    "discriminating_terms": ["material", "sample"],
                    "rationale": "The material sample wording identifies sense 1.",
                }
            ],
        }
        normal = {
            **self._metadata(
                "normal_review",
                ["router_selected_sections", "checker_pass_specs"],
                "normal",
            ),
            "pass_outputs": [
                (
                    {
                        "pass_id": item["id"],
                        "reviewer": self._reviewer(),
                        "blind_attribution_record": attribution_record,
                        "aligned_at": "2026-08-25T10:00:01+09:00",
                        "findings": [],
                        "unrouted_observations": [],
                    }
                    if item["id"] == "example-attribution"
                    else {
                        "pass_id": item["id"],
                        "reviewer": self._reviewer(),
                        "findings": [],
                    }
                )
                for item in router["passes"]
            ],
            "independent_candidates": [
                {
                    "id": "NC-001",
                    "surface_form": "sample",
                    "frame": "a sample of something",
                    "meaning": "representative subset",
                    "disposition": "included",
                    "rationale": "present in the entry",
                }
            ],
        }
        self._write("pass_findings.json", normal)
        cold = {
            **self._metadata(
                "cold_review", ["entry_body", "cold_review_prompt"], "cold"
            ),
            "audit_visible": False,
            "reviewer": self._reviewer(),
            "findings": [],
        }
        self._write("cold_review.json", cold)
        resolutions = {
            **self._metadata(
                "resolutions", ["entry_body", "all_findings"], "normal"
            ),
            "resolutions": [],
        }
        self._write("resolutions.json", resolutions)
        blind = {
            **self._metadata(
                "final_blind", ["entry_body", "final_blind_prompt"], "final"
            ),
            "audit_visible": False,
            "reviewer": self._reviewer(),
            "provisional_decision": "pass",
            "independent_candidates": [
                {
                    "id": "IC-001",
                    "surface_form": "sample",
                    "frame": "a sample of something",
                    "meaning": "representative subset",
                    "disposition": "included",
                    "rationale": "The sample is independently inventoried as a representative subset.",
                    "semantic_assertions": [
                        {
                            "id": "IC-001:A1",
                            "statement": "the subset represents a larger whole",
                            "polarity": "must_hold",
                            "scope": "definitions and examples",
                        }
                    ],
                }
            ],
            "article_findings": [],
        }
        self._write("final_blind.json", blind)
        seal = generator.seal_blind(
            self.entry,
            self.cycle / "final_blind.json",
            self.cycle / "blind_seal.json",
            repo_root=self.root,
            sealed_at="2026-08-25T10:01:00+09:00",
        )
        target_items = content_audit.extract_targets(self.entry)
        relation_items = content_audit.extract_relations(target_items)
        targets = {item["id"]: item["text"] for item in target_items}
        relations = {item["id"]: item["description"] for item in relation_items}
        final = {
            **self._metadata(
                "final_review",
                [
                    "entry_body",
                    "all_findings",
                    "resolutions",
                    "sealed_final_blind",
                    "final_review_spec",
                ],
                "final",
            ),
            "recorded_at": "2026-08-25T10:02:00+09:00",
            "reviewer": self._reviewer(),
            "blind_output_sha256": seal["blind_output_sha256"],
            "target_results": self._results(targets),
            "relation_results": self._results(relations),
            "normal_candidate_results": self._results({"NC-001"}),
            "blind_candidate_results": self._results(
                {"IC-001"},
                assertion_ids=["IC-001:A1"],
                verified_body_sha256=self.body_hash,
            ),
            "finding_results": [],
            "evidence_checks": [],
            "source_inventory_results": [
                {
                    "id": "U1",
                    "union_id": "U1",
                    "status": "pass",
                    "notes": "directly checked source union",
                }
            ],
            "decision": "pass",
            "blockers": [],
            "notes": [],
        }
        self._write("final_review.json", final)
        self._write(
            "secondary_reviews.json",
            {
                "cold_review": {
                    "reviewer": self._reviewer("fixture-secondary"),
                    "findings": [],
                },
                "example_attribution": {
                    "reviewer": self._reviewer("fixture-secondary"),
                    "blind_attribution_record": {
                        **copy.deepcopy(attribution_record),
                        "reviewer": self._reviewer("fixture-secondary"),
                    },
                    "findings": [],
                },
            },
        )
        secondary_dir = self.cycle / "secondary_reviews"
        secondary_dir.mkdir()
        (secondary_dir / "example_attribution.request.json").write_text(
            json.dumps(attribution_request, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _generate(self) -> dict:
        value = generator.generate_manifest(
            self.entry, self.cycle, repo_root=self.root
        )
        self.audit.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return value

    def test_manifest_is_derived_and_valid_without_revision_snapshots(self) -> None:
        value = self._generate()
        self.assertEqual(value["schema_version"], "content_audit_v4")
        self.assertEqual(
            generator.validate_generated_manifest(
                self.entry, self.audit, repo_root=self.root
            ),
            [],
        )
        self.assertEqual(list(self.cycle.glob("revision-*.md")), [])
        self.assertNotIn("body_revisions", value)

    def test_legacy_build_cli_cannot_create_a_new_revision_snapshot(self) -> None:
        import subprocess

        output = self.root / "audits" / "legacy-build.json"
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "content_audit.py"),
                "build",
                str(self.entry),
                "--output",
                str(output),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("legacy snapshot build is retired", completed.stderr)
        self.assertFalse(output.exists())

    def test_manual_manifest_decision_cannot_diverge_from_raw_output(self) -> None:
        value = self._generate()
        value["final_decision"]["decision"] = "reject"
        self.audit.write_text(json.dumps(value), encoding="utf-8")
        errors = generator.validate_generated_manifest(
            self.entry, self.audit, repo_root=self.root
        )
        self.assertTrue(any("differs from raw outputs" in error for error in errors))

    def test_final_input_contract_excludes_generation_and_process_context(self) -> None:
        final = json.loads((self.cycle / "final_review.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(final["input_artifacts"]),
            {
                "entry_body",
                "all_findings",
                "resolutions",
                "sealed_final_blind",
                "final_review_spec",
            },
        )
        self.assertNotIn("ACTIVE.md", json.dumps(final))

    def test_missing_pass_output_is_rejected_before_manifest_generation(self) -> None:
        normal_path = self.cycle / "pass_findings.json"
        normal = json.loads(normal_path.read_text(encoding="utf-8"))
        normal["pass_outputs"].pop()
        normal_path.write_text(json.dumps(normal), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "pass set mismatch"):
            generator.generate_manifest(self.entry, self.cycle, repo_root=self.root)

    def test_manifest_rejects_review_stage_without_reviewer(self) -> None:
        cold_path = self.cycle / "cold_review.json"
        cold = json.loads(cold_path.read_text(encoding="utf-8"))
        cold.pop("reviewer")
        self._write("cold_review.json", cold)
        with self.assertRaisesRegex(ValueError, "reviewer"):
            generator.generate_manifest(self.entry, self.cycle, repo_root=self.root)

    def test_pre_contract_cycle_remains_readable_without_reviewer_fields(self) -> None:
        for name in ("cold_review.json", "final_blind.json", "final_review.json"):
            value = json.loads((self.cycle / name).read_text(encoding="utf-8"))
            value.pop("reviewer", None)
            self._write(name, value)
        generator.seal_blind(
            self.entry,
            self.cycle / "final_blind.json",
            self.cycle / "blind_seal.json",
            repo_root=self.root,
            sealed_at="2026-08-25T10:01:00+09:00",
        )
        normal = json.loads((self.cycle / "pass_findings.json").read_text())
        normal["pass_outputs"] = [
            output
            for output in normal["pass_outputs"]
            if output.get("pass_id") != "example-attribution"
        ]
        for output in normal["pass_outputs"]:
            output.pop("reviewer", None)
        self._write("pass_findings.json", normal)
        with mock.patch.object(generator, "_is_historical_cycle", return_value=True):
            value = generator.generate_manifest(
                self.entry, self.cycle, repo_root=self.root
            )
        self.assertNotIn("invalidated_by", value)

    def test_api_review_is_bound_to_request_and_preserved_raw_response(self) -> None:
        cold_path = self.cycle / "cold_review.json"
        cold = json.loads(cold_path.read_text(encoding="utf-8"))
        request = {"stage": "cold_review", "entry_body": "fixture"}
        cold["reviewer"] = {
            "mode": "api",
            "provider": "openai",
            "model": "fixture-api",
            "response_id": "resp-cold",
            "request_sha256": generator.review_liveness.request_sha256(request),
        }
        self._write("cold_review.json", cold)
        with self.assertRaisesRegex(ValueError, "request payload is missing"):
            generator.generate_manifest(self.entry, self.cycle, repo_root=self.root)

        self._write("cold_review.request.json", request)
        with self.assertRaisesRegex(ValueError, "no preserved raw API response"):
            generator.generate_manifest(self.entry, self.cycle, repo_root=self.root)

        raw_dir = self.cycle / "raw"
        raw_dir.mkdir()
        (raw_dir / "cold_review.response.json").write_text(
            json.dumps({"id": "resp-cold", "output_text": "{}"}),
            encoding="utf-8",
        )
        generator.generate_manifest(self.entry, self.cycle, repo_root=self.root)

    def test_native_cold_finding_schema_is_preserved_during_generation(self) -> None:
        cold_path = self.cycle / "cold_review.json"
        cold = json.loads(cold_path.read_text(encoding="utf-8"))
        cold["findings"] = [
            {
                "id": "CR-001",
                "location": "first sense definition",
                "severity": "medium",
                "description": "The boundary may be overgeneralized.",
                "reason": "The representative subset definition makes an absolute claim.",
                "suggested_direction": "Narrow the stated scope.",
                "scope_anchors": [
                    {
                        "id": "CR-001:A1",
                        "exact_quote": "representative subset",
                        "location_hint": "sense 1 definition",
                    }
                ],
            }
        ]
        self._write("cold_review.json", cold)

        resolutions = json.loads(
            (self.cycle / "resolutions.json").read_text(encoding="utf-8")
        )
        resolutions["resolutions"] = [
            {
                "id": "CR-001",
                "finding_id": "CR-001",
                "status": "resolved",
                "disposition": "rejected",
                "rationale": "The candidate quote is already explicitly bounded.",
                "resolved_body_sha256": self.body_hash,
            }
        ]
        self._write("resolutions.json", resolutions)

        final = json.loads(
            (self.cycle / "final_review.json").read_text(encoding="utf-8")
        )
        final["finding_results"] = [
            {
                "id": "CR-001",
                "status": "pass",
                "notes": "Checked the raw cold finding and its resolution.",
            }
        ]
        self._write("final_review.json", final)

        value = self._generate()
        self.assertEqual(value["findings"][0]["severity"], "medium")
        self.assertEqual(
            value["findings"][0]["scope_anchors"][0]["exact_quote"],
            "representative subset",
        )


if __name__ == "__main__":
    unittest.main()
