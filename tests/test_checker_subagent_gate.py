from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import checker_subagent_gate as gate  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
