from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import review_call  # noqa: E402


class ReviewCallTests(unittest.TestCase):
    def test_api_response_is_preserved_and_normalized_with_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request_path = root / "request.json"
            prompt_path = root / "prompt.md"
            output_path = root / "result.json"
            request = {"pass_id": "translation", "input": "sample"}
            request_path.write_text(json.dumps(request), encoding="utf-8")
            prompt_path.write_text("Return JSON.", encoding="utf-8")
            raw = {
                "id": "resp-test",
                "output_text": json.dumps(
                    {"pass_id": "translation", "findings": []}
                ),
            }
            with mock.patch.object(review_call, "call_provider", return_value=raw):
                result = review_call.execute_review(
                    stage="translation",
                    request_path=request_path,
                    prompt_path=prompt_path,
                    cycle_dir=root,
                    output_path=output_path,
                    provider="openai",
                    model="review-model",
                    api_key="not-used",
                    generation_model="generation-model",
                )
            self.assertEqual(result["reviewer"]["mode"], "api")
            self.assertEqual(result["reviewer"]["response_id"], "resp-test")
            self.assertEqual(
                result["reviewer"]["request_sha256"],
                review_call.canonical_sha256(request),
            )
            self.assertEqual(
                json.loads((root / "raw" / "translation.response.json").read_text()),
                raw,
            )
            self.assertTrue(output_path.is_file())

    def test_two_provider_boundary_is_explicit(self) -> None:
        self.assertEqual(review_call.SUPPORTED_PROVIDERS, {"openai", "anthropic"})
        with self.assertRaisesRegex(ValueError, "unsupported"):
            review_call.call_provider(
                "unknown",
                model="x",
                api_key="x",
                prompt="x",
                request_payload={},
            )

    def test_stage_cannot_escape_the_raw_artifact_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request_path = root / "request.json"
            prompt_path = root / "prompt.md"
            request_path.write_text("{}", encoding="utf-8")
            prompt_path.write_text("Return JSON.", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "safe artifact name"):
                review_call.execute_review(
                    stage="../outside",
                    request_path=request_path,
                    prompt_path=prompt_path,
                    cycle_dir=root,
                    output_path=root / "result.json",
                    provider="openai",
                    model="review-model",
                    api_key="not-used",
                )

    def test_orchestrator_metadata_is_applied_after_model_output(self) -> None:
        request = {
            "stage": "cold_review",
            "entry_body": "sample",
            "_output_metadata": {
                "schema_version": "cold_review_v1",
                "stage": "cold_review",
                "input_body_sha256": "a" * 64,
                "audit_visible": False,
            },
        }
        raw = {
            "id": "resp-meta",
            "output_text": json.dumps(
                {
                    "schema_version": "model-must-not-control-this",
                    "summary": "No findings.",
                    "findings": [],
                }
            ),
        }
        result = review_call.normalize_response(
            "openai",
            "review-model",
            raw,
            request,
            recorded_at="2026-08-27T00:00:00+00:00",
        )
        self.assertEqual(result["schema_version"], "cold_review_v1")
        self.assertEqual(result["recorded_at"], "2026-08-27T00:00:00+00:00")
        self.assertFalse(result["audit_visible"])


if __name__ == "__main__":
    unittest.main()
