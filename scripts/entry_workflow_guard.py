from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import review_liveness
from slugify import slugify


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "entry_workflow_run_v1"
RUNS_ROOT = REPO_ROOT / "audits" / "workflow_runs"

PROFILES = {
    "standard": {
        "max_elapsed_minutes": 60,
        "max_pre_draft_minutes": 20,
        "max_research_queries": 12,
        "max_candidate_pages": 18,
        "max_heartbeat_gap_minutes": 10,
    },
    "extended": {
        "max_elapsed_minutes": 90,
        "max_pre_draft_minutes": 30,
        "max_research_queries": 18,
        "max_candidate_pages": 26,
        "max_heartbeat_gap_minutes": 10,
    },
}

STAGES = (
    "preflight",
    "preflight_pushed",
    "draft_saved",
    "source_inventory_complete",
    "normal_review_complete",
    "cold_review_complete",
    "blind_seal_complete",
    "final_review_complete",
    "completed",
)

TERMINAL_STATUSES = {"budget_exhausted", "completed"}
COST_SCHEMA_VERSION = "workflow_cost_v1"
MAX_REVIEW_INGEST_FAILURES = 3


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_time(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} is required")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be ISO-8601")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label} must include a timezone")
        return None
    return parsed


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("workflow run must be a JSON object")
    return value


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _resolve_run_argument(raw: str) -> Path:
    path = (REPO_ROOT / raw).resolve()
    try:
        path.relative_to(RUNS_ROOT.resolve())
    except ValueError as exc:
        raise ValueError("workflow run path must be under audits/workflow_runs") from exc
    return path


def _default_run_id(now: datetime) -> str:
    stamp = now.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid.uuid4().hex[:8]}"


def run_path(headword: str, run_id: str) -> Path:
    return RUNS_ROOT / slugify(headword) / f"{run_id}.json"


def new_manifest(
    *,
    headword: str,
    entry_path: str,
    branch: str,
    base_sha: str,
    profile: str = "standard",
    profile_reason: str = "",
    run_id: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    started = now or _now()
    if profile not in PROFILES:
        raise ValueError("profile must be standard or extended")
    if profile == "extended" and not profile_reason.strip():
        raise ValueError("extended profile requires profile_reason")
    limits = dict(PROFILES[profile])
    resolved_run_id = run_id or _default_run_id(started)
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": resolved_run_id,
        "headword": headword,
        "entry_path": entry_path,
        "branch": branch,
        "base_sha": base_sha,
        "profile": profile,
        "profile_reason": profile_reason or "bounded default profile",
        "limits": limits,
        "usage": {"research_queries": 0, "candidate_pages": 0},
        "status": "in_progress",
        "stage": "preflight",
        "started_at": _format_time(started),
        "deadline_at": _format_time(started + timedelta(minutes=limits["max_elapsed_minutes"])),
        "pre_draft_deadline_at": _format_time(
            started + timedelta(minutes=limits["max_pre_draft_minutes"])
        ),
        "last_heartbeat_at": _format_time(started),
        "remote_checkpoint": {
            "confirmed": False,
            "confirmed_at": None,
            "commit_sha": "",
        },
        "stage_history": [
            {"stage": "preflight", "recorded_at": _format_time(started), "notes": "run initialized"}
        ],
        "stop_reason": "",
        "open_questions": [],
    }


def validate_manifest(manifest: dict[str, Any], *, merge_ready: bool = False) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    for key in ("run_id", "headword", "entry_path", "branch", "base_sha"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            errors.append(f"{key} is required")
    profile = manifest.get("profile")
    if profile not in PROFILES:
        errors.append("profile must be standard or extended")
    elif profile == "extended" and not str(manifest.get("profile_reason", "")).strip():
        errors.append("extended profile requires profile_reason")
    limits = manifest.get("limits")
    if not isinstance(limits, dict):
        errors.append("limits must be an object")
    elif profile in PROFILES:
        for key, expected in PROFILES[profile].items():
            if limits.get(key) != expected:
                errors.append(f"limits.{key} must equal {expected} for {profile}")
    usage = manifest.get("usage")
    if not isinstance(usage, dict):
        errors.append("usage must be an object")
    elif isinstance(limits, dict):
        for used_key, limit_key in (
            ("research_queries", "max_research_queries"),
            ("candidate_pages", "max_candidate_pages"),
        ):
            value = usage.get(used_key)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"usage.{used_key} must be a non-negative integer")
            elif isinstance(limits.get(limit_key), int) and value > limits[limit_key]:
                errors.append(f"usage.{used_key} exceeds {limit_key}")
    status = manifest.get("status")
    if status not in {"in_progress", *TERMINAL_STATUSES}:
        errors.append("status is invalid")
    stage = manifest.get("stage")
    if stage not in STAGES:
        errors.append("stage is invalid")
    started = _parse_time(manifest.get("started_at"), "started_at", errors)
    deadline = _parse_time(manifest.get("deadline_at"), "deadline_at", errors)
    pre_draft_deadline = _parse_time(
        manifest.get("pre_draft_deadline_at"), "pre_draft_deadline_at", errors
    )
    heartbeat = _parse_time(manifest.get("last_heartbeat_at"), "last_heartbeat_at", errors)
    if started and deadline and deadline <= started:
        errors.append("deadline_at must be after started_at")
    if started and pre_draft_deadline and pre_draft_deadline <= started:
        errors.append("pre_draft_deadline_at must be after started_at")
    if deadline and pre_draft_deadline and pre_draft_deadline > deadline:
        errors.append("pre_draft_deadline_at must not exceed deadline_at")
    if started and deadline and profile in PROFILES:
        expected = started + timedelta(minutes=PROFILES[profile]["max_elapsed_minutes"])
        if deadline != expected:
            errors.append("deadline_at must match the fixed profile runtime limit")
    if started and pre_draft_deadline and profile in PROFILES:
        expected = started + timedelta(minutes=PROFILES[profile]["max_pre_draft_minutes"])
        if pre_draft_deadline != expected:
            errors.append("pre_draft_deadline_at must match the fixed profile draft limit")
    if started and heartbeat and heartbeat < started:
        errors.append("last_heartbeat_at must not precede started_at")
    remote = manifest.get("remote_checkpoint")
    if not isinstance(remote, dict):
        errors.append("remote_checkpoint must be an object")
    else:
        confirmed = remote.get("confirmed") is True
        if stage in STAGES[1:] and not confirmed:
            errors.append("remote checkpoint must be confirmed before work advances")
        if confirmed:
            if not str(remote.get("commit_sha", "")).strip():
                errors.append("remote_checkpoint.commit_sha is required when confirmed")
            _parse_time(remote.get("confirmed_at"), "remote_checkpoint.confirmed_at", errors)
    history = manifest.get("stage_history")
    if not isinstance(history, list) or not history:
        errors.append("stage_history must be a non-empty array")
    else:
        previous = -1
        for index, item in enumerate(history):
            if not isinstance(item, dict) or item.get("stage") not in STAGES:
                errors.append(f"stage_history[{index}] is invalid")
                continue
            rank = STAGES.index(item["stage"])
            if rank < previous or rank > previous + 1:
                errors.append("stage_history must advance one stage at a time")
            previous = rank
            _parse_time(item.get("recorded_at"), f"stage_history[{index}].recorded_at", errors)
        if history and isinstance(history[-1], dict) and history[-1].get("stage") != stage:
            errors.append("stage must equal the last stage_history item")
    failures = manifest.get("review_ingest_failures")
    if failures is not None:
        if not isinstance(failures, dict):
            errors.append("review_ingest_failures must be an object")
        else:
            count = failures.get("count")
            if not isinstance(failures.get("stage"), str) or not failures["stage"].strip():
                errors.append("review_ingest_failures.stage is required")
            if (
                not isinstance(count, int)
                or isinstance(count, bool)
                or count < 1
                or count > MAX_REVIEW_INGEST_FAILURES
            ):
                errors.append(
                    "review_ingest_failures.count must be between 1 and "
                    f"{MAX_REVIEW_INGEST_FAILURES}"
                )
            _parse_time(
                failures.get("last_failed_at"),
                "review_ingest_failures.last_failed_at",
                errors,
            )
    if status == "budget_exhausted":
        if not str(manifest.get("stop_reason", "")).strip():
            errors.append("budget_exhausted run requires stop_reason")
        if not isinstance(manifest.get("open_questions"), list):
            errors.append("budget_exhausted run requires open_questions")
    if status == "completed" and stage != "completed":
        errors.append("completed run must be at completed stage")
    if stage == "completed" and status != "completed":
        errors.append("completed stage requires completed status")
    if merge_ready and status != "completed":
        errors.append("merge-ready validation requires completed workflow runs")
    orchestrator = manifest.get("orchestrator")
    metrics = manifest.get("metrics")
    if isinstance(orchestrator, dict) and orchestrator.get("orchestrator_version") in {
        "run_word_v2",
        "run_word_v3",
    }:
        if not isinstance(metrics, dict):
            errors.append("run_word_v2+ workflow requires metrics")
        else:
            errors.extend(_validate_cost_metrics(metrics, orchestrator, manifest, merge_ready))
        state = manifest.get("orchestrator_state")
        if not isinstance(state, dict):
            errors.append("run_word_v2+ workflow requires orchestrator_state")
        else:
            planned = [item.get("name") for item in orchestrator.get("stages", [])]
            completed = state.get("completed_stages")
            next_index = state.get("next_stage_index")
            if not isinstance(completed, list) or completed != planned[: len(completed)]:
                errors.append("orchestrator_state.completed_stages must be a plan prefix")
            if not isinstance(next_index, int) or next_index != len(completed or []):
                errors.append("orchestrator_state.next_stage_index is inconsistent")
            if merge_ready and completed != planned:
                errors.append("merge-ready orchestrator must complete every planned stage")
    return errors


def _validate_cost_metrics(
    metrics: dict[str, Any],
    orchestrator: dict[str, Any],
    manifest: dict[str, Any],
    merge_ready: bool,
) -> list[str]:
    errors: list[str] = []
    if metrics.get("schema_version") != COST_SCHEMA_VERSION:
        errors.append(f"metrics.schema_version must be {COST_SCHEMA_VERSION}")
    for key in ("total_cycles", "total_revisions"):
        value = metrics.get(key)
        minimum = 1 if key == "total_cycles" else 0
        if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
            errors.append(f"metrics.{key} must be an integer >= {minimum}")
    duration = metrics.get("total_duration_seconds")
    if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration < 0:
        errors.append("metrics.total_duration_seconds must be non-negative")

    expected_ids = {
        "stages": [item.get("name") for item in orchestrator.get("stages", [])],
        "checker_passes": [
            item.get("id") for item in orchestrator.get("checker_passes", [])
        ],
    }
    revision_sum = 0
    for collection in ("stages", "checker_passes", "process_rules"):
        rows = metrics.get(collection)
        if not isinstance(rows, list):
            errors.append(f"metrics.{collection} must be a list")
            continue
        ids = [item.get("id") for item in rows if isinstance(item, dict)]
        if len(ids) != len(rows) or len(ids) != len(set(ids)):
            errors.append(f"metrics.{collection} ids must be unique non-empty values")
        if collection in expected_ids and ids != expected_ids[collection]:
            errors.append(f"metrics.{collection} must match the orchestrator plan")
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            for key in ("instruction_bytes", "input_bytes", "defects_detected"):
                value = row.get(key)
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    errors.append(f"metrics.{collection}[{index}].{key} must be non-negative")
            row_duration = row.get("duration_seconds")
            if (
                not isinstance(row_duration, (int, float))
                or isinstance(row_duration, bool)
                or row_duration < 0
            ):
                errors.append(
                    f"metrics.{collection}[{index}].duration_seconds must be non-negative"
                )
            if not isinstance(row.get("completed"), bool):
                errors.append(f"metrics.{collection}[{index}].completed must be boolean")
            if collection == "stages":
                revision_count = row.get("revision_count")
                if (
                    not isinstance(revision_count, int)
                    or isinstance(revision_count, bool)
                    or revision_count < 0
                ):
                    errors.append(
                        f"metrics.stages[{index}].revision_count must be non-negative"
                    )
                else:
                    revision_sum += revision_count
        if merge_ready and any(
            not isinstance(item, dict) or item.get("completed") is not True
            for item in rows
        ):
            errors.append(f"merge-ready metrics require all {collection} rows completed")
    if metrics.get("total_revisions") != revision_sum:
        errors.append("metrics.total_revisions must equal the stage revision_count sum")
    completed_at = metrics.get("completed_at")
    if manifest.get("status") == "completed":
        _parse_time(completed_at, "metrics.completed_at", errors)
        if not isinstance(duration, (int, float)) or duration <= 0:
            errors.append("completed workflow requires positive total_duration_seconds")
    elif completed_at not in (None, ""):
        errors.append("incomplete workflow metrics.completed_at must be empty")
    return errors


def _stop(
    manifest: dict[str, Any], *, reason: str, now: datetime, open_questions: list[str] | None = None
) -> None:
    manifest["status"] = "budget_exhausted"
    manifest["stop_reason"] = reason
    manifest["open_questions"] = list(open_questions or [])
    manifest["last_heartbeat_at"] = _format_time(now)


def enforce_budget(manifest: dict[str, Any], *, now: datetime | None = None) -> bool:
    current = now or _now()
    if manifest.get("status") in TERMINAL_STATUSES:
        return manifest.get("status") == "completed"
    errors: list[str] = []
    deadline = _parse_time(manifest.get("deadline_at"), "deadline_at", errors)
    pre_draft_deadline = _parse_time(
        manifest.get("pre_draft_deadline_at"), "pre_draft_deadline_at", errors
    )
    heartbeat = _parse_time(manifest.get("last_heartbeat_at"), "last_heartbeat_at", errors)
    if errors:
        raise ValueError("; ".join(errors))
    assert deadline and pre_draft_deadline and heartbeat
    stage = manifest.get("stage")
    if current > deadline and stage in {"preflight", "preflight_pushed"}:
        _stop(manifest, reason="overall elapsed-time budget exhausted", now=current)
        return False
    if stage in {"preflight", "preflight_pushed"} and current > pre_draft_deadline:
        _stop(manifest, reason="pre-draft elapsed-time budget exhausted", now=current)
        return False
    max_gap = manifest["limits"]["max_heartbeat_gap_minutes"]
    if current - heartbeat > timedelta(minutes=max_gap):
        _stop(manifest, reason="heartbeat gap budget exhausted", now=current)
        return False
    return True


def clear_review_ingest_failures(manifest: dict[str, Any]) -> None:
    """Drop the failure streak after a review stage is ingested successfully."""
    manifest.pop("review_ingest_failures", None)


def record_review_ingest_failure(
    manifest: dict[str, Any],
    *,
    stage: str,
    error: str,
    now: datetime | None = None,
) -> bool:
    """Charge a failed review ingestion to the budget and stop a retry loop.

    The heartbeat is deliberately not refreshed: a failed ingestion is not
    progress, so elapsed time and the heartbeat gap keep running against the
    run. Returns False once the run is stopped, either because a budget is
    exhausted or because the same stage failed MAX_REVIEW_INGEST_FAILURES times.
    """
    current = now or _now()
    if manifest.get("status") in TERMINAL_STATUSES:
        return False
    failures = manifest.get("review_ingest_failures")
    if not isinstance(failures, dict) or failures.get("stage") != stage:
        failures = {"stage": stage, "count": 0, "last_error": "", "last_failed_at": ""}
    count = failures.get("count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        count = 0
    failures = {
        "stage": stage,
        "count": count + 1,
        "last_error": error.strip(),
        "last_failed_at": _format_time(current),
    }
    manifest["review_ingest_failures"] = failures
    if not enforce_budget(manifest, now=current):
        return False
    if failures["count"] >= MAX_REVIEW_INGEST_FAILURES:
        _stop(
            manifest,
            reason=f"{stage} handoff ingestion failed {failures['count']} times",
            now=current,
            open_questions=[
                f"last {stage} ingestion error: {failures['last_error']}",
                "fix the handoff response contract before resuming this run",
            ],
        )
        return False
    return True


def record_research(
    manifest: dict[str, Any], *, queries: int, candidate_pages: int, now: datetime | None = None
) -> bool:
    current = now or _now()
    if manifest.get("stage") not in {"preflight_pushed", "draft_saved"}:
        raise ValueError("research can start only after preflight_pushed and before inventory closes")
    if not manifest.get("remote_checkpoint", {}).get("confirmed"):
        raise ValueError("remote checkpoint must be confirmed before research")
    if queries < 0 or candidate_pages < 0 or queries + candidate_pages < 1:
        raise ValueError("record at least one non-negative research action")
    if not enforce_budget(manifest, now=current):
        return False
    next_queries = manifest["usage"]["research_queries"] + queries
    next_pages = manifest["usage"]["candidate_pages"] + candidate_pages
    if next_queries > manifest["limits"]["max_research_queries"]:
        _stop(manifest, reason="research query budget exhausted", now=current)
        return False
    if next_pages > manifest["limits"]["max_candidate_pages"]:
        _stop(manifest, reason="candidate page budget exhausted", now=current)
        return False
    manifest["usage"]["research_queries"] = next_queries
    manifest["usage"]["candidate_pages"] = next_pages
    manifest["last_heartbeat_at"] = _format_time(current)
    return True


def advance_stage(
    manifest: dict[str, Any], *, stage: str, notes: str = "", now: datetime | None = None
) -> bool:
    current = now or _now()
    if stage not in STAGES:
        raise ValueError(f"unknown stage: {stage}")
    if manifest.get("status") in TERMINAL_STATUSES:
        raise ValueError("terminal workflow run cannot advance")
    current_stage = manifest.get("stage")
    expected_index = STAGES.index(current_stage) + 1
    if expected_index >= len(STAGES) or STAGES[expected_index] != stage:
        raise ValueError(f"next stage after {current_stage} must be {STAGES[expected_index]}")
    if stage != "preflight_pushed" and not manifest.get("remote_checkpoint", {}).get("confirmed"):
        raise ValueError("remote checkpoint must be confirmed before work advances")
    budget_ok = enforce_budget(manifest, now=current)
    if not budget_ok and stage != "draft_saved":
        return False
    manifest["stage"] = stage
    manifest["stage_history"].append(
        {"stage": stage, "recorded_at": _format_time(current), "notes": notes}
    )
    manifest["last_heartbeat_at"] = _format_time(current)
    if not budget_ok:
        errors: list[str] = []
        pre_draft_deadline = _parse_time(
            manifest.get("pre_draft_deadline_at"), "pre_draft_deadline_at", errors
        )
        if errors:
            raise ValueError("; ".join(errors))
        assert pre_draft_deadline
        if current > pre_draft_deadline:
            manifest["stop_reason"] = "draft saved after pre-draft budget expired"
        return False
    if stage == "completed":
        manifest["status"] = "completed"
        manifest["stop_reason"] = ""
        manifest["open_questions"] = []
        return True
    if stage == "draft_saved":
        errors: list[str] = []
        pre_draft_deadline = _parse_time(
            manifest.get("pre_draft_deadline_at"), "pre_draft_deadline_at", errors
        )
        if errors:
            raise ValueError("; ".join(errors))
        assert pre_draft_deadline
        if current > pre_draft_deadline:
            _stop(manifest, reason="draft saved after pre-draft budget expired", now=current)
            return False
    return enforce_budget(manifest, now=current)


def confirm_remote_checkpoint(
    manifest: dict[str, Any],
    *,
    manifest_path: Path,
    commit_sha: str,
    repo_root: Path = REPO_ROOT,
    remote: str = "origin",
    now: datetime | None = None,
) -> bool:
    if manifest.get("stage") != "preflight":
        raise ValueError("remote checkpoint can be confirmed only from preflight")
    relative_path = manifest_path.resolve().relative_to(repo_root.resolve()).as_posix()
    committed = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{commit_sha}:{relative_path}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    committed_manifest = json.loads(committed.stdout)
    if not isinstance(committed_manifest, dict):
        raise ValueError("remote checkpoint manifest must be a JSON object")
    local_errors = validate_manifest(manifest)
    remote_errors = validate_manifest(committed_manifest)
    if local_errors:
        raise ValueError(f"local preflight manifest is invalid: {'; '.join(local_errors)}")
    if remote_errors:
        raise ValueError(f"remote preflight manifest is invalid: {'; '.join(remote_errors)}")
    if committed_manifest != manifest:
        raise ValueError("remote checkpoint manifest does not match the local preflight record")
    completed = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "ls-remote",
            "--heads",
            remote,
            f"refs/heads/{manifest['branch']}",
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    remote_shas = {line.split()[0] for line in completed.stdout.splitlines() if line.split()}
    if commit_sha not in remote_shas:
        raise ValueError("remote branch does not point to the checkpoint commit")
    current = now or _now()
    manifest["remote_checkpoint"] = {
        "confirmed": True,
        "confirmed_at": _format_time(current),
        "commit_sha": commit_sha,
    }
    return advance_stage(
        manifest,
        stage="preflight_pushed",
        notes="remote start checkpoint verified",
        now=current,
    )


def _changed_files(base: str, head: str) -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _git_file_at(
    ref: str, relative: str, *, repo_root: Path = REPO_ROOT
) -> bytes | None:
    completed = subprocess.run(
        ["git", "show", f"{ref}:{relative}"],
        cwd=repo_root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout if completed.returncode == 0 else None


def _entry_front_and_body(raw: bytes) -> tuple[dict[str, str], str] | None:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    front: dict[str, str] = {}
    closing: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing = index
            break
        if ":" in line:
            key, value = line.split(":", 1)
            front[key.strip()] = value.strip().strip('"')
    if closing is None:
        return None
    return front, "\n".join(lines[closing + 1 :])


def _is_registered_review_demotion(
    entry: str,
    *,
    base: str,
    head: str,
    changed: set[str],
    repo_root: Path = REPO_ROOT,
) -> bool:
    """Allow only a body-preserving demotion tied to a registered invalid run."""
    parts = Path(entry).parts
    if len(parts) != 3 or parts[0] != "entries":
        return False
    audit_relative = f"audits/{parts[1]}/{Path(parts[2]).stem}.json"
    registry_relative = "audits/review_invalidations.json"
    if audit_relative not in changed or registry_relative not in changed:
        return False
    base_raw = _git_file_at(base, entry, repo_root=repo_root)
    head_raw = _git_file_at(head, entry, repo_root=repo_root)
    if base_raw is None or head_raw is None:
        return False
    base_entry = _entry_front_and_body(base_raw)
    head_entry = _entry_front_and_body(head_raw)
    if base_entry is None or head_entry is None:
        return False
    base_front, base_body = base_entry
    head_front, head_body = head_entry
    if base_body != head_body:
        return False
    if base_front.get("status") not in {"checked", "final"}:
        return False
    if base_front.get("checked") != "true" or head_front.get("checked") != "false":
        return False
    ignored = {"status", "checked", "updated_at"}
    if {key: value for key, value in base_front.items() if key not in ignored} != {
        key: value for key, value in head_front.items() if key not in ignored
    }:
        return False
    audit_raw = _git_file_at(head, audit_relative, repo_root=repo_root)
    registry_raw = _git_file_at(head, registry_relative, repo_root=repo_root)
    if audit_raw is None or registry_raw is None:
        return False
    try:
        audit = json.loads(audit_raw)
        registry = json.loads(registry_raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return False
    if not isinstance(audit, dict) or not isinstance(registry, dict):
        return False
    invalidated_by = audit.get("invalidated_by")
    if not isinstance(invalidated_by, list) or not invalidated_by:
        return False
    if head_front.get("status") != review_liveness.required_pending_status(
        invalidated_by
    ):
        return False
    cycle_id = audit.get("cycle_id")
    return any(
        isinstance(item, dict)
        and item.get("status") == "invalidated_run"
        and item.get("entry_path") == entry
        and item.get("run_id") == cycle_id
        and set(item.get("invalidated_by", [])) == set(invalidated_by)
        for item in registry.get("invalidations", [])
    )


def _all_run_paths() -> list[Path]:
    return sorted(RUNS_ROOT.glob("*/*.json")) if RUNS_ROOT.exists() else []


def _validate_paths(paths: list[Path], *, merge_ready: bool) -> int:
    failed = False
    for path in paths:
        try:
            manifest = _read(path)
            errors = validate_manifest(manifest, merge_ready=merge_ready)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors = [str(exc)]
        if errors:
            failed = True
            print(f"FAIL {path.relative_to(REPO_ROOT)}", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        else:
            print(f"PASS {path.relative_to(REPO_ROOT)}")
    return 1 if failed else 0


def command_start(args: argparse.Namespace) -> int:
    try:
        manifest = new_manifest(
            headword=args.headword,
            entry_path=args.entry,
            branch=args.branch,
            base_sha=args.base_sha,
            profile=args.profile,
            profile_reason=args.reason or "",
            run_id=args.run_id,
        )
    except ValueError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    path = run_path(args.headword, manifest["run_id"])
    if path.exists():
        print(f"FAIL {path.relative_to(REPO_ROOT)} already exists", file=sys.stderr)
        return 1
    _write(path, manifest)
    print(path.relative_to(REPO_ROOT))
    return 0


def command_confirm_remote(args: argparse.Namespace) -> int:
    try:
        path = _resolve_run_argument(args.run)
    except ValueError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    try:
        manifest = _read(path)
        ok = confirm_remote_checkpoint(
            manifest,
            manifest_path=path,
            commit_sha=args.commit_sha,
            remote=args.remote,
        )
        _write(path, manifest)
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    if not ok:
        print(f"STOPPED {manifest['stop_reason']}", file=sys.stderr)
        return 2
    print(f"CONFIRMED {path.relative_to(REPO_ROOT)}")
    return 0


def command_heartbeat(args: argparse.Namespace) -> int:
    try:
        path = _resolve_run_argument(args.run)
    except ValueError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    try:
        manifest = _read(path)
        ok = enforce_budget(manifest)
        if ok:
            manifest["last_heartbeat_at"] = _format_time(_now())
        _write(path, manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    if not ok:
        print(f"STOPPED {manifest['stop_reason']}", file=sys.stderr)
        return 2
    print(f"OK {manifest['stage']}")
    return 0


def command_record_research(args: argparse.Namespace) -> int:
    try:
        path = _resolve_run_argument(args.run)
    except ValueError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    try:
        manifest = _read(path)
        ok = record_research(
            manifest, queries=args.queries, candidate_pages=args.candidate_pages
        )
        _write(path, manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    if not ok:
        print(f"STOPPED {manifest['stop_reason']}", file=sys.stderr)
        return 2
    print(json.dumps(manifest["usage"], ensure_ascii=False))
    return 0


def command_checkpoint(args: argparse.Namespace) -> int:
    try:
        path = _resolve_run_argument(args.run)
    except ValueError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    try:
        manifest = _read(path)
        ok = advance_stage(manifest, stage=args.stage, notes=args.notes or "")
        _write(path, manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    if not ok:
        print(f"STOPPED {manifest['stop_reason']}", file=sys.stderr)
        return 2
    print(f"CHECKPOINT {args.stage}")
    return 0


def command_stop(args: argparse.Namespace) -> int:
    try:
        path = _resolve_run_argument(args.run)
    except ValueError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    try:
        manifest = _read(path)
        _stop(
            manifest,
            reason=args.reason,
            now=_now(),
            open_questions=args.open_question or [],
        )
        _write(path, manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    print(f"STOPPED {path.relative_to(REPO_ROOT)}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    return _validate_paths(_all_run_paths(), merge_ready=args.merge_ready)


def command_validate_changed(args: argparse.Namespace) -> int:
    changed = _changed_files(args.base, args.head)
    changed_runs = {
        REPO_ROOT / path
        for path in changed
        if path.startswith("audits/workflow_runs/") and path.endswith(".json")
    }
    changed_entries = {
        path for path in changed if path.startswith("entries/") and path.endswith(".md")
    }
    failed = bool(_validate_paths(sorted(changed_runs), merge_ready=args.merge_ready))
    if changed_entries:
        changed_set = set(changed)
        manifests: list[tuple[Path, dict[str, Any]]] = []
        for path in changed_runs:
            try:
                manifests.append((path, _read(path)))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
        for entry in sorted(changed_entries):
            matches = [
                path
                for path, manifest in manifests
                if manifest.get("entry_path") == entry and manifest.get("status") == "completed"
            ]
            if not matches and not _is_registered_review_demotion(
                entry,
                base=args.base,
                head=args.head,
                changed=changed_set,
            ):
                failed = True
                print(
                    f"FAIL {entry}: changed entry requires a changed completed workflow run",
                    file=sys.stderr,
                )
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guard bounded dictionary-entry workflow runs")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("--headword", required=True)
    start.add_argument("--entry", required=True)
    start.add_argument("--branch", required=True)
    start.add_argument("--base-sha", required=True)
    start.add_argument("--profile", choices=sorted(PROFILES), default="standard")
    start.add_argument("--reason")
    start.add_argument("--run-id")
    start.set_defaults(func=command_start)

    confirm = sub.add_parser("confirm-remote")
    confirm.add_argument("run")
    confirm.add_argument("--commit-sha", required=True)
    confirm.add_argument("--remote", default="origin")
    confirm.set_defaults(func=command_confirm_remote)

    heartbeat = sub.add_parser("heartbeat")
    heartbeat.add_argument("run")
    heartbeat.set_defaults(func=command_heartbeat)

    research = sub.add_parser("record-research")
    research.add_argument("run")
    research.add_argument("--queries", type=int, default=0)
    research.add_argument("--candidate-pages", type=int, default=0)
    research.set_defaults(func=command_record_research)

    checkpoint = sub.add_parser("checkpoint")
    checkpoint.add_argument("run")
    checkpoint.add_argument("--stage", choices=STAGES[2:], required=True)
    checkpoint.add_argument("--notes")
    checkpoint.set_defaults(func=command_checkpoint)

    stop = sub.add_parser("stop")
    stop.add_argument("run")
    stop.add_argument("--reason", required=True)
    stop.add_argument("--open-question", action="append")
    stop.set_defaults(func=command_stop)

    validate = sub.add_parser("validate")
    validate.add_argument("--merge-ready", action="store_true")
    validate.set_defaults(func=command_validate)

    changed = sub.add_parser("validate-changed")
    changed.add_argument("--base", required=True)
    changed.add_argument("--head", required=True)
    changed.add_argument("--merge-ready", action="store_true")
    changed.set_defaults(func=command_validate_changed)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
