from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
V1_VERSION = "source_first_audit_v1"
V2_VERSION = "source_first_audit_v2"
CURRENT_VERSION = V2_VERSION
DERIVED_SEPARATORS = ("/", ",", ";", "、", "・")
COVERAGE_AXES = (
    "lexical_senses",
    "part_of_speech_and_frames",
    "derived_and_related_forms",
    "specialist_and_legal_uses",
    "register_region_and_frequency",
    "pronunciation_and_etymology",
)
PROFILES = {
    "standard": {
        "max_sources": 6,
        "max_facts": 48,
        "max_research_rounds": 2,
        "max_post_cold_rechecks": 1,
        "max_final_attempts": 2,
    },
    "extended": {
        "max_sources": 8,
        "max_facts": 80,
        "max_research_rounds": 3,
        "max_post_cold_rechecks": 2,
        "max_final_attempts": 2,
    },
}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _load(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path} must contain a JSON object")
        return {}
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _index(items: Any, label: str, key: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        item_id = item.get(key)
        if not _nonempty(item_id):
            errors.append(f"{label}[{index}].{key} is required")
            continue
        item_id = str(item_id)
        if item_id in result:
            errors.append(f"{label} contains duplicate {key} {item_id}")
            continue
        result[item_id] = item
    return result


def _strings(value: Any, label: str, errors: list[str], *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    result: list[str] = []
    for index, item in enumerate(value):
        if not _nonempty(item):
            errors.append(f"{label}[{index}] must be a non-empty string")
            continue
        result.append(str(item))
    if not allow_empty and not result:
        errors.append(f"{label} must not be empty")
    if len(result) != len(set(result)):
        errors.append(f"{label} must not contain duplicates")
    return result


def _integer(value: Any, label: str, errors: list[str]) -> int | None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(f"{label} must be a non-negative integer")
        return None
    return value


def _parse_time(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not _nonempty(value):
        errors.append(f"{label} is required")
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be ISO-8601")
        return None


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="microseconds")


def _audit_path(entry: Path) -> Path:
    rel = entry.resolve().relative_to(REPO_ROOT.resolve())
    if not rel.parts or rel.parts[0] != "entries":
        raise ValueError(f"entry must be under entries/: {entry}")
    return REPO_ROOT / "audits" / Path(*rel.parts[1:]).with_suffix(".json")


def _sources(
    gate: dict[str, Any], errors: list[str], *, v2: bool, allow_empty: bool = False
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    sources = _index(gate.get("sources"), "source_first_audit.sources", "id", errors)
    if not sources and not allow_empty:
        errors.append("source_first_audit.sources must not be empty")
    facts: dict[str, dict[str, Any]] = {}
    for source_id, source in sources.items():
        for key in ("locator", "source_type"):
            if not _nonempty(source.get(key)):
                errors.append(f"source {source_id}.{key} is required")
        if v2:
            for key in ("source_role", "independence_group"):
                if not _nonempty(source.get(key)):
                    errors.append(f"source {source_id}.{key} is required")
        for fact_id, fact in _index(
            source.get("facts"), f"source {source_id}.facts", "id", errors
        ).items():
            if fact_id in facts:
                errors.append(f"duplicate source fact id {fact_id}")
                continue
            facts[fact_id] = fact
            for key in ("form", "kind", "statement", "source_detail"):
                if not _nonempty(fact.get(key)):
                    errors.append(f"source fact {fact_id}.{key} is required")
            if fact.get("kind") == "derived_form" and any(
                separator in str(fact.get("form", "")) for separator in DERIVED_SEPARATORS
            ):
                errors.append(f"derived source fact {fact_id} must contain exactly one form")
    return sources, facts


def _validate_v1(manifest: dict[str, Any], gate: dict[str, Any]) -> list[str]:
    """Compatibility validator for untouched audits created by PR #90."""
    errors: list[str] = []
    if gate.get("inventory_completed_before_article_comparison") is not True:
        errors.append("inventory_completed_before_article_comparison must be true")
    inventory_time = _parse_time(
        gate.get("inventory_completed_at"), "source_first_audit.inventory_completed_at", errors
    )
    comparison_time = _parse_time(
        gate.get("article_comparison_started_at"),
        "source_first_audit.article_comparison_started_at",
        errors,
    )
    if inventory_time and comparison_time and inventory_time >= comparison_time:
        errors.append("source inventory must be completed before article comparison starts")

    _, facts = _sources(gate, errors, v2=False)
    union = _index(gate.get("source_union"), "source_first_audit.source_union", "id", errors)
    covered: set[str] = set()
    for union_id, item in union.items():
        fact_ids = _strings(
            item.get("source_fact_ids"), f"source union {union_id}.source_fact_ids", errors
        )
        covered.update(fact_ids)
        unknown = sorted(set(fact_ids) - set(facts))
        if unknown:
            errors.append(f"source union {union_id} references unknown facts: {', '.join(unknown)}")
        if not _nonempty(item.get("canonical_statement")):
            errors.append(f"source union {union_id}.canonical_statement is required")
        if item.get("disposition") not in {"included", "integrated", "excluded"}:
            errors.append(f"source union {union_id}.disposition is invalid")
        if not _nonempty(item.get("rationale")):
            errors.append(f"source union {union_id}.rationale is required")
        _strings(
            item.get("article_target_ids"),
            f"source union {union_id}.article_target_ids",
            errors,
            allow_empty=True,
        )
    missing = sorted(set(facts) - covered)
    if missing:
        errors.append("source facts missing from source_union: " + ", ".join(missing))

    claims = _index(gate.get("claim_units"), "source_first_audit.claim_units", "id", errors)
    claimed: set[str] = set()
    for claim_id, claim in claims.items():
        for key in ("subject_form", "claim_type", "statement"):
            if not _nonempty(claim.get(key)):
                errors.append(f"claim {claim_id}.{key} is required")
        if claim.get("claim_type") == "derived_form" and any(
            separator in str(claim.get("subject_form", "")) for separator in DERIVED_SEPARATORS
        ):
            errors.append(f"derived claim {claim_id} must contain exactly one subject_form")
        fact_ids = _strings(
            claim.get("source_fact_ids"), f"claim {claim_id}.source_fact_ids", errors
        )
        claimed.update(fact_ids)
        unknown = sorted(set(fact_ids) - set(facts))
        if unknown:
            errors.append(f"claim {claim_id} references unknown facts: {', '.join(unknown)}")
        _strings(
            claim.get("article_target_ids"),
            f"claim {claim_id}.article_target_ids",
            errors,
            allow_empty=True,
        )
        supports = _index(
            claim.get("source_supports"),
            f"claim {claim_id}.source_supports",
            "source_fact_id",
            errors,
        )
        if set(supports) != set(fact_ids):
            errors.append(f"claim {claim_id}.source_supports must cover source_fact_ids exactly")
        for fact_id, support in supports.items():
            if not _nonempty(support.get("support_summary")) or len(
                str(support.get("support_summary", "")).strip()
            ) < 12:
                errors.append(f"claim {claim_id} support for {fact_id} needs a specific support_summary")
    unclaimed = sorted(covered - claimed)
    if unclaimed:
        errors.append("source facts covered by union but absent from claim_units: " + ", ".join(unclaimed))

    final = manifest.get("final_review")
    if not isinstance(final, dict):
        return errors + ["final_review is required"]
    results = _index(
        final.get("source_inventory_results"),
        "final_review.source_inventory_results",
        "union_id",
        errors,
    )
    if set(results) != set(union):
        missing = sorted(set(union) - set(results))
        extra = sorted(set(results) - set(union))
        if missing:
            errors.append("final source inventory results missing union ids: " + ", ".join(missing))
        if extra:
            errors.append("final source inventory results contain unknown union ids: " + ", ".join(extra))
    decision = str(final.get("decision", "")).lower()
    for union_id, result in results.items():
        item = union.get(union_id, {})
        checked_facts = set(
            _strings(
                result.get("source_fact_ids_checked"),
                f"final source result {union_id}.source_fact_ids_checked",
                errors,
            )
        )
        expected_facts = {str(value) for value in item.get("source_fact_ids", []) if _nonempty(value)}
        if checked_facts != expected_facts:
            errors.append(f"final source result {union_id} must check every source fact exactly")
        checked_targets = set(
            _strings(
                result.get("article_target_ids_checked"),
                f"final source result {union_id}.article_target_ids_checked",
                errors,
                allow_empty=True,
            )
        )
        expected_targets = {
            str(value) for value in item.get("article_target_ids", []) if _nonempty(value)
        }
        if not expected_targets.issubset(checked_targets):
            errors.append(f"final source result {union_id} omits article targets")
        if result.get("status") not in {"pass", "fail"}:
            errors.append(f"final source result {union_id}.status must be pass or fail")
        if decision == "pass" and result.get("status") != "pass":
            errors.append(f"final decision pass requires source inventory result {union_id} to pass")
        if not _nonempty(result.get("notes")):
            errors.append(f"final source result {union_id}.notes is required")
    return errors


def _validate_v2(
    manifest: dict[str, Any], gate: dict[str, Any], *, allow_incomplete: bool
) -> list[str]:
    errors: list[str] = []
    profile = gate.get("profile")
    profile_limits = PROFILES.get(str(profile), {})
    if not profile_limits:
        errors.append("source_first_audit.profile must be standard or extended")
    if profile == "extended" and not _nonempty(gate.get("profile_reason")):
        errors.append("extended source-first profile requires profile_reason")

    limits = gate.get("limits")
    if not isinstance(limits, dict):
        errors.append("source_first_audit.limits must be an object")
        limits = {}
    for key, expected in profile_limits.items():
        if limits.get(key) != expected:
            errors.append(f"source_first_audit.limits.{key} must equal {expected} for {profile}")

    usage = gate.get("usage")
    if not isinstance(usage, dict):
        errors.append("source_first_audit.usage must be an object")
        usage = {}
    counters = (
        ("sources_used", "max_sources"),
        ("facts_used", "max_facts"),
        ("research_rounds_used", "max_research_rounds"),
        ("post_cold_rechecks_used", "max_post_cold_rechecks"),
        ("final_attempts_used", "max_final_attempts"),
    )
    for used_key, limit_key in counters:
        used = _integer(usage.get(used_key), f"source_first_audit.usage.{used_key}", errors)
        if used is not None and used > profile_limits.get(limit_key, used):
            errors.append(f"source_first_audit.usage.{used_key} exceeds {limit_key}")

    status = gate.get("research_status")
    if status not in {"in_progress", "complete", "budget_exhausted"}:
        errors.append("source_first_audit.research_status is invalid")
    if status != "complete" and not allow_incomplete:
        errors.append("source-first research must be complete before merge validation")
    research_rounds = usage.get("research_rounds_used")
    if (
        status == "complete"
        and isinstance(research_rounds, int)
        and not isinstance(research_rounds, bool)
        and research_rounds < 1
    ):
        errors.append("complete inventory requires at least one research round")
    if status == "budget_exhausted":
        if not _nonempty(gate.get("stop_reason")):
            errors.append("budget_exhausted research requires stop_reason")
        _strings(gate.get("open_questions"), "source_first_audit.open_questions", errors)

    sources, facts = _sources(gate, errors, v2=True, allow_empty=allow_incomplete)
    if usage.get("sources_used") != len(sources):
        errors.append("source_first_audit.usage.sources_used must match sources length")
    if usage.get("facts_used") != len(facts):
        errors.append("source_first_audit.usage.facts_used must match atomic fact count")
    general_groups = {
        str(source.get("independence_group"))
        for source in sources.values()
        if source.get("source_role") == "general_lexicon"
        and _nonempty(source.get("independence_group"))
    }
    if status == "complete" and len(general_groups) < 2:
        errors.append("complete inventory requires two independent general_lexicon sources")

    axes = _index(gate.get("coverage_axes"), "source_first_audit.coverage_axes", "axis", errors)
    missing_axes = sorted(set(COVERAGE_AXES) - set(axes))
    extra_axes = sorted(set(axes) - set(COVERAGE_AXES))
    if missing_axes:
        errors.append("coverage_axes missing: " + ", ".join(missing_axes))
    if extra_axes:
        errors.append("coverage_axes unknown: " + ", ".join(extra_axes))
    for axis, item in axes.items():
        axis_status = item.get("status")
        fact_ids = _strings(
            item.get("source_fact_ids"),
            f"coverage axis {axis}.source_fact_ids",
            errors,
            allow_empty=axis_status in {"pending", "not_applicable"},
        )
        unknown = sorted(set(fact_ids) - set(facts))
        if unknown:
            errors.append(f"coverage axis {axis} references unknown facts: {', '.join(unknown)}")
        if axis_status not in {"pending", "covered", "not_applicable"}:
            errors.append(f"coverage axis {axis}.status is invalid")
        if status == "complete" and axis_status == "pending":
            errors.append(f"complete inventory cannot leave {axis} pending")
        if axis_status == "covered" and not fact_ids:
            errors.append(f"covered axis {axis} requires source_fact_ids")
        if axis_status == "not_applicable" and not _nonempty(item.get("notes")):
            errors.append(f"not_applicable axis {axis} requires notes")

    union = _index(gate.get("source_union"), "source_first_audit.source_union", "id", errors)
    covered: set[str] = set()
    for union_id, item in union.items():
        fact_ids = _strings(
            item.get("source_fact_ids"), f"source union {union_id}.source_fact_ids", errors
        )
        covered.update(fact_ids)
        unknown = sorted(set(fact_ids) - set(facts))
        if unknown:
            errors.append(f"source union {union_id} references unknown facts: {', '.join(unknown)}")
        if not _nonempty(item.get("canonical_statement")):
            errors.append(f"source union {union_id}.canonical_statement is required")
        if item.get("disposition") not in {"included", "integrated", "excluded"}:
            errors.append(f"source union {union_id}.disposition is invalid")
        if not _nonempty(item.get("rationale")):
            errors.append(f"source union {union_id}.rationale is required")
    if status == "complete":
        missing = sorted(set(facts) - covered)
        if missing:
            errors.append("source facts missing from source_union: " + ", ".join(missing))

    claims = _index(gate.get("claim_units"), "source_first_audit.claim_units", "id", errors)
    claim_count: dict[str, int] = {union_id: 0 for union_id in union}
    supported: dict[str, set[str]] = {union_id: set() for union_id in union}
    for claim_id, claim in claims.items():
        for key in ("subject_form", "claim_type", "statement"):
            if not _nonempty(claim.get(key)):
                errors.append(f"claim {claim_id}.{key} is required")
        if claim.get("claim_type") == "derived_form" and any(
            separator in str(claim.get("subject_form", "")) for separator in DERIVED_SEPARATORS
        ):
            errors.append(f"derived claim {claim_id} must contain exactly one subject_form")
        union_ids = _strings(claim.get("union_ids"), f"claim {claim_id}.union_ids", errors)
        unknown_unions = sorted(set(union_ids) - set(union))
        if unknown_unions:
            errors.append(f"claim {claim_id} references unknown unions: {', '.join(unknown_unions)}")
        _strings(claim.get("article_target_ids"), f"claim {claim_id}.article_target_ids", errors)
        supports = _index(
            claim.get("source_supports"),
            f"claim {claim_id}.source_supports",
            "source_fact_id",
            errors,
        )
        allowed: set[str] = set()
        for union_id in union_ids:
            claim_count[union_id] = claim_count.get(union_id, 0) + 1
            union_facts = {
                str(value)
                for value in union.get(union_id, {}).get("source_fact_ids", [])
                if _nonempty(value)
            }
            allowed.update(union_facts)
            supported.setdefault(union_id, set()).update(set(supports) & union_facts)
        outside = sorted(set(supports) - allowed)
        if outside:
            errors.append(
                f"claim {claim_id} source_supports are outside referenced unions: {', '.join(outside)}"
            )
        for fact_id, support in supports.items():
            if fact_id not in facts:
                errors.append(f"claim {claim_id} references unknown fact {fact_id}")
            if not _nonempty(support.get("support_summary")) or len(
                str(support.get("support_summary", "")).strip()
            ) < 12:
                errors.append(f"claim {claim_id} support for {fact_id} needs a specific support_summary")
    if status == "complete":
        for union_id, item in union.items():
            if item.get("disposition") == "excluded":
                continue
            expected = {
                str(value) for value in item.get("source_fact_ids", []) if _nonempty(value)
            }
            if claim_count.get(union_id, 0) == 0:
                errors.append(f"included source union {union_id} requires a claim unit")
            elif supported.get(union_id, set()) != expected:
                errors.append(f"claim units for source union {union_id} must support every source fact")

    if status == "complete":
        if gate.get("inventory_completed_before_article_comparison") is not True:
            errors.append("inventory_completed_before_article_comparison must be true")
        inventory_time = _parse_time(
            gate.get("inventory_completed_at"),
            "source_first_audit.inventory_completed_at",
            errors,
        )
        comparison_time = _parse_time(
            gate.get("article_comparison_started_at"),
            "source_first_audit.article_comparison_started_at",
            errors,
        )
        if inventory_time and comparison_time and inventory_time >= comparison_time:
            errors.append("source inventory must be completed before article comparison starts")

    final = manifest.get("final_review")
    if not isinstance(final, dict):
        return errors if allow_incomplete else errors + ["final_review is required"]
    decision = str(final.get("decision", "")).lower()
    if decision not in {"pass", "reject"} and not allow_incomplete:
        errors.append("final_review.decision must be pass or reject")
    results = _index(
        final.get("source_inventory_results", []),
        "final_review.source_inventory_results",
        "union_id",
        errors,
    )
    if not allow_incomplete and set(results) != set(union):
        missing = sorted(set(union) - set(results))
        extra = sorted(set(results) - set(union))
        if missing:
            errors.append("final source inventory results missing union ids: " + ", ".join(missing))
        if extra:
            errors.append("final source inventory results contain unknown union ids: " + ", ".join(extra))
    for union_id, result in results.items():
        if union_id not in union:
            continue
        result_status = result.get("status")
        if result_status not in {"pending", "pass", "fail"}:
            errors.append(f"final source result {union_id}.status is invalid")
        if not allow_incomplete and result_status == "pending":
            errors.append(f"final source result {union_id} cannot remain pending")
        if decision == "pass" and result_status != "pass":
            errors.append(f"final decision pass requires source inventory result {union_id} to pass")
        if result_status in {"pass", "fail"} and not _nonempty(result.get("notes")):
            errors.append(f"final source result {union_id}.notes is required")
    final_attempts = usage.get("final_attempts_used")
    if (
        decision in {"pass", "reject"}
        and isinstance(final_attempts, int)
        and not isinstance(final_attempts, bool)
        and final_attempts < 1
    ):
        errors.append("a completed final decision requires final_attempts_used >= 1")
    return errors


def validate_manifest(
    manifest: dict[str, Any], *, require_current: bool = False, allow_incomplete: bool = False
) -> list[str]:
    gate = manifest.get("source_first_audit")
    if not isinstance(gate, dict):
        return ["source_first_audit is required"]
    version = gate.get("version")
    if require_current and version != CURRENT_VERSION:
        return [f"source_first_audit.version must be {CURRENT_VERSION} for new or changed audits"]
    if version == V1_VERSION:
        return _validate_v1(manifest, gate)
    if version == V2_VERSION:
        return _validate_v2(manifest, gate, allow_incomplete=allow_incomplete)
    return [f"source_first_audit.version must be {V1_VERSION} or {V2_VERSION}"]


def validate_path(
    path: Path, *, require_current: bool = False, allow_incomplete: bool = False
) -> list[str]:
    errors: list[str] = []
    manifest = _load(path, errors)
    if manifest:
        manifest = _hydrate_generated_final_review(manifest, errors)
        errors.extend(
            validate_manifest(
                manifest,
                require_current=require_current,
                allow_incomplete=allow_incomplete,
            )
        )
    return errors


def _hydrate_generated_final_review(
    manifest: dict[str, Any],
    errors: list[str],
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Read the final raw result referenced by a generated v4 manifest.

    The compact canonical manifest intentionally does not duplicate item-level
    final-review results.  The source-first CLI still needs those union results,
    so it follows the generator-recorded path only after verifying the recorded
    SHA-256.  This keeps raw output authoritative without reintroducing manual
    manifest fields.
    """
    if manifest.get("schema_version") != "content_audit_v4" or isinstance(
        manifest.get("final_review"), dict
    ):
        return manifest
    provenance = manifest.get("raw_outputs")
    final_ref = provenance.get("final_review") if isinstance(provenance, dict) else None
    if not isinstance(final_ref, dict):
        errors.append("generated v4 audit is missing final_review raw provenance")
        return manifest
    relative = final_ref.get("path")
    if not _nonempty(relative):
        errors.append("generated v4 final_review raw path is required")
        return manifest
    candidate = (repo_root / str(relative)).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        errors.append("generated v4 final_review raw path escapes the repository")
        return manifest
    raw_errors: list[str] = []
    raw = _load(candidate, raw_errors)
    if raw_errors:
        errors.extend(raw_errors)
        return manifest
    expected_sha = final_ref.get("sha256")
    actual_sha = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if expected_sha != actual_sha:
        errors.append("generated v4 final_review raw SHA-256 does not match provenance")
        return manifest
    hydrated = dict(manifest)
    hydrated["final_review"] = {
        "decision": raw.get("decision"),
        "source_inventory_results": raw.get("source_inventory_results"),
    }
    return hydrated


def _changed_files(base: str, head: str) -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AM", base, head, "--", "entries", "audits"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _print(
    paths: list[Path], *, require_current: bool = False, allow_incomplete: bool = False
) -> int:
    failed = False
    for path in paths:
        errors = validate_path(
            path,
            require_current=require_current,
            allow_incomplete=allow_incomplete,
        )
        if errors:
            failed = True
            print(f"FAIL {path.relative_to(REPO_ROOT)}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        else:
            print(f"PASS {path.relative_to(REPO_ROOT)}")
    return 1 if failed else 0


def _load_entry(raw_entry: str) -> tuple[Path, dict[str, Any]]:
    path = _audit_path(REPO_ROOT / raw_entry)
    errors: list[str] = []
    manifest = _load(path, errors)
    if errors:
        raise ValueError("; ".join(errors))
    return path, manifest


def _refresh_usage(gate: dict[str, Any]) -> None:
    sources = gate.get("sources") if isinstance(gate.get("sources"), list) else []
    facts = sum(
        len(source.get("facts", []))
        for source in sources
        if isinstance(source, dict) and isinstance(source.get("facts"), list)
    )
    usage = gate.setdefault("usage", {})
    if isinstance(usage, dict):
        usage["sources_used"] = len(sources)
        usage["facts_used"] = facts


def _template(profile: str, reason: str) -> dict[str, Any]:
    return {
        "version": V2_VERSION,
        "profile": profile,
        "profile_reason": reason,
        "limits": dict(PROFILES[profile]),
        "usage": {
            "sources_used": 0,
            "facts_used": 0,
            "research_rounds_used": 0,
            "post_cold_rechecks_used": 0,
            "final_attempts_used": 0,
        },
        "research_status": "in_progress",
        "stop_reason": "",
        "open_questions": [],
        "inventory_completed_before_article_comparison": False,
        "inventory_completed_at": None,
        "article_comparison_started_at": None,
        "coverage_axes": [
            {"axis": axis, "status": "pending", "source_fact_ids": [], "notes": ""}
            for axis in COVERAGE_AXES
        ],
        "sources": [],
        "source_union": [],
        "claim_units": [],
    }


def command_validate_entries(args: argparse.Namespace) -> int:
    paths: list[Path] = []
    failed = False
    for raw in args.entries:
        try:
            path = _audit_path(REPO_ROOT / raw)
        except ValueError as exc:
            print(f"FAIL {raw}: {exc}", file=sys.stderr)
            failed = True
            continue
        if not path.exists():
            print(f"FAIL {path.relative_to(REPO_ROOT)}: audit manifest missing", file=sys.stderr)
            failed = True
            continue
        paths.append(path)
    return int(
        failed
        or bool(
            _print(
                paths,
                require_current=args.require_current,
                allow_incomplete=args.allow_incomplete,
            )
        )
    )


def _is_non_entry_audit(path: Path) -> bool:
    return path.name in {
        "escaped_defect_taxonomy.json",
        "escaped_defects.json",
        "review_invalidations.json",
    }


def command_validate_changed(args: argparse.Namespace) -> int:
    paths: set[Path] = set()
    for raw in _changed_files(args.base, args.head):
        path = REPO_ROOT / raw
        if raw.startswith("entries/") and raw.endswith(".md"):
            paths.add(_audit_path(path))
        elif raw.startswith("audits/") and raw.endswith(".json"):
            rel = Path(raw).relative_to("audits")
            if any(part in {"runs", "history", "workflow_runs"} for part in rel.parts):
                continue
            if _is_non_entry_audit(path):
                continue
            paths.add(path)
    missing = [path for path in sorted(paths) if not path.exists()]
    for path in missing:
        print(f"FAIL {path.relative_to(REPO_ROOT)}: audit manifest missing", file=sys.stderr)
    return 1 if missing else _print(sorted(paths), require_current=True)


def command_init(args: argparse.Namespace) -> int:
    try:
        path, manifest = _load_entry(args.entry)
    except ValueError as exc:
        print(f"FAIL {args.entry}: {exc}", file=sys.stderr)
        return 1
    if isinstance(manifest.get("source_first_audit"), dict) and not args.replace:
        print("FAIL source_first_audit already exists", file=sys.stderr)
        return 1
    reason = args.reason or ("bounded default profile" if args.profile == "standard" else "")
    if not reason:
        print("FAIL extended profile requires --reason", file=sys.stderr)
        return 1
    manifest["source_first_audit"] = _template(args.profile, reason)
    final = manifest.setdefault("final_review", {})
    if isinstance(final, dict):
        final["source_inventory_results"] = []
    _write(path, manifest)
    print(f"INITIALIZED {path.relative_to(REPO_ROOT)} ({args.profile})")
    return 0


def command_close_inventory(args: argparse.Namespace) -> int:
    try:
        path, manifest = _load_entry(args.entry)
    except ValueError as exc:
        print(f"FAIL {args.entry}: {exc}", file=sys.stderr)
        return 1
    gate = manifest.get("source_first_audit")
    if not isinstance(gate, dict) or gate.get("version") != V2_VERSION:
        print(f"FAIL source_first_audit.version must be {V2_VERSION}", file=sys.stderr)
        return 1
    _refresh_usage(gate)
    gate["usage"]["research_rounds_used"] = args.research_rounds
    gate["research_status"] = "complete"
    gate["stop_reason"] = "coverage_axes_closed"
    gate["open_questions"] = []
    gate["inventory_completed_before_article_comparison"] = True
    gate["inventory_completed_at"] = _now()
    gate["article_comparison_started_at"] = None
    errors = _validate_v2(manifest, gate, allow_incomplete=True)
    errors = [error for error in errors if "article_comparison_started_at" not in error]
    if errors:
        print("FAIL inventory cannot be closed", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    _write(path, manifest)
    print(f"CLOSED {path.relative_to(REPO_ROOT)}")
    return 0


def command_start_comparison(args: argparse.Namespace) -> int:
    try:
        path, manifest = _load_entry(args.entry)
    except ValueError as exc:
        print(f"FAIL {args.entry}: {exc}", file=sys.stderr)
        return 1
    gate = manifest.get("source_first_audit")
    if (
        not isinstance(gate, dict)
        or gate.get("version") != V2_VERSION
        or gate.get("research_status") != "complete"
        or not _nonempty(gate.get("inventory_completed_at"))
    ):
        print("FAIL close the v2 inventory before article comparison", file=sys.stderr)
        return 1
    if _nonempty(gate.get("article_comparison_started_at")):
        print("FAIL article comparison has already started", file=sys.stderr)
        return 1
    errors = _validate_v2(manifest, gate, allow_incomplete=True)
    errors = [error for error in errors if "article_comparison_started_at" not in error]
    if errors:
        print("FAIL source inventory is not valid", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    gate["article_comparison_started_at"] = _now()
    _write(path, manifest)
    print(f"STARTED {path.relative_to(REPO_ROOT)}")
    return 0


def command_prepare_final(args: argparse.Namespace) -> int:
    try:
        path, manifest = _load_entry(args.entry)
    except ValueError as exc:
        print(f"FAIL {args.entry}: {exc}", file=sys.stderr)
        return 1
    gate = manifest.get("source_first_audit")
    if (
        not isinstance(gate, dict)
        or gate.get("version") != V2_VERSION
        or not _nonempty(gate.get("article_comparison_started_at"))
    ):
        print("FAIL start article comparison before final preparation", file=sys.stderr)
        return 1
    final = manifest.setdefault("final_review", {})
    if not isinstance(final, dict):
        print("FAIL final_review must be an object", file=sys.stderr)
        return 1
    final["source_inventory_results"] = [
        {"union_id": item["id"], "status": "pending", "notes": ""}
        for item in gate.get("source_union", [])
        if isinstance(item, dict) and _nonempty(item.get("id"))
    ]
    _write(path, manifest)
    print(f"PREPARED {path.relative_to(REPO_ROOT)}")
    return 0


def command_record_attempt(args: argparse.Namespace) -> int:
    try:
        path, manifest = _load_entry(args.entry)
    except ValueError as exc:
        print(f"FAIL {args.entry}: {exc}", file=sys.stderr)
        return 1
    gate = manifest.get("source_first_audit")
    if not isinstance(gate, dict) or gate.get("version") != V2_VERSION:
        print(f"FAIL source_first_audit.version must be {V2_VERSION}", file=sys.stderr)
        return 1
    key, limit_key = (
        ("post_cold_rechecks_used", "max_post_cold_rechecks")
        if args.stage == "post-cold"
        else ("final_attempts_used", "max_final_attempts")
    )
    current = gate["usage"][key]
    limit = gate["limits"][limit_key]
    if current >= limit:
        print(f"STOP {args.stage} budget exhausted ({current}/{limit})", file=sys.stderr)
        return 2
    gate["usage"][key] = current + 1
    _write(path, manifest)
    print(f"RECORDED {args.stage} {current + 1}/{limit}")
    return 0


def command_stop(args: argparse.Namespace) -> int:
    try:
        path, manifest = _load_entry(args.entry)
    except ValueError as exc:
        print(f"FAIL {args.entry}: {exc}", file=sys.stderr)
        return 1
    gate = manifest.get("source_first_audit")
    if not isinstance(gate, dict) or gate.get("version") != V2_VERSION:
        print(f"FAIL source_first_audit.version must be {V2_VERSION}", file=sys.stderr)
        return 1
    _refresh_usage(gate)
    gate["research_status"] = "budget_exhausted"
    gate["stop_reason"] = args.reason
    gate["open_questions"] = args.open_question
    _write(path, manifest)
    print(f"STOPPED {path.relative_to(REPO_ROOT)}; preserve as needs_review")
    return 0


def command_summary(args: argparse.Namespace) -> int:
    try:
        path, manifest = _load_entry(args.entry)
    except ValueError as exc:
        print(f"FAIL {args.entry}: {exc}", file=sys.stderr)
        return 1
    gate = manifest.get("source_first_audit")
    if not isinstance(gate, dict):
        print("FAIL source_first_audit is missing", file=sys.stderr)
        return 1
    _refresh_usage(gate)
    print(
        json.dumps(
            {
                "audit": str(path.relative_to(REPO_ROOT)),
                "version": gate.get("version"),
                "profile": gate.get("profile"),
                "research_status": gate.get("research_status"),
                "limits": gate.get("limits"),
                "usage": gate.get("usage"),
                "open_questions": gate.get("open_questions"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and validate bounded source-first claim-centric audit records"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    entries = sub.add_parser("validate-entries")
    entries.add_argument("entries", nargs="+")
    entries.add_argument("--require-current", action="store_true")
    entries.add_argument("--allow-incomplete", action="store_true")
    entries.set_defaults(func=command_validate_entries)
    changed = sub.add_parser("validate-changed")
    changed.add_argument("--base", required=True)
    changed.add_argument("--head", required=True)
    changed.set_defaults(func=command_validate_changed)
    init = sub.add_parser("init")
    init.add_argument("entry")
    init.add_argument("--profile", choices=sorted(PROFILES), default="standard")
    init.add_argument("--reason", default="")
    init.add_argument("--replace", action="store_true")
    init.set_defaults(func=command_init)
    close = sub.add_parser("close-inventory")
    close.add_argument("entry")
    close.add_argument("--research-rounds", type=int, required=True)
    close.set_defaults(func=command_close_inventory)
    compare = sub.add_parser("start-comparison")
    compare.add_argument("entry")
    compare.set_defaults(func=command_start_comparison)
    prepare = sub.add_parser("prepare-final")
    prepare.add_argument("entry")
    prepare.set_defaults(func=command_prepare_final)
    attempt = sub.add_parser("record-attempt")
    attempt.add_argument("entry")
    attempt.add_argument("--stage", choices=("post-cold", "final"), required=True)
    attempt.set_defaults(func=command_record_attempt)
    stop = sub.add_parser("stop")
    stop.add_argument("entry")
    stop.add_argument("--reason", required=True)
    stop.add_argument("--open-question", action="append", required=True)
    stop.set_defaults(func=command_stop)
    summary = sub.add_parser("summary")
    summary.add_argument("entry")
    summary.set_defaults(func=command_summary)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
