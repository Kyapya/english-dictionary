"""Deterministic review packets and side-effect-free rehearsal of real ingestion."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import content_audit
import generate_audit_manifest as audit
import review_validation

# Keep dispatched v1 packet bindings compatible; the execution policy is versioned
# separately in review_recovery.POLICY_VERSION.
VERSION = "review_preflight_v1"
FINAL_INPUTS = review_validation.FINAL_INPUTS
PreflightError = review_validation.PreflightError


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def freeze(path: Path, value: dict) -> None:
    if path.exists() and json.loads(path.read_text()) != value:
        raise ValueError(f"immutable review input changed: {path.name}; preserve the old packet and create the required revision/recheck")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def final_inputs(entry: Path, cycle: Path, root: Path) -> dict:
    report = review_validation.final_input_report(entry, cycle, root)
    if not report["valid"]:
        raise PreflightError(report)
    values = {name: json.loads((cycle / (name + ".json")).read_text()) for name in FINAL_INPUTS}
    body_hash = audit.body_sha256(entry)
    targets = content_audit.extract_targets(entry)
    relations = content_audit.extract_relations(targets)
    source = values["source_inventory"]
    findings = [row for output in values["pass_findings"]["pass_outputs"] for row in output["findings"]]
    findings += values["cold_review"]["findings"] + values["final_blind"]["article_findings"]
    inventories = {
        "target_results": targets,
        "relation_results": relations,
        "normal_candidate_results": values["pass_findings"]["independent_candidates"],
        "blind_candidate_results": values["final_blind"]["independent_candidates"],
        "finding_results": findings,
        "evidence_checks": [{"id": item} for item in source["evidence_link_ids"]],
        "source_inventory_results": source["source_first_audit"]["source_union"],
    }
    template = {"decision": None, "blockers": [], "notes": []}
    typed_ids = {"target_results": "target_id", "relation_results": "relation_id", "source_inventory_results": "union_id"}
    for field, rows in inventories.items():
        template[field] = []
        for row in rows:
            result = {"id": row["id"], "status": None, "notes": ""}
            if field in typed_ids:
                result[typed_ids[field]] = row["id"]
            if field == "blind_candidate_results":
                result.update(assertion_ids=[a["id"] for a in row["semantic_assertions"]], verified_body_sha256=body_hash)
                result["assertion_results"] = [{"id": a["id"], "status": None, "notes": ""} for a in row["semantic_assertions"]]
            template[field].append(result)
    values["inventories"] = inventories
    template["checker_recheck_results"] = [{"id": row["pass_id"], "pass_id": row["pass_id"], "status": None, "notes": ""} for row in values["checker_recheck_manifest"]["pass_results"]]
    template["chronology_results"] = [{"id": name, "check_id": name, "status": None, "notes": ""} for name in ("body_hash_binding", "cold_and_normal_before_revision", "revision_before_final_blind", "final_blind_before_seal", "post_blind_completion")]
    values["response_template"] = template
    values["input_bindings"] = {name + ".json": hashlib.sha256((cycle / (name + ".json")).read_bytes()).hexdigest() for name in FINAL_INPUTS}
    for directory in ("check_passes", "recheck"):
        values["input_bindings"].update({p.relative_to(cycle).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((cycle / directory).glob("*.json"))})
    values["contract_version"] = VERSION
    return values


def check_bindings(packet: dict, entry: Path, cycle: Path) -> None:
    errors: list[dict] = []
    expected_body = packet.get("_output_metadata", {}).get("input_body_sha256")
    actual_body = audit.body_sha256(entry)
    if expected_body != actual_body:
        errors.append(review_validation.issue("body_changed_after_dispatch", "entry_body", "review input body changed after dispatch", expected=expected_body, actual=actual_body))
    bindings = packet.get("input_bindings", {})
    if not isinstance(bindings, dict):
        errors.append(review_validation.issue("invalid_bindings", "input_bindings", "input_bindings must be an object"))
        bindings = {}
    for name, expected in bindings.items():
        if not isinstance(name, str):
            errors.append(review_validation.issue("invalid_binding_path", "input_bindings", "binding path must be a string"))
            continue
        path = cycle / name
        actual = None
        if path.resolve().is_relative_to(cycle.resolve()) and path.is_file():
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual is None or actual != expected:
            errors.append(review_validation.issue("input_changed_after_dispatch", name, "review input changed after dispatch: " + name, expected=expected, actual=actual))
    if errors:
        raise PreflightError({"valid": False, "errors": errors, "blocked_checks": []})


def validate(manifest: dict, *, stage: str, declared_model: str, reviewer_agent_id: str | None, repo_root: Path, ingest) -> dict:
    """Run the same ingester in an isolated copy, including final audit validation.

    No timestamps, failure counters, raw outputs or manifests in the real run change.
    """
    import run_word_v3
    request = run_word_v3.next_stage_request(manifest)
    if not request or request["name"] != stage:
        raise ValueError("validate-review must target the pending stage")
    entry = repo_root / manifest["entry_path"]
    cycle = (repo_root / request["output_paths"][-1 if stage == "checker_passes" else 0]).parent
    if stage == "final_review" and manifest.get("review_preflight") == VERSION:
        report = review_validation.final_input_report(entry, cycle, repo_root)
        if not report["valid"]:
            raise PreflightError(report)
    packet_path = cycle / (stage + ".request.json")
    if packet_path.exists():
        packet = json.loads(packet_path.read_text())
        if packet.get("contract_version") == VERSION:
            check_bindings(packet, entry, cycle)
    with tempfile.TemporaryDirectory(prefix="dictionary-review-check-") as directory:
        root = Path(directory)
        for relative in (Path("prompts"), cycle.relative_to(repo_root)):
            shutil.copytree(repo_root / relative, root / relative)
        target_entry = root / manifest["entry_path"]
        target_entry.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(entry, target_entry)
        for name in ("escaped_defect_taxonomy.json", "review_invalidations.json"):
            path = repo_root / "audits" / name
            if path.exists():
                shutil.copy2(path, root / "audits" / name)
        ingest(copy.deepcopy(manifest), stage=stage, declared_model=declared_model, reviewer_agent_id=reviewer_agent_id, repo_root=root)
        if stage == "final_review":
            audit.generate_manifest(target_entry, root / cycle.relative_to(repo_root), repo_root=root)
    return {"valid": True, "stage": stage}
