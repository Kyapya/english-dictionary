from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import review_liveness


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "content_audit_v4"
GENERATOR_VERSION = "generate_audit_manifest_v1"
BLIND_SEAL_VERSION = "blind_seal_v3"
RAW_FILENAMES = {
    "source_inventory": "source_inventory.json",
    "normal_review": "pass_findings.json",
    "cold_review": "cold_review.json",
    "resolutions": "resolutions.json",
    "final_blind": "final_blind.json",
    "blind_seal": "blind_seal.json",
    "final_review": "final_review.json",
}
CONTENT_TAXONOMY = {
    "example_translation_alignment",
    "semantic_direction_reversal",
    "sense_boundary_overlap",
    "cross_section_internal_contradiction",
    "compound_component_generalization",
    "argument_slot_role_mismatch",
    "lexical_relation_mislabel",
    "regional_qualification",
    "absolute_scope_counterexample",
    "technical_terminology_conventionality",
    "pronunciation_symbol_explanation",
    "evidence_claim_mismatch",
}
REVIEW_CONTRACT_START = "20260827"


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"raw output must be a JSON object: {path}")
    return value


def _entry_body(entry_path: Path) -> str:
    text = entry_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[index + 1 :])
    return text


def _entry_front_matter(entry_path: Path) -> dict[str, str]:
    text = entry_path.read_text(encoding="utf-8")
    values: dict[str, str] = {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return values
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"')
    return values


def _validate_api_raw_provenance(
    reviewers: list[tuple[str, Any]], cycle_dir: Path
) -> None:
    raw_ids: set[str] = set()
    raw_dir = cycle_dir / "raw"
    for path in raw_dir.glob("*.response.json") if raw_dir.is_dir() else []:
        value = _read_json(path)
        response_id = str(value.get("id") or value.get("request_id") or "").strip()
        if response_id:
            raw_ids.add(response_id)
    for label, reviewer in reviewers:
        if not isinstance(reviewer, dict) or reviewer.get("mode") != "api":
            continue
        response_id = str(reviewer.get("response_id", ""))
        if response_id not in raw_ids:
            raise ValueError(
                f"{label}: reviewer.response_id has no preserved raw API response"
            )


def _registered_run_invalidation(cycle_dir: Path, repo_root: Path) -> bool:
    path = repo_root / "audits" / "review_invalidations.json"
    if not path.is_file():
        return False
    try:
        value = _read_json(path)
    except (OSError, json.JSONDecodeError, ValueError):
        return False
    return any(
        isinstance(item, dict)
        and item.get("status") == "invalidated_run"
        and item.get("run_id") == cycle_dir.name
        for item in value.get("invalidations", [])
    )


def _is_historical_cycle(cycle_dir: Path) -> bool:
    prefix = cycle_dir.name[:8]
    return len(prefix) == 8 and prefix.isdigit() and prefix < REVIEW_CONTRACT_START


def body_sha256(entry_path: Path) -> str:
    return _sha_bytes(_entry_body(entry_path).encode("utf-8"))


def _relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"artifact must be under repository: {path}") from exc


def _index(items: Any, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        raise ValueError(f"{label} must be a list")
    result: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not str(item.get("id", "")).strip():
            raise ValueError(f"{label}[{index}] requires a non-empty id")
        item_id = str(item["id"])
        if item_id in result:
            raise ValueError(f"{label} contains duplicate id: {item_id}")
        result[item_id] = item
    return result


def _result_ids(items: Any, label: str) -> tuple[set[str], list[dict[str, Any]]]:
    indexed = _index(items, label)
    for item_id, item in indexed.items():
        if item.get("status") not in {"pass", "fail"}:
            raise ValueError(f"{label} {item_id}.status must be pass or fail")
        if not str(item.get("notes", "")).strip():
            raise ValueError(f"{label} {item_id}.notes is required")
    return set(indexed), list(indexed.values())


def _require_exact_results(
    expected: set[str], items: Any, label: str, *, passing: bool
) -> list[dict[str, Any]]:
    actual, normalized = _result_ids(items, label)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"{label} id mismatch; missing={missing}, extra={extra}")
    if passing and any(item["status"] != "pass" for item in normalized):
        raise ValueError(f"pass decision requires every {label} result to pass")
    return normalized


def _validate_metadata(
    raw: dict[str, Any], stage: str, body_hash: str, expected_artifacts: set[str]
) -> None:
    if raw.get("stage") != stage:
        raise ValueError(f"{stage}: raw stage field must be {stage}")
    for key in ("run_id", "context_id", "prompt_sha256", "recorded_at"):
        if not str(raw.get(key, "")).strip():
            raise ValueError(f"{stage}.{key} is required")
    if raw.get("input_body_sha256") != body_hash:
        raise ValueError(f"{stage}.input_body_sha256 is stale")
    artifacts = raw.get("input_artifacts")
    if not isinstance(artifacts, list) or set(artifacts) != expected_artifacts:
        raise ValueError(
            f"{stage}.input_artifacts must be exactly {sorted(expected_artifacts)}"
        )
    try:
        datetime.fromisoformat(str(raw["recorded_at"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{stage}.recorded_at must be ISO-8601") from exc


def _timestamp(value: Any, label: str) -> datetime:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be ISO-8601") from exc


def _validate_finding(item: dict[str, Any], label: str) -> None:
    taxonomy = item.get("taxonomy_id")
    if taxonomy not in CONTENT_TAXONOMY:
        raise ValueError(f"{label}.taxonomy_id is not a content category: {taxonomy}")
    if item.get("severity") not in {"blocking", "minor"}:
        raise ValueError(f"{label}.severity must be blocking or minor")
    if not str(item.get("rationale", "")).strip():
        raise ValueError(f"{label}.rationale is required")
    location = item.get("location")
    if not isinstance(location, dict):
        raise ValueError(f"{label}.location must be an object")
    for key in ("section", "line_start", "line_end", "exact_quote"):
        if location.get(key) in (None, ""):
            raise ValueError(f"{label}.location.{key} is required")


def _validate_cold_finding(item: dict[str, Any], label: str) -> None:
    """Validate the native context-free cold-review output contract.

    Cold review deliberately uses open-ended problem discovery with quote-anchored
    scope, not the checker/final-blind taxonomy contract.  Keeping the two raw
    schemas distinct prevents the manifest generator from silently rewriting a
    cold reviewer finding during handoff.
    """
    if item.get("severity") not in {"high", "medium", "low"}:
        raise ValueError(f"{label}.severity must be high, medium, or low")
    for key in ("location", "description", "reason", "suggested_direction"):
        if not str(item.get(key, "")).strip():
            raise ValueError(f"{label}.{key} is required")
    anchors = _index(item.get("scope_anchors"), f"{label}.scope_anchors")
    if not anchors:
        raise ValueError(f"{label}.scope_anchors must not be empty")
    for anchor_id, anchor in anchors.items():
        for key in ("exact_quote", "location_hint"):
            if not str(anchor.get(key, "")).strip():
                raise ValueError(
                    f"{label}.scope_anchors.{anchor_id}.{key} is required"
                )


def blind_payload(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": raw.get("schema_version"),
        "stage": raw.get("stage"),
        "run_id": raw.get("run_id"),
        "context_id": raw.get("context_id"),
        "input_body_sha256": raw.get("input_body_sha256"),
        "prompt_sha256": raw.get("prompt_sha256"),
        "recorded_at": raw.get("recorded_at"),
        "provisional_decision": raw.get("provisional_decision"),
        "independent_candidates": raw.get("independent_candidates"),
        "article_findings": raw.get("article_findings"),
    }


def seal_blind(
    entry_path: Path,
    final_blind_path: Path,
    output_path: Path,
    *,
    repo_root: Path = REPO_ROOT,
    sealed_at: str | None = None,
) -> dict[str, Any]:
    raw = _read_json(final_blind_path)
    current_hash = body_sha256(entry_path)
    _validate_metadata(
        raw,
        "final_blind",
        current_hash,
        {"entry_body", "final_blind_prompt"},
    )
    if raw.get("audit_visible") is not False:
        raise ValueError("final_blind.audit_visible must be false")
    if raw.get("provisional_decision") not in {"pass", "reject"}:
        raise ValueError("final_blind.provisional_decision must be pass or reject")
    candidates = _index(raw.get("independent_candidates"), "independent_candidates")
    if not candidates:
        raise ValueError("final_blind requires an independent inventory")
    for candidate_id, candidate in candidates.items():
        if candidate.get("disposition") not in {"included", "excluded"}:
            raise ValueError(f"candidate {candidate_id}.disposition is invalid")
        assertions = _index(
            candidate.get("semantic_assertions"),
            f"candidate {candidate_id}.semantic_assertions",
        )
        if not assertions:
            raise ValueError(f"candidate {candidate_id} requires semantic assertions")
        for assertion_id, assertion in assertions.items():
            if assertion.get("polarity") not in {"must_hold", "must_not_hold"}:
                raise ValueError(f"assertion {assertion_id}.polarity is invalid")
            for key in ("statement", "scope"):
                if not str(assertion.get(key, "")).strip():
                    raise ValueError(f"assertion {assertion_id}.{key} is required")
        for forbidden in ("article_target_ids", "evidence_link_ids", "resolution_ids"):
            if candidate.get(forbidden) not in (None, []):
                raise ValueError(f"final blind candidate must not contain {forbidden}")
    blind_findings = _index(raw.get("article_findings"), "article_findings")
    for finding_id, finding in blind_findings.items():
        _validate_finding(finding, f"article_findings.{finding_id}")
    payload = {
        "schema_version": BLIND_SEAL_VERSION,
        "stage": "blind_seal",
        "entry_path": _relative(entry_path, repo_root),
        "body_sha256": current_hash,
        "final_blind_path": _relative(final_blind_path, repo_root),
        "final_blind_sha256": _sha_bytes(final_blind_path.read_bytes()),
        "blind_output_sha256": _sha_bytes(_canonical(blind_payload(raw))),
        "sealed_at": sealed_at
        or datetime.now().astimezone().isoformat(timespec="microseconds"),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return payload


def _raw_provenance(path: Path, raw: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    value = {
        "path": _relative(path, repo_root),
        "sha256": _sha_bytes(path.read_bytes()),
        "stage": raw.get("stage"),
    }
    for key in (
        "run_id",
        "context_id",
        "input_body_sha256",
        "prompt_sha256",
        "recorded_at",
    ):
        if key in raw:
            value[key] = raw[key]
    return value


def generate_manifest(
    entry_path: Path, cycle_dir: Path, *, repo_root: Path = REPO_ROOT
) -> dict[str, Any]:
    current_hash = body_sha256(entry_path)
    paths = {stage: cycle_dir / filename for stage, filename in RAW_FILENAMES.items()}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise ValueError("required raw outputs are missing: " + ", ".join(missing))
    raw = {stage: _read_json(path) for stage, path in paths.items()}
    generation_model = _entry_front_matter(entry_path).get("model")
    raw_pass_outputs = raw["normal_review"].get("pass_outputs", [])
    has_reviewer_provenance = any(
        isinstance(raw[stage].get("reviewer"), dict)
        for stage in ("cold_review", "final_blind", "final_review")
    ) or any(
        isinstance(item, dict) and isinstance(item.get("reviewer"), dict)
        for item in raw_pass_outputs
        if isinstance(raw_pass_outputs, list)
    )
    provenance_contract = not _is_historical_cycle(cycle_dir) or has_reviewer_provenance
    liveness_contract = provenance_contract or _registered_run_invalidation(
        cycle_dir, repo_root
    )

    for stage in ("cold_review", "final_blind", "final_review") if provenance_contract else ():
        reviewer = raw[stage].get("reviewer")
        reviewer_errors = review_liveness.validate_reviewer(
            reviewer, generation_model=generation_model
        )
        request_path = cycle_dir / f"{stage}.request.json"
        request_payload = _read_json(request_path) if request_path.is_file() else None
        reviewer_errors.extend(
            review_liveness.validate_api_request_binding(reviewer, request_payload)
        )
        if reviewer_errors:
            raise ValueError(f"{stage}: " + "; ".join(reviewer_errors))

    expected_inputs = {
        "source_inventory": {"headword", "source_first_spec"},
        "normal_review": {"router_selected_sections", "checker_pass_specs"},
        "cold_review": {"entry_body", "cold_review_prompt"},
        "resolutions": {"entry_body", "all_findings"},
        "final_blind": {"entry_body", "final_blind_prompt"},
        "final_review": {
            "entry_body",
            "all_findings",
            "resolutions",
            "sealed_final_blind",
            "final_review_spec",
        },
    }
    for stage, artifacts in expected_inputs.items():
        _validate_metadata(raw[stage], stage, current_hash, artifacts)
    if raw["cold_review"].get("audit_visible") is not False:
        raise ValueError("cold_review.audit_visible must be false")
    if raw["final_blind"].get("audit_visible") is not False:
        raise ValueError("final_blind.audit_visible must be false")

    # Three roles remain separate; reconciliation continues the sealed final run.
    normal_identity = (
        raw["normal_review"]["run_id"],
        raw["normal_review"]["context_id"],
    )
    cold_identity = (
        raw["cold_review"]["run_id"],
        raw["cold_review"]["context_id"],
    )
    blind_identity = (
        raw["final_blind"]["run_id"],
        raw["final_blind"]["context_id"],
    )
    if len({normal_identity, cold_identity, blind_identity}) != 3:
        raise ValueError("normal, cold, and final run/context identities must be distinct")
    review_identity = (
        raw["final_review"]["run_id"],
        raw["final_review"]["context_id"],
    )
    if review_identity != blind_identity:
        raise ValueError("final reconciliation must continue the sealed final run/context")

    # Validate every routed pass before flattening its findings.
    import check_passes

    router = check_passes.load_router(repo_root / "prompts" / "check_router_v6.md")
    outputs = raw["normal_review"].get("pass_outputs")
    if not isinstance(outputs, list):
        raise ValueError("normal_review.pass_outputs must be a list")
    expected_passes = {item["id"] for item in router["passes"]}
    actual_passes: set[str] = set()
    findings: list[dict[str, Any]] = []
    attribution_request_path = cycle_dir / "check_passes" / "example-attribution.request.json"
    attribution_alignment_path = (
        cycle_dir / "check_passes" / "example-attribution.alignment-key.json"
    )
    attribution_request = (
        _read_json(attribution_request_path)
        if attribution_request_path.is_file()
        else None
    )
    attribution_alignment = (
        _read_json(attribution_alignment_path)
        if attribution_alignment_path.is_file()
        else None
    )
    antonym_request_path = cycle_dir / "check_passes" / "frame-relation.request.json"
    antonym_stage2_path = (
        cycle_dir
        / "check_passes"
        / "frame-relation.antonym-axis.stage2.request.json"
    )
    antonym_alignment_path = (
        cycle_dir
        / "check_passes"
        / "frame-relation.antonym-axis.alignment-key.json"
    )
    antonym_request = (
        _read_json(antonym_request_path) if antonym_request_path.is_file() else None
    )
    antonym_stage2_request = (
        _read_json(antonym_stage2_path) if antonym_stage2_path.is_file() else None
    )
    antonym_alignment = (
        _read_json(antonym_alignment_path)
        if antonym_alignment_path.is_file()
        else None
    )
    if (
        _is_historical_cycle(cycle_dir)
        and attribution_request is None
        and any(
            isinstance(item, dict) and item.get("pass_id") == "example-attribution"
            for item in outputs
        )
    ):
        attribution_request, attribution_alignment = (
            check_passes.build_legacy_example_attribution_artifacts(
                entry_path, router
            )
        )
    for output in outputs:
        if not isinstance(output, dict):
            raise ValueError("normal_review.pass_outputs contains a non-object")
        pass_id = str(output.get("pass_id", ""))
        if pass_id in actual_passes:
            raise ValueError(f"normal_review has duplicate pass output: {pass_id}")
        actual_passes.add(pass_id)
        request_path = cycle_dir / "check_passes" / f"{pass_id}.request.json"
        request_payload = _read_json(request_path) if request_path.is_file() else None
        if pass_id == "frame-relation" and antonym_stage2_request is not None:
            request_payload = antonym_stage2_request
        errors = check_passes.validate_pass_output(
            output,
            router,
            entry_path=entry_path,
            repo_root=repo_root,
            example_request=attribution_request,
            antonym_request=antonym_request,
            antonym_stage2_request=antonym_stage2_request,
            antonym_alignment_key=antonym_alignment,
            request_payload=request_payload,
            alignment_key=attribution_alignment,
            check_liveness=False,
            generation_model=generation_model,
            require_reviewer=provenance_contract,
            require_antonym_axis=(
                "antonym_axis_blind_record" in output
                or antonym_request is not None
                or antonym_stage2_request is not None
                or antonym_alignment is not None
            ),
        )
        if errors:
            raise ValueError(f"pass output {pass_id}: " + "; ".join(errors))
        for item in output["findings"]:
            findings.append({**item, "origin": f"check_pass:{pass_id}"})
    if actual_passes != expected_passes and not _is_historical_cycle(cycle_dir):
        raise ValueError(
            f"normal_review pass set mismatch; expected={sorted(expected_passes)}, "
            f"actual={sorted(actual_passes)}"
        )

    for stage, key, origin in (
        ("cold_review", "findings", "cold_review"),
        ("final_blind", "article_findings", "final_blind"),
    ):
        indexed = _index(raw[stage].get(key), f"{stage}.{key}")
        for finding_id, item in indexed.items():
            if stage == "cold_review":
                _validate_cold_finding(item, f"{stage}.{key}.{finding_id}")
            else:
                _validate_finding(item, f"{stage}.{key}.{finding_id}")
            findings.append({**item, "origin": origin})
    finding_index = _index(findings, "all findings")

    resolutions = _index(raw["resolutions"].get("resolutions"), "resolutions")
    if set(resolutions) != set(finding_index):
        raise ValueError("resolutions must cover every finding exactly once")
    for resolution_id, resolution in resolutions.items():
        if resolution.get("finding_id") != resolution_id:
            raise ValueError(f"resolution {resolution_id}.finding_id must equal its id")
        if resolution.get("status") != "resolved":
            raise ValueError(f"resolution {resolution_id}.status must be resolved")
        if resolution.get("disposition") not in {"adopted", "rejected"}:
            raise ValueError(f"resolution {resolution_id}.disposition is invalid")
        if resolution.get("resolved_body_sha256") != current_hash:
            raise ValueError(f"resolution {resolution_id} is stale")
        if not str(resolution.get("rationale", "")).strip():
            raise ValueError(f"resolution {resolution_id}.rationale is required")

    seal = raw["blind_seal"]
    if seal.get("schema_version") != BLIND_SEAL_VERSION:
        raise ValueError(f"blind seal must use {BLIND_SEAL_VERSION}")
    if seal.get("body_sha256") != current_hash:
        raise ValueError("blind seal body hash is stale")
    if seal.get("final_blind_path") != _relative(paths["final_blind"], repo_root):
        raise ValueError("blind seal points to a different final_blind output")
    if seal.get("final_blind_sha256") != _sha_bytes(paths["final_blind"].read_bytes()):
        raise ValueError("blind seal final_blind raw hash is stale")
    blind_hash = _sha_bytes(_canonical(blind_payload(raw["final_blind"])))
    if seal.get("blind_output_sha256") != blind_hash:
        raise ValueError("blind seal output hash does not match final_blind content")
    if raw["final_review"].get("blind_output_sha256") != blind_hash:
        raise ValueError("final_review does not reconcile the sealed blind output")
    blind_time = _timestamp(raw["final_blind"]["recorded_at"], "final_blind.recorded_at")
    seal_time = _timestamp(seal.get("sealed_at"), "blind_seal.sealed_at")
    review_time = _timestamp(
        raw["final_review"]["recorded_at"], "final_review.recorded_at"
    )
    if seal_time < blind_time:
        raise ValueError("blind seal cannot precede final_blind recording")
    if review_time < seal_time:
        raise ValueError("final reconciliation cannot precede blind sealing")

    import content_audit

    extracted_targets = content_audit.extract_targets(entry_path)
    extracted_relations = content_audit.extract_relations(extracted_targets)
    target_ids = {item["id"] for item in extracted_targets}
    relation_ids = {item["id"] for item in extracted_relations}
    normal_candidates = set(
        _index(raw["normal_review"].get("independent_candidates"), "normal candidates")
    )
    blind_candidates = set(
        _index(raw["final_blind"].get("independent_candidates"), "blind candidates")
    )
    evidence_ids = set(
        str(value)
        for value in raw["source_inventory"].get("evidence_link_ids", [])
        if str(value).strip()
    )
    source_gate = raw["source_inventory"].get("source_first_audit")
    if not isinstance(source_gate, dict):
        raise ValueError("source_inventory.source_first_audit must be an object")
    source_union_ids = {
        str(item["id"])
        for item in source_gate.get("source_union", [])
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }

    decision = raw["final_review"].get("decision")
    if decision not in {"pass", "reject"}:
        raise ValueError("final_review.decision must be pass or reject")
    passing = decision == "pass"
    _require_exact_results(
        target_ids, raw["final_review"].get("target_results"), "target_results", passing=passing
    )
    _require_exact_results(
        relation_ids,
        raw["final_review"].get("relation_results"),
        "relation_results",
        passing=passing,
    )
    _require_exact_results(
        normal_candidates,
        raw["final_review"].get("normal_candidate_results"),
        "normal_candidate_results",
        passing=passing,
    )
    blind_results = _require_exact_results(
        blind_candidates,
        raw["final_review"].get("blind_candidate_results"),
        "blind_candidate_results",
        passing=passing,
    )
    blind_candidate_map = _index(
        raw["final_blind"].get("independent_candidates"), "blind candidates"
    )
    for result in blind_results:
        expected_assertions = set(
            _index(
                blind_candidate_map[result["id"]].get("semantic_assertions"),
                f"blind candidate {result['id']} assertions",
            )
        )
        actual_assertions = set(result.get("assertion_ids", []))
        if actual_assertions != expected_assertions:
            raise ValueError(
                f"blind_candidate_results {result['id']} must recheck every sealed assertion"
            )
        if result.get("verified_body_sha256") != current_hash:
            raise ValueError(f"blind candidate result {result['id']} is stale")
    _require_exact_results(
        set(finding_index),
        raw["final_review"].get("finding_results"),
        "finding_results",
        passing=passing,
    )
    _require_exact_results(
        evidence_ids,
        raw["final_review"].get("evidence_checks"),
        "evidence_checks",
        passing=passing,
    )
    source_results = _require_exact_results(
        source_union_ids,
        raw["final_review"].get("source_inventory_results"),
        "source_inventory_results",
        passing=passing,
    )
    for result in source_results:
        if result.get("union_id") != result["id"]:
            raise ValueError(
                f"source_inventory_results {result['id']}.union_id must equal its id"
            )
    import source_first_audit_gate

    source_errors = source_first_audit_gate.validate_manifest(
        {
            "source_first_audit": source_gate,
            "final_review": {
                "decision": decision,
                "source_inventory_results": source_results,
            },
        },
        require_current=True,
    )
    if source_errors:
        raise ValueError("source-first audit: " + "; ".join(source_errors))
    blockers = raw["final_review"].get("blockers")
    if not isinstance(blockers, list):
        raise ValueError("final_review.blockers must be a list")
    if passing and blockers:
        raise ValueError("pass decision requires no blockers")
    if not passing and not blockers:
        raise ValueError("reject decision requires at least one blocker")

    liveness_errors: list[str] = []
    attribution_output = next(
        (
            item
            for item in outputs
            if isinstance(item, dict) and item.get("pass_id") == "example-attribution"
        ),
        None,
    )
    if liveness_contract and attribution_output and attribution_request:
        liveness_errors.extend(
            review_liveness.validate_attribution_liveness(
                attribution_output.get("blind_attribution_record"),
                attribution_request,
                alignment_key=attribution_alignment,
            )
        )
    if liveness_contract:
        liveness_errors.extend(
            review_liveness.validate_finding_liveness(
                raw["cold_review"], field="findings", label="cold review findings"
            )
        )
        liveness_errors.extend(
            review_liveness.validate_finding_liveness(
                raw["final_blind"],
                field="article_findings",
                label="final blind findings",
            )
        )
        liveness_errors.extend(
            review_liveness.validate_candidate_liveness(
                raw["final_blind"], label="final blind candidates"
            )
        )
        liveness_errors.extend(
            review_liveness.validate_final_review_liveness(
                raw["final_review"],
                target_quotes={str(item["id"]): str(item.get("text", "")) for item in extracted_targets},
                relation_quotes={
                    str(item["id"]): str(item.get("description", ""))
                    for item in extracted_relations
                },
            )
        )
    secondary_path = cycle_dir / "secondary_reviews.json"
    secondary_reviews = _read_json(secondary_path) if secondary_path.is_file() else None
    reviewers: list[tuple[str, Any]] = [
        (stage, raw[stage].get("reviewer"))
        for stage in ("cold_review", "final_blind", "final_review")
    ]
    reviewers.extend(
        (
            f"check_pass:{item.get('pass_id')}",
            item.get("reviewer"),
        )
        for item in outputs
        if isinstance(item, dict)
    )
    if secondary_reviews and provenance_contract:
        for stage in ("cold_review", "example_attribution"):
            value = secondary_reviews.get(stage)
            reviewer = value.get("reviewer") if isinstance(value, dict) else None
            secondary_errors = review_liveness.validate_reviewer(
                reviewer, generation_model=generation_model
            )
            secondary_request_path = (
                cycle_dir / "secondary_reviews" / f"{stage}.request.json"
            )
            secondary_request = (
                _read_json(secondary_request_path)
                if secondary_request_path.is_file()
                else None
            )
            secondary_errors.extend(
                review_liveness.validate_api_request_binding(
                    reviewer, secondary_request
                )
            )
            if secondary_errors:
                raise ValueError(
                    f"secondary_reviews.{stage}: " + "; ".join(secondary_errors)
                )
            reviewers.append((f"secondary_reviews.{stage}", reviewer))
        secondary_cold = secondary_reviews.get("cold_review")
        secondary_attribution = secondary_reviews.get("example_attribution")
        liveness_errors.extend(
            review_liveness.validate_finding_liveness(
                secondary_cold,
                field="findings",
                label="secondary cold review findings",
            )
        )
        secondary_request_path = (
            cycle_dir
            / "secondary_reviews"
            / "example_attribution.request.json"
        )
        if not secondary_request_path.is_file():
            liveness_errors.append(
                f"{review_liveness.B4_ZERO_FINDING_SINGLE_REVIEW}: second "
                "example-attribution request is missing"
            )
        elif isinstance(secondary_attribution, dict):
            secondary_request = _read_json(secondary_request_path)
            secondary_record = secondary_attribution.get(
                "blind_attribution_record"
            )
            record_errors = check_passes.validate_blind_attribution_record(
                secondary_record,
                secondary_request,
                check_liveness=False,
                generation_model=generation_model,
            )
            if record_errors:
                raise ValueError(
                    "secondary_reviews.example_attribution: "
                    + "; ".join(record_errors)
                )
            if (
                isinstance(secondary_record, dict)
                and secondary_record.get("reviewer")
                != secondary_attribution.get("reviewer")
            ):
                raise ValueError(
                    "secondary_reviews.example_attribution reviewer does not "
                    "match its blind record"
                )
            liveness_errors.extend(
                review_liveness.validate_attribution_liveness(
                    secondary_record, secondary_request
                )
            )
    _validate_api_raw_provenance(reviewers, cycle_dir)
    if liveness_contract:
        liveness_errors.extend(
            review_liveness.zero_finding_run_errors(
                raw["normal_review"],
                raw["cold_review"],
                raw["final_blind"],
                secondary_reviews=secondary_reviews,
            )
        )
    invalidated_by = review_liveness.invalidation_ids(liveness_errors)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_by": GENERATOR_VERSION,
        "entry_path": _relative(entry_path, repo_root),
        "cycle_id": cycle_dir.name,
        "cycle_dir": _relative(cycle_dir, repo_root),
        "body_sha256": current_hash,
        "raw_outputs": {
            stage: _raw_provenance(paths[stage], raw[stage], repo_root)
            for stage in RAW_FILENAMES
        },
        "source_first_audit": source_gate,
        "findings": list(finding_index.values()),
        "resolutions": list(resolutions.values()),
        "final_decision": {
            "decision": decision,
            "blockers": blockers,
            "notes": raw["final_review"].get("notes", []),
            "reviewed_at": raw["final_review"]["recorded_at"],
            "blind_output_sha256": blind_hash,
        },
    }
    if liveness_contract:
        manifest["invalidated_by"] = invalidated_by
        manifest["review_liveness_errors"] = review_liveness.summarize_errors(
            liveness_errors
        )
    return manifest


def validate_generated_manifest(
    entry_path: Path, audit_path: Path, *, repo_root: Path = REPO_ROOT
) -> list[str]:
    try:
        actual = _read_json(audit_path)
        if actual.get("schema_version") != SCHEMA_VERSION:
            return [f"schema_version must be {SCHEMA_VERSION}"]
        if actual.get("generated_by") != GENERATOR_VERSION:
            return [f"generated_by must be {GENERATOR_VERSION}"]
        cycle_dir_value = actual.get("cycle_dir")
        if not isinstance(cycle_dir_value, str) or not cycle_dir_value.startswith(
            "audits/runs/"
        ):
            return ["cycle_dir must be a safe path under audits/runs/"]
        cycle_dir = repo_root / cycle_dir_value
        expected = generate_manifest(entry_path, cycle_dir, repo_root=repo_root)
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        return [str(exc)]
    if _canonical(actual) != _canonical(expected):
        return [
            "derived audit manifest differs from raw outputs; regenerate with "
            "scripts/generate_audit_manifest.py"
        ]
    text = entry_path.read_text(encoding="utf-8")
    front: dict[str, str] = {}
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                front[key.strip()] = value.strip().strip('"')
    decision = actual["final_decision"]["decision"]
    if actual.get("invalidated_by"):
        required_status = review_liveness.required_pending_status(
            actual["invalidated_by"]
        )
        if front.get("status") != required_status or front.get("checked") != "false":
            return [
                "review-liveness invalidation requires entry status "
                f"{required_status} and checked false"
            ]
        return []
    if decision == "pass" and (
        front.get("status") not in {"checked", "final"}
        or front.get("checked") != "true"
    ):
        return ["pass audit requires entry status checked/final and checked true"]
    if decision == "reject" and (
        front.get("status") != "needs_review" or front.get("checked") != "false"
    ):
        return ["reject audit requires entry status needs_review and checked false"]
    return []


def _git_file_at(ref: str, relative: str, repo_root: Path) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{relative}"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    return result.stdout if result.returncode == 0 else None


def validate_blind_chronology(
    audit_path: Path, base: str, head: str, *, repo_root: Path = REPO_ROOT
) -> list[str]:
    try:
        manifest = _read_json(audit_path)
        raw_outputs = manifest["raw_outputs"]
        blind_path = str(raw_outputs["final_blind"]["path"])
        seal_path = str(raw_outputs["blind_seal"]["path"])
        final_path = str(raw_outputs["final_review"]["path"])
        expected_blind = (repo_root / blind_path).read_bytes()
        expected_seal = (repo_root / seal_path).read_bytes()
    except (OSError, KeyError, TypeError, json.JSONDecodeError, ValueError) as exc:
        return [f"cannot inspect v4 blind chronology: {exc}"]
    result = subprocess.run(
        ["git", "rev-list", "--reverse", f"{base}..{head}", "--", blind_path, seal_path, final_path],
        cwd=repo_root,
        check=True,
        text=True,
        capture_output=True,
    )
    revisions = [base, *[line for line in result.stdout.splitlines() if line.strip()]]
    for revision in revisions:
        blind_bytes = _git_file_at(revision, blind_path, repo_root)
        seal_bytes = _git_file_at(revision, seal_path, repo_root)
        final_bytes = _git_file_at(revision, final_path, repo_root)
        if blind_bytes == expected_blind and seal_bytes == expected_seal and final_bytes is None:
            return []
    return [
        "blind chronology requires an ancestor commit containing the immutable "
        "final_blind and blind_seal outputs before final_review exists"
    ]


def _print_errors(errors: list[str]) -> int:
    if not errors:
        print("Generated audit manifest validation passed.")
        return 0
    print("Generated audit manifest validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate v4 audits only from raw review outputs")
    sub = parser.add_subparsers(dest="command", required=True)
    seal = sub.add_parser("seal-blind")
    seal.add_argument("entry", type=Path)
    seal.add_argument("final_blind", type=Path)
    seal.add_argument("--output", required=True, type=Path)
    generate = sub.add_parser("generate")
    generate.add_argument("entry", type=Path)
    generate.add_argument("cycle_dir", type=Path)
    generate.add_argument("--output", required=True, type=Path)
    validate = sub.add_parser("validate")
    validate.add_argument("entry", type=Path)
    validate.add_argument("audit", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "seal-blind":
            value = seal_blind(args.entry.resolve(), args.final_blind.resolve(), args.output.resolve())
            print(json.dumps(value, ensure_ascii=False, indent=2))
            return 0
        if args.command == "generate":
            value = generate_manifest(args.entry.resolve(), args.cycle_dir.resolve())
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(args.output)
            return 0
        return _print_errors(
            validate_generated_manifest(args.entry.resolve(), args.audit.resolve())
        )
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
