from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import review_liveness  # noqa: E402


class ReviewLivenessTests(unittest.TestCase):
    def test_known_yield_run_keeps_content_invalidations_but_drops_zero_count_rule(self) -> None:
        cycle = (
            REPO_ROOT
            / "audits"
            / "runs"
            / "y"
            / "yield"
            / "20260826T131200Z-yield02"
        )
        errors = review_liveness.validate_run_directory(cycle)
        ids = review_liveness.invalidation_ids(errors)
        self.assertTrue(
            {review_liveness.B1_TERM_NOT_IN_EXAMPLE,
             review_liveness.B2_RATIONALE_NOT_DISTINCT} <= set(ids)
        )
        self.assertNotIn(review_liveness.B4_ZERO_FINDING_SINGLE_REVIEW, ids)

    def test_reviewer_provenance_is_mandatory_and_mode_is_closed(self) -> None:
        self.assertTrue(review_liveness.validate_reviewer(None))
        self.assertTrue(review_liveness.validate_reviewer({"mode": "local"}))
        self.assertTrue(
            review_liveness.validate_reviewer(
                {
                    "mode": "api",
                    "provider": "unknown",
                    "model": "reviewer",
                    "response_id": "r1",
                    "request_sha256": "a" * 64,
                }
            )
        )
        self.assertEqual(
            review_liveness.validate_reviewer(
                {
                    "mode": "handoff",
                    "declared_model": "independent-model",
                    "ingested_by": "human",
                }
            ),
            [],
        )

    def test_zero_finding_run_does_not_require_secondary_reviews(self) -> None:
        reviewer = {
            "mode": "handoff",
            "declared_model": "primary",
            "ingested_by": "human",
        }
        normal = {
            "pass_outputs": [
                {
                    "pass_id": "example-attribution",
                    "reviewer": reviewer,
                    "findings": [],
                }
            ]
        }
        cold = {"reviewer": reviewer, "findings": []}
        blind = {
            "independent_candidates": [{"disposition": "included"}],
            "article_findings": [],
        }
        self.assertEqual(review_liveness.zero_finding_run_errors(normal, cold, blind), [])
        secondary_reviewer = {
            "mode": "handoff",
            "declared_model": "secondary",
            "ingested_by": "human",
        }
        self.assertEqual(
            review_liveness.zero_finding_run_errors(
                normal,
                cold,
                blind,
                secondary_reviews={
                    "cold_review": {
                        "reviewer": secondary_reviewer,
                        "findings": [],
                    },
                    "example_attribution": {
                        "reviewer": secondary_reviewer,
                        "findings": [],
                    },
                },
            ),
            [],
        )
        errors = review_liveness.zero_finding_run_errors(
            normal,
            cold,
            blind,
            secondary_reviews={
                "cold_review": {
                    "reviewer": secondary_reviewer,
                    "findings": [{"id": "new-defect"}],
                },
                "example_attribution": {
                    "reviewer": secondary_reviewer,
                    "findings": [],
                },
            },
        )
        self.assertEqual(errors, [])

    def test_regression_default_no_longer_expects_zero_finding_rule(self) -> None:
        cycle = (
            REPO_ROOT
            / "audits"
            / "runs"
            / "y"
            / "yield"
            / "20260826T131200Z-yield02"
        )
        self.assertEqual(review_liveness.main(["regression", str(cycle)]), 0)

    def test_api_request_hash_must_bind_the_supplied_packet(self) -> None:
        request = {"stage": "cold_review", "entry_body": "sample"}
        reviewer = {
            "mode": "api",
            "provider": "openai",
            "model": "reviewer",
            "response_id": "resp-1",
            "request_sha256": review_liveness.request_sha256(request),
        }
        self.assertEqual(
            review_liveness.validate_api_request_binding(reviewer, request), []
        )
        self.assertTrue(
            review_liveness.validate_api_request_binding(
                reviewer, {**request, "entry_body": "different"}
            )
        )

    def test_pending_status_distinguishes_invalid_review_from_zero_findings(self) -> None:
        self.assertEqual(
            review_liveness.required_pending_status(
                [review_liveness.B4_ZERO_FINDING_SINGLE_REVIEW]
            ),
            "review_ready",
        )
        self.assertEqual(
            review_liveness.required_pending_status(
                [
                    review_liveness.B1_TERM_NOT_IN_EXAMPLE,
                    review_liveness.B4_ZERO_FINDING_SINGLE_REVIEW,
                ]
            ),
            "needs_review",
        )

    def test_ambiguous_attribution_rationale_must_quote_its_example(self) -> None:
        request = {
            "input_sections": {
                "sense_structure": [{"sense_id": "sense:001"}],
                "collocations_examples": [
                    {
                        "example_id": "ex-abc123abc123",
                        "example": "A deliberately ambiguous example.",
                        "translation": "意図的に曖昧な例。",
                    }
                ],
            }
        }
        record = {
            "attributions": [
                {
                    "example_id": "ex-abc123abc123",
                    "classification": "ambiguous",
                    "candidate_sense_ids": ["sense:001", "sense:002"],
                    "discriminating_terms": [],
                    "rationale": "Multiple senses remain possible.",
                }
            ]
        }
        errors = review_liveness.validate_attribution_liveness(record, request)
        self.assertTrue(
            any(
                error.startswith(review_liveness.B2_RATIONALE_NOT_GROUNDED)
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
