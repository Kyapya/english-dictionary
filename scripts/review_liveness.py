from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


MIN_DISTINCT_RATIONALE_RATIO = 0.60
MAX_RECORDED_ERRORS_PER_REASON = 5
ALLOWED_REVIEWER_MODES = {"api", "handoff"}
ALLOWED_API_PROVIDERS = {"openai", "anthropic"}

B1_TERM_NOT_IN_EXAMPLE = "B1_term_not_in_example"
B2_RATIONALE_NOT_DISTINCT = "B2_rationale_not_distinct"
B2_RATIONALE_NOT_GROUNDED = "B2_rationale_not_grounded"
B3_ATTRIBUTION_COPY_PATTERN = "B3_attribution_copy_pattern"
B4_ZERO_FINDING_SINGLE_REVIEW = "B4_zero_finding_single_review"


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(text.split())


def request_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_api_request_binding(
    reviewer: Any,
    request_payload: dict[str, Any] | None,
) -> list[str]:
    if not isinstance(reviewer, dict) or reviewer.get("mode") != "api":
        return []
    if request_payload is None:
        return ["api reviewer request payload is missing"]
    if reviewer.get("request_sha256") != request_sha256(request_payload):
        return ["reviewer.request_sha256 does not bind the supplied request payload"]
    return []


def validate_reviewer(
    value: Any,
    *,
    generation_model: str | None = None,
) -> list[str]:
    if not isinstance(value, dict):
        return ["reviewer must be an object"]
    mode = value.get("mode")
    if mode not in ALLOWED_REVIEWER_MODES:
        return ["reviewer.mode must be api or handoff"]
    errors: list[str] = []
    if mode == "api":
        for key in ("provider", "model", "response_id", "request_sha256"):
            if not isinstance(value.get(key), str) or not value[key].strip():
                errors.append(f"reviewer.{key} is required for api mode")
        digest = value.get("request_sha256")
        if value.get("provider") not in ALLOWED_API_PROVIDERS:
            errors.append("reviewer.provider must be openai or anthropic")
        if isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            errors.append("reviewer.request_sha256 must be a sha256")
    else:
        for key in ("declared_model", "ingested_by"):
            if not isinstance(value.get(key), str) or not value[key].strip():
                errors.append(f"reviewer.{key} is required for handoff mode")
        if value.get("ingested_by") not in {None, "human"}:
            errors.append("reviewer.ingested_by must be human")

    agent_id = value.get("agent_id")
    if agent_id is not None and (not isinstance(agent_id, str) or not agent_id.strip()):
        errors.append("reviewer.agent_id must be a non-empty string when supplied")

    model = reviewer_model(value)
    if generation_model and model and model == normalize_text(generation_model):
        if value.get("same_model_as_generation") is not True:
            errors.append(
                "reviewer.same_model_as_generation must be true when models match"
            )
    return errors


def reviewer_model(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    raw = value.get("model") if value.get("mode") == "api" else value.get("declared_model")
    return normalize_text(raw) or None


def reviewer_agent_id(value: Any) -> str | None:
    """Return independent reviewer-agent identity with legacy compatibility."""
    if not isinstance(value, dict):
        return None
    explicit = normalize_text(value.get("agent_id"))
    if explicit:
        return explicit
    if value.get("mode") == "api":
        response_id = normalize_text(value.get("response_id"))
        provider = normalize_text(value.get("provider"))
        if response_id:
            return f"api:{provider}:{response_id}"
    # Historical handoff records predate agent_id. Keep their former
    # model-based separation only as a compatibility fallback.
    return reviewer_model(value)


def _example_map(request: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sections = request.get("input_sections", {})
    values = sections.get("collocations_examples", []) if isinstance(sections, dict) else []
    return {
        str(item.get("example_id")): item
        for item in values
        if isinstance(item, dict) and item.get("example_id")
    }


def _strip_target_ids(value: str, ids: Iterable[str]) -> str:
    normalized = normalize_text(value)
    for item_id in sorted({normalize_text(item) for item in ids if item}, key=len, reverse=True):
        normalized = normalized.replace(item_id, "<id>")
    return re.sub(r"\b(?:example|sense|target|relation)[:_-]?[0-9a-f]+\b", "<id>", normalized)


def _distinctness_errors(
    rows: list[dict[str, Any]],
    *,
    text_key: str,
    id_keys: tuple[str, ...],
    label: str,
) -> list[str]:
    if not rows:
        return []
    ids = [str(row.get(key, "")) for row in rows for key in id_keys]
    normalized = [_strip_target_ids(str(row.get(text_key, "")), ids) for row in rows]
    ratio = len(set(normalized)) / len(normalized)
    if ratio < MIN_DISTINCT_RATIONALE_RATIO:
        return [
            f"{B2_RATIONALE_NOT_DISTINCT}: {label} distinct ratio "
            f"{ratio:.3f} is below {MIN_DISTINCT_RATIONALE_RATIO:.2f}"
        ]
    return []


def validate_attribution_liveness(
    record: Any,
    request: dict[str, Any],
    *,
    alignment_key: dict[str, Any] | None = None,
) -> list[str]:
    if not isinstance(record, dict):
        return [f"{B1_TERM_NOT_IN_EXAMPLE}: attribution record is missing"]
    rows = record.get("attributions")
    if not isinstance(rows, list):
        return [f"{B1_TERM_NOT_IN_EXAMPLE}: attributions must be a list"]
    examples = _example_map(request)
    errors: list[str] = []
    all_terms: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        example_id = str(row.get("example_id", ""))
        example = examples.get(example_id, {})
        haystack = normalize_text(
            f"{example.get('example', '')} {example.get('translation', '')}"
        )
        terms = [
            normalize_text(term)
            for term in row.get("discriminating_terms", [])
            if normalize_text(term)
        ]
        all_terms.extend(terms)
        valid_terms = [term for term in terms if term in haystack]
        if row.get("classification") == "unique" and not valid_terms:
            errors.append(
                f"{B1_TERM_NOT_IN_EXAMPLE}: attribution {example_id or index} has no "
                "discriminating term present in its example or translation"
            )
        rationale = normalize_text(row.get("rationale"))
        quote = normalize_text(example.get("exact_quote") or example.get("example"))
        if not rationale or not (
            any(term in rationale for term in valid_terms)
            or (quote and quote in rationale)
        ):
            errors.append(
                f"{B2_RATIONALE_NOT_GROUNDED}: attribution {example_id or index} "
                "rationale contains neither an exact quote nor a valid discriminating term"
            )

    errors.extend(
        _distinctness_errors(
            [row for row in rows if isinstance(row, dict)],
            text_key="rationale",
            id_keys=("example_id",),
            label="example attribution rationales",
        )
    )
    sections = request.get("input_sections", {})
    senses = sections.get("sense_structure", []) if isinstance(sections, dict) else []
    if rows and len(set(all_terms)) <= len(senses):
        errors.append(
            f"{B3_ATTRIBUTION_COPY_PATTERN}: discriminating term diversity "
            "does not exceed the sense count"
        )
    if alignment_key is not None and any(
        error.startswith((B1_TERM_NOT_IN_EXAMPLE, B2_RATIONALE_NOT_DISTINCT, B2_RATIONALE_NOT_GROUNDED))
        for error in errors
    ):
        by_example = {
            str(row.get("example_id")): row
            for row in rows
            if isinstance(row, dict)
        }
        ownership = [
            item
            for item in alignment_key.get("examples", [])
            if isinstance(item, dict)
        ]
        copied_order = bool(ownership) and all(
            by_example.get(str(owner.get("example_id")), {}).get(
                "candidate_sense_ids"
            )
            == [owner.get("assigned_sense_id")]
            for owner in ownership
        )
        if copied_order and not any(
            error.startswith(B3_ATTRIBUTION_COPY_PATTERN) for error in errors
        ):
            errors.append(
                f"{B3_ATTRIBUTION_COPY_PATTERN}: candidate senses reproduce document "
                "ownership order while B1/B2 evidence is invalid"
            )
    return errors


def validate_final_review_liveness(
    review: Any,
    *,
    target_quotes: dict[str, str] | None = None,
    relation_quotes: dict[str, str] | None = None,
) -> list[str]:
    if not isinstance(review, dict):
        return []
    errors: list[str] = []
    for field, quotes in (
        ("target_results", target_quotes or {}),
        ("relation_results", relation_quotes or {}),
    ):
        rows = review.get(field)
        if not isinstance(rows, list):
            continue
        typed = [row for row in rows if isinstance(row, dict)]
        errors.extend(
            _distinctness_errors(
                typed,
                text_key="notes",
                id_keys=("id", "target_id", "relation_id"),
                label=field,
            )
        )
        for index, row in enumerate(typed):
            item_id = str(
                row.get("target_id") or row.get("relation_id") or row.get("id") or index
            )
            quote = normalize_text(quotes.get(item_id, ""))
            notes = normalize_text(row.get("notes"))
            if quote and quote not in notes:
                errors.append(
                    f"{B2_RATIONALE_NOT_GROUNDED}: {field} {item_id} notes do not "
                    "contain the target exact quote"
                )
    return errors


def validate_finding_liveness(
    value: Any,
    *,
    field: str,
    label: str,
) -> list[str]:
    if not isinstance(value, dict) or not isinstance(value.get(field), list):
        return []
    rows = [item for item in value[field] if isinstance(item, dict)]
    rationale_rows = [
        {
            **row,
            "rationale": row.get("rationale")
            or row.get("reason")
            or row.get("description")
            or "",
        }
        for row in rows
    ]
    errors = _distinctness_errors(
        rationale_rows,
        text_key="rationale",
        id_keys=("id", "finding_id"),
        label=label,
    )
    for index, row in enumerate(rationale_rows):
        location = row.get("location")
        quotes = [
            normalize_text(
                location.get("exact_quote") if isinstance(location, dict) else ""
            )
        ]
        scope_anchors = row.get("scope_anchors")
        if isinstance(scope_anchors, list):
            quotes.extend(
                normalize_text(anchor.get("exact_quote"))
                for anchor in scope_anchors
                if isinstance(anchor, dict)
            )
        quotes = [quote for quote in quotes if quote]
        rationale = normalize_text(row.get("rationale"))
        if not rationale or not quotes or not any(quote in rationale for quote in quotes):
            errors.append(
                f"{B2_RATIONALE_NOT_GROUNDED}: {label} item "
                f"{row.get('id', index)} rationale does not contain a target exact quote"
            )
    return errors


def validate_candidate_liveness(value: Any, *, label: str) -> list[str]:
    if not isinstance(value, dict) or not isinstance(
        value.get("independent_candidates"), list
    ):
        return []
    rows = [
        item
        for item in value["independent_candidates"]
        if isinstance(item, dict)
    ]
    errors = _distinctness_errors(
        rows,
        text_key="rationale",
        id_keys=("id",),
        label=label,
    )
    for index, row in enumerate(rows):
        rationale = normalize_text(row.get("rationale"))
        anchors = [
            normalize_text(row.get(key))
            for key in ("surface_form", "frame", "meaning")
            if normalize_text(row.get(key))
        ]
        if not rationale or not anchors or not any(anchor in rationale for anchor in anchors):
            errors.append(
                f"{B2_RATIONALE_NOT_GROUNDED}: {label} item "
                f"{row.get('id', index)} rationale contains no candidate-specific anchor"
            )
    return errors


def _finding_count(value: Any, *fields: str) -> int:
    if not isinstance(value, dict):
        return 0
    return sum(len(value.get(field, [])) for field in fields if isinstance(value.get(field), list))


def zero_finding_run_errors(
    pass_findings: dict[str, Any],
    cold_review: dict[str, Any],
    final_blind: dict[str, Any],
    *,
    secondary_reviews: dict[str, Any] | None = None,
) -> list[str]:
    normal_count = sum(
        _finding_count(item, "findings")
        for item in pass_findings.get("pass_outputs", [])
        if isinstance(item, dict)
    )
    total = normal_count + _finding_count(cold_review, "findings") + _finding_count(
        final_blind, "article_findings"
    )
    candidates = final_blind.get("independent_candidates", [])
    excluded = [
        item
        for item in candidates
        if isinstance(item, dict) and item.get("disposition") != "included"
    ]
    if total or excluded:
        return []

    secondary = secondary_reviews or {}
    cold_secondary = secondary.get("cold_review")
    attr_secondary = secondary.get("example_attribution")
    if not isinstance(cold_secondary, dict) or not isinstance(attr_secondary, dict):
        return [
            f"{B4_ZERO_FINDING_SINGLE_REVIEW}: a zero-finding run requires independent "
            "secondary-agent cold and example-attribution reviews"
        ]
    if _finding_count(cold_secondary, "findings") or _finding_count(
        attr_secondary, "findings"
    ):
        return [
            f"{B4_ZERO_FINDING_SINGLE_REVIEW}: second-review findings must enter "
            "the normal finding-resolution flow before approval"
        ]
    primary_agents = {
        reviewer_agent_id(cold_review.get("reviewer")),
        *(
            reviewer_agent_id(item.get("reviewer"))
            for item in pass_findings.get("pass_outputs", [])
            if isinstance(item, dict) and item.get("pass_id") == "example-attribution"
        ),
    } - {None}
    secondary_agents = {
        reviewer_agent_id(cold_secondary.get("reviewer")),
        reviewer_agent_id(attr_secondary.get("reviewer")),
    } - {None}
    if not secondary_agents or primary_agents & secondary_agents:
        return [
            f"{B4_ZERO_FINDING_SINGLE_REVIEW}: second reviews must declare an independent "
            "reviewer agent different from the primary reviewers"
        ]
    return []


def invalidation_ids(errors: Iterable[str]) -> list[str]:
    known = (
        B1_TERM_NOT_IN_EXAMPLE,
        B2_RATIONALE_NOT_DISTINCT,
        B2_RATIONALE_NOT_GROUNDED,
        B3_ATTRIBUTION_COPY_PATTERN,
        B4_ZERO_FINDING_SINGLE_REVIEW,
    )
    return sorted({item for error in errors for item in known if error.startswith(item)})


def required_pending_status(reasons: Iterable[str]) -> str:
    """Return the safe entry status for a liveness-invalidated run."""
    reason_set = set(reasons)
    if reason_set and reason_set <= {B4_ZERO_FINDING_SINGLE_REVIEW}:
        return "review_ready"
    return "needs_review"


def summarize_errors(errors: Iterable[str]) -> list[str]:
    grouped: dict[str, list[str]] = {}
    for error in errors:
        reason = error.split(":", 1)[0]
        grouped.setdefault(reason, []).append(error)
    summary: list[str] = []
    for reason in sorted(grouped):
        values = grouped[reason]
        summary.extend(values[:MAX_RECORDED_ERRORS_PER_REASON])
        omitted = len(values) - MAX_RECORDED_ERRORS_PER_REASON
        if omitted > 0:
            summary.append(f"{reason}: {omitted} additional violations omitted")
    return summary


def validate_run_directory(cycle_dir: Path) -> list[str]:
    def read(name: str) -> dict[str, Any]:
        path = cycle_dir / name
        if not path.is_file():
            return {}
        import json

        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}

    normal = read("pass_findings.json")
    cold = read("cold_review.json")
    blind = read("final_blind.json")
    final = read("final_review.json")
    secondary = read("secondary_reviews.json")
    errors: list[str] = []
    attribution = next(
        (
            item
            for item in normal.get("pass_outputs", [])
            if isinstance(item, dict) and item.get("pass_id") == "example-attribution"
        ),
        None,
    )
    request_path = cycle_dir / "check_passes" / "example-attribution.request.json"
    request: dict[str, Any] | None = None
    if request_path.is_file():
        import json

        request = json.loads(request_path.read_text(encoding="utf-8"))
    elif attribution:
        try:
            repo_root = cycle_dir.resolve().parents[4]
            slug = cycle_dir.parent.name
            entry = repo_root / "entries" / slug[0] / f"{slug}.md"
            import check_passes

            text = entry.read_text(encoding="utf-8")
            material = check_passes._example_attribution_material(text)
            request = {
                "input_sections": {
                    "sense_structure": material["senses"],
                    "collocations_examples": material["examples"],
                }
            }
        except (IndexError, OSError, ValueError):
            request = None
    if request is not None and attribution:
        errors.extend(
            validate_attribution_liveness(
                attribution.get("blind_attribution_record"),
                request,
            )
        )
    errors.extend(validate_final_review_liveness(final))
    errors.extend(
        validate_finding_liveness(cold, field="findings", label="cold review findings")
    )
    errors.extend(
        validate_finding_liveness(
            blind, field="article_findings", label="final blind findings"
        )
    )
    errors.extend(validate_candidate_liveness(blind, label="final blind candidates"))
    errors.extend(
        zero_finding_run_errors(
            normal, cold, blind, secondary_reviews=secondary or None
        )
    )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate independent review liveness")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate-run")
    validate.add_argument("cycle_dir", type=Path)
    regression = sub.add_parser("regression")
    regression.add_argument("cycle_dir", type=Path)
    regression.add_argument(
        "--expect",
        nargs="+",
        default=[
            B1_TERM_NOT_IN_EXAMPLE,
            B2_RATIONALE_NOT_DISTINCT,
            B4_ZERO_FINDING_SINGLE_REVIEW,
        ],
    )
    args = parser.parse_args(argv)
    errors = validate_run_directory(args.cycle_dir)
    ids = invalidation_ids(errors)
    if args.command == "regression":
        missing = sorted(set(args.expect) - set(ids))
        print(json.dumps({"invalidated_by": ids, "errors": errors}, ensure_ascii=False, indent=2))
        return 1 if missing else 0
    if errors:
        print(json.dumps({"invalidated_by": ids, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    print("Review liveness validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
