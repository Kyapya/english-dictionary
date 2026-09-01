from __future__ import annotations

import json
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_word  # noqa: E402


class ParallelCheckerExecutionTests(unittest.TestCase):
    def _root_and_manifest(
        self, directory: str, *, reviewer_mode: str
    ) -> tuple[Path, dict[str, object]]:
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
        manifest: dict[str, object] = {
            "entry_path": "entries/s/sample.md",
            "run_id": f"parallel-{reviewer_mode}-run",
            "orchestrator": run_word.plan_payload(
                "sample", root, reviewer_mode=reviewer_mode
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
        return root, manifest

    def test_api_checker_passes_cross_a_seven_worker_barrier(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, manifest = self._root_and_manifest(
                directory, reviewer_mode="api"
            )
            barrier = threading.Barrier(7, timeout=5)
            lock = threading.Lock()
            started: list[str] = []
            thread_names: set[str] = set()

            def fake_worker(
                bundle: dict[str, object], **_: object
            ) -> tuple[dict[str, object], list[Path]]:
                with lock:
                    started.append(str(bundle["pass_id"]))
                    thread_names.add(threading.current_thread().name)
                barrier.wait()
                return {"pass_id": str(bundle["pass_id"]), "findings": []}, []

            with mock.patch.object(
                run_word,
                "_execute_checker_bundle_api",
                side_effect=fake_worker,
            ):
                outputs = run_word.execute_api_review_stage(
                    manifest,
                    repo_root=root,
                    provider="openai",
                    model="independent-reviewer",
                    api_key="not-used",
                )

            self.assertEqual(len(started), 7)
            self.assertEqual(len(thread_names), 7)
            self.assertTrue(
                all(name.startswith("checker-pass") for name in thread_names)
            )
            cycle = (
                root
                / "audits"
                / "runs"
                / "s"
                / "sample"
                / "parallel-api-run"
            )
            aggregate = json.loads((cycle / "pass_findings.json").read_text())
            expected = [
                item["id"]
                for item in manifest["orchestrator"]["checker_passes"]  # type: ignore[index]
            ]
            self.assertEqual(
                [item["pass_id"] for item in aggregate["pass_outputs"]],
                expected,
            )
            self.assertIn(cycle / "pass_findings.json", outputs)

    def test_handoff_fans_out_seven_independent_request_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, manifest = self._root_and_manifest(
                directory, reviewer_mode="handoff"
            )
            index = run_word.prepare_handoff(manifest, repo_root=root)
            text = index.read_text(encoding="utf-8")
            self.assertIn("Independent review handoff", text)
            self.assertIn("Launch all seven request files", text)
            self.assertIn("heartbeat", text)

            handoff_dir = index.parent
            requests = sorted(
                path
                for path in handoff_dir.glob("checker_passes.*.request.md")
                if "stage2" not in path.name
            )
            self.assertEqual(len(requests), 7)
            self.assertEqual(
                {path.name for path in requests},
                {
                    "checker_passes.translation.request.md",
                    "checker_passes.example-attribution.request.md",
                    "checker_passes.sense-structure.request.md",
                    "checker_passes.frame-relation.request.md",
                    "checker_passes.qualification.request.md",
                    "checker_passes.pronunciation.request.md",
                    "checker_passes.evidence.request.md",
                },
            )
            frame = handoff_dir / "checker_passes.frame-relation.request.md"
            self.assertIn("same agent", frame.read_text(encoding="utf-8"))

    def test_parallel_handoff_rejects_partial_response_set(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, manifest = self._root_and_manifest(
                directory, reviewer_mode="handoff"
            )
            index = run_word.prepare_handoff(manifest, repo_root=root)
            router = run_word.check_passes.load_router(
                root / run_word.DEFAULT_CHECK_SPEC
            )
            pass_ids = [str(item["id"]) for item in router["passes"]]
            response = index.parent / "checker_passes.translation.response.json"
            response.write_text(
                json.dumps(
                    {
                        "pass_id": "translation",
                        "reviewer": {
                            "mode": "handoff",
                            "declared_model": "reviewer-model",
                            "ingested_by": "human",
                            "agent_id": "agent-translation",
                        },
                    }
                ),
                encoding="utf-8",
            )
            cycle = index.parent.parent
            with self.assertRaisesRegex(ValueError, "missing responses"):
                run_word._load_parallel_checker_responses(
                    cycle,
                    pass_ids,
                    generation_model="synthetic-fixture",
                )

    def test_parallel_handoff_rejects_duplicate_agent_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, manifest = self._root_and_manifest(
                directory, reviewer_mode="handoff"
            )
            index = run_word.prepare_handoff(manifest, repo_root=root)
            router = run_word.check_passes.load_router(
                root / run_word.DEFAULT_CHECK_SPEC
            )
            pass_ids = [str(item["id"]) for item in router["passes"]]
            for pass_id in pass_ids:
                (index.parent / f"checker_passes.{pass_id}.response.json").write_text(
                    json.dumps(
                        {
                            "pass_id": pass_id,
                            "reviewer": {
                                "mode": "handoff",
                                "declared_model": "reviewer-model",
                                "ingested_by": "human",
                                "agent_id": "same-agent",
                            },
                        }
                    ),
                    encoding="utf-8",
                )
            cycle = index.parent.parent
            with self.assertRaisesRegex(ValueError, "unique reviewer.agent_id"):
                run_word._load_parallel_checker_responses(
                    cycle,
                    pass_ids,
                    generation_model="synthetic-fixture",
                )

    def test_parallel_handoff_rejects_pass_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, manifest = self._root_and_manifest(
                directory, reviewer_mode="handoff"
            )
            index = run_word.prepare_handoff(manifest, repo_root=root)
            router = run_word.check_passes.load_router(
                root / run_word.DEFAULT_CHECK_SPEC
            )
            pass_ids = [str(item["id"]) for item in router["passes"]]
            for number, pass_id in enumerate(pass_ids):
                claimed = pass_ids[1] if number == 0 else pass_id
                (index.parent / f"checker_passes.{pass_id}.response.json").write_text(
                    json.dumps(
                        {
                            "pass_id": claimed,
                            "reviewer": {
                                "mode": "handoff",
                                "declared_model": "reviewer-model",
                                "ingested_by": "human",
                                "agent_id": f"agent-{number}",
                            },
                        }
                    ),
                    encoding="utf-8",
                )
            cycle = index.parent.parent
            with self.assertRaisesRegex(ValueError, "pass_id mismatch"):
                run_word._load_parallel_checker_responses(
                    cycle,
                    pass_ids,
                    generation_model="synthetic-fixture",
                )


if __name__ == "__main__":
    unittest.main()
