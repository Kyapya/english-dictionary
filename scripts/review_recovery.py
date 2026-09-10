"""Repairable review failures and provenance-preserving same-run recovery."""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import review_validation

POLICY_VERSION = "repairable_review_preflight_v2"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fingerprint(manifest: dict, *, stage: str, declared_model: str,
                reviewer_agent_id: str | None, repo_root: Path) -> str:
    """Keep the v1 digest compatible so legacy rejections cannot be replayed."""
    import run_word_v3
    import review_preflight
    pending = run_word_v3.next_stage_request(manifest)
    if not pending or pending["name"] != stage:
        raise ValueError("review correction must target the pending stage")
    cycle = (repo_root / pending["output_paths"][-1 if stage == "checker_passes" else 0]).parent
    return review_preflight.digest({
        "stage": stage, "model": declared_model, "agent": reviewer_agent_id or "",
        "files": {str(p.relative_to(cycle)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(cycle.rglob("*.json"))},
        "body": run_word_v3._entry_body(repo_root / manifest["entry_path"]),
    })


def record_validation_failure(manifest: dict, *, stage: str, error: BaseException,
                              input_fingerprint: str | None = None) -> dict:
    """Preserve rejection history without charging an actual execution attempt."""
    state = manifest.setdefault("review_preflight_failures", {"count": 0, "history": []})
    event = {"stage": stage, "error": str(error), "recorded_at": _now(),
             "fingerprint": input_fingerprint, "classification": "repairable_validation"}
    if isinstance(error, review_validation.PreflightError):
        event["diagnostics"] = copy.deepcopy(error.report)
    state["count"] += 1
    state["history"].append(event)
    manifest["review_correction"] = {**event, "status": "needs_correction"}
    manifest["review_preflight_policy"] = POLICY_VERSION
    # Keep the original proof on an old stopped run until validated recovery.
    if input_fingerprint and manifest.get("status") == "in_progress":
        manifest["last_rejected_review"] = {"fingerprint": input_fingerprint, "error": str(error)}
    return event


def resolve_validation_failure(manifest: dict, *, stage: str) -> None:
    current = manifest.get("review_correction")
    if isinstance(current, dict) and current.get("stage") == stage:
        current["status"] = "resolved"
        current["resolved_at"] = _now()


def is_recoverable_preflight_stop(manifest: dict, *, stage: str) -> bool:
    """Require positive evidence of the old preflight-to-stop bug.

    Unknown stops, research/final-review budgets and actual call failures without
    a matching dry-run rejection remain closed. No manual counter reset is used.
    """
    failures = manifest.get("review_ingest_failures")
    rejected = manifest.get("last_rejected_review")
    if not isinstance(failures, dict) or not isinstance(rejected, dict):
        return False
    count = failures.get("count")
    return (
        manifest.get("status") == "budget_exhausted"
        and isinstance(count, int) and not isinstance(count, bool) and count >= 3
        and failures.get("stage") == stage
        and manifest.get("stop_reason") == f"{stage} handoff ingestion failed {count} times"
        and isinstance(rejected.get("fingerprint"), str) and len(rejected["fingerprint"]) == 64
        and bool(rejected.get("error")) and rejected["error"] == failures.get("last_error")
    )


def recover_preflight_stop(manifest: dict, *, stage: str, declared_model: str,
                          reviewer_agent_id: str | None, repo_root: Path, ingest) -> bool:
    import entry_workflow_guard as guard
    import review_preflight
    if not is_recoverable_preflight_stop(manifest, stage=stage):
        return False
    current = fingerprint(manifest, stage=stage, declared_model=declared_model,
                          reviewer_agent_id=reviewer_agent_id, repo_root=repo_root)
    rejected = manifest.get("review_correction") or manifest["last_rejected_review"]
    if rejected.get("fingerprint") == current:
        raise ValueError("unchanged invalid response; correct the input/response before resuming the same run")
    trial = copy.deepcopy(manifest)
    trial["status"] = "in_progress"
    trial["stop_reason"] = ""
    if not guard.enforce_budget(trial):
        return False
    review_preflight.validate(trial, stage=stage, declared_model=declared_model,
                              reviewer_agent_id=reviewer_agent_id, repo_root=repo_root, ingest=ingest)
    manifest.setdefault("review_preflight_recoveries", []).append({
        "recovered_at": _now(), "stage": stage, "validated_fingerprint": current,
        "previous_stop_reason": manifest["stop_reason"],
        "previous_open_questions": list(manifest.get("open_questions", [])),
        "previous_ingest_failures": copy.deepcopy(manifest["review_ingest_failures"]),
        "original_rejection": copy.deepcopy(manifest["last_rejected_review"]),
    })
    manifest["status"] = "in_progress"
    manifest["stop_reason"] = ""
    # Identity, start time, completed stages, budget usage, counters and questions
    # stay unchanged. The ordinary ingestion path must still accept the result.
    return True


def bind_final_packet(packet: dict, packet_path: Path, *, refresh: bool = False) -> None:
    """Bind new/revised responses while leaving dispatched v1 packets readable."""
    import review_preflight
    previous = json.loads(packet_path.read_text(encoding="utf-8")) if packet_path.exists() else None
    if refresh or previous is None or previous.get("input_revision_id"):
        binding = review_preflight.digest({"body": packet["_output_metadata"]["input_body_sha256"],
                                           "inputs": packet["input_bindings"]})
        packet["input_revision_id"] = binding
        packet["response_template"]["input_revision_id"] = binding


def replace_final_packet(manifest: dict, packet_path: Path, packet: dict) -> None:
    """Archive a rejected final packet before an explicit same-body refresh.

    Called only after the new inputs pass all deterministic checks. The raw blind
    output, its seal and original checker snapshots are never touched.
    """
    cycle = packet_path.parent
    if manifest.get("status") != "in_progress" and not is_recoverable_preflight_stop(manifest, stage="final_review"):
        raise ValueError("this terminal run is not eligible for review-input correction")
    if (cycle / "final_review.json").exists():
        raise ValueError("cannot refresh an already ingested final review; use the existing revision workflow")
    if not packet_path.is_file():
        raise ValueError("there is no dispatched final-review packet to refresh")
    old_bytes = packet_path.read_bytes()
    old = json.loads(old_bytes)
    if old.get("_output_metadata", {}).get("input_body_sha256") != packet["_output_metadata"]["input_body_sha256"]:
        raise ValueError("body changed; use the existing revision/recheck workflow, not a packet refresh")
    if old.get("input_bindings") == packet.get("input_bindings"):
        raise ValueError("review inputs are unchanged; correct the response without refreshing its packet")
    old_hash = hashlib.sha256(old_bytes).hexdigest()
    archive = cycle / "review_packet_history" / "final_review" / old_hash
    files = (packet_path, cycle / "handoff/final_review.request.md",
             cycle / "handoff/final_review.response.json")
    for source in files:
        if not source.is_file():
            continue
        target = archive / source.relative_to(cycle)
        target.parent.mkdir(parents=True, exist_ok=True)
        content = source.read_bytes()
        if target.exists() and target.read_bytes() != content:
            raise ValueError("immutable packet archive differs: " + str(target))
        if not target.exists():
            target.write_bytes(content)
    # Every old byte is now preserved. Reject stale responses even after a crash.
    for source in files[1:]:
        if source.is_file():
            source.unlink()
    replacement = packet_path.with_suffix(".replacement.tmp")
    replacement.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    replacement.replace(packet_path)
    manifest.setdefault("review_packet_revisions", []).append({
        "stage": "final_review", "recorded_at": _now(),
        "old_packet_sha256": old_hash,
        "new_packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "archive": archive.relative_to(cycle).as_posix(),
        "input_revision_id": packet["input_revision_id"],
    })
