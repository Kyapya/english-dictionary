"""Versioned final-review reporting rules; coverage and decisions stay explicit."""

CONCISE_VERSION = "final_review_v3"


def concise(review: dict) -> bool:
    return review.get("schema_version") == CONCISE_VERSION


def needs_notes(row: dict, *, compact: bool, field: str) -> bool:
    # Findings are actual disputes/fixes, whose disposition must remain reviewable.
    return not compact or field == "finding_results" or row.get("status") != "pass"
