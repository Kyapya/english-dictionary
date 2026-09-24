from __future__ import annotations

"""Resumable two-review workflow. Historical workflows are read by run_word_v3.

This coordinator never fabricates a content judgment: machine receipts bind actual
raw replies, and an absent or unchecked area remains a publish blocker.
"""

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import review_dependency_v4 as dependencies
import validate_entry
import workflow_revision

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "prompts/compact_review_contract_v1.json"
VERSION = dependencies.VERSION


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def _save(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _path(manifest: dict[str, Any], key: str, root: Path) -> Path:
    candidate = (root / str(manifest[key])).resolve()
    candidate.relative_to(root.resolve())
    return candidate


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _spec(root: Path) -> str:
    return _sha(root / "prompts/compact_review_contract_v1.json")


def current(manifest: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    if manifest.get("workflow_contract_version") != VERSION:
        raise ValueError("not a compact review run")
    entry, inventory = _path(manifest, "entry_path", root), _path(manifest, "inventory_path", root)
    if not entry.is_file() or not inventory.is_file():
        raise ValueError("draft and source inventory must exist before content review")
    return dependencies.snapshot(entry, _json(inventory), specification_sha256=_spec(root))


def research_errors(manifest: dict[str, Any], body_sha256: str, root: Path = ROOT) -> list[str]:
    inventory = _json(_path(manifest, "inventory_path", root))
    errors = []
    if inventory.get("input_body_sha256") not in (None, body_sha256):
        errors.append("source inventory is bound to another article body")
    gate = inventory.get("source_first_audit")
    if not isinstance(gate, dict):
        return [*errors, "source inventory has no source_first_audit"]
    dictionaries = {row.get("independence_group") for row in gate.get("sources", [])
                    if isinstance(row, dict) and row.get("source_type") in
                    {"general_dictionary", "learner_dictionary", "general_lexicon"}
                    and str(row.get("locator", "")).startswith("http")
                    and row.get("independence_group")}
    if len(dictionaries) < 2:
        errors.append("two independent principal dictionaries are required")
    if gate.get("open_questions"):
        errors.append("unresolved source questions must be assessed before publication")
    return errors


def start(headword: str, entry: Path, inventory: Path, *, root: Path = ROOT,
          run_id: str | None = None) -> Path:
    if not re.fullmatch(r"[a-z][a-z0-9-]*", headword):
        raise ValueError("use a lowercase slug for the headword")
    branch = subprocess.check_output(["git", "-C", str(root), "branch", "--show-current"], text=True).strip()
    if branch in {"", "main", "master"}:
        raise ValueError("start on a dedicated word branch")
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = root / "audits/workflow_runs" / headword / f"{run_id}.json"
    if path.exists():
        raise FileExistsError("resume this run instead of resetting its history")
    manifest = {"workflow_contract_version": VERSION, "run_id": run_id,
                "headword": headword, "branch": branch, "started_at": _now(),
                "entry_path": _relative(entry, root), "inventory_path": _relative(inventory, root),
                "review_receipts": [], "resolutions": [], "migration": None,
                "status": "in_progress", "stage": "mechanical_validation"}
    queue = root / "queue/words.csv"
    if queue.is_file():
        lines = queue.read_text(encoding="utf-8").splitlines()
        if not any(line.startswith(headword + ",") for line in lines[1:]):
            fields = [headword, "word", "pending", "", manifest["entry_path"],
                      "entry_spec_v5", "unknown", _now()[:10], _now()[:10],
                      "false", "compact review pending"]
            with queue.open("a", encoding="utf-8") as handle:
                handle.write(("" if not lines or queue.read_bytes().endswith(b"\n") else "\n")
                             + ",".join(fields) + "\n")
    _save(path, manifest)
    return path


def prepare(manifest: dict[str, Any], run_path: Path, role: str,
            *, root: Path = ROOT) -> Path:
    if role not in {"A", "B"}:
        raise ValueError("review role must be A or B")
    snap = current(manifest, root)
    errors = validate_entry.validate_file(_path(manifest, "entry_path", root))
    errors.extend(research_errors(manifest, snap["body_sha256"], root))
    if errors:
        raise ValueError("mechanical validation failed: " + "; ".join(errors))
    if snap["ambiguous"]:
        raise ValueError("unclassified content or dangling evidence claim requires correction")
    directory = run_path.parent / run_path.stem / "compact"
    request = directory / f"review-{role}.request.json"
    entry = _path(manifest, "entry_path", root)
    snapshot_file = directory / f"snapshot-{snap['body_sha256'][:16]}-{snap['inventory_sha256'][:12]}.json"
    shared = {"entry_body": entry.read_text(encoding="utf-8"),
              "source_inventory_path": manifest["inventory_path"],
              "source_inventory_sha256": snap["inventory_sha256"],
              "body_sha256": snap["body_sha256"], "area_keys": snap["areas"]}
    if snapshot_file.is_file() and _json(snapshot_file) != shared:
        raise ValueError("shared input snapshot is immutable; create a new edition")
    if not snapshot_file.exists():
        _save(snapshot_file, shared)
    payload = {"workflow_contract_version": VERSION, "role": role,
               "snapshot_path": _relative(snapshot_file, root),
               "snapshot_sha256": _sha(snapshot_file),
               "body_sha256": snap["body_sha256"], "area_keys": snap["areas"],
               "review_scope": _json(root / "prompts/compact_review_contract_v1.json")["roles"][role]}
    if role == "B":
        payload["source_inventory_path"] = manifest["inventory_path"]
        payload["source_inventory_sha256"] = snap["inventory_sha256"]
    _save(request, payload)
    manifest["stage"] = "independent_reviews"
    _save(run_path, manifest)
    return request


def _normalize(raw: dict[str, Any], areas: set[str]) -> tuple[dict[str, Any], list[str]]:
    """Normalize only a known array alias; never fill a missing judgment."""
    value = dict(raw)
    conversions: list[str] = []
    if "findings" not in value and "issues" in value:
        value["findings"] = value.pop("issues")
        conversions.append("issues->findings")
    if value.get("schema_version") != "compact_review_response_v1":
        raise ValueError("unknown reviewer response schema")
    checked, unchecked, findings = (value.get(key) for key in
                                    ("checked_areas", "unchecked_areas", "findings"))
    if not isinstance(checked, list) or not all(isinstance(x, str) for x in checked):
        raise ValueError("checked_areas must be an explicit array")
    if not isinstance(unchecked, list) or not isinstance(findings, list):
        raise ValueError("unchecked_areas and findings must be arrays")
    unchecked_ids = {item.get("area") for item in unchecked if isinstance(item, dict)
                     and isinstance(item.get("reason"), str) and item["reason"].strip()}
    if set(checked) & unchecked_ids or set(checked) | unchecked_ids != areas:
        raise ValueError("review scope is missing, overlapping, or invents an area")
    if len(checked) != len(set(checked)):
        raise ValueError("duplicate checked area")
    for finding in findings:
        if (not isinstance(finding, dict) or finding.get("area") not in areas
                or finding.get("severity") not in {"blocking", "minor", "editorial", "uncertainty"}
                or not all(isinstance(finding.get(key), str) and finding[key].strip()
                           for key in ("impact", "evidence", "action"))):
            raise ValueError("finding requires area, severity, impact, evidence, action")
    return value, conversions


def ingest(manifest: dict[str, Any], run_path: Path, role: str, request: Path,
           raw_path: Path, *, execution_id: str, model: str, root: Path = ROOT) -> dict[str, Any]:
    if role not in {"A", "B"} or not execution_id or not model:
        raise ValueError("role, execution_id, model are required")
    source = _json(request)
    snap = current(manifest, root)
    if source.get("role") != role or source.get("body_sha256") != snap["body_sha256"] or source.get("area_keys") != snap["areas"]:
        raise ValueError("request is stale or references another role/content")
    shared = _path(source, "snapshot_path", root)
    if (_sha(shared) != source.get("snapshot_sha256")
            or _json(shared).get("area_keys") != snap["areas"]):
        raise ValueError("shared request snapshot changed")
    if role == "B" and (source.get("source_inventory_sha256") != snap["inventory_sha256"]
                        or source.get("source_inventory_path") != manifest["inventory_path"]):
        # Metadata can change without changing content, but the request must
        # reflect the inventory actually inspected to preserve provenance.
        raise ValueError("source review request references another inventory edition")
    raw = _json(raw_path)
    derived, conversions = _normalize(raw, set(snap["areas"]))
    for receipt in manifest.get("review_receipts", []):
        if receipt.get("execution_id") == execution_id and receipt.get("role") != role:
            raise ValueError("A and B must use separate execution contexts")
    receipt = {"role": role, "execution_id": execution_id, "model": model,
               "recorded_at": _now(), "request_path": _relative(request, root),
               "request_sha256": _sha(request), "raw_response_path": _relative(raw_path, root),
               "raw_response_sha256": _sha(raw_path), "body_sha256": snap["body_sha256"],
               "area_keys": {a: snap["areas"][a] for a in derived["checked_areas"]},
               "checked_areas": derived["checked_areas"],
               "unchecked_areas": derived["unchecked_areas"],
               "findings": derived["findings"], "normalizations": conversions}
    manifest.setdefault("review_receipts", []).append(receipt)
    _save(run_path, manifest)
    return receipt


def _valid_receipts(manifest: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    result = []
    for row in manifest.get("review_receipts", []):
        try:
            raw_path, request_path = (_path(row, key, root)
                                      for key in ("raw_response_path", "request_path"))
            request = _json(request_path)
            normalized = _normalize(_json(raw_path), set(request["area_keys"]))[0]
            if _sha(raw_path) != row["raw_response_sha256"] or _sha(request_path) != row["request_sha256"]:
                continue
            if (row.get("role") not in {"A", "B"} or request.get("role") != row["role"]
                    or request.get("body_sha256") != row.get("body_sha256")
                    or not row.get("execution_id") or not row.get("model")
                    or row.get("execution_id") == manifest.get("generator_execution_id")
                    or normalized["findings"] != row["findings"]
                    or normalized["checked_areas"] != row["checked_areas"]
                    or row["area_keys"] != {area: request["area_keys"][area]
                                             for area in normalized["checked_areas"]}):
                continue
            result.append(row)
        except (OSError, KeyError, ValueError):
            continue
    return result


def status(manifest: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    snap = current(manifest, root)
    valid = _valid_receipts(manifest, root)
    executions = {role: {row["execution_id"] for row in valid if row["role"] == role}
                  for role in ("A", "B")}
    if executions["A"] & executions["B"]:
        valid = []
    coverage = {role: set() for role in ("A", "B")}
    findings: list[dict[str, Any]] = []
    for role in coverage:
        for area in snap["areas"]:
            for receipt in reversed(valid):
                if receipt["role"] == role and receipt["area_keys"].get(area) == snap["areas"][area]:
                    coverage[role].add(area)
                    findings += [{**row, "receipt_sha256": receipt["raw_response_sha256"]}
                                 for row in receipt["findings"] if row["area"] == area]
                    break
    # A historical migration is allowed only when source receipts, coverage,
    # independence and content bindings have been verified by the migrator.
    migration = manifest.get("migration")
    if isinstance(migration, dict) and _verify_migration(manifest, snap, root):
        for role in coverage:
            for area, key in migration.get("area_keys", {}).items():
                if snap["areas"].get(area) == key:
                    coverage[role].add(area)
    resolutions = manifest.get("resolutions", [])
    unresolved = []
    for finding in findings:
        if finding["severity"] == "editorial":
            continue
        identifier = dependencies.digest(finding)
        decision = next((row for row in resolutions if row.get("finding_sha256") == identifier), None)
        if finding["severity"] == "minor" and decision and decision.get("decision") == "decline" and decision.get("rationale"):
            continue
        unresolved.append({"finding_sha256": identifier, **finding})
    mechanical = validate_entry.validate_file(_path(manifest, "entry_path", root))
    mechanical.extend(research_errors(manifest, snap["body_sha256"], root))
    uncovered = {role: sorted(set(snap["areas"]) - checked) for role, checked in coverage.items()}
    ready = not (unresolved or mechanical or any(uncovered.values()) or snap["ambiguous"])
    effective_status = ("completed" if ready and manifest.get("status") == "completed"
                        and manifest.get("completed_body_sha256") == snap["body_sha256"]
                        else "review_ready" if ready else "in_progress")
    return {"workflow_contract_version": VERSION, "run_id": manifest["run_id"],
            "body_sha256": snap["body_sha256"], "status": effective_status,
            "uncovered": uncovered, "unresolved": unresolved,
            "mechanical_errors": mechanical, "ambiguous": snap["ambiguous"],
            "independent_review_executions": sorted({r["execution_id"] for r in valid}),
            "publish_gate": "pass" if ready else "blocked"}


def _verify_migration(manifest: dict[str, Any], snap: dict[str, Any], root: Path) -> bool:
    """Recheck legacy evidence each time; a self-declared verified flag is inert."""
    migration = manifest.get("migration")
    if not isinstance(migration, dict) or migration.get("to_version") != VERSION:
        return False
    try:
        old_run = _json(_path(migration, "old_run_path", root))
        recheck = _json(_path(migration, "recheck_manifest_path", root))
        revision = _json(_path(migration, "post_blind_revision_path", root))
        resolution = _json(_path(migration, "post_blind_resolution_path", root))
        if old_run.get("run_id") != manifest["run_id"] or old_run.get("status") != "in_progress":
            return False
        if recheck.get("current_body_sha256") != snap["body_sha256"]:
            return False
        if revision.get("output_body_sha256") != snap["body_sha256"]:
            return False
        if resolution.get("unresolved_issues") != []:
            return False
        if not {"f1", "f2"}.issubset({row.get("finding_id") for row in resolution.get("resolutions", [])
                                      if isinstance(row, dict) and row.get("disposition") == "adopted"}):
            return False
        if workflow_revision.validate_recheck_manifest(recheck, current_body_sha256=snap["body_sha256"]):
            return False
        rows = recheck["pass_results"]
        if {row["pass_id"] for row in rows} != set(workflow_revision.ALL_CHECKER_PASSES):
            return False
        agent_ids = set()
        for row in rows:
            path = _path(row, "raw_response_path", root)
            raw = _json(path)
            reviewer = raw.get("reviewer", {})
            if (_sha(path) != row.get("raw_response_sha256")
                    or row.get("schema_valid") is not True
                    or row.get("request_binding_valid") is not True
                    or row.get("reviewer_independent") is not True
                    or row.get("finding_count") != 0
                    or raw.get("pass_id") != row["pass_id"]
                    or (raw.get("findings", raw.get("frame_findings", [])) != [])
                    or reviewer.get("agent_id") != row.get("reviewer_agent_id")):
                return False
            agent_ids.add(reviewer["agent_id"])
        if len(agent_ids) != len(rows):
            return False
        return migration.get("area_keys") == snap["areas"]
    except (OSError, KeyError, ValueError, TypeError):
        return False


def validate_completed(manifest: dict[str, Any], *, root: Path = ROOT) -> list[str]:
    errors = []
    try:
        result = status(manifest, root=root)
        if result["publish_gate"] != "pass":
            errors.append("current content lacks valid independent coverage or has unresolved findings")
        if manifest.get("status") != "completed":
            errors.append("compact run is not completed")
        if manifest.get("completed_body_sha256") != result["body_sha256"]:
            errors.append("completed review refers to another body")
        entry = _path(manifest, "entry_path", root)
        front, _ = validate_entry._split_front_matter(entry.read_text(encoding="utf-8"))
        fields = validate_entry._front_matter_values(front or [])
        if fields.get("status") not in {"checked", "final"} or fields.get("checked") != "true":
            errors.append("published entry front matter does not match completed review")
        audit = root / "audits" / entry.parent.name / (entry.stem + ".json")
        value = _json(audit)
        if (value.get("schema_version") != "compact_audit_v1"
                or value.get("body_sha256") != result["body_sha256"]
                or value.get("run_id") != manifest["run_id"]):
            errors.append("canonical audit does not bind the completed run and body")
        record = _path(value, "run_path", root)
        if _json(record) != manifest:
            errors.append("canonical audit refers to another run")
        expected_reuse = reuse_ledger(manifest, root=root)
        ledger_path = _path(manifest, "reuse_ledger_path", root)
        if _json(ledger_path) != expected_reuse or _sha(ledger_path) != manifest.get("reuse_ledger_sha256"):
            errors.append("reuse ledger does not bind original reviews to current content")
    except (OSError, ValueError, KeyError) as exc:
        errors.append(str(exc))
    return errors


def validate_audit(audit_path: Path, *, root: Path = ROOT) -> list[str]:
    try:
        audit = _json(audit_path)
        if audit.get("schema_version") != "compact_audit_v1":
            return ["not a compact audit"]
        manifest = _json(_path(audit, "run_path", root))
        return validate_completed(manifest, root=root)
    except (OSError, KeyError, ValueError) as exc:
        return [str(exc)]


def reuse_ledger(manifest: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    snap = current(manifest, root)
    rows = []
    for receipt in _valid_receipts(manifest, root):
        if receipt.get("body_sha256") == snap["body_sha256"]:
            continue
        before = {"areas": receipt["area_keys"], "body_sha256": receipt["body_sha256"],
                  "ambiguous": False}
        for area, key in receipt["area_keys"].items():
            if snap["areas"].get(area) != key:
                continue
            rows.append({"role": receipt["role"],
                         **dependencies.reuse_receipt(receipt, before, snap, area)})
    return {"schema_version": "compact_reuse_ledger_v1", "current_body_sha256": snap["body_sha256"],
            "records": rows}


def finalize(manifest: dict[str, Any], run_path: Path, *, root: Path = ROOT) -> dict[str, Any]:
    if manifest.get("status") == "completed":
        errors = validate_completed(manifest, root=root)
        if errors:
            raise ValueError("completed run is stale: " + "; ".join(errors))
        entry = _path(manifest, "entry_path", root)
        return {"entry": manifest["entry_path"],
                "audit": f"audits/{entry.parent.name}/{entry.stem}.json",
                "run": _relative(run_path, root), "status": "completed"}
    gate = status(manifest, root=root)
    if gate["publish_gate"] != "pass":
        raise ValueError("publish gate is blocked: " + json.dumps(gate, ensure_ascii=False))
    entry = _path(manifest, "entry_path", root)
    text = entry.read_text(encoding="utf-8")
    front, _ = validate_entry._split_front_matter(text)
    if front is None:
        raise ValueError("entry front matter missing")
    text = re.sub(r"(?m)^status:.*$", "status: checked", text, count=1)
    text = re.sub(r"(?m)^checked:.*$", "checked: true", text, count=1)
    text = re.sub(r"(?m)^updated_at:.*$", "updated_at: " + _now()[:10], text, count=1)
    entry.write_text(text, encoding="utf-8")
    # A body-only binding makes these front matter changes safe without
    # silently changing the review evidence.
    if current(manifest, root)["body_sha256"] != gate["body_sha256"]:
        raise ValueError("entry body changed during finalization")
    queue_path = root / "queue/words.csv"
    if queue_path.exists():
        lines = queue_path.read_text(encoding="utf-8").splitlines(keepends=True)
        matching = [index for index, line in enumerate(lines)
                    if line.startswith(manifest["headword"] + ",")]
        if len(matching) != 1:
            raise ValueError("queue must contain exactly one existing headword row")
        index = matching[0]
        columns = lines[index].rstrip("\r\n").split(",", 10)
        if len(columns) != 11 or columns[4] != manifest["entry_path"]:
            raise ValueError("queue row does not match the reviewed entry")
        columns[2], columns[8], columns[9] = "checked", _now()[:10], "true"
        columns[10] = "compact review verified; original review records preserved"
        lines[index] = ",".join(columns) + "\n"
        temporary = queue_path.with_suffix(".csv.tmp")
        temporary.write_text("".join(lines), encoding="utf-8")
        temporary.replace(queue_path)
    manifest["status"] = "completed"
    manifest["stage"] = "publication_ready"
    manifest["completed_at"] = _now()
    manifest["completed_body_sha256"] = gate["body_sha256"]
    ledger = run_path.parent / run_path.stem / "compact/reuse_ledger.json"
    _save(ledger, reuse_ledger(manifest, root=root))
    manifest["reuse_ledger_path"] = _relative(ledger, root)
    manifest["reuse_ledger_sha256"] = _sha(ledger)
    _save(run_path, manifest)
    audit = root / "audits" / entry.parent.name / (entry.stem + ".json")
    _save(audit, {"schema_version": "compact_audit_v1",
                  "workflow_contract_version": VERSION, "entry_path": manifest["entry_path"],
                  "run_path": _relative(run_path, root), "run_id": manifest["run_id"],
                  "body_sha256": gate["body_sha256"], "decision": "pass",
                  "completed_at": manifest["completed_at"]})
    errors = validate_completed(manifest, root=root)
    if errors:
        raise ValueError("finalization validation failed: " + "; ".join(errors))
    return {"entry": manifest["entry_path"], "audit": _relative(audit, root),
            "run": _relative(run_path, root), "status": "completed"}


def migrate_legacy(old_run_path: Path, *, root: Path = ROOT) -> Path:
    """Preserve the original run and reviews, recording only a checked overlay."""
    old_run = _json(old_run_path)
    entry = _path(old_run, "entry_path", root)
    run_id, headword = old_run["run_id"], old_run["headword"]
    inventory = root / "audits/runs" / entry.parent.name / entry.stem / run_id / "source_inventory.json"
    manifest = {"workflow_contract_version": VERSION, "run_id": run_id,
                "headword": headword, "entry_path": _relative(entry, root),
                "inventory_path": _relative(inventory, root),
                "started_at": old_run["started_at"], "review_receipts": [],
                "resolutions": [], "status": "in_progress", "stage": "migration_review"}
    snap = current(manifest, root)
    cycle = inventory.parent
    manifest["migration"] = {
        "from_version": old_run.get("orchestrator", {}).get("workflow_contract_version", "legacy_seven_pass"),
        "to_version": VERSION, "reason": "replace repeated normal/blind audits with verified existing coverage",
        "old_run_path": _relative(old_run_path, root),
        "recheck_manifest_path": _relative(cycle / "checker_recheck_manifest.json", root),
        "post_blind_revision_path": _relative(cycle / "post_blind_revision_round26.json", root),
        "post_blind_resolution_path": _relative(cycle / "post_blind_resolution.json", root),
        "old_head_sha": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
        "area_keys": snap["areas"], "migrated_at": _now(),
    }
    if not _verify_migration(manifest, snap, root):
        raise ValueError("legacy raw reviews, adopted blind corrections, or current content did not verify")
    path = root / "audits/workflow_migrations" / headword / f"{run_id}.json"
    if path.exists():
        raise FileExistsError("migration already exists; resume without resetting history")
    _save(path, manifest)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compact independent dictionary review")
    parser.add_argument("--start", metavar="WORD")
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--migrate", type=Path)
    parser.add_argument("--entry", type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--request", choices=("A", "B"))
    parser.add_argument("--ingest", choices=("A", "B"))
    parser.add_argument("--request-path", type=Path)
    parser.add_argument("--raw", type=Path)
    parser.add_argument("--execution-id", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--finalize", action="store_true")
    args = parser.parse_args(argv)
    if args.migrate:
        print(migrate_legacy(args.migrate.resolve()).relative_to(ROOT))
        return 0
    if args.start:
        if not args.entry or not args.inventory:
            parser.error("--start needs --entry and --inventory")
        run = start(args.start, args.entry, args.inventory)
        print(run.relative_to(ROOT))
        return 0
    if not args.resume:
        parser.error("--resume is required")
    run = args.resume.resolve()
    manifest = _json(run)
    if args.request:
        print(prepare(manifest, run, args.request).relative_to(ROOT))
    elif args.ingest:
        if not args.raw or not args.request_path:
            parser.error("--ingest needs --raw and --request-path")
        print(json.dumps(ingest(manifest, run, args.ingest, args.request_path, args.raw,
                                execution_id=args.execution_id, model=args.model), ensure_ascii=False))
    elif args.finalize:
        print(json.dumps(finalize(manifest, run), ensure_ascii=False))
    else:
        print(json.dumps(status(manifest), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
