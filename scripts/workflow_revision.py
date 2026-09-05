from __future__ import annotations

"""Deterministic contracts for post-review revisions in new workflow runs.

This module intentionally does not edit entries or ask an LLM to classify its own
changes.  It compares normalized semantic sections, computes the conservative
checker invalidation set, validates cache reuse records, and gates the two
resolution phases and targeted adjudications.
"""

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "workflow_revision_v1"
RECHECK_MANIFEST_VERSION = "checker_recheck_manifest_v1"
TARGETED_ADJUDICATION_VERSION = "targeted_adjudication_v1"

ALL_CHECKER_PASSES = frozenset(
    {
        "translation",
        "sense-structure",
        "frame-relation",
        "example-attribution",
        "qualification",
        "pronunciation",
        "evidence",
    }
)

UNIT_TO_PASSES = {
    "pronunciation": {"pronunciation", "evidence"},
    "etymology": {"sense-structure", "qualification", "evidence"},
    "word_formation": {"sense-structure", "qualification", "evidence"},
    "core_image": {
        "translation",
        "sense-structure",
        "frame-relation",
        "example-attribution",
        "qualification",
        "evidence",
    },
    "sense_structure": {
        "translation",
        "sense-structure",
        "frame-relation",
        "example-attribution",
        "qualification",
        "evidence",
    },
    "frames": {
        "translation",
        "frame-relation",
        "example-attribution",
        "qualification",
        "evidence",
    },
    "collocations_examples": {
        "translation",
        "frame-relation",
        "example-attribution",
        "evidence",
    },
    "usage_notes": {"qualification", "sense-structure", "evidence"},
    "frequency_register": {"qualification", "evidence"},
    "lexical_relations": {
        "translation",
        "sense-structure",
        "frame-relation",
        "example-attribution",
        "qualification",
        "evidence",
    },
}

ISSUE_KINDS = frozenset(
    {
        "invalid_or_missing_review",
        "judgment_conflict",
        "explicit_uncertainty",
        "unresolved_evidence",
        "unverified_revision_impact",
    }
)
MACHINE_REJECT_KINDS = frozenset(
    {"invalid_or_missing_review", "unverified_revision_impact"}
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _body(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[index + 1 :])
    return "\n".join(lines)


def body_sha256(text: str) -> str:
    return hashlib.sha256(_body(text).encode("utf-8")).hexdigest()


def _semantic_snapshot(text: str) -> tuple[dict[str, list[str]], list[str]]:
    """Return normalized semantic units and content outside known headings.

    The dictionary format has stable full-width headings and inline labelled
    sense subsections.  Line numbers are deliberately excluded so moving an
    unchanged block does not invalidate a pass merely because its offset moved.
    """

    units = {key: [] for key in UNIT_TO_PASSES}
    unclassified: list[str] = []
    main: str | None = None
    sense_unit: str | None = None
    heading_map = {
        "＃発音記号": "pronunciation",
        "＃発音": "pronunciation",
        "＃語源": "etymology",
        "＃語形成": "word_formation",
        "＃コアイメージ": "core_image",
        "＃意味・用法・関連表現": "senses",
        "＃意味や関連情報の出力（日本語訳）": "senses",
        "＃語義": "senses",
    }
    label_map = {
        "【日本語訳・定義】": "sense_structure",
        "【文法パターン】": "frames",
        "【コロケーション】": "collocations_examples",
        "【語法・注意】": "usage_notes",
        "【頻度】": "frequency_register",
        "【レジスター/領域】": "frequency_register",
        "【類義語】": "lexical_relations",
        "【反意語】": "lexical_relations",
    }
    in_front = False
    front_closed = False
    for raw in text.splitlines():
        stripped = raw.strip()
        if stripped == "---" and not front_closed:
            if not in_front:
                in_front = True
            else:
                in_front = False
                front_closed = True
            continue
        if in_front or not stripped:
            continue
        compact = stripped.replace(" ", "") if stripped.startswith("＃") else stripped
        if stripped.startswith("＃"):
            main = heading_map.get(compact)
            sense_unit = None
            if main is None:
                unclassified.append(stripped)
            elif main != "senses":
                units[main].append(compact)
            continue
        if main == "senses":
            if stripped[:1].isdigit() and "【" in stripped:
                sense_unit = "sense_structure"
                units[sense_unit].append(stripped)
                continue
            matched = next(
                (unit for label, unit in label_map.items() if stripped.startswith(label)),
                None,
            )
            if matched is not None:
                sense_unit = matched
                units[matched].append(stripped)
            elif sense_unit is not None:
                units[sense_unit].append(stripped)
            else:
                unclassified.append(stripped)
        elif main in units:
            units[main].append(stripped)
        else:
            unclassified.append(stripped)
    return units, unclassified


def _sense_count(snapshot: dict[str, list[str]]) -> int:
    return sum(
        1
        for line in snapshot["sense_structure"]
        if line[:1].isdigit() and "【" in line
    )


def plan_rechecks(before_text: str, after_text: str) -> dict[str, Any]:
    before_body = _body(before_text)
    after_body = _body(after_text)
    before, before_unknown = _semantic_snapshot(before_text)
    after, after_unknown = _semantic_snapshot(after_text)
    changed = sorted(key for key in UNIT_TO_PASSES if before[key] != after[key])
    unknown_changed = before_unknown != after_unknown
    sense_topology_changed = _sense_count(before) != _sense_count(after)
    # More than one semantic section or anything not safely classified falls
    # back to all passes.  This is deliberately conservative.
    full = unknown_changed or sense_topology_changed or len(changed) > 1
    invalidated = set(ALL_CHECKER_PASSES) if full else set()
    if not full:
        for unit in changed:
            invalidated.update(UNIT_TO_PASSES[unit])
    return {
        "schema_version": SCHEMA_VERSION,
        "before_body_sha256": hashlib.sha256(before_body.encode("utf-8")).hexdigest(),
        "after_body_sha256": hashlib.sha256(after_body.encode("utf-8")).hexdigest(),
        "changed_units": changed or (["unclassified"] if unknown_changed else []),
        "full_recheck": full,
        "fallback_reasons": [
            reason
            for condition, reason in (
                (unknown_changed, "unclassified_change"),
                (sense_topology_changed, "sense_or_part_of_speech_topology_changed"),
                (len(changed) > 1, "multiple_semantic_sections_changed"),
            )
            if condition
        ],
        "invalidated_passes": sorted(invalidated),
        "reusable_passes": sorted(ALL_CHECKER_PASSES - invalidated),
    }


def reuse_errors(record: Any, expected: dict[str, Any]) -> list[str]:
    if not isinstance(record, dict):
        return ["checker reuse record must be an object"]
    errors: list[str] = []
    for key in (
        "pass_id",
        "spec_sha256",
        "normalized_input_sha256",
        "source_artifact_sha256",
    ):
        if record.get(key) != expected.get(key):
            errors.append(f"checker reuse {key} mismatch")
    for key in ("schema_valid", "reviewer_independent", "request_binding_valid"):
        if record.get(key) is not True:
            errors.append(f"checker reuse requires {key}=true")
    output_hash = record.get("output_sha256")
    if not isinstance(output_hash, str) or len(output_hash) != 64:
        errors.append("checker reuse output_sha256 is invalid")
    return errors


def validate_recheck_manifest(
    manifest: Any,
    *,
    current_body_sha256: str,
    expected_passes: Iterable[str] = ALL_CHECKER_PASSES,
) -> list[str]:
    if not isinstance(manifest, dict):
        return ["checker recheck manifest must be an object"]
    errors: list[str] = []
    if manifest.get("schema_version") != RECHECK_MANIFEST_VERSION:
        errors.append(f"schema_version must be {RECHECK_MANIFEST_VERSION}")
    if manifest.get("current_body_sha256") != current_body_sha256:
        errors.append("checker recheck manifest references an old body")
    rows = manifest.get("pass_results")
    if not isinstance(rows, list):
        return [*errors, "checker recheck pass_results must be a list"]
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            errors.append("checker recheck pass result must be an object")
            continue
        pass_id = str(row.get("pass_id", ""))
        if not pass_id or pass_id in indexed:
            errors.append(f"checker recheck pass_id is missing or duplicated: {pass_id}")
            continue
        indexed[pass_id] = row
        if row.get("mode") not in {"rechecked", "reused"}:
            errors.append(f"{pass_id}: mode must be rechecked or reused")
        if row.get("validated_on_body_sha256") != current_body_sha256:
            errors.append(f"{pass_id}: result was not validated for the current body")
        for key in (
            "spec_sha256",
            "normalized_input_sha256",
            "source_artifact_sha256",
            "output_sha256",
        ):
            value = row.get(key)
            if not isinstance(value, str) or len(value) != 64:
                errors.append(f"{pass_id}: {key} must be a sha256")
        for key in ("schema_valid", "reviewer_independent", "request_binding_valid"):
            if row.get(key) is not True:
                errors.append(f"{pass_id}: {key} must be true")
        if row.get("mode") == "reused" and row.get("reuse_validated") is not True:
            errors.append(f"{pass_id}: reused result lacks deterministic validation")
    expected = set(expected_passes)
    if set(indexed) != expected:
        errors.append(
            "checker recheck pass set mismatch; "
            f"missing={sorted(expected - set(indexed))}, extra={sorted(set(indexed) - expected)}"
        )
    return errors


def build_recheck_manifest(
    *, current_body_sha256: str, plan: dict[str, Any], pass_results: list[dict[str, Any]]
) -> dict[str, Any]:
    """Assemble and validate the complete seven-pass post-revision result set."""

    invalidated = set(plan.get("invalidated_passes", []))
    rows: list[dict[str, Any]] = []
    for row in pass_results:
        value = dict(row)
        pass_id = str(value.get("pass_id", ""))
        expected_mode = "rechecked" if pass_id in invalidated else "reused"
        if value.get("mode") != expected_mode:
            raise ValueError(
                f"{pass_id}: revision plan requires mode {expected_mode}"
            )
        value["validated_on_body_sha256"] = current_body_sha256
        rows.append(value)
    manifest = {
        "schema_version": RECHECK_MANIFEST_VERSION,
        "current_body_sha256": current_body_sha256,
        "revision_plan_sha256": sha256_json(plan),
        "full_recheck": plan.get("full_recheck") is True,
        "invalidated_passes": sorted(invalidated),
        "pass_results": rows,
    }
    errors = validate_recheck_manifest(
        manifest, current_body_sha256=current_body_sha256
    )
    if errors:
        raise ValueError("; ".join(errors))
    return manifest


def _resolution_ids(rows: Any, label: str, errors: list[str]) -> set[str]:
    if not isinstance(rows, list):
        errors.append(f"{label} must be a list")
        return set()
    result: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        item_id = str(row.get("id", ""))
        if not item_id or item_id in result:
            errors.append(f"{label}[{index}].id is missing or duplicated")
            continue
        result.add(item_id)
        if row.get("finding_id") != item_id:
            errors.append(f"{label} {item_id}.finding_id must equal id")
        if row.get("status") != "resolved":
            errors.append(f"{label} {item_id}.status must be resolved")
        if row.get("disposition") not in {"adopted", "rejected"}:
            errors.append(f"{label} {item_id}.disposition is invalid")
    return result


def validate_resolution_partition(
    *,
    checker_and_cold_ids: set[str],
    final_blind_ids: set[str],
    pre_blind_resolutions: Any,
    post_blind_resolutions: Any,
) -> list[str]:
    errors: list[str] = []
    if checker_and_cold_ids & final_blind_ids:
        errors.append("finding ids must be unique across pre- and post-blind stages")
    pre = _resolution_ids(pre_blind_resolutions, "pre_blind_resolutions", errors)
    post = _resolution_ids(post_blind_resolutions, "post_blind_resolutions", errors)
    if pre != checker_and_cold_ids:
        errors.append("pre_blind_resolutions must cover checker/cold findings exactly once")
    if post != final_blind_ids:
        errors.append("post_blind_resolutions must cover final-blind findings exactly once")
    if pre & post:
        errors.append("a finding cannot be adjudicated in both resolution phases")
    return errors


def _time(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{label} is required")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be an ISO timestamp")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label} must include a timezone")
        return None
    return parsed


def final_blind_chronology_errors(
    *,
    cold_review: dict[str, Any],
    pre_blind_revision: dict[str, Any],
    final_blind: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    cold_at = _time(cold_review.get("recorded_at"), "cold_review.recorded_at", errors)
    revision_at = _time(
        pre_blind_revision.get("recorded_at"),
        "pre_blind_revision.recorded_at",
        errors,
    )
    blind_at = _time(final_blind.get("recorded_at"), "final_blind.recorded_at", errors)
    expected_hash = pre_blind_revision.get("output_body_sha256")
    if final_blind.get("input_body_sha256") != expected_hash:
        errors.append("final blind input body hash does not match the pre-blind revision")
    if cold_at and revision_at and revision_at < cold_at:
        errors.append("pre-blind revision must not precede cold review")
    if revision_at and blind_at and blind_at <= revision_at:
        errors.append("final blind must be recorded after the pre-blind revision")
    return errors


def unresolved_issue_actions(issues: Any) -> list[dict[str, Any]]:
    if not isinstance(issues, list):
        raise ValueError("unresolved issues must be a list")
    actions: list[dict[str, Any]] = []
    for index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            raise ValueError(f"unresolved issue {index} must be an object")
        issue_id = str(issue.get("id", "")).strip()
        kind = str(issue.get("kind", "")).strip()
        if not issue_id or kind not in ISSUE_KINDS:
            raise ValueError(f"unresolved issue {index} has invalid id or kind")
        if kind in MACHINE_REJECT_KINDS:
            action = "mechanical_reject"
        else:
            for field in ("question", "article_excerpt", "judgments"):
                if not issue.get(field):
                    raise ValueError(f"unresolved issue {issue_id} requires {field}")
            action = "targeted_adjudication"
        actions.append({"issue_id": issue_id, "kind": kind, "action": action})
    return actions


def collect_declared_unresolved_issues(reviews: Iterable[Any]) -> list[dict[str, Any]]:
    """Collect concrete reviewer-declared issues without using finding counts."""

    collected: dict[str, dict[str, Any]] = {}
    for review in reviews:
        if not isinstance(review, dict):
            continue
        items = review.get("unresolved_issues", [])
        if items in (None, []):
            continue
        if not isinstance(items, list):
            raise ValueError("review unresolved_issues must be a list")
        for item in items:
            if not isinstance(item, dict) or not str(item.get("id", "")).strip():
                raise ValueError("review unresolved issue requires an id")
            issue_id = str(item["id"])
            if issue_id in collected and collected[issue_id] != item:
                raise ValueError(f"unresolved issue {issue_id} has conflicting declarations")
            collected[issue_id] = item
    return list(collected.values())


def validate_targeted_adjudication_request(request: Any) -> list[str]:
    if not isinstance(request, dict):
        return ["targeted adjudication request must be an object"]
    errors: list[str] = []
    allowed = {
        "schema_version",
        "issue_id",
        "question",
        "article_excerpt",
        "judgments",
        "source_material",
    }
    extra = set(request) - allowed
    if extra:
        errors.append(
            "targeted adjudication request contains unrelated fields: "
            + ", ".join(sorted(extra))
        )
    if request.get("schema_version") != "targeted_adjudication_request_v1":
        errors.append(
            "targeted adjudication request schema_version must be "
            "targeted_adjudication_request_v1"
        )
    for field in ("issue_id", "question", "article_excerpt"):
        if not isinstance(request.get(field), str) or not request[field].strip():
            errors.append(f"targeted adjudication request requires {field}")
    judgments = request.get("judgments")
    if not isinstance(judgments, list) or not judgments:
        errors.append("targeted adjudication request requires judgments")
    sources = request.get("source_material")
    if not isinstance(sources, list):
        errors.append("targeted adjudication request source_material must be a list")
    return errors


def validate_targeted_adjudication(
    record: Any, *, conflicting_agent_ids: Iterable[str] = ()
) -> list[str]:
    if not isinstance(record, dict):
        return ["targeted adjudication must be an object"]
    errors: list[str] = []
    if record.get("schema_version") != TARGETED_ADJUDICATION_VERSION:
        errors.append(f"schema_version must be {TARGETED_ADJUDICATION_VERSION}")
    for field in ("issue_id", "rationale", "applicable_scope"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            errors.append(f"targeted adjudication requires {field}")
    if record.get("decision") not in {
        "resolved_correct",
        "resolved_needs_change",
        "insufficient_evidence",
    }:
        errors.append("targeted adjudication decision is invalid")
    reviewer = record.get("reviewer")
    agent_id = reviewer.get("agent_id") if isinstance(reviewer, dict) else None
    if not isinstance(agent_id, str) or not agent_id.strip():
        errors.append("targeted adjudication reviewer.agent_id is required")
    elif agent_id.strip() in {str(value).strip() for value in conflicting_agent_ids}:
        errors.append("targeted adjudicator must be independent of conflicting reviewers")
    return errors


def targeted_adjudication_blocks_pass(record: Any) -> bool:
    return bool(validate_targeted_adjudication(record)) or (
        isinstance(record, dict) and record.get("decision") == "insufficient_evidence"
    )


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan and validate deterministic post-review checker rechecks"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser("plan", help="classify a before/after entry change")
    plan.add_argument("before", type=Path)
    plan.add_argument("after", type=Path)

    validate = subparsers.add_parser(
        "validate-recheck", help="validate the complete seven-pass recheck manifest"
    )
    validate.add_argument("manifest", type=Path)
    validate.add_argument("entry", type=Path)

    targeted = subparsers.add_parser(
        "validate-targeted", help="validate one targeted adjudication result"
    )
    targeted.add_argument("record", type=Path)
    targeted.add_argument(
        "--conflicting-agent-id", action="append", default=[]
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "plan":
        result = plan_rechecks(
            args.before.read_text(encoding="utf-8"),
            args.after.read_text(encoding="utf-8"),
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.command == "validate-recheck":
        errors = validate_recheck_manifest(
            _read_json(args.manifest),
            current_body_sha256=body_sha256(args.entry.read_text(encoding="utf-8")),
        )
    else:
        errors = validate_targeted_adjudication(
            _read_json(args.record),
            conflicting_agent_ids=args.conflicting_agent_id,
        )
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
