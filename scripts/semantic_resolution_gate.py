from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_GATE_VERSION = "semantic_resolution_v2"
CANONICAL_AUDIT_SCHEMA = "content_audit_v3"
FINAL_DECISIONS = {"pass", "reject"}
INVALIDATION_REGISTRY = Path("audits/review_invalidations.json")
INVALIDATION_SCHEMA_VERSION = "review_invalidations_v1"


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _body_sha256(entry_path: Path) -> str:
    text = entry_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    body = text
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                body = "\n".join(lines[index + 1 :])
                break
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _entry_body(entry_path: Path) -> str:
    text = entry_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[index + 1 :])
    return text


def _front_matter(entry_path: Path) -> dict[str, str]:
    text = entry_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"')
    return values


def _matching_invalidation(
    entry_path: Path, body_sha: str, repo_root: Path
) -> dict[str, Any] | None:
    registry_path = repo_root / INVALIDATION_REGISTRY
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if (
        not isinstance(registry, dict)
        or registry.get("schema_version") != INVALIDATION_SCHEMA_VERSION
        or not isinstance(registry.get("invalidations"), list)
    ):
        return None
    relative = entry_path.resolve().relative_to(repo_root.resolve()).as_posix()
    for record in registry["invalidations"]:
        if (
            isinstance(record, dict)
            and record.get("entry_path") == relative
            and record.get("body_sha256") == body_sha
            and record.get("status") == "invalidated"
        ):
            return record
    return None


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _selected(item: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: item.get(key) for key in keys}


def _selected_list(value: Any, keys: tuple[str, ...]) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [_selected(item, keys) for item in value if isinstance(item, dict)]


def _query_result_index(
    value: Any, label: str, errors: list[str]
) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(value):
        if not isinstance(item, dict) or not _nonempty(item.get("query")):
            errors.append(f"{label}[{index}] requires a non-empty query")
            continue
        query = str(item["query"])
        if query in result:
            errors.append(f"{label} contains duplicate query {query}")
            continue
        result[query] = item
    return result


def _audit_path_for_entry(entry_path: Path, repo_root: Path = REPO_ROOT) -> Path:
    relative = entry_path.resolve().relative_to(repo_root.resolve())
    if not relative.parts or relative.parts[0] != "entries":
        raise ValueError(f"entry must be under entries/: {entry_path}")
    return repo_root / "audits" / Path(*relative.parts[1:]).with_suffix(".json")


def _load_json(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label} cannot be read as JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label} must be a JSON object")
        return {}
    return value


def _index_by_id(items: Any, label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return {}
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        item_id = item.get("id")
        if not _nonempty(item_id):
            errors.append(f"{label}[{index}] requires a non-empty id")
            continue
        if item_id in result:
            errors.append(f"{label} contains duplicate id {item_id}")
            continue
        result[item_id] = item
    return result


def _string_list(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    result: list[str] = []
    for index, item in enumerate(value):
        if not _nonempty(item):
            errors.append(f"{label}[{index}] must be a non-empty string")
            continue
        result.append(item)
    if len(result) != len(set(result)):
        errors.append(f"{label} must not contain duplicates")
    return result


def _semantic_assertions(
    candidate: dict[str, Any], label: str, errors: list[str]
) -> list[dict[str, str]]:
    raw = candidate.get("semantic_assertions")
    if not isinstance(raw, list) or not raw:
        errors.append(f"{label}.semantic_assertions must be a non-empty list")
        return []
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        item_label = f"{label}.semantic_assertions[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{item_label} must be an object")
            continue
        assertion_id = item.get("id")
        statement = item.get("statement")
        polarity = item.get("polarity")
        scope = item.get("scope")
        if not _nonempty(assertion_id):
            errors.append(f"{item_label}.id is required")
            continue
        if assertion_id in seen:
            errors.append(f"{label}.semantic_assertions contains duplicate id {assertion_id}")
            continue
        seen.add(str(assertion_id))
        if not _nonempty(statement):
            errors.append(f"{item_label}.statement is required")
        if polarity not in {"must_hold", "must_not_hold"}:
            errors.append(f"{item_label}.polarity must be must_hold or must_not_hold")
        if not _nonempty(scope):
            errors.append(f"{item_label}.scope is required")
        result.append(
            {
                "id": str(assertion_id),
                "statement": str(statement or ""),
                "polarity": str(polarity or ""),
                "scope": str(scope or ""),
            }
        )
    return result


def _normalize_assertions(candidate: dict[str, Any]) -> list[dict[str, str]]:
    raw = candidate.get("semantic_assertions")
    if not isinstance(raw, list):
        return []
    normalized: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "id": str(item.get("id", "")),
                "statement": str(item.get("statement", "")),
                "polarity": str(item.get("polarity", "")),
                "scope": str(item.get("scope", "")),
            }
        )
    return normalized


def _is_final_phase(manifest: dict[str, Any], phase: str) -> bool:
    if phase == "final":
        return True
    if phase == "handoff":
        return False
    if phase != "auto":
        raise ValueError(f"unknown validation phase: {phase}")
    final = manifest.get("final_review")
    if not isinstance(final, dict):
        return False
    return str(final.get("decision", "")).lower() in FINAL_DECISIONS


def _validate_raw_stage_bindings(
    manifest: dict[str, Any],
    repo_root: Path,
    errors: list[str],
    *,
    final_phase: bool,
) -> dict[str, Any]:
    cycle = manifest.get("current_cycle")
    raw_outputs = cycle.get("raw_outputs") if isinstance(cycle, dict) else None
    if not isinstance(raw_outputs, dict):
        errors.append("current_cycle.raw_outputs must be an object")
        return {}

    def load(stage: str) -> dict[str, Any]:
        reference = raw_outputs.get(stage)
        if not isinstance(reference, dict) or not _nonempty(reference.get("path")):
            errors.append(f"current_cycle.raw_outputs.{stage}.path is required")
            return {}
        return _load_json(
            repo_root / str(reference["path"]),
            errors,
            f"sealed {stage} raw output",
        )

    normal = manifest.get("normal_review")
    if isinstance(normal, dict) and normal.get("completed") is True:
        raw_normal = load("normal_review")
        for key in ("independent_candidates", "target_results", "relation_results"):
            if _canonical(raw_normal.get(key)) != _canonical(normal.get(key)):
                errors.append(
                    f"sealed normal_review {key} must exactly match the audit manifest"
                )

    finding_keys = (
        "id",
        "location",
        "severity",
        "description",
        "reason",
        "suggested_direction",
        "scope_anchors",
    )
    cold = manifest.get("cold_review")
    if isinstance(cold, dict) and cold.get("completed") is True:
        raw_cold = load("cold_review")
        if raw_cold.get("summary") != cold.get("summary"):
            errors.append("sealed cold_review summary must exactly match the audit manifest")
        if _canonical(_selected_list(raw_cold.get("findings"), finding_keys)) != _canonical(
            _selected_list(cold.get("findings"), finding_keys)
        ):
            errors.append(
                "sealed cold_review findings and scope anchors must exactly match the audit manifest"
            )

    if not final_phase:
        return {}

    final = manifest.get("final_review")
    if not isinstance(final, dict):
        return {}
    raw_blind = load("final_blind")
    candidate_keys = (
        "id",
        "surface_form",
        "frame",
        "meaning",
        "disposition",
        "rationale",
        "semantic_assertions",
    )
    if _canonical(_selected_list(raw_blind.get("independent_candidates"), candidate_keys)) != _canonical(
        _selected_list(final.get("independent_candidates"), candidate_keys)
    ):
        errors.append(
            "sealed final_blind candidates, dispositions, and semantic assertions must exactly match the audit manifest"
        )
    blind = final.get("blind_review")
    manifest_blind_findings = blind.get("article_findings") if isinstance(blind, dict) else None
    if _canonical(_selected_list(raw_blind.get("article_findings"), finding_keys)) != _canonical(
        _selected_list(manifest_blind_findings, finding_keys)
    ):
        errors.append(
            "sealed final_blind article findings must exactly match the audit manifest"
        )

    raw_final = load("final_review")
    adjudication = raw_final.get("adjudication")
    if not isinstance(adjudication, dict):
        errors.append("sealed final_review.adjudication must be an object")
        return raw_blind
    expected = {
        "decision": str(final.get("decision", "")).lower(),
        "inventory_comparison": final.get("inventory_comparison"),
        "target_results": final.get("target_results"),
        "relation_results": final.get("relation_results"),
        "candidate_results": final.get("candidate_results"),
        "blind_finding_results": final.get("blind_finding_results"),
        "finding_results": final.get("finding_results"),
        "evidence_checks": final.get("evidence_checks"),
        "final_inventory_checks": manifest.get("semantic_gate", {}).get(
            "final_inventory_checks"
        ),
        "blockers": final.get("blockers"),
    }
    actual = {key: adjudication.get(key) for key in expected}
    if _canonical(actual) != _canonical(expected):
        errors.append(
            "sealed final_review adjudication must exactly match every item-level manifest decision"
        )
    return raw_blind


def validate_manifest(
    manifest: dict[str, Any],
    audit_path: Path,
    *,
    repo_root: Path = REPO_ROOT,
    require_gate: bool = True,
    phase: str = "final",
) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != CANONICAL_AUDIT_SCHEMA:
        if require_gate:
            errors.append(
                f"semantic hard gate requires {CANONICAL_AUDIT_SCHEMA}; "
                f"found {manifest.get('schema_version')!r}"
            )
        return errors

    body_sha = manifest.get("body_sha256")
    if not _nonempty(body_sha):
        errors.append("audit body_sha256 is required")
        body_sha = ""
    entry_path: Path | None = None
    entry_body = ""
    invalidation: dict[str, Any] | None = None
    entry_path_value = manifest.get("entry_path")
    if _nonempty(entry_path_value):
        entry_path = repo_root / str(entry_path_value)
        if entry_path.exists():
            actual_body_sha = _body_sha256(entry_path)
            entry_body = _entry_body(entry_path)
            if actual_body_sha != body_sha:
                errors.append("audit body_sha256 does not match the current entry body")
            invalidation = _matching_invalidation(entry_path, str(body_sha), repo_root)
        elif require_gate:
            errors.append(f"entry_path does not exist: {entry_path_value}")

    gate = manifest.get("semantic_gate")
    if not isinstance(gate, dict):
        if invalidation is not None and entry_path is not None:
            front = _front_matter(entry_path)
            if front.get("status") != "needs_review" or front.get("checked") != "false":
                errors.append(
                    "an invalidated audit requires entry status needs_review and checked false"
                )
            return errors
        if require_gate:
            errors.append(
                "semantic_gate is required for changed v3 audits; read "
                "prompts/semantic_resolution_gate_v1.md"
            )
        elif entry_path is not None:
            front = _front_matter(entry_path)
            if front.get("status") in {"checked", "final"} or front.get("checked") == "true":
                errors.append(
                    "compatibility mode cannot keep a checked/final v3 audit without a semantic gate; invalidate it or run a fresh audit"
                )
        return errors

    if gate.get("version") != SEMANTIC_GATE_VERSION:
        errors.append(f"semantic_gate.version must be {SEMANTIC_GATE_VERSION}")

    if gate.get("body_sha256") != body_sha:
        errors.append("semantic_gate.body_sha256 must match the current audit body_sha256")

    targets = _index_by_id(manifest.get("targets"), "targets", errors)
    relations = _index_by_id(manifest.get("relations"), "relations", errors)
    target_ids = set(targets)
    relation_ids = set(relations)

    cold = manifest.get("cold_review")
    cold_findings = _index_by_id(
        cold.get("findings") if isinstance(cold, dict) else None,
        "cold_review.findings",
        errors,
    )
    cold_input_body = ""
    cold_input_hash = ""
    if isinstance(cold, dict) and isinstance(cold.get("execution"), dict):
        cold_input_hash = str(cold["execution"].get("input_body_sha256", ""))
    cycle = manifest.get("current_cycle")
    revisions = cycle.get("body_revisions") if isinstance(cycle, dict) else None
    if isinstance(revisions, list):
        for revision in revisions:
            if not isinstance(revision, dict) or revision.get("body_sha256") != cold_input_hash:
                continue
            snapshot_value = revision.get("snapshot_path")
            if _nonempty(snapshot_value):
                snapshot_path = repo_root / str(snapshot_value)
                try:
                    cold_input_body = snapshot_path.read_text(encoding="utf-8")
                except OSError as exc:
                    errors.append(f"cold-review input snapshot cannot be read: {exc}")
            break

    anchors_by_finding: dict[str, dict[str, dict[str, Any]]] = {}
    for finding_id, finding in cold_findings.items():
        anchors = _index_by_id(
            finding.get("scope_anchors"),
            f"cold finding {finding_id}.scope_anchors",
            errors,
        )
        anchors_by_finding[finding_id] = anchors
        if not anchors:
            errors.append(f"cold finding {finding_id} requires at least one scope anchor")
        for anchor_id, anchor in anchors.items():
            quote = anchor.get("exact_quote")
            if not _nonempty(quote):
                errors.append(
                    f"cold finding {finding_id} anchor {anchor_id}.exact_quote is required"
                )
            elif not cold_input_body:
                errors.append(
                    f"cold finding {finding_id} anchor {anchor_id} cannot be checked without its input revision"
                )
            elif str(quote) not in cold_input_body:
                errors.append(
                    f"cold finding {finding_id} anchor {anchor_id}.exact_quote is not present in the cold-review input revision"
                )

    constraints = _index_by_id(gate.get("constraints"), "semantic_gate.constraints", errors)
    constraints_by_source: dict[str, list[dict[str, Any]]] = {}
    for constraint_id, constraint in constraints.items():
        for key in ("source_type", "source_id", "statement", "scope", "verification_notes"):
            if not _nonempty(constraint.get(key)):
                errors.append(f"semantic constraint {constraint_id} requires non-empty {key}")
        if constraint.get("polarity") not in {"must_hold", "must_not_hold"}:
            errors.append(
                f"semantic constraint {constraint_id} polarity must be must_hold or must_not_hold"
            )
        affected_targets = _string_list(
            constraint.get("affected_target_ids"),
            f"semantic constraint {constraint_id}.affected_target_ids",
            errors,
        )
        affected_relations = _string_list(
            constraint.get("affected_relation_ids"),
            f"semantic constraint {constraint_id}.affected_relation_ids",
            errors,
        )
        article_queries = _string_list(
            constraint.get("article_queries"),
            f"semantic constraint {constraint_id}.article_queries",
            errors,
        )
        source_anchor_ids = _string_list(
            constraint.get("source_anchor_ids"),
            f"semantic constraint {constraint_id}.source_anchor_ids",
            errors,
        )
        if not (affected_targets or affected_relations or article_queries):
            errors.append(
                f"semantic constraint {constraint_id} must name at least one target, relation, or article query"
            )
        unknown_targets = sorted(set(affected_targets) - target_ids)
        unknown_relations = sorted(set(affected_relations) - relation_ids)
        if unknown_targets:
            errors.append(
                f"semantic constraint {constraint_id} references unknown targets: "
                + ", ".join(unknown_targets)
            )
        if unknown_relations:
            errors.append(
                f"semantic constraint {constraint_id} references unknown relations: "
                + ", ".join(unknown_relations)
            )
        if constraint.get("verified_on_body_sha256") != body_sha:
            errors.append(
                f"semantic constraint {constraint_id} is stale: verified_on_body_sha256 "
                "must match the current body"
            )
        source_id = constraint.get("source_id")
        if _nonempty(source_id):
            constraints_by_source.setdefault(str(source_id), []).append(constraint)
            known_anchors = set(anchors_by_finding.get(str(source_id), {}))
            unknown_anchors = sorted(set(source_anchor_ids) - known_anchors)
            if unknown_anchors:
                errors.append(
                    f"semantic constraint {constraint_id} references unknown source anchors: "
                    + ", ".join(unknown_anchors)
                )

    resolutions = _index_by_id(manifest.get("resolutions"), "resolutions", errors)
    confirmed_resolution_ids: set[str] = set()
    invariant_ids_by_resolution: dict[str, set[str]] = {}
    for resolution_id, resolution in resolutions.items():
        if resolution.get("problem_confirmed") is not True:
            continue
        if resolution.get("status") == "rejected":
            errors.append(
                f"resolution {resolution_id} cannot be rejected while problem_confirmed is true"
            )
            continue
        confirmed_resolution_ids.add(resolution_id)
        source_constraints = [
            item
            for item in constraints_by_source.get(resolution_id, [])
            if item.get("source_type") == "cold_finding"
        ]
        if not source_constraints:
            errors.append(
                f"confirmed resolution {resolution_id} requires at least one cold_finding semantic constraint"
            )
        expected_anchor_ids = set(anchors_by_finding.get(resolution_id, {}))
        constrained_anchor_ids: set[str] = set()
        for item in source_constraints:
            constrained_anchor_ids.update(
                str(value)
                for value in item.get("source_anchor_ids", [])
                if _nonempty(value)
            )
        if constrained_anchor_ids != expected_anchor_ids:
            errors.append(
                f"confirmed resolution {resolution_id} constraints must cover every cold-finding scope anchor exactly"
            )
        anchor_results = _index_by_id(
            resolution.get("scope_anchor_results"),
            f"resolution {resolution_id}.scope_anchor_results",
            errors,
        )
        if set(anchor_results) != expected_anchor_ids:
            errors.append(
                f"confirmed resolution {resolution_id} must resolve every cold-finding scope anchor exactly"
            )
        expected_ids = {str(item.get("id")) for item in source_constraints}
        recorded_ids = set(
            _string_list(
                resolution.get("semantic_invariant_ids"),
                f"resolution {resolution_id}.semantic_invariant_ids",
                errors,
            )
        )
        if recorded_ids != expected_ids:
            errors.append(
                f"resolution {resolution_id}.semantic_invariant_ids must exactly match its active constraints"
            )
        invariant_ids_by_resolution[resolution_id] = expected_ids
        if resolution.get("resolved_on_body_sha256") != body_sha:
            errors.append(
                f"resolution {resolution_id} is stale: resolved_on_body_sha256 must match the current body"
            )

    final_phase = _is_final_phase(manifest, phase)
    raw_blind = _validate_raw_stage_bindings(
        manifest,
        repo_root,
        errors,
        final_phase=final_phase,
    )
    if not final_phase:
        return errors

    final = manifest.get("final_review")
    if not isinstance(final, dict):
        errors.append("final_review must be an object")
        final = {}

    finding_results = _index_by_id(
        final.get("finding_results"), "final_review.finding_results", errors
    )
    for resolution_id in sorted(confirmed_resolution_ids):
        result = finding_results.get(resolution_id)
        if result is None:
            errors.append(
                f"final_review.finding_results is missing confirmed resolution {resolution_id}"
            )
            continue
        if result.get("verified_body_sha256") != body_sha:
            errors.append(
                f"final finding {resolution_id} is stale: verified_body_sha256 must match the current body"
            )
        verified_ids = set(
            _string_list(
                result.get("verified_invariant_ids"),
                f"final finding {resolution_id}.verified_invariant_ids",
                errors,
            )
        )
        if verified_ids != invariant_ids_by_resolution.get(resolution_id, set()):
            errors.append(
                f"final finding {resolution_id}.verified_invariant_ids must exactly match the resolution invariants"
            )
        blast_targets = set(
            _string_list(
                result.get("blast_radius_target_ids"),
                f"final finding {resolution_id}.blast_radius_target_ids",
                errors,
            )
        )
        blast_relations = set(
            _string_list(
                result.get("blast_radius_relation_ids"),
                f"final finding {resolution_id}.blast_radius_relation_ids",
                errors,
            )
        )
        blast_queries = set(
            _string_list(
                result.get("blast_radius_queries_checked"),
                f"final finding {resolution_id}.blast_radius_queries_checked",
                errors,
            )
        )
        required_targets = set(
            str(value)
            for value in resolution.get("affected_target_ids", [])
            if _nonempty(value)
        )
        required_relations = set(
            str(value)
            for value in resolution.get("affected_relation_ids", [])
            if _nonempty(value)
        )
        required_queries: set[str] = set()
        anchor_results = _index_by_id(
            resolution.get("scope_anchor_results"),
            f"resolution {resolution_id}.scope_anchor_results",
            errors,
        )
        for anchor_result in anchor_results.values():
            required_targets.update(
                str(value)
                for value in anchor_result.get("affected_target_ids", [])
                if _nonempty(value)
            )
            required_queries.update(
                str(value)
                for value in anchor_result.get("article_queries", [])
                if _nonempty(value)
            )
        for constraint in constraints_by_source.get(resolution_id, []):
            required_targets.update(
                str(value)
                for value in constraint.get("affected_target_ids", [])
                if _nonempty(value)
            )
            required_relations.update(
                str(value)
                for value in constraint.get("affected_relation_ids", [])
                if _nonempty(value)
            )
            required_queries.update(
                str(value)
                for value in constraint.get("article_queries", [])
                if _nonempty(value)
            )
        required_relations.update(
            relation_id
            for relation_id, relation in relations.items()
            if required_targets
            & {
                str(value)
                for value in relation.get("target_ids", [])
                if _nonempty(value)
            }
        )
        if not required_targets.issubset(blast_targets):
            errors.append(
                f"final finding {resolution_id} blast radius omits targets: "
                + ", ".join(sorted(required_targets - blast_targets))
            )
        if not required_relations.issubset(blast_relations):
            errors.append(
                f"final finding {resolution_id} blast radius omits relations: "
                + ", ".join(sorted(required_relations - blast_relations))
            )
        if not required_queries.issubset(blast_queries):
            errors.append(
                f"final finding {resolution_id} blast radius omits article queries: "
                + ", ".join(sorted(required_queries - blast_queries))
            )
        query_results = _query_result_index(
            result.get("blast_radius_query_results"),
            f"final finding {resolution_id}.blast_radius_query_results",
            errors,
        )
        if set(query_results) != required_queries or blast_queries != required_queries:
            errors.append(
                f"final finding {resolution_id} must record exact query results for every required article query"
            )
        for query, query_result in query_results.items():
            actual_targets = sorted(
                target_id
                for target_id, target in targets.items()
                if query in str(target.get("text", ""))
            )
            if query_result.get("match_count") != entry_body.count(query):
                errors.append(
                    f"final finding {resolution_id} query {query!r} has an incorrect match_count"
                )
            if query_result.get("matched_target_ids") != actual_targets:
                errors.append(
                    f"final finding {resolution_id} query {query!r} has incorrect matched_target_ids"
                )

    final_candidates = _index_by_id(
        final.get("independent_candidates"),
        "final_review.independent_candidates",
        errors,
    )
    assertions_by_candidate: dict[str, list[dict[str, str]]] = {}
    for candidate_id, candidate in final_candidates.items():
        assertions_by_candidate[candidate_id] = _semantic_assertions(
            candidate, f"final candidate {candidate_id}", errors
        )

    raw_candidate_index = _index_by_id(
        raw_blind.get("independent_candidates"),
        "sealed final_blind independent_candidates",
        errors,
    )
    if set(raw_candidate_index) != set(final_candidates):
        errors.append(
            "sealed final_blind candidates must exactly match final_review.independent_candidates"
        )
    for candidate_id, candidate in final_candidates.items():
        raw_candidate = raw_candidate_index.get(candidate_id)
        if raw_candidate is None:
            continue
        if _normalize_assertions(raw_candidate) != _normalize_assertions(candidate):
            errors.append(
                f"final candidate {candidate_id} semantic_assertions were not fixed in the sealed final_blind raw output"
            )

    inventory_checks_raw = gate.get("final_inventory_checks")
    if not isinstance(inventory_checks_raw, list):
        errors.append("semantic_gate.final_inventory_checks must be a list")
        inventory_checks_raw = []
    inventory_checks: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(inventory_checks_raw):
        if not isinstance(item, dict):
            errors.append(f"semantic_gate.final_inventory_checks[{index}] must be an object")
            continue
        candidate_id = item.get("candidate_id")
        if not _nonempty(candidate_id):
            errors.append(
                f"semantic_gate.final_inventory_checks[{index}].candidate_id is required"
            )
            continue
        if candidate_id in inventory_checks:
            errors.append(
                f"semantic_gate.final_inventory_checks contains duplicate candidate_id {candidate_id}"
            )
            continue
        inventory_checks[str(candidate_id)] = item
    if set(inventory_checks) != set(final_candidates):
        missing = sorted(set(final_candidates) - set(inventory_checks))
        extra = sorted(set(inventory_checks) - set(final_candidates))
        if missing:
            errors.append("semantic gate is missing final inventory checks: " + ", ".join(missing))
        if extra:
            errors.append("semantic gate contains unknown final inventory checks: " + ", ".join(extra))

    final_decision = str(final.get("decision", "")).lower()
    for candidate_id, check in inventory_checks.items():
        assertion_ids = set(
            _string_list(
                check.get("assertion_ids"),
                f"inventory check {candidate_id}.assertion_ids",
                errors,
            )
        )
        expected_assertion_ids = {
            item["id"] for item in assertions_by_candidate.get(candidate_id, [])
        }
        if assertion_ids != expected_assertion_ids:
            errors.append(
                f"inventory check {candidate_id}.assertion_ids must exactly match the blind assertions"
            )
        if check.get("checked_on_body_sha256") != body_sha:
            errors.append(
                f"inventory check {candidate_id} is stale: checked_on_body_sha256 must match the current body"
            )
        status = check.get("status")
        if status not in {"pass", "fail"}:
            errors.append(f"inventory check {candidate_id}.status must be pass or fail")
        if final_decision == "pass" and status != "pass":
            errors.append(
                f"final decision pass requires inventory check {candidate_id} to pass"
            )
        if not _nonempty(check.get("notes")):
            errors.append(f"inventory check {candidate_id}.notes is required")
        checked_targets = _string_list(
            check.get("article_target_ids_checked"),
            f"inventory check {candidate_id}.article_target_ids_checked",
            errors,
        )
        checked_relations = _string_list(
            check.get("article_relation_ids_checked"),
            f"inventory check {candidate_id}.article_relation_ids_checked",
            errors,
        )
        checked_queries = _string_list(
            check.get("article_queries_checked"),
            f"inventory check {candidate_id}.article_queries_checked",
            errors,
        )
        query_results = _query_result_index(
            check.get("article_query_results"),
            f"inventory check {candidate_id}.article_query_results",
            errors,
        )
        if set(query_results) != set(checked_queries):
            errors.append(
                f"inventory check {candidate_id} must record exact results for every checked article query"
            )
        for query, query_result in query_results.items():
            actual_targets = sorted(
                target_id
                for target_id, target in targets.items()
                if query in str(target.get("text", ""))
            )
            if query_result.get("match_count") != entry_body.count(query):
                errors.append(
                    f"inventory check {candidate_id} query {query!r} has an incorrect match_count"
                )
            if query_result.get("matched_target_ids") != actual_targets:
                errors.append(
                    f"inventory check {candidate_id} query {query!r} has incorrect matched_target_ids"
                )
        unknown_targets = sorted(set(checked_targets) - target_ids)
        unknown_relations = sorted(set(checked_relations) - relation_ids)
        if unknown_targets:
            errors.append(
                f"inventory check {candidate_id} references unknown targets: "
                + ", ".join(unknown_targets)
            )
        if unknown_relations:
            errors.append(
                f"inventory check {candidate_id} references unknown relations: "
                + ", ".join(unknown_relations)
            )
        candidate = final_candidates.get(candidate_id, {})
        mapped_targets = {
            str(value)
            for value in candidate.get("article_target_ids", [])
            if _nonempty(value)
        }
        if candidate.get("disposition") == "included" and not mapped_targets.issubset(
            set(checked_targets)
        ):
            errors.append(
                f"inventory check {candidate_id} does not recheck all mapped article targets"
            )
        incident_relations = {
            relation_id
            for relation_id, relation in relations.items()
            if mapped_targets
            & {
                str(value)
                for value in relation.get("target_ids", [])
                if _nonempty(value)
            }
        }
        if candidate.get("disposition") == "included" and not incident_relations.issubset(
            set(checked_relations)
        ):
            errors.append(
                f"inventory check {candidate_id} does not recheck all relations incident to mapped targets"
            )
        if not (checked_targets or checked_relations or checked_queries):
            errors.append(
                f"inventory check {candidate_id} must inspect at least one target, relation, or explicit article query"
            )

    return errors


def validate_audit_path(
    audit_path: Path,
    *,
    repo_root: Path = REPO_ROOT,
    require_gate: bool = True,
    phase: str = "final",
) -> list[str]:
    errors: list[str] = []
    manifest = _load_json(audit_path, errors, str(audit_path))
    if manifest:
        errors.extend(
            validate_manifest(
                manifest,
                audit_path,
                repo_root=repo_root,
                require_gate=require_gate,
                phase=phase,
            )
        )
    return errors


def _canonical_audit_paths(repo_root: Path = REPO_ROOT) -> list[Path]:
    paths: list[Path] = []
    for path in sorted((repo_root / "audits").rglob("*.json")):
        relative = path.relative_to(repo_root / "audits")
        if any(part in {"runs", "history"} for part in relative.parts):
            continue
        if path.name in {"escaped_defect_taxonomy.json", "review_invalidations.json"}:
            continue
        paths.append(path)
    return paths


def _changed_files(base: str, head: str, repo_root: Path = REPO_ROOT) -> list[str]:
    completed = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=AM",
            base,
            head,
            "--",
            "entries",
            "audits",
        ],
        cwd=repo_root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _validate_many(
    paths: list[Path], *, require_gate: bool, phase: str = "final"
) -> int:
    failed = False
    if not paths:
        print("No semantic-resolution audits to validate.")
        return 0
    for path in paths:
        errors = validate_audit_path(
            path,
            require_gate=require_gate,
            phase=phase,
        )
        if errors:
            failed = True
            print(f"FAIL {path.relative_to(REPO_ROOT)}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        else:
            print(f"PASS {path.relative_to(REPO_ROOT)}")
    return 1 if failed else 0


def command_validate_changed(args: argparse.Namespace) -> int:
    audit_paths: set[Path] = set()
    for raw_path in _changed_files(args.base, args.head):
        path = REPO_ROOT / raw_path
        if raw_path.startswith("entries/") and raw_path.endswith(".md"):
            audit_paths.add(_audit_path_for_entry(path))
            continue
        if raw_path.startswith("audits/") and raw_path.endswith(".json"):
            relative = Path(raw_path).relative_to("audits")
            if any(part in {"runs", "history"} for part in relative.parts):
                continue
            if Path(raw_path).name in {
                "escaped_defect_taxonomy.json",
                "review_invalidations.json",
            }:
                continue
            audit_paths.add(path)
    missing = [path for path in sorted(audit_paths) if not path.exists()]
    if missing:
        for path in missing:
            print(
                f"FAIL {path.relative_to(REPO_ROOT)}\n  - changed entry requires a canonical audit manifest",
                file=sys.stderr,
            )
        return 1
    return _validate_many(sorted(audit_paths), require_gate=True, phase="final")


def command_validate_entries(args: argparse.Namespace) -> int:
    paths: list[Path] = []
    missing = False
    for value in args.entries:
        entry_path = (REPO_ROOT / value).resolve()
        try:
            audit_path = _audit_path_for_entry(entry_path)
        except ValueError as exc:
            print(f"FAIL {value}\n  - {exc}", file=sys.stderr)
            missing = True
            continue
        if not audit_path.exists():
            print(
                f"FAIL {audit_path.relative_to(REPO_ROOT)}\n  - audit manifest does not exist",
                file=sys.stderr,
            )
            missing = True
            continue
        paths.append(audit_path)
    result = _validate_many(
        paths,
        require_gate=not args.compat,
        phase="auto",
    )
    return 1 if missing or result else 0


def command_validate_audited(args: argparse.Namespace) -> int:
    return _validate_many(
        _canonical_audit_paths(),
        require_gate=not args.compat,
        phase="final",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate semantic finding-resolution and blind-inventory hard gates."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    changed = subparsers.add_parser("validate-changed")
    changed.add_argument("--base", required=True)
    changed.add_argument("--head", required=True)
    changed.set_defaults(func=command_validate_changed)

    entries = subparsers.add_parser("validate-entries")
    entries.add_argument("entries", nargs="+")
    entries.add_argument(
        "--compat",
        action="store_true",
        help="Allow pre-gate existing audits while validating any gate that is present.",
    )
    entries.set_defaults(func=command_validate_entries)

    audited = subparsers.add_parser("validate-audited")
    audited.add_argument(
        "--compat",
        action="store_true",
        help="Allow pre-gate existing audits while validating any gate that is present.",
    )
    audited.set_defaults(func=command_validate_audited)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
