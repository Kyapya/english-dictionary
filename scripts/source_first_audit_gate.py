from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION = "source_first_audit_v1"
DERIVED_SEPARATORS = ("/", ",", ";", "、", "・")
FINAL_DECISIONS = {"pass", "reject"}


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


def _index(items: Any, label: str, key: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{i}] must be an object")
            continue
        item_id = item.get(key)
        if not _nonempty(item_id):
            errors.append(f"{label}[{i}].{key} is required")
            continue
        if str(item_id) in result:
            errors.append(f"{label} contains duplicate {key} {item_id}")
            continue
        result[str(item_id)] = item
    return result


def _strings(value: Any, label: str, errors: list[str], *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    result: list[str] = []
    for i, item in enumerate(value):
        if not _nonempty(item):
            errors.append(f"{label}[{i}] must be a non-empty string")
            continue
        result.append(str(item))
    if not allow_empty and not result:
        errors.append(f"{label} must not be empty")
    if len(result) != len(set(result)):
        errors.append(f"{label} must not contain duplicates")
    return result


def _parse_time(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not _nonempty(value):
        errors.append(f"{label} is required")
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be ISO-8601")
        return None


def _audit_path(entry: Path) -> Path:
    rel = entry.resolve().relative_to(REPO_ROOT.resolve())
    if not rel.parts or rel.parts[0] != "entries":
        raise ValueError(f"entry must be under entries/: {entry}")
    return REPO_ROOT / "audits" / Path(*rel.parts[1:]).with_suffix(".json")


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    gate = manifest.get("source_first_audit")
    if not isinstance(gate, dict):
        return ["source_first_audit is required"]
    if gate.get("version") != VERSION:
        errors.append(f"source_first_audit.version must be {VERSION}")
    if gate.get("inventory_completed_before_article_comparison") is not True:
        errors.append("inventory_completed_before_article_comparison must be true")
    inv_time = _parse_time(gate.get("inventory_completed_at"), "source_first_audit.inventory_completed_at", errors)
    compare_time = _parse_time(gate.get("article_comparison_started_at"), "source_first_audit.article_comparison_started_at", errors)
    if inv_time is not None and compare_time is not None and inv_time >= compare_time:
        errors.append("source inventory must be completed before article comparison starts")

    sources = _index(gate.get("sources"), "source_first_audit.sources", "id", errors)
    if not sources:
        errors.append("source_first_audit.sources must not be empty")

    facts: dict[str, dict[str, Any]] = {}
    for source_id, source in sources.items():
        for key in ("locator", "source_type"):
            if not _nonempty(source.get(key)):
                errors.append(f"source {source_id}.{key} is required")
        source_facts = _index(source.get("facts"), f"source {source_id}.facts", "id", errors)
        if not source_facts:
            errors.append(f"source {source_id}.facts must not be empty")
        for fact_id, fact in source_facts.items():
            if fact_id in facts:
                errors.append(f"duplicate source fact id {fact_id}")
                continue
            facts[fact_id] = fact
            for key in ("form", "kind", "statement", "source_detail"):
                if not _nonempty(fact.get(key)):
                    errors.append(f"source fact {fact_id}.{key} is required")
            if fact.get("kind") == "derived_form":
                form = str(fact.get("form", ""))
                if any(sep in form for sep in DERIVED_SEPARATORS):
                    errors.append(f"derived source fact {fact_id} must contain exactly one form")

    union = _index(gate.get("source_union"), "source_first_audit.source_union", "id", errors)
    if not union:
        errors.append("source_first_audit.source_union must not be empty")
    covered_facts: set[str] = set()
    for union_id, item in union.items():
        fact_ids = _strings(item.get("source_fact_ids"), f"source union {union_id}.source_fact_ids", errors)
        unknown = sorted(set(fact_ids) - set(facts))
        if unknown:
            errors.append(f"source union {union_id} references unknown facts: {', '.join(unknown)}")
        covered_facts.update(fact_ids)
        if not _nonempty(item.get("canonical_statement")):
            errors.append(f"source union {union_id}.canonical_statement is required")
        if item.get("disposition") not in {"included", "integrated", "excluded"}:
            errors.append(f"source union {union_id}.disposition is invalid")
        if not _nonempty(item.get("rationale")):
            errors.append(f"source union {union_id}.rationale is required")
        _strings(item.get("article_target_ids"), f"source union {union_id}.article_target_ids", errors, allow_empty=True)
    missing_facts = sorted(set(facts) - covered_facts)
    if missing_facts:
        errors.append("source facts missing from source_union: " + ", ".join(missing_facts))

    claims = _index(gate.get("claim_units"), "source_first_audit.claim_units", "id", errors)
    if not claims:
        errors.append("source_first_audit.claim_units must not be empty")
    claimed_facts: set[str] = set()
    for claim_id, claim in claims.items():
        for key in ("subject_form", "claim_type", "statement"):
            if not _nonempty(claim.get(key)):
                errors.append(f"claim {claim_id}.{key} is required")
        if claim.get("claim_type") == "derived_form":
            form = str(claim.get("subject_form", ""))
            if any(sep in form for sep in DERIVED_SEPARATORS):
                errors.append(f"derived claim {claim_id} must contain exactly one subject_form")
        fact_ids = _strings(claim.get("source_fact_ids"), f"claim {claim_id}.source_fact_ids", errors)
        unknown = sorted(set(fact_ids) - set(facts))
        if unknown:
            errors.append(f"claim {claim_id} references unknown facts: {', '.join(unknown)}")
        claimed_facts.update(fact_ids)
        _strings(claim.get("article_target_ids"), f"claim {claim_id}.article_target_ids", errors, allow_empty=True)
        supports = _index(claim.get("source_supports"), f"claim {claim_id}.source_supports", "source_fact_id", errors)
        if set(supports) != set(fact_ids):
            errors.append(f"claim {claim_id}.source_supports must cover source_fact_ids exactly")
        for source_fact_id, support in supports.items():
            summary = support.get("support_summary")
            if not _nonempty(summary) or len(str(summary).strip()) < 12:
                errors.append(f"claim {claim_id} support for {source_fact_id} needs a specific support_summary")
    unclaimed = sorted(covered_facts - claimed_facts)
    if unclaimed:
        errors.append("source facts covered by union but absent from claim_units: " + ", ".join(unclaimed))

    final = manifest.get("final_review")
    if not isinstance(final, dict):
        errors.append("final_review is required")
        return errors
    results = _index(final.get("source_inventory_results"), "final_review.source_inventory_results", "union_id", errors)
    if set(results) != set(union):
        missing = sorted(set(union) - set(results))
        extra = sorted(set(results) - set(union))
        if missing:
            errors.append("final source inventory results missing union ids: " + ", ".join(missing))
        if extra:
            errors.append("final source inventory results contain unknown union ids: " + ", ".join(extra))
    decision = str(final.get("decision", "")).lower()
    for union_id, result in results.items():
        expected = union.get(union_id, {})
        checked_facts = set(_strings(result.get("source_fact_ids_checked"), f"final source result {union_id}.source_fact_ids_checked", errors))
        expected_facts = set(str(x) for x in expected.get("source_fact_ids", []) if _nonempty(x))
        if checked_facts != expected_facts:
            errors.append(f"final source result {union_id} must check every source fact exactly")
        checked_targets = set(_strings(result.get("article_target_ids_checked"), f"final source result {union_id}.article_target_ids_checked", errors, allow_empty=True))
        expected_targets = set(str(x) for x in expected.get("article_target_ids", []) if _nonempty(x))
        if not expected_targets.issubset(checked_targets):
            errors.append(f"final source result {union_id} omits article targets")
        if result.get("status") not in {"pass", "fail"}:
            errors.append(f"final source result {union_id}.status must be pass or fail")
        if decision == "pass" and result.get("status") != "pass":
            errors.append(f"final decision pass requires source inventory result {union_id} to pass")
        if not _nonempty(result.get("notes")):
            errors.append(f"final source result {union_id}.notes is required")
    return errors


def validate_path(path: Path) -> list[str]:
    errors: list[str] = []
    manifest = _load(path, errors)
    if manifest:
        errors.extend(validate_manifest(manifest))
    return errors


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


def _print(paths: list[Path]) -> int:
    failed = False
    for path in paths:
        errors = validate_path(path)
        if errors:
            failed = True
            print(f"FAIL {path.relative_to(REPO_ROOT)}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        else:
            print(f"PASS {path.relative_to(REPO_ROOT)}")
    return 1 if failed else 0


def command_validate_entries(args: argparse.Namespace) -> int:
    paths: list[Path] = []
    missing = False
    for raw in args.entries:
        try:
            audit = _audit_path(REPO_ROOT / raw)
        except ValueError as exc:
            print(f"FAIL {raw}: {exc}", file=sys.stderr)
            missing = True
            continue
        if not audit.exists():
            print(f"FAIL {audit.relative_to(REPO_ROOT)}: audit manifest missing", file=sys.stderr)
            missing = True
            continue
        paths.append(audit)
    return 1 if missing or _print(paths) else 0


def command_validate_changed(args: argparse.Namespace) -> int:
    paths: set[Path] = set()
    for raw in _changed_files(args.base, args.head):
        path = REPO_ROOT / raw
        if raw.startswith("entries/") and raw.endswith(".md"):
            paths.add(_audit_path(path))
        elif raw.startswith("audits/") and raw.endswith(".json"):
            rel = Path(raw).relative_to("audits")
            if any(part in {"runs", "history"} for part in rel.parts):
                continue
            if path.name in {"escaped_defect_taxonomy.json", "review_invalidations.json"}:
                continue
            paths.add(path)
    missing = [path for path in sorted(paths) if not path.exists()]
    if missing:
        for path in missing:
            print(f"FAIL {path.relative_to(REPO_ROOT)}: audit manifest missing", file=sys.stderr)
        return 1
    return _print(sorted(paths))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate source-first claim-centric audit records")
    sub = parser.add_subparsers(dest="command", required=True)
    entries = sub.add_parser("validate-entries")
    entries.add_argument("entries", nargs="+")
    entries.set_defaults(func=command_validate_entries)
    changed = sub.add_parser("validate-changed")
    changed.add_argument("--base", required=True)
    changed.add_argument("--head", required=True)
    changed.set_defaults(func=command_validate_changed)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
