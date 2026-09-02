from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_word  # noqa: E402


class SubagentReviewContractTests(unittest.TestCase):
    def _root_and_manifest(self, directory: str) -> tuple[Path, dict[str, object]]:
        root = Path(directory)
        shutil.copytree(REPO_ROOT / "prompts", root / "prompts")
        entry = root / "entries" / "s" / "sample.md"
        entry.parent.mkdir(parents=True)
        entry.write_text(
            "---\nheadword: sample\nmodel: generation-model\n---\n\n# sample\n",
            encoding="utf-8",
        )
        manifest: dict[str, object] = {
            "entry_path": "entries/s/sample.md",
            "run_id": "subagent-contract-run",
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
        return root, manifest

    def test_plan_declares_parallel_subagent_protocol(self) -> None:
        plan = run_word.plan_payload("sample", REPO_ROOT, reviewer_mode="handoff")
        self.assertEqual(
            plan["checker_execution_protocol"],
            run_word.CHECKER_SUBAGENT_PROTOCOL_VERSION,
        )
        self.assertEqual(plan["checker_subagent_count"], len(plan["checker_passes"]))
        self.assertEqual(plan["checker_subagent_count"], 7)

    def test_same_model_is_allowed_for_distinct_subagents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cycle = Path(directory)
            handoff = cycle / "handoff"
            handoff.mkdir()
            router = run_word.check_passes.load_router(REPO_ROOT / run_word.DEFAULT_CHECK_SPEC)
            pass_ids = [str(item["id"]) for item in router["passes"]]
            for index, pass_id in enumerate(pass_ids):
                (handoff / f"checker_passes.{pass_id}.response.json").write_text(
                    json.dumps(
                        {
                            "pass_id": pass_id,
                            "reviewer": {
                                "mode": "handoff",
                                "declared_model": "same-review-model",
                                "ingested_by": "human",
                                "agent_id": f"subagent-{index}",
                            },
                        }
                    ),
                    encoding="utf-8",
                )
            loaded = run_word._load_parallel_checker_responses(
                cycle,
                pass_ids,
                generation_model="generation-model",
            )
            self.assertIsNotNone(loaded)
            self.assertEqual(
                {item["reviewer"]["declared_model"] for item in loaded.values()},
                {"same-review-model"},
            )
            self.assertEqual(
                len({item["reviewer"]["agent_id"] for item in loaded.values()}),
                7,
            )

    def test_standard_ingest_rejects_legacy_checker_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, manifest = self._root_and_manifest(directory)
            with self.assertRaisesRegex(
                ValueError, "one response from each parallel subagent"
            ):
                run_word.ingest_handoff_review(
                    manifest,
                    stage="checker_passes",
                    declared_model="same-review-model",
                    repo_root=root,
                )

    def test_generated_checker_handoff_uses_subagent_term(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, manifest = self._root_and_manifest(directory)
            index = run_word.prepare_handoff(manifest, repo_root=root)
            text = index.read_text(encoding="utf-8")
            self.assertIn("one independent subagent per pass", text)
            self.assertNotIn("one independent agent per pass", text)
            example = index.parent / "checker_passes.example-attribution.request.md"
            request_text = example.read_text(encoding="utf-8")
            self.assertIn("independent subagent/session", request_text)
            self.assertIn("reuse one subagent for multiple passes", request_text)

    def test_review_prompts_block_known_scope_failure_modes(self) -> None:
        attribution = (REPO_ROOT / "prompts" / "check_pass_example_attribution_v6.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("周辺語だけを根拠に `unique` としてはならない", attribution)
        self.assertIn("もっともらしい競合語義", attribution)
        self.assertIn("表面的なトピック推定で曖昧性を消してはならない", attribution)

        final_blind = (REPO_ROOT / "prompts" / "final_blind_prompt_v2.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("別語義へ自然に帰属し得るなら", final_blind)
        self.assertIn("内部の1フレームの帰属を自動的に正しいとみなさない", final_blind)
        self.assertIn("新しいレビュー段階を追加するものではない", final_blind)


if __name__ == "__main__":
    unittest.main()
