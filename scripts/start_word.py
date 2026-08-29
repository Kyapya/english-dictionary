from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from slugify import slugify


REPO_ROOT = Path(__file__).resolve().parents[1]
REMOTE = "origin"
GUARD_MARKER = "scripts/start_word.py"
RUNS_ROOT = "audits/workflow_runs"


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _ref_has_guard(ref: str) -> bool:
    result = _git("cat-file", "-e", f"{ref}:{GUARD_MARKER}", check=False)
    return result.returncode == 0


def _remote_refs() -> list[str]:
    result = _git(
        "for-each-ref",
        "--format=%(refname:short)",
        f"refs/remotes/{REMOTE}",
    )
    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip() and line.strip() != f"{REMOTE}/HEAD"
    ]


def _manifest_paths(ref: str, slug: str) -> list[str]:
    prefix = f"{RUNS_ROOT}/{slug}"
    result = _git("ls-tree", "-r", "--name-only", ref, "--", prefix)
    return [
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip().endswith(".json")
    ]


def discover_remote_runs(headword: str) -> list[dict[str, Any]]:
    """Return guarded workflow runs visible on remote branches.

    Only refs containing this guard script participate. This intentionally
    grandfathers branches created before the single-run policy was introduced,
    while making every branch created from the fixed main participate.
    """
    resolved = slugify(headword)
    if not resolved:
        raise ValueError("headword must produce a non-empty slug")
    _git(
        "fetch",
        "--prune",
        REMOTE,
        "+refs/heads/*:refs/remotes/origin/*",
    )
    found: dict[str, dict[str, Any]] = {}
    status_rank = {"in_progress": 0, "budget_exhausted": 1, "completed": 2}
    for ref in _remote_refs():
        if not _ref_has_guard(ref):
            continue
        for path in _manifest_paths(ref, resolved):
            raw = _git("show", f"{ref}:{path}").stdout
            try:
                manifest = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(manifest, dict):
                continue
            if slugify(str(manifest.get("headword", ""))) != resolved:
                continue
            run_id = str(manifest.get("run_id", "")).strip()
            if not run_id:
                continue
            record = {
                "run_id": run_id,
                "branch": ref.removeprefix(f"{REMOTE}/"),
                "run_path": path,
                "status": str(manifest.get("status", "")),
                "stage": str(manifest.get("stage", "")),
                "started_at": manifest.get("started_at"),
                "deadline_at": manifest.get("deadline_at"),
                "stop_reason": str(manifest.get("stop_reason", "")),
            }
            previous = found.get(run_id)
            if previous is None or status_rank.get(record["status"], -1) > status_rank.get(
                str(previous.get("status", "")), -1
            ):
                found[run_id] = record
    return sorted(
        found.values(),
        key=lambda item: _parse_time(item.get("started_at"))
        or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )


def blocking_runs(
    runs: list[dict[str, Any]], *, allow_restart_after_budget_exhausted: bool
) -> tuple[str | None, list[dict[str, Any]]]:
    """Classify whether a fresh run is allowed.

    Incomplete runs older than the newest completed run are historical and do
    not block. A current in-progress run always requires resume. A current
    budget-exhausted run requires an explicit restart flag so an agent cannot
    silently reset the deadline/failure counter by creating v2/v3/... runs.
    """
    completed_times = [
        parsed
        for item in runs
        if item.get("status") == "completed"
        for parsed in [_parse_time(item.get("started_at"))]
        if parsed is not None
    ]
    newest_completed = max(completed_times) if completed_times else None

    def current(item: dict[str, Any]) -> bool:
        started = _parse_time(item.get("started_at"))
        if newest_completed is None:
            return True
        if started is None:
            return True
        return started > newest_completed

    active = [
        item
        for item in runs
        if item.get("status") == "in_progress" and current(item)
    ]
    if active:
        return "resume_required", active
    exhausted = [
        item
        for item in runs
        if item.get("status") == "budget_exhausted" and current(item)
    ]
    if exhausted and not allow_restart_after_budget_exhausted:
        return "restart_confirmation_required", exhausted
    return None, []


def _new_start_args(argv: list[str]) -> tuple[str | None, bool]:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("headword", nargs="?")
    parser.add_argument("--resume")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--acceptance", action="store_true")
    parser.add_argument("--complete-stage")
    parser.add_argument("--record-revision")
    parser.add_argument("--restart-after-budget-exhausted", action="store_true")
    known, _ = parser.parse_known_args(argv)
    is_start = bool(known.headword) and not any(
        (
            known.resume,
            known.dry_run,
            known.acceptance,
            known.complete_stage,
            known.record_revision,
        )
    )
    return (
        str(known.headword) if is_start else None,
        bool(known.restart_after_budget_exhausted),
    )


def _forward_args(argv: list[str]) -> list[str]:
    return [arg for arg in argv if arg != "--restart-after-budget-exhausted"]


def _print_block(status: str, headword: str, runs: list[dict[str, Any]]) -> None:
    payload: dict[str, Any] = {
        "status": status,
        "headword": headword,
        "reason": (
            "unfinished guarded workflow exists; resume it instead of creating a new branch/run"
            if status == "resume_required"
            else "the latest guarded workflow exhausted its budget; a fresh run requires explicit operator approval"
        ),
        "runs": runs,
    }
    if runs:
        candidate = runs[0]
        payload["next_command"] = (
            f"git checkout {candidate['branch']} && "
            f"python scripts/run_word.py --resume {candidate['run_path']}"
        )
    if status == "restart_confirmation_required":
        payload["restart_command"] = (
            f"python scripts/start_word.py {headword} --restart-after-budget-exhausted"
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    headword, allow_restart = _new_start_args(args)
    if headword is not None:
        try:
            runs = discover_remote_runs(headword)
        except (subprocess.CalledProcessError, ValueError) as exc:
            print(
                json.dumps(
                    {
                        "status": "remote_run_scan_failed",
                        "headword": headword,
                        "reason": str(exc),
                        "action": "do not start a new run until remote run state can be verified",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 5
        status, blockers = blocking_runs(
            runs,
            allow_restart_after_budget_exhausted=allow_restart,
        )
        if status is not None:
            _print_block(status, headword, blockers)
            return 3 if status == "resume_required" else 4

    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "run_word.py"), *_forward_args(args)],
        cwd=REPO_ROOT,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
