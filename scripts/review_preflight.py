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

VERSION = "review_preflight_v1"
FINAL_INPUTS = (
    "pass_findings", "cold_review", "final_blind", "blind_seal",
    "pre_blind_resolution", "pre_blind_revision", "checker_recheck_manifest",
    "post_blind_resolution", "post_blind_verification", "targeted_adjudications",
    "source_inventory", "resolutions",
)


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def freeze(path: Path, value: dict) -> None:
    if path.exists() and json.loads(path.read_text()) != value:
        raise ValueError(f"immutable review input changed: {path.name}; preserve the old packet and create the required revision/recheck")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def final_inputs(entry: Path, cycle: Path, root: Path) -> dict:
    missing = [name for name in FINAL_INPUTS if not (cycle / (name + ".json")).is_file()]
    if missing:
        raise ValueError("final review input missing: " + ", ".join(missing))
    values = {name: json.loads((cycle / (name + ".json")).read_text()) for name in FINAL_INPUTS}
    body_hash = audit.body_sha256(entry)
    if values["final_blind"].get("input_body_sha256") != body_hash:
        raise ValueError("final blind references an old body")
    seal = values["blind_seal"]
    if seal.get("final_blind_sha256") != hashlib.sha256((cycle / "final_blind.json").read_bytes()).hexdigest():
        raise ValueError("blind seal references a different raw output")
    import workflow_revision
    errors = workflow_revision.validate_recheck_manifest(values["checker_recheck_manifest"], current_body_sha256=body_hash)
    current_source = values["source_inventory"]
    for result in values["checker_recheck_manifest"].get("pass_results", []):
        if result.get("source_artifact_sha256") != digest(current_source.get("source_first_audit")):
            errors.append(f"{result.get('pass_id')}: source changed since checker verification; verify against the fixed current source before final review")
    for path in sorted((cycle / "check_passes").glob("*.request.json")):
        # Stage-specific request binding is also enforced by the original ingester.
        request = json.loads(path.read_text())
        snapshot_path = cycle / "check_passes" / "input_snapshot.json"
        if snapshot_path.exists():
            snapshot = json.loads(snapshot_path.read_text())
            expected = snapshot["request_hashes"].get(request.get("pass_id"))
            if path.name == f"{request.get('pass_id')}.request.json" and expected != digest(request):
                errors.append("original checker request was rewritten: " + path.name)
    if errors:
        raise ValueError("; ".join(errors))
    # Require the actual immutable bytes in an ancestor before calling the reviewer.
    relative = cycle.relative_to(root).as_posix()
    import subprocess
    history = subprocess.check_output(["git", "-C", str(root), "rev-list", "HEAD", "--", relative + "/blind_seal.json"], text=True).splitlines()
    sealed = False
    for sha in history:
        if all(audit._git_file_at(sha, relative + "/" + name + ".json", root) == (cycle / (name + ".json")).read_bytes() for name in ("final_blind", "blind_seal")) and audit._git_file_at(sha, relative + "/final_review.json", root) is None:
            sealed = True
            break
    if not sealed:
        raise ValueError("commit final_blind and blind_seal before preparing final review")
    targets = content_audit.extract_targets(entry)
    relations = content_audit.extract_relations(targets)
    source = values["source_inventory"]
    if not isinstance(source.get("source_first_audit"), dict) or not isinstance(source["source_first_audit"].get("source_union"), list):
        raise ValueError("source union must be explicitly present, including when empty")
    for value, field in ((values["pass_findings"], "independent_candidates"), (values["pass_findings"], "pass_outputs"), (source, "evidence_link_ids"), (values["cold_review"], "findings"), (values["final_blind"], "independent_candidates"), (values["final_blind"], "article_findings")):
        if not isinstance(value.get(field), list):
            raise ValueError(field + " must be explicitly present, including when empty")
    findings = [row for output in values["pass_findings"].get("pass_outputs", []) for row in output.get("findings", [])]
    findings += values["cold_review"].get("findings", []) + values["final_blind"].get("article_findings", [])
    inventories = {
        "target_results": targets,
        "relation_results": relations,
        "normal_candidate_results": values["pass_findings"].get("independent_candidates", []),
        "blind_candidate_results": values["final_blind"].get("independent_candidates", []),
        "finding_results": findings,
        "evidence_checks": [{"id": item} for item in source.get("evidence_link_ids", [])],
        "source_inventory_results": source["source_first_audit"]["source_union"],
    }
    template = {"decision": None, "blockers": [], "notes": []}
    typed_ids = {"target_results": "target_id", "relation_results": "relation_id", "source_inventory_results": "union_id"}
    for field, rows in inventories.items():
        ids = [row["id"] for row in rows]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate IDs in " + field)
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
    if packet.get("_output_metadata", {}).get("input_body_sha256") != audit.body_sha256(entry):
        raise ValueError("review input body changed after dispatch")
    for name, expected in packet.get("input_bindings", {}).items():
        path = cycle / name
        if not path.resolve().is_relative_to(cycle.resolve()) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("review input changed after dispatch: " + name)


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
