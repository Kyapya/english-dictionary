"""Versioned final-review reporting rules; coverage and decisions stay explicit."""

CONCISE_VERSION = "final_review_v3"


def concise(review: dict) -> bool:
    return review.get("schema_version") == CONCISE_VERSION


def needs_notes(row: dict, *, compact: bool, field: str) -> bool:
    # Findings are actual disputes/fixes, whose disposition must remain reviewable.
    return not compact or field == "finding_results" or row.get("status") != "pass"


TRACE_CONTRACT = {
    "version": "concise_review_trace_v1",
    "finding_notes": "Record the concrete fix or rejection reason for each finding.",
    "overall_notes": "If there are no finding notes, record one short concrete review observation.",
    "no_duplicate_pass_reasons": True,
    "minimum_characters": None,
    "not_identity_proof": True,
}


def concrete_note(value: object) -> bool:
    """Reject empty/stock acknowledgments, without imposing a prose length quota.

    This is only a syntactic trace check, not proof that a review actually ran.
    Identity, preserved responses, coverage and substantive review remain required.
    """
    if not isinstance(value, str):
        return False
    text = value.strip().casefold().rstrip("。.!！")
    return bool(text) and text not in {
        "ok", "pass", "passed", "reviewed", "checked", "all pass", "all passed",
        "no issues", "looks good", "問題なし", "確認済み", "合格", "全件合格",
        "確認しました", "すべて確認済み",
    }
