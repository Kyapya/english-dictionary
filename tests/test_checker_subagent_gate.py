from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import checker_subagent_gate as gate  # noqa: E402
import compact_workflow as compact  # noqa: E402
from tests.test_content_audit import ENTRY_TEXT  # noqa: E402


PASS_IDS = [
    "translation",
    "sense-structure",
    "frame-relation",
    "example-attribution",
    "qualification",
    "pronunciation",
    "evidence",
]


class CheckerSubagentGateTests(unittest.TestCase):
    def _write_run(
        self,
        root: Path,
        *,
        duplicate_agent: bool = False,
        protocol: str | None = gate.PROTOCOL_VERSION,
    ) -> dict[str, object]:
        run_id = "gate-run"
        pass_path = root / "audits" / "runs" / "s" / "sample" / run_id / "pass_findings.json"
        pass_path.parent.mkdir(parents=True, exist_ok=True)
        outputs = []
        for index, pass_id in enumerate(PASS_IDS):
            outputs.append(
                {
                    "pass_id": pass_id,
                    "findings": [],
                    "reviewer": {
                        "mode": "handoff",
                        "declared_model": "same-review-model",
                        "ingested_by": "human",
                        "agent_id": "same-subagent" if duplicate_agent else f"subagent-{index}",
                    },
                }
            )
        pass_path.write_text(
            json.dumps({"pass_outputs": outputs}, ensure_ascii=False),
            encoding="utf-8",
        )
        orchestrator: dict[str, object] = {
            "reviewer_mode": "handoff",
            "checker_subagent_count": 7,
            "checker_passes": [{"id": pass_id} for pass_id in PASS_IDS],
            "stages": [
                {
                    "name": "checker_passes",
                    "output_paths": [
                        "audits/runs/s/sample/{run_id}/source_inventory.json",
                        "audits/runs/s/sample/{run_id}/check_passes/",
                        "audits/runs/s/sample/{run_id}/pass_findings.json",
                    ],
                }
            ],
        }
        if protocol is not None:
            orchestrator["checker_execution_protocol"] = protocol
        return {
            "run_id": run_id,
            "status": "completed",
            "orchestrator": orchestrator,
        }

    def test_same_model_distinct_subagents_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._write_run(root)
            self.assertEqual(
                gate.validate_manifest_subagents(
                    manifest, repo_root=root, merge_ready=True
                ),
                [],
            )

    def test_duplicate_subagent_id_fails_even_when_model_rule_is_satisfied(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._write_run(root, duplicate_agent=True)
            errors = gate.validate_manifest_subagents(
                manifest, repo_root=root, merge_ready=True
            )
            self.assertTrue(any("unique reviewer.agent_id" in error for error in errors))
            self.assertFalse(any("declared_model" in error and "unique" in error for error in errors))

    def test_legacy_runs_are_not_retroactively_invalidated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self._write_run(root, duplicate_agent=True, protocol=None)
            self.assertEqual(
                gate.validate_manifest_subagents(
                    manifest, repo_root=root, merge_ready=True
                ),
                [],
            )


class ChangedProtocolGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.relative = "audits/workflow_runs/sample/run-1.json"
        self.run = self.root / self.relative
        self.run.parent.mkdir(parents=True)

    def _changed(self, manifest, *, old=None, extra=()):
        self.run.write_text(json.dumps(manifest), encoding="utf-8")
        previous = SimpleNamespace(returncode=1 if old is None else 0,
                                   stdout=json.dumps(old).encode("utf-8"))
        paths = "\n".join([self.relative, *extra])
        with patch.object(gate.subprocess, "check_output", return_value=paths), \
                patch.object(gate.subprocess, "run", return_value=previous):
            return gate.validate_changed_protocol("base", "head", self.root)

    def _completed_compact(self):
        (self.root / "prompts").mkdir()
        shutil.copy2(REPO_ROOT / "prompts/compact_review_contract_v1.json",
                     self.root / "prompts/compact_review_contract_v1.json")
        entry = self.root / "entries/s/sample.md"
        entry.parent.mkdir(parents=True)
        entry.write_text(ENTRY_TEXT, encoding="utf-8")
        compact._save(self.root / "inventory.json", {"source_first_audit": {
            "sources": [
                {"source_type": "learner_dictionary", "locator": "https://example.com/one",
                 "independence_group": "one"},
                {"source_type": "general_dictionary", "locator": "https://example.com/two",
                 "independence_group": "two"}],
            "source_union": [], "claim_units": []}})
        manifest = {"workflow_contract_version": compact.VERSION, "run_id": "run-1",
                    "entry_path": "entries/s/sample.md", "inventory_path": "inventory.json",
                    "review_receipts": [], "resolutions": [], "status": "in_progress"}
        for role in ("A", "B"):
            request = compact.prepare(manifest, self.run, role, root=self.root)
            raw = request.parent / f"{role}.raw.json"
            compact._save(raw, {"schema_version": "compact_review_response_v1",
                                "checked_areas": list(compact.current(manifest, self.root)["areas"]),
                                "unchecked_areas": [], "findings": []})
            compact.ingest(manifest, self.run, role, request, raw,
                           execution_id=f"reviewer-{role}", model="test-reviewer", root=self.root)
        compact.finalize(manifest, self.run, root=self.root)
        return manifest

    def test_compact_draft_and_nested_evidence_are_not_legacy_runs(self):
        nested = self.run.with_suffix("") / "compact"
        nested.mkdir(parents=True)
        for name in ("review-A.request.json", "review-B.request.json", "snapshot.json"):
            # Even non-object evidence must not be parsed as a run manifest.
            (nested / name).write_text("[]", encoding="utf-8")
        extra = [str(path.relative_to(self.root)) for path in nested.iterdir()]
        extra.append("audits/workflow_runs/README.md")
        self.assertEqual(self._changed({"workflow_contract_version": compact.VERSION,
                                      "run_id": "run-1", "status": "in_progress"}, extra=extra), [])
        self.assertEqual(gate.validate_all(repo_root=self.root, merge_ready=True), [])

    def test_completed_compact_uses_existing_independent_review_validator(self):
        manifest = self._completed_compact()
        extra = [str(path.relative_to(self.root)) for path in self.run.with_suffix("").rglob("*.json")]
        self.assertEqual(self._changed(manifest, extra=extra), [])
        self.assertEqual(gate.validate_all(repo_root=self.root, merge_ready=True), [])
        manifest["review_receipts"][1]["execution_id"] = "reviewer-A"
        errors = self._changed(manifest, extra=extra)
        self.assertTrue(any("independent coverage" in error for error in errors), errors)

    def test_completed_compact_raw_tampering_is_rejected_repository_wide(self):
        manifest = self._completed_compact()
        raw = self.root / manifest["review_receipts"][0]["raw_response_path"]
        raw.write_text(raw.read_text(encoding="utf-8") + " ", encoding="utf-8")
        errors = gate.validate_all(repo_root=self.root, merge_ready=True)
        self.assertTrue(any("independent coverage" in error for error in errors), errors)

    def test_new_legacy_runs_still_require_preserved_handoff(self):
        errors = self._changed({"run_id": "run-1", "status": "completed"})
        self.assertTrue(any("new runs require preserved_handoff_v1" in error for error in errors))

    def test_legacy_protocol_cannot_be_removed_or_relabelled_compact(self):
        old = {"run_id": "run-1", "orchestrator": {
            "review_provenance_protocol": "preserved_handoff_v1"}}
        errors = self._changed({"run_id": "run-1"}, old=old)
        self.assertTrue(any("protocol cannot be removed" in error for error in errors))
        for keep_marker in (False, True):
            manifest = {"workflow_contract_version": compact.VERSION,
                        "run_id": "run-1", "status": "in_progress"}
            if keep_marker:
                manifest["orchestrator"] = old["orchestrator"]
            errors = self._changed(manifest, old=old)
            self.assertTrue(any("run contract cannot change" in error for error in errors))

    def test_existing_compact_cannot_be_downgraded_to_legacy(self):
        errors = self._changed({"run_id": "run-1"}, old={
            "run_id": "run-1", "workflow_contract_version": compact.VERSION})
        self.assertTrue(any("run contract cannot change" in error for error in errors))

    def test_old_unmarked_legacy_run_is_not_retroactively_invalidated(self):
        manifest = {"run_id": "run-1", "status": "in_progress"}
        self.assertEqual(self._changed(manifest, old=manifest), [])


if __name__ == "__main__":
    unittest.main()
