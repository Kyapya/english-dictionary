from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import review_liveness  # noqa: E402


def _reviewer(model: str, agent_id: str) -> dict[str, object]:
    return {
        "mode": "handoff",
        "declared_model": model,
        "ingested_by": "human",
        "agent_id": agent_id,
    }


def _zero_finding_inputs(primary: dict[str, object]):
    normal = {
        "pass_outputs": [
            {
                "pass_id": "example-attribution",
                "reviewer": primary,
                "findings": [],
            }
        ]
    }
    cold = {"reviewer": primary, "findings": []}
    blind = {
        "independent_candidates": [{"disposition": "included"}],
        "article_findings": [],
    }
    return normal, cold, blind


class ReviewerAgentIndependenceTests(unittest.TestCase):
    def test_zero_finding_allows_same_model_with_different_agent_ids(self) -> None:
        primary = _reviewer("gpt-5.6-sol", "primary-agent")
        secondary = _reviewer("gpt-5.6-sol", "secondary-agent")
        normal, cold, blind = _zero_finding_inputs(primary)
        self.assertEqual(
            review_liveness.zero_finding_run_errors(
                normal,
                cold,
                blind,
                secondary_reviews={
                    "cold_review": {"reviewer": secondary, "findings": []},
                    "example_attribution": {"reviewer": secondary, "findings": []},
                },
            ),
            [],
        )

    def test_zero_finding_rejects_same_agent_even_when_models_differ(self) -> None:
        primary = _reviewer("model-a", "same-agent")
        secondary = _reviewer("model-b", "same-agent")
        normal, cold, blind = _zero_finding_inputs(primary)
        errors = review_liveness.zero_finding_run_errors(
            normal,
            cold,
            blind,
            secondary_reviews={
                "cold_review": {"reviewer": secondary, "findings": []},
                "example_attribution": {"reviewer": secondary, "findings": []},
            },
        )
        self.assertTrue(
            any("independent reviewer agent" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
