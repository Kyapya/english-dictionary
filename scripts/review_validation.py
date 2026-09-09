"""Input-only review checks shared by dispatch and final audit validation.

No reviewer is called, no input is repaired, and no audit file is written here.
Independent checks collect errors; unavailable prerequisites are reported separately.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

FINAL_INPUTS = (
    "pass_findings", "cold_review", "final_blind", "blind_seal",
    "pre_blind_resolution", "pre_blind_revision", "checker_recheck_manifest",
    "post_blind_resolution", "post_blind_verification", "targeted_adjudications",
    "source_inventory", "resolutions",
)
INPUT_ARTIFACTS = {
    "source_inventory": {"headword", "source_first_spec"},
    "normal_review": {"router_selected_sections", "checker_pass_specs"},
    "cold_review": {"entry_body", "cold_review_prompt"},
    "resolutions": {"entry_body", "all_findings"},
    "final_blind": {"entry_body", "final_blind_prompt"},
}


class PreflightError(ValueError):
    """A repairable input/response contract rejection, not an execution failure."""

    def __init__(self, report: dict[str, Any]):
        self.report = report
        messages = [row["message"] for row in report["errors"]]
        messages.extend("blocked check: " + row["check"] for row in report.get("blocked_checks", []))
        super().__init__("; ".join(messages))


def issue(code: str, path: str, message: str, **details: Any) -> dict[str, Any]:
    return {"code": code, "path": path, "message": message, **details}


def metadata_errors(raw: dict, stage: str, body_hash: str,
                    expected_artifacts: set[str]) -> list[dict]:
    errors: list[dict] = []
    def mismatch(field: str, expected: Any, actual: Any, message: str) -> None:
        errors.append(issue("metadata_mismatch", f"{stage}.{field}", message,
                            expected=expected, actual=actual))
    if raw.get("stage") != stage:
        mismatch("stage", stage, raw.get("stage"), f"{stage}: raw stage field must be {stage}")
    for key in ("run_id", "context_id", "prompt_sha256", "recorded_at"):
        if not str(raw.get(key, "")).strip():
            mismatch(key, "non-empty value", raw.get(key), f"{stage}.{key} is required")
    if raw.get("input_body_sha256") != body_hash:
        mismatch("input_body_sha256", body_hash, raw.get("input_body_sha256"),
                 f"{stage}.input_body_sha256 is stale; expected={body_hash}, actual={raw.get('input_body_sha256')}")
    artifacts = raw.get("input_artifacts")
    if (not isinstance(artifacts, list) or not all(isinstance(x, str) for x in artifacts)
            or set(artifacts) != expected_artifacts):
        mismatch("input_artifacts", sorted(expected_artifacts), artifacts,
                 f"{stage}.input_artifacts must be exactly {sorted(expected_artifacts)}")
    try:
        datetime.fromisoformat(str(raw.get("recorded_at", "")).replace("Z", "+00:00"))
    except ValueError:
        mismatch("recorded_at", "ISO-8601", raw.get("recorded_at"), f"{stage}.recorded_at must be ISO-8601")
    return errors


def index_rows(items: Any, label: str, errors: list[dict]) -> dict[str, dict] | None:
    if not isinstance(items, list):
        errors.append(issue("invalid_list", label, f"{label} must be a list"))
        return None
    result: dict[str, dict] = {}
    valid = True
    for i, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
            errors.append(issue("invalid_id", f"{label}[{i}]", f"{label}[{i}] requires a non-empty id"))
            valid = False
        elif item["id"] in result:
            errors.append(issue("duplicate_id", label, f"{label} contains duplicate id: {item['id']}", actual=item["id"]))
            valid = False
        else:
            result[item["id"]] = item
    return result if valid else None


def resolution_errors(items: Any, expected_ids: set[str] | None,
                      body_hash: str) -> list[dict]:
    errors: list[dict] = []
    rows = index_rows(items, "resolutions", errors)
    if rows is not None and expected_ids is not None and set(rows) != expected_ids:
        missing, extra = sorted(expected_ids - set(rows)), sorted(set(rows) - expected_ids)
        errors.append(issue("resolution_coverage", "resolutions",
                            f"resolutions must cover every finding exactly once; missing={missing}, extra={extra}",
                            missing=missing, extra=extra, expected=sorted(expected_ids), actual=sorted(rows)))
    # Inspect valid individual objects even when another row prevents set comparison.
    for row in items if isinstance(items, list) else []:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            continue
        rid = row["id"]
        for field, expected in (("finding_id", rid), ("status", "resolved"),
                                ("resolved_body_sha256", body_hash)):
            if row.get(field) != expected:
                message = (f"resolution {rid} is stale" if field == "resolved_body_sha256"
                           else f"resolution {rid}.finding_id must equal its id" if field == "finding_id"
                           else f"resolution {rid}.status must be resolved")
                errors.append(issue("resolution_mismatch", f"resolutions.{rid}.{field}",
                                    message, expected=expected, actual=row.get(field)))
        if row.get("disposition") not in {"adopted", "rejected"}:
            errors.append(issue("resolution_disposition", f"resolutions.{rid}.disposition", f"resolution {rid}.disposition is invalid"))
        if not str(row.get("rationale", "")).strip():
            errors.append(issue("resolution_rationale", f"resolutions.{rid}.rationale", f"resolution {rid}.rationale is required"))
    return errors


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def _sealed_in_history(cycle: Path, root: Path) -> bool:
    import generate_audit_manifest as audit
    relative = cycle.relative_to(root).as_posix()
    history = subprocess.check_output(
        ["git", "-C", str(root), "rev-list", "HEAD", "--", relative + "/blind_seal.json"],
        text=True,
    ).splitlines()
    for sha in history:
        if (all(audit._git_file_at(sha, relative + "/" + name + ".json", root)
                == (cycle / (name + ".json")).read_bytes()
                for name in ("final_blind", "blind_seal"))
                and audit._git_file_at(sha, relative + "/final_review.json", root) is None):
            return True
    return False


def final_input_report(entry: Path, cycle: Path, root: Path, *,
                       check_history: bool = True) -> dict[str, Any]:
    """Collect all independently checkable prerequisites before final dispatch.

    Runtime/permission/subprocess failures intentionally propagate to the caller's
    execution-failure path. Missing/malformed input data are ordinary diagnostics.
    """
    import content_audit
    import generate_audit_manifest as audit
    import workflow_revision

    errors: list[dict] = []
    blocked: list[dict] = []
    values: dict[str, dict] = {}

    def load(path: Path, label: str) -> dict | None:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            errors.append(issue("missing_input", label, f"final review input missing: {label}"))
            return None
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(issue("malformed_json", label, f"invalid JSON in {label}: {exc}"))
            return None
        if not isinstance(value, dict):
            errors.append(issue("invalid_object", label, f"{label} must be a JSON object"))
            return None
        return value

    def ready(check: str, *names: str) -> bool:
        missing = [name for name in names if name not in values]
        if missing:
            blocked.append({"check": check, "requires": missing})
        return not missing

    def collect(label: str, call) -> Any:
        try:
            result = call()
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            # These calls are pure schema validators over already-loaded JSON.
            errors.append(issue("input_contract", label, f"{label}: {exc}"))
            return None
        if isinstance(result, list):
            errors.extend(issue("input_contract", label, str(message)) for message in result)
        return result

    for name in FINAL_INPUTS:
        value = load(cycle / (name + ".json"), name)
        if value is not None:
            values[name] = value
    try:
        body_hash = audit.body_sha256(entry)
    except (FileNotFoundError, UnicodeDecodeError) as exc:
        errors.append(issue("entry_unreadable", "entry_body", str(exc)))
        blocked.append({"check": "body_bound_checks", "requires": ["entry_body"]})
        return {"valid": False, "errors": errors, "blocked_checks": blocked}

    initial = values.get("pre_blind_revision", {}).get("input_body_sha256")
    for name, stage in (("source_inventory", "source_inventory"), ("pass_findings", "normal_review"),
                        ("cold_review", "cold_review"), ("resolutions", "resolutions"),
                        ("final_blind", "final_blind")):
        if not ready("metadata:" + name, name):
            continue
        expected_hash = initial if name in {"pass_findings", "cold_review"} else body_hash
        if not isinstance(expected_hash, str) or not expected_hash:
            blocked.append({"check": "metadata:" + name, "requires": ["pre_blind_revision.input_body_sha256"]})
            continue
        errors.extend(metadata_errors(values[name], stage, expected_hash, INPUT_ARTIFACTS[stage]))
    for name in ("cold_review", "final_blind"):
        if ready("blind_context:" + name, name) and values[name].get("audit_visible") is not False:
            errors.append(issue("context_exposure", name + ".audit_visible", f"{name}.audit_visible must be false"))
    if ready("context_independence", "pass_findings", "cold_review", "final_blind"):
        identities = [(values[n].get("run_id"), values[n].get("context_id"))
                      for n in ("pass_findings", "cold_review", "final_blind")]
        if all(all(isinstance(v, str) and v for v in pair) for pair in identities) and len(set(identities)) != 3:
            errors.append(issue("context_identity", "review_contexts", "normal, cold, and final run/context identities must be distinct"))

    collections: dict[str, dict[str, dict] | None] = {}
    for name, field in (("pass_findings", "independent_candidates"), ("cold_review", "findings"),
                        ("final_blind", "independent_candidates"), ("final_blind", "article_findings")):
        label = name + "." + field
        collections[label] = index_rows(values[name].get(field), label, errors) if name in values else None
    import check_passes
    router = check_passes.load_router(root / "prompts/check_router_v6.md")
    expected_passes = {row["id"] for row in router["passes"]}
    outputs = values.get("pass_findings", {}).get("pass_outputs")
    normal_findings: list[dict] = []
    normal_ready = isinstance(outputs, list)
    if "pass_findings" in values and not normal_ready:
        errors.append(issue("invalid_list", "pass_findings.pass_outputs", "pass_outputs must be explicitly present as a list"))
    pass_ids: list[str] = []
    for i, output in enumerate(outputs if isinstance(outputs, list) else []):
        if not isinstance(output, dict):
            errors.append(issue("invalid_object", f"pass_outputs[{i}]", "checker pass output must be an object"))
            normal_ready = False
            continue
        pid = output.get("pass_id")
        if not isinstance(pid, str) or not pid:
            errors.append(issue("invalid_id", f"pass_outputs[{i}].pass_id", "checker pass_id is required"))
        else:
            pass_ids.append(pid)
        rows = index_rows(output.get("findings"), f"pass_outputs[{i}].findings", errors)
        if rows is None:
            normal_ready = False
        else:
            normal_findings.extend(rows.values())
    if isinstance(outputs, list):
        duplicate = sorted(pid for pid, count in Counter(pass_ids).items() if count > 1)
        if set(pass_ids) != expected_passes or duplicate:
            errors.append(issue("pass_coverage", "pass_findings.pass_outputs", "normal review must cover every routed pass exactly once",
                                missing=sorted(expected_passes - set(pass_ids)), extra=sorted(set(pass_ids) - expected_passes), duplicates=duplicate))
    # Checker findings use the router's native taxonomy, not the article-finding
    # taxonomy. Reuse the same validator and provenance inputs as final audit.
    def optional(relative: str) -> dict | None:
        path = cycle / relative
        return load(path, relative) if path.is_file() else None

    attribution = optional("check_passes/example-attribution.request.json")
    attribution_key = optional("check_passes/example-attribution.alignment-key.json")
    antonym = optional("check_passes/frame-relation.request.json")
    antonym_stage2 = optional("check_passes/frame-relation.antonym-axis.stage2.request.json")
    antonym_key = optional("check_passes/frame-relation.antonym-axis.alignment-key.json")
    provenance = not audit._is_historical_cycle(cycle) or any(
        isinstance(values.get(name, {}).get("reviewer"), dict)
        for name in ("cold_review", "final_blind")
    ) or any(isinstance(row, dict) and isinstance(row.get("reviewer"), dict)
             for row in (outputs if isinstance(outputs, list) else []))
    generation_model = audit._entry_front_matter(entry).get("model")
    for i, output in enumerate(outputs if isinstance(outputs, list) else []):
        if not isinstance(output, dict) or output.get("pass_id") not in expected_passes:
            continue
        pid = output["pass_id"]
        request = optional("check_passes/" + pid + ".request.json")
        if pid == "frame-relation" and antonym_stage2 is not None:
            request = antonym_stage2
        collect(f"pass_outputs[{i}]", lambda output=output, request=request: check_passes.validate_pass_output(
            output, router, entry_path=entry, repo_root=root,
            example_request=attribution, alignment_key=attribution_key,
            antonym_request=antonym, antonym_stage2_request=antonym_stage2,
            antonym_alignment_key=antonym_key, request_payload=request,
            check_liveness=False, generation_model=generation_model,
            require_reviewer=provenance,
            require_antonym_axis=("antonym_axis_blind_record" in output
                                  or any(value is not None for value in (antonym, antonym_stage2, antonym_key))),
        ))
    cold = collections.get("cold_review.findings")
    blind = collections.get("final_blind.article_findings")
    for name, rows, validator in (("cold_review.findings", cold, audit._validate_cold_finding),
                                   ("final_blind.article_findings", blind, audit._validate_finding)):
        for rid, row in (rows or {}).items():
            collect(f"{name}.{rid}", lambda row=row, rid=rid, validator=validator: validator(row, rid))
    all_rows = None
    if normal_ready and cold is not None and blind is not None:
        all_rows = index_rows([*normal_findings, *cold.values(), *blind.values()], "all findings", errors)
    if "resolutions" in values:
        errors.extend(resolution_errors(values["resolutions"].get("resolutions"),
                                        set(all_rows) if all_rows is not None else None, body_hash))
    if all_rows is None:
        blocked.append({"check": "resolution_coverage", "requires": ["valid finding inventories"]})

    for field in ("independent_candidates",):
        for rid, row in (collections.get("final_blind." + field) or {}).items():
            assertions = index_rows(row.get("semantic_assertions"), f"final_blind.candidates.{rid}.semantic_assertions", errors)
            if assertions == {}:
                errors.append(issue("empty_assertions", rid, f"candidate {rid} requires semantic assertions"))
    source = values.get("source_inventory", {})
    source_first = source.get("source_first_audit")
    if "source_inventory" in values:
        if not isinstance(source_first, dict):
            errors.append(issue("invalid_object", "source_inventory.source_first_audit", "source_first_audit must be an object"))
        else:
            index_rows(source_first.get("source_union"), "source_inventory.source_first_audit.source_union", errors)
        # The v1 field is optional; explicit malformed values are still rejected.
        evidence = source.get("evidence_link_ids", [])
        if (not isinstance(evidence, list) or not all(isinstance(x, str) and x for x in evidence)
                or len(evidence) != len(set(evidence))):
            errors.append(issue("evidence_ids", "source_inventory.evidence_link_ids", "evidence_link_ids, when present, must be a list of unique non-empty IDs"))

    if ready("checker_recheck", "checker_recheck_manifest"):
        recheck = values["checker_recheck_manifest"]
        collect("checker_recheck_manifest", lambda: workflow_revision.validate_recheck_manifest(recheck, current_body_sha256=body_hash))
        if isinstance(source_first, dict):
            for row in recheck.get("pass_results", []) if isinstance(recheck.get("pass_results"), list) else []:
                if isinstance(row, dict) and row.get("source_artifact_sha256") != _digest(source_first):
                    errors.append(issue("stale_source", f"checker_recheck_manifest.{row.get('pass_id')}.source_artifact_sha256",
                                        "source changed since checker verification; verify against the fixed current source before final review",
                                        expected=_digest(source_first), actual=row.get("source_artifact_sha256")))
        else:
            blocked.append({"check": "checker_source_binding", "requires": ["source_inventory.source_first_audit"]})

    snapshot_path = cycle / "check_passes/input_snapshot.json"
    snapshot = load(snapshot_path, "check_passes/input_snapshot.json") if snapshot_path.is_file() else None
    if snapshot is not None:
        request_hashes = snapshot.get("request_hashes")
        if not isinstance(request_hashes, dict):
            errors.append(issue("invalid_object", "input_snapshot.request_hashes", "request_hashes must be an object"))
        else:
            original_ids = {p.name.removesuffix(".request.json")
                            for p in (cycle / "check_passes").glob("*.request.json")
                            if p.name.removesuffix(".request.json") in expected_passes}
            for pid in sorted(set(request_hashes) | original_ids):
                expected = request_hashes.get(pid)
                if not isinstance(pid, str) or Path(pid).name != pid or pid in {".", ".."}:
                    errors.append(issue("invalid_id", "input_snapshot.request_hashes", "invalid checker request pass_id"))
                    continue
                packet = load(cycle / "check_passes" / (pid + ".request.json"), pid + ".request.json")
                if packet is not None and _digest(packet) != expected:
                    errors.append(issue("immutable_request_changed", pid + ".request.json", "original checker request was rewritten: " + pid + ".request.json", expected=expected, actual=_digest(packet)))

    if (all_rows is not None and ready("workflow_partition", "pre_blind_resolution", "pre_blind_revision",
                                      "post_blind_resolution", "post_blind_verification", "checker_recheck_manifest",
                                      "pass_findings", "cold_review", "final_blind", "source_inventory", "targeted_adjudications")):
        raw = {"normal_review": values["pass_findings"], "cold_review": values["cold_review"],
               "final_blind": values["final_blind"], "source_inventory": source,
               }
        collect("workflow_improvement", lambda: audit._validate_workflow_improvement_artifacts(
            cycle_dir=cycle, repo_root=root, raw=raw, current_hash=body_hash,
            checker_and_cold_ids={r["id"] for r in normal_findings} | set(cold or {}),
            final_blind_ids=set(blind or {}), require_resolved=True))

    if ready("blind_seal", "final_blind", "blind_seal"):
        seal = values["blind_seal"]
        expected_fields = {
            "schema_version": audit.BLIND_SEAL_VERSION,
            "body_sha256": body_hash,
            "final_blind_path": (cycle / "final_blind.json").relative_to(root).as_posix(),
            "final_blind_sha256": hashlib.sha256((cycle / "final_blind.json").read_bytes()).hexdigest(),
            "blind_output_sha256": _digest(audit.blind_payload(values["final_blind"])),
        }
        for field, expected in expected_fields.items():
            if seal.get(field) != expected:
                errors.append(issue("seal_mismatch", "blind_seal." + field, f"blind seal {field} does not match current sealed input", expected=expected, actual=seal.get(field)))
        try:
            blind_time = audit._timestamp(values["final_blind"].get("recorded_at"), "final_blind.recorded_at")
            seal_time = audit._timestamp(seal.get("sealed_at"), "blind_seal.sealed_at")
            if seal_time < blind_time:
                errors.append(issue("seal_chronology", "blind_seal.sealed_at", "blind seal cannot precede final_blind recording"))
        except (ValueError, TypeError) as exc:
            errors.append(issue("seal_chronology", "blind_seal.sealed_at", str(exc)))
        if check_history and not _sealed_in_history(cycle, root):
            errors.append(issue("seal_not_committed", "blind_seal", "commit final_blind and blind_seal before preparing final review"))

    # Target extraction is independent of unrelated malformed audit JSON.
    try:
        targets = content_audit.extract_targets(entry)
        relations = content_audit.extract_relations(targets)
        index_rows(targets, "targets", errors)
        index_rows(relations, "relations", errors)
    except (ValueError, KeyError, TypeError) as exc:
        errors.append(issue("target_extraction", "entry_body", str(exc)))
    return {"valid": not errors and not blocked, "errors": errors, "blocked_checks": blocked}
