"""Replace invalid final-review evidence with a fresh independent response.

The article body and all sealed pre-final artifacts must be unchanged.  Old
canonical bytes are archived before replacement; the replacement is rehearsed
through the ordinary ingester and audit generator before any tracked file is
mutated.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import generate_audit_manifest as audit
import handoff_provenance
import review_preflight
import run_word_v3
import content_audit


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pending_final(manifest: dict) -> dict:
    trial = copy.deepcopy(manifest)
    stages = trial["orchestrator"]["stages"]
    index = next(i for i, row in enumerate(stages) if row["name"] == "final_review")
    trial["status"] = "in_progress"
    trial["stage"] = "final_review_pending"
    trial["orchestrator"]["review_response_protocol"] = handoff_provenance.SELF_ATTESTED_PROTOCOL
    state = trial["orchestrator_state"]
    state["next_stage_index"] = index
    state["completed_stages"] = [row["name"] for row in stages[:index]]
    state["stage_outputs"] = {
        key: value for key, value in state.get("stage_outputs", {}).items()
        if key in state["completed_stages"]
    }
    return trial


def _copy_trial(root: Path, manifest: dict, packet: Path, response: Path,
                destination: Path) -> tuple[Path, Path, Path]:
    entry = root / manifest["entry_path"]
    request = run_word_v3.next_stage_request(_pending_final(manifest))
    assert request is not None
    cycle = (root / request["output_paths"][0]).parent
    shutil.copytree(root / "prompts", destination / "prompts")
    trial_cycle = destination / cycle.relative_to(root)
    shutil.copytree(cycle, trial_cycle)
    trial_entry = destination / entry.relative_to(root)
    trial_entry.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(entry, trial_entry)
    (destination / "audits").mkdir(exist_ok=True)
    for name in ("escaped_defect_taxonomy.json", "review_invalidations.json"):
        shutil.copy2(root / "audits" / name, destination / "audits" / name)
    shutil.copy2(packet, trial_cycle / "final_review.request.json")
    trial_response = trial_cycle / "handoff" / "final_review.response.json"
    trial_response.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(response, trial_response)
    return trial_entry, trial_cycle, trial_response


def repair(root: Path, manifest_path: Path, packet: Path, response: Path) -> dict:
    root = root.resolve()
    manifest_path = manifest_path.resolve()
    packet = packet.resolve()
    response = response.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "completed":
        raise ValueError("final-review evidence repair requires a completed run")
    reviewer = handoff_provenance.normalize_source_reviewer(
        json.loads(response.read_text(encoding="utf-8")).get("reviewer")
    )
    pending = _pending_final(manifest)
    request = run_word_v3.next_stage_request(pending)
    assert request is not None
    cycle = (root / request["output_paths"][0]).parent
    entry = root / manifest["entry_path"]
    supplied_packet = json.loads(packet.read_text(encoding="utf-8"))
    review_preflight.check_bindings(supplied_packet, entry, cycle)
    if supplied_packet.get("_output_metadata", {}).get("input_body_sha256") != audit.body_sha256(entry):
        raise ValueError("repair packet does not bind the current article body")

    # Rehearse the exact replacement in isolation first.
    with tempfile.TemporaryDirectory(prefix="final-review-evidence-repair-") as directory:
        trial_root = Path(directory)
        trial_entry, trial_cycle, _ = _copy_trial(
            root, manifest, packet, response, trial_root
        )
        run_word_v3.ingest_handoff_review(
            pending,
            stage="final_review",
            declared_model=reviewer["declared_model"],
            reviewer_agent_id=reviewer["agent_id"],
            repo_root=trial_root,
        )
        audit.generate_manifest(trial_entry, trial_cycle, repo_root=trial_root)

    canonical = {
        "request": cycle / "final_review.request.json",
        "response": cycle / "handoff" / "final_review.response.json",
        "output": cycle / "final_review.json",
    }
    old_hashes = {key: _sha(path) for key, path in canonical.items()}
    archive = cycle / "review_evidence_history" / "final_review" / old_hashes["output"]
    for key, source in canonical.items():
        target = archive / (key + ".json")
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise ValueError("immutable review-evidence archive differs: " + str(target))
        if not target.exists():
            target.write_bytes(source.read_bytes())

    shutil.copy2(packet, canonical["request"])
    shutil.copy2(response, canonical["response"])
    run_word_v3.ingest_handoff_review(
        pending,
        stage="final_review",
        declared_model=reviewer["declared_model"],
        reviewer_agent_id=reviewer["agent_id"],
        repo_root=root,
    )
    audit_value = audit.generate_manifest(entry, cycle, repo_root=root)
    audit_path = content_audit.audit_path_for_entry(entry, root)
    audit_path.write_text(
        json.dumps(audit_value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    recorded_at = _now()
    repair_record = {
        "schema_version": "final_review_evidence_repair_v1",
        "recorded_at": recorded_at,
        "reason": "C1_synthetic_review",
        "article_body_sha256": audit.body_sha256(entry),
        "old_artifacts": {
            key: {"sha256": value, "archive": (archive / (key + ".json")).relative_to(root).as_posix()}
            for key, value in old_hashes.items()
        },
        "replacement": {
            "request_sha256": _sha(canonical["request"]),
            "response_sha256": _sha(canonical["response"]),
            "output_sha256": _sha(canonical["output"]),
            "reviewer_agent_id": reviewer["agent_id"],
            "declared_model": reviewer["declared_model"],
        },
    }
    record_path = archive / "repair.json"
    record_path.write_text(json.dumps(repair_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["orchestrator"]["review_response_protocol"] = handoff_provenance.SELF_ATTESTED_PROTOCOL
    manifest.setdefault("review_evidence_repairs", []).append({
        "recorded_at": recorded_at,
        "stage": "final_review",
        "record": record_path.relative_to(root).as_posix(),
        "replacement_output_sha256": repair_record["replacement"]["output_sha256"],
    })
    metrics = manifest.get("metrics")
    if isinstance(metrics, dict):
        metrics["total_duration_source"] = "workflow_wall_elapsed"
        metrics["measurement_notice"] = (
            "This legacy run recorded placeholder per-stage durations before "
            "duration_source was enforced; those rows are not performance data."
        )
        for collection in ("stages", "checker_passes", "process_rules"):
            for row in metrics.get(collection, []):
                if isinstance(row, dict) and "duration_source" not in row:
                    row["duration_source"] = "legacy_unmeasured"
    run_word_v3.process_stage_learning(
        manifest,
        stage="post_blind_resolution",
        output_paths=manifest["orchestrator_state"]["stage_outputs"].get(
            "post_blind_resolution", []
        ),
        repo_root=root,
    )
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "audit": audit_path.relative_to(root).as_posix(),
        "record": record_path.relative_to(root).as_posix(),
        "reviewer": reviewer,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(repair(args.root, args.manifest, args.packet, args.response), ensure_ascii=False))


if __name__ == "__main__":
    main()
